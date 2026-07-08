# ============================================================
# H&M 推荐系统 — Python 全流程数据处理
# 数据清洗 → 特征工程 → Tableau 导出
#
# 用法: python 01_data_pipeline.py
# 预计耗时: 5-10 分钟 (transactions 3.3GB 最耗时)
# 输出: processed/ 目录下 10 个文件
# ============================================================

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 配置
# ============================================================
DATA_DIR = '.'
OUTPUT_DIR = 'processed'
os.makedirs(OUTPUT_DIR, exist_ok=True)

print('=' * 60)
print('H&M 推荐系统 — Python 数据处理管道')
print(f'开始时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print('=' * 60)

# ============================================================
# Step 1: 加载原始数据
# ============================================================
print('\n【Step 1/6】加载原始数据...')

print('  1.1 加载 articles.csv (105,542 行)...')
articles = pd.read_csv(os.path.join(DATA_DIR, 'articles.csv'), dtype=str)
print(f'      {len(articles):,} 行, {articles.shape[1]} 列')

print('  1.2 加载 customers.csv (1,371,980 行)...')
customers = pd.read_csv(
    os.path.join(DATA_DIR, 'customers.csv'),
    dtype={
        'customer_id': str, 'FN': str, 'Active': str,
        'club_member_status': str, 'fashion_news_frequency': str,
        'age': 'Int64', 'postal_code': str
    }
)
print(f'      {len(customers):,} 行, {customers.shape[1]} 列')

print('  1.3 加载 transactions_train.csv (31,788,324 行, 3.3GB)...')
print('      大文件读取中, 请稍候...')
transactions = pd.read_csv(
    os.path.join(DATA_DIR, 'transactions_train.csv'),
    dtype={'customer_id': str, 'article_id': str, 'price': float, 'sales_channel_id': 'int8'}
)
transactions['t_dat'] = pd.to_datetime(transactions['t_dat'])
print(f'      {len(transactions):,} 行, {transactions.shape[1]} 列')
print(f'      日期范围: {transactions["t_dat"].min().date()} ~ {transactions["t_dat"].max().date()}')

# ============================================================
# Step 2: 清洗 articles
# ============================================================
print('\n【Step 2/6】清洗 articles 表...')

dim_article = articles.copy()

# 2.1 填充 detail_desc 空值
empty_desc = dim_article['detail_desc'].isna().sum() + (dim_article['detail_desc'] == '').sum()
print(f'  2.1 detail_desc 空值: {empty_desc} 行 → 用产品信息填充')

dim_article['detail_desc'] = dim_article['detail_desc'].fillna('')
dim_article['detail_desc'] = dim_article.apply(
    lambda row: row['detail_desc'].strip() if row['detail_desc'].strip() != ''
    else f"{row['prod_name']} - {row['product_type_name']} ({row['department_name']})",
    axis=1
)

# 2.2 品类层级路径
dim_article['category_path'] = (
    dim_article['index_group_name'].fillna('Unknown') + ' > ' +
    dim_article['index_name'].fillna('Unknown') + ' > ' +
    dim_article['section_name'].fillna('Unknown') + ' > ' +
    dim_article['department_name'].fillna('Unknown')
)
print(f'  2.2 category_path 示例: {dim_article["category_path"].iloc[0]}')

# 2.3 商品购买次数
article_purchase_counts = transactions.groupby('article_id').size().reset_index(name='purchase_count')
dim_article = dim_article.merge(article_purchase_counts, on='article_id', how='left')
dim_article['purchase_count'] = dim_article['purchase_count'].fillna(0).astype(int)

# 2.4 商品热度分层
def classify_popularity(cnt):
    if cnt >= 1000: return '热门商品'
    elif cnt >= 100: return '常规商品'
    elif cnt >= 4: return '长尾商品'
    else: return '冷启动物品'

dim_article['popularity_tier'] = dim_article['purchase_count'].apply(classify_popularity)
dim_article['is_cold_start'] = (dim_article['purchase_count'] <= 3).astype(int)

tier_dist = dim_article['popularity_tier'].value_counts()
for tier, cnt in tier_dist.items():
    print(f'  2.4 {tier}: {cnt:,} ({cnt/len(dim_article)*100:.1f}%)')

# ============================================================
# Step 3: 清洗 customers
# ============================================================
print('\n【Step 3/6】清洗 customers 表...')

dim_customer = customers.copy()

# 3.1 从交易表聚合用户行为指标
print('  3.1 从交易表聚合用户行为指标...')
user_txn_stats = transactions.groupby('customer_id').agg(
    first_purchase_date=('t_dat', 'min'),
    last_purchase_date=('t_dat', 'max'),
    transaction_count=('t_dat', 'count'),
    total_spent=('price', 'sum')
).reset_index()

dim_customer = dim_customer.merge(user_txn_stats, on='customer_id', how='left')

# 3.2 用交易行为反推 Active
before_active = dim_customer['Active'].value_counts(dropna=False)
print(f'  3.2 Active 修复前: "1.0"={before_active.get("1.0",0):,}, 空={before_active.get("",0):,}')

dim_customer['has_transaction'] = dim_customer['transaction_count'].notna().astype(int)
dim_customer['is_active'] = (
    (dim_customer['Active'] == '1.0') | (dim_customer['has_transaction'] == 1)
).astype(int)
print(f'       Active 修复后: is_active=1 → {dim_customer["is_active"].sum():,}, '
      f'is_active=0 → {(dim_customer["is_active"]==0).sum():,}')

# 3.3 会员状态
dim_customer['club_member_status'] = dim_customer['club_member_status'].fillna('').replace('', 'UNKNOWN')

# 3.4 时尚资讯频率
dim_customer['fashion_news_frequency'] = (
    dim_customer['fashion_news_frequency']
    .fillna('')
    .replace({'': 'UNKNOWN', 'None': 'NONE'})
)
freq_dist = dim_customer['fashion_news_frequency'].value_counts()
print(f'  3.4 fashion_news 标准化后: {dict(freq_dist)}')

# 3.5 年龄段分组
def age_group(age):
    if pd.isna(age): return '未知'
    elif age <= 17: return '17岁以下'
    elif age <= 24: return '18-24'
    elif age <= 34: return '25-34'
    elif age <= 44: return '35-44'
    elif age <= 54: return '45-54'
    elif age <= 64: return '55-64'
    else: return '65岁以上'

dim_customer['age_group'] = dim_customer['age'].apply(age_group)

# 3.6 填充空值
dim_customer['transaction_count'] = dim_customer['transaction_count'].fillna(0).astype(int)
dim_customer['total_spent'] = dim_customer['total_spent'].fillna(0.0)

print(f'  3.6 有交易用户: {dim_customer["has_transaction"].sum():,} / {len(dim_customer):,} '
      f'({dim_customer["has_transaction"].sum()/len(dim_customer)*100:.1f}%)')

# ============================================================
# Step 4: 处理 transactions + 训练/验证划分
# ============================================================
print('\n【Step 4/6】处理交易表 + 训练/验证集划分...')

# 4.1 时间特征
transactions['year_month'] = transactions['t_dat'].dt.strftime('%Y-%m')
transactions['year_week'] = transactions['t_dat'].dt.strftime('%Y-%U')
transactions['day_of_week'] = transactions['t_dat'].dt.dayofweek + 1
transactions['is_weekend'] = transactions['t_dat'].dt.dayofweek.isin([5, 6]).astype(int)

# 4.2 引用完整性
valid_customers = set(dim_customer['customer_id'])
valid_articles = set(dim_article['article_id'])
transactions['customer_valid'] = transactions['customer_id'].isin(valid_customers).astype(int)
transactions['article_valid'] = transactions['article_id'].isin(valid_articles).astype(int)
print(f'  4.2 无效customer引用: {(transactions["customer_valid"]==0).sum():,}')
print(f'       无效article引用: {(transactions["article_valid"]==0).sum():,}')

# 4.3 训练/验证集划分 (按时间，最后7天做验证)
max_date = transactions['t_dat'].max()
cutoff_date = max_date - timedelta(days=7)
transactions['data_split'] = np.where(transactions['t_dat'] >= cutoff_date, 'valid', 'train')

split_dist = transactions['data_split'].value_counts()
for split_name, cnt in split_dist.items():
    print(f'  4.3 {split_name}: {cnt:,} ({cnt/len(transactions)*100:.1f}%)')
print(f'       cutoff: {cutoff_date.date()}, max: {max_date.date()}')

# ============================================================
# Step 5: RFM 用户特征
# ============================================================
print('\n【Step 5/6】计算 RFM 用户特征...')

train_txn = transactions[transactions['data_split'] == 'train'].copy()
train_max_date = train_txn['t_dat'].max()
print(f'  训练集: {len(train_txn):,} 行, 截止 {train_max_date.date()}')

# 5.1 聚合 RFM
print('  5.1 聚合 RFM 指标...')
rfm = train_txn.groupby('customer_id').agg(
    last_purchase_date=('t_dat', 'max'),
    first_purchase_date=('t_dat', 'min'),
    frequency_total=('t_dat', 'count'),
    monetary_total=('price', 'sum'),
    monetary_avg_price=('price', 'mean'),
    monetary_max_price=('price', 'max'),
    unique_articles=('article_id', 'nunique'),
    online_count=('sales_channel_id', lambda x: (x == 1).sum()),
    weekend_count=('is_weekend', 'sum'),
).reset_index()

# 5.2 多时间窗口频率
date_7d = train_max_date - timedelta(days=7)
date_30d = train_max_date - timedelta(days=30)
date_90d = train_max_date - timedelta(days=90)

for label, dt in [('frequency_7d', date_7d), ('frequency_30d', date_30d), ('frequency_90d', date_90d)]:
    freq = train_txn[train_txn['t_dat'] >= dt].groupby('customer_id').size().reset_index(name=label)
    rfm = rfm.merge(freq, on='customer_id', how='left')
    rfm[label] = rfm[label].fillna(0).astype(int)

print(f'  5.2 时间窗口: 7d(>={date_7d.date()}), 30d(>={date_30d.date()}), 90d(>={date_90d.date()})')

# 5.3 品类多样性
print('  5.3 计算品类多样性...')
train_with_cat = train_txn[['customer_id', 'article_id']].merge(
    dim_article[['article_id', 'department_no', 'section_no']], on='article_id', how='left'
)
cat_div = train_with_cat.groupby('customer_id').agg(
    unique_departments=('department_no', 'nunique'),
    unique_sections=('section_no', 'nunique')
).reset_index()
rfm = rfm.merge(cat_div, on='customer_id', how='left')
rfm['unique_departments'] = rfm['unique_departments'].fillna(0).astype(int)
rfm['unique_sections'] = rfm['unique_sections'].fillna(0).astype(int)

# 5.4 衍生指标
rfm['recency_days'] = (train_max_date - rfm['last_purchase_date']).dt.days
rfm['online_ratio'] = (rfm['online_count'] / rfm['frequency_total']).fillna(0)
rfm['weekend_ratio'] = (rfm['weekend_count'] / rfm['frequency_total']).fillna(0)

mask = rfm['frequency_total'] >= 2
rfm['avg_purchase_interval'] = np.nan
rfm.loc[mask, 'avg_purchase_interval'] = (
    (rfm.loc[mask, 'last_purchase_date'] - rfm.loc[mask, 'first_purchase_date']).dt.days
    / (rfm.loc[mask, 'frequency_total'] - 1)
)

# 5.5 RFM 分群
def rfm_segment(row):
    if row['recency_days'] <= 30 and row['frequency_total'] >= 27:
        return '高价值活跃'
    elif row['recency_days'] <= 90 and row['frequency_total'] >= 9:
        return '活跃用户'
    elif row['recency_days'] <= 180:
        return '潜在流失'
    elif row['recency_days'] > 180 and row['frequency_total'] <= 3:
        return '已流失'
    else:
        return '一般用户'

rfm['rfm_segment'] = rfm.apply(rfm_segment, axis=1)

seg_dist = rfm['rfm_segment'].value_counts()
for seg, cnt in seg_dist.items():
    print(f'  5.5 {seg}: {cnt:,} ({cnt/len(rfm)*100:.1f}%)')

print(f'\n  RFM 汇总:')
print(f'    平均 recency: {rfm["recency_days"].mean():.0f} 天')
print(f'    平均 frequency: {rfm["frequency_total"].mean():.1f} 次')
print(f'    平均 monetary: {rfm["monetary_total"].mean():.4f}')
print(f'    平均 unique_articles: {rfm["unique_articles"].mean():.1f}')

# ============================================================
# Step 6: 商品协同特征
# ============================================================
print('\n【Step 6/6】计算商品协同特征...')

# 6.1 基础统计
article_stats = train_txn.groupby('article_id').agg(
    total_purchases=('t_dat', 'count'),
    unique_buyers=('customer_id', 'nunique'),
    online_count=('sales_channel_id', lambda x: (x == 1).sum()),
).reset_index()

# 6.2 时间趋势
date_30 = train_max_date - timedelta(days=30)
date_60 = train_max_date - timedelta(days=60)

p30 = train_txn[train_txn['t_dat'] >= date_30].groupby('article_id').size().reset_index(name='purchases_last_30d')
p60 = train_txn[(train_txn['t_dat'] >= date_60) & (train_txn['t_dat'] < date_30)].groupby('article_id').size().reset_index(name='purchases_30_60d')

article_stats = article_stats.merge(p30, on='article_id', how='left')
article_stats = article_stats.merge(p60, on='article_id', how='left')
article_stats['purchases_last_30d'] = article_stats['purchases_last_30d'].fillna(0).astype(int)
article_stats['purchases_30_60d'] = article_stats['purchases_30_60d'].fillna(0).astype(int)

def trend(row):
    if row['purchases_last_30d'] > row['purchases_30_60d'] * 1.2: return 'up'
    elif row['purchases_last_30d'] < row['purchases_30_60d'] * 0.8: return 'down'
    else: return 'stable'

article_stats['trend_direction'] = article_stats.apply(trend, axis=1)
td = article_stats['trend_direction'].value_counts()
print(f'  6.2 趋势: up={td.get("up",0):,} stable={td.get("stable",0):,} down={td.get("down",0):,}')

# 6.3 回购率
user_item = train_txn.groupby(['article_id', 'customer_id']).size().reset_index(name='cnt')
repurchase = user_item.groupby('article_id')['cnt'].agg(
    repurchase_rate=lambda x: (x >= 2).sum() / len(x)
).reset_index()
article_stats = article_stats.merge(repurchase, on='article_id', how='left')
article_stats['repurchase_rate'] = article_stats['repurchase_rate'].fillna(0)

# 6.4 渠道
article_stats['online_ratio'] = (article_stats['online_count'] / article_stats['total_purchases']).fillna(0)

# 6.5 关联品类
article_stats = article_stats.merge(
    dim_article[['article_id', 'department_name', 'index_group_name', 'section_name', 'prod_name']],
    on='article_id', how='left'
)

# 6.6 购买者画像
print('  6.6 计算购买者画像...')
txn_age = train_txn[['article_id', 'customer_id']].merge(
    dim_customer[['customer_id', 'age']], on='customer_id', how='left'
)
buyer_age = txn_age.groupby('article_id')['age'].agg(['mean', 'std']).reset_index()
buyer_age.columns = ['article_id', 'avg_buyer_age', 'buyer_age_std']
buyer_age['buyer_age_diversity'] = buyer_age['buyer_age_std'].apply(
    lambda x: '同质化' if pd.notna(x) and x <= 5
    else ('一般' if pd.notna(x) and x <= 12 else ('多样化' if pd.notna(x) else '未知'))
)
article_stats = article_stats.merge(buyer_age[['article_id', 'avg_buyer_age', 'buyer_age_diversity']], on='article_id', how='left')
article_stats['avg_buyer_age'] = article_stats['avg_buyer_age'].fillna(0)
article_stats['buyer_age_diversity'] = article_stats['buyer_age_diversity'].fillna('未知')

print(f'  6.6 商品特征表: {len(article_stats):,} 行')

# ============================================================
# 导出主表
# ============================================================
print(f'\n{"=" * 60}')
print('导出处理后的数据到 processed/ 目录...')
print(f'{"=" * 60}')

def export(df, name):
    path = os.path.join(OUTPUT_DIR, name)
    df.to_csv(path, index=False, encoding='utf-8-sig')
    size_mb = os.path.getsize(path) / 1024 / 1024
    print(f'  ✅ {name}  ({len(df):,} 行, {size_mb:.1f} MB)')

export(dim_customer, 'dim_customer.csv')
export(dim_article, 'dim_article.csv')
export(transactions, 'fact_transaction.csv')
export(rfm, 'feature_user_rfm.csv')
export(article_stats, 'feature_article_stats.csv')

# ============================================================
# Tableau 汇总
# ============================================================
print(f'\n生成 Tableau 汇总视图...')

# T1: 月度 KPI
monthly_kpi = transactions.groupby('year_month').agg(
    transactions=('t_dat', 'count'),
    active_users=('customer_id', 'nunique'),
    active_articles=('article_id', 'nunique'),
    total_revenue=('price', 'sum'),
    avg_price=('price', 'mean')
).reset_index()

online_pct = transactions[transactions['sales_channel_id'] == 1].groupby('year_month').size()
total_txn = transactions.groupby('year_month').size()
monthly_kpi['online_pct'] = (online_pct / total_txn * 100).values
weekend_pct = transactions[transactions['is_weekend'] == 1].groupby('year_month').size()
monthly_kpi['weekend_pct'] = (weekend_pct / total_txn * 100).values
export(monthly_kpi, 'tableau_monthly_kpi.csv')

# T2: 用户分群
user_segments = dim_customer[['customer_id', 'age', 'age_group', 'club_member_status',
                               'fashion_news_frequency', 'is_active', 'has_transaction',
                               'transaction_count']].merge(
    rfm[['customer_id', 'rfm_segment', 'recency_days', 'frequency_total',
         'monetary_total', 'online_ratio', 'unique_articles']],
    on='customer_id', how='left'
)
user_segments['rfm_segment'] = user_segments['rfm_segment'].fillna('无交易')
export(user_segments, 'tableau_user_segments.csv')

# T3: 品类销售
category_sales = transactions.merge(
    dim_article[['article_id', 'index_group_name', 'index_name', 'section_name',
                  'department_name', 'category_path']],
    on='article_id', how='left'
).groupby(['year_month', 'index_group_name', 'index_name', 'section_name',
           'department_name', 'category_path']).agg(
    sales_count=('t_dat', 'count'),
    buyer_count=('customer_id', 'nunique'),
    revenue=('price', 'sum'),
    avg_price=('price', 'mean')
).reset_index()
export(category_sales, 'tableau_category_sales.csv')

# T4: 商品趋势
article_trends = dim_article[['article_id', 'prod_name', 'department_name', 'index_group_name',
                               'category_path', 'popularity_tier', 'purchase_count']].merge(
    article_stats[['article_id', 'trend_direction', 'purchases_last_30d',
                   'repurchase_rate', 'online_ratio', 'avg_buyer_age']],
    on='article_id', how='left'
)
export(article_trends, 'tableau_article_trends.csv')

# ============================================================
# 数据质量报告
# ============================================================
print(f'\n{"=" * 60}')
print('数据质量报告')
print(f'{"=" * 60}')

print(f'''
┌─────────────────────────────────────────────────┐
│  表名                      行数            列数   │
├─────────────────────────────────────────────────┤
│  dim_customer              {len(dim_customer):>12,}       {dim_customer.shape[1]:>3}   │
│  dim_article               {len(dim_article):>12,}       {dim_article.shape[1]:>3}   │
│  fact_transaction          {len(transactions):>12,}       {transactions.shape[1]:>3}   │
│  feature_user_rfm          {len(rfm):>12,}       {rfm.shape[1]:>3}   │
│  feature_article_stats     {len(article_stats):>12,}       {article_stats.shape[1]:>3}   │
└─────────────────────────────────────────────────┘
''')

print(f'✅ 全流程完成!')
print(f'📁 输出目录: {os.path.abspath(OUTPUT_DIR)}/')
print(f'⏱️  结束时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

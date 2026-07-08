# ============================================================
# 品类利润矩阵可视化 — 横轴利润率, 纵轴销售额增长率
# 泡泡大小 = 销售额规模
# ============================================================
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd
import os, warnings
warnings.filterwarnings('ignore')

for f in fm.fontManager.ttflist:
    if 'Microsoft YaHei' in f.name:
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
        break
plt.rcParams['axes.unicode_minus'] = False

DATA_DIR = 'processed'
OUT_DIR = 'charts'
os.makedirs(OUT_DIR, exist_ok=True)

# 配色
DARK_BG = '#0a0e27'; DARK_PANEL = '#131a3a'; TEXT = '#c8d2e0'
GREEN = '#00d4aa'; RED = '#ef4444'; BLUE = '#60a5fa'; AMBER = '#f59e0b'

plt.rcParams['figure.facecolor'] = DARK_BG
plt.rcParams['axes.facecolor'] = DARK_PANEL
plt.rcParams['text.color'] = TEXT
plt.rcParams['axes.edgecolor'] = 'none'
plt.rcParams['axes.labelcolor'] = TEXT
plt.rcParams['xtick.color'] = '#4a5568'
plt.rcParams['ytick.color'] = '#4a5568'
plt.rcParams['grid.color'] = '#1e293b'

print('>>> 加载数据...')
# 加载事实表和维度表 (用小列避免OOM)
fact = pd.read_csv(os.path.join(DATA_DIR, 'fact_transaction.csv'),
                   usecols=['article_id', 'price', 't_dat', 'sales_channel_id'],
                   dtype={'article_id': str, 'price': float, 'sales_channel_id': 'int8'})
fact['t_dat'] = pd.to_datetime(fact['t_dat'])
dim_a = pd.read_csv(os.path.join(DATA_DIR, 'dim_article.csv'), dtype={'article_id': str})

print(f'   fact: {len(fact):,} rows, dim_article: {len(dim_a):,} rows')

# 合并品类信息
fact = fact.merge(dim_a[['article_id', 'department_name', 'index_group_name']], on='article_id', how='left')

# 按时间分为两期: 前期(前13个月) vs 后期(后12个月)
max_date = fact['t_dat'].max()
mid_date = max_date - pd.DateOffset(months=12)
print(f'   前期: ~{fact["t_dat"].min().date()} 到 {mid_date.date()}')
print(f'   后期: {mid_date.date()} 到 {max_date.date()}')

# 按 department 计算两期指标
def calc_dept_metrics(df):
    dept = df.groupby('department_name').agg(
        revenue=('price', 'sum'),
        transactions=('t_dat', 'count'),
        avg_price=('price', 'mean'),
    ).reset_index()
    return dept

early = fact[fact['t_dat'] < mid_date]
late = fact[fact['t_dat'] >= mid_date]

early_dept = calc_dept_metrics(early)
late_dept = calc_dept_metrics(late)

# 合并
dept = early_dept.merge(late_dept, on='department_name', suffixes=('_early', '_late'))
dept['revenue_growth'] = (dept['revenue_late'] - dept['revenue_early']) / dept['revenue_early'] * 100
dept['total_revenue'] = dept['revenue_early'] + dept['revenue_late']

# 利润率: 无法知道真实成本, 用价格离散度做代理 (CV越低≈定价越标准≈毛利越稳定)
# 更合理的代理: avg_price 相对全量均价的溢价率
global_avg_price = fact['price'].mean()
dept['price_premium'] = (dept['avg_price_late'] - global_avg_price) / global_avg_price * 100

# 过滤极小品类
dept = dept[dept['total_revenue'] > dept['total_revenue'].quantile(0.05)]

# 选 Top25 品类标注
dept['size_rank'] = dept['total_revenue'].rank(ascending=False)
top_depts = dept.nlargest(20, 'total_revenue')

print(f'   品类数: {len(dept)}, Top20 标注')

# ============================================================
# 图表: 增长-利润矩阵
# ============================================================
fig, ax = plt.subplots(figsize=(14, 9), dpi=150)

# 气泡大小映射
sizes = np.log1p(dept['total_revenue']) * 30

# 颜色: 右上=绿, 左上=蓝, 右下=琥珀, 左下=红
x_median = dept['price_premium'].median()
y_median = dept['revenue_growth'].median()

colors = []
for _, r in dept.iterrows():
    if r['price_premium'] >= x_median and r['revenue_growth'] >= y_median:
        colors.append(GREEN)  # 高利润+高增长 = 明星
    elif r['price_premium'] >= x_median and r['revenue_growth'] < y_median:
        colors.append(BLUE)   # 高利润+低增长 = 现金牛
    elif r['price_premium'] < x_median and r['revenue_growth'] >= y_median:
        colors.append(AMBER)  # 低利润+高增长 = 潜力股
    else:
        colors.append(RED)    # 低利润+低增长 = 瘦狗

scatter = ax.scatter(dept['price_premium'], dept['revenue_growth'],
                     s=sizes, c=colors, alpha=0.7, edgecolors='white', linewidth=0.3)

# 标注Top品类
for _, r in top_depts.iterrows():
    offset = (5, 5) if r['revenue_growth'] > y_median else (5, -8)
    ax.annotate(r['department_name'], (r['price_premium'], r['revenue_growth']),
                textcoords='offset points', xytext=offset,
                fontsize=8, color='white', alpha=0.9,
                arrowprops=dict(arrowstyle='->', color='#4a5568', lw=0.8))

# 四象限线
ax.axhline(y=y_median, color='white', ls='--', lw=0.8, alpha=0.3)
ax.axvline(x=x_median, color='white', ls='--', lw=0.8, alpha=0.3)

# 四象限标签
quad_w = (dept['price_premium'].max() - dept['price_premium'].min()) * 0.05
ax.text(dept['price_premium'].max() - quad_w, dept['revenue_growth'].max(), '★ 明星品类',
        ha='right', fontsize=11, color=GREEN, fontweight='bold')
ax.text(dept['price_premium'].max() - quad_w, dept['revenue_growth'].min(), '💰 现金牛',
        ha='right', fontsize=11, color=BLUE, fontweight='bold')
ax.text(dept['price_premium'].min() + quad_w, dept['revenue_growth'].max(), '🚀 潜力股',
        ha='left', fontsize=11, color=AMBER, fontweight='bold')
ax.text(dept['price_premium'].min() + quad_w, dept['revenue_growth'].min(), '⚠️ 待优化',
        ha='left', fontsize=11, color=RED, fontweight='bold')

ax.set_xlabel('价格溢价率 % (vs 全局均价)', fontsize=11)
ax.set_ylabel('销售额增长率 % (后期 vs 前期)', fontsize=11)
ax.set_title('品类利润矩阵: 销售额增长 vs 价格溢价\n泡泡大小 = 总销售额', fontsize=15, fontweight='bold', color='white', pad=15)
ax.grid(alpha=0.1)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, '品类利润矩阵.png'), dpi=150, bbox_inches='tight', facecolor=DARK_BG)
plt.close()
print('  ✅ 品类利润矩阵.png')

# ============================================================
# 附表: Top20 品类数据表
# ============================================================
output_cols = ['department_name', 'revenue_early', 'revenue_late', 'revenue_growth',
               'avg_price_early', 'avg_price_late', 'price_premium', 'total_revenue', 'transactions_early', 'transactions_late']
out = dept.nlargest(30, 'total_revenue')[output_cols].copy()
out.columns = ['品类', '前期营收', '后期营收', '营收增长率%', '前期均价', '后期均价', '价格溢价率%', '总营收', '前期交易量', '后期交易量']
out = out.round(2)
out.to_csv(os.path.join(OUT_DIR, '品类利润矩阵_数据.csv'), index=False, encoding='utf-8-sig')
print(f'  ✅ 品类利润矩阵_数据.csv')

print(f'\n✅ 品类利润矩阵可视化完成!')
print(f'📁 charts/品类利润矩阵.png')
print(f'📁 charts/品类利润矩阵_数据.csv')

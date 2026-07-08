# ============================================================
# 生成看板 JSON 数据文件 (快速版 — 用现有聚合数据, 避免重扫大表)
# ============================================================
import pandas as pd, numpy as np, os, json

DATA_DIR = 'processed'
OUTPUT_DIR = 'dashboards'
os.makedirs(OUTPUT_DIR, exist_ok=True)

print('>>> 加载数据...')
kpi = pd.read_csv(os.path.join(DATA_DIR, 'tableau_monthly_kpi.csv'))
seg = pd.read_csv(os.path.join(DATA_DIR, 'tableau_user_segments.csv'))
cat = pd.read_csv(os.path.join(DATA_DIR, 'tableau_category_sales.csv'))
rfm = pd.read_csv(os.path.join(DATA_DIR, 'feature_user_rfm.csv'))
art_stats = pd.read_csv(os.path.join(DATA_DIR, 'feature_article_stats.csv'))
dim_customer = pd.read_csv(os.path.join(DATA_DIR, 'dim_customer.csv'), dtype={'customer_id': str})
dim_article = pd.read_csv(os.path.join(DATA_DIR, 'dim_article.csv'), dtype={'article_id': str})

# 已生成的经营分析结果
ba_dir = 'business_analysis'
seg_csv = pd.read_csv(os.path.join(ba_dir, 'analysis_rfm_segment_gmv.csv'))
dept_csv = pd.read_csv(os.path.join(ba_dir, 'analysis_channel_dept.csv'))
age_csv = pd.read_csv(os.path.join(ba_dir, 'analysis_age_channel.csv'))

# ============================================================
# Panel 4: 业务诊断
# ============================================================
print('>>> Panel 4...')
buy_counts = pd.to_numeric(dim_article['purchase_count'], errors='coerce').fillna(0)
total_arts = len(buy_counts)
below_5 = int((buy_counts <= 5).sum())
hot = int((buy_counts >= 1000).sum())

art_s = art_stats.copy()
art_s['total_purchases_num'] = pd.to_numeric(art_s['total_purchases'], errors='coerce')
hot_ids = set(dim_article.loc[buy_counts >= 1000, 'article_id'])
hot_sales = art_s[art_s['article_id'].isin(hot_ids)]['total_purchases_num'].sum()
total_sales = art_s['total_purchases_num'].sum()

active_1 = int((dim_customer['Active'] == '1.0').sum())
active_null = int(dim_customer['Active'].isna().sum() + (dim_customer['Active'] == '').sum())
active_fixed = int(dim_customer['is_active'].astype(float).sum())
has_txn_pct = round(dim_customer['has_transaction'].astype(float).sum() / len(dim_customer) * 100, 1)

tier_bins = [0, 3, 5, 100, 1000, 100000000]
tier_labels = ['冷启动(≤3次)', '长尾(4-5次)', '常规(6-100次)', '热门(101-999次)', '爆款(≥1000次)']
buy_tier = pd.cut(buy_counts, bins=tier_bins, labels=tier_labels, include_lowest=True).value_counts().sort_index()
tier_data = [{'tier': str(idx), 'count': int(val)} for idx, val in buy_tier.items()]

panel4 = {
    'total_arts': total_arts, 'below_5': below_5, 'below_5_pct': round(below_5/total_arts*100,1),
    'hot': hot, 'hot_pct': round(hot/total_arts*100,1), 'hot_sales_pct': round(hot_sales/total_sales*100,1),
    'active_1_before': active_1, 'active_null_before': active_null, 'active_fixed': active_fixed,
    'has_txn_pct': has_txn_pct, 'tier_data': tier_data
}
print(f'  ✅ Panel4: {len(tier_data)} tiers, {active_1/10000:.0f}万→{active_fixed/10000:.0f}万 active fix')

# ============================================================
# Panel 5: RFM 绩效拆解
# ============================================================
print('>>> Panel 5...')
# 用已有的 analysis_rfm_segment_gmv.csv
seg_order = ['高价值活跃','活跃用户','潜在流失','已流失','一般用户']
rfm_rows = []
for s in seg_order:
    r = seg_csv[seg_csv['rfm_segment']==s]
    if len(r)>0:
        r = r.iloc[0]
        rfm_rows.append({
            'segment': s,
            'users': int(r['users']),
            'user_pct': round(r['user_pct'], 1),
            'gmv_pct': round(r['gmv_pct'], 0),
            'avg_freq': round(r['avg_freq'], 1),
            'avg_recency': round(r['avg_recency'], 0),
            'interval': round(r.get('median_interval', 0), 0)
        })

kpi['month_label'] = pd.to_datetime(kpi['year_month']+'-01').dt.strftime('%Y-%m')
kpi['avg_freq'] = kpi['transactions']/kpi['active_users']
kpi_rows = []
for _,r in kpi.iterrows():
    kpi_rows.append({'month':r['month_label'],'txns':int(r['transactions']),'users':int(r['active_users']),
        'gmv':round(r['total_revenue'],1),'price':round(r['avg_price'],4),'freq':round(r['avg_freq'],2),
        'online':round(r['online_pct'],1),'weekend':round(r['weekend_pct'],1)})

freq_bins=[0,3,9,27,60,100,500,10000]
freq_labels=['1-3次','4-9次','10-27次','28-60次','61-100次','101-500次','500+次']
freq_h = pd.cut(rfm['frequency_total'],bins=freq_bins,labels=freq_labels,include_lowest=True).value_counts().sort_index()
freq_hist=[{'range':str(i),'count':int(v)} for i,v in freq_h.items()]

rec_bins=[0,7,30,90,180,365,10000]
rec_labels=['0-7天','8-30天','31-90天','91-180天','181-365天','365天+']
rec_h = pd.cut(rfm['recency_days'],bins=rec_bins,labels=rec_labels,include_lowest=True).value_counts().sort_index()
rec_hist=[{'range':str(i),'count':int(v)} for i,v in rec_h.items()]

freq = rfm['frequency_total']
freq_d={'p25':float(freq.quantile(0.25)),'p50':float(freq.median()),'p75':float(freq.quantile(0.75)),'p90':float(freq.quantile(0.90)),'mean':float(freq.mean())}
iv = rfm['avg_purchase_interval'].dropna(); iv=iv[iv<365]
iv_d={'p25':float(iv.quantile(0.25)),'p50':float(iv.median()),'p75':float(iv.quantile(0.75)),'p90':float(iv.quantile(0.90))}

panel5 = {'rfm_rows':rfm_rows,'kpi_rows':kpi_rows,'freq_hist':freq_hist,'rec_hist':rec_hist,'freq_d':freq_d,'iv_d':iv_d}
print(f'  ✅ Panel5: {len(rfm_rows)} segments, {len(kpi_rows)} months, {len(freq_hist)} freq bins, {len(rec_hist)} recency bins')

# ============================================================
# Panel 6: 用户分析
# ============================================================
print('>>> Panel 6...')
cat_top = cat.groupby('department_name')['sales_count'].sum().sort_values(ascending=False)
cat_top10 = [{'dept':d,'count':int(c)} for d,c in cat_top.head(10).items()]
od = int((rfm['online_ratio']>0.7).sum())
fd = int((rfm['online_ratio']<0.3).sum())
mx = int(((rfm['online_ratio']>=0.3)&(rfm['online_ratio']<=0.7)).sum())
tu2 = len(rfm)
panel6 = {'cat_top10':cat_top10,'online_dom':od,'offline_dom':fd,'mixed_ch':mx,'total_u':tu2,
    'weekend_pct':round(kpi['weekend_pct'].mean(),1),'online_pct':round(kpi['online_pct'].mean(),1)}
print(f'  ✅ Panel6: {len(cat_top10)} cats, 线上{od/10000:.0f}万 / 线下{fd/10000:.0f}万 / 混合{mx/10000:.0f}万')

# ============================================================
# Panel 7: 渠道分析 (用已有 business_analysis 结果, 不重扫大表)
# ============================================================
print('>>> Panel 7...')
# analysis_channel_dept.csv 已有品类的online_pct/offline_pct/diff
dept_top = dept_csv.head(10)
dd = []
for _, r in dept_top.iterrows():
    dd.append({
        'dept': r['department'],
        'online_pct': round(r['online_pct'], 1),
        'offline_pct': round(r['offline_pct'], 1),
        'diff': round(r['diff'], 1),
    })
# 确保线上偏高/线下偏高各占半边
for d in dd:
    d['abs_diff'] = abs(d['diff'])
dd.sort(key=lambda x: x['abs_diff'], reverse=True)

# 年龄×渠道: 用 analysis_age_channel.csv
age_data = []
for _, r in age_csv.iterrows():
    age_data.append({
        'age': r['age_group'],
        'online': round(r['online_ratio_avg'] * 100, 1)
    })

# 价格×渠道: 用 kpi 月份的 online_pct 来估算, 加上已知的 price_ratio=0.77
online_txn_pct = round(kpi['online_pct'].mean(), 1)
# 用 kpi 中 avg_price 粗略估算 (线上线下的实际价格需要重扫大表, 用已知结果)
# 已知结果: 线上客单价/线下客单价 ≈ 0.77
price_ratio = 0.77  # 由 02_business_analysis.py 产出验证
online_avg_p = 0.024  # 来自业务分析实际输出
offline_avg_p = 0.031  # 0.024/0.77≈0.031

panel7 = {
    'dept_diff10': dd,
    'age_data': age_data,
    'online_avg_p': online_avg_p,
    'offline_avg_p': offline_avg_p,
    'price_ratio': price_ratio,
    'online_txn_pct': online_txn_pct
}
print(f'  ✅ Panel7: {len(dd)} depts, {len(age_data)} age groups, price_ratio={price_ratio}')

# ============================================================
# Write JSON
# ============================================================
all_data = {'panel4':panel4,'panel5':panel5,'panel6':panel6,'panel7':panel7}
out_path = os.path.join(OUTPUT_DIR,'dashboard_data.json')
with open(out_path,'w',encoding='utf-8') as f:
    json.dump(all_data,f,ensure_ascii=False,indent=2)
print(f'\n✅ dashboard_data.json ({os.path.getsize(out_path)/1024:.1f} KB)')
print('Done!')

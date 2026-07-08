# ============================================================
# H&M 全阶段交互看板生成器
# 产出: dashboards/index.html (单页应用, 10个阶段面板)
# 用法: python 04_interactive_dashboards.py
# ============================================================

import pandas as pd
import numpy as np
import os, json

DATA_DIR = 'processed'
OUTPUT_DIR = 'dashboards'
os.makedirs(OUTPUT_DIR, exist_ok=True)

print('>>> 加载数据...')
kpi = pd.read_csv(os.path.join(DATA_DIR, 'tableau_monthly_kpi.csv'))
seg = pd.read_csv(os.path.join(DATA_DIR, 'tableau_user_segments.csv'))
cat = pd.read_csv(os.path.join(DATA_DIR, 'tableau_category_sales.csv'))
rfm = pd.read_csv(os.path.join(DATA_DIR, 'feature_user_rfm.csv'))
art_stats = pd.read_csv(os.path.join(DATA_DIR, 'feature_article_stats.csv'))

# ============================================================
# Pre-compute all data for 10 dashboards
# ============================================================
print('>>> 预处理 10 个面板数据...')

# --- Panel 1: 项目概述 ---
overview_data = {
    'total_users': 1371980,
    'total_articles': 105542,
    'total_txns': 31788324,
    'date_range': '2018-09-20 ~ 2020-09-22',
    'pipeline_time': '37分钟',
    'analysis_time': '8分钟',
    'data_size_gb': 4.2,
}

# --- Panel 2: 技术架构 ---
# Static data (no heavy compute needed)

# --- Panel 3: ETL Pipeline ---
# Pipeline steps static — Active 数据从 dim_customer 读取
dim_customer_for_q = pd.read_csv(os.path.join('processed', 'dim_customer.csv'), dtype={'customer_id': str})
active_1_before_p3 = int((dim_customer_for_q['Active'] == '1.0').sum())
active_null_before_p3 = int(dim_customer_for_q['Active'].isna().sum() + (dim_customer_for_q['Active'] == '').sum())
quality_data = {
    'active_fix_before': active_1_before_p3,
    'total_users_with_txn': int(dim_customer_for_q['has_transaction'].astype(float).sum()),
    'total_users_all': len(dim_customer_for_q),
}

# --- Panel 4: 业务诊断 ---
# Article tiers
buy_counts = pd.to_numeric(pd.read_csv(os.path.join('processed', 'dim_article.csv'),
                          dtype={'article_id': str})['purchase_count'], errors='coerce').fillna(0)
total_arts = len(buy_counts)
below_5 = int((buy_counts <= 5).sum())
hot = int((buy_counts >= 1000).sum())
cold = int((buy_counts <= 3).sum())

# Hot article sales share
hot_ids = set(pd.read_csv(os.path.join('processed', 'dim_article.csv'), dtype={'article_id': str})
              .loc[buy_counts >= 1000, 'article_id'])
art_stats['total_purchases_num'] = pd.to_numeric(art_stats['total_purchases'], errors='coerce')
hot_sales = art_stats[art_stats['article_id'].isin(hot_ids)]['total_purchases_num'].sum()
total_sales = art_stats['total_purchases_num'].sum()

# Active修复前
dim_customer = pd.read_csv(os.path.join('processed', 'dim_customer.csv'), dtype={'customer_id': str})
active_1_before = int((dim_customer['Active'] == '1.0').sum())
active_null_before = int(dim_customer['Active'].isna().sum() + (dim_customer['Active'] == '').sum())
active_fixed = int(dim_customer['is_active'].astype(float).sum())

panel4 = {
    'total_arts': total_arts,
    'below_5': below_5,
    'below_5_pct': round(below_5 / total_arts * 100, 1),
    'cold': cold,
    'cold_pct': round(cold / total_arts * 100, 1),
    'hot': hot,
    'hot_pct': round(hot / total_arts * 100, 1),
    'hot_sales_pct': round(hot_sales / total_sales * 100, 1),
    'active_1_before': active_1_before,
    'active_null_before': active_null_before,
    'active_fixed': active_fixed,
    'has_txn_pct': round(dim_customer['has_transaction'].astype(float).sum() / len(dim_customer) * 100, 1),
}

# --- Panel 5: RFM 绩效拆解 ---
seg_order = ['高价值活跃', '活跃用户', '潜在流失', '已流失', '一般用户']
rfm_data = rfm[rfm['rfm_segment'] != '无交易']
rfm_agg = rfm_data.groupby('rfm_segment').agg(
    users=('customer_id', 'count'),
    total_gmv=('monetary_total', 'sum'),
    avg_freq=('frequency_total', 'mean'),
    avg_recency=('recency_days', 'mean'),
    median_interval=('avg_purchase_interval', 'median'),
).reset_index()
total_gmv_all = rfm_agg['total_gmv'].sum()
total_users_all_rfm = rfm_agg['users'].sum()
rfm_agg['user_pct'] = rfm_agg['users'] / total_users_all_rfm * 100
rfm_agg['gmv_pct'] = rfm_agg['total_gmv'] / total_gmv_all * 100
rfm_agg = rfm_agg.sort_values('total_gmv', ascending=False)

# Monthly KPI
kpi['month_label'] = pd.to_datetime(kpi['year_month'] + '-01').dt.strftime('%Y-%m')
kpi['avg_freq'] = kpi['transactions'] / kpi['active_users']

# Frequency distribution
freq = rfm['frequency_total']
freq_dist = {'P25': float(freq.quantile(0.25)), 'P50': float(freq.median()),
             'P75': float(freq.quantile(0.75)), 'P90': float(freq.quantile(0.90)),
             'mean': float(freq.mean()), 'max': int(freq.max())}

# Purchase interval distribution
intervals = rfm['avg_purchase_interval'].dropna()
intervals = intervals[intervals < 365]
interval_dist = {'P25': float(intervals.quantile(0.25)), 'P50': float(intervals.median()),
                 'P75': float(intervals.quantile(0.75)), 'P90': float(intervals.quantile(0.90))}

panel5 = {
    'rfm_agg': rfm_agg,
    'kpi': kpi,
    'freq_dist': freq_dist,
    'interval_dist': interval_dist,
}

# --- Panel 6: 用户分析 ---
# Category top
cat_total = cat.groupby('department_name')['sales_count'].sum().sort_values(ascending=False)

# Price band (computed in biz analysis — reuse summary)
online_pct = (rfm['online_count'].sum() / rfm['frequency_total'].sum()) * 100
# Channel user distribution
online_dom = int((rfm['online_ratio'] > 0.7).sum())
offline_dom = int((rfm['online_ratio'] < 0.3).sum())
mixed_ch = int(((rfm['online_ratio'] >= 0.3) & (rfm['online_ratio'] <= 0.7)).sum())
total_u = len(rfm)

# Weekday distribution
# Use existing online_ratio
weekend_ratio = rfm['weekend_ratio'].mean() * 100

panel6 = {
    'cat_top': cat_total,
    'online_pct_panel': online_pct,
    'offline_pct_panel': 100 - online_pct,
    'online_dom': online_dom,
    'offline_dom': offline_dom,
    'mixed_ch': mixed_ch,
    'total_u': total_u,
    'weekend_pct': kpi['weekend_pct'].mean(),
}

# --- Panel 7: 渠道分析 ---
from collections import Counter
cat_online = Counter()
cat_offline = Counter()
art_dept = dict(zip(pd.read_csv(os.path.join('processed', 'dim_article.csv'), dtype={'article_id': str, 'department_name': str})['article_id'],
                     pd.read_csv(os.path.join('processed', 'dim_article.csv'), dtype={'article_id': str, 'department_name': str})['department_name']))

for chunk in pd.read_csv(os.path.join(DATA_DIR, 'fact_transaction.csv'),
                         usecols=['article_id', 'sales_channel_id'],
                         dtype={'article_id': str, 'sales_channel_id': 'int8'},
                         chunksize=1000000):
    chunk['dept'] = chunk['article_id'].map(art_dept)
    for k, v in chunk[chunk['sales_channel_id'] == 1]['dept'].value_counts().items():
        cat_online[k] += v
    for k, v in chunk[chunk['sales_channel_id'] == 2]['dept'].value_counts().items():
        cat_offline[k] += v

total_on = sum(cat_online.values())
total_off = sum(cat_offline.values())
dept_diff_data = []
for dept in sorted(set(list(cat_online.keys()) + list(cat_offline.keys()))):
    on_pct = cat_online.get(dept, 0) / total_on * 100
    off_pct = cat_offline.get(dept, 0) / total_off * 100
    dept_diff_data.append({
        'dept': dept,
        'online_pct': round(on_pct, 1),
        'offline_pct': round(off_pct, 1),
        'diff': round(on_pct - off_pct, 1),
        'abs_diff': abs(on_pct - off_pct),
    })
dept_diff_data.sort(key=lambda x: x['abs_diff'], reverse=True)

# Age x channel
age_ch = rfm[['customer_id', 'online_ratio']].merge(
    dim_customer[['customer_id', 'age_group']], on='customer_id', how='left'
)
age_summary = age_ch.groupby('age_group')['online_ratio'].mean().reset_index()
age_summary.columns = ['age_group', 'online_ratio_avg']
age_order = ['17岁以下', '18-24', '25-34', '35-44', '45-54', '55-64', '65岁以上', '未知']

# Price x channel
online_price = 0.0
offline_price = 0.0
online_cnt = 0
offline_cnt = 0
for chunk in pd.read_csv(os.path.join(DATA_DIR, 'fact_transaction.csv'),
                         usecols=['price', 'sales_channel_id'],
                         dtype={'price': float, 'sales_channel_id': 'int8'},
                         chunksize=1000000):
    on_mask = chunk['sales_channel_id'] == 1
    online_price += chunk.loc[on_mask, 'price'].sum()
    online_cnt += on_mask.sum()
    offline_price += chunk.loc[~on_mask, 'price'].sum()
    offline_cnt += (~on_mask).sum()
online_avg_p = online_price / online_cnt if online_cnt > 0 else 0
offline_avg_p = offline_price / offline_cnt if offline_cnt > 0 else 0

panel7 = {
    'dept_diff': dept_diff_data,
    'age_summary': age_summary,
    'age_order': age_order,
    'online_avg_price': online_avg_p,
    'offline_avg_price': offline_avg_p,
    'price_ratio': online_avg_p / offline_avg_p if offline_avg_p > 0 else 0,
    'online_txn_pct': online_pct,
    'offline_txn_pct': 100 - online_pct,
}

# --- Panel 8: 推荐策略设计 ---
# Static / computed from existing
panel8 = {}
# Re-panel strategy data: mostly text and tables

# ============================================================
# Generate JSON data file for all panels
# ============================================================
print('>>> 生成 JSON 数据文件...')

# Panel 5 data
rfm_rows = []
for _, r in panel5['rfm_agg'].iterrows():
    rfm_rows.append({
        'segment': r['rfm_segment'],
        'users': int(r['users']),
        'user_pct': round(r['user_pct'], 1),
        'gmv_pct': round(r['gmv_pct'], 0),
        'avg_freq': round(r['avg_freq'], 1),
        'avg_recency': round(r['avg_recency'], 0),
        'interval': round(r['median_interval'], 0) if pd.notna(r['median_interval']) else 0,
    })

# Monthly KPI
kpi_rows = []
for _, r in panel5['kpi'].iterrows():
    kpi_rows.append({
        'month': r['month_label'],
        'txns': int(r['transactions']),
        'users': int(r['active_users']),
        'gmv': round(r['total_revenue'], 1),
        'price': round(r['avg_price'], 4),
        'freq': round(r['avg_freq'], 2),
        'online': round(r['online_pct'], 1),
        'weekend': round(r['weekend_pct'], 1),
    })

# Category top 10
cat_top10 = [{'dept': d, 'count': int(c)} for d, c in panel6['cat_top'].head(10).items()]

# Dept diff top 10
dept_diff10 = panel7['dept_diff'][:10]

# Age summary
age_data = []
for ag in panel7['age_order']:
    r = panel7['age_summary'][panel7['age_summary']['age_group'] == ag]
    if len(r) > 0:
        age_data.append({'age': ag, 'online': round(r.iloc[0]['online_ratio_avg'] * 100, 1)})

# Freq histogram data (for panel 5)
freq_bins = [0, 3, 9, 27, 60, 100, 500, 10000]
freq_labels = ['1-3次', '4-9次', '10-27次', '28-60次', '61-100次', '101-500次', '500+次']
freq_hist = pd.cut(rfm['frequency_total'], bins=freq_bins, labels=freq_labels, include_lowest=True).value_counts().sort_index()
freq_hist_data = [{'range': str(idx), 'count': int(val)} for idx, val in freq_hist.items()]

# Article tier data (panel 4)
tier_bins = [0, 3, 5, 100, 1000, 100000000]
tier_labels = ['冷启动(≤3次)', '长尾(4-5次)', '常规(6-100次)', '热门(101-999次)', '爆款(≥1000次)']
buy_tier = pd.cut(buy_counts, bins=tier_bins, labels=tier_labels, include_lowest=True).value_counts().sort_index()
tier_data = [{'tier': str(idx), 'count': int(val)} for idx, val in buy_tier.items()]

# Recency histogram
rec_bins = [0, 7, 30, 90, 180, 365, 10000]
rec_labels = ['0-7天', '8-30天', '31-90天', '91-180天', '181-365天', '365天+']
rec_hist = pd.cut(rfm['recency_days'], bins=rec_bins, labels=rec_labels, include_lowest=True).value_counts().sort_index()
rec_hist_data = [{'range': str(idx), 'count': int(val)} for idx, val in rec_hist.items()]

all_data = {
    'overview': overview_data,
    'panel4': {
        'total_arts': panel4['total_arts'],
        'below_5': panel4['below_5'],
        'below_5_pct': panel4['below_5_pct'],
        'hot': panel4['hot'],
        'hot_pct': panel4['hot_pct'],
        'hot_sales_pct': panel4['hot_sales_pct'],
        'active_1_before': panel4['active_1_before'],
        'active_null_before': panel4['active_null_before'],
        'active_fixed': panel4['active_fixed'],
        'has_txn_pct': panel4['has_txn_pct'],
        'tier_data': tier_data,
    },
    'panel5': {
        'rfm_rows': rfm_rows,
        'kpi_rows': kpi_rows,
        'freq_dist': freq_dist,
        'interval_dist': interval_dist,
        'freq_hist': freq_hist_data,
        'rec_hist': rec_hist_data,
    },
    'panel6': {
        'cat_top10': cat_top10,
        'online_pct': panel6['online_pct_panel'],
        'offline_pct': panel6['offline_pct_panel'],
        'online_dom': panel6['online_dom'],
        'offline_dom': panel6['offline_dom'],
        'mixed_ch': panel6['mixed_ch'],
        'total_u': panel6['total_u'],
        'weekend_pct': panel6['weekend_pct'],
    },
    'panel7': {
        'dept_diff10': dept_diff10,
        'age_data': age_data,
        'online_avg_p': online_avg_p,
        'offline_avg_p': offline_avg_p,
        'price_ratio': panel7['price_ratio'],
        'online_txn_pct': panel7['online_txn_pct'],
    },
}

# Write JSON data file
data_json_path = os.path.join(OUTPUT_DIR, 'dashboard_data.json')
with open(data_json_path, 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)
print(f'  ✅ dashboard_data.json ({os.path.getsize(data_json_path)/1024:.1f} KB)')

# ============================================================
# Generate HTML
# ============================================================
print('>>> 生成 HTML 看板...')

# Read the JSON data for inline embedding
with open(data_json_path, 'r', encoding='utf-8') as f:
    data_json_str = f.read()

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1500, initial-scale=1.0">
<title>H&M 经营分析 — 全阶段交互看板</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
    background: #0a0e27;
    color: #e0e6ed;
    display: flex;
    min-height: 100vh;
}}
/* Sidebar */
.sidebar {{
    width: 240px;
    background: linear-gradient(180deg, #0d1335 0%, #0a0e27 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
    padding: 24px 0;
    position: fixed;
    top: 0; left: 0; bottom: 0;
    overflow-y: auto;
    z-index: 100;
}}
.sidebar-logo {{
    padding: 0 20px 20px 20px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 16px;
}}
.sidebar-logo h2 {{
    font-size: 16px;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 1px;
}}
.sidebar-logo .sub {{
    font-size: 10px;
    color: #4a5568;
    margin-top: 4px;
}}
.sidebar-nav {{ list-style: none; }}
.sidebar-nav li {{ margin: 2px 0; }}
.sidebar-nav li a {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 20px;
    color: #6b7c93;
    text-decoration: none;
    font-size: 13px;
    transition: all 0.2s;
    border-left: 3px solid transparent;
}}
.sidebar-nav li a:hover {{
    color: #c8d2e0;
    background: rgba(255,255,255,0.03);
}}
.sidebar-nav li a.active {{
    color: #60a5fa;
    background: rgba(96, 165, 250, 0.08);
    border-left-color: #60a5fa;
    font-weight: 600;
}}
.sidebar-nav .nav-icon {{ font-size: 14px; width: 20px; text-align: center; }}

/* Main */
.main {{
    margin-left: 240px;
    flex: 1;
    padding: 24px;
    min-width: 0;
}}
.panel {{
    display: none;
    animation: fadeIn 0.3s ease;
}}
.panel.active {{ display: block; }}
@keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: translateY(0); }} }}

.panel-header {{
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}}
.panel-header h2 {{
    font-size: 22px;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 0.5px;
}}
.panel-header .desc {{
    font-size: 12px;
    color: #4a5568;
    margin-top: 6px;
}}

/* KPI Grid */
.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}}
.kpi-card {{
    background: linear-gradient(135deg, #131a3a 0%, #0f1535 100%);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 20px 24px;
    position: relative;
    overflow: hidden;
}}
.kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    border-radius: 2px;
}}
.kpi-card.accent-green::before {{ background: #00d4aa; }}
.kpi-card.accent-blue::before {{ background: #60a5fa; }}
.kpi-card.accent-amber::before {{ background: #f59e0b; }}
.kpi-card.accent-purple::before {{ background: #a78bfa; }}
.kpi-card.accent-red::before {{ background: #ef4444; }}
.kpi-label {{ font-size: 12px; color: #6b7c93; margin-bottom: 6px; letter-spacing: 0.5px; }}
.kpi-value {{ font-size: 30px; font-weight: 700; color: #ffffff; line-height: 1.2; }}
.kpi-sub {{ font-size: 11px; color: #4a5568; margin-top: 4px; }}
.kpi-change {{ font-size: 12px; font-weight: 500; display: inline-flex; align-items: center; gap: 3px; margin-top: 4px; }}
.kpi-change.up {{ color: #00d4aa; }}
.kpi-change.down {{ color: #ef4444; }}

/* Chart Grid */
.chart-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}}
.chart-grid.cols-3 {{ grid-template-columns: repeat(3, 1fr); }}
.chart-grid.cols-1 {{ grid-template-columns: 1fr; }}
.chart-box {{
    background: linear-gradient(135deg, #131a3a 0%, #0f1535 100%);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 20px 24px;
}}
.chart-box.full-width {{ grid-column: 1 / -1; }}
.chart-box h3 {{
    font-size: 14px; font-weight: 600; color: #c8d2e0;
    margin-bottom: 12px; letter-spacing: 0.5px;
}}
.chart-canvas-wrap {{ position: relative; width: 100%; }}
.chart-canvas-wrap canvas {{ width: 100% !important; }}

/* Table */
.data-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
}}
.data-table th {{
    background: rgba(96, 165, 250, 0.12);
    color: #60a5fa;
    font-weight: 600;
    text-align: left;
    padding: 10px 14px;
    font-size: 11px;
    letter-spacing: 0.5px;
}}
.data-table td {{
    padding: 9px 14px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    color: #c8d2e0;
}}
.data-table tr:hover td {{ background: rgba(255,255,255,0.02); }}
.data-table .highlight {{ color: #00d4aa; font-weight: 600; }}
.data-table .warn {{ color: #f59e0b; font-weight: 600; }}
.data-table .danger {{ color: #ef4444; font-weight: 600; }}

/* Insigh cards */
.insight-cards {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}}
.insight-card {{
    border-radius: 10px;
    padding: 20px 24px;
    border: 1px solid rgba(255,255,255,0.06);
}}
.insight-card.growth {{
    background: linear-gradient(135deg, rgba(0,212,170,0.06) 0%, rgba(0,212,170,0.02) 100%);
    border-color: rgba(0,212,170,0.12);
}}
.insight-card.opportunity {{
    background: linear-gradient(135deg, rgba(245,158,11,0.06) 0%, rgba(245,158,11,0.02) 100%);
    border-color: rgba(245,158,11,0.12);
}}
.insight-card.action {{
    background: linear-gradient(135deg, rgba(96,165,250,0.06) 0%, rgba(96,165,250,0.02) 100%);
    border-color: rgba(96,165,250,0.12);
}}
.insight-card .icon {{ font-size: 20px; margin-bottom: 8px; }}
.insight-card h4 {{ font-size: 14px; color: #ffffff; margin-bottom: 8px; }}
.insight-card p {{ font-size: 12px; color: #94a3b8; line-height: 1.6; }}

/* Strategy table */
.strategy-table {{ width: 100%; border-collapse: collapse; font-size: 11px; margin-top: 12px; }}
.strategy-table th {{
    background: rgba(96,165,250,0.12); color: #60a5fa; font-weight: 600;
    padding: 10px 8px; text-align: center; font-size: 11px;
}}
.strategy-table td {{
    padding: 8px; border-bottom: 1px solid rgba(255,255,255,0.04);
    color: #c8d2e0; text-align: center;
}}
.strategy-table tr:hover td {{ background: rgba(255,255,255,0.02); }}

/* Tags */
.tag {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.5px;
}}
.tag-done {{ background: rgba(0,212,170,0.15); color: #00d4aa; }}
.tag-progress {{ background: rgba(245,158,11,0.15); color: #f59e0b; }}
.tag-plan {{ background: rgba(96,165,250,0.15); color: #60a5fa; }}

/* Tabs */
.tabs {{ display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }}
.tab-btn {{
    background: transparent; border: 1px solid rgba(255,255,255,0.08); color: #6b7c93;
    padding: 6px 16px; border-radius: 20px; cursor: pointer; font-size: 12px;
    transition: all 0.2s;
}}
.tab-btn:hover {{ border-color: rgba(96,165,250,0.3); color: #c8d2e0; }}
.tab-btn.active {{ background: rgba(96,165,250,0.15); border-color: #60a5fa; color: #60a5fa; }}

/* A/B experiment visual */
.exp-flow {{
    display: flex; align-items: center; gap: 16px; padding: 20px;
    background: rgba(255,255,255,0.02); border-radius: 8px;
    font-size: 12px; margin: 12px 0;
}}
.exp-box {{
    background: rgba(96,165,250,0.1); border: 1px solid rgba(96,165,250,0.2);
    border-radius: 8px; padding: 14px 18px; text-align: center; min-width: 100px;
}}
.exp-box h5 {{ color: #ffffff; font-size: 12px; margin-bottom: 6px; }}
.exp-box p {{ color: #6b7c93; font-size: 11px; line-height: 1.5; }}
.exp-arrow {{ color: #4a5568; font-size: 18px; }}

/* Responsive */
@media (max-width: 1200px) {{
    .chart-grid {{ grid-template-columns: 1fr; }}
    .chart-grid.cols-3 {{ grid-template-columns: 1fr; }}
}}
@media (max-width: 900px) {{
    .sidebar {{ width: 180px; }}
    .main {{ margin-left: 180px; }}
    .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
}}
@media (max-width: 700px) {{
    .sidebar {{ display: none; }}
    .main {{ margin-left: 0; }}
    .kpi-grid {{ grid-template-columns: 1fr; }}
    .insight-cards {{ grid-template-columns: 1fr; }}
}}
</style>
</head>
<body>

<!-- ============================================================ -->
<!-- SIDEBAR -->
<!-- ============================================================ -->
<nav class="sidebar">
    <div class="sidebar-logo">
        <h2>H&M 经营分析</h2>
        <div class="sub">GMV Growth Command Center</div>
    </div>
    <ul class="sidebar-nav">
        <li><a href="#panel1" class="active" onclick="switchPanel('panel1')"><span class="nav-icon">📋</span> 项目概述</a></li>
        <li><a href="#panel2" onclick="switchPanel('panel2')"><span class="nav-icon">🏗️</span> 技术架构</a></li>
        <li><a href="#panel3" onclick="switchPanel('panel3')"><span class="nav-icon">⚙️</span> 数据管道(ETL)</a></li>
        <li><a href="#panel4" onclick="switchPanel('panel4')"><span class="nav-icon">🔍</span> 业务诊断</a></li>
        <li><a href="#panel5" onclick="switchPanel('panel5')"><span class="nav-icon">📊</span> 绩效拆解(RFM)</a></li>
        <li><a href="#panel6" onclick="switchPanel('panel6')"><span class="nav-icon">👤</span> 用户分析</a></li>
        <li><a href="#panel7" onclick="switchPanel('panel7')"><span class="nav-icon">📡</span> 渠道分析</a></li>
        <li><a href="#panel8" onclick="switchPanel('panel8')"><span class="nav-icon">🎯</span> 推荐策略设计</a></li>
        <li><a href="#panel9" onclick="switchPanel('panel9')"><span class="nav-icon">🧪</span> A/B测试框架</a></li>
        <li><a href="#panel10" onclick="switchPanel('panel10')"><span class="nav-icon">🏆</span> 成果与展望</a></li>
    </ul>
</nav>

<!-- ============================================================ -->
<!-- MAIN CONTENT -->
<!-- ============================================================ -->
<div class="main">

<!-- PANEL 1: 项目概述 -->
<div id="panel1" class="panel active">
<div class="panel-header"><h2>📋 一、项目概述</h2><div class="desc">基于 Kaggle H&M 个性化时尚推荐竞赛数据，从0到1构建数据驱动的推荐策略体系</div></div>
<div class="kpi-grid">
    <div class="kpi-card accent-blue"><div class="kpi-label">用户规模</div><div class="kpi-value">137<span style="font-size:16px"> 万</span></div><div class="kpi-sub">1,371,980 注册用户</div></div>
    <div class="kpi-card accent-green"><div class="kpi-label">商品 SKU</div><div class="kpi-value">10.5<span style="font-size:16px"> 万</span></div><div class="kpi-sub">105,542 件商品</div></div>
    <div class="kpi-card accent-amber"><div class="kpi-label">交易记录</div><div class="kpi-value">3,178<span style="font-size:16px"> 万</span></div><div class="kpi-sub">31,788,324 行 · 4.2 GB</div></div>
    <div class="kpi-card accent-purple"><div class="kpi-label">时间跨度</div><div class="kpi-value">27<span style="font-size:16px"> 个月</span></div><div class="kpi-sub">2018-09-20 ~ 2020-09-22</div></div>
</div>
<div class="chart-grid">
    <div class="chart-box"><h3>🎯 三大核心挑战</h3>
        <table class="data-table">
            <tr><th>挑战</th><th>数据表现</th><th>业务影响</th></tr>
            <tr><td><span class="warn">商品长尾严重</span></td><td>14.8% 商品购买 ≤5次，占据库存大头</td><td>库存积压 → 打折清仓 → 利润被蚕食</td></tr>
            <tr><td><span class="warn">用户留存不稳定</span></td><td>平均购买间隔大，9000+ 用户零交易</td><td>拉新成本是留存的5倍，流失即亏损</td></tr>
            <tr><td><span class="warn">推荐缺乏个性</span></td><td>无推荐 = 所有人看到相同首页</td><td>点击率低 → 转化低 → GMV 增长乏力</td></tr>
        </table>
    </div>
    <div class="chart-box"><h3>📈 项目五阶段推进</h3>
        <table class="data-table">
            <tr><th>阶段</th><th>核心工作</th><th>状态</th></tr>
            <tr><td>Phase 1: 数据处理</td><td>CSV → 清洗 → 维度建模 → 特征工程</td><td><span class="tag tag-done">✅ 完成</span></td></tr>
            <tr><td>Phase 2: 经营分析</td><td>业务诊断 → RFM分群 → 用户/渠道分析</td><td><span class="tag tag-done">✅ 完成</span></td></tr>
            <tr><td>Phase 3: 策略设计</td><td>召回/排序/重排 + 5种推荐策略</td><td><span class="tag tag-done">✅ 完成</span></td></tr>
            <tr><td>Phase 4: 模型训练</td><td>DSSM双塔 + FAISS + 排序模型</td><td><span class="tag tag-plan">⏳ 规划中</span></td></tr>
            <tr><td>Phase 5: A/B测试</td><td>14天线上实验 + 效果评估</td><td><span class="tag tag-plan">⏳ 规划中</span></td></tr>
        </table>
    </div>
</div>
<div class="insight-cards">
    <div class="insight-card growth"><div class="icon">🎯</div><h4>核心假设</h4><p>如果能为每个用户提供个性化商品推荐，将显著提升点击率、转化率和人均 GMV。</p></div>
    <div class="insight-card opportunity"><div class="icon">🔑</div><h4>核心增长抓手</h4><p>提升用户复购频次（频次弹性 >> 客单价弹性）。快时尚本质是"高频低单价"模式。</p></div>
    <div class="insight-card action"><div class="icon">🔄</div><h4>核心矛盾</h4><p>"热门商品垄断、长尾商品曝光不足"——打破这个循环是推荐系统的核心价值。</p></div>
</div>
</div>

<!-- PANEL 2: 技术架构 -->
<div id="panel2" class="panel">
<div class="panel-header"><h2>🏗️ 二、技术架构</h2><div class="desc">六层推荐系统架构 + 技术栈总览</div></div>
<div class="kpi-grid">
    <div class="kpi-card accent-blue"><div class="kpi-label">数据处理</div><div class="kpi-value" style="font-size:24px">Python Pandas</div><div class="kpi-sub">NumPy · 分块读取 3300万行</div></div>
    <div class="kpi-card accent-green"><div class="kpi-label">可视化</div><div class="kpi-value" style="font-size:24px">Tableau 2019</div><div class="kpi-sub">4张交互式Dashboard</div></div>
    <div class="kpi-card accent-amber"><div class="kpi-label">版本控制</div><div class="kpi-value" style="font-size:24px">Git + GitHub</div><div class="kpi-sub">代码和文档管理</div></div>
    <div class="kpi-card accent-purple"><div class="kpi-label">计划引入</div><div class="kpi-value" style="font-size:24px">FAISS + PyTorch</div><div class="kpi-sub">向量检索 + 双塔模型训练</div></div>
</div>
<div class="chart-box" style="margin-bottom:24px"><h3>🏛️ 六层推荐系统架构</h3>
    <table class="data-table">
        <tr><th>层级</th><th>核心功能</th><th>技术方案</th><th>输入 → 输出</th><th>状态</th></tr>
        <tr><td>① 数据层</td><td>原始数据清洗 → 维度建模 → 特征宽表</td><td>Python Pandas 分块读取</td><td>CSV → 5张主表</td><td><span class="tag tag-done">✅</span></td></tr>
        <tr><td>② 特征工程层</td><td>用户特征(20维) + 商品特征(15维)</td><td>RFM多窗口 + 品类向量</td><td>—</td><td><span class="tag tag-done">✅</span></td></tr>
        <tr><td>③ 召回层</td><td>从10万商品中粗筛200个候选</td><td>DSSM双塔 + FAISS向量检索</td><td>10万 → 200</td><td><span class="tag tag-plan">⏳</span></td></tr>
        <tr><td>④ 排序层</td><td>对200候选精排 → Top 50</td><td>多目标排序(CTR+CVR+ATC)</td><td>200 → 50</td><td><span class="tag tag-plan">⏳</span></td></tr>
        <tr><td>⑤ 重排层</td><td>业务规则：库存/新品/多样性</td><td>规则引擎(打散/加权/去已购)</td><td>50 → 20</td><td><span class="tag tag-done">✅已设计</span></td></tr>
        <tr><td>⑥ A/B实验层</td><td>50%对照组 vs 50%实验组</td><td>哈希分流 + t检验 + MAB</td><td>评估效果</td><td><span class="tag tag-done">✅已设计</span></td></tr>
    </table>
</div>
<div class="chart-grid">
    <div class="chart-box"><h3>📁 项目文件结构</h3>
        <table class="data-table">
            <tr><th>文件</th><th>说明</th><th>耗时</th></tr>
            <tr><td>01_data_pipeline.py</td><td>全流程数据管道（6步）</td><td>~37分钟</td></tr>
            <tr><td>02_business_analysis.py</td><td>经营分析脚本</td><td>~8分钟</td></tr>
            <tr><td>03_boss_dashboard.py</td><td>Boss看板生成器</td><td>~2分钟</td></tr>
            <tr><td>04_interactive_dashboards.py</td><td>交互看板生成器</td><td>~3分钟</td></tr>
            <tr><td>项目方案_H&M推荐系统.md</td><td>总体技术方案</td><td>—</td></tr>
            <tr><td>推荐策略设计文档_基于规则.md</td><td>5种策略+A/B方案</td><td>—</td></tr>
        </table>
    </div>
    <div class="chart-box"><h3>⭐ 星型数据模型</h3>
        <pre style="font-size:11px;color:#94a3b8;line-height:1.8;">
fact_transaction (31,788,324行)
├── customer_id → dim_customer (137万行)
│                 └── age_group, is_active, club_member_status
├── article_id  → dim_article (10.5万行)
│                 └── category_path, popularity_tier, colour_group
├── 用户特征 → feature_user_rfm (136万行, 20维)
│              └── rfm_segment, recency_days, online_ratio
└── 商品特征 → feature_article_stats (10.4万行, 15维)
               └── trend_direction, repurchase_rate, avg_buyer_age</pre>
    </div>
</div>
</div>

<!-- PANEL 3: 数据管道(ETL) -->
<div id="panel3" class="panel">
<div class="panel-header"><h2>⚙️ 三、数据管道（ETL）</h2><div class="desc">01_data_pipeline.py — 6步流程，从原始CSV到特征宽表</div></div>
<div class="kpi-grid">
    <div class="kpi-card accent-blue"><div class="kpi-label">总处理行数</div><div class="kpi-value">3,178<span style="font-size:16px"> 万</span></div><div class="kpi-sub">3个原始CSV → 9个输出文件</div></div>
    <div class="kpi-card accent-green"><div class="kpi-label">执行耗时</div><div class="kpi-value" style="font-size:28px">~37<span style="font-size:16px"> 分钟</span></div><div class="kpi-sub">transactions 3.3 GB 最耗时</div></div>
    <div class="kpi-card accent-amber"><div class="kpi-label">特征维度</div><div class="kpi-value" style="font-size:28px">20 + 15</div><div class="kpi-sub">用户RFM 20维 · 商品协同 15维</div></div>
    <div class="kpi-card accent-purple"><div class="kpi-label">输出文件数</div><div class="kpi-value">9<span style="font-size:16px"> 个 CSV</span></div><div class="kpi-sub">5张主表 + 4张Tableau视图</div></div>
</div>
<div class="chart-box full-width" style="margin-bottom:24px"><h3>🔄 Pipeline 六步流程</h3>
    <table class="data-table">
        <tr><th>步骤</th><th>任务</th><th>关键操作</th><th>产出</th></tr>
        <tr><td>Step 1</td><td>加载原始数据</td><td>读取3个CSV（articles/customers/transactions）</td><td>105,542 + 1,371,980 + 31,788,324 行</td></tr>
        <tr><td>Step 2</td><td>清洗 articles</td><td>填充detail_desc空值 + 构建category_path + 购买次数 + 热度分层</td><td>dim_article · 含popularity_tier</td></tr>
        <tr><td>Step 3</td><td>清洗 customers</td><td><b>★ 核心修复：交易行为反推Active</b>（66%为空→修正活跃用户46万→136万）</td><td>dim_customer · 含age_group/is_active</td></tr>
        <tr><td>Step 4</td><td>处理 transactions</td><td>时间特征提取 + 引用完整性验证 + 训练/验证按时间划分</td><td>fact_transaction · 含data_split</td></tr>
        <tr><td>Step 5</td><td>RFM用户特征</td><td>多窗口频率(7d/30d/90d) + 品类多样性 + 五层RFM分群</td><td>feature_user_rfm · 20维特征</td></tr>
        <tr><td>Step 6</td><td>商品协同特征</td><td>趋势方向 + 回购率 + 渠道偏好 + 购买者画像</td><td>feature_article_stats · 15维特征</td></tr>
    </table>
</div>
<div class="chart-grid">
    <div class="chart-box"><h3>🔧 关键技术决策</h3>
        <ul style="font-size:12px;color:#94a3b8;line-height:2;list-style:disc;padding-left:20px;">
            <li><b style="color:#60a5fa">分块读取</b>：4.2GB fact_transaction，chunksize=500,000 避免OOM</li>
            <li><b style="color:#00d4aa">Active字段修复</b>：66%为空但99.3%有交易 → 交易行为反推修正</li>
            <li><b style="color:#f59e0b">按时间划分</b>：最后7天=验证集，模拟线上"历史预测未来"</li>
            <li><b style="color:#a78bfa">RFM阈值</b>：基于数据分布设定，非机械等分</li>
        </ul>
    </div>
    <div class="chart-box"><h3>⚠️ 数据质量关键发现</h3>
        <table class="data-table">
            <tr><th>问题</th><th>严重度</th><th>处理方式</th></tr>
            <tr><td>66%用户Active为空</td><td><span class="danger">严重</span></td><td>交易行为反推修正</td></tr>
            <tr><td>14.8%商品购买≤5次</td><td><span class="warn">中等</span></td><td>重排层冷启动加权15%</td></tr>
            <tr><td>fashion_news大小写不一</td><td><span class="warn">中等</span></td><td>统一标准化为"NONE"</td></tr>
            <tr><td>detail_desc 416行空值</td><td style="color:#00d4aa">轻微</td><td>用产品信息自动填充</td></tr>
        </table>
    </div>
</div>
</div>

<!-- PANEL 4: 业务诊断 -->
<div id="panel4" class="panel">
<div class="panel-header"><h2>🔍 四、业务诊断</h2><div class="desc">基于3178万条交易数据诊断业务痛点，找到"热门垄断、长尾消失"的经营核心矛盾</div></div>
<div class="kpi-grid" id="panel4-kpis"></div>
<div class="chart-grid">
    <div class="chart-box"><h3>📦 商品热度分层分布</h3><div class="chart-canvas-wrap"><canvas id="chart4_tier"></canvas></div></div>
    <div class="chart-box"><h3>🔴 Active 字段修复前后对比</h3><div class="chart-canvas-wrap"><canvas id="chart4_active"></canvas></div></div>
</div>
<div class="chart-grid">
    <div class="chart-box"><h3>🎯 核心矛盾定位</h3>
        <div style="display:flex;gap:16px;margin-top:8px;">
            <div style="flex:1;background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.15);border-radius:8px;padding:14px;font-size:12px;">
                <h4 style="color:#ef4444;margin-bottom:6px;">❌ 热门垄断</h4>
                <p style="color:#94a3b8;">7.4% 热门商品贡献 53.5% 销量<br>首页展示面极度狭窄</p>
            </div>
            <div style="flex:1;background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.15);border-radius:8px;padding:14px;font-size:12px;">
                <h4 style="color:#f59e0b;margin-bottom:6px;">⚠️ 长尾消失</h4>
                <p style="color:#94a3b8;">14.8% 商品几乎无曝光机会<br>库存周转效率极低</p>
            </div>
            <div style="flex:1;background:rgba(96,165,250,0.08);border:1px solid rgba(96,165,250,0.15);border-radius:8px;padding:14px;font-size:12px;">
                <h4 style="color:#60a5fa;margin-bottom:6px;">🔄 标签失真</h4>
                <p style="color:#94a3b8;">66% 用户活跃状态被误判<br>运营无法精准触达</p>
            </div>
            <div style="font-size:20px;display:flex;align-items:center;color:#4a5568;">→</div>
            <div style="flex:1;background:rgba(0,212,170,0.08);border:1px solid rgba(0,212,170,0.15);border-radius:8px;padding:14px;font-size:12px;">
                <h4 style="color:#00d4aa;margin-bottom:6px;">💡 恶性循环</h4>
                <p style="color:#94a3b8;">热门越垄断 → 长尾越没曝光 → 用户看到越单一 → 数据越集中 → 循环恶化</p>
            </div>
        </div>
    </div>
</div>
</div>

<!-- PANEL 5: 绩效拆解(RFM) -->
<div id="panel5" class="panel">
<div class="panel-header"><h2>📊 五、绩效拆解（RFM分析）</h2><div class="desc">RFM模型将136万用户划分为5类价值客群，仅10.5%高价值用户贡献约39% GMV</div></div>
<div class="kpi-grid" id="panel5-kpis"></div>
<div class="chart-grid">
    <div class="chart-box"><h3>👥 RFM 五层分群 · 用户金字塔</h3><div class="chart-canvas-wrap"><canvas id="chart5_rfm"></canvas></div></div>
    <div class="chart-box"><h3>📈 月度 GMV 趋势（25个月）</h3><div class="chart-canvas-wrap"><canvas id="chart5_kpi"></canvas></div></div>
</div>
<div class="chart-grid">
    <div class="chart-box"><h3>📊 用户购买频次分布</h3><div class="chart-canvas-wrap"><canvas id="chart5_freq"></canvas></div></div>
    <div class="chart-box"><h3>⏰ 最近购买天数分布</h3><div class="chart-canvas-wrap"><canvas id="chart5_recency"></canvas></div></div>
</div>
<div class="insight-cards">
    <div class="insight-card growth"><div class="icon">⭐</div><h4>频次弹性 >> 客单价弹性</h4><p>高频83.6次 vs 流失1.9次 = <b>44倍差距</b>。客单价方差极小（99.5%用户锁死在单一价格带）。<b>提升复购是核心增长抓手，比"提价"更有效且风险更低。</b></p></div>
    <div class="insight-card opportunity"><div class="icon">🎯</div><h4>策略优先级</h4><p>① 唤醒23.4%潜在流失（317,557人）→ ② 拉升20.6%活跃用户频次 → ③ 稳住10.5%高价值用户。唤醒+拉升的GMV提升空间 >> 提价。</p></div>
    <div class="insight-card action"><div class="icon">📅</div><h4>月度KPI基线</h4><p>25个月趋势：12月旺季峰值 → 1-2月低谷。线上占比稳定29.6%，周末占比28.6%。周期性规律为推荐推送时机提供依据。</p></div>
</div>
</div>

<!-- PANEL 6: 用户分析 -->
<div id="panel6" class="panel">
<div class="panel-header"><h2>👤 六、用户分析</h2><div class="desc">依托14维特征宽表，挖掘用户品类、价格、时段消费规律，搭建标准化分层用户画像</div></div>
<div class="kpi-grid" id="panel6-kpis"></div>
<div class="chart-grid">
    <div class="chart-box"><h3>📦 全球销量 Top 10 品类</h3><div class="chart-canvas-wrap"><canvas id="chart6_cat"></canvas></div></div>
    <div class="chart-box"><h3>📡 用户渠道偏好分布</h3><div class="chart-canvas-wrap"><canvas id="chart6_channel"></canvas></div></div>
</div>
<div class="chart-grid">
    <div class="chart-box"><h3>💡 品类偏好建模创新</h3>
        <div style="font-size:12px;color:#94a3b8;line-height:2;">
            <p style="color:#60a5fa;font-weight:600;font-size:14px;margin-bottom:8px;">preference_score = user_ratio / global_ratio</p>
            <p>不是"买得多就是喜欢"，而是看相对于全局的偏好程度：</p>
            <p style="margin-top:8px;padding:10px;background:rgba(255,255,255,0.03);border-radius:6px;">
                📌 举例：用户A买了100件商品，其中10件是Ladieswear（占比10%）<br>
                全球Ladieswear占比50% → preference_score = 10%/50% = <b style="color:#ef4444;">0.2</b><br>
                实际上用户A <b style="color:#ef4444;">不偏好</b> Ladieswear！但如果只看绝对次数（10件）会误判
            </p>
            <p style="margin-top:8px;">> 1.0 = 偏好的推荐信号 · > 2.0 = 强推荐信号</p>
        </div>
    </div>
    <div class="chart-box"><h3>🎯 用户画像宽表（14维）</h3>
        <table class="data-table">
            <tr><th>维度</th><th>字段</th><th>用途</th></tr>
            <tr><td>基础</td><td>age_group, club_member_status</td><td>人群细分</td></tr>
            <tr><td>RFM</td><td>recency_days, frequency_total, monetary_total</td><td>价值分层</td></tr>
            <tr><td>品类</td><td>preference_score, unique_departments</td><td>品类偏好</td></tr>
            <tr><td>价格</td><td>price_band, monetary_avg_price</td><td>价格定位</td></tr>
            <tr><td>渠道</td><td>online_ratio, channel_preference</td><td>触达策略</td></tr>
            <tr><td>时间</td><td>weekend_ratio, avg_purchase_interval</td><td>推送时机</td></tr>
        </table>
    </div>
</div>
</div>

<!-- PANEL 7: 渠道分析 -->
<div id="panel7" class="panel">
<div class="panel-header"><h2>📡 七、渠道分析</h2><div class="desc">交叉分析渠道与品类、价格、年龄的消费差异，输出渠道专属推荐方案</div></div>
<div class="kpi-grid" id="panel7-kpis"></div>
<div class="chart-grid">
    <div class="chart-box"><h3>🏪 渠道 × 品类交叉（差异Top10）</h3><div class="chart-canvas-wrap"><canvas id="chart7_dept"></canvas></div></div>
    <div class="chart-box"><h3>👴 各年龄段线上购物偏好</h3><div class="chart-canvas-wrap"><canvas id="chart7_age"></canvas></div></div>
</div>
<div class="chart-grid">
    <div class="chart-box"><h3>💰 渠道 × 价格</h3>
        <div id="panel7-price-viz" style="font-size:12px;margin-top:8px;"></div>
    </div>
    <div class="chart-box"><h3>🚀 分渠道推荐策略</h3>
        <table class="data-table">
            <tr><th>渠道</th><th>推荐策略</th><th>核心逻辑</th></tr>
            <tr><td>🖥️ <b>线上</b></td><td>高性价比基础款 + 高复购品类</td><td>价格敏感、偏好标准化（Jewellery/Knitwear）</td></tr>
            <tr><td>🏪 <b>线下</b></td><td>当季新品 + 趋势款 + 高客单价</td><td>愿为体验付费（Swimwear/Jersey）</td></tr>
            <tr><td>🔄 <b>混合型</b></td><td>根据 online_ratio 动态调整权重</td><td>历史渠道偏好预测当前最相关推荐</td></tr>
        </table>
    </div>
</div>
</div>

<!-- PANEL 8: 推荐策略设计 -->
<div id="panel8" class="panel">
<div class="panel-header"><h2>🎯 八、推荐策略设计</h2><div class="desc">5种推荐策略 + 召回/排序/重排三层架构，按用户状态分层使用</div></div>
<div class="chart-box full-width" style="margin-bottom:24px"><h3>📋 推荐策略矩阵</h3>
    <table class="strategy-table">
        <tr><th>策略</th><th>名称</th><th>适用条件</th><th>推荐位占比</th><th>核心逻辑</th><th>可调参数</th></tr>
        <tr><td>0</td><td>热门兜底</td><td>新用户/无购买</td><td>100%</td><td>全局销量降序Top20</td><td>时间窗口</td></tr>
        <tr><td>1</td><td>混合探索</td><td>购买≤2次</td><td>60%+40%</td><td>热门为主+探索性推荐</td><td>热门/随机比例</td></tr>
        <tr><td>2</td><td>品类偏好</td><td>购买≥3次</td><td>40%（8位）</td><td>preference_score推荐偏好品类热销</td><td>TopN品类数</td></tr>
        <tr><td>3</td><td>价格带</td><td>购买≥3次</td><td>25%（5位）</td><td>匹配用户价格带±1档</td><td>价格箱数量</td></tr>
        <tr><td>4</td><td>协同过滤</td><td>购买≥5次</td><td>25%（5位）</td><td>Jaccard共购相似度</td><td>相似度阈值</td></tr>
        <tr><td>5</td><td>颜色偏好</td><td>购买≥3次</td><td>10%（2位）</td><td>偏好颜色组+同品类热销</td><td>TopN颜色数</td></tr>
    </table>
</div>
<div class="chart-grid">
    <div class="chart-box"><h3>🔍 召回层（10万 → 200）</h3>
        <ul style="font-size:12px;color:#94a3b8;line-height:2;list-style:disc;padding-left:20px;">
            <li><b style="color:#60a5fa">双塔模型(DSSM)</b>：用户塔 + 商品塔 → 128维向量</li>
            <li><b style="color:#00d4aa">FAISS向量检索</b>：10万商品建索引 → Top200</li>
            <li><b style="color:#f59e0b">品类规则召回补充</b>：偏好品类下热销强制进候选</li>
            <li><b style="color:#a78bfa">多样性召回通道</b>：随机采样不同department热门</li>
        </ul>
    </div>
    <div class="chart-box"><h3>📊 排序层（200 → 50）</h3>
        <div style="font-size:12px;color:#94a3b8;line-height:2;">
            <p><b style="color:#60a5fa">多目标排序</b>：CTR(点击率) + CVR(购买率) + ATC(加购率)</p>
            <p style="padding:10px;background:rgba(255,255,255,0.03);border-radius:6px;margin:8px 0;">
                final_score = <b style="color:#00d4aa">0.3</b> × p_ctr + <b style="color:#f59e0b">0.5</b> × p_cvr + <b style="color:#a78bfa">0.2</b> × p_atc
            </p>
            <p>权重来自敏感性分析：CVR权重最高 → 直接指向GMV</p>
        </div>
    </div>
</div>
<div class="chart-box" style="margin-top:24px"><h3>🎛️ 重排层（50 → 20）</h3>
    <table class="data-table">
        <tr><th>规则</th><th>具体操作</th><th>目的</th></tr>
        <tr><td>🔴 库存过滤</td><td>库存 < 阈值的商品降权或移除</td><td>避免推荐买不到的商品</td></tr>
        <tr><td>🟡 新品加权</td><td>冷启动商品(购买≤3次)加权 <b>+15%</b></td><td>给新品曝光机会，均衡库存</td></tr>
        <tr><td>🔵 品类打散</td><td>同品类(department)最多出现 <b>3个</b></td><td>避免推荐列表全是同类</td></tr>
        <tr><td>🟣 价格多样性</td><td>至少保留 <b>2个</b> 价格带的商品</td><td>覆盖不同预算需求</td></tr>
        <tr><td>⚫ 去已购</td><td>过去 <b>7天</b> 已购买的商品降权</td><td>避免重复推荐</td></tr>
    </table>
</div>
</div>

<!-- PANEL 9: A/B测试框架 -->
<div id="panel9" class="panel">
<div class="panel-header"><h2>🧪 九、A/B测试框架</h2><div class="desc">完整实验设计方案 + 7项评估指标体系 + Thompson Sampling持续优化</div></div>
<div class="chart-grid">
    <div class="chart-box"><h3>⚙️ 实验设计方案</h3>
        <table class="data-table">
            <tr><th>要素</th><th>方案</th></tr>
            <tr><td>实验周期</td><td><b>14天</b>（覆盖两个完整周 + 消除新奇效应）</td></tr>
            <tr><td>分流方式</td><td>customer_id 哈希取模 → hash(id)%2==0→A组 / ==1→B组</td></tr>
            <tr><td>对照组 A (50%)</td><td>热门商品兜底推荐（按全局销量降序）</td></tr>
            <tr><td>实验组 B (50%)</td><td>完整推荐系统（品类偏好+价格带+协同过滤+重排）</td></tr>
            <tr><td>AA验证</td><td>上线前两组用相同策略，确认分流均匀无偏</td></tr>
            <tr><td>数据剔除</td><td>前2天标记为"新奇效应期"，分析时做敏感性检验</td></tr>
        </table>
    </div>
    <div class="chart-box"><h3>📏 评估指标体系</h3>
        <table class="data-table">
            <tr><th>层级</th><th>指标</th><th>计算公式</th><th>优先级</th></tr>
            <tr><td>北极星</td><td>人均GMV</td><td>SUM(price)/COUNT(DISTINCT user)</td><td>⭐⭐⭐</td></tr>
            <tr><td>核心</td><td>CTR</td><td>点击次数/曝光次数</td><td>⭐⭐⭐</td></tr>
            <tr><td>核心</td><td>CVR</td><td>购买次数/曝光次数</td><td>⭐⭐⭐</td></tr>
            <tr><td>观察</td><td>覆盖率</td><td>被推荐商品数/总商品数</td><td>⭐⭐</td></tr>
            <tr><td>观察</td><td>多样性</td><td>推荐列表不同department数</td><td>⭐⭐</td></tr>
            <tr><td>观察</td><td>冷启动曝光</td><td>冷启动商品曝光/总曝光</td><td>⭐⭐</td></tr>
            <tr><td>诊断</td><td>客单价</td><td>GMV/购买订单数</td><td>⭐</td></tr>
        </table>
    </div>
</div>
<div class="chart-grid">
    <div class="chart-box"><h3>📊 显著性检验标准</h3>
        <table class="data-table">
            <tr><th>场景</th><th>判断</th><th>行动</th></tr>
            <tr><td>p < 0.05, 提升 > 5%</td><td><span class="tag tag-done">✅ 有效</span></td><td>全量上线</td></tr>
            <tr><td>p < 0.05, 提升 0~5%</td><td><span class="tag tag-progress">⚠️ 微弱</span></td><td>优化后再测</td></tr>
            <tr><td>p < 0.05, 提升 < 0</td><td><span style="color:#ef4444">❌ 有害</span></td><td>立即下线</td></tr>
            <tr><td>p ≥ 0.05</td><td><span style="color:#6b7c93">❓ 不确定</span></td><td>延长实验/加大样本</td></tr>
        </table>
    </div>
    <div class="chart-box"><h3>🎰 MAB 持续优化</h3>
        <div style="font-size:12px;color:#94a3b8;line-height:2;">
            <p><b style="color:#60a5fa">Thompson Sampling</b> 自动调整流量分配：</p>
            <p style="margin-top:8px;">· 每个策略 = 一个"臂"</p>
            <p>· 臂的表现 = Beta分布(购买次数+1, 未购买次数+1)</p>
            <p>· 每次推荐从Beta分布采样 → 选采样值最大的策略</p>
            <p style="margin-top:8px;color:#00d4aa;">效果：好策略自动获更多流量，差策略自动减少，无需人工干预</p>
        </div>
    </div>
</div>
<div class="chart-box" style="margin-top:16px"><h3>🎯 预期效果</h3>
    <table class="data-table">
        <tr><th>指标</th><th>预期提升</th><th>原因</th></tr>
        <tr><td>CTR（点击率）</td><td><span class="highlight">+10~20%</span></td><td>品类偏好让推荐"更对胃口"</td></tr>
        <tr><td>CVR（购买转化率）</td><td><span class="highlight">+8~15%</span></td><td>价格带匹配降低"看了买不起"</td></tr>
        <tr><td>推荐覆盖率</td><td><span class="highlight">+100~300%</span></td><td>从只推热门→推长尾商品</td></tr>
        <tr><td>冷启动商品曝光</td><td><span class="highlight">从0→5%</span></td><td>重排层有意识给新品机会</td></tr>
        <tr><td>人均GMV</td><td><span class="highlight">+5~10%</span></td><td>CVR提升 + 价格带匹配的综合效果</td></tr>
    </table>
</div>
</div>

<!-- PANEL 10: 成果与展望 -->
<div id="panel10" class="panel">
<div class="panel-header"><h2>🏆 十、项目成果与展望</h2><div class="desc">核心数字摘要 · 交付物清单 · 面试追问应答 · 后续规划</div></div>
<div class="chart-grid">
    <div class="chart-box"><h3>🏅 核心数字摘要</h3>
        <table class="data-table">
            <tr><th>分析维度</th><th>核心发现</th></tr>
            <tr><td>数据规模</td><td>137万用户 × 10.5万商品 × 3178万交易（4.2GB）</td></tr>
            <tr><td>商品长尾</td><td><span class="warn">14.8%</span> 商品 ≤5次，<span class="highlight">7.4%</span> 热门贡献 53.5% 销量</td></tr>
            <tr><td>数据修正</td><td>Active: 46万 → <span class="highlight">136万</span>（66%空但99.3%有交易）</td></tr>
            <tr><td>RFM分群</td><td>高价值活跃10.5% · 活跃20.6% · 潜在流失23.4% · 已流失18.8%</td></tr>
            <tr><td>GMV集中度</td><td>仅<span class="highlight">10.5%</span>高价值用户贡献约<span class="highlight">39%</span> GMV</td></tr>
            <tr><td>增长抓手</td><td>频次弹性 >> 客单价弹性 → <b>提升复购是核心</b></td></tr>
            <tr><td>价格带</td><td><span class="highlight">99.5%</span> 用户 ≥80% 购买集中在单一价格带</td></tr>
            <tr><td>渠道</td><td>线上29.6% vs 线下70.4% · 线上客单价=线下<span class="warn">0.77倍</span></td></tr>
        </table>
    </div>
    <div class="chart-box"><h3>📦 交付物清单</h3>
        <table class="data-table">
            <tr><th>交付物</th><th>形式</th><th>状态</th></tr>
            <tr><td>01_data_pipeline.py</td><td>Python · ~400行</td><td><span class="tag tag-done">✅</span></td></tr>
            <tr><td>02_business_analysis.py</td><td>Python · ~600行</td><td><span class="tag tag-done">✅</span></td></tr>
            <tr><td>项目方案_H&M推荐系统.md</td><td>Markdown</td><td><span class="tag tag-done">✅</span></td></tr>
            <tr><td>推荐策略设计文档_基于规则.md</td><td>Markdown</td><td><span class="tag tag-done">✅</span></td></tr>
            <tr><td>数据分析工作思考过程.md</td><td>Markdown</td><td><span class="tag tag-done">✅</span></td></tr>
            <tr><td>processed/ (9 CSV)</td><td>处理后数据 ~4.8GB</td><td><span class="tag tag-done">✅</span></td></tr>
            <tr><td>business_analysis/ (5文件)</td><td>分析结果</td><td><span class="tag tag-done">✅</span></td></tr>
            <tr><td>Tableau Dashboard ×4</td><td>.twbx 工作簿</td><td><span class="tag tag-plan">⏳</span></td></tr>
        </table>
    </div>
</div>
<div class="insight-cards">
    <div class="insight-card growth"><div class="icon">💡</div><h4>Q: "热门垄断、长尾消失怎么解决？"</h4><p>三层开窗策略：① 召回层品类偏好召回(40%位) → ② 重排层冷启动加权15%+品类打散(≤3个) → ③ 长期MAB自动调整流量。核心思想：不消灭热门，而是在热门基础上"开窗"给长尾和新品。</p></div>
    <div class="insight-card opportunity"><div class="icon">📊</div><h4>Q: "怎么确定提升复购比提价更有效？"</h4><p>两个角度：① RFM数据——频次方差44倍（P25=3 vs P90=59），提升空间大；99.5%用户价格带锁定，提价可能流失。② 业务逻辑——快时尚本质"高频低单价"，提价违背品牌定位。</p></div>
    <div class="insight-card action"><div class="icon">🚀</div><h4>Q: "项目最终落地了什么？"</h4><p>三样东西：① 两个可复用Python脚本（数据更新一键重跑） → ② 推荐策略设计文档（算法和产品可直接实现） → ③ 4个Tableau看板+交互HTML看板（运营日常使用，不需找分析师取数）</p></div>
</div>
</div>

</div><!-- END MAIN -->

<!-- ============================================================ -->
<!-- DATA & JS -->
<!-- ============================================================ -->
<script>
const DATA = {data_json_str};

// ============================================================
// Panel switching
// ============================================================
function switchPanel(panelId) {{
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    const panel = document.getElementById(panelId);
    if (panel) panel.classList.add('active');
    document.querySelectorAll('.sidebar-nav a').forEach(a => a.classList.remove('active'));
    const link = document.querySelector(`.sidebar-nav a[href="#${{panelId}}"]`);
    if (link) link.classList.add('active');
    // Trigger chart resize
    setTimeout(() => {{ Object.values(Chart.instances).forEach(c => c.resize()); }}, 100);
}}

// ============================================================
// Common chart options
// ============================================================
function darkOptions(opts = {{}}) {{
    return Object.assign({{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{
            legend: {{ labels: {{ color: '#6b7c93', font: {{ size: 11 }}, padding: 16 }} }},
            tooltip: {{
                backgroundColor: 'rgba(15, 21, 53, 0.95)',
                titleColor: '#ffffff', bodyColor: '#c8d2e0',
                borderColor: 'rgba(96,165,250,0.2)', borderWidth: 1, padding: 12
            }}
        }},
        scales: {{
            x: {{ ticks: {{ color: '#4a5568', font: {{ size: 10 }} }}, grid: {{ color: 'rgba(255,255,255,0.04)' }} }},
            y: {{ ticks: {{ color: '#4a5568', font: {{ size: 10 }} }}, grid: {{ color: 'rgba(255,255,255,0.04)' }} }}
        }}
    }}, opts);
}}

const colors = ['#60a5fa','#00d4aa','#f59e0b','#a78bfa','#ef4444','#34d399','#fbbf24','#818cf8','#fb7185','#38bdf8'];

// ============================================================
// PANEL 4: Business Diagnosis
// ============================================================
(function() {{
    const p4 = DATA.panel4;
    // KPI cards
    document.getElementById('panel4-kpis').innerHTML = `
        <div class="kpi-card accent-red"><div class="kpi-label">长尾商品（≤5次）</div><div class="kpi-value">${p4.below_5_pct}<span style="font-size:16px">%</span></div><div class="kpi-sub">${p4.below_5.toLocaleString()} / ${p4.total_arts.toLocaleString()} SKU</div></div>
        <div class="kpi-card accent-amber"><div class="kpi-label">热门商品（≥1000次）</div><div class="kpi-value">${p4.hot_pct}<span style="font-size:16px">%</span></div><div class="kpi-sub">贡献 ${p4.hot_sales_pct}% 销量</div></div>
        <div class="kpi-card accent-blue"><div class="kpi-label">Active修复前</div><div class="kpi-value">${p4.active_1_before.toLocaleString()}</div><div class="kpi-sub">66%为空（约91万）</div></div>
        <div class="kpi-card accent-green"><div class="kpi-label">Active修复后</div><div class="kpi-value">${p4.active_fixed.toLocaleString()}</div><div class="kpi-sub">${p4.has_txn_pct}% 用户有实际交易</div></div>`;

    // Tier chart
    const tierData = p4.tier_data;
    new Chart(document.getElementById('chart4_tier'), {{
        type: 'bar',
        data: {{
            labels: tierData.map(d => d.tier),
            datasets: [{{
                label: 'SKU 数量', data: tierData.map(d => d.count),
                backgroundColor: ['rgba(239,68,68,0.7)','rgba(245,158,11,0.7)','rgba(96,165,250,0.7)','rgba(0,212,170,0.7)','rgba(167,139,250,0.7)'],
                borderColor: ['rgba(239,68,68,1)','rgba(245,158,11,1)','rgba(96,165,250,1)','rgba(0,212,170,1)','rgba(167,139,250,1)'],
                borderWidth: 1, borderRadius: 4
            }}]
        }},
        options: darkOptions({{ indexAxis: 'y' }})
    }});

    // Active fix chart
    new Chart(document.getElementById('chart4_active'), {{
        type: 'bar',
        data: {{
            labels: ['Active="1.0"', 'Active为空', '修正后活跃'],
            datasets: [
                {{ label: '用户数(万)', data: [${active_1_before/10000:.0f}, ${active_null_before/10000:.0f}, ${active_fixed/10000:.0f}],
                   backgroundColor: ['rgba(96,165,250,0.7)','rgba(239,68,68,0.7)','rgba(0,212,170,0.7)'],
                   borderColor: ['rgba(96,165,250,1)','rgba(239,68,68,1)','rgba(0,212,170,1)'],
                   borderWidth: 1, borderRadius: 4 }}
            ]
        }},
        options: darkOptions()
    }});
}})();

// ============================================================
// PANEL 5: RFM Performance
// ============================================================
(function() {{
    const p5 = DATA.panel5;
    const rfm = p5.rfm_rows;

    document.getElementById('panel5-kpis').innerHTML = rfm.map(r =>
        `<div class="kpi-card ${{['accent-green','accent-blue','accent-amber','accent-red','accent-purple'][rfm.indexOf(r)]}}">
            <div class="kpi-label">${r.segment}</div>
            <div class="kpi-value" style="font-size:24px">${r.user_pct}<span style="font-size:14px">%</span> <span style="font-size:12px;color:#6b7c93;">用户</span></div>
            <div class="kpi-sub">GMV贡献 ${r.gmv_pct}% · 均频 ${r.avg_freq}次</div>
        </div>`
    ).join('');

    // RFM bar
    new Chart(document.getElementById('chart5_rfm'), {{
        type: 'bar',
        data: {{
            labels: rfm.map(r => r.segment),
            datasets: [
                {{ label: '用户占比 %', data: rfm.map(r => r.user_pct),
                   backgroundColor: colors.map(c => c.replace('1)', '0.8)')), borderColor: colors, borderWidth: 1, borderRadius: 4, yAxisID: 'y' }},
                {{ label: 'GMV贡献 %', data: rfm.map(r => r.gmv_pct),
                   backgroundColor: 'rgba(0,212,170,0.3)', borderColor: '#00d4aa', borderWidth: 2, borderDash: [4,4], type: 'line', yAxisID: 'y1' }}
            ]
        }},
        options: darkOptions({{
            scales: {{
                x: {{ ticks: {{ color: '#4a5568', font: {{ size: 11 }} }}, grid: {{ color: 'rgba(255,255,255,0.04)' }} }},
                y: {{ position: 'left', ticks: {{ color: '#60a5fa', font: {{ size: 10 }}, callback: v => v+'%' }}, grid: {{ color: 'rgba(255,255,255,0.04)' }} }},
                y1: {{ position: 'right', ticks: {{ color: '#00d4aa', font: {{ size: 10 }}, callback: v => v+'%' }}, grid: {{ display: false }}, min: 0, max: 55 }}
            }}
        }})
    }});

    // KPI trend
    const kpiRows = p5.kpi_rows;
    new Chart(document.getElementById('chart5_kpi'), {{
        type: 'line',
        data: {{
            labels: kpiRows.map(r => r.month),
            datasets: [{{
                label: 'GMV', data: kpiRows.map(r => r.gmv),
                borderColor: '#60a5fa', backgroundColor: 'rgba(96,165,250,0.05)', borderWidth: 2, fill: true, tension: 0.3, yAxisID: 'y',
                pointRadius: kpiRows.map(r => r.month.includes('-12') ? 7 : (r.month.includes('-01')||r.month.includes('-02') ? 7 : 2)),
                pointBackgroundColor: kpiRows.map(r => r.month.includes('-12') ? '#00d4aa' : (r.month.includes('-01')||r.month.includes('-02') ? '#ef4444' : '#60a5fa'))
            }}]
        }},
        options: darkOptions()
    }});

    // Frequency histogram
    const freqH = p5.freq_hist;
    new Chart(document.getElementById('chart5_freq'), {{
        type: 'bar',
        data: {{
            labels: freqH.map(d => d.range),
            datasets: [{{ label: '用户数', data: freqH.map(d => d.count), backgroundColor: colors.map(c => c.replace('1)','0.7)')), borderColor: colors, borderWidth: 1, borderRadius: 4 }}]
        }},
        options: darkOptions()
    }});

    // Recency histogram
    const recH = p5.rec_hist;
    new Chart(document.getElementById('chart5_recency'), {{
        type: 'bar',
        data: {{
            labels: recH.map(d => d.range),
            datasets: [{{ label: '用户数', data: recH.map(d => d.count), backgroundColor: 'rgba(167,139,250,0.7)', borderColor: '#a78bfa', borderWidth: 1, borderRadius: 4 }}]
        }},
        options: darkOptions()
    }});
}})();

// ============================================================
// PANEL 6: User Analysis
// ============================================================
(function() {{
    const p6 = DATA.panel6;
    document.getElementById('panel6-kpis').innerHTML = `
        <div class="kpi-card accent-blue"><div class="kpi-label">⭐ 价格带集中度</div><div class="kpi-value">99.5<span style="font-size:16px">%</span></div><div class="kpi-sub">用户≥80%购买在单一价格带</div></div>
        <div class="kpi-card accent-green"><div class="kpi-label">🖥️ 线上为主</div><div class="kpi-value">${(p6.online_dom/p6.total_u*100).toFixed(0)}<span style="font-size:16px">%</span></div><div class="kpi-sub">${p6.online_dom.toLocaleString()} 人</div></div>
        <div class="kpi-card accent-amber"><div class="kpi-label">🏪 线下为主</div><div class="kpi-value">${(p6.offline_dom/p6.total_u*100).toFixed(0)}<span style="font-size:16px">%</span></div><div class="kpi-sub">${p6.offline_dom.toLocaleString()} 人</div></div>
        <div class="kpi-card accent-purple"><div class="kpi-label">📅 周末占比</div><div class="kpi-value">${p6.weekend_pct.toFixed(1)}<span style="font-size:16px">%</span></div><div class="kpi-sub">高于均分14.3%的预期</div></div>`;

    // Category chart
    const cats = p6.cat_top10;
    new Chart(document.getElementById('chart6_cat'), {{
        type: 'bar',
        data: {{
            labels: cats.map(d => d.dept),
            datasets: [{{ label: '销量', data: cats.map(d => d.count), backgroundColor: colors.map(c => c.replace('1)','0.7)')), borderColor: colors, borderWidth: 1, borderRadius: 4 }}]
        }},
        options: darkOptions({{ indexAxis: 'y' }})
    }});

    // Channel donut
    new Chart(document.getElementById('chart6_channel'), {{
        type: 'doughnut',
        data: {{
            labels: [`线上为主 ${(p6.online_dom/p6.total_u*100).toFixed(0)}%`, `线下为主 ${(p6.offline_dom/p6.total_u*100).toFixed(0)}%`, `混合渠道 ${(p6.mixed_ch/p6.total_u*100).toFixed(0)}%`],
            datasets: [{{ data: [p6.online_dom, p6.offline_dom, p6.mixed_ch], backgroundColor: ['rgba(96,165,250,0.8)','rgba(0,212,170,0.8)','rgba(245,158,11,0.8)'], borderColor: '#0f1535', borderWidth: 2 }}]
        }},
        options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ labels: {{ color: '#6b7c93', font: {{ size: 11 }}, padding: 14 }} }} }} }}
    }});
}})();

// ============================================================
// PANEL 7: Channel Analysis
// ============================================================
(function() {{
    const p7 = DATA.panel7;
    document.getElementById('panel7-kpis').innerHTML = `
        <div class="kpi-card accent-blue"><div class="kpi-label">线上交易占比</div><div class="kpi-value">${p7.online_txn_pct.toFixed(1)}<span style="font-size:16px">%</span></div><div class="kpi-sub">线下 ${(100-p7.online_txn_pct).toFixed(1)}% · 线上客单价=线下${(p7.price_ratio*100).toFixed(0)}%</div></div>
        <div class="kpi-card accent-green"><div class="kpi-label">线上客单价（归一化）</div><div class="kpi-value" style="font-size:26px">${p7.online_avg_p.toFixed(4)}</div><div class="kpi-sub">归一化价格单位</div></div>
        <div class="kpi-card accent-amber"><div class="kpi-label">线下客单价（归一化）</div><div class="kpi-value" style="font-size:26px">${p7.offline_avg_p.toFixed(4)}</div><div class="kpi-sub">归一化价格单位</div></div>
        <div class="kpi-card accent-purple"><div class="kpi-label">线上/线下价格比</div><div class="kpi-value" style="font-size:26px">${(p7.price_ratio*100).toFixed(0)}<span style="font-size:16px">%</span></div><div class="kpi-sub">线上比价效应明显</div></div>`;

    // Dept diff
    const dd10 = p7.dept_diff10;
    new Chart(document.getElementById('chart7_dept'), {{
        type: 'bar',
        data: {{
            labels: dd10.map(d => d.dept),
            datasets: [
                {{ label: '线上偏高', data: dd10.map(d => d.diff > 0 ? d.diff : 0), backgroundColor: 'rgba(96,165,250,0.7)', borderColor: '#60a5fa', borderWidth: 1, borderRadius: 0, stack: 'stack' }},
                {{ label: '线下偏高', data: dd10.map(d => d.diff < 0 ? Math.abs(d.diff) : 0), backgroundColor: 'rgba(0,212,170,0.7)', borderColor: '#00d4aa', borderWidth: 1, borderRadius: 0, stack: 'stack' }}
            ]
        }},
        options: darkOptions()
    }});

    // Age x channel
    const ageD = p7.age_data;
    new Chart(document.getElementById('chart7_age'), {{
        type: 'bar',
        data: {{
            labels: ageD.map(d => d.age),
            datasets: [{{ label: '线上占比 %', data: ageD.map(d => d.online), backgroundColor: ageD.map((_, i) => colors[i].replace('1)','0.7)')), borderColor: ageD.map((_, i) => colors[i]), borderWidth: 1, borderRadius: 4 }}]
        }},
        options: darkOptions()
    }});

    // Price viz
    document.getElementById('panel7-price-viz').innerHTML = `
        <div style="display:flex;align-items:center;gap:20px;padding:20px 0;">
            <div style="text-align:center;flex:1;">
                <div style="font-size:28px;font-weight:700;color:#60a5fa;">🖥️ 线上</div>
                <div style="font-size:20px;color:#ffffff;">${p7.online_avg_p.toFixed(5)}</div>
                <div style="font-size:11px;color:#4a5568;">归一化客单价</div>
            </div>
            <div style="font-size:24px;color:#4a5568;">×${p7.price_ratio.toFixed(2)}</div>
            <div style="text-align:center;flex:1;">
                <div style="font-size:28px;font-weight:700;color:#00d4aa;">🏪 线下</div>
                <div style="font-size:20px;color:#ffffff;">${p7.offline_avg_p.toFixed(5)}</div>
                <div style="font-size:11px;color:#4a5568;">归一化客单价</div>
            </div>
        </div>
        <p style="font-size:11px;color:#6b7c93;text-align:center;">线上客单价为线下 <b style="color:#f59e0b;">${(p7.price_ratio*100).toFixed(0)}%</b> · 符合"线上比价、线下体验"行为逻辑</p>`;
}})();

// ============================================================
// INIT
// ============================================================
// Fix sidebar links to use onclick
document.querySelectorAll('.sidebar-nav a').forEach(a => {{
    a.addEventListener('click', function(e) {{
        e.preventDefault();
        const href = this.getAttribute('href').replace('#', '');
        switchPanel(href);
    }});
}});

// Set canvas heights
document.querySelectorAll('.chart-canvas-wrap canvas').forEach(c => {{
    c.parentElement.style.height = '280px';
}});
</script>

</body>
</html>
'''

html_path = os.path.join(OUTPUT_DIR, 'index.html')
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'  ✅ index.html ({os.path.getsize(html_path)/1024:.1f} KB)')

print(f'\n✅ 全阶段交互看板生成完毕!')
print(f'📁 输出目录: {os.path.abspath(OUTPUT_DIR)}/')
print(f'   ├── index.html           ← 浏览器打开（主看板）')
print(f'   └── dashboard_data.json  ← 数据文件')

# ============================================================
# H&M Boss Dashboard Generator
# 产出:
#   1. boss_dashboard.html — HTML 看板(深色专业风格)
#   2. boss_dashboard_kpi.csv — Tableau 月度KPI数据
#   3. boss_dashboard_segments.csv — Tableau RFM分群数据
#   4. boss_dashboard_insights.csv — Tableau 结论卡数据
# 用法: python 03_boss_dashboard.py
# ============================================================

import pandas as pd
import numpy as np
import os, json
from datetime import datetime

DATA_DIR = 'processed'
OUTPUT_DIR = 'boss_dashboard'
os.makedirs(OUTPUT_DIR, exist_ok=True)

PROJ = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# Step 1: 加载现有数据
# ============================================================
print('>>> 加载数据...')
kpi = pd.read_csv(os.path.join(DATA_DIR, 'tableau_monthly_kpi.csv'))
seg = pd.read_csv(os.path.join(DATA_DIR, 'tableau_user_segments.csv'))

# ============================================================
# Step 2: 计算衍生指标
# ============================================================
print('>>> 计算衍生指标...')

# --- 月度KPI增强 ---
kpi = kpi.sort_values('year_month')
kpi['month_label'] = pd.to_datetime(kpi['year_month'] + '-01').dt.strftime('%Y-%m')

# 环比变化
kpi['transactions_mom'] = kpi['transactions'].pct_change() * 100
kpi['active_users_mom'] = kpi['active_users'].pct_change() * 100
kpi['total_revenue_mom'] = kpi['total_revenue'].pct_change() * 100

# 人均频次
kpi['avg_frequency'] = kpi['transactions'] / kpi['active_users']

# 最新月 & 上个月
latest = kpi.iloc[-1]
prev = kpi.iloc[-2]
prev_12m = kpi.iloc[-13] if len(kpi) >= 13 else kpi.iloc[0]

# 12月 & 1-2月 均值
dec_avg = kpi[kpi['year_month'].str.contains('-12')]['transactions'].mean()
jan_avg = kpi[kpi['year_month'].str.contains('-01')]['transactions'].mean()
feb_avg = kpi[kpi['year_month'].str.contains('-02')]['transactions'].mean()

# --- RFM分群汇总 ---
rfm_agg = seg.groupby('rfm_segment').agg(
    users=('customer_id', 'count'),
    total_gmv=('monetary_total', 'sum'),
    avg_frequency=('frequency_total', 'mean'),
    avg_recency=('recency_days', 'mean'),
).reset_index()
rfm_agg = rfm_agg[rfm_agg['rfm_segment'] != '无交易']

total_users = rfm_agg['users'].sum()
total_gmv = rfm_agg['total_gmv'].sum()
rfm_agg['user_pct'] = rfm_agg['users'] / total_users * 100
rfm_agg['gmv_pct'] = rfm_agg['total_gmv'] / total_gmv * 100

# 排序
seg_order = ['高价值活跃', '活跃用户', '潜在流失', '已流失', '一般用户']
rfm_agg['sort_order'] = rfm_agg['rfm_segment'].apply(lambda x: seg_order.index(x) if x in seg_order else 99)
rfm_agg = rfm_agg.sort_values('sort_order')

# 提取关键数字
high_val = rfm_agg[rfm_agg['rfm_segment'] == '高价值活跃']
latent = rfm_agg[rfm_agg['rfm_segment'] == '潜在流失']
active = rfm_agg[rfm_agg['rfm_segment'] == '活跃用户']

hv_gmv_pct = high_val.iloc[0]['gmv_pct'] if len(high_val) > 0 else 0
latent_pct = latent.iloc[0]['user_pct'] if len(latent) > 0 else 0
latent_users = int(latent.iloc[0]['users']) if len(latent) > 0 else 0
active_pct = active.iloc[0]['user_pct'] if len(active) > 0 else 0

# 频次 & 价格带关键数字
online_pct = kpi['online_pct'].mean()
offline_pct = 100 - online_pct
weekend_pct = kpi['weekend_pct'].mean()

# 渠道用户分布
online_dom = (seg['online_ratio'] > 0.7).sum() / len(seg) * 100
offline_dom = (seg['online_ratio'] < 0.3).sum() / len(seg) * 100
mixed = 100 - online_dom - offline_dom

# ============================================================
# Step 3: 生成 Tableau CSV
# ============================================================
print('>>> 生成 Tableau 数据文件 (兼容 2019.2)...')

# --- CSV 1: 月度KPI ---
boss_kpi = kpi[['year_month', 'month_label', 'transactions', 'active_users',
                 'total_revenue', 'avg_price', 'avg_frequency',
                 'online_pct', 'weekend_pct',
                 'transactions_mom', 'active_users_mom', 'total_revenue_mom']].copy()
boss_kpi.columns = ['年月', '月份标签', '交易量', '活跃用户数', 'GMV', '客单价',
                     '人均频次', '线上占比%', '周末占比%',
                     '交易量环比%', '活跃用户环比%', 'GMV环比%']
boss_kpi.to_csv(os.path.join(OUTPUT_DIR, 'boss_dashboard_kpi.csv'), index=False, encoding='utf-8-sig')
print(f'  ✅ boss_dashboard_kpi.csv ({len(boss_kpi)} 行)')

# --- CSV 2: RFM分群 ---
boss_seg = rfm_agg[['rfm_segment', 'users', 'user_pct', 'gmv_pct', 'avg_frequency', 'avg_recency']].copy()
boss_seg.columns = ['RFM分群', '用户数', '用户占比%', 'GMV占比%', '平均购买频次', '平均最近购买天数']
boss_seg.to_csv(os.path.join(OUTPUT_DIR, 'boss_dashboard_segments.csv'), index=False, encoding='utf-8-sig')
print(f'  ✅ boss_dashboard_segments.csv ({len(boss_seg)} 行)')

# --- CSV 3: 结论卡 ---
boss_insights = pd.DataFrame([
    {
        '结论ID': 'INSIGHT_01',
        '标题': '增长抓手：提升复购频次',
        '结论': f'频次弹性远大于客单价弹性。99.5%用户购买集中在单一价格带，提价空间有限。高价值用户均频83.6次 vs 已流失1.9次，拉升复购空间明确。',
        '类型': '增长',
        '优先级': 1,
    },
    {
        '结论ID': 'INSIGHT_02',
        '标题': f'最大机会：唤醒{latent_pct:.0f}%潜在流失用户',
        '结论': f'{latent_users:,}人处于潜在流失状态，占比{latent_pct:.1f}%。这批用户有购买历史、有品牌认知，唤醒成本远低于拉新，是ROI最高的增长机会。',
        '类型': '机会',
        '优先级': 2,
    },
    {
        '结论ID': 'INSIGHT_03',
        '标题': '行动建议：渠道差异化推荐',
        '结论': f'线上客单价为线下0.77倍 → 线上主推平价基础款+高复购品类，线下主推当季新品+趋势款。{online_dom:.0f}%线上型用户和{offline_dom:.0f}%线下型用户应有两套推荐策略。',
        '类型': '行动',
        '优先级': 3,
    },
])
boss_insights.to_csv(os.path.join(OUTPUT_DIR, 'boss_dashboard_insights.csv'), index=False, encoding='utf-8-sig')
print(f'  ✅ boss_dashboard_insights.csv ({len(boss_insights)} 行)')

# ============================================================
# Step 4: 生成 HTML Boss 看板
# ============================================================
print('>>> 生成 HTML Boss 看板...')

# 准备图表数据
months_json = json.dumps(boss_kpi['月份标签'].tolist(), ensure_ascii=False)
gmv_json = json.dumps([round(x, 1) for x in boss_kpi['GMV'].tolist()])
txn_json = json.dumps([int(x) for x in boss_kpi['交易量'].tolist()])
freq_json = json.dumps([round(x, 2) for x in boss_kpi['人均频次'].tolist()])

# 标注12月和1-2月的索引
dec_indices = [i for i, m in enumerate(boss_kpi['年月'].tolist()) if '-12' in str(m)]
jan_indices = [i for i, m in enumerate(boss_kpi['年月'].tolist()) if '-01' in str(m)]
feb_indices = [i for i, m in enumerate(boss_kpi['年月'].tolist()) if '-02' in str(m)]
dec_idx_json = json.dumps(dec_indices)
jan_idx_json = json.dumps(jan_indices)
feb_idx_json = json.dumps(feb_indices)

# RFM 数据
seg_labels = json.dumps(boss_seg['RFM分群'].tolist(), ensure_ascii=False)
seg_users_pct = json.dumps([round(x, 1) for x in boss_seg['用户占比%'].tolist()])
seg_gmv_pct = json.dumps([round(x, 0) for x in boss_seg['GMV占比%'].tolist()])
seg_freq = json.dumps([round(x, 1) for x in boss_seg['平均购买频次'].tolist()])

# KPI 数字(最新月/汇总)
latest_month = boss_kpi['年月'].iloc[-1]
prev_month = boss_kpi['年月'].iloc[-2]
total_gmv_k = boss_kpi['GMV'].iloc[-1]
total_users_k = boss_kpi['活跃用户数'].iloc[-1] / 10000
avg_freq_val = boss_kpi['人均频次'].iloc[-1]
online_val = boss_kpi['线上占比%'].iloc[-1]
online_mom = boss_kpi['线上占比%'].iloc[-1] - boss_kpi['线上占比%'].iloc[-2]

monthly_active = int(boss_kpi['活跃用户数'].mean())

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1400, initial-scale=1.0">
<title>H&M Boss Dashboard — GMV Growth Command Center</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
    background: #0a0e27;
    color: #e0e6ed;
    min-height: 100vh;
    padding: 20px;
}}
.dashboard {{
    max-width: 1400px;
    margin: 0 auto;
}}
.header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 10px 20px 10px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 24px;
}}
.header h1 {{
    font-size: 24px;
    font-weight: 600;
    color: #ffffff;
    letter-spacing: 1px;
}}
.header .subtitle {{
    font-size: 12px;
    color: #6b7c93;
    letter-spacing: 0.5px;
}}
.header .update-time {{
    font-size: 11px;
    color: #4a5568;
    text-align: right;
}}
.header .update-time span {{
    display: block;
}}
/* KPI Row */
.kpi-row {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
}}
.kpi-card {{
    background: linear-gradient(135deg, #131a3a 0%, #0f1535 100%);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 24px 28px;
    position: relative;
    overflow: hidden;
}}
.kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px;
    height: 100%;
    border-radius: 2px;
}}
.kpi-card:nth-child(1)::before {{ background: #00d4aa; }}
.kpi-card:nth-child(2)::before {{ background: #60a5fa; }}
.kpi-card:nth-child(3)::before {{ background: #f59e0b; }}
.kpi-card:nth-child(4)::before {{ background: #a78bfa; }}

.kpi-label {{
    font-size: 13px;
    color: #6b7c93;
    margin-bottom: 8px;
    letter-spacing: 0.5px;
}}
.kpi-value {{
    font-size: 36px;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.1;
    margin-bottom: 6px;
}}
.kpi-mom {{
    font-size: 13px;
    font-weight: 500;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}}
.kpi-mom.up {{ color: #00d4aa; }}
.kpi-mom.down {{ color: #ef4444; }}
.kpi-mom.flat {{ color: #6b7c93; }}
.kpi-sub {{
    font-size: 11px;
    color: #4a5568;
    margin-top: 4px;
}}
/* Chart Row */
.chart-row {{
    display: grid;
    grid-template-columns: 1.3fr 0.7fr;
    gap: 16px;
    margin-bottom: 24px;
}}
.chart-box {{
    background: linear-gradient(135deg, #131a3a 0%, #0f1535 100%);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 24px 28px;
}}
.chart-box h3 {{
    font-size: 15px;
    font-weight: 600;
    color: #c8d2e0;
    margin-bottom: 16px;
    letter-spacing: 0.5px;
}}
.chart-container {{
    position: relative;
    width: 100%;
}}
.chart-container canvas {{
    width: 100% !important;
}}
/* Insight Row */
.insight-row {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
}}
.insight-card {{
    border-radius: 12px;
    padding: 24px 28px;
    border: 1px solid rgba(255,255,255,0.06);
}}
.insight-card.growth {{
    background: linear-gradient(135deg, rgba(0,212,170,0.08) 0%, rgba(0,212,170,0.03) 100%);
    border-color: rgba(0,212,170,0.15);
}}
.insight-card.opportunity {{
    background: linear-gradient(135deg, rgba(245,158,11,0.08) 0%, rgba(245,158,11,0.03) 100%);
    border-color: rgba(245,158,11,0.15);
}}
.insight-card.action {{
    background: linear-gradient(135deg, rgba(96,165,250,0.08) 0%, rgba(96,165,250,0.03) 100%);
    border-color: rgba(96,165,250,0.15);
}}
.insight-icon {{
    font-size: 24px;
    margin-bottom: 10px;
}}
.insight-card h4 {{
    font-size: 15px;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 10px;
    letter-spacing: 0.5px;
}}
.insight-card p {{
    font-size: 13px;
    color: #94a3b8;
    line-height: 1.6;
}}
/* Responsive */
@media (max-width: 1200px) {{
    .chart-row {{ grid-template-columns: 1fr; }}
    .kpi-row {{ grid-template-columns: repeat(2, 1fr); }}
    .insight-row {{ grid-template-columns: 1fr; }}
}}
@media (max-width: 768px) {{
    .kpi-row {{ grid-template-columns: 1fr; }}
    .kpi-value {{ font-size: 28px; }}
}}
</style>
</head>
<body>
<div class="dashboard">

<!-- Header -->
<div class="header">
    <div>
        <h1>H&M 经营分析 · GMV 增长指挥舱</h1>
        <div class="subtitle">数据来源：2018-09 ~ 2020-09 · 137万用户 · 3178万交易</div>
    </div>
    <div class="update-time">
        <span>数据更新</span>
        <span>{latest_month}</span>
    </div>
</div>

<!-- KPI Row -->
<div class="kpi-row">
    <div class="kpi-card">
        <div class="kpi-label">月均 GMV（归一化）</div>
        <div class="kpi-value">{total_gmv_k:,.0f}</div>
        <div class="kpi-mom {'up' if boss_kpi['GMV环比%'].iloc[-1] > 0 else 'down'}">
            {'▲' if boss_kpi['GMV环比%'].iloc[-1] > 0 else '▼'} {abs(boss_kpi['GMV环比%'].iloc[-1]):.1f}%
        </div>
        <div class="kpi-sub">vs {prev_month}</div>
    </div>

    <div class="kpi-card">
        <div class="kpi-label">月均活跃用户</div>
        <div class="kpi-value">{monthly_active/10000:.0f}<span style="font-size:16px;font-weight:400;color:#6b7c93;"> 万</span></div>
        <div class="kpi-mom {'up' if boss_kpi['活跃用户环比%'].iloc[-1] > 0 else 'down'}">
            {'▲' if boss_kpi['活跃用户环比%'].iloc[-1] > 0 else '▼'} {abs(boss_kpi['活跃用户环比%'].iloc[-1]):.1f}%
        </div>
        <div class="kpi-sub">总注册：137万 · 修正后活跃：136万</div>
    </div>

    <div class="kpi-card">
        <div class="kpi-label">人均月购买频次</div>
        <div class="kpi-value">{avg_freq_val:.1f}<span style="font-size:16px;font-weight:400;color:#6b7c93;"> 次/月</span></div>
        <div class="kpi-mom {'up' if boss_kpi['交易量环比%'].iloc[-1] > 0 else 'down'}">
            {'▲' if boss_kpi['交易量环比%'].iloc[-1] > 0 else '▼'} {abs(boss_kpi['交易量环比%'].iloc[-1]):.1f}%
        </div>
        <div class="kpi-sub">高频用户均频 83.6 · 流失用户 1.9</div>
    </div>

    <div class="kpi-card">
        <div class="kpi-label">线上渠道占比</div>
        <div class="kpi-value">{online_val:.1f}<span style="font-size:16px;font-weight:400;color:#6b7c93;">%</span></div>
        <div class="kpi-mom {'up' if online_mom > 0 else 'down'}">
            {'▲' if online_mom > 0 else '▼'} {abs(online_mom):.1f}pp
        </div>
        <div class="kpi-sub">线上为主{online_dom:.0f}% · 线下为主{offline_dom:.0f}%</div>
    </div>
</div>

<!-- Chart Row -->
<div class="chart-row">
    <div class="chart-box">
        <h3>📈 月度 GMV 趋势（25个月）</h3>
        <div class="chart-container">
            <canvas id="gmvChart"></canvas>
        </div>
    </div>
    <div class="chart-box">
        <h3>👥 RFM 用户价值金字塔</h3>
        <div class="chart-container">
            <canvas id="rfmChart"></canvas>
        </div>
    </div>
</div>

<!-- Insight Row -->
<div class="insight-row">
    <div class="insight-card growth">
        <div class="insight-icon">🟢</div>
        <h4>增长抓手：提升复购频次</h4>
        <p>频次弹性 >> 客单价弹性。99.5% 用户购买集中在单一价格带——提价空间有限且风险高。高价值活跃用户均频 <b style="color:#00d4aa;">83.6次</b> vs 已流失用户 <b style="color:#ef4444;">1.9次</b>，44 倍差距 = 44 倍增长空间。拉升 20.6% 活跃用户 + 23.4% 潜在流失用户的购买频次，是最高 ROl 的增长路径。</p>
    </div>
    <div class="insight-card opportunity">
        <div class="insight-icon">🟡</div>
        <h4>最大机会：唤醒 {latent_pct:.0f}% 潜在流失</h4>
        <p><b style="color:#f59e0b;">{latent_users:,}</b> 用户处于潜在流失状态，占总用户 {latent_pct:.1f}%。这批用户有购买历史、有品牌认知，唤醒成本远低于拉新。配合个性化推荐 + 品类偏好召回，预估可挽回其中 15-25% 的用户回到活跃状态。</p>
    </div>
    <div class="insight-card action">
        <div class="insight-icon">🔵</div>
        <h4>行动建议：渠道差异化推荐</h4>
        <p>线上客单价仅为线下 <b style="color:#60a5fa;">0.77 倍</b> → 线上主推平价基础款 + 高复购品类（Jewellery / Knitwear）；线下主推当季新品 + 趋势款（Swimwear / Jersey）。<b>{online_dom:.0f}%</b> 线上型用户和 <b>{offline_dom:.0f}%</b> 线下型用户应有两套独立的推荐策略。</p>
    </div>
</div>

</div>

<script>
// ============================================================
// Chart 1: 月度 GMV 趋势
// ============================================================
const ctx1 = document.getElementById('gmvChart').getContext('2d');
const months = {months_json};
const gmvData = {gmv_json};
const decIndices = {dec_idx_json};
const janIndices = {jan_idx_json};
const febIndices = {feb_idx_json};

// Build point colors
const pointColors = gmvData.map((_, i) => {{
    if (decIndices.includes(i)) return '#00d4aa';
    if (janIndices.includes(i) || febIndices.includes(i)) return '#ef4444';
    return '#60a5fa';
}});
const pointSizes = gmvData.map((_, i) => {{
    if (decIndices.includes(i)) return 8;
    if (janIndices.includes(i) || febIndices.includes(i)) return 8;
    return 3;
}});

new Chart(ctx1, {{
    type: 'line',
    data: {{
        labels: months,
        datasets: [{{
            label: 'GMV (归一化)',
            data: gmvData,
            borderColor: '#60a5fa',
            backgroundColor: 'rgba(96, 165, 250, 0.08)',
            borderWidth: 2,
            fill: true,
            tension: 0.3,
            pointBackgroundColor: pointColors,
            pointBorderColor: pointColors,
            pointRadius: pointSizes,
            pointHoverRadius: 8,
        }}]
    }},
    options: {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{
            legend: {{ display: false }},
            tooltip: {{
                backgroundColor: 'rgba(15, 21, 53, 0.95)',
                titleColor: '#ffffff',
                bodyColor: '#c8d2e0',
                borderColor: 'rgba(96, 165, 250, 0.2)',
                borderWidth: 1,
                padding: 12,
                callbacks: {{
                    label: function(ctx) {{
                        let label = 'GMV: ' + ctx.parsed.y.toLocaleString();
                        const m = months[ctx.dataIndex];
                        if (m.includes('-12')) label += '  🎄 旺季';
                        if (m.includes('-01') || m.includes('-02')) label += '  📉 低谷';
                        return label;
                    }}
                }}
            }}
        }},
        scales: {{
            x: {{
                ticks: {{
                    color: '#4a5568',
                    font: {{ size: 10 }},
                    maxTicksLimit: 13,
                    callback: function(val, index) {{
                        const m = this.getLabelForValue(val);
                        return m.endsWith('-01') || m.endsWith('-07') ? m : '';
                    }}
                }},
                grid: {{ color: 'rgba(255,255,255,0.04)' }}
            }},
            y: {{
                ticks: {{
                    color: '#4a5568',
                    font: {{ size: 10 }},
                    callback: v => v.toLocaleString()
                }},
                grid: {{ color: 'rgba(255,255,255,0.04)' }}
            }}
        }},
        interaction: {{
            intersect: false,
            mode: 'index'
        }}
    }}
}});

// ============================================================
// Chart 2: RFM 用户价值金字塔 (水平条形)
// ============================================================
const ctx2 = document.getElementById('rfmChart').getContext('2d');
const segLabels = {seg_labels};
const segUsersPct = {seg_users_pct};
const segGmvPct = {seg_gmv_pct};
const segFreq = {seg_freq};

// 颜色
const barColors = [
    'rgba(0, 212, 170, 0.85)',
    'rgba(96, 165, 250, 0.85)',
    'rgba(245, 158, 11, 0.85)',
    'rgba(239, 68, 68, 0.70)',
    'rgba(107, 124, 147, 0.65)',
];

new Chart(ctx2, {{
    type: 'bar',
    data: {{
        labels: segLabels,
        datasets: [{{
            label: '用户占比 %',
            data: segUsersPct,
            backgroundColor: barColors,
            borderColor: barColors.map(c => c.replace('0.85', '1').replace('0.70', '0.9').replace('0.65', '0.85')),
            borderWidth: 1,
            borderRadius: 4,
            borderSkipped: false,
        }}]
    }},
    options: {{
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{
            legend: {{ display: false }},
            tooltip: {{
                backgroundColor: 'rgba(15, 21, 53, 0.95)',
                titleColor: '#ffffff',
                bodyColor: '#c8d2e0',
                borderColor: 'rgba(255,255,255,0.1)',
                borderWidth: 1,
                padding: 12,
                callbacks: {{
                    label: function(ctx) {{
                        const i = ctx.dataIndex;
                        return [
                            '用户占比: ' + segUsersPct[i].toFixed(1) + '%',
                            'GMV贡献: ' + segGmvPct[i].toFixed(0) + '%',
                            '平均频次: ' + segFreq[i].toFixed(1) + ' 次'
                        ];
                    }}
                }}
            }}
        }},
        scales: {{
            x: {{
                ticks: {{
                    color: '#4a5568',
                    font: {{ size: 10 }},
                    callback: v => v + '%'
                }},
                grid: {{ color: 'rgba(255,255,255,0.04)' }},
                max: 35
            }},
            y: {{
                ticks: {{
                    color: '#c8d2e0',
                    font: {{ size: 11, weight: '500' }}
                }},
                grid: {{ display: false }}
            }}
        }}
    }}
}});

// Set canvas height
document.getElementById('gmvChart').parentElement.style.height = '320px';
document.getElementById('rfmChart').parentElement.style.height = '320px';
</script>

</body>
</html>
'''

html_path = os.path.join(OUTPUT_DIR, 'boss_dashboard.html')
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'  ✅ boss_dashboard.html ({os.path.getsize(html_path)/1024:.1f} KB)')

# ============================================================
# Done
# ============================================================
print(f'\n✅ Boss Dashboard 生成完毕!')
print(f'📁 输出目录: {os.path.abspath(OUTPUT_DIR)}/')
print(f'   ├── boss_dashboard.html        → 浏览器打开即看')
print(f'   ├── boss_dashboard_kpi.csv     → Tableau: 月度KPI趋势')
print(f'   ├── boss_dashboard_segments.csv → Tableau: RFM金字塔')
print(f'   └── boss_dashboard_insights.csv → Tableau: 结论文本')

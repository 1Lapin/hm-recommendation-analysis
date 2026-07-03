# H&M 个性化推荐策略 — 经营分析项目

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.3-green)](https://pandas.pydata.org/)
[![Tableau](https://img.shields.io/badge/Tableau-Dashboard-orange)](https://www.tableau.com/)

> **基于 137万用户 × 10.5万商品 × 3178万条交易数据，从0到1构建数据驱动的推荐策略体系**

---

## 📊 项目概览

| 维度 | 数据 |
|------|------|
| 数据来源 | [Kaggle - H&M Personalized Fashion Recommendations](https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations) |
| 时间跨度 | 2018-09-20 ~ 2020-09-22（27个月） |
| 用户规模 | 1,371,980 用户 |
| 商品规模 | 105,542 SKU |
| 交易记录 | 31,788,324 行（4.2GB） |
| 原始文件 | articles.csv / customers.csv / transactions_train.csv |

---

## 🏗️ 项目结构

```
项目5-H$M/
│
├── 📜 01_data_pipeline.py              # 数据管道（6步，~37分钟）
│       ├── Step 1: 加载原始数据
│       ├── Step 2: 清洗 articles → dim_article
│       ├── Step 3: 清洗 customers → dim_customer（Active字段修复）
│       ├── Step 4: 处理 transactions → fact_transaction（训练/验证集划分）
│       ├── Step 5: RFM 用户特征（20字段，5类分群）
│       └── Step 6: 商品协同特征（15字段，趋势/回购率/购买者画像）
│
├── 📜 02_business_analysis.py          # 经营分析脚本（~8分钟）
│       ├── ◆ 业务诊断（商品结构/用户数据/核心矛盾）
│       ├── ◆ 绩效拆解（RFM分群GMV/频次vs客单价/月度KPI）
│       ├── ◆ 用户分析（品类偏好/价格带/渠道/时间规律）
│       └── ◆ 渠道分析（品类×渠道/价格×渠道/年龄×渠道）
│
├── 📄 项目方案_H&M推荐系统.md           # 总体技术方案（6层架构）
├── 📄 推荐策略设计文档_基于规则.md       # 5种推荐策略 + A/B测试框架
├── 📄 数据分析工作思考过程.md           # 数据思维过程（给团队）
├── 📄 简历项目描述_四版适配.md           # 4版简历（治理/监控/经营/产品）
├── 📄 简历项目描述_经营分析_终版.md       # 经营分析版简历（数字验证版）
├── 📄 README.md                        # 本文件
├── 📄 .gitignore                       # 只提交代码和文档
│
└── 📁 processed/                        # 数据管道输出（不入库，太大）
    ├── dim_customer.csv                 (137万行, 269MB)
    ├── dim_article.csv                  (10.5万行, 43MB)
    ├── fact_transaction.csv             (3178万行, 4.2GB)
    ├── feature_user_rfm.csv             (136万行, 273MB)
    ├── feature_article_stats.csv        (10.4万行, 15MB)
    ├── tableau_monthly_kpi.csv          (25行)
    ├── tableau_user_segments.csv        (137万行, 197MB)
    ├── tableau_category_sales.csv       (7K行, 1.2MB)
    └── tableau_article_trends.csv       (10.5万行, 19MB)

📁 business_analysis/                    # 经营分析输出（不入库，可选）
    ├── analysis_rfm_segment_gmv.csv
    ├── analysis_channel_dept.csv
    ├── analysis_age_channel.csv
    ├── analysis_monthly_kpi.csv
    └── analysis_summary.json
```

---

## 🚀 快速开始

### 1. 下载数据

从 [Kaggle](https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations/data) 下载以下文件并放到项目根目录：

- `articles.csv`
- `customers.csv`
- `transactions_train.csv`

### 2. 安装依赖

```bash
pip install pandas numpy
```

### 3. 运行数据管道

```bash
python 01_data_pipeline.py
```

预计耗时 **35-40分钟**（transactions 有 3300万行）。输出到 `processed/` 目录。

### 4. 运行经营分析

```bash
python 02_business_analysis.py
```

预计耗时 **6-8分钟**。输出到 `business_analysis/` 目录。

---

## 📈 核心分析发现

### 业务诊断
- **14.8%** 商品购买 ≤5次 → 长尾积压
- **7.4%** 热门商品贡献 **53.5%** 销量 → 热门垄断
- **66%** 用户 Active 标签为空但 **99.3%** 有交易 → 数据逻辑矛盾

### 绩效拆解
- 仅 **10.5%** 高价值用户贡献约 **39%** GMV
- 频次弹性 > 客单价弹性 → **提升复购是核心增长抓手**
- 高价值活跃用户均频 **83.6次** vs 已流失 **1.9次**

### 用户分析
- **99.5%** 用户购买集中在单一价格带
- 线上为主的用户 **26.1%**，线下为主 **60.0%**，混合 **14.0%**
- 周末购买占比 **28.6%**

### 渠道分析
- 线上客单价为线下的 **0.77倍**（比价效应）
- 线上偏 Jewellery/Knitwear → **基础款**
- 线下偏 Swimwear/Jersey → **趋势款**

---

## 🛠️ 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| 数据处理 | Python (Pandas 2.3, NumPy) | 3300万行ETL |
| 特征工程 | Python (Pandas) | RFM 20维 + 商品 15维 |
| 可视化 | Tableau | 4张Dashboard（KPI/用户/品类/商品） |
| 文档 | Markdown | 技术方案 + 策略设计 + 分析思考 |
| 版本控制 | Git + GitHub | 代码和文档管理 |

---

## 📋 数据模型（星型模型）

```
                    ┌─────────────────┐
                    │ fact_transaction │
                    │  31,788,324 行   │
                    │  ─────────────── │
                    │  customer_id FK  │────────┐
                    │  article_id FK   │────┐   │
                    │  t_dat           │    │   │
                    │  price           │    │   │
                    │  sales_channel_id │   │   │
                    └─────────────────┘    │   │
                              │            │   │
           ┌──────────────────┼────────────┘   │
           ▼                  ▼                ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ dim_article   │  │ dim_customer  │  │ feature_rfm   │
    │  105,542 行   │  │ 1,371,980 行 │  │ 1,356,132 行 │
    │  ──────────── │  │  ──────────── │  │  ──────────── │
    │  article_id PK│  │  customer_id PK│  │  rfm_segment  │
    │  category_path│  │  age_group    │  │  recency_days │
    │  popularity   │  │  is_active    │  │  frequency    │
    │  trend_dir    │  │  club_member  │  │  monetary     │
    └──────────────┘  └──────────────┘  └──────────────┘
```

---

## 📝 许可证

MIT License — 仅供学习和面试展示使用。数据归 H&M / Kaggle 所有。

---

## 👤 作者

数据分析项目 — 经营分析方向

**关键词**：RFM分析、用户分群、渠道分析、品类偏好、价格带分析、A/B测试设计、Tableau看板

export const STAGES = [
  {
    id: "diagnosis",
    num: "01",
    title: "业务诊断",
    subtitle: "发现矛盾",
    tag: "诊断",
    tagColor: "text-amber bg-amber/10",
    problem: "H&M 面临商品长尾积压、用户留存不稳定、推荐缺乏个性化三大挑战。必须先从数据中诊断根因。",
    methods: [
      "商品热度分层分析 — 按购买次数将10.5万SKU分为5层",
      "数据质量审计 — 交叉验证用户标签与交易行为",
      "贡献度结构分析 — 识别热门商品集中度",
    ],
    findings: [
      { value: "14.8%", label: "商品购买 ≤5次，形成长尾积压" },
      { value: "7.4%", label: "热门商品贡献 53.5% 销量" },
      { value: "66%→修复", label: "Active标签错误，46万→136万" },
    ],
    insight:
      "核心矛盾定位：「热门商品垄断、长尾商品曝光不足」的恶性循环。首页千篇一律，新品永无出头之日。",
    recommendations: [
      { action: "长尾激活计划", detail: "对购买≤5次的9万+ SKU建立曝光加权机制，首页推荐位强制至少30%冷门商品位" },
      { action: "数据修复优先", detail: "修复Active标签后用户池从46万→136万，立即基于修正数据重新计算推荐候选池" },
      { action: "热度分层运营", detail: "热门商品作为「确定性锚点」保底推荐，新商品给予15%流量倾斜测试市场反应" },
    ],
    charts: [
      { src: "/charts/阶段一_01_商品购买次数分布.png", caption: "商品购买次数分布" },
      { src: "/charts/阶段一_02_商品销量贡献结构.png", caption: "商品销量贡献结构" },
      { src: "/charts/阶段一_03_Active修复前后对比.png", caption: "Active修复前后对比" },
    ],
  },
  {
    id: "rfm",
    num: "02",
    title: "绩效拆解",
    subtitle: "RFM五层分群",
    tag: "分析",
    tagColor: "text-green bg-green/10",
    problem: "136万用户的价值分布如何？GMV增长的核心抓手是提价还是提频？需要RFM模型给出数据答案。",
    methods: [
      "RFM三维建模 — Recency / Frequency / Monetary 多窗口计算",
      "五层用户分群 — 高价值活跃 → 已流失，基于数据分布设阈值",
      "GMV驱动因子拆解 — 频次弹性 vs 客单价弹性对比",
    ],
    findings: [
      { value: "10.5%", label: "高价值用户贡献约 39% GMV" },
      { value: "44x", label: "高频83.6次 vs 流失1.9次频次差距" },
      { value: "23.4%", label: "潜在流失用户，唤醒空间明确" },
    ],
    insight:
      "频次弹性远大于客单价弹性。提升复购是核心增长抓手，比「提价」更有效且风险更低。唤醒23.4%潜在流失+拉升20.6%活跃用户频次。",
    recommendations: [
      { action: "潜力用户唤醒", detail: "对23.4%潜在流失群体发送定向优惠券+个性化推荐邮件，设置7/14/30天触达节奏" },
      { action: "高价值用户权益", detail: "为10.5%高价值用户开通专属会员折扣与提前购权益，提升转介绍率与LTV" },
      { action: "频次提升抓手", detail: "放弃单纯提价策略，通过「满3件享折扣」「搭配推荐」自然拉升客单件数" },
    ],
    charts: [
      { src: "/charts/阶段二_04_RFM五层分群.png", caption: "RFM五层分群" },
      { src: "/charts/阶段二_05_购买频次对比.png", caption: "购买频次对比" },
      { src: "/charts/阶段二_06_月度KPI趋势.png", caption: "月度KPI趋势" },
    ],
  },
  {
    id: "user",
    num: "03",
    title: "用户分析",
    subtitle: "画像与偏好",
    tag: "画像",
    tagColor: "text-blue bg-blue/10",
    problem: "推荐系统需要理解用户「是谁」「喜欢什么」「在什么时候买」。需要用数据刻画用户画像，而非直觉。",
    methods: [
      "品类偏好建模 — preference_score = user_ratio / global_ratio，消除热门品类误导",
      "价格带锁定分析 — 计算用户购买的价格集中度",
      "时间消费规律 — 工作日 vs 周末购买分布",
    ],
    findings: [
      { value: "99.5%", label: "用户 ≥80% 购买集中在单一价格带" },
      { value: "28.6%", label: "周末购买占比，为推荐推送时机提供依据" },
      { value: "14维", label: "用户特征宽表，直接支撑运营分群" },
    ],
    insight:
      "用户品类偏好不能看「买最多」，必须看「相对全局的偏好程度」——preference_score创新性地消除热门品类对偏好的误导。",
    recommendations: [
      { action: "偏好匹配引擎", detail: "上线preference_score排序权重，对每个用户Top3偏好品类商品加权+20%排序分" },
      { action: "价格带精准推荐", detail: "99.5%用户锁定在单一价格带 → 推荐的200个候选必须80%以上落在用户价格带±20%区间" },
      { action: "周末推送策略", detail: "周末购买占比28.6% → 周五晚20点推送个性化推荐通知，周末时段加大新品曝光" },
    ],
    charts: [
      { src: "/charts/阶段三_07_渠道偏好分布.png", caption: "渠道偏好分布" },
      { src: "/charts/阶段三_08_价格带集中度.png", caption: "价格带集中度" },
      { src: "/charts/阶段三_09_时间消费规律.png", caption: "时间消费规律" },
    ],
  },
  {
    id: "channel",
    num: "04",
    title: "渠道分析",
    subtitle: "线上 vs 线下",
    tag: "交叉",
    tagColor: "text-purple bg-purple/10",
    problem: "线上29.6%、线下70.4%的交易数据背后，品类偏好、价格承受、年龄分布是否存在结构性差异？",
    methods: [
      "渠道 × 品类交叉 — 计算各品类在线上线下的占比差异",
      "渠道 × 年龄交叉 — 分析不同年龄段的渠道偏好",
      "渠道 × 价格对比 — 计算线上/线下客单价比率",
    ],
    findings: [
      { value: "0.77x", label: "线上客单价为线下的0.77倍" },
      { value: "+1.6pp", label: "Jewellery线上偏好最高" },
      { value: "36.6%", label: "65岁以上线上占比最高" },
    ],
    insight:
      "线上主推平价基础款+高复购品类；线下主推当季新品+趋势款+高客单价商品。分渠道货品策略的数据依据充分。",
    recommendations: [
      { action: "线上货品策略", detail: "线上推荐池优先展示0.77x客单价以下的平价基础款+Jewellery高偏好品类，首图用模特穿搭" },
      { action: "线下货品策略", detail: "线下门店陈列主推当季新品+高客单价趋势款，搭配推荐(如T恤配牛仔裤)提升客单件数" },
      { action: "银发线上渗透", detail: "65岁以上用户36.6%偏好线上 → 设计大字体适老化推荐页+子女代购场景推荐链路" },
    ],
    charts: [
      { src: "/charts/阶段四_10_渠道品类交叉.png", caption: "渠道品类交叉" },
      { src: "/charts/阶段四_11_渠道年龄交叉.png", caption: "渠道年龄交叉" },
      { src: "/charts/阶段四_12_渠道价格对比.png", caption: "渠道价格对比" },
    ],
  },
  {
    id: "strategy",
    num: "05",
    title: "推荐策略设计",
    subtitle: "从分析到行动",
    tag: "策略",
    tagColor: "text-accent bg-accent/10",
    problem: "分析结论如何转化为可落地的推荐策略？需要设计从召回→排序→重排的完整推荐架构。",
    methods: [
      "三层架构 — 召回层(10万→200) + 排序层(200→50) + 重排层(50→20)",
      "5种推荐策略 — 热门兜底/混合探索/品类偏好/价格带/协同过滤",
      "重排规则 — 库存过滤/新品加权15%/品类打散≤3/价格多样性",
    ],
    findings: [
      { value: "5种", label: "策略按用户状态分层使用" },
      { value: "15%", label: "冷启动商品加权，给新品曝光机会" },
      { value: "≤3个", label: "同品类上限，确保推荐多样性" },
    ],
    insight:
      "召回层的品类规则召回+多样性召回通道补充，确保该召回的商品不会漏掉——「召回不只要准，还要全」。",
    recommendations: [
      { action: "冷启动策略", detail: "新品上线首周自动进入「混合探索」策略组，获得15%额外排序加权，两周后按CTR数据决定去留" },
      { action: "多样性保障", detail: "重排层品类打散规则最高≤3个同品类 + 价格多样性校验(价差≥30%)，防止推荐同质化" },
      { action: "策略分层路由", detail: "新用户→热门兜底+混合探索；活跃用户→品类偏好+协同过滤；流失预警→价格带精准匹配触发召回" },
    ],
    charts: [
      { src: "/charts/阶段五_13_推荐位分配.png", caption: "推荐位分配" },
      { src: "/charts/阶段五_14_推荐架构漏斗.png", caption: "推荐架构漏斗" },
      { src: "/charts/阶段五_15_偏好度计算创新.png", caption: "偏好度计算创新" },
    ],
  },
  {
    id: "abtest",
    num: "06",
    title: "预期效果与实验",
    subtitle: "A/B测试框架",
    tag: "验证",
    tagColor: "text-red bg-red/10",
    problem: "推荐策略上线前必须先验证效果。需要设计科学的分流方案、评估指标体系和显著性检验标准。",
    methods: [
      "A/B 实验设计 — 哈希分流(50/50) + 14天实验周期",
      "Thompson Sampling MAB — 自动调整策略流量分配",
      "显著性判断矩阵 — t检验 + Bonferroni校正多指标问题",
    ],
    findings: [
      { value: "+15%", label: "CTR预期提升" },
      { value: "+10%", label: "CVR预期提升" },
      { value: "+8%", label: "GMV预期提升" },
    ],
    insight:
      "好的数据分析不只是报告数字，而是解释「为什么」并建议「怎么做」。CTR升CVR不升→推荐够吸引但不够准→优化价格带匹配。",
    recommendations: [
      { action: "实验分流方案", detail: "按user_id哈希取模50/50分流，实验组启用个性化推荐策略，对照组使用热门排序，确保两组用户画像无显著差异" },
      { action: "MAB动态调权", detail: "上线Thompson Sampling自动调整5种策略流量分配，每24h更新一次后验分布，优胜策略自动获得更多流量" },
      { action: "多指标监控", detail: "CTR/CVR/GMV三项核心指标 + 多样性/覆盖率/新颖度三项辅助指标，Bonferroni校正后p<0.0167才算显著" },
    ],
    charts: [
      { src: "/charts/阶段六_16_预期效果对比.png", caption: "预期效果对比" },
      { src: "/charts/阶段六_17_MAB流量优化.png", caption: "MAB流量优化" },
      { src: "/charts/阶段六_18_显著性判断矩阵.png", caption: "显著性判断矩阵" },
    ],
  },
];

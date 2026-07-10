import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ChevronRight, TrendingUp, Users, Database, ArrowDown,
  Layers, Target, BarChart3, Gauge, Brain, Menu, X, MapPin,
  Mail, Phone, BookOpen, ArrowUp, School, Building2, FolderKanban,
  Lightbulb, CheckCircle2,
} from "lucide-react";
import { STAGES } from "./data";
import AnimatedCounter from "./components/AnimatedCounter";
import Particles from "./components/Particles";
import Lanyard from "./components/Lanyard";

// ============================================================
// Navigation
// ============================================================
function Nav({ activeStage, onNavigate }) {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 60);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const navItems = [
    { id: "hero", label: "首页" },
    { id: "scenario", label: "H&M项目" },
    ...STAGES.map((s) => ({ id: `stage-${s.num}`, label: s.title })),
    { id: "about", label: "关于我" },
    { id: "footer", label: "联系" },
  ];

  return (
    <motion.nav
      initial={{ y: -80 }} animate={{ y: 0 }}
      transition={{ duration: 0.5, delay: 0.8 }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled ? "border-b border-white/[0.06] bg-[#0a0e27]/80 backdrop-blur-xl" : "bg-transparent"
      }`}
    >
      <div className="mx-auto flex h-14 max-w-[1400px] items-center justify-between px-4 md:h-16 md:px-8">
        <a href="#hero" onClick={(e) => { e.preventDefault(); onNavigate("hero"); }}
           className="font-mono text-xs font-bold tracking-tight text-white md:text-sm">
          XY<span className="text-blue-400">.portfolio</span>
        </a>
        <div className="hidden items-center gap-0.5 lg:flex">
          {navItems.map((item) => (
            <button key={item.id}
              onClick={() => { onNavigate(item.id); setOpen(false); }}
              className={`rounded-full px-2 py-1.5 text-xs whitespace-nowrap transition-colors ${
                activeStage === item.id ? "bg-white/[0.08] text-white" : "text-slate-500 hover:text-slate-300"
              }`}>
              {item.label}
            </button>
          ))}
        </div>
        <button className="lg:hidden text-slate-400" onClick={() => setOpen(!open)}>
          {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>
      <AnimatePresence>
        {open && (
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden border-b border-white/[0.06] bg-[#0a0e27]/95 backdrop-blur-xl lg:hidden">
            <div className="flex flex-col gap-1 px-4 py-3">
              {navItems.map((item) => (
                <button key={item.id}
                  onClick={() => { onNavigate(item.id); setOpen(false); }}
                  className={`rounded-lg px-3 py-2 text-left text-sm ${
                    activeStage === item.id ? "bg-white/[0.08] text-white" : "text-slate-500"
                  }`}>
                  {item.label}
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  );
}

// ============================================================
// KPI Card
// ============================================================
function KpiCard({ icon: Icon, value, unit, label, accent }) {
  const colors = {
    blue: "from-blue-500/20 to-blue-500/5 border-blue-500/20",
    green: "from-emerald-400/20 to-emerald-400/5 border-emerald-400/20",
    amber: "from-amber-400/20 to-amber-400/5 border-amber-400/20",
    purple: "from-purple-400/20 to-purple-400/5 border-purple-400/20",
  };
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-80px" }} transition={{ duration: 0.5 }}
      className={`relative overflow-hidden rounded-2xl border bg-gradient-to-br ${colors[accent]} p-4 md:p-6`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="mb-1 text-[10px] uppercase tracking-wider text-slate-400 md:text-[11px]">{label}</p>
          <p className="font-mono text-2xl font-bold tracking-tight text-white md:text-3xl">
            {value}{unit && <span className="text-base font-normal text-slate-400 md:text-lg">{unit}</span>}
          </p>
        </div>
        <Icon className="h-4 w-4 text-slate-500 md:h-5 md:w-5" />
      </div>
    </motion.div>
  );
}

// ============================================================
// Hero — particles + Lanyard 3D card + animated counter
// ============================================================
function Hero() {
  return (
    <section id="hero" className="relative flex min-h-[100dvh] flex-col justify-center px-4 pt-20 pb-12 md:px-8 md:pb-16">
      {/* Particles background */}
      <Particles
        particleCount={150}
        particleSpread={8}
        speed={0.08}
        particleBaseSize={80}
        sizeRandomness={1}
        cameraDistance={18}
        disableRotation={false}
        particleColors={['#60a5fa', '#818cf8', '#38bdf8']}
      />

      <div className="relative z-10 mx-auto w-full max-w-[1400px] lg:flex lg:items-center lg:gap-12 xl:gap-20">
        {/* === LEFT: text + KPIs + tags === */}
        <div className="lg:flex-1">
          <motion.p initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="mb-4 font-mono text-xs uppercase tracking-[0.18em] text-blue-400">
            黄晓媛 · 数据分析师
          </motion.p>

          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="mb-6">
            <div className="flex flex-wrap items-baseline gap-x-2 text-3xl font-bold leading-[1.2] tracking-tighter text-white sm:text-4xl md:gap-x-4 md:text-5xl lg:text-6xl xl:text-7xl">
              <span>从</span>
              <span className="inline-flex items-baseline">
                <AnimatedCounter value="3,178" height={50} />
              </span>
              <span className="inline-flex items-baseline gap-x-1">
                <span className="text-[0.6em]">万条交易</span>
                <span>数据</span>
              </span>
            </div>
            <div className="text-3xl font-bold leading-[1.2] tracking-tighter text-white sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl">
              到推荐策略体系
            </div>
          </motion.div>

          <motion.p initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="mb-8 max-w-[520px] text-sm leading-relaxed text-slate-400 md:text-base lg:text-lg">
            具备千万级交易数据处理经验，可参与从清洗、建模到结论输出的全流程。
            擅长RFM用户分层、漏斗转化诊断、A/B测试设计。
          </motion.p>

          {/* KPI row — 2x2 on mobile, compact */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="mb-8 grid grid-cols-2 gap-2 sm:gap-3"
          >
            <KpiCard icon={Database} value="3,178" unit=" 万" label="千万数据处理" accent="blue" />
            <KpiCard icon={Target} value="5" unit=" 层" label="RFM分层" accent="green" />
            <KpiCard icon={BarChart3} value="6" unit=" 维" label="门店诊断" accent="amber" />
            <KpiCard icon={FolderKanban} value="18" unit=" 张" label="可视化图表" accent="purple" />
          </motion.div>

          {/* Tags + scroll hint */}
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.7 }}
            className="flex flex-wrap items-center justify-between gap-4 border-t border-white/[0.06] pt-5">
            <div className="flex flex-wrap gap-1.5">
              {["Python", "SQL", "Tableau", "Power BI", "Excel", "RFM分析", "A/B测试", "漏斗分析"].map((t) => (
                <span key={t} className="rounded-full border border-white/[0.06] bg-white/[0.04] px-2.5 py-1 text-[11px] text-slate-400 md:text-xs">{t}</span>
              ))}
            </div>
            <a href="#scenario" className="flex items-center gap-2 text-xs text-slate-500 transition-colors hover:text-slate-300">
              了解更多 <ArrowDown className="h-3.5 w-3.5" />
            </a>
          </motion.div>
        </div>

        {/* === RIGHT: Lanyard 3D card — compact width === */}
        <motion.div
          initial={{ opacity: 0 }} animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.5 }}
          className="relative mt-10 h-[380px] w-full max-w-[380px] mx-auto lg:mt-0 lg:h-[460px] lg:w-[360px] lg:flex-shrink-0 xl:h-[520px] xl:w-[400px]"
        >
          {/* Floating label */}
          <motion.div
            initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 1.2 }}
            className="absolute -top-1 left-1/2 z-20 -translate-x-1/2 rounded-full border border-white/[0.08] bg-white/[0.04] px-4 py-1.5 whitespace-nowrap backdrop-blur-sm"
          >
            <p className="text-xs text-slate-300 md:text-sm">
              <span className="font-bold text-white">黄晓媛</span>
              <span className="mx-1.5 text-slate-500">·</span>
              数据分析师
              <span className="mx-1.5 text-slate-500">·</span>
              拖拽卡片互动 👆
            </p>
          </motion.div>
          <Lanyard
            position={[0, 0, 22]}
            gravity={[0, -40, 0]}
            fov={22}
            frontImage="/avatar.jpg"
            lanyardWidth={1.2}
          />
        </motion.div>
      </div>
    </section>
  );
}

// ============================================================
// Business Scenario Card
// ============================================================
function ScenarioCard() {
  return (
    <section id="scenario" className="border-t border-white/[0.06] px-4 py-20 md:px-8 md:py-32">
      <div className="mx-auto max-w-[1400px]">
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }} transition={{ duration: 0.5 }} className="mb-12">
          <p className="mb-3 font-mono text-xs uppercase tracking-[0.18em] text-blue-400">Project Deep Dive</p>
          <h2 className="text-2xl font-bold tracking-tight text-white md:text-5xl">H&M 推荐系统</h2>
          <p className="mt-4 max-w-3xl text-sm leading-relaxed text-slate-400 md:text-base">
            诊断 → 绩效拆解 → 用户分析 → 渠道分析 → 策略设计 → 实验验证，每一步都给出<span className="text-blue-400 font-medium">可落地的业务建议</span>。
          </p>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }} transition={{ duration: 0.5 }}
          className="overflow-hidden rounded-3xl border border-white/[0.06] bg-gradient-to-br from-white/[0.03] to-transparent p-6 md:p-10">
          <div className="grid gap-8 md:grid-cols-3">
            <div>
              <p className="mb-3 text-[11px] uppercase tracking-wider text-slate-500">业务场景</p>
              <p className="text-sm leading-relaxed text-slate-300">
                H&M 面对商品长尾积压、用户留存不稳定等挑战。
                用户A（25岁女性，常买黑色基础款）打开APP，
                <span className="text-slate-400">无推荐时</span>看到男士夹克——划走关掉。
                <span className="text-blue-400">有推荐后</span>，
                基于她的偏好召回200个候选、打分排序，最终展示黑色罗纹吊带背心——点进购买。
                <span className="text-white font-medium">差距：0 vs 1。放大到137万用户，这就是GMV的来源。</span>
              </p>
            </div>
            <div>
              <p className="mb-3 text-[11px] uppercase tracking-wider text-slate-500">核心思想</p>
              <p className="text-sm leading-relaxed text-slate-300">
                <span className="text-blue-400 font-medium">召回层</span>——10万→200，管"有没有"；
                <span className="text-emerald-400 font-medium">排序层</span>——打分排序，管"准不准"；
                <span className="text-amber-400 font-medium">重排层</span>——库存/新品/多样性，管"赚不赚钱"。
              </p>
            </div>
            <div>
              <p className="mb-3 text-[11px] uppercase tracking-wider text-slate-500">项目定位</p>
              <p className="text-sm leading-relaxed text-slate-300">
                数据分析师主导的完整闭环：
                <span className="text-white font-medium">数据探查→质量诊断→特征设计→策略落地→实验验证</span>。
                下文六阶段展示每一步的分析方法和关键发现。
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

// ============================================================
// Stage Section — now includes actionable recommendations
// ============================================================
function StageSection({ stage }) {
  const [activeImage, setActiveImage] = useState(0);

  return (
    <section id={`stage-${stage.num}`}
      className="border-t border-white/[0.06] px-4 py-20 md:px-8 md:py-32">
      <div className="mx-auto max-w-[1400px]">
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }} transition={{ duration: 0.5 }}
          className="mb-12 flex items-start gap-4 md:gap-6">
          <span className="font-mono text-4xl font-bold tracking-tighter text-white/[0.04] md:text-8xl">{stage.num}</span>
          <div className="pt-1 md:pt-2">
            <div className="mb-2 flex items-center gap-2">
              <span className={`rounded-full px-2.5 py-0.5 text-[10px] font-medium md:text-[11px] ${stage.tagColor}`}>{stage.tag}</span>
              <p className="text-xs uppercase tracking-[0.12em] text-slate-500 md:text-sm">{stage.subtitle}</p>
            </div>
            <h2 className="text-xl font-bold tracking-tight text-white md:text-5xl">{stage.title}</h2>
          </div>
        </motion.div>

        {/* Mobile: stack vertically; desktop: 2-col */}
        <div className="grid gap-10 lg:grid-cols-2 lg:gap-16">
          {/* Left column */}
          <motion.div initial={{ opacity: 0, x: -20 }} whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-80px" }} transition={{ duration: 0.5, delay: 0.1 }}>

            <div className="mb-8 rounded-2xl border border-white/[0.06] bg-white/[0.02] p-5 md:p-6">
              <p className="mb-2 text-[11px] uppercase tracking-wider text-slate-500">业务场景</p>
              <p className="text-sm leading-relaxed text-slate-400">{stage.problem}</p>
            </div>

            <div className="mb-8">
              <p className="mb-4 text-[11px] uppercase tracking-wider text-slate-500">分析方法</p>
              <ul className="space-y-2.5">
                {stage.methods.map((m, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-slate-400">
                    <ChevronRight className="mt-0.5 h-3.5 w-3.5 flex-shrink-0 text-blue-400" />{m}
                  </li>
                ))}
              </ul>
            </div>

            <div className="mb-8 grid grid-cols-3 gap-2">
              {stage.findings.map((f, i) => (
                <div key={i} className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-3 text-center md:p-4">
                  <p className="font-mono text-base font-bold tracking-tight text-white md:text-xl">{f.value}</p>
                  <p className="mt-1 text-[10px] leading-tight text-slate-500 md:text-[11px]">{f.label}</p>
                </div>
              ))}
            </div>

            {/* Core Insight */}
            <div className="mb-6 rounded-2xl border border-emerald-400/15 bg-emerald-400/[0.04] p-5 md:p-6">
              <p className="mb-2 flex items-center gap-2 text-[11px] uppercase tracking-wider text-emerald-400">
                <Target className="h-3.5 w-3.5" /> 核心洞察
              </p>
              <p className="text-sm leading-relaxed text-slate-400">{stage.insight}</p>
            </div>

            {/* Actionable Recommendations — NEW */}
            {stage.recommendations && (
              <div className="rounded-2xl border border-amber-400/15 bg-amber-400/[0.04] p-5 md:p-6">
                <p className="mb-3 flex items-center gap-2 text-[11px] uppercase tracking-wider text-amber-400">
                  <Lightbulb className="h-3.5 w-3.5" /> 落地建议
                </p>
                <div className="space-y-3">
                  {stage.recommendations.map((rec, i) => (
                    <div key={i} className="flex items-start gap-2.5">
                      <span className="mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-amber-400/10 text-[10px] font-bold text-amber-400">
                        {i + 1}
                      </span>
                      <div>
                        <p className="text-sm font-medium text-white">{rec.action}</p>
                        <p className="mt-0.5 text-xs leading-relaxed text-slate-400">{rec.detail}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>

          {/* Right column — charts */}
          <motion.div initial={{ opacity: 0, x: 20 }} whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-80px" }} transition={{ duration: 0.5, delay: 0.2 }}>
            <p className="mb-3 text-[11px] uppercase tracking-wider text-slate-500">可视化证据</p>
            <div className="mb-3 overflow-hidden rounded-2xl border border-white/[0.06] bg-white/[0.01]">
              <AnimatePresence mode="wait">
                <motion.img key={activeImage} initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }} transition={{ duration: 0.25 }}
                  src={stage.charts[activeImage].src} alt={stage.charts[activeImage].caption} className="w-full" />
              </AnimatePresence>
              <div className="border-t border-white/[0.06] px-4 py-2.5 md:px-5 md:py-3">
                <p className="text-xs text-slate-500">{stage.charts[activeImage].caption}</p>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-2">
              {stage.charts.map((chart, i) => (
                <button key={i} onClick={() => setActiveImage(i)}
                  className={`overflow-hidden rounded-xl border transition-all ${
                    i === activeImage ? "border-blue-400 ring-1 ring-blue-400/30" : "border-white/[0.06] opacity-50 hover:opacity-80"
                  }`}>
                  <img src={chart.src} alt={chart.caption} className="w-full" />
                </button>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

// ============================================================
// About Me — now includes Skills section inside it
// ============================================================
function AboutMe() {
  const skillGroups = [
    {
      title: "数据分析方法论",
      icon: Brain, color: "text-blue-400", borderColor: "border-blue-400/20", bgColor: "bg-blue-400/5",
      items: ["指标体系搭建", "量化测算", "漏斗转化建模", "RFM用户分层", "归因分析", "异动分析", "业务诊断", "A/B测试设计"],
    },
    {
      title: "工具与语言",
      icon: Layers, color: "text-emerald-400", borderColor: "border-emerald-400/20", bgColor: "bg-emerald-400/5",
      items: ["Python", "SQL", "Tableau", "Power BI", "Excel（透视表/VLOOKUP）", "影刀RPA", "Mockup"],
    },
    {
      title: "数据工程",
      icon: Database, color: "text-amber-400", borderColor: "border-amber-400/20", bgColor: "bg-amber-400/5",
      items: ["数仓分层", "维度建模", "Linux", "Shell"],
    },
    {
      title: "办公与协作",
      icon: BookOpen, color: "text-purple-400", borderColor: "border-purple-400/20", bgColor: "bg-purple-400/5",
      items: ["Office", "飞书", "幕布", "Xmind"],
    },
  ];

  const achievements = [
    { icon: TrendingUp, value: "18%", label: "高价值线索占比", sub: "贡献52%成交", accent: "border-blue-400/20 bg-blue-400/5" },
    { icon: BarChart3, value: "34%→26%", label: "流失率下降", sub: "漏斗诊断+预警回访", accent: "border-emerald-400/20 bg-emerald-400/5" },
    { icon: Gauge, value: "85%", label: "利润预测准确率", sub: "200+项目成本归集", accent: "border-amber-400/20 bg-amber-400/5" },
    { icon: Users, value: "18%", label: "人效提升", sub: "TOPSIS+A/B测试", accent: "border-purple-400/20 bg-purple-400/5" },
  ];

  const projects = [
    {
      icon: Database, tag: "推荐系统", tagColor: "text-blue-400 bg-blue-400/10",
      title: "H&M 推荐系统经营分析",
      desc: "基于137万用户×10.5万商品×3178万交易数据，从0到1构建推荐策略体系。业务诊断→RFM绩效拆解→用户画像→渠道交叉分析→推荐策略设计→A/B测试。",
      highlights: ["RFM五层分群", "3,178万行ETL", "18张可视化"],
    },
    {
      icon: Target, tag: "电商分析", tagColor: "text-emerald-400 bg-emerald-400/10",
      title: "Online Retail 数据监控与分析",
      desc: "基于14个月交易数据搭建RFM-I分层模型，冠军客户(10.65%)贡献49%营收。追踪月度消费波动，归因Q2下滑23%的核心因子，推动运营策略调整。",
      highlights: ["RFM-I分层", "异动归因", "运营策略"],
    },
  ];

  return (
    <section id="about" className="border-t border-white/[0.06] px-4 py-20 md:px-8 md:py-32">
      <div className="mx-auto max-w-[1400px]">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }} transition={{ duration: 0.5 }} className="mb-12">
          <p className="mb-3 font-mono text-xs uppercase tracking-[0.18em] text-amber-400">About</p>
          <h2 className="text-2xl font-bold tracking-tight text-white md:text-5xl">关于我</h2>
        </motion.div>

        {/* === SKILLS subsection (moved from standalone to inside About) === */}
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }} transition={{ duration: 0.5 }} className="mb-10">
          <p className="mb-6 flex items-center gap-2 font-mono text-xs uppercase tracking-[0.18em] text-purple-400">
            <Brain className="h-3.5 w-3.5" /> 专业技能
          </p>
          <div className="grid gap-4 sm:grid-cols-2">
            {skillGroups.map((g, i) => (
              <motion.div key={i}
                initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-60px" }} transition={{ duration: 0.4, delay: i * 0.08 }}
                className={`rounded-2xl border ${g.borderColor} ${g.bgColor} p-5 md:p-6 transition-all`}>
                <div className="mb-4 flex items-center gap-3">
                  <g.icon className={`h-5 w-5 ${g.color}`} />
                  <h3 className="text-sm font-bold text-white md:text-base">{g.title}</h3>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {g.items.map((s) => (
                    <span key={s} className="rounded-full border border-white/[0.06] bg-white/[0.04] px-2.5 py-1 text-[11px] text-slate-400 md:text-xs">{s}</span>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Intro + contact card */}
        <motion.div
          initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }} transition={{ duration: 0.5 }}
          className="mb-6 overflow-hidden rounded-3xl border border-white/[0.06] bg-gradient-to-br from-white/[0.03] to-transparent p-6 md:p-10">
          <p className="mb-6 max-w-[65ch] text-sm leading-relaxed text-slate-300 md:text-base">
            具备千万级交易数据处理经验，可参与完成从清洗、建模到结论输出的全流程。
            善于从数据中定位问题根因，能针对业务问题选择合适的分析方法（RFM、漏斗、归因、A/B测试），
            输出可落地的分析结论。学习能力强，能快速理解新业务场景并迁移分析方法。
          </p>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <div className="flex items-center gap-3 rounded-xl border border-white/[0.06] bg-white/[0.02] p-3 md:p-4">
              <Phone className="h-4 w-4 text-emerald-400" /><div><p className="text-[10px] uppercase tracking-wider text-slate-500">电话</p><p className="text-sm text-slate-300">198-6013-8335</p></div>
            </div>
            <div className="flex items-center gap-3 rounded-xl border border-white/[0.06] bg-white/[0.02] p-3 md:p-4">
              <Mail className="h-4 w-4 text-blue-400" /><div><p className="text-[10px] uppercase tracking-wider text-slate-500">邮箱</p><p className="text-sm text-slate-300">lapin_2023@qq.com</p></div>
            </div>
            <div className="flex items-center gap-3 rounded-xl border border-white/[0.06] bg-white/[0.02] p-3 md:p-4">
              <School className="h-4 w-4 text-purple-400" /><div><p className="text-[10px] uppercase tracking-wider text-slate-500">教育</p><p className="text-sm text-slate-300">广州应用科技学院 · 软件工程 · 2027届</p></div>
            </div>
          </div>
        </motion.div>

        {/* Work */}
        <motion.div
          initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }} transition={{ duration: 0.5, delay: 0.1 }}
          className="mb-6 overflow-hidden rounded-3xl border border-white/[0.06] bg-gradient-to-br from-white/[0.03] to-transparent p-6 md:p-10">
          <div className="flex flex-wrap items-center gap-3 mb-6">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-amber-400/20 bg-amber-400/10 md:h-12 md:w-12 md:rounded-2xl">
              <Building2 className="h-5 w-5 text-amber-400 md:h-6 md:w-6" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white md:text-lg">新海滨装饰有限公司</h3>
              <p className="text-xs text-slate-400 md:text-sm">数据分析实习生 · 业务部 · 2025.01 - 2025.03</p>
            </div>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            {[
              { title: "客户分层", desc: "基于3,000+客户线索的RFM-KMeans聚类，识别线上渠道18%高价值线索贡献52%成交，采纳后转化率提升12%。" },
              { title: "漏斗诊断", desc: "搭建六阶段销售漏斗，定位方案-签约流失率34%，Cox回归输出报价/工期/竞品三大因子权重，上线72h预警回访后流失率下降8pp。" },
              { title: "成本预测", desc: "归集200+项目成本数据，完成主材与人工费敏感性对比分析(系数0.72 vs 0.18)，利润预测模型准确率约85%。" },
              { title: "门店优化", desc: "从6维度构建门店经营指标体系，TOPSIS与帕累托分析定位低效门店根因，A/B测试后人效提升18%、获客成本降低15%。" },
            ].map((a, i) => (
              <div key={i} className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
                <h4 className="mb-1.5 text-sm font-bold text-white">{a.title}</h4>
                <p className="text-xs leading-relaxed text-slate-400">{a.desc}</p>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Projects */}
        <motion.div
          initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }} transition={{ duration: 0.5, delay: 0.2 }}
          className="mb-6 grid gap-4 lg:grid-cols-2">
          {projects.map((proj, i) => (
            <div key={i} className="overflow-hidden rounded-3xl border border-white/[0.06] bg-gradient-to-br from-white/[0.03] to-transparent p-6 md:p-8">
              <div className="mb-4 flex items-start justify-between">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-blue-400/20 bg-blue-400/10">
                  <proj.icon className="h-5 w-5" />
                </div>
                <span className={`rounded-full px-2.5 py-0.5 text-[10px] font-medium md:text-[11px] ${proj.tagColor}`}>{proj.tag}</span>
              </div>
              <h3 className="mb-2 text-lg font-bold text-white md:text-xl">{proj.title}</h3>
              <p className="mb-4 text-sm leading-relaxed text-slate-400">{proj.desc}</p>
              <div className="flex flex-wrap gap-1.5">
                {proj.highlights.map((h) => (
                  <span key={h} className="rounded-full border border-white/[0.06] bg-white/[0.04] px-2.5 py-1 text-[10px] text-slate-400 md:text-[11px]">{h}</span>
                ))}
              </div>
            </div>
          ))}
        </motion.div>

        {/* Achievement numbers */}
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
          {achievements.map((a, i) => (
            <motion.div key={i}
              initial={{ opacity: 0, y: 15 }} whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }} transition={{ duration: 0.4, delay: i * 0.08 }}
              className={`rounded-2xl border ${a.accent} p-4 text-center md:p-5`}>
              <p className="font-mono text-xl font-bold tracking-tight text-white md:text-2xl">{a.value}</p>
              <p className="mt-1 text-xs font-medium text-slate-300">{a.label}</p>
              <p className="mt-0.5 text-[10px] text-slate-500">{a.sub}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ============================================================
// Footer
// ============================================================
function Footer() {
  return (
    <footer id="footer" className="relative flex min-h-[100dvh] flex-col justify-center border-t border-white/[0.06] px-4 md:px-8">
      <div className="mx-auto w-full max-w-[1400px] py-20 md:py-24">
        <motion.div initial={{ opacity: 0, y: 40 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-120px" }} transition={{ duration: 0.7 }} className="text-center">
          <p className="mb-6 font-mono text-xs uppercase tracking-[0.18em] text-blue-400">Get in Touch</p>
          <h2 className="mb-6 text-3xl font-bold tracking-tight text-white md:text-6xl">期待与你交流</h2>
          <p className="mx-auto mb-14 max-w-[480px] text-sm leading-relaxed text-slate-400 md:text-lg">
            如果你对我的项目感兴趣，或希望进一步了解我的数据分析能力，欢迎随时联系。
          </p>

          <div className="mx-auto mb-14 grid max-w-lg gap-3 sm:grid-cols-2 md:max-w-2xl">
            {[
              { icon: Mail, label: "邮箱", value: "lapin_2023@qq.com", color: "text-blue-400 border-blue-400/20 bg-blue-400/5" },
              { icon: Phone, label: "电话", value: "198-6013-8335", color: "text-emerald-400 border-emerald-400/20 bg-emerald-400/5" },
              { icon: MapPin, label: "期望职位", value: "数据分析", color: "text-amber-400 border-amber-400/20 bg-amber-400/5" },
              { icon: School, label: "毕业院校", value: "广州应用科技学院 · 2027届", color: "text-purple-400 border-purple-400/20 bg-purple-400/5" },
            ].map((c, i) => (
              <motion.div key={i}
                initial={{ opacity: 0, y: 15 }} whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }} transition={{ duration: 0.4, delay: i * 0.08 }}
                className={`flex items-center gap-3 rounded-2xl border p-4 ${c.color} md:p-5`}>
                <c.icon className={`h-4 w-4 md:h-5 md:w-5 ${c.color.split(" ")[0]}`} />
                <div className="text-left">
                  <p className="text-[10px] uppercase tracking-wider text-slate-500">{c.label}</p>
                  <p className="text-xs text-slate-300 md:text-sm">{c.value}</p>
                </div>
              </motion.div>
            ))}
          </div>

          <div className="border-t border-white/[0.06] pt-6">
            <p className="text-xs text-slate-500">黄晓媛 · 数据分析作品集 · 2025-2026</p>
          </div>
        </motion.div>
      </div>
    </footer>
  );
}

// ============================================================
// Back to top
// ============================================================
function BackToTop() {
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const onScroll = () => setVisible(window.scrollY > 600);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);
  return (
    <AnimatePresence>
      {visible && (
        <motion.button initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
          className="fixed right-4 bottom-4 z-50 rounded-full border border-white/[0.08] bg-white/[0.04] p-3 backdrop-blur-sm transition-colors hover:bg-white/[0.08] md:right-8 md:bottom-8">
          <ArrowUp className="h-4 w-4 text-slate-400 md:h-5 md:w-5" />
        </motion.button>
      )}
    </AnimatePresence>
  );
}

// ============================================================
// APP
// ============================================================
export default function App() {
  const [activeStage, setActiveStage] = useState("hero");

  useEffect(() => {
    const ids = ["hero", "scenario", ...STAGES.map((s) => `stage-${s.num}`), "about", "footer"];
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries.filter((e) => e.isIntersecting);
        if (visible.length > 0) {
          const best = visible.reduce((a, b) => (a.intersectionRatio > b.intersectionRatio ? a : b));
          setActiveStage(best.target.id);
        }
      },
      { threshold: [0.1, 0.3, 0.5], rootMargin: "-80px 0px" },
    );
    ids.forEach((id) => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });
    return () => observer.disconnect();
  }, []);

  const scrollTo = (id) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <div className="min-h-screen bg-[#0a0e27] overflow-x-hidden">
      <Nav activeStage={activeStage} onNavigate={scrollTo} />
      <Hero />
      <ScenarioCard />
      {STAGES.map((stage) => (
        <StageSection key={stage.id} stage={stage} />
      ))}
      <AboutMe />
      <Footer />
      <BackToTop />
    </div>
  );
}

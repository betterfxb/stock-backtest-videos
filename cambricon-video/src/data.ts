// 第003期 寒武纪 sh688256 —— 数据层
// 数据来源：westock CLI 月K线（backtest_nav.csv），未复权，分红单独计算
// 区间 2023-01-31 ~ 2026-09-30  共 45 个月
// 累计 2384.66%  年化 140.17%  最大回撤 58.16%  年化波动 113.24%  月胜率 54.5%

export const NAV: { date: string; close: number; wan: number; dd: number }[] = [
  { date: "2023-01-31", close: 40.67, wan: 100.0, dd: 0 },
  { date: "2023-02-28", close: 55.35, wan: 136.1, dd: 0 },
  { date: "2023-03-31", close: 123.79, wan: 304.38, dd: 0 },
  { date: "2023-04-28", close: 166.44, wan: 409.25, dd: 0 },
  { date: "2023-05-31", close: 169.59, wan: 416.99, dd: 0 },
  { date: "2023-06-30", close: 125.17, wan: 307.77, dd: -0.2619 },
  { date: "2023-07-31", close: 109.07, wan: 268.18, dd: -0.3569 },
  { date: "2023-08-31", close: 105.57, wan: 259.58, dd: -0.3775 },
  { date: "2023-09-28", close: 82.18, wan: 202.07, dd: -0.5154 },
  { date: "2023-10-31", close: 70.96, wan: 174.48, dd: -0.5816 },
  { date: "2023-11-30", close: 99.54, wan: 244.75, dd: -0.4131 },
  { date: "2023-12-29", close: 89.57, wan: 220.24, dd: -0.4718 },
  { date: "2024-01-31", close: 72.82, wan: 179.05, dd: -0.5706 },
  { date: "2024-02-29", close: 112.19, wan: 275.85, dd: -0.3385 },
  { date: "2024-03-29", close: 115.41, wan: 283.77, dd: -0.3195 },
  { date: "2024-04-30", close: 114.02, wan: 280.35, dd: -0.3277 },
  { date: "2024-05-31", close: 116.3, wan: 285.96, dd: -0.3142 },
  { date: "2024-06-28", close: 132.33, wan: 325.37, dd: -0.2197 },
  { date: "2024-07-31", close: 176.21, wan: 433.27, dd: 0 },
  { date: "2024-08-30", close: 171.27, wan: 421.12, dd: -0.028 },
  { date: "2024-09-30", close: 193.06, wan: 474.7, dd: 0 },
  { date: "2024-10-31", close: 303.42, wan: 746.05, dd: 0 },
  { date: "2024-11-29", close: 375.5, wan: 923.28, dd: 0 },
  { date: "2024-12-31", close: 440.6, wan: 1083.35, dd: 0 },
  { date: "2025-01-27", close: 382.89, wan: 941.46, dd: -0.131 },
  { date: "2025-02-28", close: 492.58, wan: 1211.16, dd: 0 },
  { date: "2025-03-31", close: 417.11, wan: 1025.6, dd: -0.1532 },
  { date: "2025-04-30", close: 471.21, wan: 1158.62, dd: -0.0434 },
  { date: "2025-05-30", close: 404.13, wan: 993.68, dd: -0.1796 },
  { date: "2025-06-30", close: 402.68, wan: 990.12, dd: -0.1825 },
  { date: "2025-07-31", close: 475.17, wan: 1168.36, dd: -0.0353 },
  { date: "2025-08-29", close: 1000.66, wan: 2460.44, dd: 0 },
  { date: "2025-09-30", close: 888.26, wan: 2184.07, dd: -0.1123 },
  { date: "2025-10-31", close: 921.81, wan: 2266.56, dd: -0.0788 },
  { date: "2025-11-28", close: 892.28, wan: 2193.95, dd: -0.1083 },
  { date: "2025-12-31", close: 908.76, wan: 2234.47, dd: -0.0918 },
  { date: "2026-01-30", close: 843.89, wan: 2074.97, dd: -0.1567 },
  { date: "2026-02-27", close: 789.6, wan: 1941.48, dd: -0.2109 },
  { date: "2026-03-31", close: 658.72, wan: 1619.67, dd: -0.3417 },
  { date: "2026-04-30", close: 1139.91, wan: 2802.83, dd: 0 },
  { date: "2026-05-29", close: 1310.0, wan: 3221.05, dd: 0 },
  { date: "2026-06-30", close: 1595.55, wan: 3923.16, dd: 0 },
  { date: "2026-07-31", close: 1106.0, wan: 2719.45, dd: -0.3068 },
  { date: "2026-08-31", close: 1112.18, wan: 2734.64, dd: -0.3029 },
  { date: "2026-09-30", close: 1009.01, wan: 2480.97, dd: -0.3676 },
];

// 回撤段（暗红底纹）。脚本按 dd<0 自动检测，剔除单月浅回撤后共 2 段。
export const DD_RANGES: [number, number][] = [
  [4, 9],
  [41, 44],
];

// 阶段标签（按数据索引区间）
export const STAGES: { from: number; to: number; name: string }[] = [
  { from: 0, to: 4, name: "AI 行情" },
  { from: 4, to: 9, name: "行情退潮" },
  { from: 9, to: 13, name: "磨底" },
  { from: 13, to: 23, name: "国产替代" },
  { from: 23, to: 31, name: "算力爆发" },
  { from: 31, to: 41, name: "冲顶" },
  { from: 41, to: 44, name: "回落" },
];

// 事件卡（正文均 ≤ 50 字）。idx = 45 个月净值序列的数据下标（0..44），
// 出帧时间由分段配速 src/reveal.ts 推导（事件密集处最短停留 90 帧），
// 保证事件卡与图表笔尖严格同步。
export const EVENTS: {
  idx: number;
  tag: string;
  type: string;
  value: string;
  body: string;
}[] = [
  {
    idx: 0,
    tag: "2023年1月",
    type: "起投",
    value: "100.00 万",
    body: "AI 芯片板块情绪低点，1 月 31 日收盘 40.67 元买入 100 万元。",
  },
  {
    idx: 4,
    tag: "2023年5月",
    type: "主升",
    value: "416.99 万",
    body: "ChatGPT 引爆 AI 行情，芯片龙头领涨，4 个月账户翻倍。",
  },
  {
    idx: 9,
    tag: "2023年10月",
    type: "回撤",
    value: "174.48 万",
    body: "行情退潮，商业化落地受质疑，5 个月回撤 58.16%。",
  },
  {
    idx: 13,
    tag: "2024年2月",
    type: "反弹",
    value: "275.85 万",
    body: "AI 落地预期升温，股价两个月反弹约 58%。",
  },
  {
    idx: 18,
    tag: "2024年7月",
    type: "继续反弹",
    value: "433.27 万",
    body: "国产替代逻辑强化，账户重回 400 万上方。",
  },
  {
    idx: 23,
    tag: "2024年12月",
    type: "翻倍",
    value: "1083.35 万",
    body: "新一代 AI 芯片发布，账户一年站上千万。",
  },
  {
    idx: 25,
    tag: "2025年2月",
    type: "继续上涨",
    value: "1211.16 万",
    body: "算力需求爆发，订单预期带动股价再创新高。",
  },
  {
    idx: 31,
    tag: "2025年8月",
    type: "10 倍",
    value: "2460.44 万",
    body: "股价破 1000 元，成为 A 股 AI 芯片第一股。",
  },
  {
    idx: 41,
    tag: "2026年6月",
    type: "区间最高",
    value: "3923.16 万",
    body: "算力景气延续，股价冲至 1595.55 元创区间新高。",
  },
  {
    idx: 44,
    tag: "2026年9月",
    type: "期末",
    value: "2480.97 万",
    body: "含 1 次分红 3.69 万，含息总资产 2484.66 万。",
  },
];

// 关键节点标注（BeatOverlay，≤4 个）：最新到达的保留、旧的交汇淡出；
// 标注金额由渲染端现取 NAV[idx]，这里只给人核验过的标签。
export const BEATS: { idx: number; label: string }[] = [
  { idx: 9, label: "最深回撤" },
  { idx: 23, label: "站上千万" },
  { idx: 31, label: "千元股" },
  { idx: 41, label: "区间最高" },
];

export const METRICS = {
  code: "sh688256",
  name: "寒武纪",
  episode: "第 003 期",
  range: "2023-01-31 ~ 2026-09-30",
  startYM: "2023-01",
  totalRet: "2384.66%",
  cagr: "140.17%",
  mdd: "−58.16%",
  vol: "113.24%",
  winRate: "54.5%",
  months: "45 个月",
  endAsset: "2484.66 万",
  peakAsset: "3923.16 万",
  peakDate: "2026-06-30",
  minAsset: "100.00 万",
  minDate: "2023-01-31",
  minMonth: "第1个月",
  longestDdMonths: "13",
  endVsPeak: "-36.76%",
  principal: 100,
  source: "westock CLI 月K线（backtest_nav.csv）未复权 · 分红单独计算",
};

// 钩子/收尾/封面用定稿文案（人工核验）
export const COPY = {
  hold: "拿满 3 年 9 个月",
  hookSub: "100 万买入 · 拿满 3 年 9 个月",
  closingQ: "那 6 个月里，你还拿得住吗？",
};

// 纵轴上限制（cover 用）：按峰值上浮 8% 后取整到千位
export const YMAX = 5000;

// 配色：深海军蓝底 + 金强调（数字/品牌），亮蓝曲线（金融终端风）
export const C = {
  bg: "#0A1128",
  paper: "#0E1730",
  panel: "#141F3D",
  brand: "#F0B860",
  brandSoft: "#F8DCA4",
  line: "#4E9EFF",
  glow: "#16407C",
  dd: "#3E2438",
  gold: "#F0B860",
  amber: "#F5CE6A",
  peak: "#FFD58A",
  grid: "#1C2A4A",
  axis: "#8A93B5",
  ink: "#F2F5FF",
  inkSoft: "#B6BFD8",
  up: "#4FD39A",
  down: "#FF6B6B",
};
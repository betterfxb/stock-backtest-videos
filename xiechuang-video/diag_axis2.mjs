/** 复算 axis.ts 的每帧窗口最大值/目标档位，诊断"纵轴为什么不降档"。
 * 用法: node diag_axis2.mjs
 */
import fs from "fs";

const src = fs.readFileSync("src/data.ts", "utf-8");
function block(marker) {
  const lines = src.split("\n");
  const start = lines.findIndex((l) => l.includes(marker) && l.includes("export const"));
  let depth = 0;
  const out = [];
  for (let i = start; i < lines.length; i++) {
    out.push(lines[i]);
    depth += (lines[i].match(/[\[{]/g) || []).length - (lines[i].match(/[\]}]/g) || []).length;
    if (depth === 0 && i > start) break;
  }
  return out.join("\n");
}
const NAV = [...block("const NAV").matchAll(/wan:\s*([\d.]+)/g)].map((m) => +m[1]);
const N = NAV.length - 1;

const REVEAL_START = 150, REVEAL_END = 2640, TOTAL = 2760;
const WIN = 13, LOCK = 0.26, TAIL_KF = 44, TAIL_END = 0.94;
const AXIS_STEPS = [25, 50, 100, 200, 250, 500, 1000, 2000, 2500];
const HEADROOM = 1.18, DECAY = 0.9965;
const clamp01 = (t) => Math.max(0, Math.min(1, t));
const fitStep = (v) => AXIS_STEPS.find((s) => s * 4 >= v) ?? AXIS_STEPS.at(-1);

console.log(`N=${N}  NAV min=${Math.min(...NAV).toFixed(2)} max=${Math.max(...NAV).toFixed(2)}\n`);

let release = 0;
const rows = [];
for (let f = 0; f < TOTAL; f++) {
  const reveal = f <= REVEAL_START ? 0 : f >= REVEAL_END ? 1 : (f - REVEAL_START) / (REVEAL_END - REVEAL_START);
  const kf = clamp01(reveal) * N;
  const tailT = clamp01((kf - TAIL_KF) / (N - TAIL_KF));
  const tailE = tailT * tailT * (3 - 2 * tailT);
  const frac = LOCK + (TAIL_END - LOCK) * tailE;
  const L = kf - WIN * frac;

  const ki = Math.min(Math.floor(kf), N);
  const atEnd = ki >= N;
  const kfrac = atEnd ? 0 : kf - ki;
  const curVal = atEnd ? NAV[N] : NAV[ki] + (NAV[ki + 1] - NAV[ki]) * kfrac;

  let wmax = curVal, wi = ki;
  const a = Math.max(0, Math.ceil(L)), b = Math.min(N, Math.floor(kf));
  for (let i = a; i <= b; i++) if (NAV[i] > wmax) { wmax = NAV[i]; wi = i; }

  const target = fitStep(wmax * HEADROOM) * 4;
  // 与 axis.ts v4.2 保持一致：release 连续，不存量化值
  release = target >= release ? target : Math.max(target, release * DECAY);
  const top = fitStep(release) * 4;
  rows.push({ f, top, target, wmax, wi, curVal, L });
}

// 纵轴"占幅比" = 当前值占顶值的比例。绘图区高 OFF=300px，占幅 25% 意味着
// 整段行情只用了 75px，看不出月度起伏。
const OFF = 300;
const pct = (v, top) => (100 * v) / top;
console.log("frame   kf    idx   播放头值  窗口max(max@idx)  target  实际top  占幅");
console.log("-".repeat(78));
for (const f of [200, 400, 600, 800, 1000, 1300, 1600, 1900, 2200, 2400, 2550, 2640]) {
  const r = rows[f];
  console.log(
    String(f).padStart(5) + "  " +
    (r.f >= 150 && r.f <= 2640 ? (((r.f - 150) / 2490) * N).toFixed(1).padStart(5) : "  —  ") + "  " +
    String(Math.round(r.wi)).padStart(3) + "  " +
    r.curVal.toFixed(1).padStart(8) + "  " +
    (r.wmax.toFixed(1) + "(@" + r.wi + ")").padStart(14) + "  " +
    String(r.target).padStart(6) + "  " +
    String(r.top).padStart(8) + "  " +
    (pct(r.curVal, r.top).toFixed(1) + "%").padStart(7),
  );
}

let desc = 0, asc = 0;
for (let i = 1; i < rows.length; i++) {
  if (rows[i].target < rows[i - 1].target) desc++;
  else if (rows[i].target > rows[i - 1].target) asc++;
}
console.log(`\ntarget 升档 ${asc} 次 / 降档 ${desc} 次`);
const tops = [...new Set(rows.map((r) => r.top))];
console.log(`实际 top 档位: ${tops.join(" → ")}`);

console.log("\n42 个月回撤段（idx19..idx60）采样：");
for (const f of [800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]) {
  const r = rows[f];
  const hPx = (OFF * r.curVal) / r.top;
  console.log(`  f${String(f).padStart(4)}  idx${String(Math.round(r.wi)).padStart(3)}  值 ${r.curVal.toFixed(1).padStart(7)}  top ${String(r.top).padStart(4)}  占幅 ${pct(r.curVal, r.top).toFixed(1)}%  曲线高 ${hPx.toFixed(0)}px  target ${r.target}`);
}

// 逐帧 target 序列：看清 target 在 400/800 之间来回抖动，还是稳定在 400
console.log("\ntarget 分布（f 150..2640）:");
const cnt = {};
for (let f = 150; f <= 2640; f++) cnt[rows[f].target] = (cnt[rows[f].target] || 0) + 1;
Object.keys(cnt).sort((a, b) => a - b).forEach((k) => console.log(`  target=${k}: ${cnt[k]} 帧`));

// 关键诊断：top 卡在 800，说明 decay 每次快降到底时又被某个 target=800 的帧
// 立刻吸回去。数一下 f900..f1900 这段里 target=800 的帧有多密集。
const bear = rows.slice(900, 1901);
const bearCnt = {};
for (const r of bear) bearCnt[r.target] = (bearCnt[r.target] || 0) + 1;
console.log("\n回撤段 f900..f1900 的 target 分布:");
Object.keys(bearCnt).sort((a, b) => a - b).forEach((k) => console.log(`  target=${k}: ${bearCnt[k]} 帧`));

// top 连续段：看 top=800 到底持续了多久
const segs = [];
let s0 = 0, sv = rows[0].top;
for (let f = 1; f < rows.length; f++) {
  if (rows[f].top !== sv) { segs.push([s0, f - 1, sv]); s0 = f; sv = rows[f].top; }
}
segs.push([s0, rows.length - 1, sv]);
console.log("\ntop 连续段（帧数 = 时长/30 秒）:");
for (const [a, b, v] of segs) {
  console.log(`  f${String(a).padStart(4)}..f${String(b).padStart(4)}  top=${String(v).padStart(4)}  ${((b - a + 1) / 30).toFixed(1)} 秒`);
}
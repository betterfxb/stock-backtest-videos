/**
 * 叙事配速（v5.0）—— 单调分段线性 reveal，取代「idx 线性映射到帧」。
 *
 * 为什么改：线性配速下 reveal 速度恒定 ≈ 32 月/千帧，事件卡的停留时间
 * 完全由事件间距决定 —— 相邻两个月的事件（如 2025-08 暴涨 / 2025-09 站上
 * 千万）只有 31 帧 ≈ 1 秒，正文 50 字还没读完就切走；而 24 个月的静默段
 * 反而拖掉 750 帧。观众注意力最集中的地方停得最短，这是节奏倒挂。
 *
 * 规则（三条约束，缺一不可）：
 *   1. **锚点** = 每个事件的 idx ∪ {0, N}。段 = 相邻锚点之间的数据索引区间。
 *   2. **段帧数** = max(MIN_DWELL, K × span)：短段（事件密集）吃满 90 帧
 *      最短停留，长段（横盘静默）按月数线性拉长 —— 事件密集处慢、空窗处快，
 *      与注意力曲线同向。K 用二分求解，使 Σ段帧数 ≡ REVEAL_END − REVEAL_START。
 *   3. **端点锁死**：CUM 首尾分别钉在 REVEAL_START / REVEAL_END，二分残差
 *      摊到最长段上（亚帧级），保证钩子交接与收尾帧不漂移。
 *
 * 由此得到两条反函数（事件卡/BeatOverlay 用）：
 *   evFrame(idx)  该数据索引被笔尖走到的帧号 —— 事件卡出帧、停留
 *                  （卡间可见间隔 = 下一 evFrame − 本 evFrame ≥ MIN_DWELL）
 *   revealAt(f)   该帧的 reveal ∈ [0,1]（分段线性单调，含端点 clamp）
 * valueAt / totalPctAt 供数据卡实时读数与 check_readout 同源复算 ——
 * 校验器必须 import 这里的函数，不得复刻线性插值公式（v4 曾错位一整个配速段）。
 */
import { EVENTS, NAV } from "./data";
import { TOTAL_FRAMES } from "./layout";

export const REVEAL_START = 150;
export const REVEAL_END = 2640;
/** 单段最短停留帧数（3 秒）—— 事件卡正文 ≥50 字的可读下限 */
export const MIN_DWELL = 90;

const N = NAV.length - 1;

// 锚点：事件 idx ∪ {0, N}，去重升序
const IDXS: number[] = (() => {
  const s = new Set<number>([0, N]);
  for (const e of EVENTS) if (e.idx >= 0 && e.idx <= N) s.add(e.idx);
  return [...s].sort((a, b) => a - b);
})();

const SPANS: number[] = IDXS.slice(1).map((v, i) => v - IDXS[i]);
const TOTAL = REVEAL_END - REVEAL_START;

const SEG_FRAMES: number[] = (() => {
  // 事件极密（段数 × 90 已超预算）时整体压缩 dwell，保证总长不破
  const dwell = Math.min(MIN_DWELL, Math.floor(TOTAL / SPANS.length));
  const sumAt = (K: number) => SPANS.reduce((a, s) => a + Math.max(dwell, K * s), 0);
  let lo = 0;
  let hi = 1;
  while (sumAt(hi) < TOTAL) hi *= 2;
  for (let i = 0; i < 100; i++) {
    const mid = (lo + hi) / 2;
    if (sumAt(mid) < TOTAL) lo = mid;
    else hi = mid;
  }
  const K = (lo + hi) / 2;
  const frames = SPANS.map((s) => Math.max(dwell, K * s));
  // 二分残差（亚帧级）摊到最长段，末帧严格 = REVEAL_END
  const drift = TOTAL - frames.reduce((a, b) => a + b, 0);
  if (drift !== 0) {
    let mi = 0;
    frames.forEach((f, i) => {
      if (f > frames[mi]) mi = i;
    });
    frames[mi] += drift;
  }
  return frames;
})();

/** CUM[i] = 锚点 IDXS[i] 被走到的帧号；CUM[0]=REVEAL_START，末位=REVEAL_END */
const CUM: number[] = (() => {
  const c: number[] = [REVEAL_START];
  for (const f of SEG_FRAMES) c.push(c[c.length - 1] + f);
  c[c.length - 1] = REVEAL_END;
  return c;
})();

/** 数据索引 → 出帧帧号（事件卡、BeatOverlay、抽帧脚本同源引用） */
export const evFrame = (idx: number): number => {
  const last = IDXS.length - 1;
  if (idx <= IDXS[0]) return CUM[0];
  if (idx >= IDXS[last]) return CUM[last];
  let i = 0;
  while (i < last - 1 && IDXS[i + 1] <= idx) i++;
  const t = (idx - IDXS[i]) / (IDXS[i + 1] - IDXS[i]);
  return CUM[i] + t * (CUM[i + 1] - CUM[i]);
};

/** 帧号 → reveal ∈ [0,1]（evFrame 的反函数，分段线性单调） */
export const revealAt = (frame: number): number => {
  if (frame <= REVEAL_START) return 0;
  if (frame >= REVEAL_END) return 1;
  const last = CUM.length - 1;
  let i = 0;
  while (i < last - 1 && CUM[i + 1] <= frame) i++;
  const t = (frame - CUM[i]) / (CUM[i + 1] - CUM[i]);
  return (IDXS[i] + t * (IDXS[i + 1] - IDXS[i])) / N;
};

/** 帧号 → 连续小数数据端点（getCam/相机窗口的输入） */
export const kfAt = (frame: number): number => revealAt(frame) * N;

/** 该帧笔尖的真实净值（与 NavChart 的 curVal 同一插值公式） */
export const valueAt = (frame: number): number => {
  const kf = kfAt(frame);
  const ki = Math.min(Math.floor(kf), N);
  if (ki >= N) return NAV[N].wan;
  return NAV[ki].wan + (NAV[ki + 1].wan - NAV[ki].wan) * (kf - ki);
};

/** 数据卡实时累计收益率（%）—— 跟笔尖，不再开场就摆出终值 */
export const totalPctAt = (frame: number): number => (valueAt(frame) / 100 - 1) * 100;

export { EVENTS, NAV, TOTAL_FRAMES };

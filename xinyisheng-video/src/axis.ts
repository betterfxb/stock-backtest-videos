/**
 * 动态纵轴（v4.1）
 *
 * 为什么改：固定 YMAX=8000 时，2020-2023 那段净值只有 78~474 万，占满 8000 的
 * 纵幅不足 5%，105 万跌到 78 万在屏幕上只差 3px —— 完全看不出起伏，"拿满六年
 * 涨 45 倍"的叙事没有任何视觉证据。固定轴在这里是**叙事失败**，不是"更稳重"。
 *
 * 为什么不能直接用瞬时值：
 *   top = max(可见窗口) * headroom 直接算，会在每个月的小波动上反复跨档，
 *   观众看到的是刻度数字疯狂跳动，比"没起伏"更糟。所以这里用三条约束：
 *
 *   1. **跟随窗口最大值，而不是当前值**。窗口内始终是满的，不会把已经画出来的
 *      历史峰值顶出画面外（否则从 250 掉到 100 时，早先 210 万的点会被切掉）。
 *   2. **上升即时、下降缓慢**。涨上去立刻给空间（不然看不到突破），缩回来按
 *      每帧 ×0.9965 衰减（约 1 秒降 10%、20 秒腰斩），避免抖动。
 *   3. **档位量化**：top 恒等于 step×4，step 取 1/2/2.5/5×10^n 的整数表。
 *      于是刻度永远是 0 / 25% / 50% / 75% / 100% 这五个整数，不会出现 62.5
 *      这种数；同时只会在跨档时跳一次，不是连续漂移。
 *
 * 代价（已知且接受）：长熊段里纵轴会从 800 逐档降到 100，刻度数字会变。
 * 这是"把波动放大"必须付的账，比让观众什么都看不到划算。
 *
 * 修过的 bug（v4.2）：见下面 AXIS_TOP 里的 release 注释 —— 衰减状态量必须
 * 连续，不能存量化后的 top，否则纵轴卡在高档位永不下降。
 */
import { NAV } from "./data";
import { TOTAL_FRAMES } from "./layout";
import { REVEAL_END, REVEAL_START, revealAt } from "./reveal";

export { REVEAL_END, REVEAL_START, TOTAL_FRAMES };

const N = NAV.length - 1;

// 与 NavChart 的横向相机保持一致（本模块要按窗口取最大值）
const WIN = 13;
const LOCK = 0.26;
const TAIL_KF = 44;
const TAIL_END = 0.94;

const clamp01 = (t: number) => Math.max(0, Math.min(1, t));

/** 顶值 = step × 4。5 条刻度全是整数；上限 10000（step=2500），
 *  再高会让 "10,000" 这类 6 字符标签铺到 x<80 吃掉左侧安全带。 */
const AXIS_STEPS = [25, 50, 100, 200, 250, 500, 1000, 2000, 2500];
const HEADROOM = 1.18;
const DECAY = 0.9965;

const camOf = (reveal: number) => {
  const kf = clamp01(reveal) * N;
  const tailT = clamp01((kf - TAIL_KF) / (N - TAIL_KF));
  const tailE = tailT * tailT * (3 - 2 * tailT);
  const frac = LOCK + (TAIL_END - LOCK) * tailE;
  return { kf, L: kf - WIN * frac };
};

const fitStep = (v: number) => AXIS_STEPS.find((s) => s * 4 >= v) ?? AXIS_STEPS[AXIS_STEPS.length - 1];

/** 每帧的纵轴顶值，预计算一次，运行期 O(1) 查表。 */
export const AXIS_TOP: number[] = (() => {
  const out: number[] = [];
  // release 必须保持**连续**（不量化），top 才是它的量化投影。
  //
  // 上一版写的是 `prev = top`，于是衰减收敛到一个不动点：prev=800 时
  // prev*DECAY=797.2，fitStep 又把它吸回 800，下一帧 prev 还是 800 ——
  // 纵轴永远降不下来。ep004 当时记录的"7 次换档且从不下降"就是这个 bug，
  // 不是数据本身单调。长期回撤段因此被压在 800 的档位上（占幅仅 25%），
  // 42 个月的横盘在屏幕上几乎是一条直线，正是动态轴本该消除的问题。
  let release = 0;

  for (let f = 0; f < TOTAL_FRAMES; f++) {
    // v5.0：配速分段线性后，reveal 不再是 (f-start)/(end-start)。
    // 必须与 Video.tsx 走同一个 revealAt，否则纵轴预计算与画面错位一整个配速段。
    const { kf, L } = camOf(revealAt(f));

    const ki = Math.min(Math.floor(kf), N);
    const atEnd = ki >= N;
    const frac = atEnd ? 0 : kf - ki;
    const curVal = atEnd ? NAV[N].wan : NAV[ki].wan + (NAV[ki + 1].wan - NAV[ki].wan) * frac;

    // 窗口内最大值 + 当前插值点：保证画面上没有任何点被顶到顶值之外
    let wmax = curVal;
    const a = Math.max(0, Math.ceil(L));
    const b = Math.min(N, Math.floor(kf));
    for (let i = a; i <= b; i++) wmax = Math.max(wmax, NAV[i].wan);

    const target = fitStep(wmax * HEADROOM) * 4;
    // 上升即时；下降在连续量上衰减，再量化显示
    release = target >= release ? target : Math.max(target, release * DECAY);
    out.push(fitStep(release) * 4);
  }
  return out;
})();

/** 帧号 → 该帧纵轴顶值（v5.0：NavChart 直接用真实帧号查表，
 *  不再走 reveal 中转 —— 中转要四舍五入回帧号，会与 revealAt 的分段边界错位）。 */
export const axisTopForFrame = (frame: number): number => {
  const f = Math.round(frame);
  return AXIS_TOP[Math.max(0, Math.min(TOTAL_FRAMES - 1, f))];
};

/** 5 条刻度：0 / 25% / 50% / 75% / 100%，全部为整数。 */
export const axisTicks = (top: number): number[] => [0, 1, 2, 3, 4].map((i) => (top * i) / 4);

import React from "react";
import { useCurrentFrame } from "remotion";
import { BEATS, C, EVENTS, NAV, STAGES, YMAX } from "./data";
import { axisTicks, axisTopForFrame } from "./axis";
import {
  AXIS_Y,
  FLOAT_H,
  FLOAT_W,
  MAIN_BOT,
  PX0,
  PX1,
  PY0,
  SAFE_X0,
  SAFE_X1,
  SAFE_Y1,
} from "./layout";

const N = NAV.length - 1;

const OFF = MAIN_BOT - PY0;
const SPAN = PX1 - PX0;

// 纵轴：动态、实时跟随（详见 axis.ts）。顶值恒为 step×4，5 条刻度全是整数；

// ── 横向跟随相机 ──────────────────────────────────────────────
// 播放头钉在屏幕 26% 处，窗口固定 13 个月，内容持续向左滚动。
const WIN = 13;
const LOCK = 0.26;
const TAIL_KF = 44;
const TAIL_END = 0.94;
const EDGE = 1.2;

// 浮动读数标签：贴播放头的间隔（宽高与圆角从 layout 同源取）
const FLOAT_GAP = 22;

const PEAK_I = NAV.reduce((a, p, i) => (p.wan > NAV[a].wan ? i : a), 0);
const PEAK_WAN = NAV[PEAK_I].wan;

const clamp01 = (t: number) => Math.max(0, Math.min(1, t));

export interface CamState {
  reveal: number;
  /** 连续小数端点 0..N，曲线按它插值，绝不在格点上跳 */
  kf: number;
  /** 四舍五入整数索引，仅用于取标签文案 */
  curIdx: number;
  /** 窗口左缘（数据索引，可为负 = 起点前留白） */
  L: number;
  /** 可见月份数 */
  win: number;
  /** 播放头所在屏幕比例 0..1 */
  frac: number;
}

/**
 * @param mode "pan" 横向跟随相机（成片用）；"full" 全区间静态（开场钩子背景用）
 */
export const getCam = (reveal: number, mode: "pan" | "full" = "pan"): CamState => {
  const r = clamp01(reveal);
  const kf = r * N;
  const curIdx = Math.min(Math.round(kf), N);
  if (mode === "full") return { reveal: r, kf, curIdx, L: 0, win: N, frac: kf / N };
  const tailT = clamp01((kf - TAIL_KF) / (N - TAIL_KF));
  const tailE = tailT * tailT * (3 - 2 * tailT);
  const frac = LOCK + (TAIL_END - LOCK) * tailE;
  return { reveal: r, kf, curIdx, L: kf - WIN * frac, win: WIN, frac };
};

export const NavChart: React.FC<{ cam: CamState; preview?: boolean }> = ({ cam, preview = false }) => {
  const frame = useCurrentFrame();
  const { kf, L, win } = cam;

  // 本帧的纵轴顶值。preview（开场钩子的整段静态轮廓）沿用全区间 YMAX，
  // 因为那一帧要一屏看完全程，用动态顶值反而误导。
  const top = preview ? YMAX : axisTopForFrame(frame);
  const TICKS = axisTicks(top);

  // 相机映射：窗口内的数据下标铺满整个绘图区宽度
  const x = (i: number) => PX0 + ((i - L) / win) * SPAN;
  const y = (v: number) => MAIN_BOT - (OFF * v) / top;

  const iMin = Math.ceil(L);
  const iMax = Math.floor(L + win);
  const inView = (i: number) => i >= iMin && i <= iMax;
  const edgeA = (i: number) => clamp01((i - L) / EDGE) * clamp01((L + win - i) / EDGE);

  const ki = Math.min(Math.floor(kf), N);
  const atEnd = ki >= N;
  const frac = atEnd ? 0 : kf - ki;
  const curVal = atEnd ? NAV[N].wan : NAV[ki].wan + (NAV[ki + 1].wan - NAV[ki].wan) * frac;
  const curIdx = atEnd ? N : ki;

  const pts: string[] = [];
  for (let i = 0; i <= ki; i++) {
    pts.push(`${i === 0 ? "M" : "L"}${x(i).toFixed(1)},${y(NAV[i].wan).toFixed(1)}`);
  }
  if (!atEnd) pts.push(`L${x(kf).toFixed(1)},${y(curVal).toFixed(1)}`);
  const d = pts.join(" ");
  // 曲线面积渐变：沿已画曲线向下铺到绘图区底，越下越透（去块化的"体积感"）
  const areaD = `${d} L${x(kf).toFixed(1)},${MAIN_BOT} L${PX0},${MAIN_BOT} Z`;

  const stageIdx = STAGES.findIndex((s, i) => curIdx >= s.from && (curIdx < s.to || i === STAGES.length - 1));
  const si = stageIdx < 0 ? 0 : stageIdx;
  const cur = STAGES[si];
  const stageFade = Math.min(
    clamp01((kf - cur.from) / 0.55),
    cur.to < N ? clamp01((cur.to - kf) / 0.55) : 1,
  );

  const peakLabelA = clamp01((kf - PEAK_I) / 0.6);

  // ── 浮动读数：贴播放头的当前资产金额（终端式"quote chip"）──
  const hx = x(kf);
  const hy = y(curVal);
  const flip = hx + FLOAT_GAP + FLOAT_W > PX1;
  const bxRaw = flip ? hx - FLOAT_GAP - FLOAT_W : hx + FLOAT_GAP;
  const bx = Math.max(SAFE_X0, Math.min(bxRaw, PX1 - FLOAT_W));
  // 纵向回推：标签完整落在绘图区内（绝不压到时间轴/事件卡，v6 不再借用 SAFE_Y1）
  const floatY = Math.max(PY0 + 6, Math.min(hy - FLOAT_H - 18, MAIN_BOT - FLOAT_H - 6));

  if (preview) {
    return (
      <svg width={1080} height={1920} style={{ position: "absolute", left: 0, top: 0 }}>
        <path d={d} fill="none" stroke={C.glow} strokeWidth={24} strokeLinejoin="round" strokeLinecap="round" />
        <path d={d} fill="none" stroke={C.line} strokeWidth={9} strokeLinejoin="round" strokeLinecap="round" />
      </svg>
    );
  }

  const months: number[] = [];
  for (let i = Math.max(0, iMin); i <= Math.min(N, iMax); i++) if (i % 2 === 0) months.push(i);

  return (
    <svg width={1080} height={1920} style={{ position: "absolute", left: 0, top: 0 }}>
      <defs>
        <clipPath id="plotClip">
          <rect x={PX0 - 8} y={PY0 - 24} width={SPAN + 16} height={MAIN_BOT - PY0 + 30} />
        </clipPath>
        {/* 面积渐变的"蓝→透"漏斗 */}
        <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={C.line} stopOpacity={0.14} />
          <stop offset="55%" stopColor={C.line} stopOpacity={0.04} />
          <stop offset="100%" stopColor={C.line} stopOpacity={0} />
        </linearGradient>
        {/* 笔尖发光：低强度高斯模糊 */}
        <filter id="penGlow" x="-120%" y="-120%" width="340%" height="340%">
          <feGaussianBlur stdDeviation="9" result="b" />
          <feMerge>
            <feMergeNode in="b" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      {/* ---------- 固定网格 + 纵轴刻度（终端式：刻度值留装订沟左侧）---------- */}
      {TICKS.map((v) => (
        <g key={v}>
          <line x1={PX0} y1={y(v)} x2={PX1} y2={y(v)} stroke={C.grid} strokeWidth={2} />
          <text x={PX0 - 18} y={y(v) + 8} fill={C.axis} fontSize={21} fontWeight={700} textAnchor="end">
            {v.toLocaleString("en-US")}
          </text>
        </g>
      ))}

      {/* ---------- 本金基准线（100 万） ---------- */}
      <line
        x1={PX0}
        y1={y(100)}
        x2={PX1}
        y2={y(100)}
        stroke="#2E4A7A"
        strokeWidth={2}
        strokeDasharray="14 10"
        opacity={0.7}
      />
      <text x={PX0 + 8} y={y(100) - 12} fill="#7C8DB8" fontSize={21} fontWeight={700} opacity={0.8}>
        本金 100 万
      </text>

      {/* ---------- 区间峰值参考线（进入当前量程才画） ---------- */}
      {PEAK_WAN <= top ? (
        <>
          <line x1={PX0} y1={y(PEAK_WAN)} x2={PX1} y2={y(PEAK_WAN)} stroke="#2C3E63" strokeWidth={2} strokeDasharray="22 12" />
          {peakLabelA > 0 ? (
            <text x={PX0 + 10} y={y(PEAK_WAN) - 14} fill="#7C8DB8" fontSize={23} fontWeight={700} opacity={peakLabelA}>
              区间峰值 {Math.round(PEAK_WAN).toLocaleString("en-US")} 万
            </text>
          ) : null}
        </>
      ) : null}

      {/* ---------- 阶段分界细线（装饰性质的竖线，去块化后留存） ---------- */}
      {STAGES.slice(1)
        .filter((s) => s.from >= L - 1 && s.from <= L + win)
        .map((s) => (
          <line key={s.from} x1={x(s.from)} y1={PY0} x2={x(s.from)} y2={MAIN_BOT} stroke="#2A3758" strokeWidth={2} />
        ))}

      {/* ---------- 曲线：面积渐变 + 辉光 + 主线，只画到笔尖 ---------- */}
      <g clipPath="url(#plotClip)">
        <path d={areaD} fill="url(#areaGrad)" />
        <path d={d} fill="none" stroke={C.glow} strokeWidth={20} strokeLinejoin="round" strokeLinecap="round" />
        <path d={d} fill="none" stroke={C.line} strokeWidth={8} strokeLinejoin="round" strokeLinecap="round" />
      </g>

      {/* ---------- 事件节点 + 峰值节点 ---------- */}
      {EVENTS.filter((e) => e.idx <= kf && inView(e.idx)).map((e) => (
        <circle key={e.idx} cx={x(e.idx)} cy={y(NAV[e.idx].wan)} r={7} fill={C.ink} />
      ))}
      {kf >= PEAK_I && inView(PEAK_I) ? <circle cx={x(PEAK_I)} cy={y(PEAK_WAN)} r={11} fill="#FFFFFF" /> : null}

      {/* ---------- 关键节点全宽标注（BeatOverlay）：金线 + 曲线上的金点 ---------- */}
      {BEATS.map((b, i) => {
        if (kf < b.idx) return null;
        const v = NAV[b.idx].wan;
        if (v > top) return null;
        const a = Math.min(
          clamp01((kf - b.idx) / 0.5),
          BEATS[i + 1] ? clamp01((BEATS[i + 1].idx - kf) / 0.5) : 1,
        );
        if (a <= 0.01) return null;
        const ly = y(v);
        const txt = `${b.label} ${Math.round(v).toLocaleString("en-US")} 万`;
        const tw = [...txt].reduce((s, ch) => s + (ch.charCodeAt(0) > 255 ? 23 : 12.5), 0) + 30;
        let ty = ly - 16;
        if (ty - 30 < PY0) ty = ly + 34;
        if (ty - 30 < PY0) ty = PY0 + 30;
        if (ty + 6 > MAIN_BOT) ty = MAIN_BOT - 6;
        return (
          <g key={b.idx} opacity={a}>
            <line x1={PX0} y1={ly} x2={PX1} y2={ly} stroke={C.gold} strokeWidth={2.5} strokeDasharray="18 12" opacity={0.9} />
            <rect x={PX0 + 8} y={ty - 30} width={tw} height={36} rx={8} fill="#111A33" stroke={C.gold} strokeWidth={2} />
            <text x={PX0 + 24} y={ty - 5} fill={C.gold} fontSize={23} fontWeight={800}>
              {txt}
            </text>
            {/* 曲线上的金色锚点：让"标注值此刻落在曲线哪一点"一目了然 */}
            <circle cx={x(b.idx)} cy={ly} r={7} fill={C.gold} stroke={C.bg} strokeWidth={3} />
          </g>
        );
      })}

      {/* ---------- 扫描游标（去块化：不再画整列半透明扫掠块，改细线引导） ---------- */}
      <line x1={hx} y1={hy + 26} x2={hx} y2={MAIN_BOT} stroke={C.line} strokeWidth={3} strokeDasharray="12 12" opacity={0.4} />
      {/* 笔尖：金芯 + 蓝环 + 呼吸辉光 */}
      <circle cx={hx} cy={hy} r={30} fill={C.line} opacity={0.16 + 0.12 * Math.sin(frame * 0.11)} filter="url(#penGlow)" />
      <circle cx={hx} cy={hy} r={17} fill={C.line} opacity={0.25} />
      <circle cx={hx} cy={hy} r={9} fill={C.brand} />

      {/* ---------- 浮动读数：终端式 quote chip（贴住播放头） ---------- */}
      <g>
        <line
          x1={flip ? bx + FLOAT_W : bx}
          y1={floatY + FLOAT_H}
          x2={hx}
          y2={hy}
          stroke={C.line}
          strokeWidth={3}
          opacity={0.6}
        />
        <rect x={bx} y={floatY} width={FLOAT_W} height={FLOAT_H} rx={14} fill="#111A33" stroke={C.line} strokeWidth={3} />
        <text x={bx + 20} y={floatY + 38} fill={C.brandSoft} fontSize={23} fontWeight={700}>
          当前资产
        </text>
        <text x={bx + 20} y={floatY + 80} fill="#FFFFFF" fontSize={42} fontWeight={900}>
          {Math.round(curVal).toLocaleString("en-US")}
          <tspan fontSize={25} fontWeight={700} fill={C.brandSoft}>
            {" "}万
          </tspan>
        </text>
      </g>

      {/* ---------- 阶段进度条（v6：基线 + 9 圆点 + 阶段名 + 进度计数） ---------- */}
      <line x1={PX0} y1={1572} x2={PX1} y2={1572} stroke="#23305A" strokeWidth={3} />
      {STAGES.map((s, i) => {
        const cxr = PX0 + (s.from / N) * SPAN;
        const done = i <= si;
        const curDot = i === si;
        return (
          <g key={s.from}>
            {curDot ? (
              <circle cx={cxr} cy={1572} r={16} fill={C.brand} opacity={0.2} />
            ) : null}
            <circle
              cx={cxr}
              cy={1572}
              r={done ? 8 : 6}
              fill={done ? C.brand : "#23305A"}
              stroke={curDot ? C.brandSoft : "#111A33"}
              strokeWidth={3}
            />
          </g>
        );
      })}
      <text x={PX0} y={1596} fill={C.axis} fontSize={22} fontWeight={700}>
        阶段
      </text>
      <text
        x={PX0 + 62}
        y={1596}
        fill={C.line}
        fontSize={30}
        fontWeight={800}
        opacity={0.4 + 0.6 * stageFade}
        transform={`translate(0,${(Math.sin(frame * 0.05) * 1.0).toFixed(2)})`}
      >
        {cur.name}
      </text>
      <text x={PX1} y={1596} fill={C.axis} fontSize={22} fontWeight={700} textAnchor="end">
        {si + 1} / {STAGES.length}
      </text>

      {/* ---------- 时间轴：轴线贯通，刻度随相机滚动进出 ---------- */}
      <line x1={PX0} y1={AXIS_Y} x2={PX1} y2={AXIS_Y} stroke={C.axis} strokeWidth={3} />
      {Array.from({ length: iMax - iMin + 1 }, (_, k) => iMin + k).map((i) => {
        if (i < 0 || i > N) return null;
        const a = edgeA(i);
        if (a <= 0) return null;
        const major = NAV[i].date.slice(5, 7) === "01";
        return (
          <line key={i} x1={x(i)} y1={AXIS_Y} x2={x(i)} y2={AXIS_Y + (major ? 14 : 6)}
            stroke={major ? C.axis : "#2A3758"} strokeWidth={3} opacity={a} />
        );
      })}
      {months.map((i) => {
        const a = edgeA(i);
        if (a <= 0) return null;
        return (
          <text key={i} x={x(i)} y={1540} fill={i <= kf ? C.axis : "#4A5778"} fontSize={20} fontWeight={700}
            textAnchor="middle" opacity={a}>
            {NAV[i].date.slice(2, 7)}
          </text>
        );
      })}
      <circle cx={hx} cy={AXIS_Y} r={17} fill={C.line} opacity={0.15} />
      <circle cx={hx} cy={AXIS_Y} r={8} fill={C.line} stroke={C.bg} strokeWidth={3} />
    </svg>
  );
};

export { AXIS_Y, MAIN_BOT, PX0, PX1, PY0, SAFE_X0, SAFE_X1, SAFE_Y0, SAFE_Y1 } from "./layout";
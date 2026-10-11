import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C, COPY, METRICS, NAV } from "./data";
import { BEATS, EVENTS } from "./data";
import { SAFE_X0 as SX0, SAFE_X1 as SX1, SAFE_Y0 as SY0 } from "./layout";
import { NavChart, getCam } from "./NavChart";
import { evFrame, revealAt, totalPctAt, valueAt } from "./reveal";

const FONT = '"Microsoft YaHei", "微软雅黑", "PingFang SC", sans-serif';

// v6：垂直预算与安全区统一在 src/layout.ts（正文栈 200..1720，中点 960 = 画布中线）。
// 本文件只消费，不复刻数字。

// 以下全部由 METRICS/COPY/NAV 派生。换期时只改 data.ts，Video.tsx 不得出现具体数字。
const END_WAN = parseFloat(METRICS.endAsset);
const START_Y = METRICS.startYM.slice(0, 4);

const num = (v: string) => parseFloat(v.replace(/[^\d.]/g, ""));
const fmt = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const clamp01 = (t: number) => Math.max(0, Math.min(1, t));

// 全局统一缓动：快进快出（先快后收）
const EASE = Easing.bezier(0.16, 1, 0.3, 1);

const rise = (frame: number, start: number, dur = 22) => ({
  opacity: interpolate(frame, [start, start + dur], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: EASE,
  }),
  transform: `translateY(${interpolate(frame, [start, start + dur], [26, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: EASE,
  })}px)`,
});

const ComplianceBar: React.FC = () => (
  <div
    style={{
      position: "absolute",
      left: 0,
      top: 1852,
      width: 1080,
      height: 68,
      background: "rgba(240,184,96,0.05)",
      borderTop: "2px solid #2B3A5E",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "0 40px",
      fontFamily: FONT,
    }}
  >
    <span style={{ fontSize: 28, fontWeight: 700, color: C.brand }}>历史数据模拟，切勿作为投资建议</span>
    <span style={{ fontSize: 24, fontWeight: 600, color: C.axis }}>数据源：{METRICS.source}</span>
  </div>
);

// 事件卡方向徽标：该事件当月真实环比（涨绿 / 跌红 / 起点中性）
const eventMom = (idx: number) => {
  if (idx === 0) return null;
  const r = NAV[idx].wan / NAV[idx - 1].wan - 1;
  return { up: r >= 0, txt: `${r >= 0 ? "+" : "−"}${(Math.abs(r) * 100).toFixed(2)}%` };
};

const HookScene: React.FC<{ frame: number }> = ({ frame }) => {
  const out = interpolate(frame, [78, 108], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  // 钩子数字 fs 自适应：endAsset 过千/过万时逐级收缩，避免横向溢出安全框
  const bigFS = END_WAN >= 10000 ? 96 : END_WAN >= 4000 ? 112 : 150;
  const bigUnitFS = bigFS * 0.5;
  const big = interpolate(frame, [6, 54], [0, END_WAN], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: EASE,
  });
  const chartIn = rise(frame, 12, 20);
  const flash = interpolate(frame, [70, 86], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE });
  const breathe = 0.9 + 0.1 * Math.sin(frame * 0.08);
  const badge = `${COPY.hold.replace("拿满 ", "")} · 一条线讲完`;

  return (
    <AbsoluteFill style={{ background: C.bg, opacity: out, fontFamily: FONT }}>
      {/* 钩子背景曲线：整段静态轮廓。蒙版只暴露安全列（140..940）。 */}
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          width: 1080,
          height: "100%",
          overflow: "hidden",
          ...chartIn,
          opacity: chartIn.opacity * 0.9 * breathe,
          filter: `brightness(${(1 + 0.5 * flash).toFixed(3)}) saturate(${(1 + 0.12 * flash).toFixed(3)})`,
          maskImage: `linear-gradient(to right, transparent ${SX0}px, #000 ${SX0}px, #000 ${SX1}px, transparent ${SX1}px)`,
          WebkitMaskImage: `linear-gradient(to right, transparent ${SX0}px, #000 ${SX0}px, #000 ${SX1}px, transparent ${SX1}px)`,
        }}
      >
        <NavChart cam={getCam(1, "full")} preview />
      </div>

      {/* 钩子文案：垂直中心压在 960 中线的 860..1140 一带（图区空档），水平对称居中 */}
      <div style={{ position: "absolute", top: 546, left: SX0, width: SX1 - SX0, textAlign: "center" }}>
        <div style={{ fontSize: 40, fontWeight: 700, color: C.axis, letterSpacing: 4, ...rise(frame, 0, 16) }}>
          假如你不小心
        </div>
        <div
          style={{
            fontSize: bigFS,
            fontWeight: 900,
            color: C.brand,
            lineHeight: 1.12,
            marginTop: 26,
            letterSpacing: -2,
            whiteSpace: "nowrap",
            ...rise(frame, 4, 16),
          }}
        >
          {fmt(big)}
          <span style={{ fontSize: bigUnitFS, fontWeight: 800 }}> 万</span>
        </div>
        <div
          style={{
            fontSize: 40,
            fontWeight: 700,
            color: C.brandSoft,
            marginTop: 18,
            whiteSpace: "nowrap",
            ...rise(frame, 18, 16),
          }}
        >
          {METRICS.name} · {COPY.hookSub}
        </div>
        <div style={{ fontSize: 34, fontWeight: 700, color: C.down, marginTop: 24, whiteSpace: "nowrap", ...rise(frame, 30, 16) }}>
          中间最大回撤 {METRICS.mdd}
        </div>
      </div>

      {/* 终局快闪落款 */}
      <div
        style={{
          position: "absolute",
          top: 1112,
          left: SX0 + 120,
          width: SX1 - SX0 - 240,
          textAlign: "center",
          fontSize: 30,
          fontWeight: 800,
          color: C.brandSoft,
          background: "rgba(13,20,40,0.92)",
          border: `2px solid ${C.brand}`,
          borderRadius: 999,
          padding: "12px 0",
          letterSpacing: 2,
          opacity: flash,
        }}
      >
        {badge}
      </div>
      <ComplianceBar />
    </AbsoluteFill>
  );
};

export const StockVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const reveal = revealAt(frame);
  const cam = getCam(reveal);
  const revealIdx = cam.curIdx;

  const cardIdx = EVENTS.reduce((acc, e, i) => (frame >= evFrame(e.idx) ? i : acc), 0);
  const card = EVENTS[cardIdx];
  const cardAt = evFrame(card.idx);
  const nextAt = cardIdx + 1 < EVENTS.length ? evFrame(EVENTS[cardIdx + 1].idx) : Infinity;
  const cardAlpha =
    Math.min(clamp01((frame - cardAt) / 15), nextAt === Infinity ? 1 : clamp01((nextAt - frame) / 13.5)) *
    interpolate(frame, [durationInFrames - 300, durationInFrames - 240], [1, 0], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

  const prevVal = cardIdx === 0 ? 100 : num(EVENTS[cardIdx - 1].value);
  const shownVal = interpolate(frame, [cardAt, cardAt + 22], [prevVal, num(card.value)], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: EASE,
  });

  // 报价 HUD 数据：跟笔尖实时
  const curWan = valueAt(frame);
  const totalPct = totalPctAt(frame);

  // 快闪亮卡
  const beatFlash = BEATS.map((b) => {
    const at = evFrame(b.idx);
    const dur = frame - at;
    const a = clamp01(dur / 5) * clamp01((28 - dur) / 12);
    const pop = clamp01((5 - dur) / 5);
    return a > 0.012 ? { b, a, pop } : null;
  }).filter((x): x is { b: (typeof BEATS)[number]; a: number; pop: number } => x !== null);

  const closing = interpolate(frame, [durationInFrames - 300, durationInFrames - 240], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const nowAt = new Date(Number(START_Y), Number(NAV[0].date.slice(5, 7)) - 1, 23);
  nowAt.setMonth(nowAt.getMonth() + revealIdx);
  const nowStr = `${nowAt.getFullYear()}/${String(nowAt.getMonth() + 1).padStart(2, "0")}`;

  const titleBar = interpolate(frame, [104, 156], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE });

  return (
    <AbsoluteFill style={{ background: C.bg, fontFamily: FONT }}>
      <div style={{ position: "absolute", left: 0, top: 0, width: 1080, height: 10, background: C.brand }} />

      {/* ── 标头行（200..279）：左 期号+标的　右 月份+代码，底缘细分隔线 ── */}
      <div
        style={{
          position: "absolute",
          top: SY0,
          left: SX0,
          width: SX1 - SX0,
          height: 79,
          borderBottom: "3px solid #1C2A4A",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          fontSize: 30,
          fontWeight: 700,
          color: C.axis,
          letterSpacing: 2,
          ...rise(frame, 84, 20),
        }}
      >
        <span>
          {METRICS.episode} · {METRICS.name}
        </span>
        <span>{METRICS.months} · {METRICS.code}</span>
      </div>

      {/* ── 报价 HUD（288..408）：终端式双格 —— 当前资产 / 累计收益 ── */}
      <div style={{ position: "absolute", top: 288, left: SX0, width: SX1 - SX0, display: "flex", gap: 18, ...rise(frame, 104, 24) }}>
        {/* 左格：当前资产（白，跟笔尖实时） */}
        <div style={{ flex: 1, background: C.panel, border: `3px solid ${C.grid}`, borderRadius: 20, padding: "14px 22px", position: "relative", overflow: "hidden" }}>
          <div style={{ position: "absolute", left: 0, top: 0, width: 6, height: "100%", background: C.line }} />
          <div style={{ fontSize: 22, fontWeight: 700, color: C.inkSoft }}>当前资产</div>
          <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginTop: 2 }}>
            <span style={{ fontSize: 48, fontWeight: 900, color: "#FFFFFF", letterSpacing: -1, lineHeight: 1.1 }}>
              {Math.round(curWan).toLocaleString("en-US")}
            </span>
            <span style={{ fontSize: 26, fontWeight: 700, color: C.brandSoft }}>万</span>
          </div>
          <div style={{ fontSize: 21, fontWeight: 600, color: C.axis, marginTop: 2 }}>
            第 {revealIdx + 1} / {NAV.length} 月 · {nowStr}
          </div>
        </div>
        {/* 右格：累计收益（金，跟笔尖实时） */}
        <div style={{ flex: 1, background: C.panel, border: `3px solid ${C.grid}`, borderRadius: 20, padding: "14px 22px", position: "relative", overflow: "hidden" }}>
          <div style={{ position: "absolute", left: 0, top: 0, width: 6, height: "100%", background: C.brand }} />
          <div style={{ fontSize: 22, fontWeight: 700, color: C.inkSoft }}>累计收益</div>
          <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginTop: 2 }}>
            <span style={{ fontSize: 46, fontWeight: 900, color: totalPct >= 0 ? C.brand : C.down, letterSpacing: -1, lineHeight: 1.1 }}>
              {totalPct.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}%
            </span>
          </div>
          <div style={{ fontSize: 21, fontWeight: 600, color: C.amber, marginTop: 2 }}>
            年化 {METRICS.cagr} · 回撤 {METRICS.mdd}
          </div>
        </div>
      </div>

      {/* ── 标题两行（434..613）+ 金色下划线进度 ── */}
      <div
        style={{
          position: "absolute",
          top: 434,
          left: SX0,
          width: SX1 - SX0,
          ...rise(frame, 92, 24),
        }}
      >
        <div style={{ fontSize: 72, fontWeight: 900, color: C.brand, lineHeight: 1.1, whiteSpace: "nowrap" }}>假如你不小心</div>
        <div style={{ fontSize: 44, fontWeight: 700, color: C.ink, marginTop: 6, whiteSpace: "nowrap" }}>{START_Y} 年买 100 万</div>
        <div style={{ position: "relative", width: 180, height: 6, marginTop: 14 }}>
          <div style={{ position: "absolute", left: 0, top: 0, width: 180, height: 6, background: "rgba(240,184,96,0.22)", transformOrigin: "left center", transform: `scaleX(${titleBar})` }} />
        </div>
      </div>

      <NavChart cam={cam} />

      {/* ── 快闪亮卡（y 866..1036，绘图区内不挡浮动读数） ── */}
      {beatFlash.map(({ b, a, pop }) => (
        <div
          key={b.idx}
          style={{
            position: "absolute",
            left: SX0 + 50,
            top: 866,
            width: SX1 - SX0 - 100,
            height: 170,
            borderRadius: 22,
            background: "linear-gradient(135deg, #FFFDF4, #FFF6E0)",
            border: `3px solid ${C.brand}`,
            boxShadow: "0 12px 44px rgba(6,12,32,0.75)",
            opacity: a,
            transform: `scale(${(1 + 0.06 * pop).toFixed(2)})`,
            transformOrigin: "center center",
            padding: "22px 40px 18px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <span style={{ fontSize: 24, fontWeight: 800, color: "#8A6D2F", letterSpacing: 3 }}>关键节点</span>
            <span style={{ fontSize: 22, fontWeight: 800, color: "#B08030" }}>{NAV[b.idx].date.slice(0, 7).replace("-", " / ")}</span>
          </div>
          <div style={{ fontSize: 52, fontWeight: 900, color: "#1B2440", marginTop: 6, letterSpacing: -1 }}>{b.label}</div>
          <div style={{ fontSize: 26, fontWeight: 800, color: "#B0792F", marginTop: 4 }}>
            {Math.round(NAV[b.idx].wan).toLocaleString("en-US")} 万 · 随线点亮
          </div>
        </div>
      ))}

      {/* ── 事件卡（1608..1720，紧凑三行） ── */}
      <div
        style={{
          position: "absolute",
          top: 1608,
          left: SX0,
          width: SX1 - SX0,
          height: 112,
          background: C.panel,
          borderRadius: 18,
          border: `3px solid ${C.grid}`,
          boxShadow: "0 6px 22px rgba(6,12,32,0.6)",
          overflow: "hidden",
          opacity: cardAlpha,
        }}
      >
        <div style={{ position: "absolute", left: 0, top: 0, width: 8, height: "100%", background: C.brand }} />
        <div style={{ padding: "10px 26px 0 30px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{ fontSize: 24, fontWeight: 800, color: C.ink }}>{card.tag}</span>
            <span style={{ fontSize: 19, fontWeight: 800, color: C.bg, background: C.brand, borderRadius: 7, padding: "2px 10px" }}>
              {card.type}
            </span>
            {(() => {
              const m = eventMom(card.idx);
              if (!m)
                return (
                  <span style={{ fontSize: 18, fontWeight: 800, color: C.inkSoft, background: "#202C4E", borderRadius: 7, padding: "2px 9px" }}>
                    起点
                  </span>
                );
              return (
                <span style={{ fontSize: 18, fontWeight: 800, color: m.up ? C.bg : "#FFFFFF", background: m.up ? C.up : C.down, borderRadius: 7, padding: "2px 9px" }}>
                  {m.txt}
                </span>
              );
            })()}
            <span style={{ fontSize: 20, fontWeight: 700, color: C.axis, marginLeft: "auto" }}>{nowStr}</span>
          </div>
          <div style={{ display: "flex", alignItems: "flex-start", gap: 22, marginTop: 6 }}>
            <span style={{ fontSize: 38, fontWeight: 900, color: C.brand, letterSpacing: -1, lineHeight: 1.15, whiteSpace: "nowrap" }}>
              {fmt(shownVal)} 万
            </span>
            <span style={{ fontSize: 21, fontWeight: 600, color: C.inkSoft, lineHeight: 1.4, marginTop: 2 }}>{card.body}</span>
          </div>
        </div>
      </div>

      {/* ── 收尾结语条（与事件卡同位，互斥淡入淡出） ── */}
      <div
        style={{
          position: "absolute",
          top: 1608,
          left: SX0 + 8,
          width: SX1 - SX0 - 16,
          height: 112,
          borderRadius: 18,
          background: "#14213F",
          border: `3px solid ${C.brand}`,
          boxShadow: "0 6px 22px rgba(6,12,32,0.65)",
          padding: "6px 30px 0",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          opacity: interpolate(closing, [0.35, 1], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        }}
      >
        <div style={{ fontSize: 28, fontWeight: 900, color: C.ink, lineHeight: 1.16 }}>这条曲线最值得看的不是终点</div>
        <div style={{ fontSize: 22, fontWeight: 800, color: C.brandSoft, marginTop: 3, lineHeight: 1.15 }}>{COPY.closingQ}</div>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 5, paddingTop: 5, borderTop: `2px solid ${C.grid}` }}>
          <span style={{ fontSize: 20, fontWeight: 800, color: C.ink, lineHeight: 1.15 }}>
            100 万买入 · {END_WAN.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} 万 · {COPY.hold}
          </span>
          <span style={{ fontSize: 19, fontWeight: 800, color: C.brand, lineHeight: 1.15 }}>关注 + 点名，下期做你的持仓</span>
        </div>
      </div>

      <ComplianceBar />
      <HookScene frame={frame} />
    </AbsoluteFill>
  );
};
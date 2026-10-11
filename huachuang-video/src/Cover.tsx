/** A/B 封面组件（v6）：与成片同源的安全区（对称 x∈[140,940]），
 *  文案站整体下移居中，单行大数字水平居中；曲线作底部装饰背景 */
import React from "react";
import { AbsoluteFill } from "remotion";
import { C, COPY, METRICS, NAV, YMAX } from "./data";

const FONT = '"Microsoft YaHei", "微软雅黑", "PingFang SC", sans-serif';
const SX0 = 140, SX1 = 940, SY0 = 200, SY1 = 1720;
const W = SX1 - SX0;
/** 从上版安全区 (130..1440) 下移，让海报正文站垂直居中（约 960 中线） */
const SH = 168;
/** 底部金色收尾条（1416..1508）与页脚（1494..）的位置 */
const BOTBAR = 1416;
const FOOT = 1592;

const PK = NAV.reduce((a, p, i) => (p.wan > NAV[a].wan ? i : a), 0);
const END = NAV.length - 1;
const DD_MIN = NAV.reduce((a, p, i) => (p.dd < NAV[a].dd ? i : a), 0);

// 全部数字从 METRICS/NAV 现取，不在本文件写死
const TOTAL = parseFloat(METRICS.totalRet);
const TOTAL_FLOOR = Math.floor(TOTAL);
const MIN_WAN = parseFloat(METRICS.minAsset);
const MIN_IDX = NAV.reduce((a, p, i) => (p.wan < NAV[a].wan ? i : a), 0);
const BELOW = 100 - MIN_WAN;
// 是否曾跌破本金
const BROKE_PAR = BELOW > 0.005;
const START_Y = METRICS.startYM.slice(0, 4);
const END_YM = METRICS.range.split(" ~ ")[1];

const CX0 = SX0 + 30, CX1 = SX1 - 30;
const CY0 = 980, CY1 = 1280;
const CYMAX = YMAX;
const ccx = (i: number) => CX0 + (i / END) * (CX1 - CX0);
const ccy = (v: number) => CY1 - ((CY1 - CY0) * v) / CYMAX;

function CoverCurve() {
  const d = NAV.map((p, i) => `${i ? "L" : "M"}` + ccx(i).toFixed(1) + "," + ccy(p.wan).toFixed(1)).join(" ");
  const ticks = [0, 1, 2, 3, 4].map((i) => Math.round((CYMAX * i) / 4 / 10) * 10);
  return (
    <svg width={1080} height={1920} style={{ position: "absolute", left: 0, top: 0 }}>
      {ticks.map((v: number) => (
        <line key={v} x1={CX0} y1={ccy(v)} x2={CX1} y2={ccy(v)} stroke={C.grid} strokeWidth={2} />
      ))}
      <path d={d} fill="none" stroke={C.glow} strokeWidth={26} strokeLinejoin="round" strokeLinecap="round" />
      <path d={d} fill="none" stroke={C.line} strokeWidth={12} strokeLinejoin="round" strokeLinecap="round" />
      <circle cx={ccx(PK)} cy={ccy(NAV[PK].wan)} r={13} fill="#FFFFFF" />
      <text x={CX1} y={CY1 + 46} fill={C.axis} fontSize={24} fontWeight={700} textAnchor="end">
        {START_Y}-01 → {END_YM} · {END + 1} 个月
      </text>
    </svg>
  );
}

const CENTER = { textAlign: "center" as const };

export const CoverA: React.FC = () => (
  <AbsoluteFill style={{ background: C.bg, fontFamily: FONT }}>
    <div style={{ position: "absolute", left: 0, top: 0, width: 1080, height: 10, background: C.brand }} />
    <CoverCurve />

    <div style={{ position: "absolute", top: SY0 + SH, left: SX0, width: W, display: "flex", justifyContent: "space-between", fontSize: 28, fontWeight: 700, color: C.axis, letterSpacing: 2 }}>
      <span>{METRICS.episode} · 假如你不小心</span>
      <span>{METRICS.name} {METRICS.code}</span>
    </div>

    <div style={{ position: "absolute", top: 196 + SH, left: SX0, width: W, fontSize: 60, fontWeight: 700, color: C.brandSoft, lineHeight: 1.2, ...CENTER }}>
      {START_Y} 年 1 月 100 万买入
    </div>

    <div style={{ position: "absolute", top: 318 + SH, left: SX0, width: W, fontSize: 168, fontWeight: 900, color: C.brand, lineHeight: 1.02, letterSpacing: -4, whiteSpace: "nowrap", ...CENTER }}>
      {TOTAL_FLOOR}<span style={{ fontSize: 84, fontWeight: 800 }}>%</span>
    </div>

    <div style={{ position: "absolute", top: 548 + SH, left: SX0, width: W, fontSize: 54, fontWeight: 900, color: C.ink, lineHeight: 1.2, ...CENTER }}>
      {COPY.hold}
    </div>

    <div style={{ position: "absolute", top: 686 + SH, left: SX0, width: W, display: "flex", gap: 16 }}>
      <div style={{ flex: 1, background: C.panel, border: `2px solid ${C.grid}`, borderRadius: 18, padding: "20px 22px" }}>
        <div style={{ fontSize: 26, fontWeight: 700, color: C.inkSoft }}>年化收益</div>
        <div style={{ fontSize: 50, fontWeight: 900, color: C.brand, marginTop: 6 }}>{METRICS.cagr}</div>
      </div>
      <div style={{ flex: 1, background: C.panel, border: `2px solid ${C.grid}`, borderRadius: 18, padding: "20px 22px" }}>
        <div style={{ fontSize: 26, fontWeight: 700, color: C.inkSoft }}>最大回撤</div>
        <div style={{ fontSize: 50, fontWeight: 900, color: C.down, marginTop: 6 }}>{METRICS.mdd}</div>
      </div>
    </div>

    <div style={{ position: "absolute", top: BOTBAR, left: SX0, width: W, height: 92, borderRadius: 18, background: "#14213F", border: `3px solid ${C.brand}`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 36, fontWeight: 800, color: C.brandSoft }}>
      {BROKE_PAR ? `中间最深只剩 ${METRICS.minAsset}` : `中间最大回撤 ${METRICS.mdd}`}
    </div>

    <div style={{ position: "absolute", top: FOOT, left: SX0, width: W, fontSize: 26, fontWeight: 600, color: C.axis }}>
      数据源：东方财富 月K 前复权 · 历史数据模拟，切勿作为投资建议
    </div>
  </AbsoluteFill>
);

export const CoverB: React.FC = () => {
  // 破净过的：谷底 = 只剩最少钱的那个月。
  // 从未破净的（黄金等）：谷底 = 从峰值回撤最深的那个月。
  const I = BROKE_PAR ? MIN_IDX : DD_MIN;
  const I_WAN = NAV[I].wan;
  const I_DD = -NAV[I].dd * 100;
  const ym = (s: string) => s.slice(0, 7).replace("-", "年") + "月";
  const I_YM = ym(NAV[I].date);
  const PK_WAN = parseFloat(METRICS.peakAsset);
  const LOST = PK_WAN - I_WAN;
  const BIG_FS = BROKE_PAR ? 168 : 148;
  const BIG_UNIT = BROKE_PAR ? 84 : 76;

  return (
    <AbsoluteFill style={{ background: C.bg, fontFamily: FONT }}>
      <div style={{ position: "absolute", left: 0, top: 0, width: 1080, height: 10, background: C.down }} />
      <CoverCurve />

      <div style={{ position: "absolute", top: SY0 + SH, left: SX0, width: W, display: "flex", justifyContent: "space-between", fontSize: 28, fontWeight: 700, color: C.axis, letterSpacing: 2 }}>
        <span>{METRICS.episode} · 最痛的一段</span>
        <span>{METRICS.name} {METRICS.code}</span>
      </div>

      {BROKE_PAR ? (
        <>
          <div style={{ position: "absolute", top: 196 + SH, left: SX0, width: W, fontSize: 64, fontWeight: 700, color: C.inkSoft, lineHeight: 1.18, ...CENTER }}>
            100 万买入
          </div>
          <div style={{ position: "absolute", top: 290 + SH, left: SX0, width: W, fontSize: 64, fontWeight: 900, color: C.ink, lineHeight: 1.18, ...CENTER }}>
            {I_YM}，只剩
          </div>
          <div style={{ position: "absolute", top: 414 + SH, left: SX0, width: W, fontSize: BIG_FS, fontWeight: 900, color: C.down, lineHeight: 1.02, letterSpacing: -4, whiteSpace: "nowrap", ...CENTER }}>
            {I_WAN.toFixed(2)}<span style={{ fontSize: BIG_UNIT, fontWeight: 800 }}> 万</span>
          </div>
          <div style={{ position: "absolute", top: 660 + SH, left: SX0, width: W, fontSize: 44, fontWeight: 800, color: C.brandSoft, lineHeight: 1.3, ...CENTER }}>
            比本金还少 {(100 - I_WAN).toFixed(2)} 万
          </div>
          <div style={{ position: "absolute", top: 790 + SH, left: SX0, width: W, display: "flex", gap: 16 }}>
            <div style={{ flex: 1, background: C.panel, border: `2px solid ${C.grid}`, borderRadius: 18, padding: "20px 22px" }}>
              <div style={{ fontSize: 26, fontWeight: 700, color: C.inkSoft }}>谷底月份</div>
              <div style={{ fontSize: 44, fontWeight: 900, color: C.ink, marginTop: 6 }}>{I_YM}</div>
            </div>
            <div style={{ flex: 1, background: C.panel, border: `2px solid ${C.grid}`, borderRadius: 18, padding: "20px 22px" }}>
              <div style={{ fontSize: 26, fontWeight: 700, color: C.inkSoft }}>谷底回撤</div>
              <div style={{ fontSize: 44, fontWeight: 900, color: C.down, marginTop: 6 }}>−{I_DD.toFixed(2)}%</div>
            </div>
          </div>
        </>
      ) : (
        <>
          <div style={{ position: "absolute", top: 196 + SH, left: SX0, width: W, fontSize: 60, fontWeight: 700, color: C.inkSoft, lineHeight: 1.18, ...CENTER }}>
            100 万买入
          </div>
          <div style={{ position: "absolute", top: 288 + SH, left: SX0, width: W, fontSize: 54, fontWeight: 900, color: C.ink, lineHeight: 1.18, ...CENTER }}>
            {I_YM}，从峰值回撤到
          </div>
          <div style={{ position: "absolute", top: 424 + SH, left: SX0, width: W, fontSize: BIG_FS, fontWeight: 900, color: C.down, lineHeight: 1.02, letterSpacing: -4, whiteSpace: "nowrap", ...CENTER }}>
            {I_WAN.toFixed(2)}<span style={{ fontSize: BIG_UNIT, fontWeight: 800 }}> 万</span>
          </div>
          <div style={{ position: "absolute", top: 658 + SH, left: SX0, width: W, fontSize: 42, fontWeight: 800, color: C.brandSoft, lineHeight: 1.3, ...CENTER }}>
            从最高 {(PK_WAN).toFixed(2)} 万峰值掉了 {LOST.toFixed(2)} 万
          </div>
          <div style={{ position: "absolute", top: 786 + SH, left: SX0, width: W, display: "flex", gap: 16 }}>
            <div style={{ flex: 1, background: C.panel, border: `2px solid ${C.grid}`, borderRadius: 18, padding: "20px 22px" }}>
              <div style={{ fontSize: 26, fontWeight: 700, color: C.inkSoft }}>谷底月份</div>
              <div style={{ fontSize: 44, fontWeight: 900, color: C.ink, marginTop: 6 }}>{I_YM}</div>
            </div>
            <div style={{ flex: 1, background: C.panel, border: `2px solid ${C.grid}`, borderRadius: 18, padding: "20px 22px" }}>
              <div style={{ fontSize: 26, fontWeight: 700, color: C.inkSoft }}>谷底回撤</div>
              <div style={{ fontSize: 44, fontWeight: 900, color: C.down, marginTop: 6 }}>−{I_DD.toFixed(2)}%</div>
            </div>
          </div>
        </>
      )}

      <div style={{ position: "absolute", top: BOTBAR, left: SX0, width: W, height: 92, borderRadius: 18, background: "#0F1931", border: `3px solid ${C.down}`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 34, fontWeight: 800, color: C.ink, textAlign: "center" }}>
        {BROKE_PAR ? `后来涨到 ${METRICS.peakAsset}` : `最高 ${METRICS.peakAsset} · ${COPY.hold} · 仍剩 ${METRICS.endAsset}`}
      </div>

      <div style={{ position: "absolute", top: FOOT, left: SX0, width: W, fontSize: 26, fontWeight: 600, color: C.axis }}>
        {I_YM} 触底 · 东方财富 月K 前复权 · 切勿作为投资建议
      </div>
    </AbsoluteFill>
  );
};
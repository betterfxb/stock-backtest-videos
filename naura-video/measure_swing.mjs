/**
 * 起伏度量：比较固定轴 vs 动态轴下，曲线在屏幕上占多少纵向像素。
 *
 * 用户的原话是"刻度是1000万但波动只有几十万，根本没起伏"。
 * 这里直接量化：对每个数据月，算它与前一个月的净值差，
 * 在两种轴下折算成像素高度差（v5.0：绘图高度 OFF=500px）。
 */
import fs from "fs";
import { pathToFileURL } from "url";

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
const NAV = [...block("const NAV").matchAll(/date:\s*"([\d-]+)",\s*close:\s*([\d.]+),\s*wan:\s*([\d.]+)/g)]
  .map((m) => ({ date: m[1], wan: +m[3] }));
const AXIS_TOP = (await import(pathToFileURL("out/axis.mjs").href)).AXIS_TOP;

const OFF = 500;
const FIXED = 8000;
const N = NAV.length - 1;
const { evFrame } = await import(pathToFileURL("out/reveal.mjs").href);
const frameOf = (i) => Math.round(evFrame(i));

const px = (dWan, top) => (OFF * dWan) / top;

const rows = [];
for (let i = 1; i <= N; i++) {
  const d = Math.abs(NAV[i].wan - NAV[i - 1].wan);
  rows.push({ i, date: NAV[i].date, d, fixed: px(d, FIXED), dyn: px(d, AXIS_TOP[frameOf(i)]) });
}

const bear = rows.filter((r) => r.i >= 7 && r.i <= 38);
const sum = (a, k) => a.reduce((s, r) => s + r[k], 0);

console.log("== 全部 80 段月度变化，折算成屏幕像素 ==");
console.log(`固定轴 YMAX=8000  平均 ${(sum(rows, "fixed") / rows.length).toFixed(2)}px   ` +
  `最大 ${Math.max(...rows.map((r) => r.fixed)).toFixed(2)}px   ` +
  `<2px 的月数 ${rows.filter((r) => r.fixed < 2).length}`);
console.log(`动态轴            平均 ${(sum(rows, "dyn") / rows.length).toFixed(2)}px   ` +
  `最大 ${Math.max(...rows.map((r) => r.dyn)).toFixed(2)}px   ` +
  `<2px 的月数 ${rows.filter((r) => r.dyn < 2).length}`);

console.log("\n== 长熊段 idx7~38（净值 78~474 万，固定轴下最难看的地方）==");
console.log(`固定轴  平均 ${(sum(bear, "fixed") / bear.length).toFixed(2)}px   最大 ${Math.max(...bear.map((r) => r.fixed)).toFixed(2)}px`);
console.log(`动态轴  平均 ${(sum(bear, "dyn") / bear.length).toFixed(2)}px   最大 ${Math.max(...bear.map((r) => r.dyn)).toFixed(2)}px`);
console.log(`放大倍数 平均 ${(sum(bear, "dyn") / sum(bear, "fixed")).toFixed(1)}x`);

console.log("\n== 逐月明细（idx 6~20，2020 高点回落到熊市）==");
console.log("idx  date        变化万    固定轴px   动态轴px   轴顶");
for (const r of rows.filter((x) => x.i >= 6 && x.i <= 20)) {
  console.log(
    String(r.i).padStart(3), r.date,
    r.d.toFixed(1).padStart(9),
    r.fixed.toFixed(2).padStart(10),
    r.dyn.toFixed(2).padStart(10),
    String(AXIS_TOP[frameOf(r.i)]).padStart(7),
  );
}

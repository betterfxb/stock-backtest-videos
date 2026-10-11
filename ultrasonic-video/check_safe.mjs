/**
 * UI 安全区校验：逐帧扫描像素，区分「核心内容」与「豁免装饰」。
 *
 * 规则（1080×1920 抖音竖版，v6 中心对称安全区）：
 *   核心内容必须落在 x∈[140,940]  y∈[200,1720]  （正文栈中点 960 = 画布中线）
 *   豁免：顶部品牌线 y∈[0,12]、底部合规条 y∈[1850,1920]、
 *         背景底色/面板/网格/曲线辉光等装饰色
 *
 * 用法: node check_safe.mjs out [更多目录...]
 */
import fs from "fs";
import path from "path";
import { PNG } from "pngjs";

const W = 1080, H = 1920;
const SAFE = { x0: 140, x1: 940, y0: 200, y1: 1720 };
const EXEMPT_BANDS = [
  { name: "顶部品牌线", y0: 0, y1: 12 },
  { name: "底部合规条", y0: 1850, y1: 1920 },
];

// 装饰色板（背景、面板、网格、曲线辉光）—— 与 data.ts C 同步；回撤大块已移除
const DECOR = [
  [10, 17, 40], [14, 23, 48], [20, 31, 61], [28, 42, 74], [22, 64, 124],
];

const near = (r, g, b, c, tol = 16) =>
  Math.abs(r - c[0]) <= tol && Math.abs(g - c[1]) <= tol && Math.abs(b - c[2]) <= tol;

function inExempt(y) {
  return EXEMPT_BANDS.find((b) => y >= b.y0 && y <= b.y1);
}

const dirs = process.argv.slice(2);
if (!dirs.length) dirs.push("out");

const files = dirs.flatMap((d) =>
  fs.readdirSync(d).filter((f) => f.endsWith(".png")).map((f) => path.join(d, f)),
).sort();

if (!files.length) {
  console.log("未找到 png 帧");
  process.exit(1);
}

let globalWorst = { right: -1, bottom: -1, top: 9999, left: 9999, frame: "" };
const offenders = [];

for (const f of files) {
  const png = PNG.sync.read(fs.readFileSync(f));
  let minX = W, maxX = -1, minY = H, maxY = -1;
  let rightAt = null, bottomAt = null, leftAt = null, topAt = null;

  for (let y = 0; y < H; y++) {
    const ex = inExempt(y);
    for (let x = 0; x < W; x++) {
      const i = (png.width * y + x) << 2;
      const r = png.data[i], g = png.data[i + 1], b = png.data[i + 2];
      if (r + g + b < 120) continue;                 // 近黑背景
      if (DECOR.some((c) => near(r, g, b, c))) continue;
      if (ex) continue;                              // 豁免带
      if (x > maxX) { maxX = x; rightAt = [x, y, r, g, b]; }
      if (x < minX) { minX = x; leftAt = [x, y, r, g, b]; }
      if (y > maxY) { maxY = y; bottomAt = [x, y, r, g, b]; }
      if (y < minY) { minY = y; topAt = [x, y, r, g, b]; }
    }
  }
  if (maxX < 0) continue;

  const bad = [];
  if (maxX > SAFE.x1) bad.push(`右溢 ${maxX} (+${maxX - SAFE.x1}) @y${rightAt[1]} rgb(${rightAt[2]},${rightAt[3]},${rightAt[4]})`);
  if (minX < SAFE.x0) bad.push(`左溢 ${minX} (-${SAFE.x0 - minX}) @y${leftAt[1]}`);
  if (maxY > SAFE.y1) bad.push(`下溢 ${maxY} (+${maxY - SAFE.y1}) @x${bottomAt[0]} rgb(${bottomAt[2]},${bottomAt[3]},${bottomAt[4]})`);
  if (minY < SAFE.y0) bad.push(`上溢 ${minY} (-${SAFE.y0 - minY}) @x${topAt[0]}`);
  if (bad.length) offenders.push(`${path.basename(f)}: ${bad.join(" | ")}`);

  if (maxX > globalWorst.right) globalWorst.right = maxX, globalWorst.frame = f;
  if (maxY > globalWorst.bottom) globalWorst.bottom = maxY;
  if (minY < globalWorst.top) globalWorst.top = minY;
  if (minX < globalWorst.left) globalWorst.left = minX;
}

console.log(`扫描 ${files.length} 帧`);
console.log(`核心内容安全区: x∈[${SAFE.x0},${SAFE.x1}]  y∈[${SAFE.y0},${SAFE.y1}]`);
console.log(`豁免带: ${EXEMPT_BANDS.map((b) => `${b.name} y${b.y0}-${b.y1}`).join("  ")}`);
console.log(`核心内容实测极值: 右 ${globalWorst.right}  下 ${globalWorst.bottom}  上 ${globalWorst.top}  左 ${globalWorst.left}`);

if (offenders.length) {
  console.log(`\n✗ 越界帧 ${offenders.length}/${files.length}:`);
  offenders.forEach((o) => console.log("  " + o));
} else {
  console.log("\n✓ 全部帧核心内容均在安全区内");
}
process.exit(offenders.length ? 1 : 0);
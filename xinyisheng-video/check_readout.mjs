/**
 * 读数校验 v2：靠"找出标签盒子"而不是"预测标签在哪"。
 *
 * v1 的做法是按几何公式预测盒子位置，再在该位置数白字像素。改动态纵轴后
 * 连续 5 帧 FAIL，但 diag 显示这些帧的粉边/盒底/白字都存在 —— 说明预测
 * 偏了，不是标签没画出来。预测式校验把"标签被覆盖"和"标签挪了位置"
 * 混成一个 FAIL，测不出真问题。
 *
 * v2 改成：先在绘图区内找出宽约 208px 的粉色边框（标签盒的上下边），
 * 由它反推盒子的真实位置，再统计盒内白字。这样与几何公式解耦，
 * 轴怎么变都不影响校验的有效性。
 */
import fs from "fs";
import path from "path";
import { PNG } from "pngjs";
import { AXIS_TOP } from "./out/axis.mjs";
// v5.0：版面与配速全部同源 import —— 校验器不得复刻任何公式/常量。
// 前提：out/*.mjs 与 src/data.ts 同步重建（esbuild 三个 bundle）。
import { CORNER, FLOAT_H, FLOAT_W, PY0, SAFE_X0, SAFE_X1, SAFE_Y0, SAFE_Y1, TOTAL_FRAMES } from "./out/layout.mjs";
import { REVEAL_END, REVEAL_START, valueAt } from "./out/reveal.mjs";

// v5.2：浮标边框色 = 曲线亮蓝 C.line(#4E9EFF)，不再用粉色判据。
// b>190 把「环比 +x%」的绿色文字行（C.up #4FD39A b≈154）排除在外，
// 避免把短绿字行误当成标签盒边。
const isBoxEdge = (r, g, b) => r > 40 && r < 170 && g > 110 && g < 220 && b > 190;
const isWhite = (r, g, b) => r > 215 && g > 215 && b > 215;

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

// 月数从 data.ts 现取，不写死 80 —— 换标的月份数不同，写死会静默错位。
const N = NAV.length - 1;
console.log(`数据 ${NAV.length} 个月（末月下标 ${N}）  reveal ${REVEAL_START}..${REVEAL_END}\n`);

/** 找出标签盒：返回 {x, y} 左上角，找不到返回 null */
function findBox(png) {
  const { width, data } = png;
  // 标签盒上下边是长约 FLOAT_W 的粉色横线。在绘图区内找最长的一行。
  const rows = [];
  for (let y = PY0 - 30; y <= SAFE_Y1; y++) {
    let best = 0, run = 0, bestX = -1, runX = 0;
    for (let x = 0; x < width; x++) {
      const i = (width * y + x) << 2;
      if (isBoxEdge(data[i], data[i + 1], data[i + 2])) {
        if (run === 0) runX = x;
        run++;
        if (run > best) { best = run; bestX = runX; }
      } else run = 0;
    }
    // 圆角矩形顶边实心段会比 FLOAT_W 略短，取 >=150 视为候选
    if (best >= 150) rows.push({ y, x: bestX, len: best });
  }

  // 相隔约 FLOAT_H 的两条横线 = 同一盒子的上下边；取左边缘最靠右的一对（标签优先贴笔尖）
  let bestPair = null;
  for (let a = 0; a < rows.length; a++) {
    for (let b = a + 1; b < rows.length; b++) {
      const h = rows[b].y - rows[a].y;
      if (h < 60) continue;
      if (h > FLOAT_H + 30) break;
      const dx = Math.abs(rows[b].x - rows[a].x);
      if (dx > 12) continue;
      // rows[].x 是边框**实心段**的起点，圆角处（rx=14）不算实心，
      // 所以真实左缘要再往左退一个圆角半径。不扣这一下会凭空多算 14px 宽度，
      // 把贴右缘合法的标签误报成越界。
      const pair = { y: rows[a].y, x: Math.max(0, rows[a].x - CORNER), h };
      if (!bestPair || pair.x > bestPair.x) bestPair = pair;
    }
  }
  return bestPair;
}

const dir = process.argv[2] || "out";
const files = fs.readdirSync(dir).filter((f) => /^f\d+\.png$/.test(f)).sort();
let fail = 0, skipped = 0;

console.log("frame    真实值   轴顶    标签盒(x,y)        盒宽  盒内白字   判定");
console.log("-".repeat(84));

for (const f of files) {
  const frame = parseInt(f.match(/(\d+)\.png$/)[1], 10);
  const val = valueAt(frame);
  const top = AXIS_TOP[Math.max(0, Math.min(TOTAL_FRAMES - 1, frame))];
  const png = PNG.sync.read(fs.readFileSync(path.join(dir, f)));

  const box = findBox(png);
  const hookOrEnd = frame <= 108 || frame >= TOTAL_FRAMES - 60;

  let white = 0, w = 0, ok = false;
  if (box) {
    const x0 = box.x + 10, x1 = box.x + FLOAT_W - 4;
    const y0 = box.y + 30, y1 = box.y + box.h - 4;
    for (let y = y0; y <= y1; y++) {
      for (let x = x0; x <= x1; x++) {
        const i = (png.width * y + x) << 2;
        if (isWhite(png.data[i], png.data[i + 1], png.data[i + 2])) white++;
      }
    }
    w = box.h;
    ok = white > 300;
  }
  // 钩子/收尾帧本来就不画图表，找不到标签是正常的 —— 计入 skipped，
  // 不能计入 fail。上一版虽然打印了"(钩子/收尾)"，却仍把 ok=false 累加进
  // fail，导致只要采样帧落在钩子窗口内就必然退出码 1。
  if (!ok && hookOrEnd) skipped++;
  else if (!ok) fail++;

  const inSafe = box
    ? box.x >= SAFE_X0 && box.x + FLOAT_W <= SAFE_X1 && box.y >= SAFE_Y0 && box.y + box.h <= SAFE_Y1
    : false;

  console.log(
    `${String(frame).padStart(5)} ${val.toFixed(1).padStart(9)} ${String(top).padStart(6)}  ` +
    `${box ? `${String(box.x).padStart(4)},${String(box.y).padStart(4)}` : "  缺失 "}` +
    `${box ? `   ${String(w).padStart(3)}   ${String(white).padStart(6)}` : ""}` +
    `    ${box ? (inSafe ? "ok" : "OUT-OF-SAFE") : "FAIL"}${hookOrEnd ? "  (钩子/收尾)" : ""}`,
  );
}

console.log(
  `\n${fail === 0 ? "✓" : "✗"} 浮动读数: ${files.length - skipped}/${files.length} 帧有可见标签` +
    `（其中 ${skipped} 帧为钩子/收尾，本就不显示图表，不计入判定）`,
);
process.exit(fail ? 1 : 0);

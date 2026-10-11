/**
 * v6 版面分带诊断：对抽样帧按 layout 常量分带扫描非装饰像素，
 * 报告每带的内容极值 —— 回答"标头/报价HUD/标题/事件卡有没有互相压、有没有横向溢出"，
 * 以及"BeatOverlay 金色标注线在该帧到底画没画出来"。
 * 用法: node diag_v5.mjs out/frames [更多目录...]
 */
import fs from "fs";
import path from "path";
import { PNG } from "pngjs";
import { AXIS_Y, MAIN_BOT, PY0, SAFE_X0, SAFE_X1, SAFE_Y0, SAFE_Y1 } from "./out/layout.mjs";

// 分带（与 layout.ts v6 纵向预算一致）
const BANDS = [
  { name: "标头行", y0: 200, y1: 279 },
  { name: "报价HUD", y0: 288, y1: 419 },
  { name: "标题", y0: 434, y1: 614 },
  { name: "绘图区", y0: PY0, y1: MAIN_BOT + 8 },
  { name: "时间轴/阶段", y0: AXIS_Y - 4, y1: 1600 },
  { name: "事件卡", y0: 1608, y1: SAFE_Y1 },
];

const DECOR = [
  [10, 17, 40], [14, 23, 48], [20, 31, 61], [28, 42, 74], [22, 64, 124],
];
const near = (r, g, b, c, tol = 16) =>
  Math.abs(r - c[0]) <= tol && Math.abs(g - c[1]) <= tol && Math.abs(b - c[2]) <= tol;
const isGold = (r, g, b) => r > 200 && g > 140 && g < 225 && b > 55 && b < 145;

const dirs = process.argv.slice(2);
if (!dirs.length) dirs.push("out/frames");
const files = dirs.flatMap((d) =>
  fs.readdirSync(d).filter((f) => /^f\d+\.png$/.test(f)).map((f) => path.join(d, f)),
).sort();

let fail = 0;
for (const f of files) {
  const frame = parseInt(path.basename(f).match(/(\d+)/)[1], 10);
  if (frame < 110) {
    // 钩子场（HookScene 不透明期 + 标题未升起）：无图表版面，check_safe 已覆盖
    console.log(`f${String(frame).padStart(4)} --  钩子场，跳过分带`);
    continue;
  }
  const png = PNG.sync.read(fs.readFileSync(f));
  const { width, data } = png;
  const bands = BANDS.map((b) => ({ ...b, minX: 1e9, maxX: -1, n: 0 }));
  let gold = 0, goldMinY = 1e9, goldMaxY = -1;

  for (let y = SAFE_Y0; y <= SAFE_Y1; y++) {
    for (let x = 0; x < width; x++) {
      const i = (width * y + x) << 2;
      const r = data[i], g = data[i + 1], b = data[i + 2];
      if (r + g + b < 120) continue;
      if (DECOR.some((c) => near(r, g, b, c))) continue;
      if (isGold(r, g, b)) {
        gold++;
        if (y < goldMinY) goldMinY = y;
        if (y > goldMaxY) goldMaxY = y;
      }
      const bd = bands.find((b) => y >= b.y0 && y <= b.y1);
      if (bd) {
        bd.n++;
        if (x < bd.minX) bd.minX = x;
        if (x > bd.maxX) bd.maxX = x;
      }
    }
  }

  const probs = [];
  for (const b of bands) {
    if (b.n === 0) {
      // 事件卡在首帧 evFrame 前、淡入当帧、收尾击杀后本就不在场 —— 记注不记过
      if (b.name === "事件卡") continue;
      probs.push(`${b.name} 空`);
      continue;
    }
    if (b.maxX > SAFE_X1) probs.push(`${b.name} 右溢 x${b.maxX}`);
    if (b.minX < SAFE_X0) probs.push(`${b.name} 左溢 x${b.minX}`);
    if ((b.name === "报价HUD" || b.name === "标题") && b.maxX > SAFE_X1 - 22)
      probs.push(`${b.name} 文字逼近右内缘 x${b.maxX} (>${SAFE_X1 - 22})`);
  }

  // BeatOverlay：该帧应显示的最新 beat（kf 线性近似判定即可，仅作提示）
  const beatNote = gold > 50 ? `金色标注 y${goldMinY}..${goldMaxY} (${gold}px)` : gold > 0 ? `金色 ${gold}px（偏少）` : "无金色";
  const ok = probs.length === 0;
  if (!ok) fail++;
  console.log(
    `f${String(frame).padStart(4)} ${ok ? "ok " : "NG "} ${beatNote}` +
    (ok ? "" : "  " + probs.join(" | ")),
  );
  if (ok) {
    for (const b of bands.filter((x) => x.n > 0))
      console.log(`         ${b.name.padEnd(10)} x${b.minX}..${b.maxX}`);
  }
}
console.log(fail ? `\n✗ ${fail} 帧有分带问题` : `\n✓ 全部 ${files.length} 帧分带正常`);
process.exit(fail ? 1 : 0);

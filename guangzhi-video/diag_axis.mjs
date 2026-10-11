/** 调试：打印每帧的 wmax / target / top，确认动态轴为何迟迟不回落 */
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
const NAV = [...block("const NAV").matchAll(/date:\s*"([\d-]+)",\s*close:\s*([\d.]+),\s*wan:\s*([\d.]+)/g)]
  .map((m) => ({ date: m[1], wan: +m[3] }));
const N = NAV.length - 1;

const WIN = 13, LOCK = 0.26, TAIL_KF = 44, TAIL_END = 0.94;
const STEPS = [25, 50, 100, 200, 250, 500, 1000, 2000, 2500];
const HEADROOM = 1.18, DECAY = 0.9965;
const RS = 150, RE = 2640, TF = 2760;
const c01 = (t) => Math.max(0, Math.min(1, t));
const fit = (v) => STEPS.find((s) => s * 4 >= v) ?? STEPS[STEPS.length - 1];

let prev = 0;
console.log("frame   kf    L     curVal   wmax   target  top");
for (let f = 0; f < TF; f++) {
  const reveal = f <= RS ? 0 : f >= RE ? 1 : (f - RS) / (RE - RS);
  const kf = c01(reveal) * N;
  const tailT = c01((kf - TAIL_KF) / (N - TAIL_KF));
  const tailE = tailT * tailT * (3 - 2 * tailT);
  const frac = LOCK + (TAIL_END - LOCK) * tailE;
  const L = kf - WIN * frac;

  const ki = Math.min(Math.floor(kf), N);
  const atEnd = ki >= N;
  const f2 = atEnd ? 0 : kf - ki;
  const curVal = atEnd ? NAV[N].wan : NAV[ki].wan + (NAV[ki + 1].wan - NAV[ki].wan) * f2;

  let wmax = curVal;
  const a = Math.max(0, Math.ceil(L));
  const b = Math.min(N, Math.floor(kf));
  for (let i = a; i <= b; i++) wmax = Math.max(wmax, NAV[i].wan);

  const target = fit(wmax * HEADROOM) * 4;
  const base = prev === 0 ? target : Math.max(target, prev * DECAY);
  const top = fit(base) * 4;
  prev = top;

  if (f % 100 === 0) {
    console.log(
      String(f).padStart(5), kf.toFixed(1).padStart(6), L.toFixed(1).padStart(7),
      curVal.toFixed(1).padStart(9), wmax.toFixed(1).padStart(8),
      String(target).padStart(7), String(top).padStart(6),
    );
  }
}

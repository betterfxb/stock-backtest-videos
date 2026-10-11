/** 从 src/data.ts 直接解析事件节点与阶段，算出需要渲染的帧号 */
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

const evTxt = block("const EVENTS");
const events = [...evTxt.matchAll(/idx:\s*(\d+),[\s\S]*?tag:\s*"([^"]+)",[\s\S]*?value:\s*"([^"]+)"/g)].map((m) => ({
  idx: +m[1], tag: m[2], value: m[3],
}));

const navTxt = block("const NAV");
const nav = [...navTxt.matchAll(/date:\s*"([\d-]+)",\s*close:\s*([\d.]+),\s*wan:\s*([\d.]+)/g)].map((m) => ({
  date: m[1], close: +m[2], wan: +m[3],
}));

// v5.0：出帧时间从配速实现同源取，不再在脚本里复刻线性公式
// （复刻公式在分段配速下会把抽帧点全抽错，校验的就是不存在的帧）。
import { evFrame } from "./out/reveal.mjs";

console.log(`NAV ${nav.length} 个月  ${nav[0].date} ~ ${nav.at(-1).date}`);
console.log(`EVENTS ${events.length} 个\n`);

const frames = new Set([0, 120, 2759]);
console.log("idx  tag          frame   value        nav.wan   一致");
for (const e of events) {
  const f = Math.round(evFrame(e.idx));
  frames.add(f);
  frames.add(Math.max(0, f - 12));
  frames.add(Math.min(2759, f + 12));
  const wan = nav[e.idx].wan;
  const v = parseFloat(e.value);
  const ok = Math.abs(wan - v) < 0.011;
  console.log(
    `${String(e.idx).padStart(3)}  ${e.tag.padEnd(12)} ${String(f).padStart(4)}   ${e.value.padEnd(11)} ${String(wan).padStart(8)}   ${ok ? "ok" : "MISMATCH"}`,
  );
}

// 阶段切换与极值点也抽两帧（极值从数据现取，不写死 32/45/77）
for (const s of [...block("const STAGES").matchAll(/from:\s*(\d+)/g)].map((m) => +m[1])) {
  frames.add(Math.round(evFrame(s)));
}
const minI = nav.reduce((a, p, i) => (p.wan < nav[a].wan ? i : a), 0);
const peakI = nav.reduce((a, p, i) => (p.wan > nav[a].wan ? i : a), 0);
for (const idx of [minI, peakI, nav.length - 1]) frames.add(Math.round(evFrame(idx)));

const uniq = [...frames].filter((f) => f >= 0 && f <= 2759).sort((a, b) => a - b);
console.log(`\n共 ${uniq.length} 帧:`);
console.log(uniq.join(","));
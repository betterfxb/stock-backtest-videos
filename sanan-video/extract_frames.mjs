/** 抽帧：Node 直调 ffmpeg 传参数组，规避 PowerShell 下 select 表达式的引号损坏。
 *  输出命名 f<帧号>.png —— check_readout / diag_v5 只认这个格式。 */
import { execFileSync } from "child_process";
import fs from "fs";

const MP4 = "out/ep014_三安光电_sh600703_2020-2026_ai_v6.mp4";
const DIR = "out/frames";
const FRAMES = [
  0, 120, 138, 150, 162, 228, 240, 252, 371, 383, 395, 461, 473, 485, 559, 605, 617, 629, 719, 731, 743,
  892, 904, 916, 982, 994, 1006, 1297, 1309, 1321, 1584, 1596, 1608, 1784, 1796, 1808, 1874, 1886, 1898,
  2190, 2202, 2214, 2374, 2448, 2460, 2472, 2538, 2550, 2562, 2628, 2640, 2652, 2759,
];

fs.mkdirSync(DIR, { recursive: true });
for (const f of FRAMES) {
  const out = `${DIR}/f${f}.png`;
  execFileSync("ffmpeg", [
    "-y", "-loglevel", "error",
    "-i", MP4,
    "-vf", `select=eq(n\\,${f})`,
    "-vsync", "0",
    "-frames:v", "1",
    out,
  ]);
  const kb = (fs.statSync(out).size / 1024).toFixed(0);
  console.log(`f${f}.png  ${kb}KB`);
}
console.log(`\nextracted ${FRAMES.length} frames -> ${DIR}`);

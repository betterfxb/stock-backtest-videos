/** 诊断：浮动标签到底有没有被画出来，还是被覆盖了 */
import fs from "fs";
import path from "path";
import { PNG } from "pngjs";

const dir = process.argv[2] || "out";
const frames = process.argv.slice(3);
const isPink = (r, g, b) => r > 200 && g > 50 && g < 120 && b > 90 && b < 165;
const isBox = (r, g, b) => r > 25 && r < 70 && g > 8 && g < 40 && b > 18 && b < 55;
const isWhite = (r, g, b) => r > 220 && g > 220 && b > 220;

for (const f of frames) {
  const png = PNG.sync.read(fs.readFileSync(path.join(dir, f)));
  let pink = 0, box = 0, white = 0;
  let minX = 9999, maxX = -1, minY = 9999, maxY = -1;
  for (let y = 780; y < 1300; y++) {
    for (let x = 0; x < 1080; x++) {
      const i = (png.width * y + x) << 2;
      const r = png.data[i], g = png.data[i + 1], b = png.data[i + 2];
      if (isPink(r, g, b)) {
        pink++;
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
      }
      if (isBox(r, g, b)) box++;
      if (isWhite(r, g, b)) white++;
    }
  }
  console.log(
    `${f}  粉边像素=${String(pink).padStart(5)}  盒底=${String(box).padStart(5)}  白字=${String(white).padStart(5)}` +
    (pink ? `  bbox=(${minX},${minY})-(${maxX},${maxY})` : "  标签完全不可见"),
  );
}
import fs from "fs";
import { PNG } from "pngjs";

const f = process.argv[2];
const png = PNG.sync.read(fs.readFileSync(f));
const px = (x, y) => {
  const i = (png.width * y + x) << 2;
  return [png.data[i], png.data[i + 1], png.data[i + 2], png.data[i + 3]];
};

const y = parseInt(process.argv[3] || "797", 10);
console.log(`frame ${f}  row y=${y}`);
console.log("x, rgba:");
for (let x = 0; x <= 90; x += 3) console.log(`  x=${x}  ${px(x, y).join(",")}`);

console.log("\nleftmost non-bg pixel per row, rows 780..830:");
for (let yy = 780; yy <= 830; yy += 5) {
  let lx = -1, c = null;
  for (let x = 0; x < 200; x++) {
    const p = px(x, yy);
    if (p[0] + p[1] + p[2] >= 120) { lx = x; c = p; break; }
  }
  console.log(`  y=${yy}  leftmost=${lx}  rgba=${c ? c.join(",") : "-"}`);
}
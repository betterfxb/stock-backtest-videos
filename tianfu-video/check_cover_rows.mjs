import fs from "fs";
import { PNG } from "pngjs";
// 检查封面文案是否与 data.ts 真实值一致（数字抽像素宽度间接验证易错，
// 这里直接验证"关键行是否有像素"——即文案没被裁掉/换行错位）
const f=process.argv[2];
const png=PNG.sync.read(fs.readFileSync(f));
const px=(x,y)=>{const i=(png.width*y+x)<<2;return [png.data[i],png.data[i+1],png.data[i+2]];};
const ink=(y0,y1)=>{let c=0;for(let y=y0;y<=y1;y++)for(let x=80;x<=880;x++){const[r,g,b]=px(x,y);if(r+g+b>330)c++;}return c;};
const rows=[["期号条",137,170],["副标题",200,260],["巨数",320,470],["大字",556,620],["卡片",700,830],["结论条",1272,1364],["脚注",1392,1423]];
for(const [n,a,b] of rows){const c=ink(a,b);console.log(`  ${n.padEnd(6)} y${a}-${b}  像素${String(c).padStart(6)}  ${c>500?"✓ 有内容":(c>0?"△ 极少":"✗ 空")}`);}

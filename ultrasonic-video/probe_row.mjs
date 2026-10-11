import fs from "fs";
import { PNG } from "pngjs";
const f = process.argv[2];
const png = PNG.sync.read(fs.readFileSync(f));
const px=(x,y)=>{const i=(png.width*y+x)<<2;return [png.data[i],png.data[i+1],png.data[i+2]];};
const row=parseInt(process.argv[3],10);
const runs=[];
let cur=null;
for(let x=0;x<1080;x++){const p=px(x,row);const k=p.join(",");
 if(!cur||cur.k!==k){if(cur)runs.push(cur);cur={x0:x,x1:x,k};}else cur.x1=x;}
if(cur)runs.push(cur);
console.log(`--- ${f} row ${row} ---`);
for(const r of runs) console.log(`  x ${r.x0}..${r.x1}  rgb(${r.k})`);

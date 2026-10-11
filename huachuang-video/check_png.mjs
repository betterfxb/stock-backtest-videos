import fs from "fs";
import { PNG } from "pngjs";
const f=process.argv[2];
const png=PNG.sync.read(fs.readFileSync(f));
const px=(x,y)=>{const i=(png.width*y+x)<<2;return [png.data[i],png.data[i+1],png.data[i+2],png.data[i+3]];};
const W=1080,H=1920;
const SAFE={x0:80,x1:880,y0:130,y1:1440};
const EX=[["brandbar",0,12],["compliance",1850,1920]];
const DECOR=[[9,4,9],[20,10,17],[28,18,24],[34,22,30],[58,36,52],[62,22,32],[24,14,20],[16,8,14]];
const near=(r,g,b,c,t=16)=>Math.abs(r-c[0])<=t&&Math.abs(g-c[1])<=t&&Math.abs(b-c[2])<=t;
let minX=W,maxX=-1,minY=H,maxY=-1;const bad=[];
for(let y=0;y<H;y++){
  const ex=EX.find(([,a,b])=>y>=a&&y<=b);
  for(let x=0;x<W;x++){
    const [r,g,b]=px(x,y);
    if(r+g+b<120)continue;
    if(DECOR.some(c=>near(r,g,b,c)))continue;
    if(ex)continue;
    if(x>maxX){maxX=x;bad.push([x,y,r,g,b]);}
    if(x<minX)minX=x;
    if(y>maxY)maxY=y;
    if(y<minY)minY=y;
  }
}
console.log(f);
console.log("  极值: 左"+minX+" 右"+maxX+" 上"+minY+" 下"+maxY);
const v=[];
if(maxX>SAFE.x1)v.push("右溢"+(maxX-SAFE.x1)+" @"+bad[0]);
if(minX<SAFE.x0)v.push("左溢"+(SAFE.x0-minX));
if(maxY>SAFE.y1)v.push("下溢"+(maxY-SAFE.y1));
if(minY<SAFE.y0)v.push("上溢"+(SAFE.y0-minY));
console.log("  "+(v.length?"FAIL "+v.join(" "):"✓ 安全区内"));

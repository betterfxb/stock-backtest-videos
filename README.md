# 历史回测短视频项目 · 「假如你不小心」

A 股历史回测竖版短视频系列（抖音发布）。每期设定"100 万买入一只标的、持有不动"，用动画曲线还原完整持有期的收益与回撤，主打"收益率 vs 拿得住"的反差叙事。

- 画幅 1080×1920 · 30fps · 2760 帧（≈92s），Remotion + React 渲染
- 数据：腾讯 fqkline 月 K（后复权 hfq，含分红再投，近似总回报）
- 数值全部由脚本现算，画面经过四重像素校验，全绿才交付

## 目录结构

```
.
├── video_analysis/          # 数据管线（全期共用）
│   ├── klines_hfq.jsonl     # 5223 只 A 股 hfq 月K（最终数据源）
│   ├── klines_all.json      # 各期快照（market/code/rows）
│   ├── episodes.py          # UNIVERSE + EPISODES：人工核验的叙事配置（阶段/事件卡/关键节点/钩子文案）
│   └── gen_data_ts.py       # 数值现算引擎：快照 + 叙事 → src/data.ts
├── <name>-video/            # 各期 Remotion 工程（cambricon/huachuang/innolight/naura/…/guangzhi）
│   ├── src/                 # Video.tsx / NavChart.tsx / Cover.tsx / Root.tsx / data.ts / layout.ts / reveal.ts / axis.ts
│   ├── check_safe.mjs / check_readout.mjs / diag_v5.mjs / check_cover_rows.mjs / list_frames.mjs
│   └── out/                 # 构建产物与成片（不进仓库，本地重建）
└── deliverables/
    ├── 00_文档方案/         # 候选池、每期完整内容稿（含发布文案与校验报告）
    └── 02_成片_定稿发布/    # 第XXX期_XXX/：成片 mp4 + 封面 A/B（mp4 不进仓库，见 Release）
```

> 最新一期工程（`guangzhi-video`）即当前模板基线：新一期从它复制。
> `node_modules` 只在任一期保留一份实拷贝，其余用 `mklink /J` 链接（见下）。

## 环境准备

- Node.js（项目内 Remotion 5.x / React 19）、Python 3、ffmpeg
- 任选一期执行 `npm install`，其余期链接过去（Windows 管理员终端）：
  ```powershell
  cmd /c mklink /J <新工程>\node_modules <已有工程>\node_modules
  ```

## 制作新一期（标准七步）

```powershell
# 1. 数据：jsonl 抽目标行 → 追加 klines_all.json（BOM 保留，market 0=深市/1=沪市）
# 2. 叙事：episodes.py 加 UNIVERSE + EPISODES（stages 首尾相接覆盖 0..N；事件正文 ≤50 字）
cd video_analysis
python gen_data_ts.py <code> data_<code>.ts   # 3. 现算并自检（指标/回撤段/YMAX 直接打印核对）
# 4. 建工程：复制最新一期目录（不含 node_modules/out），改 package.json 名，data_<code>.ts 覆盖 src/data.ts
cd ..\<new>-video
npx esbuild src/layout.ts --bundle --format=esm --outfile=out/layout.mjs   # 同理 reveal / axis
npx tsc --noEmit                                                            # 必须 exit 0
node list_frames.mjs                                                        # 5. 抽帧表：事件金额必须全 ok
npx remotion render Stock "out\epXXX_XXX_xx000000_2020-2026_ai_v6.mp4" --overwrite
npx remotion still CoverA out\epXXX_coverA.png --overwrite   # CoverB 同理
# 6. 抽帧（见下）→ check_safe / check_readout / diag_v5 / check_cover_rows + 封面目检，全绿
# 7. 交付：mp4 + 封面进 deliverables/02_成片_定稿发布/第XXX期_XXX/，补 00_文档方案 内容稿，候选池标期号
```

抽帧命名注意：`check_readout` / `diag_v5` 只认 `f<帧号>.png`。PowerShell 下 `ffmpeg -vf select` 引号必坏，
请用 Node 直调（`execFile` 传参，见各期 `extract_frames_*.mjs` 做法）或全量抽取后按名挑选。

## 校验体系（四重，全部按帧号抽样）

| 校验器 | 判据 |
|---|---|
| `check_safe.mjs` | 核心内容 x∈[140,940]、y∈[200,1720]（豁免：顶部金线 y0–12、合规条 y1850–1920） |
| `check_readout.mjs` | 浮动读数蓝框 + 白字可辨（frame 0 钩子帧不计） |
| `diag_v5.mjs` | 标头/HUD/标题/绘图区/时间轴/事件卡六分带无越界 |
| `check_cover_rows.mjs` + 目检 | 封面 7 行全有内容；期号条/副标题无重影、月份/数字与数据层一致 |

## 已交付期次

| 期号 | 标的 | 代码 | 区间 |
|---|---|---|---|
| 第 001 期 | 贵州茅台 | sh600519 | 2020–2026 |
| 第 002 期 | 比亚迪 | sz002594 | 2020–2026 |
| 第 003 期 | 寒武纪 | sh688256 | 2023–2026 |
| 第 004 期 | 新易盛 | sz300502 | 2020–2026 |
| 第 005 期 | 北方华创 | sz002371 | 2020–2026 |
| 第 006 期 | 中际旭创 | sz300308 | 2020–2026 |
| 第 007 期 | 黄金ETF | sh518880 | — |
| 第 008 期 | 超声电子 | sz000823 | 2020–2026 |
| 第 009 期 | 天孚通信 | sz300394 | 2020–2026 |
| 第 010 期 | 源杰科技 | sh688498 | 2022–2026 |
| 第 011 期 | 协创数据 | sz300857 | 2020–2026 |
| 第 012 期 | 罗博特科 | sz300757 | 2020–2026 |
| 第 013 期 | 光智科技 | sz300489 | 2020–2026 |

详细指标、叙事与发布文案见 `deliverables/00_文档方案/第XXX期_*_完整内容稿.md`；
选题顺位见 `deliverables/00_文档方案/A股涨幅榜_候选池_2020-2026.md`。

## 合规声明

- 本系列为**历史数据模拟**，不构成任何投资建议；成片底部合规条逐帧常驻。
- 叙事不涉及荐股、买卖建议与未来走势预测；数据源与复权口径逐片标注。
- 公开数据仅作技术复现与投资者教育用途。

## 注意事项

- **不要用 PowerShell `Set-Content` 改源码文件**（会破坏 UTF-8 中文并合并行）；改代码只用编辑器。
- `ffmpeg -vf select` 不要写在 PowerShell 行内（引号转义必坏），用 Node `execFile`。
- `out/`、`node_modules/`、成片 mp4 不进仓库；成片发布请走 GitHub Releases。

# 正文图 1、2：绘制约定

本轮由用户明确要求制作并接入正文。静态 Python / Matplotlib，矢量 PDF 与 300 dpi PNG；不编译论文。

## 图 1：Feature lifting 的新软件边界

- 问题：与在原仓库内修改代码相比，评测对象如何变化？
- 结论：源仓库是实现证据，产物在新的包边界接受 source-free 行为评测。
- 形式：三栏示意图，完整 source repository → 新 package → source-free evaluation；下方一条紧凑对照说明 repo editing 仍在原项目内评测。
- 证据：main.tex 的 Blinker 公开契约案例与 source-free 协议；不展示隐藏断言，不虚构实际模块调用图。
- 三项公开义务：dispatch、weak-receiver lifetime、namespace identity，穿过新包边界继续作为行为要求。
- 交付尺寸：7.2 × 3.8 英寸。蓝色表示可见输入、绿色表示产物、金色表示评测；标题、框线、箭头和文字提供非颜色区分。
- 输出：figures/fig01_feature_lifting.pdf，output/ 下保留 PDF/PNG；检查 PNG 字体、箭头、边界与内容。

## 图 2：构建与验证

- 问题：200 题如何形成并获得验证依据？
- 结论：任务构建与多种验证活动共同支持 release。
- 形式：上方 construction 带，下方 validation 带。上方连接 selection → pinned source / contract → protected tests / reference → release。下方四个互补模块，避免伪造人工复核与 replay 的精确时间顺序。
- 数字依据：200 tasks、176 repositories、182 snapshots、200 consistency checks、38-task AI repair-scope review、600 reference runs / 200 tasks。
- 人工依据：作者本轮确认约半数任务的人工抽检与 AI 复核，覆盖语义、分类、失败标注；有问题的候选删除。未提供人/AI 分别精确数量、删除清单和逐题 replay 关系。因此图不标“100 human-reviewed”或人工后逐题重跑。
- 下方注明问题候选排除，review 与 replay 是互补证据，不画串行时间轴。
- 交付尺寸：7.2 × 4.0 英寸。相同配色，文字和分区标题保证灰度可读。
- 输出：figures/fig02_construction_validation.pdf，output/ 下保留 PDF/PNG；检查 PNG，核对数字与正文。

## 同步 A/B

A 保持 150 题原始计数，改为 task annotations，说明作者抽检与 AI 辅助复核为 sampled review，不再声称没有进行任何人工语义审核。
B 保留 900 条结果和原始阶段 key，只把显示名 Public/Hidden 改为 Basic/Extended。图例和正文必须一致。

# Fig. 1：从通用流程图改为具体任务示意图

这一版由 Matplotlib 绘制，输出 SVG、PDF 和 PNG，没有替换 main.tex 或正式图片，也没有运行实验。

## 设计逻辑

- 顶部用两条平行流程说明 repository editing 与 feature lifting 的输入、产物和评测环境差异。
- 左侧展示真实 Blinker 源文件及选取的符号，说明完整实现是可供检索的证据；下方 A/B/C 是公开契约的代表性行为要求。
- 中间展示新包的公开 API、允许的实现策略和禁止的运行时依赖。不强制内部文件布局，也不把参考实现当作唯一答案。
- 右侧用 A/B/C 对应的具体场景解释行为保持。场景是根据公开契约写的示意，不是实验结果，也不是展示隐藏测试代码。
- 橙色箭头穿过运行时边界，说明提交包进入源仓库不可用的评测环境。
- 底部用一个完整的逻辑与表达 functional pass，并明确哪些输入对 agent 可见。

RRES / Copy 没有放入这个版本。第一张图集中定义任务与成功条件，产物特征分析由正文指标和结果图承担。

## 内容依据

- benchmark/tasks/blinker__signal_registry_core__001/TASK.md
- benchmark/tasks/blinker__signal_registry_core__001/repo/src/blinker/base.py
- benchmark/tasks/blinker__signal_registry_core__001/repo/src/blinker/_utilities.py
- benchmark/tasks/blinker__signal_registry_core__001/repo/src/blinker/_saferef.py
- docs/paper/main.tex，任务定义与运行示例

图中只选取三类行为，任务还包含 ANY、responses、connected_to、disconnect 等要求。图中 API 保留实际要求的 Signal、Namespace、ANY。

## 建议英文 caption

Feature lifting from intact source evidence to source-free behavior. Unlike repository editing, the deliverable is a new package evaluated without the source repository. The Blinker example connects selected source symbols and public contract obligations (A–C) to illustrative behavioral checks at the new boundary. Agents may extract, adapt, or reimplement code, but the submitted package cannot depend on the original repository at runtime. Functional success requires all four evaluation gates. Source symbols and behavioral clauses are illustrative rather than exhaustive.

## 编辑和输出

脚本：docs/paper/figures/scripts/draw_fig1_evidence.py

- fig1_evidence_v2.svg：可编辑矢量文件，文字保留为文本。
- fig1_evidence_v2.pdf：矢量预览。
- fig1_evidence_v2.png：对话预览与 PPT 复刻底图。

画布为 12 × 6.6 英寸，拟用于双栏通栏。缩至 7.2 英寸宽时正文约 6.4–7.2 pt，最终版需结合论文实际版面判断是否进一步删减辅助说明、增大字号。本轮仅渲染图片，不编译论文。

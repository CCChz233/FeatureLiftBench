# Python-150 论文范围修订

2026-09-13，按作者确认，正式论文使用原有 Python-150 集合。本文范围为 150 题、126 个仓库、132 个快照，六配置共 900 条结果。没有按逐题成败重新挑选任务，没有新增评测，也没有修改题包或原始运行。

## 修改

- `main.tex` 的摘要、贡献、任务构建与验证、组成统计、实验范围、结论与附录统一为 150 题；删除额外 50 题的扩展评测及交叉引用。
- Fig. 1/2 另存 `_python150.png` 版本，保留旧图。Fig. 3 两侧均使用 150 题；Direct / Adapted / Composite 为 56 / 76 / 18。Composite 示例改为集合内的 Pyramid action registry。
- 按 150 个任务 ID 从历史逐条记录核实：每题 3 次参考执行，共 450/450 次通过，每题指纹稳定。修复记录覆盖本文 24 题，其中 4 题追加裁决；历史全量记录仍保持 38/6。
- `paper_sources.json` 增加固定成员文件 `python150_membership.json`，读取历史 freeze 时显式筛选；表格与图示生成脚本采用同一集合。
- `chapter2_evidence.py` 生成新的 `chapter2_python150_task_inventory.json` 和 `chapter2_python150_evidence.json`。原 200 题派生记录保留。
- 五个已生成实证表、结构表及原有消融实验假设占位与修改前逐块一致。通过数仍为 Pro 115、Flash 108、Luna 102、GLM 68、Qwen 63、OSS 36。

## 验证与产物

运行了 `chapter2_evidence.py`、`scripts/paper.py tables`、`figures` 和 `package`（内含 `check`）。任务身份、900 条结果与配置、表格数值、450 条参考执行成员和图示分母核对通过。Fig. 4/5 内容未改，恢复原 PDF 字节，避免时间戳变动。

使用 TeX Live 2024 的 `latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex` 编译为 26 页。最终日志无未解析引用和 Overfull box；BibTeX 首轮仍有原文献字段缺省提示。已渲染检查第 1、2、6、7、8、21、22、23、25、26 页以及三张修改图。

- LaTeX：`docs/paper/main.tex`
- PDF：`docs/paper/build/main.pdf`
- Overleaf：`docs/paper/featureliftbench_overleaf.zip`，10 个文件，逐项验证与当前文件一致。
- 核对记录：`writing/python150_scope_validation.json`
- 修改前快照：`docs/archive/snapshots/paper_python150_scope_20260913/`

原有 source-ablation 假设数字仍明确标记为 **HYPOTHETICAL PLACEHOLDER—NOT EXPERIMENTAL RESULTS**；本次没有把它们当作实测结果。作者审核细节和 reference 构建者身份等原有 TODO 保留。该文件仍是工作稿。

## 图像编辑记录

使用内置 image generation 编辑工具；两张输入图均先查看。只要求更新数字并保留其他文字、结构、颜色、图标和比例。新图已逐项目视核对并写入项目，原图没有覆盖。

Fig. 1 提示词：

> Use case: text-localization. Edit target is attached academic paper diagram. Change ONLY bottom footer text '200 tasks · 176 repositories · 182 source snapshots' to '150 tasks · 126 repositories · 132 source snapshots'. Preserve all other text, diagram elements, layout, typography, colors and aspect ratio exactly.

Fig. 2 提示词：

> Use case: text-localization. Edit target is attached academic paper diagram. Change ONLY six numeric labels: '200 task packages' to '150 task packages'; 'All 200 retained tasks' to 'All 150 retained tasks'; '600/600 passing runs' to '450/450 passing runs'; '200 Python tasks' to '150 Python tasks'; '176 source repositories' to '126 source repositories'; '182 pinned snapshots' to '132 pinned snapshots'. Preserve all other text, layout, typography, icons, diagram elements, colors and aspect ratio exactly.

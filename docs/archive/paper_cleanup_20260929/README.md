# 2026-09-29 论文目录清理归档

> **Status: archived · Historical paper record**

本目录保存从当前论文工作区移出的历史文件，**不是**现行论文或实验输入。逐项来源、去向及移动前/当前 SHA-256 见 [MOVED_FILES.json](MOVED_FILES.json)。正式论文及其 12 个引用图片仍在 [docs/paper](../../paper/README.md)；现行数据路径仍由 [paper_sources.json](../../paper-workbench/paper_sources.json) 指定。

- `unused_paper_figures/`：正文未引用的 4 个旧图片。
- `workbench_figures/`：旧版图、备选图及其设计材料。
- `workbench_plans/`：早期工作流、计划与同步记录，旧编号和旧路径不代表当前正文。
- `package_snapshots/`：旧的论文 ZIP 快照；本地旧 PDF 已移至 `exports/archive/paper_pdf_snapshots_20260929/`（该目录被 Git 忽略，不随仓库发布）。
- 本地绘图预览与 TeX 编译缓存分别移至 `exports/archive/paper_figure_previews_20260929/` 和 `exports/archive/paper_build_cache_20260929/`；需要时可以重新生成。
- 原工作区的重复图号符号链接仅记录在 `MOVED_FILES.json`，目标正式资产仍在 `docs/paper/figures/`。

`docs/paper-workbench/writing/archive/notes_20260929/` 保存旧写作修订记录；`figures/scripts/legacy/` 保存旧绘图和预览脚本。历史文档中的相对链接可能指向迁移前布局，复现当前论文请从正式 README 进入。

# FeatureLiftBench 论文工作区

> **Status: current · Last verified: 2026-09-16**

新版正文来自用户提供的 FSE.zip。入口：[main.tex](main.tex) · [项目地图](../PROJECT_MAP.md) · [本次同步记录](FSE_SYNC_20260914.md)。

当前论文包含 150 个 Python 任务、126 个仓库、132 个快照；六配置各 150 题，共 900 条主比较结果。另有三配置 × 40 题 × 两臂的 240 条源码消融结果。当前正文七张图、七张表，引用九个图形文件；没有附录。

## 写作与修改

- 论述与文献：[main.tex](main.tex)、[references.bib](references.bib)。不运行历史章节组装器。
- 输入、模型顺序、图片打包清单：[paper_sources.json](paper_sources.json)。
- 表格布局：[writing/templates/](writing/templates/README.md)；数值从保留记录计算，模板修改不会被数值更新覆盖。
- 正式图形资产位于 [figures/](figures/README.md) 根目录；绘图源码在 [figures/scripts/](figures/scripts/README.md)。旧文件名已归档，不进 Overleaf 包。
- Fig.1–Fig.3 锁定不动；原结构 Fig.4 删除，Table 2 保留；footprint 使用柱状图。
- 运行记录与题包：[PAPER_FOLDERS.md](PAPER_FOLDERS.md)。

从项目根目录执行：

```bash
python -B scripts/paper.py check
python -B scripts/paper.py tables
python -B docs/paper/figures/scripts/redraw_figures.py --output-dir /tmp/flb-figures-preview
python -B scripts/paper.py package
```

`check` 只读核对，`tables` 更新生成区域，预览绘图不替换正式图片，`package` 检查后输出 [Overleaf 压缩包](featureliftbench_overleaf.zip)。完整步骤见 [WORKFLOW.md](WORKFLOW.md)。

## 当前证据边界

主比较逐题结果完整，但本地仅有 307/900 个可核验原始运行 profile。`python -B scripts/paper.py audit` 要求 900 个全部可用，当前会明确报告缺失并失败。普通 `check` 通过不能代替完整原始记录审计。

Luna / GLM 的 Token 总量按作者确认值写入 Table 1。Pro 的 Contract-Only 恢复结果为 7/40，通过恢复后仍有 12 次长上下文执行未交付；原因与口径在正文说明。源码暴露分析的 241/303（79.5%）仅代表工具成功返回入口关联文件内容，不证明完整定位或理解。

当前使用 `acmsmall,screen,review,anonymous`，未修改 `acmart.cls`。图 caption 在下、表 caption 在上；本轮未编译或验证最终分页。

辅助入口：[写作证据](writing/README.md) · [图形工作区](figures/README.md) · [大纲与历史论证](PAPER_OUTLINE.md) · [方法与结果修订记录](writing/METHODS_RESULTS_REVISION_20260912.md)。

最新分工及图表编号见 [Results 视觉证据计划](RESULTS_VISUAL_PLAN.md) 顶部最终决定；历史预览不进入 Overleaf 包。

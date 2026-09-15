# 当前论文绘图源码

> **Status: current · Updated: 2026-09-15**

| 当前图号 | 独立源码 | LaTeX 资产 | 说明 |
| --- | --- | --- | --- |
| Fig. 1 | [legacy/fig1_motivation.py](legacy/fig1_motivation.py) | `fig1.png` | 仅历史设计；当前定稿 PNG 无精确 renderer |
| Fig. 2 | [legacy/fig2_construction.py](legacy/fig2_construction.py) | `fig2.png` | 仅历史设计；保留现有 PNG |
| Fig. 3 | [fig3_composition.py](fig3_composition.py) | `fig3a_families.pdf`、`fig3b_entanglement.pdf` | 组成双面板 |
| Fig. 4（新增） | [fig4_structure.py](fig4_structure.py) | `fig4_structure.pdf` | 六配置 × 三种 lift type 竖向分组柱状图 |
| Fig. 5 | [fig4_functional_results.py](fig4_functional_results.py) | `fig4.pdf` | 失败阶段图；沿用旧文件名，图号由 LaTeX 决定 |
| Fig. 6 | [fig5_source_ablation.py](fig5_source_ablation.py) | `fig5a_pass_rate.pdf`、`fig5b_paired_gain.pdf` | 源码消融；保留导入 PDF |
| Fig. 7（新增） | [fig7_matched_footprint.py](fig7_matched_footprint.py) | `fig7_matched_footprint.pdf` | 六配置 task-adjusted forest plot；115 题 / 485 成功产物 |

## 单独重画新增图

从项目根目录运行：

```bash
python -B docs/paper/figures/scripts/fig4_structure.py --output-dir /tmp/flb-structure
python -B docs/paper/figures/scripts/fig7_matched_footprint.py --output-dir /tmp/flb-matched
```

指定输出目录时，PDF/PNG 和 `data/` 都在该目录，不修改正式图。去掉 `--output-dir` 会写入 `figures/output/` 并同步同名 PDF 到论文使用的 `figures/` 根目录。

只重画这两张图：

```bash
python -B docs/paper/figures/scripts/redraw_figures.py --only structure footprint --output-dir /tmp/flb-new-results
```

批量入口支持 `coverage`（Fig. 3）、`structure`（Fig. 4）、`functional`（Fig. 5）、`ablation`（Fig. 6）、`footprint`（Fig. 7）。默认全画五张统计图，输出七组 PDF/PNG；不调用 Fig. 1/2 历史 renderer。

## 数据与历史版本

Fig. 4 通过 [results_visuals.py](../../writing/results_visuals.py) 读取固定 150 题的结果。

Fig. 7 的独立统计实现是 [fig7_adjusted_analysis.py](fig7_adjusted_analysis.py)：读取正式 main-results CSV 的 900 条结果，保留至少两配置成功的 115 题 / 485 个成功产物。RRES 拟合 `log2(RRES)`，Copy 拟合保存的 `copied_fraction`；均含 task fixed effects，配置效应 sum-to-zero。图上报告 `2**beta` / `100*beta` pp。

主 artifact 等权 task bootstrap、`1/k_t` task 等权 bootstrap、repository bootstrap 各保留 10,000 次，逐次检查 comparison graph 连通并记录断开重抽次数。默认 seed 为 20260915 / 20260915 / 20260916。Task 内 outcome 和 configuration indicators 同时去均值，并用完整 task-dummy OLS/WLS 独立核对系数。

推荐生成预览、核查几何并导出全部统计：

```bash
python -B docs/paper/figures/scripts/preview_results.py --only footprint --output-dir docs/paper/figures/output/fig7_adjusted_preview
```

只运行分析，不绘图：

```bash
python -B docs/paper/figures/scripts/fig7_adjusted_analysis.py --output-dir /tmp/flb-adjusted-data --replicates 10000 --seed 20260915
```

预览目录的 `data/` 包含：

- `fig7_adjusted_analysis.json`：样本、三套结果、检查、逐条输入和来源 SHA256。
- `fig7_bootstrap_coefficients.npz`：三套 10,000 × 6 × 2 coefficient draws（log2 RRES / Copy fraction）。
- `table5_adjusted.csv`：新版主表六行精确值；另有两份稳健性 CSV。
- `fig7_adjusted_results.md`：可读的三套区间和验证记录。

置信区间为 pointwise percentile interval；基线是配置效应 sum-to-zero center，不是 Pro 或 raw median。此分析仅描述成功产物；不能外推失败任务的 footprint，也不构成质量排名。

**迁移状态：** 保留历史图片文件名 `fig7_matched_footprint`，但代码已改为新版 forest plot。正式 PDF、LaTeX 的 RQ4/caption/Table 5/Threats、`writing/results_tables.py` 尚未迁移；旧生成器仍会生成 Pro–Luna 表，本轮不要用它更新 Table 5。

[fig7_paired_footprint.py](fig7_paired_footprint.py) 仍是旧版多配置对照图，不参与当前默认批量入口。旧 `fig6.pdf` 分类附录图及旧 `fig7.pdf` 不被当前正文引用。

当前 Fig. 6 的导入 PDF 使用连接点图，本地 `fig5_source_ablation.py` 使用分组横条；数据一致但不能逐像素复现。此次未替换这些现有资产。

运行依赖为 NumPy、Matplotlib、SciPy。本轮核验版本：NumPy 1.26.4、Matplotlib 3.9.2、SciPy 1.13.1。共享导出/样式在 `figure_common.py`、`paper_style.py`，旧数据接口在 `redraw_data.py`、`figure_data.py`。

实施和检查见 [Results 计划](../../RESULTS_VISUAL_PLAN.md)。不自动编译 LaTeX。

## 图内文字规范（最新）

图内只保留面板标题、坐标轴/必要节点名、必要基线、数据和极简图例。样本汇总、CI 定义、基线解释、读图说明移到 caption。全图审查和逐图 caption 草稿见 [FIGURE_TEXT_AUDIT.md](FIGURE_TEXT_AUDIT.md)。

最新预览位于 `../output/text_cleanup_preview/`。Fig. 7 当前为用户选定的零起点竖向柱状图，左轴线性倍率、右轴 pp；统计分析不变。Fig. 1/2 与保留附录资产仅检查并列出文字迁移项，原始图片保留。上文 forest plot 是较早的视觉方案，已由当前柱状版替代。

## 正文同步完成（2026-09-15）

`main.tex` 和 Table 5 生成器现已使用六配置 task-adjusted 分析；正式 Fig. 4 / Fig. 7 PDF 已从 `text_cleanup_preview/` 同步。较早章节中的“尚未迁移”是历史状态，由本条替代。本次只完成源码、图片同步和静态核查，未编译论文。

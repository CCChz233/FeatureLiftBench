# Results 视觉规范

> **Status: locked · 2026-09-15** · 先把清单看清，再决定要不要重画。

本文只做两件事：**分清「论文里已经有的」和「本轮计划新增的」**，以及锁住新增项怎么画、怎么列表。  
不再讨论第 8 张图或第 7 张表。不编译 LaTeX。不预填 Pro 重跑。

**最新图内文字原则（2026-09-15）。** 图内仅保留面板标题、坐标轴/必要节点标签、必要基线、数据、极简图例。样本总数、CI 定义、基线解释和读图说明移至 caption 或正文。逐图检查及 caption 草稿见 [FIGURE_TEXT_AUDIT.md](figures/scripts/FIGURE_TEXT_AUDIT.md)。Fig. 7 视觉已由 forest plot 改为用户保留的零起点竖向柱图（左轴线性倍率）；本轮再移除首尾说明，统计方案不变。下方较早的 forest plot 布局记录由本条替代。

印刷图号由 LaTeX 按出现顺序编排；**文件名可以保留旧数字**（例如失败阶段图的文件仍叫 `fig4.pdf`）。

---

## 1. 当前论文里已经有的（继承资产）

这些在 Results 视觉扩展**之前**就在正文里。本轮**不是**新图/新表，默认**不要重画、不要换文件名**。

### 已有图（5 个 figure 环境，7 个图片文件）

| 现在的印刷号 | 作用 | 正文引用的文件 | LaTeX label | 说明 |
| --- | --- | --- | --- | --- |
| Fig. 1 | 任务设定 / feature lifting | `figures/fig1.png` | `fig:pipeline` | AI 编辑 PNG；`scripts/legacy/` 里的代码**不等于**这张定稿 |
| Fig. 2 | 构建与验证 | `figures/fig2.png` | `fig:construction` | 同上 |
| Fig. 3 | 150 题组成 | `figures/fig3a_families.pdf` + `figures/fig3b_entanglement.pdf` | `fig:coverage` | 双面板；已有 `fig3_composition.py` |
| Fig. 5 | 首败阶段 / 失败边界 | `figures/fig4.pdf` | `fig:failures` | **文件名仍是 fig4**；插入新 Fig. 4 之后印刷号变成 5 |
| Fig. 6 | 配对源码消融 | `figures/fig5a_pass_rate.pdf` + `figures/fig5b_paired_gain.pdf` | `fig:source-evidence` | **文件名仍是 fig5a/fig5b**；印刷号变成 6 |

### 已有表（3 张）

| 现在的印刷号 | 作用 | LaTeX label | 本轮是否改内容 |
| --- | --- | --- | --- |
| Table 1 | 150 题 × 6 配置总结果 | `tab:main` | 不改结构 |
| Table 3 | 按结局的源码暴露 | `tab:source-exposure` | **只改列**：补 `Runs`；确认读取仍用 \(n/N\) (%) |
| Table 6 | Related Work 任务界面 | `tab:task-comparison` | 不改 |

这 5 图 + 3 表就是「论文里已经有的」。Fig. 5 / Fig. 6 看起来像新编号，只是因为中间**插入**了新增的 Fig. 4。

---

## 2. 计划新增的（Results 扩展）

这些是本轮要加进 Results 的，用来补结构、配对消融统计、配对 footprint。  
**不是**去替换上一节那些图。

### 新增图（2 个 figure 环境，2 个文件）

| 印刷号 | 作用 | 正文引用的文件 | LaTeX label | 一句话 |
| --- | --- | --- | --- | --- |
| Fig. 4 | lift type 通过率格局 | `figures/fig4_structure.pdf` | `fig:structure-capability` | 六配置 × Direct/Adapted/Composite 竖向分组柱状图 |
| Fig. 7 | 同题成功产物的 footprint | `figures/fig7_matched_footprint.pdf` | `fig:matched-footprint` | 六配置 task-adjusted forest plot；115 tasks / 485 artifacts |

### 新增表（3 张）

| 印刷号 | 作用 | LaTeX label | 一句话 |
| --- | --- | --- | --- |
| Table 2 | 结构通过率（精确百分数） | `tab:structure` | 三种 lift type + 四类重叠 mechanism |
| Table 4 | 配对消融的不一致对与检验 | `tab:paired-ablation` | Full-only / Contract-only 分列，加 \(\Delta\) 与 95% CI |
| Table 5 | 六配置调整后 footprint 统计 | `tab:matched-footprint` | Included success n；调整后 RRES ratio / Copy pp 及 95% CI |

### 对已有表的唯一修订

| 印刷号 | 改什么 | 不改什么 |
| --- | --- | --- |
| Table 3 | 增加 `Runs` 列；脚注写明 median step 只在 confirmed-read runs 上算 | 不改结局分组，不另画一张暴露图 |

---

## 3. 一张对照表（避免文件名和印刷号混在一起）

| 印刷号 | 来源 | 文件 | 代码应放在 |
| --- | --- | --- | --- |
| Fig. 1 | **已有** | `fig1.png` | 尚未有能复现定稿的正式脚本 |
| Fig. 2 | **已有** | `fig2.png` | 同上 |
| Fig. 3 | **已有** | `fig3a_families.pdf`、`fig3b_entanglement.pdf` | `scripts/fig3_composition.py` |
| Table 1 | **已有** | 生成表 | `writing/templates/main_table.tex` |
| **Fig. 4** | **新增** | `fig4_structure.pdf` | `scripts/fig4_structure.py` |
| Table 2 | **新增** | 生成表 | `writing/results_tables.py` |
| Fig. 5 | **已有**（旧 Fig. 4） | `fig4.pdf` | `scripts/fig4_functional_results.py`（有脚本，但**不要覆盖**现用 PDF，除非另作决定） |
| Table 3 | **已有**，只加列 | 生成表 | `writing/templates/source_exposure_table.tex` |
| Fig. 6 | **已有**（旧 Fig. 5） | `fig5a_pass_rate.pdf`、`fig5b_paired_gain.pdf` | `scripts/fig5_source_ablation.py`（本地脚本与现用 PDF 不完全一致，**不要覆盖**现用 PDF，除非另作决定） |
| Table 4 | **新增** | 生成表 | `writing/results_tables.py` |
| **Fig. 7** | **新增** | `fig7_matched_footprint.pdf` | `scripts/fig7_matched_footprint.py` |
| Table 5 | **新增** | 生成表 | `writing/results_tables.py` |
| Table 6 | **已有** | 手工表 | Related Work |

**不要当成正文图的文件：** `fig6.pdf`、`fig7.pdf`、`scripts/fig7_paired_footprint.py`（旧多配置对照）。

扩展完成后正文是 **7 图、6 表**（9 个图片文件）。其中 5 图 + 3 表是继承，2 图 + 3 表是新增，Table 3 是已有表改列。

---

## 4. 图文分工（只约束 Results，不动 Fig. 1–3）

- **已有 Fig. 5** 看 failure boundary。
- **已有 Fig. 6** 看 intervention effect。
- **新增 Fig. 4** 看 task-structure pattern。
- **新增 Fig. 7** 看六配置成功产物的 task-adjusted footprint profiles。
- Table 2–5 分别给 exact structure、exposure、paired ablation、task-adjusted footprint。同一论点不画第二张同类图。

共享样式（新增统计图）：画布宽 7.2 in；正文字 `#202B33`；配置顺序与 Table 1 相同（Pro, Flash, Luna, GLM, Qwen, OSS）。

**RQ4 已锁定（2026-09-15）。** 采用六配置、success-conditional、task fixed effects 分析。旧 Pro–Luna scatter / Wilcoxon Table 5 不再作为主结果；不退回六模型共同成功集。保留历史文件名和 label；2026-09-15 已将六配置分析同步到 LaTeX 统计方法、RQ4、Fig. 7 caption / Description、Table 5 和 Threats。
---

## 5. 新增 Fig. 4 — Performance by lift type

**形式（按用户最终选择）。** 竖向分组柱状图，每个配置三根柱。

- 横轴：Pro / Flash / Luna / GLM / Qwen / OSS，与 Table 1 顺序一致。
- 纵轴：Functional pass rate (%)，固定 0–100，所有柱从 0 开始，不堆叠。
- 画布约 7.2 × 3.35 in；无大块底纹，不标逐柱数值。
- Direct 蓝 `#0072B2` / Adapted 橙 `#E69F00` / Composite 绿 `#009E73`。
- 顶部图例写分母 56 / 76 / 18；每格一次保留结果，不画误差条。
- 精确百分数和四类重叠机制保留在 Table 2；不解释为因果难度。

---

## 6. 新增 Fig. 7 — Task-adjusted artifact footprint

**科学问题。** Among successful artifacts that admit within-task comparison, do configurations exhibit different implementation footprints after accounting for task-level variation?

**正式样本。** 只保留至少两个配置成功的任务：115 tasks / 485 successful artifacts / 97 repositories。
进入分析的配置样本数为 113 / 107 / 99 / 68 / 63 / 35；仅排除 7 个 singleton successes。
六模型共同成功的 17 题不作为主样本。纳入任务的 lift types 为 Direct 52、Adapted 55、Composite 8。

**主模型与 estimand（锁定）。**

\[
\log_2(\mathrm{RRES}_{t,m})=\alpha_t+\beta_m+\epsilon_{t,m},\qquad \sum_m\beta_m=0.
\]

图报告 \(2^{\beta_m}\)，名称 **task-adjusted RRES ratio**。

\[
\mathrm{Copy}_{t,m}=\alpha_t+\beta_m+\epsilon_{t,m},\qquad \sum_m\beta_m=0.
\]

Copy 使用保存的 `copied_fraction`，图报告 \(100\beta_m\) percentage points。
`1×` / `0 pp` 的解释统一为 **the sum-to-zero center of configuration effects**。
不称为共同任务平均 RRES、adjusted median 或相对 Pro 的差异。
主 OLS 每个 successful artifact 等权；同时对 outcome 和 configuration indicators 做 within-task 去均值，不能只减 outcome 的任务均值。

**三套分析。**

1. 主分析：task cluster bootstrap，整题携全部成功配置重采样，每次重新拟合、sum-center。
2. Task-equal-weight：每条观测权重 \(1/k_t\)，每道任务总权重相同；task bootstrap。
3. Repository bootstrap：同仓库全部纳入任务一起重采样；保持主模型的 artifact 等权。

每套保留 10,000 个有效 replicate；主分析和 task 等权 seed = 20260915，repository seed = 20260916。
每次检查六配置 comparison graph 连通；断开则重抽并记录拒绝数，设置最大尝试次数防止无限重抽。
95% CI 为 coefficient 上 2.5% / 97.5% percentile，再转换为 ratio 或 pp；是 pointwise interval，不是同时置信带，也不表示重复运行方差。
bootstrap 重复抽到的 cluster 按 multiplicity 计入，等价于复制整题并给每个副本单独的 task fixed effect。

**图形。** 两面板 forest plot，六行配置，顺序与 Fig. 4 / Table 1 一致：Pro / Flash / Luna / GLM / Qwen / OSS。

- (a) **Task-adjusted RRES ratio**：点 + 主 task-bootstrap 95% CI；log2 坐标，实际预览刻度 0.5× / 1× / 2×，中心虚线 1×。范围覆盖全部 CI；无需为 4× 空刻度扩大图。
- (b) **Task-adjusted Copy**：点 + 同一 bootstrap 的 95% CI；横轴 pp，中心虚线 0。
- 单一蓝色，不用颜色编码模型排名或“好坏”。纳入数放 Table 5，图顶部标总体样本。
- 画布约 7.2 × 3.5 in。先输出 `figures/output/fig7_adjusted_preview/`，不覆盖正文 PDF。

**解释边界（RQ4 / Threats 已同步）。**

> The analysis characterizes successful artifacts only and does not extrapolate footprint behavior to tasks on which a configuration fails.

固定效应吸收共同的 task-level variation，但加性系数仍是异质任务差异的概括；不消除 success selection，不解释为因果 effect。
两个配置各自 CI 是否重叠不能当作它们之间的检验；较小或较少重合不等于更好。

**已完成的稳健性结果。** 三套各 10,000 次有效抽样，断开拒绝次数均为 0。
Task 等权后六配置两个指标的点估计方向均保持；RRES ratio 最大相对变化 4.71%，Copy 最大变化 0.772 pp。
Copy 点估计次序保持；Luna / OSS 的 RRES 次序互换，因此不声称完整模型排序稳定。
Qwen Copy 在三套分析中 CI 均跨 0。推荐表述 **successful configurations exhibit distinct task-adjusted footprint profiles**，不写每两配置都显著不同。
数值与区间详见 `figures/output/fig7_adjusted_preview/data/fig7_adjusted_results.md`。

---

## 7. 新增 Table 2 — Performance by task structure

`tab:structure`。7 行 × 6 配置。lift type 互斥；mechanism 重叠。

| 列 | 内容 | 格式 |
| --- | --- | --- |
| Category | Direct, Adapted, Composite；空行后四类 mechanism | 左对齐 |
| \(n\) | 56, 76, 18, 139, 127, 71, 49 | 整数 |
| Pro … OSS | 该行分母下的通过率 | 一位小数，单位在表题 (%) |

配置表头用短名，脚注指向 Table 1 全称。

**脚注（锁定）。** Lift types partition the 150 tasks; the four mechanism groups overlap. Every cell uses the row denominator \(n\). These comparisons are descriptive and do not isolate causal difficulty effects. The Composite group contains 18 tasks, so one task changes its rate by 5.6 percentage points.

---

## 8. 已有 Table 3 — Source exposure by outcome（只加列）

`tab:source-exposure`。四行，按最终结局。这是**已有表**，不是新表。

| 列 | 内容 | 格式 |
| --- | --- | --- |
| Outcome | Pass; Behavioral-first; Delivery/build; Isolation-first | 左对齐 |
| Runs | 该组运行数 | 492 / 303 / 101 / 4 |
| Confirmed read | 确认读取 / 该组运行 | `363/492 (73.8)`；Behavioral-first 加粗 `241/303 (79.5)` |
| Median first-read step | 仅在确认读取的运行上 | 5；Isolation-first 为 10.5 |

相对原表：拆出 **Runs** 列；确认读取仍用 \(n/N\) (%)。

**脚注（锁定）。** Confirmed reads require returned content matching a statically mapped source file. Steps are computed among confirmed reads; search snippets are excluded. A confirmed read is not complete localization or understanding, and this table does not estimate a causal effect of source access.

---

## 9. 新增 Table 4 — Paired source-evidence ablation

`tab:paired-ablation`。三行：Luna, Pro, Qwen。重点是不一致对。图（已有 Fig. 6）给人看区间，这张表给人查数。

| 列 | 内容 | 格式 |
| --- | --- | --- |
| Configuration | 全称；Pro 加 \(\dagger\) | 左对齐 |
| Full pass | Full Source 通过 | `23/40` |
| Contract pass | Contract Only 通过 | `9/40` |
| Full-only | 仅 Full 通过的题数 | 17 / 20 / 12 |
| Contract-only | 仅 Contract 通过的题数 | 3 / 1 / 1 |
| \(\Delta\) (pp) | Full−Contract，百分点 | 35.0 / 47.5 / 27.5 |
| 95% CI | 既有 paired task-bootstrap 百分位区间 | `[15.0, 55.0]` |
| \(p_{\mathrm{Holm}}\) | 三配置 McNemar 的 Holm | 科学计数 |

Full-only 与 Contract-only **分列**，不要再合成 `17 / 3`。CI 与已有 Fig. 6b 同一组 100,000 次 paired task-bootstrap。

**脚注（锁定）。** Missing submissions remain failures. Intervals describe paired task variation, not repeated-run variance. \(\dagger\): Pro has 18 Contract-only missing submissions with recorded LLM timeouts; its 40-task contrast includes those interruptions and is not interpreted as a clean reconstruction effect. After any Pro rerun, replace the full three-configuration record and recompute the Holm family; do not splice successful cells into the current table. 若整组 Pro ablation 重跑成功，\(\dagger\) 不再表示“结果有问题”，只说明 the complete Pro ablation family was rerun after a provider-side interruption, and all reported Pro statistics derive from that complete rerun；旧 timeout run 不混入最终统计。

---

## 10. 新增 Table 5 — Task-adjusted artifact footprint

`tab:matched-footprint`（已同步正文，保留 label）。六行配置，不再使用旧 Pro–Luna 主表。

| 列 | 内容 | 格式 |
| --- | --- | --- |
| Configuration | Pro / Flash / Luna / GLM / Qwen / OSS | 与 Table 1 顺序一致 |
| Included success n | 113 / 107 / 99 / 68 / 63 / 35 | 实际进入调整分析的观测数 |
| Adjusted RRES ratio [95% CI] | \(2^{\beta_m}\) 及主 task-bootstrap 区间 | 三位小数 |
| Adjusted Copy, pp [95% CI] | \(100\beta_m\) 及主 task-bootstrap 区间 | 带符号两位小数 |

原始 marginal median 已在 Table 1，不重复。主表不沿用旧 Wilcoxon / Holm / rank-biserial。
精确数据来自 `figures/scripts/fig7_adjusted_analysis.py`。`writing/results_tables.py` 已迁移，直接复用同一分析；主文 Table 5 已替换为六配置表。独立 LaTeX 片段见 `writing/final_tables/table5_adjusted_footprint.tex`。

**脚注口径。** The analysis includes 485 successful artifacts from 115 tasks with at least two successful configurations. Models include task fixed effects and sum-to-zero configuration effects. Intervals are pointwise 95% task-cluster bootstrap percentile intervals (10,000 accepted resamples). Values characterize successful artifacts only and are not causal effects or quality rankings.

---

## 11. 实施状态（按「已有 / 新增」分开）

**已有图、已有表：默认不动资产。**

- [x] Fig. 1–3、Fig. 5（`fig4.pdf`）、Fig. 6（`fig5a`/`fig5b`）已在正文。
- [x] Table 1、Table 6 已在正文。
- [x] Table 3 已在正文；Runs 列与脚注已按规范生成。
- [ ] 不为已有 Fig. 1–3 / Fig. 5 / Fig. 6 另起炉灶重画，除非单独决定。
- [ ] 不覆盖 `fig4.pdf`、`fig5a_pass_rate.pdf`、`fig5b_paired_gain.pdf`。

**新增项：**

- [x] Fig. 4 已按最新要求改为竖向分组柱状图；预览检查通过，正式 PDF 尚未替换。
- [x] Fig. 7 主分析、task 等权、repository bootstrap 各 10,000 次完成。
- [x] 固定效应系数经独立 explicit task-dummy OLS / WLS 核对；全部重采样检查连通性与 sum-center。
- [x] Fig. 7 forest plot 预览和 Table 5 CSV 已生成；旧 scatter 不再作为当前绘图方案。
- [x] Table 2 / Table 4 已在正文；本轮不动。
- [x] LaTeX 统计方法、RQ4、Fig. 7 caption / Description、Table 5 与 Threats 已统一迁移；旧 Pro–Luna 结果已退出主文。
- [x] Table 5 生成器已迁移；Table 2–5 生成与数据核查通过。
- [x] 正式 Fig. 4 / Fig. 7 PDF 已同步到确认的文字精简版，未重新绘图；其他正式图片保留。

本轮不编译 LaTeX。Pro ablation 重跑只更新 Table 4 整族，不影响本次保留的 main-results footprint 样本。

## LaTeX 交付（2026-09-15）

- 完整源码：`main.tex`；Overleaf 包：`featureliftbench_overleaf.zip`。
- Table 2 / 3 / 4 核对现有完整结果；Table 5 六配置调整后分析已完成。表顺序为 Main / Structure / Exposure / Ablation / Adjusted footprint / Related work，共 6 张。
- 独立表格片段：`writing/final_tables/`；静态结构检查：`writing/check_final_latex.py`。
- 统计和引用校验通过，不编译 LaTeX，因此不报告页数或声称排版已验证。
- 原始运行 profile 可用 307/900；完整 900-cell 汇总和 900 份 exposure 记录已核对，这不等于原始证据完整性审计。

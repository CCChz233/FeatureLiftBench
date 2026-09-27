# 最新论文 Fig. 3–8 绘图索引

以用户提供的 2026-09-26 版 PDF 中的**印刷图号和图注**为准。Fig. 1、Fig. 2 是 PPT 图片，不在此绘图流程中。运行入口：`draw_all.py`。

| PDF 图号 | PDF 页 | 内容 | 对应源码 | 预览输出 |
| --- | ---: | --- | --- | --- |
| Fig. 3(a,b) | 6 | 150 题功能类别、耦合机制 | `fig03_benchmark_composition.py` | `fig03a_families.pdf`, `fig03b_entanglement.pdf` |
| Fig. 4(a,b) | 11 | 40 题源码证据消融及配对区间 | `fig04_repository_evidence.py` | `fig04a_ablation_pass_rate.pdf`, `fig04b_ablation_paired_gain.pdf` |
| Fig. 4(c) | 11 | 机械迁移 DSE 诊断 | `fig04c_mechanical_relocation.py`；由 Fig. 4 入口调用 | `fig04c_dse_comparison.pdf` |
| Fig. 5 | 13 | 150 题的通过、缺交付和首败 gate | `fig05_failure_stages.py` | `fig05_evaluation_outcomes.pdf` |
| Fig. 6 | 14 | 三个定性案例的成败实现关系 | `fig06_qualitative_cases.py` 导出正式 PNG | `fig06_qualitative_cases.png` |
| Fig. 7(a,b) | 15 | 首次通过后 token 比例、响应次数 | `fig07_post_pass_execution.py` | `fig07a_post_pass_tokens.pdf`, `fig07b_post_pass_responses.pdf` |
| Fig. 8(a,b) | 16 | 成功产物的 task-adjusted RRES、Copy | `fig08_artifact_footprint.py` | `fig08a_rres.pdf`, `fig08b_copy.pdf` |

Fig. 6 的正式图是作者选定的手工编辑 PNG，不存在逐像素复现它的 Python 绘图源码。`fig06_qualitative_cases.py` 只将正式文件复制到预览目录。`legacy/fig06_qualitative_mechanisms.py` 是另一版向量构图，不对应 PDF 中的图。其历史来源见 `../fig6_final_provenance.md`。

Fig. 4(c) 从 `experiments/dse/source_ablation40_v1_2_reviewed_20260926/functional_summary.json` 读取 DSE 通过数，并与消融逐题数据核对相同的 40 题；其余数值从 Fig. 4(a,b) 的已保存消融结果读取。该面板是诊断比较，不是消融的第三个实验臂。

Fig. 4 的三个面板使用相同的 2.28 × 1.86 英寸画布，模型缩写统一为 Luna、Pro、Qwen；并排时总宽 7.2 英寸，面板间距 0.18 英寸。(a) 中的 “Full source” 是 “Full source + contract” 的图内短标签。可用 `python -B docs/paper-workbench/figures/scripts/preview_fig04_row.py` 生成一排的 PDF/PNG 排版预览。该预览不修改正文或正式图片。

## 使用

在仓库根目录运行：

```bash
python -B docs/paper-workbench/figures/scripts/draw_all.py --list
python -B docs/paper-workbench/figures/scripts/draw_all.py
python -B docs/paper-workbench/figures/scripts/draw_all.py --only 4 7 --output-dir /tmp/flb-figure-preview
```

默认生成 Fig. 3–8 的 PDF/PNG 预览和派生数据，位置为 `docs/paper-workbench/figures/output/latest_pdf/`。`python -B scripts/paper.py figures` 调用相同入口。只有显式 `--publish` 才将生成的 PDF 写入 `docs/paper/figures/`；发布前应检查预览，并同步 `main.tex` 的引用。单图脚本也支持 `--output-dir`；Fig. 3 使用 `draw_all.py` 统一入口。

`docs/paper/main.tex` 通过三个宽度为 `0.32\linewidth` 的 `minipage` 拼接 Fig. 4(a,b,c)，分别引用三个独立 PDF。`fig04_one_row_preview.pdf` 仅供检查排版，不是正文引用的图。图内 “Full source” 缩写在 caption 中对应 Full Source 条件。

统计输入由 `../../paper_sources.json` 和 `../../paper_inputs.py` 管理。Fig. 3/4/5 读取保存的任务与实验结果；Fig. 7 读取 `../../execution_effort.py` 的已保存分析；Fig. 8 使用 `footprint_analysis.py` 的 fixed-effects 与 bootstrap，派生分析文件以 `fig08_` 开头。`figure_common.py` 管理预览和显式发布，`paper_style.py` 管理画图样式。`legacy/` 和其余 `preview_*.py` 是历史或探索图，不在统一入口中。

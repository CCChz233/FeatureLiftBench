# 当前论文：从保存数据绘图

> **Status: current · Last verified: 2026-09-29**

这套脚本读取 [paper_sources.json](../../paper_sources.json) 选定的实验结果并生成 Fig. 3–8。它是**可复算流程**；若只想逐张调整外观，可用 [独立脚本](../standalone/README.md)。正式图片只在 [docs/paper/figures](../../../paper/figures/)。

| 正文图 | 脚本 | 正式文件 |
| --- | --- | --- |
| Fig. 3(a,b) | `fig03_benchmark_composition.py` | `fig03a_families.pdf`, `fig03b_entanglement.pdf` |
| Fig. 4(a,b) | `fig04_repository_evidence.py` | `fig04a_ablation_pass_rate.pdf`, `fig04b_ablation_paired_gain.pdf` |
| Fig. 4(c) | `fig04c_mechanical_relocation.py`，由 Fig. 4 入口调用 | `fig04c_dse_comparison.pdf` |
| Fig. 5 | `fig05_failure_stages.py` | `fig05_evaluation_outcomes.pdf` |
| Fig. 6 | `fig06_qualitative_cases.py` 仅复制手工编辑 PNG | `fig06_qualitative_cases.png` |
| Fig. 7(a,b) | `fig07_post_pass_execution.py` | `fig07a_post_pass_tokens.pdf`, `fig07b_post_pass_responses.pdf` |
| Fig. 8(a,b) | `fig08_artifact_footprint.py` | `fig08a_rres.pdf`, `fig08b_copy.pdf` |

Fig. 4 仍是当前正文的 **40 题**消融与 DSE 诊断；150 题试画保存在 [草稿目录](../drafts/rq2_150/README.md)，没有纳入正文。Fig. 1 是编辑后的 PNG；Fig. 2 在正文 LaTeX 中排版，均无现行 Python 绘图脚本。

在仓库根目录运行：

```bash
python -B docs/paper-workbench/figures/scripts/draw_all.py --list
python -B docs/paper-workbench/figures/scripts/draw_all.py --only 4 --output-dir /tmp/flb-figures-preview
python -B docs/paper-workbench/figures/scripts/draw_all.py
```

默认输出在 `figures/output/latest_pdf/`，不覆盖正式图片。只有显式 `--publish` 才会把生成的 PDF 写入 `docs/paper/figures/`。Fig. 6 的 PNG 来源见 [来源记录](../fig6_final_provenance.md)。`legacy/` 中的脚本是历史版本和试画，勿用来更新正文。

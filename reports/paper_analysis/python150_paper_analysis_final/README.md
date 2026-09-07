# Python-150 paper analysis final

Freeze v2 Official Main 收尾包。不再跑模型、不造方法。输入是
`../python150_prime_v2_analysis_20260905/task_results.csv`。

```bash
.venv/bin/python reports/paper_analysis/python150_paper_analysis_final/build.py
```

先读 **`summary_final.md`**：全部数字、逐题表、成对 copy、Finding 都在这一份里，不依赖图片。

| 路径 | 内容 |
| --- | --- |
| `summary_final.md` | 论文可抄写的 RQ 结论 |
| `fig/fig_task_difficulty_spectrum.pdf` | Figure 2：0/6–6/6，Core/hard3 stacked |
| `fig/fig_paired_copy.pdf` | Figure 4：Pro vs Luna 同题 copy |
| `fig/fig_independent_gates.pdf` | 非互斥四门失败 |
| `fig/fig_failure_stage_funnel.pdf` | Figure 1：首败漏斗 |
| `fig/fig_lift_type_hard3.pdf` | Lift × hard3（注明小 n） |
| `fig/fig_token_efficiency.pdf` | 附录：Pro/Flash incremental |
| `csv/task_difficulty.csv` | 每题 6 模型 pass 与 `num_models_solved` |
| `csv/lift_inventory.csv` | Direct/Adapted/Composite × Core/hard3 题数 |
| `csv/logistic_params.csv` | `passed ~ model + hard3 + lift_type` |
| `tex/tables.tex` | 可粘贴的 LaTeX 表 |
| `json/stats.json` | 全部统计 |

**不要**把控制 hard3 后的 Composite 写成显著更难。**不要**把 F3 的 63 升级成金标。

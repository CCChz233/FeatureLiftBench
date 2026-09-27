# Failure profile heatmap — subtype review preview

Status: **L1 assistant first pass; not final paper evidence or independent human review.**

本次工作的目的是把过宽的 Behavior drift 拆成读者能理解的具体问题，回答：
**在各模型已有的失败记录中，已经能识别出哪些具体失效行为？**
当前结果不能用于比较模型优劣，也不能证明某模型不存在图中为零的失效类型。

## Review coverage and denominator

All **201** records originally labeled Behavior drift were inspected against archived
failure output, submitted implementation, and frozen public clauses. The source set
contains 4,272 extracted files checked against archive-index SHA256 hashes and byte
counts. This was static review of archived evidence, not a new evaluation run or
an independent human review. One timeout has no identifying failure traceback.

| First-pass outcome | Cases | Treatment |
|---|---:|---|
| Subtype assigned without a recorded concern | 74 | Included in the five subtype columns |
| Candidate subtype with an unresolved contract or interpretation concern | 86 | Withheld from the plot |
| Original parent label needs review | 41 | Withheld from the plot |
| Total original Behavior drift | 201 | Every original record accounted for |

The **127** withheld records remain in the original within-model denominators.
They are pending review, not established benchmark defects. Three have a proposed
Missing API parent label because the absent operation is explicitly named in a
public clause; the frozen labels are not changed by this proposal.

The original 16 API-completion, 8 dependency-closure, and 2 packaging records are
carried forward from the frozen classification file and have **not** received this
new subtype review. The original one unclassified case is omitted visually as
requested, without changing its denominator. The 13 previously excluded candidate
defects remain excluded. No new exclusions are applied to the original denominator.

| Model | Original n | Assigned behavior subtypes | Pending review |
|---|---:|---:|---:|
| Pro | 26 | 8 | 17 |
| Flash | 31 | 11 | 19 |
| Luna | 30 | 7 | 20 |
| GLM | 35 | 7 | 20 |
| Qwen | 42 | 17 | 21 |
| OSS | 64 | 24 | 30 |

The cells display **100 × category count / original n**, not the share of the 74
assigned cases. Displayed counts total 100 cases: 74 subtype assignments plus 26
carried-forward categories. Therefore **100 + 127 + 1 = 228**. Rows do not sum to
100%. Colors use one linear 0–25% scale. Zero means no currently assigned record
in that cell; resolving pending cases may increase it.

## Codebook v1

| Key | Figure label | Meaning | Assigned cases |
|---|---|---|---:|
| call | Call mismatch | 调用兼容：参数次序、绑定或输入适配不符合约定，接口本身存在 | 4 |
| result | Incorrect result | 结果错误：返回值、数据结构、转换结果或结果次序错误 | 12 |
| parse | Parsing / formatting | 解析与格式：解析、规范化、语法树重建、序列化、文本或路径格式错误 | 33 |
| validation | Validation & errors | 校验与异常：接受或拒绝输入、警告或异常行为不符合约定 | 6 |
| state | State / control flow | 状态与控制流：生命周期、状态更新、回调分派、优先级或短路执行错误 | 19 |

“Missing API” 对应原来的 `contract_api_completion`，表示必需接口缺失；
“Call mismatch” 表示接口存在，但调用约定不匹配。这两个概念不能合并。
“Missing dependencies” 包括必需的内部辅助函数、资源或注册项缺失，
不单指未安装第三方软件包。

Assignment rules:

1. Screen whether the failure is within the frozen public contract. A missing
   required member or unresolved contract mismatch first triggers parent-label review.
2. Assign one subtype per artifact using the first observed failure and relevant
   implementation. Do not count every symptom or copy a classification across models.
3. Parsing/formatting takes precedence over generic wrong-result classification
   when the broken obligation is a parser, normalization rule, or serializer.
4. Use validation for incorrect accept/reject/error behavior, not every exception.
   Argument binding/adaptation belongs to call; lifecycle and dispatch to state.
5. Use result for a specific returned-value or transformation discrepancy, never
   as a residual bucket. A parser timeout without a diagnostic is not automatically
   parsing or control flow.
6. Keep candidate assignments and parent-review cases inspectable. Do not force
   their counts into the five cells to complete a visual pattern.

Examples in the assigned set include discarded transformation results, eager
evaluation where short-circuiting is required, reversed configuration precedence,
and comment text retained inside a parsed environment value. These descriptions
are sanitized; no hidden test names, assertions, or input literals are exported.

## Files and reproduction

- `failure_root_cause_annotations.csv`: all 201 first-pass decisions, candidate
  labels, concerns, public clause IDs, and submission file/line references.
- `summary.json`: definitions, per-model counts, review tiers, reconciliation,
  and source/annotation hashes.
- `../../figures/scripts/preview_fig06_failure_subtypes.py`: checks source hashes,
  independently aggregates the ledger, and renders PDF/PNG/SVG plus plot-data CSV.
- The private evidence pointer in each CSV row is relative to
  `reports/paper_analysis/behavior_drift_subtypes_20260918/`. Its review index maps
  the identifier to the archived run and extracted material directory. Private
  logs and submissions must not be included in a public release of this folder.
- `reports/paper_analysis/behavior_drift_subtypes_20260918/build_dataset.py`
  reproduces these public files from the private manual-decision ledger.

`root_cause_primary` and `original_evidence_eligibility` preserve the frozen source
labels for traceability; **they do not assert that pending rows have been
reconfirmed**. `evidence_eligibility` is `review_pending` for every flagged record.
Only `plot_eligible=1` is counted in the new subtype columns. All new review rows
have `independent_human_review=false`.

From the repository root:

```sh
python -B .agents/skills/featureliftbench-annotate-failures/scripts/validate_annotation_csv.py docs/paper/data/failure_subtypes_20260918/failure_root_cause_annotations.csv
MPLCONFIGDIR=/tmp/flb-mpl python -B docs/paper/figures/scripts/preview_fig06_failure_subtypes.py
```

The renderer writes only to `docs/paper/figures/output/fig6_subtypes/` by default.
It does not update the PDF referenced by `main.tex`. The refinement is ready for
visual review; final adoption requires resolving the pending cases under the
existing annotation protocol and updating the paper's denominator/tier statements
consistently if any original parent labels or eligibility decisions change.

Suggested preview caption:

> Failure profiles with a first-pass refinement of behavioral drift. Cells show
> percentages of the original within-configuration failure total. The five
> behavioral columns include 74 assigned cases; 127 cases with unresolved subtype
> or parent-label questions are withheld and reported at right. Original API,
> dependency, and packaging categories are carried forward. The one original
> unclassified case is not plotted. Denominators are unchanged; the figure is a
> review preview, not a completed or independently human-reviewed taxonomy.

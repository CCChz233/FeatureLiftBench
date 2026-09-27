# Figure text audit — 2026-09-15

## Rule

Figures retain panel titles, axes / necessary node labels, essential reference lines, data, and minimal legends. Sample summaries, uncertainty definitions, baseline interpretation, and reading instructions belong in captions or the text. For schematic figures, nodes, gates, boundary names, and short edge labels carry the diagram's data and must remain understandable.

This audit inspected the seven figures referenced by `docs/paper/main.tex`, the current Fig. 4 / Fig. 7 Python renderers, and retained `fig6.pdf` / `fig7.pdf`. Formal PDFs and the manuscript were not overwritten. Latest statistical previews: `../output/text_cleanup_preview/`.

## Figure-by-figure decisions

| Figure | Keep | Move to caption / text | Status |
| --- | --- | --- | --- |
| Fig. 1 (`fig1.png`) | Three panel titles; source/new package boxes; capability highlight legend; dependency names; agent/submission/evaluator nodes; evaluation boundary and gates | Three introductory sentences; three bottom takeaway boxes; dataset count footer; full-sentence notes listed below | PNG inspected; removal map recorded, image not edited |
| Fig. 2 (`fig2.png`) | Construction/validation headings; four construction steps; validation node names and compact descriptors; Frozen release; 450/450 as validation data | Band subtitles; withheld-test sentence; exclusion sentence; repeated 150-task counts; 126 repositories / 132 snapshots; replay count explanation | PNG inspected; removal map recorded, image not edited |
| Fig. 3 | Panel titles, families, totals at bar ends, heatmap percentages and fractions, category names | Lift-type counts in legend and row labels (already in cells / caption) | Script cleaned; two new previews generated |
| Fig. 4 | Six models, zero-to-100 axis, three colored bar series, category legend | Legend `n=56/76/18` | Script cleaned; preview generated; caption below retains denominators |
| Fig. 5 (`fig4.pdf`) | Axis/model labels, stacked stage counts, stage legend | No active explanatory sentence remains | Current PDF already complies; preserved |
| Fig. 6 (`fig5a/fig5b`) | Panel titles, conditions, exact values, baseline, CI marks, Pro dagger marker | `(95% CI)` in panel (b) title; dagger/interval definitions | Script title cleaned; preview generated; existing caption already explains CI and Pro timeouts |
| Fig. 7 | Two panel titles, model/metric axes, zero-based bars, 1× / 0 pp lines, CI marks | Entire top sample/CI line; entire bottom baseline/oracle line | Script cleaned; compact preview generated; caption retained separately |

### Fig. 1: exact sentence-removal map

Move these explanatory elements out of the image while preserving the three-column structure:

- `A new project needs behavior already implemented in another repository.`
- `Behavior supported by the original project may break when that context is removed.`
- `Can an agent preserve the required behavior across a new software boundary?`
- `(spans multiple locations)` and `Dependencies must be resolved.`
- `Only the submitted package enters` and `Source repository unavailable at runtime.` (The boundary and Source-free evaluator node remain.)
- `Both test groups are withheld from the agent.` and `All four checks required.`
- All three bottom takeaway boxes: `Existing implementation / Different reuse boundary`, `Working in the source project does not establish independent correctness.`, and `Source repository: implementation evidence / New package: evaluation target`.
- Footer `150 tasks · 126 repositories · 132 source snapshots`.

Keep the required API / observable behavior / runtime constraints nodes, and the capability/context arrows. Those specify the task rather than explain how to read a statistic.

### Fig. 2: exact removal / retention map

Move `From source capability to executable task`, `Complementary evidence`, `Primary and Extended benchmark tests are both withheld from agents.`, and `Problematic candidates excluded during construction` to caption/text.

Move `150 task packages`, `All 150 retained tasks`, `150 Python tasks`, `126 source repositories`, and `132 pinned snapshots` to a single caption statement. Keep `450/450 passing runs` as the one numerical validation result; describe the three executions per task in the caption. Keep the short semantic descriptors inside construction/validation nodes, so the process remains intelligible. `Frozen release` names the endpoint and remains.

Fig. 1/2 are embedded-text PNGs, and the historical Python renderers do not reproduce them. This turn records a specific edit map without substituting a different design or modifying the raster assets.

## Retained appendix / historical assets

- `fig6.pdf` is the retained classification appendix asset. Remove its two `Benchmark (n = 150)` lines and `Mechanisms can overlap` when next editing it; the heatmap counts remain. `Within-type coverage` can be shortened to `Coverage (%)` if the colorbar is retained. The appendix asset is preserved, not deleted. Current `main.tex` does not include this file.
- `fig7.pdf` is a historical multi-pair comparison, not the current Fig. 7. It contains a top title/description, per-pair n labels, and a bottom reading instruction. These should be moved to a caption if that historical design is reused. The inactive renderer is left untouched to preserve history.
- Formal `fig7_matched_footprint.pdf` is still the old Pro–Luna identity scatter and contains `97 tasks passed by both configurations` and `Points below...`. It must eventually be replaced as a whole by the approved adjusted analysis; stripping text alone would leave the wrong scientific content.
- Formal Fig. 4 is also older than the approved vertical grouped-bar renderer.

## Caption drafts (not yet written into LaTeX)

### Fig. 1

Feature lifting and its evaluation boundary. An agent receives an intact source repository and a public behavioral contract, constructs a new package, and submits only that package to a source-free evaluator. Correctness requires Build, Primary, Extended, and Isolation checks; both test groups are withheld from the agent. Highlighted source locations are illustrative, not benchmark-provided localization hints. The source repository is implementation evidence; the independent package is the evaluation target.

### Fig. 2

Construction and validation of FeatureLiftBench. A pinned source capability is turned into a public contract, protected tests, and an independent feasible reference. Validation combines automated consistency checks, author semantic review supported by structured AI-assisted evidence checks, and three source-free reference replays per task (450/450 passing executions). Problematic candidates are excluded during construction. The frozen release contains 150 tasks from 126 repositories and 132 source snapshots; both benchmark test groups are withheld from agents.

### Fig. 3

Composition of the 150-task benchmark. (a) Ten functional families partitioned by lift type: Direct (56), Adapted (76), and Composite (18). (b) Coverage of four non-exclusive entanglement mechanisms overall and within each lift type; cells report task percentages and counts. A task may involve multiple mechanisms.

### Fig. 4

Observed functional capability by lift type. Grouped bars show within-category pass rates for Direct (56 tasks), Adapted (76), and Composite (18). These categories describe task structure rather than an independently calibrated difficulty scale. Exact structural results appear in Table 2.

### Fig. 5

Keep the existing caption: the current figure contains data and a minimal stage legend, with no redundant prose to relocate.

### Fig. 6

Keep the existing caption, which already explains the 40-task paired comparison, the 95% paired task-bootstrap intervals, the experimental conditions, and the Pro timeout marker. The panel title becomes simply `(b) Paired gain`. The local Fig. 6(a) renderer uses grouped bars while the imported formal asset uses connected points; cleaned script output is a preview, not a silent replacement of the imported design.

### Fig. 7

Task-adjusted implementation footprints of 485 successful artifacts from 115 tasks with at least two successful configurations. (a) Configuration effects from a task fixed-effects model of log2(RRES), displayed as multiplicative size effects on a linear ratio axis. (b) Configuration effects for detected source overlap (Copy), in percentage points. Bars start at zero; dashed lines mark the sum-to-zero center of configuration effects (1× and 0 pp). These are configuration-relative effects rather than raw oracle-relative RRES values. Error bars show pointwise 95% task-cluster bootstrap percentile intervals from 10,000 accepted resamples. The analysis characterizes successful artifacts only and does not extrapolate to tasks on which a configuration fails.

## Checks / migration state

- Fig. 4 and Fig. 7 preview geometry checks passed: values / CI endpoints match saved evidence, all labels inside the canvas, bar baselines preserved.
- Fig. 7 statistical model, sample, estimates and three bootstrap analyses are unchanged.
- Fig. 3 percentages/counts and Fig. 6 ablation data were regenerated from the existing evidence and assertions, without new experiments.
- No LaTeX compilation or formal asset replacement. Caption drafts above require later coordinated manuscript migration; the old RQ4 and Table 5 remain in main.tex.

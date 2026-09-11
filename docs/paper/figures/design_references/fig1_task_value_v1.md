# Fig. 1 — task positioning and joint reuse requirements

## Delivered files

- fig1_task_value_v1.svg: editable vector, text remains text.
- fig1_task_value_v1.pdf: vector paper figure, embedded fonts.
- fig1_task_value_v1.png: full-resolution preview.
- ../scripts/draw_fig1_task_value.py: reproducible layout source.
- fig1_task_value_v1_validation.json: dimensions and layout checks.

This version was directly composed with Python/Matplotlib. It is not an AI-generated raster. Existing manuscript files and figures have not been replaced, and no experiments or LaTeX compilation were run.

## Editorial purpose

The left panel establishes the distinctive combination of intact implementation evidence and an independent output artifact. It contrasts representative task objectives, rather than trying to classify every benchmark or claim greater difficulty. Feature development can be incremental or from scratch; source-independent output alone is not claimed as novel.

The right panel makes two requirements explicit: the artifact must satisfy specified behavior and must not require the source repository at runtime. It is a conceptual requirements matrix, not an empirical result, root-cause taxonomy, or depiction of independently measured evaluator gates. A source-dependent wrapper can reproduce behavior when its original dependency is available, but it cannot thereby pass the actual source-free benchmark evaluation.

“Imports the original source package” means a runtime dependency on the original package. It does not prohibit copying source code into the submitted artifact. Retained third-party dependencies remain governed by each task environment. Correct behavior here includes the relevant execution requirements; the four concrete gates are explained by the paper, not separately expanded in this motivation figure.

## Manuscript alignment

The figure is based on main.tex Introduction, Task Formulation, and Related Work, especially:
- Intact source repository plus public output contract.
- Extract, adapt, or reimplement are permitted.
- New package evaluated without source repository access.
- FeatureBench has both incremental and from-scratch settings.
- Functional success requires actual behavioral and source-isolation checks.

This is a different Fig. 1 concept from the current Blinker running-example figure. If adopted, revise the existing running-example lead-in, caption, and accessibility description together. Do not silently replace the existing file under its old caption.

## Suggested caption

FeatureLiftBench evaluates reuse across a new software boundary. (a) The agent receives an intact implementation and an output contract, then constructs an independent package; representative feature-development and repository-modification objectives provide context. (b) Functional reuse requires both the specified behavior and independence from the source repository. The matrix illustrates these joint requirements, not measured outcome frequencies. Actual submissions are evaluated without access to the source repository.

## Accessibility description

The left panel compares available evidence and deliverables for feature implementation, repository modification, and feature lifting. Feature lifting is highlighted: an intact source repository and output contract lead to an independent package. The right panel has a two-by-two matrix of behavior satisfaction and runtime source dependence. Only the cell with specified behavior satisfied and no source repository required is marked successful feature lifting.

## Layout verification

Canvas: 180 × 94 mm, intended for full paper width. In a two-column ACM layout, use a figure* spanning both columns; do not shrink this design to one column. Main text is approximately 8–9.5 pt at its native width, with secondary labels down to 7.2 pt.

The exported PDF was rendered and visually inspected, including at an 1100-pixel preview. Text-on-text overlap, canvas overflow, and matrix-cell horizontal overflow checks passed after revision. No visible clipped labels or overlapping text remained in the inspected export.


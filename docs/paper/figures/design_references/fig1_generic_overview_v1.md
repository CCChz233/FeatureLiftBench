# Fig. 1 generic task overview — preview

- Mode: built-in imagegen, reference-guided edit.
- Reference: fig1_layout_refinement_v1.png.
- Output: fig1_generic_overview_v1.png.
- User direction: the introductory schematic should describe the general benchmark task, without a named repository or concrete API example.
- Changes: replace Blinker-specific structure and requirements with a generic repository, public behavior contract, independent package boundary, and source-free evaluation.
- Visually checked: no Blinker/Signal/Namespace identifiers or prescribed Python file tree; two inputs feed the agent; runtime source absence and withholding of both evaluator test groups are explicit; four checks are conjunctive; footer remains 200/176/182; text fits without visible clipping.
- The repository graph and agent activities are illustrative, not a precise dependency graph or mandated algorithm. The independent package is evaluated under the benchmark environment; the figure does not claim distribution-ready installation.
- This is a raster preview. main.tex and the currently referenced figure were not changed. Adoption should update the current Blinker-specific figure introduction, caption, and accessibility description.

## Suggested caption if adopted

FeatureLiftBench task overview. Given an intact source repository and a public behavioral contract, an agent reconstructs the required capability within a new package boundary. The submitted artifact is evaluated without access to the source repository, and functional success requires Build, Public, Hidden, and Isolation checks to pass. Both evaluator test groups are withheld from the agent. Repository structure and reconstruction activities are illustrative; internal implementation organization is unrestricted.

## Exact generation prompt

Use case: precise-object-edit / scientific infographic.
Edit the supplied FeatureLiftBench figure into a GENERAL benchmark overview. The user explicitly rejects the named Blinker example and wants a generic schematic. Keep the restrained three-column academic composition and blue/orange visual vocabulary, while replacing all domain-specific content.

Output ONE high-resolution, approximately 2:1 landscape figure on pure white. Make it a clean paper figure with flat solid fills, crisp thin outlines, modest corner radii, one readable sans-serif family, consistent font hierarchy, and perfectly aligned cards. No gradients, shadows, poster title, mascots, decorative shapes, 3D, logos, source-code screenshots, or empirical model results. Avoid tiny writing and large empty gaps. Every label must fit; no clipping or intersections with connector lines.

Absolutely remove ALL occurrences of blinker, Signal, Namespace, weak receivers, sender dispatch, featurelifted, and example-specific Python filenames. This version must depict the TASK CLASS rather than an individual repository, API, programming language, or implementation. No exact file organization is mandated.

THREE COLUMNS, approximately equal width, with subtle vertical divider rules. Retain small numbered blue circles. Align headings, description baselines, and bottom summary cards.

COLUMN 1: INPUTS AND THE REUSE NEED
Title: "An existing capability to reuse"
Description, two lines: "The required behavior may span multiple modules and dependencies."

Large pale-blue source card titled "Complete source repository".
Inside show an abstract repository structure:
Three equal blue module cards "Module A", "Module B", "Module C" on an upper row. They contain minimal short gray code strokes as abstract code, no real programming text.
Under them, two wide lighter neutral cards "Shared utilities" and "Data and resources".
A few restrained thin connecting lines express illustrative relationships among repository components. Do not draw elaborate cycles, or highlight a preselected solution slice. This is a generic structure, not a claim every task has all dependency types.
Small internal bottom note: "Relevant implementation must be identified."
Use hierarchy and grouping to make this source card visually rich and informative without any specific example.

Below, a white/blue public specification card:
Header "Public behavioral contract"
Three clearly spaced parallel entries:
"Required API"
"Observable behavior"
"Constraints and exclusions"
Short final line: "Defines what the new package must preserve."
The source card and contract card are visibly separate inputs.

Bottom summary, aligned with other columns:
"Source repository + public contract"
"Available to the agent"

COLUMN 2: THE RECONSTRUCTION TASK
Title: "Reconstruct across a new boundary"
Description, two lines: "Recover the required functionality and reorganize it for independent execution."

At top of the main diagram, two small compact input labels "Source evidence" and "Public contract", with visible blue connectors from BOTH to a centered orange "Coding agent" card. These compact labels refer to the two full inputs in column 1.
Below the agent, three compact equal-width activity labels on one row, separated cleanly:
"Locate code"
"Resolve dependencies"
"Preserve behavior"
These are illustrative activities, not a prescribed algorithm.
A clear orange arrow leads down into an orange dashed "NEW PACKAGE BOUNDARY". The boundary label is centered in a gap in its top border.
Inside, an orange-tinted output card headed "Independent package" with a small flat folder icon. Show two or three wide internal content rows, as conceptual contents rather than required filenames:
"Required public API"
"Reconstructed behavior"
"Supporting implementation"
Below the internal rows, small legible text:
"extract · adapt · reimplement"
Keep padding around the package and do not let activity labels or arrows collide.

Bottom summary card:
"New boundary, preserved contract"
"Internal organization may change"

COLUMN 3: SOURCE-FREE VERIFICATION
Title: "Evaluate without the source"
Description, two lines: "Check the submitted artifact in an environment without the source repository."

One orange card at the upper center, titled "Submitted package", with a simple folder icon.
A single blue arrow from this artifact crosses a horizontal dashed line labeled "EVALUATION BOUNDARY", and enters the evaluator below.
Adjacent to this crossing, clearly legible but compact: "Only the submitted artifact enters"
There must be NO runtime arrow from a source repository into the artifact or evaluator.

A large pale-blue evaluator capsule, heading "Source-free evaluator".
Immediately underneath, an environment-restriction line:
"Source repository unavailable at runtime"
Then four equally sized white checks on ONE row:
"Build" ∧ "Public tests" ∧ "Hidden tests" ∧ "Isolation"
Use proper logical AND glyphs, not carets or OR. All labels must fit comfortably; test labels can use two lines.
Small note below:
"Both test groups are withheld from the agent."
A blue result bar inside the capsule:
"Functional pass"
"All four checks required"
No green ticks implying automatic success. This diagram defines the criteria.

Bottom summary card:
"Source repository: implementation evidence"
"Submitted package: evaluation target"

FOOTER:
A thin pale-blue rule and a plain centered line with exact numbers:
"200 tasks · 176 repositories · 182 source snapshots"
These are full benchmark scope counts. No model-count or 150-task comparison labels belong in this task overview.

SEMANTIC REQUIREMENTS:
The source repository is intact and visible during construction; unavailable during evaluation. The agent must infer relevant implementation from the public contract and complete source, without being handed source-location hints. Behavior preservation is relative to the declared contract, not every capability of the original project. Adapting or reimplementing is permitted; preserving the original dependency structure or original file tree is not required. Independent execution is under the benchmark environment, not a promise of distribution-ready packaging. All four checks are necessary. The public contract is available; both evaluator test groups are withheld.
Maintain an informative general overview with clear input, reconstruction, new boundary, and evaluation distinctions. This must be a reusable schematic of the benchmark task, not a renamed concrete example.


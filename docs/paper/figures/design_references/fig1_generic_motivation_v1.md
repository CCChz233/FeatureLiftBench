# Fig. 1 — generic motivation and task overview

- Mode: built-in imagegen; reference-guided edit.
- Input: fig1_generic_overview_v1.png.
- Output: fig1_generic_motivation_v1.png.
- User-approved story: reuse need -> loss of the original supporting context and evaluation gap -> FeatureLiftBench's source-free task.
- Generic illustration; no named repository, API, model, or required file layout.
- Visually checked: the middle column explains the context-removal risk rather than repeating an agent workflow; both source and contract connect to the agent; only the submitted package enters evaluation; source absence, withholding of both evaluator test groups, all four conjunctive checks, and exact 200/176/182 counts are present. No visible clipped text.
- The middle-panel green check and question mark depict illustrative conditions, not measured results or an inevitable failure. The comparison concerns repository-editing evaluation, not a universal assertion about all existing benchmarks.
- Source highlights illustrate behavior distributed across implementation locations; these are not source-location hints supplied to agents.
- This remains a raster preview for review or PowerPoint reconstruction. No current paper figure or main.tex reference was replaced; no experiments or LaTeX compilation were run.

## Suggested caption if adopted

Motivation and task overview of FeatureLiftBench. A requested capability can span modules and supporting dependencies in a source repository. Correct behavior in the original project does not establish that the capability will remain correct after that context is removed. FeatureLiftBench provides an intact source repository and a public behavioral contract, and evaluates the reconstructed package without access to the source repository. Functional success requires Build, Public, Hidden, and Isolation checks to pass; both evaluator test groups are withheld from the agent. Source structure and highlighted locations are illustrative and are not location hints supplied to agents.

## Exact prompt

Use case: scientific-educational infographic / reference-guided image edit.
Create the latest Fig. 1 for the FeatureLiftBench paper by substantially revising the supplied overview. This revision must communicate MOTIVATION, not merely repeat a benchmark workflow. The agreed story is: a real reuse need → why working in the source project does not establish correctness across a new boundary → the task that FeatureLiftBench evaluates. Keep the generic three-column composition, white background, and restrained blue/orange academic palette. No named repository, no concrete library API, and no programming-language-specific filenames.

Design one polished high-resolution landscape paper figure, approximately 2:1. Flat vector-like graphics, thin clean strokes, solid white/pale-blue/pale-orange fills, consistent modest corner radii, navy text, one sans-serif family. No gradients, shadows, 3D, decorative logos, marketing poster title, mascots, or ornamental icons. Use information-rich diagram relationships instead of long prose. Three equal-width columns, subtle vertical separators, small numbered blue circles. Align titles, introductory descriptions and bottom takeaway cards. All text must be legible at reduced size, fit inside its own region, and never overlap arrows or borders. Maintain generous internal padding.

COLUMN 1 — A REUSE NEED
Title: "Reuse an existing capability"
Description, two short lines:
"A new project needs behavior already implemented in another repository."

Upper diagram: a large blue source-project enclosure titled "Source repository".
Inside it, show three module cards on one row labeled "Module A", "Module B", "Module C". Each contains several short gray code strokes and one small orange code segment, suggesting that the desired capability spans multiple implementation locations rather than a ready-made selected file.
Below them, two supporting cards "Shared code" and "State / resources", connected by thin blue undirected relationships to the modules. The graph is illustrative; no elaborate cycles.
Include a compact orange key "Desired capability" for the orange segments. Highlighting is explanatory, not an agent-visible location hint. Do not draw a precomputed source slice as an input.

Below the source enclosure, a clean white card headed "Reuse goal".
Use an orange outlined small package symbol beside the main phrase:
"The capability under a new package boundary"
Below this phrase, three short well-spaced contract attributes:
"Required API"
"Observable behavior"
"Runtime constraints"
A small orange arrow from the source enclosure toward this goal may be labeled "Reuse selected behavior". This is a developer's goal, not a claim the extraction is already solved.

Bottom takeaway:
"Existing implementation"
"Different reuse boundary"

COLUMN 2 — THE MOTIVATION AND EVALUATION GAP
Title: "Correctness depends on context"
Description:
"Behavior supported by the original project may break when that context is removed."

This is the conceptual centerpiece. Do NOT draw a coding-agent workflow in this column.
Show two vertically arranged situations connected across a clearly marked change of boundary.

Upper blue enclosure labeled "Original project context".
Inside, a blue "Existing capability" card with clearly drawn short connections to three smaller support labels:
"Code dependencies"
"State / resources"
"Framework assumptions"
The support labels may be on one row with two-line text. A modest green check next to "Works in this context" indicates an ILLUSTRATIVE working original configuration. This is not an empirical benchmark result.

An orange downward arrow from the capability leads out of this original enclosure, crossing a dashed horizontal boundary with the label "Original context removed".
The support boxes remain visibly inside the original enclosure; do not draw them as automatically migrating into the new package.

Below the boundary, an orange "New package" card with a restrained orange question mark and the question:
"Required behavior preserved?"
Use a thin broken connection or a single gray disconnected stub near the new package to suggest that earlier supporting assumptions no longer automatically hold. Do not assert that every lift fails, that all dependencies are prohibited, or that raw copying is the required strategy.
Small supporting line:
"Dependencies must be resolved."

Under this conceptual comparison, a compact two-row evaluation contrast:
"Repository editing" → "Evaluate in the original project"
"Feature lifting" → "Evaluate without the source repository"
Keep this crisp and readable, with equal row alignment. No named benchmarks and no universal claim about ALL existing benchmarks. This specifically contrasts repository-editing tasks with feature-lifting tasks.

Bottom takeaway:
"Working in the source project"
"does not establish independent correctness."
Use a legible font and two or three lines if needed, without crowding.

COLUMN 3 — THE BENCHMARK'S RESPONSE
Title: "What FeatureLiftBench tests"
Description:
"Can an agent preserve the required behavior across a new software boundary?"

A compact, complete vertical task diagram:
Two equal blue input cards, "Intact source repository" and "Public behavioral contract". BOTH have visible blue connectors into an orange "Coding agent" card.
Orange arrow to an orange folder card "Submitted package".
A blue arrow from the package crosses a horizontal blue dashed line labeled "EVALUATION BOUNDARY" and enters a pale-blue evaluator.
Only the submitted package crosses into evaluation.

Evaluator heading: "Source-free evaluator"
Environment statement directly under it:
"Source repository unavailable at runtime"
Then four white checks in a single row, each with enough space:
"Build" ∧ "Public tests" ∧ "Hidden tests" ∧ "Isolation"
Use the mathematical logical AND symbols between the checks. No automatic success ticks.
Below: "Both test groups are withheld from the agent."
Blue result bar:
"Functional pass"
"All four checks required"

Bottom takeaway:
"Source repository: implementation evidence"
"New package: evaluation target"

BOTTOM FOOTER:
A thin light-blue separator and a single plain centered scope line:
"200 tasks · 176 repositories · 182 source snapshots"
These exact verified numbers describe the released benchmark. No model results, sample pass rates, or additional difficulty labels.

SCIENTIFIC CONSTRAINTS:
The source is intact and available during construction. Public contract defines the behavior and constraints to preserve. Original code may be extracted, adapted, or reimplemented; the task does not prescribe a single construction pipeline. Source repository access is absent during evaluation, while permitted dependencies belong to the benchmark environment. Independence does not claim a distribution-ready package or a minimal implementation. The center panel depicts a possible risk, not an inevitable failure or measured frequency. Its repository-editing contrast must not claim other benchmarks are static or do not execute tests.
Generic module/support illustrations are explanatory, not location hints supplied to agents and not assertions of a fixed structure across all 200 tasks.
No Blinker, Signal, Namespace, featurelifted, real project names, actual API examples, filenames, or model names anywhere.
The visual priority is the reuse need and context-removal problem; the right-hand workflow should be compact enough to leave the middle motivation easy to understand at a glance.


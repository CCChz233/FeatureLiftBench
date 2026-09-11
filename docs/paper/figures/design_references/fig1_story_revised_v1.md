# Fig. 1 — edited user-provided three-panel figure

Source edit target: C:/Users/CHZ/Downloads/ChatGPT Image 2026年9月10日 21_20_26.png

Final image: fig1_story_revised_v1.png

Method: built-in image_gen, image editing with the user image as reference. A second targeted edit corrected two arrow endpoints. Original image, main.tex, and existing paper figure files are unchanged.

## Changes verified visually

- Retained reuse need → evaluation objectives → FeatureLiftBench narrative.
- Removed oversized top title, decorative corner slogans, and redundant footer.
- Replaced donor terminology with source repository.
- Removed unsupported bidirectional call-graph-like arrows and global-registry obligation.
- Four selected Blinker behaviors: sender-specific dispatch, receiver responses, weak-receiver cleanup, namespace identity.
- Qualified package-boundary motivation; no claim that Blinker lacks a package.
- Feature development explicitly includes incremental and from-scratch settings.
- Distinguished upstream repository assets from withheld benchmark tests and references.
- Package runtime restriction refers to the original source repository; source copying remains allowed.
- Retained all four conjunctive evaluator gates.
- Corrected headline result: 76 of 77 combined failures first occur in Public or Hidden, not a set including Isolation.
- Full model names and the 150-task comparison scope retained; separate score cards removed.
- Agent output arrow reaches the package; submission arrow crosses the source-free boundary.

Numeric evidence: docs/paper/main.tex:663–668 and appendix funnel rows: Pro 25 Public + 10 Hidden; Flash 26 Public + 15 Hidden + 1 Isolation. Both have zero missing and Build-first outcomes. These are first observed failing gates, not causal diagnoses.

This is an AI-edited raster reference. Its wording and layout were inspected at preview scale; it is not an editable vector or a full-size typeset-paper validation.

## Primary editing prompt

Use case: infographic-diagram, precise editing of an existing academic figure.
EDIT THE ATTACHED IMAGE. It is the edit target, not merely stylistic inspiration. Preserve its recognizable three-panel narrative, blue-and-orange academic palette, clean borders, and left-to-right organization: reuse need, task positioning, benchmark setting. Improve this specific figure rather than inventing an unrelated layout. Produce a crisp high-resolution landscape paper figure, roughly 2:1 aspect ratio, with all English text legible at full paper width.

GLOBAL EDITS:
Remove the enormous top "FeatureLiftBench" title and subtitle, ALL tiny decorative corner slogans, their ornamental lines, and the extra bottom subtitle. Reallocate the freed space to larger body text and comfortable spacing; start with the three panel headers near the top. Keep only the useful full-width bottom sentence verbatim:
"The source is implementation evidence; the new package is the evaluation target."
Keep the three sections with modest 1/2/3 markers, but reduce decorative icons. White background, very pale blue panel accents, muted orange for feature lifting. No gradients or shadows. Do not turn this into a table or abstract anonymous-module drawing.

PANEL 1:
Heading: "Software reuse across boundaries".
Change "Intact donor repository" to "Intact source repository". The word "donor" must not appear anywhere.
Subtitle: "Example: Blinker signal registry".
Replace the six-box dense bidirectional dependency graph with an honest, clean grouped view labeled "Selected behavioral obligations". Show four equal, readable boxes in a 2 by 2 grid:
"Sender-specific dispatch" with sublabel "Route events by sender"
"Receiver responses" with sublabel "Collect callback results"
"Weak-receiver cleanup" with sublabel "Remove collected receivers"
"Namespace identity" with sublabel "Stable signal per name"
Group these under a single small label "Signal registry". Use grouping/containment rather than a fabricated call graph: NO inter-box arrows, cross arrows, or file icons claiming these are separate files.
Below the four obligations, a quiet gray strip:
"Supporting implementation: identity handling, weak references, utilities"
Delete "shared state / global registries" entirely, since the task excludes the upstream global singleton. Delete the ellipsis and the old bottom text about framework logic.
Replace the red warning "No ready-made package boundary" with a restrained warm-accent statement, with NO warning triangle:
"Existing package boundaries may not match the reuse target."
Fit this statement in two or three clearly readable lines. This is the motivation, not a claim Blinker lacks a package.

PANEL 2:
Heading: "Different evaluation objectives".
Delete the bracket and label "MISSING EVALUATION SETTING" between panels.
Keep the three stacked task comparisons, but use the following precise labels.
Row 1 heading: "Repository editing"
Flow: "Existing repository" → "Patch" → "Evaluate in the revised project"
Small caption: "Modify the existing project."
Row 2 heading: "Feature development"
Flow: "Requirements" → "Implement target feature" → "Evaluate feature"
Small caption, split into two readable lines if needed:
"Incremental or from scratch; the target implementation is not supplied intact."
This refers to the complete TARGET implementation, not absence of all repository evidence.
Row 3, emphasized in pale orange:
Heading: "Feature lifting"
Flow: "Intact source + output contract" → "Reconstruct capability" → "Independent package"
Closing sentence: "Preserve specified behavior beyond the original project."
Do not claim all previous research lacks software reuse or independent outputs.

PANEL 3, slightly wider than the other two:
Heading: "FeatureLiftBench"
Retain the useful two-input diagram feeding a coding agent, then an independent package and a source-free evaluator, but simplify texts and make font size readable.

Input box 1:
"Complete source repository"
"Pinned source snapshot"
"Upstream tests / docs / resources"
Input box 2:
"Public behavioral contract"
"Required API"
"Behavior obligations + exclusions"
Both connect to "Coding agent".
Small policy note below the two inputs, if space allows without crowding:
"Benchmark tests and reference solutions are withheld."
Do not conflate upstream tests with protected benchmark tests.

Coding agent connects down to a warm outlined:
"Independent package"
"featurelifted"
"Extract / adapt / reimplement"
"No runtime dependency on the source repository"
Remove "own runtime dependencies". This does NOT prohibit vendoring or copying source code.

A single clear dashed vertical boundary separates this package from its evaluator. The package arrow crosses to evaluator. Label the arrow "Submission only", and label the dashed line "Source-free evaluation boundary". Ensure boundary labels do not overlap connectors.
Evaluator text:
"Source-free evaluator"
"Source repository unavailable"
"Build ∧ Public ∧ Hidden ∧ Isolation"
The four conjunctive gate labels are evaluation criteria, not the failure-statistic definition.

BOTTOM OF PANEL 3:
Replace the whole large “Why this benchmark matters” leaderboard block with ONE compact result callout, without separate model score cards.
Heading:
"Evidence from the 150-task comparison"
Text verbatim, with deliberate line breaks as needed:
"DeepSeek V4 Pro and DeepSeek V4 Flash each delivered packages for all 150 tasks."
Then emphasize:
"76 of 77 combined failures first occurred in Public or Hidden tests."
Do NOT include Isolation in that 76/77 statistic. There was ONE additional Isolation-first failure; it is fine to omit that detail here. Remove the 115/150 and 108/150 cards, the magnifier icon, and the general “Strong agents usually...” box. Keep exactly this one correctly scoped finding.
Use whitespace and typographic hierarchy rather than more boxes.

TYPOGRAPHY AND QUALITY:
Keep a polished research-paper appearance and the reference's overall identity, but remove poster-like decoration. Balanced three-column widths, with third wider as needed. Body text must be substantially readable; simplify spacing, do not shrink to tiny fonts. Use bold selectively for headings and the "76 of 77" finding. No cropped labels, no overlaps, no meaningless arrows, no invented statistics. All requested scientific corrections must be applied. This is an edited version of the supplied figure.

## Targeted connector correction

Edit this exact supplied figure. Preserve ALL text verbatim, all numbers, the complete three-panel layout, colors, typography, sizes, and all boxes. Make ONLY two small connector-geometry corrections in the rightmost FeatureLiftBench panel:
1. The output arrow from "Coding agent" must clearly terminate at the TOP CENTER of the "Independent package" box. Use a neat elbow connector below the Coding agent, going left then down, with its final downward arrowhead meeting the top border of the package. Currently the downward arrow points just outside the package's upper-right edge; fix that. Avoid all text and borders other than its intended endpoints.
2. Extend the horizontal "Submission only" arrow so that it visibly CROSSES the dashed vertical source-free evaluation boundary and its arrowhead meets the LEFT BORDER of the "Source-free evaluator" box. Currently it stops before crossing the boundary. Keep the "Submission only" label above the arrow without collision with the dashed line or box.
Everything else must remain unchanged. In particular, preserve "76 of 77 combined failures first occurred in Public or Hidden tests.", both full DeepSeek model names, all source repository terminology, the four behavioral obligations, and the single bottom sentence. No additional elements, redesign, or text changes. Return the corrected full image at high resolution.


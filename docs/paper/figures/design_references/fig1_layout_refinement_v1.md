# Fig. 1 layout refinement preview

- Mode: built-in imagegen; reference-guided image editing, followed by one localized typography correction.
- Source: C:/Users/CHZ/AppData/Local/Temp/codex-clipboard-e9a7fa0d-b8d2-435f-b291-505e3cdd34e0.png
- Selected output: fig1_layout_refinement_v1.png
- Scope: retain three columns and the source/contract/package/evaluation story; group Signal and Namespace coherently, repair text spacing, show source absence and test visibility explicitly, shorten footer to verified release counts.
- Visually reviewed: no central text obstruction; left reuse-request list wraps within its card; source-repository-unavailable and both-tests-withheld statements retained; all four checks are conjunctive; counts are 200 tasks, 176 repositories, 182 source snapshots.
- This is an AI-generated raster layout preview for user review or PowerPoint reconstruction. It is not an editable vector asset. No main.tex or existing final figure was replaced; no experiments or LaTeX compilation were run.
- When adopting the figure, the caption should state that source grouping, selected behavioral requirements, and output file layout are illustrative, and internal organization is unrestricted.

## Initial edit prompt

Use case: precise-object-edit / scientific infographic.
Edit target: the supplied three-column FeatureLiftBench paper figure. Produce ONE refined, fully typeset version of this figure. Preserve its three-column story, white background, restrained navy/blue/orange palette, and named Blinker example. The user's request is to apply a specific layout correction, not to invent a different concept or a decorative poster.

Output: a crisp high-resolution landscape academic figure, approximately 2:1 aspect ratio, suitable for a software engineering paper and easy to recreate in PowerPoint. Flat vector-like rendering; solid fills, thin consistent outlines, modest corner radii. Use a single highly legible sans-serif font, with monospace for Python identifiers. No gradients, shadows, textures, 3D, giant brand heading, decorative illustrations, or watermark. All content must fit with comfortable padding; absolutely no overlap, clipping, text crossing lines, or text touching borders.

GLOBAL LAYOUT:
Three well-balanced columns separated by two thin pale-blue vertical rules. Each has a small blue numbered circle and bold navy title. Titles and the subsequent two-line descriptions align across columns. Diagram regions start at the same height. Leave generous spacing between descriptions and diagrams. Make typography substantially easier to read than in the input; solve crowding by using the exact shorter text specified here. Align the lower edge of the first column's reuse-request card with the lower summary cards in columns 2 and 3. A compact plain footer centered under all three columns contains only:
"200 tasks · 176 repositories · 182 source snapshots"
Delete the input's full-width long concluding sentence and large numerical boxes. Numbers must remain exact.

COLUMN 1
Title: "Real-world reuse need"
Description: "Required behavior spans interacting components and their supporting logic."

Upper blue-tinted source card header: "blinker (source repository)", with blinker in monospace.
Inside, an orange dashed group labeled "Desired capability".
Replace the four disconnected diamond-layout nodes with a clear stacked grouping:
- A wide light-blue card headed "Signal". Inside it, two compact horizontal labels: "Sender dispatch" and "Weak-receiver cleanup".
- Below it, a wide light-blue card headed "Namespace", with subtitle "Stable signal identity per name".
Below the dashed group, inside the source card, a thin gray card: "Supporting helpers".
Do NOT draw a call graph, circular arrows, bidirectional dependency edges, or connections claiming that dispatch/cleanup call Namespace. These are conceptual functional groupings, not exact source file organization.

Lower white card:
Header "Reuse request"
Sentence "Reuse the signal registry in an independent package."
Then TWO clearly separated columns with equal top alignment and clean list spacing:
Left header "Behavior examples"
- "Sender-specific dispatch"
- "Weak-receiver cleanup"
- "Stable signal identity per name"
Right header "Output requirements"
- "API under featurelifted"
- "Independent execution"
- "No runtime import of blinker"
Use monospace for featurelifted and blinker. Allow carefully spaced line wraps when needed. The two columns must never collide. No separate repetitive summary box under this card.

COLUMN 2
Title: "Why lifting is non-trivial"
Description: "Reconstruct the required behavior within a new package boundary."

Main diagram retains evidence on the left and an orange output package on the right, but removes the input's three crowded central text lines entirely. Leave the central connector corridor empty except for arrows.
Left evidence nodes, compact and consistently spaced:
"Signal"
"Sender dispatch"
"Weak-receiver cleanup"
"Namespace"
"Supporting helpers"
Use light-blue nodes and a gray helpers node. Thin blue collectors/arrows lead right toward the reconstructed package, representing use and reorganization of source evidence, not a source code dependency graph. Arrows may not cross labels.
Above the package on the right: orange-tinted "Coding agent" card with a vertical orange arrow down to the package.
Orange dashed boundary labeled "NEW PACKAGE BOUNDARY"; the heading must have a clear break in the dashed top edge.
Inside the boundary: pale-orange package card, simple flat folder icon and monospace "featurelifted/".
Three white file rows, spelled exactly:
"signal.py"
"namespace.py"
"__init__.py"
Small line inside the bottom of the boundary: "extract · adapt · reimplement".
Ensure all elements stay inside the column with clear padding.
Below the diagram, three small equal-size pale neutral action labels:
"Locate relevant code"
"Resolve dependencies"
"Preserve behavior"
These replace the input's long question boxes. They are short action labels, not paragraphs.
Bottom summary card with two lines:
"The reuse goal defines the new boundary."
"Internal organization may change."

COLUMN 3
Title: "What FeatureLiftBench evaluates"
Description: "Evaluate the submitted package without access to the source repository."

Two aligned input cards:
"Complete source repository"
subtitle "(implementation evidence)"
and
"Public behavioral contract"
subtitle "(reuse goal specification)"
Both connect by clear blue arrows to one centered orange "Coding agent" card.
Orange arrow from agent to orange folder card "featurelifted/".
Blue arrow from the submitted package enters a large light-blue evaluator card.

Evaluator card:
Header "Source-free evaluator"
Directly below the header, a clear environment restriction line:
"Source repository unavailable at runtime"
No source-repository arrow feeding the package or evaluator.
Inside, four evenly spaced white checks on one row:
"Build" ∧ "Public tests" ∧ "Hidden tests" ∧ "Isolation"
Use the logical AND character between checks. This must not appear as alternatives.
A small centered note below checks: "Both test groups are withheld from the agent."
Then one blue result bar:
"Functional pass"
second line "All four checks required"
No automatically green checks or success rates; this is a task definition.
Bottom summary card:
"Source repository: implementation evidence"
"New package: evaluation target"

Maintain the scientific meaning:
The source is visible during construction and unavailable during evaluation.
All four checks jointly determine functional pass.
Extracting, adapting, and reimplementing are allowed strategies.
No mandatory preservation of original dependency topology; no claim of guaranteed packaging quality beyond the benchmark environment.
Do not add model results, difficulty tiers, logos, extra metrics, citations, or additional claims.
Render EVERY label cleanly with strong readable hierarchy and comfortable space. The final should look like a carefully laid-out paper figure, not an ornate AI-generated infographic.

## Local typography correction prompt

Edit this academic figure with ONE strictly localized typography correction. Keep the entire figure unchanged except the right-hand column of the bottom-left "Reuse request" card. Preserve every other diagram, label, arrow, color, card, and footer number at its current position. Do not restyle or regenerate the overall layout.

The right-hand "Output requirements" list currently approaches the card's right border. Reflow its three bullet items with deliberate line breaks, using a slightly smaller but clearly legible font if necessary, so there is a comfortable right inner margin. The exact content and line breaks should be:
• API under
  featurelifted
• Independent execution
• No runtime import
  of blinker

Use monospace for featurelifted and blinker. Keep the header "Output requirements" and the central vertical divider. Make the three bullet blocks evenly spaced, with no collisions, and keep at least 12 pixels of white padding above the card's bottom border at the supplied image size. The whole list must remain inside the existing card; all characters must be visible. Leave the left "Behavior examples" list unchanged.

Preserve the clear source-absence line, both-test-groups-withheld note, four conjunctive checks, grouped Signal/Namespace example, source repository terminology, source file names, and exact footer "200 tasks · 176 repositories · 182 source snapshots".


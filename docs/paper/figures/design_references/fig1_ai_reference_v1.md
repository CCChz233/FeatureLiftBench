# Fig. 1 AI design reference

Generated with the built-in image_gen tool. This PNG is a PowerPoint reconstruction reference; it does not replace any manuscript figure.

## PowerPoint corrections

- Arrange Build, Public tests, Hidden tests, and Source isolation in a clearly conjunctive sequence, or label the group "All four required". The current two-row layout has no conjunction connecting its rows.
- Group Public tests and Hidden tests together under "Evaluator-only tests". The generated brace currently spans Hidden tests alone.
- Use plain flat fills and vector shapes for the final paper figure.
- Source component connections are schematic associations, not a verified dependency graph.

## Generation prompt

Use case: infographic-diagram.
Create ONE polished academic overview figure for FeatureLiftBench, a software engineering benchmark paper targeting FSE. This is a raster design reference that the author will reproduce in PowerPoint. Use the supplied image only as a conceptual reference; substantially simplify and redesign it. All figure text in English.
Wide landscape aspect ratio approximately 2.4:1, opaque pure white background, crisp flat vector-like geometry, no shadows, gradients, textures, perspective or decorative art. Simple editable-looking rounded rectangles, straight connectors, Arial-like typography. Navy text, restrained blue for source/evaluation, warm orange for reconstructed package, light grey for environment boundary. Large readable labels, ample whitespace, aligned columns. Avoid massive enclosing panel borders and avoid excess text. No big figure title, caption, watermark or conference logo.

Three stages with small numbered circles and exact headers:
"1  Source evidence"
"2  Feature lifting"
"3  Source-free evaluation"

LAYOUT AND SCIENCE:
Stage 1 (left):
Two stacked clean cards both connect via short clear arrows to the Agent in stage 2.
Top card title "Source repository", small subtitle "blinker · simplified view".
Inside four small connected elements: "Signal", "Namespace", "Sender dispatch", "Receiver cleanup". Use undirected light grey association lines (NOT a precise dependency graph). Convey distributed implementation evidence.
Bottom card title "Public behavioral contract" with exactly three short lines:
"Sender-specific dispatch"
"Weak-receiver cleanup"
"Stable namespace identity"
Small unobtrusive footer: "Agent sees source code and contract".

Stage 2 (center):
An "Agent" rounded rectangle leads via a strong orange arrow to a larger orange-outlined "Lifted package" card. Both fit in middle column and are visually central. Inside package three rows: "Signal", "Namespace", "Supporting logic". Orange outline itself clearly represents the new package boundary; small label directly above outline "New package boundary". Under Agent a small two-line annotation "Inspect • adapt • reconstruct". Under package a small crossed-out dependency annotation "No runtime dependency on blinker" (one restrained red cross, no giant red warning).
MAIN DATAFLOW: two left input cards -> Agent -> Lifted package -> evaluator. Make this visible and uninterrupted. The arrow from package to evaluator must visibly CROSS a vertical GREY DASHED LINE between columns 2 and 3, then ENTER evaluator box. Label this crossing arrow "Submitted package". The dashed line label is "Evaluation boundary" and fits neatly within top safe margin; never collide with headers. Leave a clear gutter for line and arrow.

Stage 3 (right):
One large light blue outlined card "Source-free evaluator".
Small subtitle INSIDE card: "Source repository unavailable".
Next smaller line "Network disabled · frozen dependencies".
Main content label "Functional correctness"; underneath four modest gate boxes in two-by-two layout, showing conjunction with small plus/AND or mathematical conjunction:
"Build", "Public tests", "Hidden tests", "Source isolation".
Place "Evaluator-only tests" in small text adjacent to the Public/Hidden boxes, so it is unambiguous that neither test set is agent-visible.
Below evaluator a small narrow pale orange strip, subordinate to correctness:
"Successful artifacts: RRES · Copy"
Small subtitle "Relative size and source overlap".
Do not label these as universally better/worse extraction quality, do not imply size must pass a gate.

Bottom spanning width: two compact comparison rows separated from main diagram by whitespace and a thin rule:
"Repository editing"  "Existing repository → Patch → Evaluation in the same repository"
"Feature lifting"  "Source repository → Independent package → Evaluation without the source repository"
Align labels and paths precisely. Second row lightly accent orange package and blue source-free evaluation.

REQUIREMENTS: reduced text versus reference; consistent source repository terminology, NEVER donor. Every piece of text contained with comfortable padding; no clipped labels, overlapping text or line through words. The central package-crossing arrow is the key visual. Prioritize coherent, accurate workflow over decorative sophistication. Easy to recreate using PowerPoint basic shapes.


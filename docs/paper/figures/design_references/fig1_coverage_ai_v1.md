# Fig. 1 coverage.py AI reference, v1

Generated with the built-in image_gen tool for review and possible PowerPoint reconstruction. main.tex and existing paper figures are unchanged.

Image: `fig1_coverage_ai_v1.png`

The scenario and POSIX paths are illustrative, derived from the existing PathAliases contract and source. Outputs represent required behavior, not measured model outcomes. See `FIG1_CASE_SELECTION.md` for source evidence.

Visual inspection: both path outputs and key labels are correct. Helpers are grouped in coverage/files.py, with ConfigError in coverage/exceptions.py. The absent coverage.py repository is distinct from the controlled target filesystem. The partial dependency view and the middle-column spacing can be refined during editable reconstruction.

## Exact generation prompt

Use case: infographic-diagram.
Create a NEW high-resolution academic paper Figure 1 concept image for FeatureLiftBench, intended as a reference the author will recreate in PowerPoint. Landscape roughly 2.1:1 aspect ratio. English labels only. White background, sophisticated restrained scientific typography, crisp flat vector-like lines, precise alignment. Dense in meaningful relationships but highly legible. No giant title, no decorative pictograms, no robots, no 3D, no gradient, no shadows, no black background, no stock infographic styling, no big rounded cards. Mostly charcoal text, muted navy for source evidence, burnt orange for new artifact, teal for correct behavior, light gray for excluded context.

Central narrative: reuse a specific existing capability, reconstruct across a new software boundary, preserve a conditional behavior with the original source repository unavailable. Illustrative scenario, not model experiment.

LAYOUT:
A narrow top strip about 16% of height compares two task objectives in aligned horizontal rows, separated from the main example by a fine rule:
gray row: "Repository modification" followed by "Issue + existing repository  →  Patch  →  Evaluation in that repository"
navy/orange row: "Feature lifting" followed by "Intact source + contract  →  New package  →  Source-free evaluation"
Do not say existing benchmarks all have one setup; these are task objectives, no benchmark names or superiority claims.

Below, a short lead sentence: "Illustrative reuse need: bring CI-path remapping into an independent report viewer."
Then use an organized left-to-right schematic over remaining main area, with three unequal sections about 40%, 20%, 40%, small lettered headings:
"(a) Existing implementation"
"(b) New package"
"(c) Required behavior"

LEFT:
A thin rectangular source boundary labeled "coverage.py — source repository".
Inside draw an actual implementation relationship diagram, not a folder inventory.
One large inner region labeled "coverage/files.py" contains the focal box "PathAliases.add / map". From it, thin dependency arrows go to three compact supporting labels within SAME files.py region:
"globs_to_regex"
"canonical_filename / sep"
"source_exists"
A separate small inner region labeled "coverage/exceptions.py" contains "ConfigError", with an arrow from the focal box. Use modest code monospace.
At bottom of source boundary a light gray area labeled "Outside the requested feature" with smaller "measurement · storage · CLI". Do not draw dependencies into this excluded area.
Directly underneath source boundary, a compact text block "Behavioral contract" with three concise lines:
"Match aliases and normalize paths"
"Accept a mapping only if its target exists"
"Preserve unmatched paths"
These represent publicly specified obligations, no visible hidden test files.

MIDDLE:
Thin arrow from source evidence to a simple orange outlined package rectangle.
Arrow label "inspect & reconstruct".
Rectangle label "featurelifted", containing small code text "PathAliases" and underneath "matching", "path handling", "existence checks". Its internal organization is illustrative, not a dictated implementation.
Short small note below "Extract, adapt, or reimplement".
To the right of this package, a prominent dashed vertical line indicating the evaluation boundary. One clear horizontal arrow crosses from the package into the right evaluation section, labeled "artifact only". NO arrow from source repository crossing this line. Place "New runtime boundary" near the dashed line without overlapping arrow labels.

RIGHT:
Heading "Source-free evaluation".
Small context label "coverage.py unavailable".
An input and rule block at top:
"One alias rule"
"/ci/*/src → /workspace/src"
"Input: /ci/job42/src/a.py"
Then two equal vertically stacked cases, with thin rules rather than giant cards:
"Target exists" in teal, output monospace "/workspace/src/a.py", explanatory label "accept mapping".
"Target missing" in charcoal, output monospace "/ci/job42/src/a.py", explanatory label "keep original path".
Connect the common input to both cases with a clean branching connector. Both are REQUIRED correct behaviors, not successes/failures of competing methods: do not put a red failure X on the second case.
Small bottom note "Controlled target filesystem / exists callback" to make clear that source-free does not mean no filesystem.
The right cases must show the SAME input and SAME alias; the ONLY difference is target existence. There is only one rule in this example.

At the bottom across whole figure, a narrow understated takeaway separated by thin line:
"Recover the behavior behind the API, then preserve it beyond the source repository."

IMPORTANT QUALITY:
Ensure every label is fully inside the image and does not overlap. Avoid long prose and unnecessary repeated headings. All fonts sufficiently large for two-column paper width. Preserve path strings exactly. No performance numbers, no fabricated model outputs, no new task counts, no RRES/Copy table, no public-versus-hidden results. No claim of unique minimal closure, no claim that the entire coverage tool is copied or needed. All visible structure should be easy to recreate with ordinary PowerPoint rectangles, connectors, and text.


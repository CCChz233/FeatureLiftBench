# Fig. 1 final selection

## Decision

Use the three-panel task overview based on the author's latest Blinker figure:

1. Complete source repository + public behavioral contract.
2. Reconstruct an independent package.
3. Evaluate without the source repository.

This is the selected Fig. 1. It defines the task, deliverable, and success conditions. Keep literature positioning, illustrative failures, and model results in their corresponding paper sections; do not add these back into Fig. 1.

## Final asset and integration

- Figure: `fig01_feature_lifting_final.png`, under docs/paper/figures.
- main.tex now references that file.
- Lead-in, caption, and accessibility description have been updated together.
- Original PDF and earlier design variants remain untouched.
- No experiments or LaTeX compilation were run.

## Content decisions

- Blinker is the running example, consistent with Section 2.
- Source repository is the term used throughout.
- Source implementation is simplified into Signal, Namespace, and supporting implementation; no invented call-graph edges.
- Five selected public obligations include sender-specific dispatch and responses, weak receiver cleanup, namespace identity, scoped connections, and the required API.
- Both source repository and public contract visibly feed the agent.
- Package layout is explicitly illustrative and unrestricted.
- Source copying, adaptation, and reimplementation remain permitted.
- Only the submission is evaluated, without runtime access to the source repository.
- Four check marks are explicitly prerequisites for functional pass, not empirical results.
- 200 tasks / 176 repositories / 182 snapshots are benchmark scope, not the common comparison size.
- Top title and redundant slogans are removed.

## Production and review

Built-in image_gen image editing was used on the user-provided PNG. A targeted second edit moved the lower input connector from the source group to the public-contract group. The resulting text, counts, grouping, and input connector endpoints were visually inspected. The final asset is a raster image; no claim of vector editability or LaTeX-rendered verification is made.

Original edit target:
C:/Users/CHZ/AppData/Local/Temp/codex-clipboard-c39d23aa-568f-4f72-a5f0-34c5e84a2217.png

## Final editing prompt

Use case: infographic-diagram. EDIT the supplied FeatureLiftBench figure into the final task-overview Figure 1 for an academic paper. Preserve this image's overall three-panel composition, Blinker running example, restrained blue/orange distinction, white background, and clear source → independent package → source-free evaluation narrative. This is the selected final design, not a request for alternative concepts.

Remove the huge top "FeatureLiftBench" title and its subtitle. Move the panel headers upward and use the recovered space for larger readable labels. Keep one modest bottom interpretation strip and the three benchmark-size numbers. No results, model names, scores, failure case, literature comparison, or motivation sidebar should be added. High-resolution, landscape roughly 2:1. Clean flat fills, crisp typography, no gradients or shadows.

PANEL 1, header: "1  Source evidence + public contract"
Upper group title: "blinker (source repository)".
Use ONLY "source repository" throughout; no "donor".
Within this upper group, show a simplified implementation view with two side-by-side named regions:
"Signal" with "sender dispatch" and "weak-receiver cleanup" inside or directly beneath it;
"Namespace" with "named-signal identity" inside or directly beneath it.
A short lower strip reads "Supporting code and state".
Show these as grouped implementation elements. Remove the source image's arbitrary bidirectional dependency arrows and cross-links. This is a simplified view of relevant implementation, not a call graph or a claim about separate files.
A small label can read "Selected implementation elements".

Lower group title: "Public behavioral contract".
Small subheading: "Selected obligations".
Five short lines, clearly readable:
"Required API in a new namespace"
"Sender-specific dispatch and responses"
"Weak-receiver cleanup after GC"
"Stable signal identity within a namespace"
"Scoped connection and disconnection"
Bottom information-policy note, in two or three readable lines:
"Agent-visible: complete source repository + contract."
"Withheld: benchmark tests, reference solutions, and source-location hints."

CRITICAL CONNECTOR: both the upper source group and the lower public-contract group must feed the coding agent in panel 2. Use a tidy joining connector along the narrow gutter between panels, ending at the Coding agent's left edge. Do not route through labels. Two inputs, one agent. If needed move the agent slightly down to align with the joint input. This is more important than preserving exact old positions.

PANEL 2, header: "2  Reconstruct an independent package"
Keep "Coding agent" as a modest orange box.
A downward arrow leads from it into the new package boundary.
Use the text "Extract / adapt / reimplement" exactly ONCE, next to this downward arrow.
Inside a dashed orange boundary labeled "New package boundary", show "featurelifted/" with these illustrative file entries:
"signal.py"
"namespace.py"
"__init__.py"
Directly beneath the entries, add "Illustrative layout; internal structure is unrestricted."
Remove the second redundant "extract / adapt / reimplement" inside the package.
Below the package boundary, a concise requirement:
"Preserve the declared behavior without runtime access to the source repository."

CRITICAL CONNECTOR: a clear right-pointing arrow from the submitted package in panel 2 must cross the gutter into panel 3 and reach the submission-only entry. Label it "Submission only". The arrow must actually connect the package to the evaluation area. It must not suggest that the source repository crosses this boundary.

PANEL 3, header: "3  Source-free evaluation"
Top entry group, connected from panel 2:
"Submitted package"
"featurelifted/"
Alongside it, a smaller gray crossed-out repository symbol labeled:
"Source repository unavailable at runtime".
A thin downward connector from the submitted-package entry leads into the evaluation checks.

Rename "Evaluator capsule" to "Functional evaluation".
Prominently state:
"Functional pass requires all four checks"
Display the four conjunctive checks in a single readable row, retaining the source image's overall familiar arrangement:
"Build" ∧ "Public tests" ∧ "Hidden tests" ∧ "Isolation"
Use at most a small check icon per check; explicitly present these as REQUIREMENTS for a functional pass, not observed model outcomes. The requirements sentence must be readable above the four checks.
Replace "Behavior-preserving functional score" with simply "Functional pass".
Do not add a numeric score or suggest distribution-ready packaging. Build means loadable/executable under the benchmark environment.

BOTTOM STRIP:
Keep one concise main sentence:
"Source repository = implementation evidence; new package = evaluation target."
Keep three small scope labels on the right, exact:
"200 tasks"
"176 repositories"
"182 snapshots"
Delete the redundant second source-evidence → package → evaluation tagline.
If all elements cannot fit on one line at a readable font size, use two clean lines rather than shrink text.

QUALITY CONSTRAINTS:
All labels fully contained and readable. Preserve the reference's chosen narrative and example; do not redesign into a matrix, table, anonymous modules, or experimental-results figure. No "donor", no unsupported dependency edges, no implied fixed required file layout, no ambiguity that public benchmark tests are visible to the agent. No large empty title region or decorative corner slogans. Prioritize correct connector endpoints, controlled density, and enough room around conjunction symbols. Produce the complete final edited image only.

## Targeted connector correction

Make ONE precise connector edit to this exact attached image. Preserve every word, label, number, font, color, panel, file entry, icon, arrow elsewhere, and the full layout exactly.

In the LEFT panel, there are currently TWO blue lines leaving the UPPER source-repository group and merging into the Coding agent. This is incorrect because the agent must have TWO DIFFERENT INPUTS: source repository AND the lower Public behavioral contract.

Keep the UPPER blue input line from the source-repository group to the Coding agent unchanged.

REMOVE the LOWER existing blue line that leaves the source-repository group at the height of the Signal / Namespace boxes. Restore its old location cleanly with the original background.

Replace that lower line with a line that STARTS at the RIGHT EDGE of the LOWER "Public behavioral contract" rectangle, roughly at the height of that rectangle's title (not through any text). Route it right into the slim empty channel between the panels, then UP along that channel to join the existing input merge immediately before the Coding agent arrow. Keep the route to the LEFT of the dashed orange "New package boundary", so it never crosses any part of the submitted-package drawing. The resulting long elbow connector must visibly attach to the public-contract rectangle, not the source-repository rectangle.

There must now be exactly one source-repository input branch and one public-contract input branch, merging into one arrow ending at the Coding agent.

Do not add any new labels or change any other content. In particular, the "Submission only" arrow and all four evaluation checks remain exactly as supplied. Return the corrected complete figure.


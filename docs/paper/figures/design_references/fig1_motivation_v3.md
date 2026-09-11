# Fig. 1 motivation design v3

Generated with the built-in image_gen tool from FIG1_STORY_V3.md. This PNG is a design reference for PowerPoint reconstruction. No manuscript image was replaced.

## Scientific scope and final reconstruction notes

- Upper rows compare task objectives, not model performance or universal capabilities of all previous benchmarks. Feature implementation includes within-repository and from-scratch settings.
- The reuse request is illustrative, not a collected user quotation.
- Source graph lines show schematic relationships between behaviors; they are not a literal call graph or required output architecture.
- The receiver-lifetime check is an illustrative public contract requirement, not an experiment result or hidden test reproduction.
- "Submitted package remains executable" describes the required outcome. In final PowerPoint text, prefer "Required: executable without the source repository" to make this explicit.
- Runtime source access is forbidden; copying, adapting and reimplementing source code remain permitted.
- Use flat white/pale fills in the editable final figure. Shorten the dashed boundary line or mask behind labels so it does not visually run through the central questions.
- The final figure still needs actual-size typography inspection after PowerPoint reconstruction; this generation is not a compiled-paper layout check.

## Final generation prompt

Create ONE new academic motivation figure for the FeatureLiftBench software engineering benchmark paper, intended as the FIRST figure in an FSE paper and as a reference for PowerPoint reconstruction.

Use case: infographic-diagram. This is a rigorous scientific argument diagram, not a marketing infographic or software architecture poster. Flat vector-like artwork, opaque PURE WHITE canvas, wide landscape aspect about 2:1, high resolution. Arial/Helvetica-like typography, black-charcoal text, thin grey rules, restrained blue (#245B78) for existing functional behavior and muted burnt orange (#B36536) for the new package. No gradients, shadows, 3D, robot/brain/person/database icons, oversized numbered circles, glossy rounded cards, giant title, decorative illustrations, branding logos, giant checkmarks, or background texture. Use rectangular boundaries, compact labels, purposeful connectors, clean typesetting, ample padding. Increase meaningful information density by showing behavioral relationships, not by adding paragraphs. All text in English and legible at paper width.

SCIENTIFIC STORY:
An existing implementation is available as evidence, yet it is embedded in its original repository. A reuse request requires the capability to preserve specified behavior under a new independent package boundary. Source code MAY be copied, adapted or rewritten; the ORIGINAL repository may NOT be used as a runtime dependency. This task is distinct from modifying an existing repository and from implementing missing functionality. Do not claim that prior benchmarks never test dependencies, behavior preservation, independent generation or reuse.

COMPOSITION: top compact positioning strip (~23% of height), central concrete reuse challenge (~62%), bottom behavioral requirement (~15%). Clean full-figure margins.

TOP STRIP, heading in small bold text "Three evaluation objectives".
Three perfectly aligned text-and-arrow rows with modest column spacing, not giant bordered boxes.
Row 1 grey:
"Repository modification"    "Issue + repository" → "Patch" → "Revised repository"
Row 2 grey:
"Feature implementation"    "Feature requirement" → "Implement feature" → "Within a repository or from scratch"
Row 3 accent:
"Feature lifting (ours)"    "Intact source + contract" → "Independent package" → "Source-free behavior"
Rows describe objectives, not performance rankings. Add no check/cross superiority matrix. Fine rule below.

CENTRAL PART:
At its top place a small bold "Reuse need" label followed by one concise sentence:
"Reuse an existing signal registry as an independent component."
This is an illustrative motivating request, NOT a quote from a real user.

Below that, main artwork occupies three regions:
LEFT 39%: a thin grey RECTANGULAR source boundary, title "Existing capability in a source repository", subtitle "blinker · implementation evidence".
Inside depict a compact interrelated code/behavior cluster, not a tree of filenames. One blue-bordered main node labeled "Signal dispatch", and two smaller blue-bordered nodes labeled "Weak-reference support" and "Receiver cleanup". Thin solid grey association lines connect the three, with a small nearby label "Supporting behavior". These lines are schematic associations, not claimed exact call graph. Include a few unobtrusive pale-grey background rectangles INSIDE the source boundary labeled "Other APIs", "Async support", "Project context". These must be visibly separate from the three blue relevant nodes. Do not color them red or claim they are defective.
The point is that the capability and required support are embedded in broader repository context. Small bottom note inside source boundary: "Complete implementation available to the agent".

CENTER 22%: a clear horizontal orange arrow from the relevant source cluster to the new package on the right. Label above arrow "Preserve required behavior". Label below "Extract / adapt / reimplement".
One GREY dashed vertical line through the arrow in the gap, label neatly above the line "New package boundary". Arrow visibly crosses line without colliding with text. Make this boundary-crossing the dominant visual event, not a giant Agent box.
Below this arrow, two short stacked questions in dark grey with restrained text, no cartoon question marks:
"Which supporting behavior is required?"
"What must be rebuilt across the boundary?"
Arrange them to fit within the central gap; they may wrap to two lines.

RIGHT 34%: title above "Independent component". An orange rectangular package boundary titled "featurelifted".
Inside it show a blue main node "Signal dispatch", supported by a blue node "Receiver lifetime handling". A connector between them demonstrates the target behavior plus supporting behavior must both be present. Small text inside bottom: "Internal structure may change".
Immediately under the package boundary (still in right region) show two compact environment conditions:
"Source repository unavailable at runtime"
"Submitted package remains executable"
No grey ghost repository in the target area, no Python import details, no lock icon. Code reuse is permitted; runtime import of the source repository is not.

BOTTOM:
Thin rule, then an understated one-line concrete semantic test spanning width:
"Behavior that must survive:"  "Weak receiver is garbage-collected" → "Receiver is no longer invoked"
Small "Illustrative contract requirement" annotation.
Then a short bold research question centered:
"Can existing functionality survive a new software boundary?"

IMPORTANT TYPOGRAPHY:
Use 2–3 font sizes, aligned baselines, clear whitespace between sections. No tiny prose blocks. Keep the source and target nodes readable and the central transition unambiguous. No text or arrows crossing through labels. All content within canvas. Draw in an understated technical-figure aesthetic typical of software engineering papers. Do not include RRES, Copy, steps, tokens, model results, success percentages, dataset counts, four evaluator gates, or construction/validation pipeline. This is the motivation and positioning figure, not a protocol diagram.


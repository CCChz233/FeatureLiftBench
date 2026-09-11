# Fig. 2 AI design reference

Generated using the built-in image_gen tool. PowerPoint reconstruction reference only; existing manuscript files and figures are unchanged.

## Evidence and reconstruction notes

- Content checked against main.tex, Section 2 construction and validation: 200 tasks, 176 source repositories, 182 snapshots; full author review of retained tasks; saved reference replay 600/600, three runs per task.
- The validation band groups complementary evidence. It does not establish chronological order or reruns after each author decision. Keep the cards unconnected to one another.
- Both Public and Hidden benchmark tests are withheld from agents. The public behavioral contract is visible.
- Recreate with flat fills, editable text, and vector connectors in PowerPoint. The generated image has slight fill variation that is unnecessary in the final figure.
- No model results, 150/50 comparison split, or difficulty tiers belong in this construction figure.

## Generation prompt

Use case: infographic-diagram.
Create ONE publication-quality academic Figure 2 design reference for the FeatureLiftBench paper. The author will recreate it with basic PowerPoint shapes. A crisp flat vector-like English scientific workflow diagram on opaque WHITE, landscape about 2.2:1. Consistent with a companion source-evidence / feature-lifting / source-free-evaluation figure: dark navy Arial-like typography, blue outlines and pale blue fills for construction, warm orange outlines and pale orange fills for validation, a neutral final release card. No gradients, 3D, textures, shadows, glossy effects, oversized icons, or decorations. Use generous whitespace, large legible text, tidy straight arrows, simple rectangles with mildly rounded corners. All text must fit. No caption or Figure 2 number or overall title inside artwork.

PURPOSE: Clearly separate HOW TASKS ARE BUILT from WHAT EVIDENCE SUPPORTS THEM. Do not repeat agent execution from Fig1. Do not portray validation blocks as a chronological sequence; the saved replay records are complementary evidence, not proven reruns after each author decision.

LAYOUT:
Main area left 78% has TWO horizontal bands stacked. Right 19% contains one vertically centered final release card reached by two independent clean arrows, one from construction and one from a collector bracket for validation. Whitespace gutter between main area and release. No looping connectors. Top and bottom main area are aligned.

TOP BAND:
Small navy uppercase heading "CONSTRUCTION" with small subtitle "From source capability to executable task".
Four equal blue cards left to right linked by blue arrows. Headers numbered 1–4, with at most 3 short body lines per card:
1 header "Select capability"
body "Real Python projects"
"Bounded reuse target"
2 header "Pin source"
body "Complete source repository"
"Versioned snapshot"
3 header "Define contract"
body "APIs and behavior"
"Explicit exclusions"
4 header "Build task assets"
body "Protected tests"
"Independent reference"
Small shared note underneath these four cards: "Public and Hidden benchmark tests are both withheld from agents."
The arrow from final construction card goes into right release card. Avoid squeezed lettering; wrap headers to 2 lines if needed.

BOTTOM BAND:
Small orange uppercase heading "VALIDATION" with small subtitle "Complementary evidence".
Four equal orange-outline cards with NO arrows between them:
header "Automated checks"
body "Files, source mappings"
"Contract–test consistency"
small bottom badge "200 task packages"
header "AI-assisted audit"
body "Review evidence"
"Supports author judgment"
NO count for AI review, do not invent whole-suite AI coverage.
header "Author review"
body "Task and test semantics"
"Taxonomy labels"
small bottom badge "All 200 retained tasks"
header "Reference replay"
body "3 executions per task"
"Source-free feasibility"
small bottom badge "600/600 passing runs"
Join these FOUR validation cards with a simple shared thin bracket underneath; route ONE clean connector from bracket into right release card. Label that connector or bracket "Validation evidence" only if ample space. DO NOT draw arrows between author review and reference replay. This is conceptual assembly, not a strict temporal claim.
A small unobtrusive footer under left bands: "Problematic candidates excluded during construction". No exclusion counts, no seven-task discussion, no claim of zero defects or independent outside reviewers.

RIGHT OUTPUT:
Compact distinct navy-bordered white card with a small minimalist stack-of-documents icon. Header "Frozen release". Large central number/text "200 Python tasks". Two smaller lines "176 source repositories" and "182 pinned snapshots". Thin divider. Small text "Versioned task assets" and "Evaluation policy". No model scores, no 150/50 results split, no hashes or Docker identifiers, no taxonomy heatmap, no chart.

STYLE AND ACCURACY:
Keep blue and orange hierarchy restrained; more whitespace than the reference figure. All content within canvas with consistent margins. Typographic hierarchy: band headings medium, card titles bold, body smaller but readable, key release count largest. Scientific and clean, not marketing. Prefer minimal file/check/terminal icons only if they improve scanability. The orange review band must not be mistaken for a second construction pipeline. Do not add unstated counts (38 or 6), reviewer agreement statistics, or an AI-pass verdict. Spell "FeatureLiftBench" correctly if used. Use only "source repository", never donor.


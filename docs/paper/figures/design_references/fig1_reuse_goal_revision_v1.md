# Fig. 1 — reuse request card revision

Generated with the built-in imagegen tool as a localized image edit.

- Source: C:/Users/CHZ/xwechat_files/wxid_aafmxuwvu58e12_6380/temp/RWTemp/2026-09/9e20f478899dc29eb19741386f9343c8/22ec74ed9439d6cdc76cfe18ea67da67.png
- Output: fig1_reuse_goal_revision_v1.png
- Scope: replace the lower first-column reuse-goal list and separate summary with one card containing a reuse request and two columns of requirements; use a white preview background.
- The remaining panels retain their content. This localized revision does not resolve all wording and diagram issues discussed earlier.
- Visually checked the lower-card text, two-column layout, and alignment.
- Original image and main.tex were not changed.

## Exact prompt

Use case: infographic-diagram; precise local edit of the provided research figure.

Edit the supplied image, preserving its existing three-column structure, blue/orange colors, upper diagrams, numbered headings, and all content in columns 2 and 3. This request is specifically to improve the empty lower-left area. Do NOT redesign the figure or generate a different concept.

BACKGROUND: the source PNG has transparent areas that may display black in a viewer. Render these transparent areas on a pure WHITE background for a readable paper preview. Preserve all opaque fills and all existing text colors. The intended figure is not black-background artwork.

LOCAL EDIT, FIRST COLUMN ONLY:
The current lower first-column "Public reuse goal" card has a narrow left-aligned bullet list and too much unused horizontal space. Beneath it there is a separate repetitive summary card beginning "Useful behavior exists in the repository...".
Replace these TWO lower blocks with ONE well-composed reuse-request card that uses their combined available space, stays entirely within the first column, and ends at the same baseline as the bottom summary cards in columns 2 and 3. Keep the Signal/Namespace diagram and shared state/helpers block above it unchanged. Adjust only the outer source-container bottom border as necessary to neatly separate the upper source diagram from this lower card.

DESIGN OF THE NEW CARD:
Thin blue border, very light blue or white fill, restrained rounded corners consistent with the existing figure.
A bold card heading: "Reuse request"
Below the heading, one full-width sentence:
"Reuse the signal registry in an independent package."

Below that, arrange TWO equal-width text columns with a subtle vertical divider and comfortable inner padding. Keep left and right headings aligned and the three content rows aligned.

Left heading:
"Required behavior"
Three items:
"Sender-specific dispatch"
"Weak-receiver cleanup"
"Stable namespace identity"

Right heading:
"Output requirements"
Three items:
"API under featurelifted"
"Independent execution"
"No runtime import of blinker"

Use monospace for "featurelifted" and "blinker" if it remains readable. Modest bullets are allowed; no large icons. Wrap long items into two lines when necessary, with aligned row spacing. Do NOT shrink the text to tiny size. The goal is balanced use of the horizontal space, not a taller narrow bullet list.

REMOVE the old first-column summary sentence "Useful behavior exists in the repository, but not as a ready-made reusable package." Do not move it elsewhere.

PRESERVE:
- All top headings and explanatory sentences.
- The full upper first-column source diagram, labels, and arrows.
- Every element and wording in columns 2 and 3.
- The full bottom-wide banner and exact scope numbers: 200 tasks, 176 repositories, 182 snapshots.
- Overall landscape aspect ratio close to the original (about 2:1), with no cropped edges.
- The original image's typography and visual hierarchy, with legible body text.

Only the first-column lower-card composition and transparent-background display should change. No new empirical claims, no task-count changes, no model scores. Output the complete edited figure at high resolution.


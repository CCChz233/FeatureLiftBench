"""Fig. 1: task positioning and joint acceptance requirements; no experiments.

Sources: paper/main.tex Introduction, Task Formulation, Related Work.
This is a conceptual illustration, not a measured outcome distribution.
"""
from pathlib import Path
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

OUT = Path(__file__).resolve().parents[1] / "design_references"
W, H = 180, 94
INK, MUTED, RULE = "#202329", "#606670", "#CDD0D5"
ACCENT, TINT = "#633C61", "#F3EDF3"
PALE = "#F6F7F8"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "svg.fonttype": "none",
    "pdf.fonttype": 42, "text.usetex": False,
})
fig = plt.figure(figsize=(W / 25.4, H / 25.4), facecolor="white")
ax = fig.add_axes([0, 0, 1, 1])
ax.set(xlim=(0, W), ylim=(H, 0))
ax.axis("off")
regions = []


def text(x, y, s, size=8.2, color=INK, weight="normal", **kw):
    return ax.text(x, y, s, fontsize=size, color=color, fontweight=weight,
                   va="center", linespacing=1.25, **kw)


def line(x1, y1, x2, y2, color=RULE, lw=.65, **kw):
    ax.plot([x1, x2], [y1, y2], color=color, lw=lw, **kw)


def rect(x, y, w, h, fill="white", edge=RULE, lw=.7):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fill,
                           edgecolor=edge, linewidth=lw))


def arrow(x1, y1, x2, y2, color=INK, lw=.85):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                               mutation_scale=7, linewidth=lw,
                               color=color, shrinkA=0, shrinkB=0))


# Panel A: differences in task objectives, aligned rather than a workflow.
text(2, 5, "(a) What does the task ask an agent to deliver?", 9.5, weight="bold")
text(2, 15, "Task", 8, MUTED, "bold")
text(31, 15, "Available evidence", 8, MUTED, "bold")
text(67, 15, "Deliverable", 8, MUTED, "bold")
line(2, 19, 96, 19, INK, .9)

text(2, 29, "Feature\nimplementation", 8.6, weight="bold")
text(31, 29, "Requirements; target\nimplementation absent", 8.1)
text(67, 29, "New functionality", 8.3, weight="bold")
text(67, 36, "In-place / from scratch", 7.4, MUTED)
line(2, 41, 96, 41)

text(2, 50, "Repository\nmodification", 8.6, weight="bold")
text(31, 50, "Issue + existing\nrepository", 8.1)
rect(67, 45, 28, 11, PALE, RULE, .6)
text(81, 48, "Original project", 7.8, ha="center")
text(81, 53, "+ patch", 7.5, MUTED, ha="center")
text(67, 60, "Evaluate within\nthe revised project", 7.3, MUTED)
line(2, 64, 96, 64)

rect(1, 66, 96, 18.5, TINT, "none", 0)
rect(1, 66, .8, 18.5, ACCENT, "none", 0)
text(3, 71, "Feature lifting", 8.7, ACCENT, "bold")
text(3, 78, "FeatureLiftBench", 7.4, ACCENT)
text(31, 73.2, "Intact source +\noutput contract", 8.5, ACCENT, "bold")
rect(67, 68.5, 28, 11, "white", ACCENT, 1)
text(81, 74, "Independent\npackage", 8.5, ACCENT, "bold", ha="center")
text(31, 81, "Existing implementation supplied", 7.3, ACCENT)

# Panel B: a requirements matrix, NOT causal or empirical outcomes.
text(103, 5, "(b) What counts as successful reuse?", 9.5, weight="bold")
text(149, 15, "Source repository needed at runtime?", 7.9, MUTED, "bold", ha="center")
text(132, 23, "Yes", 8.3, ha="center")
text(162.5, 23, "No", 8.3, ACCENT, "bold", ha="center")

rect(117, 29, 30, 24, PALE, RULE)
rect(147, 29, 31, 24, ACCENT, ACCENT, 1.1)
rect(117, 53, 30, 24, "white", RULE)
rect(147, 53, 31, 24, PALE, RULE)

text(102.5, 53, "Specified behavior", 8.2, MUTED, "bold",
     rotation=90, ha="center")
text(114.3, 41, "Met", 7.8, ha="right")
text(114.3, 65, "Unmet", 7.8, ha="right")

text(132, 37, "Correct behavior,", 8.2, ha="center")
text(132, 42, "source still needed", 8.2, ha="center")
text(132, 48.5, "Imports the original\nsource package", 7.2, MUTED, ha="center")

text(162.5, 37, "Successful", 9.3, "white", "bold", ha="center")
text(162.5, 42, "feature lifting", 9.3, "white", "bold", ha="center")
text(162.5, 48.3, "Both satisfied", 7.4, "white", ha="center")

text(132, 62.5, "Both requirements", 8, MUTED, ha="center")
text(132, 67.5, "unmet", 8, MUTED, ha="center")

text(162.5, 60.5, "Independent,", 8.2, ha="center")
text(162.5, 65.5, "incomplete behavior", 8, ha="center")
text(162.5, 72, "Required cases\nomitted", 7.2, MUTED, ha="center")
text(147.5, 82, "A new package alone is insufficient.", 8.2, ACCENT,
     weight="bold", ha="center")

# Shared interpretation: not a benchmark leaderboard or pipeline.
line(2, 87, 178, 87, INK, .8)
text(90, 91, "Use the original implementation as evidence; preserve its specified behavior beyond the source repository.",
     8.15, INK, ha="center")

OUT.mkdir(parents=True, exist_ok=True)
fig.canvas.draw()
renderer = fig.canvas.get_renderer()
outside = []
for t in ax.texts:
    b = t.get_window_extent(renderer)
    if b.x0 < -.2 or b.y0 < -.2 or b.x1 > fig.bbox.width + .2 or b.y1 > fig.bbox.height + .2:
        outside.append(t.get_text())
if outside:
    raise ValueError(f"Text outside canvas: {outside}")

overlaps = []
for i, a in enumerate(ax.texts):
    ba = a.get_window_extent(renderer)
    for b in ax.texts[i+1:]:
        bb = b.get_window_extent(renderer)
        if min(ba.x1, bb.x1) - max(ba.x0, bb.x0) > .3 and min(ba.y1, bb.y1) - max(ba.y0, bb.y0) > .3:
            overlaps.append([a.get_text(), b.get_text()])
if overlaps:
    raise ValueError(f"Overlapping labels: {overlaps}")

cell_overflows = []
for t in ax.texts:
    x, y = t.get_position()
    if 117 <= x <= 178 and 29 <= y <= 77:
        lo, hi = (117, 147) if x < 147 else (147, 178)
        b = t.get_window_extent(renderer).transformed(ax.transData.inverted())
        if b.x0 < lo + .65 or b.x1 > hi - .65:
            cell_overflows.append(t.get_text())
if cell_overflows:
    raise ValueError(f"Matrix label overflow: {cell_overflows}")

for suffix in ("svg", "pdf", "png"):
    dest = OUT / f"fig1_task_value_v1.{suffix}"
    fig.savefig(dest, dpi=300, facecolor="white")
    print(dest)

validation = {
    "canvas_mm": [W, H], "minimum_text_size_pt": min(t.get_fontsize() for t in ax.texts),
    "main_text_size_pt": "8.1-9.5", "outside_canvas_text": outside,
    "overlapping_labels": overlaps, "matrix_label_overflows": cell_overflows,
    "matrix": "Conceptual joint requirements, not observed outcome frequencies or causal labels.",
    "comparison": "Task families, not an exhaustive partition of benchmarks or difficulty ranking.",
    "evidence": "docs/paper/main.tex Introduction, Task Formulation and Related Work",
    "manuscript_replaced": False, "experiments_run": False,
}
(OUT / "fig1_task_value_v1_validation.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
plt.close(fig)

"""Compare two Fig. 3(a) encodings; PNG preview only, no paper replacement."""
import json
import math
from figure_data import prepare_matplotlib

prepare_matplotlib()
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Patch
from paper_style import FIGURES_DIR, apply_paper_style, save_figure


def main():
    apply_paper_style(10)
    data = json.loads((FIGURES_DIR / "data/figA_task_coverage.json").read_text(encoding="utf-8"))
    families = data["feature_families"]
    assert sum(f["count"] for f in families) == 200
    fig = plt.figure(figsize=(12.6, 4.85))
    ink, muted = "#202B33", "#56616A"
    fig.text(.02, .952, "A  Stacked bars", fontsize=13, weight="bold", color=ink)
    fig.text(.02, .900, "Functional family + lift-type breakdown | 200 tasks", fontsize=10, color=muted)
    fig.text(.505, .952, "B  Donut", fontsize=13, weight="bold", color=ink)
    fig.text(.505, .900, "Functional-family totals | 200 tasks", fontsize=10, color=muted)

    ax = fig.add_axes([.205, .225, .232, .605])
    colors = {"Direct": "#0072B2", "Adapted": "#E69F00", "Composite": "#009E73"}
    y = np.arange(len(families))
    start = np.zeros(len(families))
    for lift, color in colors.items():
        counts = np.array([f["lift_counts"][lift] for f in families])
        ax.barh(y, counts, left=start, height=.7, color=color, edgecolor="white", linewidth=.6)
        start += counts
    for i, family in enumerate(families):
        ax.text(family["count"] + .8, i, str(family["count"]), va="center", fontsize=10)
    ax.set(yticks=y, yticklabels=[f["label"] for f in families],
           xlim=(0, 44), xticks=[0, 10, 20, 30, 40], xlabel="Tasks")
    ax.invert_yaxis()
    ax.tick_params(axis="y", length=0, labelsize=9)
    ax.grid(axis="x", color="#E7ECF0", linewidth=.6)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#A6AFB5")
    fig.legend(handles=[Patch(facecolor=c, label=f'{k} ({data["release_lift_counts"][k]})')
                        for k, c in colors.items()], loc="lower left", bbox_to_anchor=(.043, .097),
               ncol=3, fontsize=9.3, handlelength=1.3, columnspacing=1.5)

    ring = fig.add_axes([.485, .193, .50, .650])
    family_colors = ["#4477AA", "#66A6C2", "#78B7AD", "#6A9B69", "#AEB96B",
                     "#D7B768", "#D39572", "#B88291", "#927FA6", "#929AA3"]
    wedges, _ = ring.pie([f["count"] for f in families], startangle=90, counterclock=False,
                        radius=1, colors=family_colors,
                        wedgeprops={"width": .35, "edgecolor": "white", "linewidth": 1.1})
    ring.text(0, .11, "200", ha="center", va="center", fontsize=30, weight="bold", color=ink)
    ring.text(0, -.15, "tasks", ha="center", va="center", fontsize=11, color=muted)
    ring.text(0, -.34, "10 families", ha="center", va="center", fontsize=8.7, color=muted)
    labels = []
    for wedge, family in zip(wedges, families):
        angle = math.radians((wedge.theta1 + wedge.theta2) / 2)
        x, yy = math.cos(angle), math.sin(angle)
        labels.append({"x": x, "y": yy, "family": family})
    for side in [-1, 1]:
        items = sorted([p for p in labels if (p["x"] < 0) == (side == -1)], key=lambda p: p["y"])
        positions = np.linspace(-1.08, 1.08, len(items))
        for item, yy in zip(items, positions):
            family = item["family"]
            # Labels are printed, not encoded only by ten colors.
            text = family["label"] + f'\n{family["count"]} ({family["count"] / 2:g}%)'
            ring.plot([item["x"] * 1.035, side * 1.12, side * 1.21],
                      [item["y"] * 1.035, yy, yy], color="#AAB3BA", linewidth=.75)
            ring.text(side * 1.26, yy, text, va="center",
                      ha="left" if side > 0 else "right", fontsize=8.5,
                      linespacing=1.35, color=ink)
    ring.set(xlim=(-2.95, 3.18), ylim=(-1.3, 1.3))
    fig.text(.02, .041, "Preserves the cross-classification in each family.", fontsize=10, color=muted)
    fig.text(.505, .128, "Lift types: Direct 68 / Adapted 100 / Composite 32", fontsize=9.4, color=muted)
    fig.text(.505, .041, "Shows overall composition; within-family lift types are omitted.", fontsize=9.5, color=muted)
    for path in save_figure(fig, "fig3_round_comparison", formats=("png",), dpi=240):
        print(path)
    plt.close(fig)


if __name__ == "__main__":
    main()

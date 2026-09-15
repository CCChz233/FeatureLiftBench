"""Appendix Fig. 6: paired artifact differences (stored as fig7.pdf).

Edit this file for this figure's layout, marks, labels, and annotations.
Run directly to update its PDF/PNG, or use --output-dir for a separate preview.
Data preparation is shared in redraw_data.py; styles are in paper_style.py.
"""
from figure_common import BLUE, INK, MUTED, WIDTH, finish, run_single
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

from redraw_data import footprint
from paper_style import BACKEND_FULL_NAMES, panel_label


def draw_footprint():
    data = footprint()
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH, 3.75), sharey=True)
    fig.subplots_adjust(left=.255, right=.978, bottom=.275, top=.810, wspace=.23)
    fig.text(.024, .949, "Paired artifact differences", fontsize=9.4, weight="bold", color=INK)
    fig.text(.024, .886, "Difference = configuration - DeepSeek V4 Pro; common successes within each pair", fontsize=8.5, color=MUTED)
    comparisons = data["comparisons"]
    # Hash-derived vertical offsets are shared across metrics; x stays exact.
    import hashlib
    offsets = {p["task_id"]: ((int(hashlib.sha256(p["task_id"].encode()).hexdigest()[:8], 16) / (2**32 - 1)) - .5) * .36
               for row in comparisons for p in row["points"]}
    for ax, metric, letter, title in zip(axes, ("rres", "copy"), ("a", "b"),
                                        ("Relative size (RRES)", "Source overlap (Copy)")):
        ax.axvline(0, color="#555555", linestyle="--", linewidth=.9, zorder=1)
        for index, row in enumerate(comparisons):
            values = np.array([p[f"delta_{metric}"] for p in row["points"]])
            yy = index + np.array([offsets[p["task_id"]] for p in row["points"]])
            ax.scatter(values, yy, s=12, color=BLUE, alpha=.38, edgecolors="none", zorder=2)
            summary = row["summaries"][metric]
            ax.plot([summary["q1"], summary["q3"]], [index, index], color=INK,
                    linewidth=2.5, solid_capstyle="round", zorder=3)
            ax.scatter([summary["median"]], [index], s=32, marker="D", color="#D58B24",
                       edgecolors=INK, linewidths=.55, zorder=4)
            ax.axhline(index + .5, color="#E9EDF0", linewidth=.5, zorder=0)
        if metric == "rres":
            ax.set_xscale("symlog", linthresh=.1, linscale=1, base=10)
            ax.set_xlim(-50, 50)
            ticks = [-10, -1, -.1, 0, .1, 1, 10]
            ax.set_xticks(ticks, ["−10", "−1", "−0.1", "0", "0.1", "1", "10"])
            ax.set_xlabel("RRES difference (symmetric log)", fontsize=8)
        else:
            ax.set_xlim(-1.035, 1.035)
            ax.set_xticks([-1, -.5, 0, .5, 1], ["−1", "−0.5", "0", "0.5", "1"])
            ax.set_xlabel("Copy difference (linear)", fontsize=8)
        low, high = ax.get_xlim()
        assert all(low <= p[f"delta_{metric}"] <= high for row in comparisons for p in row["points"])
        ax.set_ylim(4.5, -.5)
        ax.tick_params(axis="y", length=0)
        ax.tick_params(axis="x", length=3, labelsize=8)
        ax.spines["bottom"].set_color("#89959D")
        ax.spines["left"].set_visible(False)
        panel_label(ax, letter, title)
    axes[0].set_yticks(range(5), [f'{BACKEND_FULL_NAMES[row["backend"]]}\n(n = {row["common_passing_tasks"]})' for row in comparisons])
    handles = [Line2D([], [], marker="o", color=BLUE, linestyle="none", markersize=4, alpha=.5, label="Matched task"),
               Line2D([], [], marker="D", markerfacecolor="#D58B24", markeredgecolor=INK, markeredgewidth=.55,
                      linestyle="none", markersize=4.5, label="Median"),
               Line2D([], [], color=INK, linewidth=2.5, label="Interquartile range")]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.57, .106), ncol=3, columnspacing=1.6, fontsize=8)
    fig.text(.024, .036, "Negative: smaller artifact / less detected copying than DeepSeek V4 Pro.", fontsize=8, color=INK)
    finish(fig, "fig7")

def main():
    run_single(draw_footprint, __doc__)


if __name__ == "__main__":
    main()

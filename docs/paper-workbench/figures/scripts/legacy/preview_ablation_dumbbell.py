"""Preview: compact dumbbell + forest for the source-evidence ablation.

Does not replace manuscript assets. Pass rates sit on the dumbbell; the forest
shows the paired difference and 95% interval without repeating table statistics.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from figure_data import prepare_matplotlib

prepare_matplotlib()

import paper_style
from figure_common import BLUE, INK
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from paper_inputs import MANIFEST, input_path, read_json

CONTRACT = "#D9E0E5"
CONTRACT_EDGE = "#65727B"
STEM = "#8E9AA3"
GRID = "#E8EDF1"


def load_rows():
    stats = read_json(input_path("source_ablation_statistics"))
    names = {model["id"]: model["display"] for model in MANIFEST["models"]}
    rows = []
    for summary in stats["results"]:
        n = summary["n"]
        rows.append({
            "label": names[summary["model"]],
            "contract": 100.0 * summary["contract_pass"] / n,
            "full": 100.0 * summary["full_pass"] / n,
            "delta": summary["delta_pp"],
            "lo": summary["paired_bootstrap_95ci_pp"][0],
            "hi": summary["paired_bootstrap_95ci_pp"][1],
        })
    return rows


def rate_label(ax, x, y, text, *, color, weight="regular"):
    """Place a pass-rate label beside the marker, or above it near the axis."""
    if x < 18:
        ax.annotate(
            text, xy=(x, y), xytext=(0, 5.5), textcoords="offset points",
            ha="center", va="bottom", fontsize=7.0, color=color, weight=weight,
        )
        return
    ax.annotate(
        text, xy=(x, y), xytext=(-5.5, 0), textcoords="offset points",
        ha="right", va="center", fontsize=7.0, color=color, weight=weight,
    )


def draw(rows):
    paper_style.apply_paper_style(font_size=8)
    fig, (left, right) = plt.subplots(
        1, 2, figsize=(7.05, 1.78), sharey=True,
        gridspec_kw={"width_ratios": (1.22, 1.0), "wspace": 0.10},
    )
    fig.subplots_adjust(left=0.195, right=0.985, bottom=0.34, top=0.97)

    y = list(range(len(rows)))
    for i, row in enumerate(rows):
        left.plot(
            [row["contract"], row["full"]], [i, i],
            color=STEM, linewidth=1.35, solid_capstyle="round", zorder=2,
        )
        left.scatter(
            [row["contract"]], [i], s=28, color=CONTRACT,
            edgecolor=CONTRACT_EDGE, linewidth=0.7, zorder=3,
        )
        left.scatter(
            [row["full"]], [i], s=28, color=BLUE,
            edgecolor=BLUE, linewidth=0.4, zorder=3,
        )
        rate_label(left, row["contract"], i, f"{row['contract']:.1f}%", color=INK)
        left.annotate(
            f"{row['full']:.1f}%", xy=(row["full"], i), xytext=(5.5, 0),
            textcoords="offset points", ha="left", va="center",
            fontsize=7.0, color=BLUE, weight="semibold",
        )

        gain = row["delta"]
        right.errorbar(
            gain, i,
            xerr=[[gain - row["lo"]], [row["hi"] - gain]],
            fmt="D", color=BLUE, markerfacecolor=BLUE, markeredgecolor=BLUE,
            markersize=4.2, linewidth=1.15, capsize=2.4, capthick=0.9, zorder=3,
        )

    left.set(
        yticks=y, yticklabels=[row["label"] for row in rows],
        ylim=(len(rows) - 0.42, -0.72),
        xlim=(0, 100), xticks=[0, 25, 50, 75, 100],
        xlabel="Functional pass (%)",
    )
    right.set(
        xlim=(0, 75), xticks=[0, 25, 50, 75],
        xlabel="Full source − Contract only (pp)",
    )
    right.axvline(0, color="#A2ACB4", linestyle="--", linewidth=0.7, zorder=1)

    for ax in (left, right):
        ax.tick_params(axis="y", length=0, pad=4, labelsize=7.4)
        ax.tick_params(axis="x", length=2.6, labelsize=7.1)
        ax.xaxis.label.set_size(7.4)
        ax.xaxis.labelpad = 2
        ax.set_axisbelow(True)
        ax.grid(axis="x", color=GRID, linewidth=0.5)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_color("#8E9AA3")
        ax.spines["bottom"].set_linewidth(0.7)
    right.tick_params(axis="y", left=False, labelleft=False)

    handles = [
        Line2D([], [], marker="o", markersize=5.2, markerfacecolor=CONTRACT,
               markeredgecolor=CONTRACT_EDGE, markeredgewidth=0.7,
               linestyle="none", label="Contract only"),
        Line2D([], [], marker="o", markersize=5.2, markerfacecolor=BLUE,
               markeredgecolor=BLUE, markeredgewidth=0.4,
               linestyle="none", label="Full source"),
    ]
    fig.legend(
        handles=handles, loc="lower center", bbox_to_anchor=(0.46, 0.012),
        ncol=2, frameon=False, fontsize=7.0,
        handletextpad=0.35, columnspacing=1.2, borderaxespad=0,
    )
    return fig


def main():
    destination = Path(__file__).resolve().parents[1] / "output" / "ablation_dumbbell_preview"
    destination.mkdir(parents=True, exist_ok=True)
    fig = draw(load_rows())
    for fmt in ("pdf", "png"):
        path = destination / f"fig_ablation_compact.{fmt}"
        fig.savefig(path, format=fmt, dpi=300)
        print(path)
    plt.close(fig)


if __name__ == "__main__":
    main()

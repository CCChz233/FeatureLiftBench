"""Fig. 4: repository-evidence utilization on the common 40-task subset.

Produces three compact panels sized for one manuscript row:

    fig04a_ablation_pass_rate.pdf/png
        Functional pass rates under Contract Only versus Full Source.

    fig04b_ablation_paired_gain.pdf/png
        Paired pass-rate gain with 95% bootstrap confidence intervals.

    fig04c_dse_comparison.pdf/png
        Diagnostic mechanical-relocation comparison.

Panel titles belong in the LaTeX caption.

Data preparation is shared in redraw_data.py.
"""

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D

from figure_common import BLUE, INK, finish, run_single
from redraw_data import source_ablation


PANEL = dict(
    figsize=(2.28, 1.86),
    left=0.22,
    right=0.94,
    bottom=0.30,
    top=0.97,
)


# ===========================================================================
# Shared data
# ===========================================================================

def load_data():
    data = source_ablation()

    from paper_inputs import MANIFEST

    names = {
        model["id"]: model["short"]
        for model in MANIFEST["models"]
    }

    return data, names


def model_labels(data, names):

    return [names[row["model"]] for row in data["results"]]


# ===========================================================================
# Fig. 4(a): grouped horizontal bars
# ===========================================================================

def draw_pass_rate(data, names):

    rows = data["results"]
    labels = model_labels(data, names)

    fig, ax = plt.subplots(figsize=PANEL["figsize"])

    fig.subplots_adjust(
        left=PANEL["left"],
        right=PANEL["right"],
        bottom=PANEL["bottom"],
        top=PANEL["top"],
    )

    y = np.arange(len(rows))

    bar_height = 0.24
    offset = 0.15

    spec_color = "#D9E0E5"
    spec_edge = "#65727B"

    full_color = BLUE

    for i, row in enumerate(rows):

        spec = 100.0 * row["contract_pass"] / row["n"]
        full = 100.0 * row["full_pass"] / row["n"]

        # Contract-only arm.
        ax.barh(
            y[i] + offset,
            spec,
            height=bar_height,
            color=spec_color,
            edgecolor=spec_edge,
            linewidth=0.65,
            zorder=3,
        )

        # Full-source arm.
        ax.barh(
            y[i] - offset,
            full,
            height=bar_height,
            color=full_color,
            edgecolor="white",
            linewidth=0.55,
            zorder=3,
        )

        ax.text(
            spec + 1.5,
            y[i] + offset,
            f"{spec:.1f}%",
            ha="left",
            va="center",
            fontsize=6.8,
            color=INK,
        )

        ax.text(
            full + 1.5,
            y[i] - offset,
            f"{full:.1f}%",
            ha="left",
            va="center",
            fontsize=6.8,
            color=full_color,
            weight="semibold",
        )


    ax.set(
        yticks=y,
        yticklabels=labels,
        ylim=(len(rows) - 0.48, -0.48),
        xlim=(0, 100),
        xticks=[0, 25, 50, 75, 100],
        xlabel="Functional pass (%)",
    )

    ax.tick_params(
        axis="y",
        length=0,
        pad=3,
        labelsize=7.0,
    )

    ax.tick_params(
        axis="x",
        length=3,
        labelsize=6.8,
    )

    ax.xaxis.label.set_size(7.0)
    ax.xaxis.labelpad = 2


    ax.set_axisbelow(True)

    ax.grid(
        axis="x",
        color="#E8EDF1",
        linewidth=0.5,
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    ax.spines["bottom"].set_color("#8E9AA3")
    ax.spines["bottom"].set_linewidth(0.7)


    handles = [
        Line2D(
            [],
            [],
            marker="s",
            markersize=5.4,
            markerfacecolor=spec_color,
            markeredgecolor=spec_edge,
            markeredgewidth=0.7,
            linestyle="none",
            label="Contract only",
        ),
        Line2D(
            [],
            [],
            marker="s",
            markersize=5.4,
            markerfacecolor=full_color,
            markeredgecolor="white",
            markeredgewidth=0.5,
            linestyle="none",
            label="Full source",
        ),
    ]

    fig.legend(
        handles=handles,
        loc="lower center",
        bbox_to_anchor=(0.52, 0.015),
        ncol=2,
        frameon=False,
        fontsize=6.0,
        handletextpad=0.25,
        columnspacing=0.65,
        borderaxespad=0,
    )

    finish(fig, "fig04a_ablation_pass_rate")


# ===========================================================================
# Fig. 4(b): paired gain with 95% CI
# ===========================================================================

def draw_paired_gain(data, names):

    rows = data["results"]
    labels = model_labels(data, names)

    fig, ax = plt.subplots(figsize=PANEL["figsize"])

    fig.subplots_adjust(
        left=PANEL["left"],
        right=PANEL["right"],
        bottom=PANEL["bottom"],
        top=PANEL["top"],
    )

    y = np.arange(len(rows))


    for i, row in enumerate(rows):

        lo, hi = row["paired_bootstrap_95ci_pp"]
        gain = row["delta_pp"]

        ax.errorbar(
            gain,
            y[i],
            xerr=[
                [gain - lo],
                [hi - gain],
            ],
            fmt="D",
            color=BLUE,
            markerfacecolor=BLUE,
            markeredgecolor=BLUE,
            markersize=4.5,
            linewidth=1.3,
            capsize=3.0,
            capthick=1.0,
            zorder=4,
        )

        ax.text(
            gain,
            y[i] - 0.20,
            f"+{gain:.1f} pp",
            ha="center",
            va="center",
            fontsize=6.9,
            weight="semibold",
            color=INK,
        )


    ax.set(
        yticks=y,
        yticklabels=labels,
        ylim=(len(rows) - 0.48, -0.48),
        xlim=(0, 75),
        xticks=[0, 25, 50, 75],
        xlabel="Full source gain (pp)",
    )


    ax.tick_params(
        axis="y",
        length=0,
        pad=3,
        labelsize=7.0,
    )

    ax.tick_params(
        axis="x",
        length=3,
        labelsize=6.8,
    )

    ax.xaxis.label.set_size(7.0)
    ax.xaxis.labelpad = 2


    ax.axvline(
        0,
        color="#A2ACB4",
        linestyle="--",
        linewidth=0.7,
        zorder=1,
    )


    ax.set_axisbelow(True)

    ax.grid(
        axis="x",
        color="#E8EDF1",
        linewidth=0.5,
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    ax.spines["bottom"].set_color("#8E9AA3")
    ax.spines["bottom"].set_linewidth(0.7)


    finish(fig, "fig04b_ablation_paired_gain")


# ===========================================================================
# Generate all three panels in the latest PDF
# ===========================================================================

def draw_all():

    data, names = load_data()

    draw_pass_rate(data, names)

    draw_paired_gain(data, names)
    from fig04c_mechanical_relocation import draw_dse_comparison
    draw_dse_comparison(data)


def main():

    run_single(draw_all, __doc__)


if __name__ == "__main__":
    main()

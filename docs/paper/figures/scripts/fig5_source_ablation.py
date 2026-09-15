"""Fig. 5: paired source-evidence ablation on 40 tasks.

Produces two independent panels:

    fig5a_pass_rate.pdf/png
        Functional pass rates under Contract only versus
        Full source + contract.

    fig5b_paired_gain.pdf/png
        Paired pass-rate gain with 95% bootstrap confidence intervals.

Panel titles and the Pro timeout marker are included in the exported figures.

Data preparation is shared in redraw_data.py.
"""

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D

from figure_common import BLUE, INK, finish, run_single
from redraw_data import source_ablation


# ===========================================================================
# Shared data
# ===========================================================================

def load_data():
    data = source_ablation()

    from paper_inputs import MANIFEST

    names = {
        model["id"]: model["display"]
        for model in MANIFEST["models"]
    }

    return data, names


def model_labels(data, names):
    labels = []

    for row in data["results"]:
        label = names[row["model"]]

        if row["model"] == "deepseek-v4-pro":
            label += r" $\dagger$"

        labels.append(label)

    return labels


# ===========================================================================
# Fig. 5(a): grouped horizontal bars
# ===========================================================================

def draw_pass_rate(data, names):
    rows = data["results"]
    labels = model_labels(data, names)

    # Normal aspect ratio; compactness comes from removing unused margins,
    # not from vertically squashing the figure.
    fig, ax = plt.subplots(figsize=(4.70, 2.20))

    fig.subplots_adjust(
        left=0.39,
        right=0.96,
        bottom=0.29,
        top=0.83,
    )

    y = np.arange(len(rows))

    bar_height = 0.24
    offset = 0.15

    # Restrained neutral vs primary accent.
    contract_color = "#D9E0E5"
    contract_edge = "#65727B"
    full_color = BLUE

    for i, row in enumerate(rows):
        contract = 100.0 * row["contract_pass"] / row["n"]
        full = 100.0 * row["full_pass"] / row["n"]

        # Contract-only bar above the group center.
        ax.barh(
            y[i] + offset,
            contract,
            height=bar_height,
            color=contract_color,
            edgecolor=contract_edge,
            linewidth=0.65,
            zorder=3,
        )

        # Full-source bar below the group center.
        ax.barh(
            y[i] - offset,
            full,
            height=bar_height,
            color=full_color,
            edgecolor="white",
            linewidth=0.55,
            zorder=3,
        )

        # Exact values at the ends of bars.
        ax.text(
            contract + 1.5,
            y[i] + offset,
            f"{contract:.1f}%",
            ha="left",
            va="center",
            fontsize=7.2,
            color=INK,
        )

        ax.text(
            full + 1.5,
            y[i] - offset,
            f"{full:.1f}%",
            ha="left",
            va="center",
            fontsize=7.2,
            color=full_color,
            weight="semibold",
        )

    # ------------------------------------------------------------------
    # Axes
    # ------------------------------------------------------------------

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
        pad=6,
        labelsize=7.5,
    )

    ax.tick_params(
        axis="x",
        length=3,
        labelsize=7.1,
    )

    ax.xaxis.label.set_size(7.5)
    ax.xaxis.labelpad = 2

    # ------------------------------------------------------------------
    # Styling
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Legend
    # ------------------------------------------------------------------

    handles = [
        Line2D(
            [],
            [],
            marker="s",
            markersize=5.4,
            markerfacecolor=contract_color,
            markeredgecolor=contract_edge,
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
            label="Full source + contract",
        ),
    ]

    fig.legend(
        handles=handles,
        loc="lower center",
        bbox_to_anchor=(0.65, 0.035),
        ncol=2,
        frameon=False,
        fontsize=6.9,
        handletextpad=0.4,
        columnspacing=1.15,
        borderaxespad=0,
    )

    fig.text(0.03, 0.93, "(a) Functional pass rate", weight="bold", fontsize=9)
    finish(fig, "fig5a_pass_rate")


# ===========================================================================
# Fig. 5(b): paired gain with 95% CI
# ===========================================================================

def draw_paired_gain(data, names):
    rows = data["results"]
    labels = model_labels(data, names)

    fig, ax = plt.subplots(figsize=(4.70, 2.20))

    fig.subplots_adjust(
        left=0.39,
        right=0.96,
        bottom=0.22,
        top=0.83,
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
            fontsize=7.3,
            weight="semibold",
            color=INK,
        )

    # ------------------------------------------------------------------
    # Axes
    # ------------------------------------------------------------------

    ax.set(
        yticks=y,
        yticklabels=labels,
        ylim=(len(rows) - 0.48, -0.48),
        xlim=(0, 75),
        xticks=[0, 25, 50, 75],
        xlabel="Full source − Contract only (pp)",
    )

    ax.tick_params(
        axis="y",
        length=0,
        pad=6,
        labelsize=7.5,
    )

    ax.tick_params(
        axis="x",
        length=3,
        labelsize=7.1,
    )

    ax.xaxis.label.set_size(7.5)
    ax.xaxis.labelpad = 2

    # Zero-effect reference.
    ax.axvline(
        0,
        color="#A2ACB4",
        linestyle="--",
        linewidth=0.7,
        zorder=1,
    )

    # ------------------------------------------------------------------
    # Styling
    # ------------------------------------------------------------------

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

    fig.text(0.03, 0.93, "(b) Paired gain", weight="bold", fontsize=9)
    finish(fig, "fig5b_paired_gain")


# ===========================================================================
# Generate both panels
# ===========================================================================

def draw_all():
    data, names = load_data()

    draw_pass_rate(data, names)
    draw_paired_gain(data, names)


def main():
    run_single(draw_all, __doc__)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Render Figure 4 panels for the repository-evidence analysis."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")

from matplotlib import pyplot as plt
from matplotlib.lines import Line2D


# ============================================================================
# Style
# ============================================================================

BLUE = "#0072B2"
INK = "#202B33"
MUTED = "#56616A"
WIDTH = 7.2

matplotlib.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 9,
    "axes.labelsize": 9,
    "axes.titlesize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.8,
    "axes.axisbelow": True,
    "axes.grid": False,
    "lines.linewidth": 1.2,
    "lines.markersize": 4,
    "legend.frameon": False,
    "text.usetex": False,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "savefig.transparent": False,
})


PANEL = dict(
    figsize=(2.28, 1.86),
    left=0.22,
    right=0.94,
    bottom=0.30,
    top=0.97,
)


# ============================================================================
# Data
# ============================================================================

ABLATION_DATA = [
    {
        "label": "Luna",
        "n": 150,
        "full_pass": 102,
        "contract_pass": 54,
        "delta_pp": 32.0,
        "ci": [22.7, 41.3],
    },
    {
        "label": "Pro",
        "n": 150,
        "full_pass": 115,
        "contract_pass": 31,
        "delta_pp": 56.0,
        "ci": [47.3, 64.7],
    },
    {
        "label": "Qwen",
        "n": 150,
        "full_pass": 63,
        "contract_pass": 7,
        "delta_pp": 37.3,
        "ci": [28.7, 46.0],
    },
]


DSE_DATA = [
    {
        "label": "All",
        "pass_n": 31,
        "total_n": 150,
        "rate": 20.7,
    },
    {
        "label": "Direct",
        "pass_n": 22,
        "total_n": 56,
        "rate": 39.3,
    },
    {
        "label": "Adapted",
        "pass_n": 9,
        "total_n": 76,
        "rate": 11.8,
    },
    {
        "label": "Composite",
        "pass_n": 0,
        "total_n": 18,
        "rate": 0.0,
    },
]


# ============================================================================
# Helpers
# ============================================================================

def finish(fig, name):
    for ext in ("pdf", "png"):
        path = OUTPUT_DIR / f"{name}.{ext}"
        fig.savefig(
            path,
            format=ext,
            dpi=300,
            bbox_inches=None,
        )
        print(path)

    plt.close(fig)


def style_axis(ax):
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


# ============================================================================
# Panel (a): Full Source vs Contract Only
# ============================================================================

def draw_pass_rate():

    rows = ABLATION_DATA
    labels = [row["label"] for row in rows]

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

    contract_color = "#D9E0E5"
    contract_edge = "#65727B"
    full_color = BLUE

    for i, row in enumerate(rows):

        contract = 100.0 * row["contract_pass"] / row["n"]
        full = 100.0 * row["full_pass"] / row["n"]

        ax.barh(
            y[i] + offset,
            contract,
            height=bar_height,
            color=contract_color,
            edgecolor=contract_edge,
            linewidth=0.65,
            zorder=3,
        )

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
            contract + 1.5,
            y[i] + offset,
            f"{contract:.1f}%",
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

    style_axis(ax)

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

    finish(
        fig,
        "fig04a_ablation_pass_rate",
    )


# ============================================================================
# Panel (b): Paired Full Source gain
# ============================================================================

def draw_paired_gain():

    rows = ABLATION_DATA
    labels = [row["label"] for row in rows]

    fig, ax = plt.subplots(figsize=PANEL["figsize"])

    fig.subplots_adjust(
        left=PANEL["left"],
        right=PANEL["right"],
        bottom=PANEL["bottom"],
        top=PANEL["top"],
    )

    y = np.arange(len(rows))

    for i, row in enumerate(rows):

        lo, hi = row["ci"]
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

    ax.axvline(
        0,
        color="#A2ACB4",
        linestyle="--",
        linewidth=0.7,
        zorder=1,
    )

    style_axis(ax)

    finish(
        fig,
        "fig04b_ablation_paired_gain",
    )


# ============================================================================
# Panel (c): DSE overall and by lift type
# ============================================================================

def draw_dse_by_lift_type():

    rows = DSE_DATA

    fig, ax = plt.subplots(
        figsize=PANEL["figsize"]
    )

    fig.subplots_adjust(
        left=0.33,
        right=PANEL["right"],
        bottom=PANEL["bottom"],
        top=PANEL["top"],
    )

    y = np.arange(len(rows))

    relocation_color = "#B9C4CC"
    relocation_edge = "#56636C"

    bar_height = 0.52

    for i, row in enumerate(rows):

        ax.barh(
            y[i],
            row["rate"],
            height=bar_height,
            color=relocation_color,
            edgecolor=relocation_edge,
            linewidth=0.65,
            zorder=3,
        )

        text_x = row["rate"] + 1.1

        if row["rate"] == 0:
            text_x = 1.1

        ax.text(
            text_x,
            y[i],
            f'{row["pass_n"]}/{row["total_n"]}',
            ha="left",
            va="center",
            fontsize=6.7,
            color=INK,
        )

    ax.set(
        yticks=y,
        yticklabels=[row["label"] for row in rows],
        ylim=(len(rows) - 0.48, -0.48),
        xlim=(0, 50),
        xticks=[0, 25, 50],
        xlabel="Functional pass (%)",
    )

    style_axis(ax)

    finish(
        fig,
        "fig04c_dse_comparison",
    )


# ============================================================================
# Main
# ============================================================================

def main():

    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "output",
    )

    args = parser.parse_args()

    global OUTPUT_DIR

    OUTPUT_DIR = args.output_dir.expanduser().resolve()
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    draw_pass_rate()
    draw_paired_gain()
    draw_dse_by_lift_type()


if __name__ == "__main__":
    main()
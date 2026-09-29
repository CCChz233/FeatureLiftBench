#!/usr/bin/env python3
"""Standalone renderer for one current-paper figure. Run --help for output options."""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt

BLUE = "#0072B2"
INK = "#202B33"
MUTED = "#56616A"
WIDTH = 7.2

matplotlib.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 9, "axes.labelsize": 9, "axes.titlesize": 9,
    "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8,
    "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.8,
    "axes.axisbelow": True, "axes.grid": False,
    "lines.linewidth": 1.2, "lines.markersize": 4, "legend.frameon": False,
    "text.usetex": False, "pdf.fonttype": 42, "ps.fonttype": 42,
    "svg.fonttype": "none", "figure.facecolor": "white",
    "savefig.facecolor": "white", "savefig.transparent": False,
})

PANEL = dict(
    figsize=(2.28, 1.86),
    left=0.31,
    right=0.94,
    bottom=0.30,
    top=0.97,
)

DATA = [
  {
    "label": "Luna CO",
    "pass_n": 9,
    "rate": 22.5,
    "style": "spec"
  },
  {
    "label": "Relocation",
    "pass_n": 10,
    "rate": 25.0,
    "style": "relocation"
  },
  {
    "label": "Luna",
    "pass_n": 23,
    "rate": 57.5,
    "style": "agent"
  },
  {
    "label": "Pro",
    "pass_n": 25,
    "rate": 62.5,
    "style": "agent"
  },
  {
    "label": "Qwen",
    "pass_n": 12,
    "rate": 30.0,
    "style": "agent"
  }
]

def finish(fig, name):
    for ext in ("pdf", "png"):
        path = OUTPUT_DIR / f"{name}.{ext}"
        fig.savefig(path, format=ext, dpi=300, bbox_inches=None)
        print(path)
    plt.close(fig)


def draw_dse_comparison(ablation=None):

    rows = DATA

    fig, ax = plt.subplots(
        figsize=PANEL["figsize"]
    )

    fig.subplots_adjust(
        left=PANEL["left"],
        right=PANEL["right"],
        bottom=PANEL["bottom"],
        top=PANEL["top"],
    )


    # Important:
    # matplotlib barh places larger y values higher.
    # Combined with invert_yaxis(), this gives:
    #
    # Luna Contract Only
    # Relocation
    #
    # Luna
    # Pro
    # Qwen

    y = np.array([
        3.30,
        2.65,
        1.55,
        0.90,
        0.25,
    ])


    # Colors

    spec_color = "#D9E0E5"
    spec_edge = "#65727B"

    relocation_color = "#B9C4CC"
    relocation_edge = "#56636C"

    agent_color = BLUE
    agent_edge = "white"


    bar_height = 0.40


    for yi, row in zip(y, rows):

        if row["style"] == "spec":

            color = spec_color
            edge = spec_edge
            text_color = INK
            weight = None


        elif row["style"] == "relocation":

            color = relocation_color
            edge = relocation_edge
            text_color = INK
            weight = None


        else:

            color = agent_color
            edge = agent_edge
            text_color = agent_color
            weight = "semibold"


        ax.barh(
            yi,
            row["rate"],
            height=bar_height,
            color=color,
            edgecolor=edge,
            linewidth=0.65,
            zorder=3,
        )


        ax.text(
            row["rate"] - 1.1 if row["style"] == "agent" else row["rate"] + 1.1,
            yi,
            f'{row["pass_n"]}/40',
            ha="right" if row["style"] == "agent" else "left",
            va="center",
            fontsize=6.7,
            color="white" if row["style"] == "agent" else text_color,
            weight=weight,
        )


    # ===========================================================================
    # Axes
    # ===========================================================================

    ax.set(
        yticks=y,
        yticklabels=[row["label"] for row in rows],
        ylim=(3.70, -0.10),
        xlim=(0, 100),
        xticks=[0, 25, 50, 75, 100],
        xlabel="Functional pass (%)",
    )

    # Critical for desired ordering
    ax.invert_yaxis()


    ax.tick_params(
        axis="y",
        length=0,
        pad=3,
        labelsize=6.8,
    )


    ax.tick_params(
        axis="x",
        length=3,
        labelsize=6.8,
    )


    ax.xaxis.label.set_size(7.0)
    ax.xaxis.labelpad = 2


    # ===========================================================================
    # Styling
    # ===========================================================================

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


    finish(
        fig,
        "fig04c_dse_comparison"
    )

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "output")
    args = parser.parse_args()
    global OUTPUT_DIR
    OUTPUT_DIR = args.output_dir.expanduser().resolve()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    draw_dse_comparison()

if __name__ == "__main__":
    main()

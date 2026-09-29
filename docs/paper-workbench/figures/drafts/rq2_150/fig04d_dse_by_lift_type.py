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
    left=0.33,
    right=0.94,
    bottom=0.30,
    top=0.97,
)

DATA = [
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
    }
]


def finish(fig, name):
    for ext in ("pdf", "png"):
        path = OUTPUT_DIR / f"{name}.{ext}"
        fig.savefig(path, format=ext, dpi=300, bbox_inches=None)
        print(path)
    plt.close(fig)


def draw_dse_by_lift_type():
    rows = DATA

    fig, ax = plt.subplots(figsize=PANEL["figsize"])

    fig.subplots_adjust(
        left=PANEL["left"],
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

        text_x = row["rate"] + 1.1 if row["rate"] > 0 else 1.1
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

    finish(fig, "fig04d_dse_by_lift_type")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "output")
    args = parser.parse_args()
    global OUTPUT_DIR
    OUTPUT_DIR = args.output_dir.expanduser().resolve()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    draw_dse_by_lift_type()


if __name__ == "__main__":
    main()
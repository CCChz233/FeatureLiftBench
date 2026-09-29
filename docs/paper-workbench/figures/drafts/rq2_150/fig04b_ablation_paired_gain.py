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

from matplotlib.lines import Line2D

PANEL = dict(
    figsize=(2.28, 1.86),
    left=0.22,
    right=0.94,
    bottom=0.30,
    top=0.97,
)

DATA = {
  "results": [
    {
      "model": "gpt-5.6-luna",
      "n": 150,
      "full_pass": 102,
      "contract_pass": 54,
      "full_only": 56,
      "contract_only": 8,
      "delta_pp": 32.0,
      "paired_bootstrap_95ci_pp": [
        22.7,
        41.3
      ]
    },
    {
      "model": "deepseek-v4-pro",
      "n": 150,
      "full_pass": 115,
      "contract_pass": 31,
      "full_only": 88,
      "contract_only": 4,
      "delta_pp": 56.0,
      "paired_bootstrap_95ci_pp": [
        47.3,
        64.7
      ]
    },
    {
      "model": "qwen3.6-35b-a3b-fp8",
      "n": 150,
      "full_pass": 63,
      "contract_pass": 7,
      "full_only": 59,
      "contract_only": 3,
      "delta_pp": 37.3,
      "paired_bootstrap_95ci_pp": [
        28.7,
        46.0
      ]
    }
  ]
}

NAMES = {
  "deepseek-v4-pro": "Pro",
  "deepseek-v4-flash": "Flash",
  "gpt-5.6-luna": "Luna",
  "glm-5.3-flash": "GLM",
  "qwen3.6-35b-a3b-fp8": "Qwen",
  "gpt-oss-120b": "OSS"
}

def finish(fig, name):
    for ext in ("pdf", "png"):
        path = OUTPUT_DIR / f"{name}.{ext}"
        fig.savefig(path, format=ext, dpi=300, bbox_inches=None)
        print(path)
    plt.close(fig)


def model_labels(data, names):

    return [names[row["model"]] for row in data["results"]]

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

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "output")
    args = parser.parse_args()
    global OUTPUT_DIR
    OUTPUT_DIR = args.output_dir.expanduser().resolve()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    draw_paired_gain(DATA, NAMES)

if __name__ == "__main__":
    main()

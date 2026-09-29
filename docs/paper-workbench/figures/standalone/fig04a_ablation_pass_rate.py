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
      "n": 40,
      "full_pass": 23,
      "contract_pass": 9,
      "full_only": 17,
      "contract_only": 3,
      "delta_pp": 35.0,
      "paired_bootstrap_95ci_pp": [
        15.0,
        55.00000000000001
      ]
    },
    {
      "model": "deepseek-v4-pro",
      "n": 40,
      "full_pass": 25,
      "contract_pass": 6,
      "full_only": 20,
      "contract_only": 1,
      "delta_pp": 47.5,
      "paired_bootstrap_95ci_pp": [
        30.0,
        65.0
      ]
    },
    {
      "model": "qwen3.6-35b-a3b-fp8",
      "n": 40,
      "full_pass": 12,
      "contract_pass": 1,
      "full_only": 12,
      "contract_only": 1,
      "delta_pp": 27.500000000000004,
      "paired_bootstrap_95ci_pp": [
        12.5,
        42.5
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

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "output")
    args = parser.parse_args()
    global OUTPUT_DIR
    OUTPUT_DIR = args.output_dir.expanduser().resolve()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    draw_pass_rate(DATA, NAMES)

if __name__ == "__main__":
    main()

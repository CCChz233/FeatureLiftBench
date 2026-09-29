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

from matplotlib.ticker import FixedLocator, FixedFormatter, NullLocator

PANEL = dict(figsize=(3.50, 2.55), left=0.22, right=0.98, bottom=0.16, top=0.97)

ROWS = [
  {
    "short": "Pro",
    "copy_pp": 15.424735977856265,
    "copy_pp_ci": [
      12.353098836416807,
      18.56076218140069
    ]
  },
  {
    "short": "Flash",
    "copy_pp": 16.808294503911522,
    "copy_pp_ci": [
      13.606367673717083,
      20.166303056840437
    ]
  },
  {
    "short": "Luna",
    "copy_pp": -20.637263889275452,
    "copy_pp_ci": [
      -26.070567719491393,
      -15.276404468979052
    ]
  },
  {
    "short": "GLM",
    "copy_pp": 14.19746173406258,
    "copy_pp_ci": [
      10.565707090861295,
      17.729591219245027
    ]
  },
  {
    "short": "Qwen",
    "copy_pp": -1.7949500071363373,
    "copy_pp_ci": [
      -5.892978507430624,
      2.4496789765574687
    ]
  },
  {
    "short": "OSS",
    "copy_pp": -23.998278319418574,
    "copy_pp_ci": [
      -31.395282294967004,
      -17.027793967779832
    ]
  }
]

def finish(fig, name):
    for ext in ("pdf", "png"):
        path = OUTPUT_DIR / f"{name}.{ext}"
        fig.savefig(path, format=ext, dpi=300, bbox_inches=None)
        print(path)
    plt.close(fig)


def _draw_panel(rows, *, metric, center, limits, ticks, labels, ylabel, name):
    fig, ax = plt.subplots(figsize=PANEL["figsize"])
    fig.subplots_adjust(
        left=PANEL["left"],
        right=PANEL["right"],
        bottom=PANEL["bottom"],
        top=PANEL["top"],
    )
    positions = np.arange(6)
    estimates = np.array([r[metric] for r in rows])
    bounds = np.array([r[metric + "_ci"] for r in rows])
    assert bounds.min() > limits[0] and bounds.max() < limits[1]
    ax.axhline(center, color="#87939D", lw=.9, ls=(0, (3, 3)), zorder=4)
    ax.bar(positions, estimates, width=.56, bottom=0, color=BLUE,
           edgecolor="none", zorder=2)
    ax.vlines(positions, bounds[:, 0], bounds[:, 1], color=INK, lw=1, zorder=5)
    for end in (0, 1):
        ax.plot(positions, bounds[:, end], linestyle="none", marker="_",
                markersize=6, markeredgewidth=1, color=INK, zorder=5)
    ax.set_ylim(limits)
    ax.set_xlim(-.55, 5.55)
    ax.yaxis.set_major_locator(FixedLocator(ticks))
    ax.yaxis.set_major_formatter(FixedFormatter(labels))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.set_xticks(positions, [r["short"] for r in rows])
    ax.set_ylabel(ylabel, fontsize=8, labelpad=7)
    ax.tick_params(axis="y", labelsize=8, length=3, color="#89959D")
    ax.tick_params(axis="x", labelsize=8, length=0, pad=8)
    ax.set_axisbelow(True)
    ax.grid(axis="y", color="#EEF0F2", linewidth=.5)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#89959D")
    ax.spines["bottom"].set_linewidth(.7)
    ax.spines["left"].set_color("#89959D")
    ax.spines["left"].set_linewidth(.7)
    finish(fig, name)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "output")
    args = parser.parse_args()
    global OUTPUT_DIR
    OUTPUT_DIR = args.output_dir.expanduser().resolve()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _draw_panel(ROWS, metric="copy_pp", center=0, limits=(-40, 40), ticks=[-40, -20, 0, 20, 40], labels=['−40', '−20', '0', '+20', '+40'], ylabel='Copy vs. center (pp)', name="fig08b_copy")

if __name__ == "__main__":
    main()

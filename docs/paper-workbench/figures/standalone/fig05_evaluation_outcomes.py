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

from matplotlib.patches import Patch
from matplotlib.colors import to_rgb
BACKEND_ORDER = ('Pro', 'Flash', 'Luna', 'GLM', 'Qwen', 'OSS')
BACKEND_FULL_NAMES = {'Pro': 'DeepSeek V4 Pro', 'Flash': 'DeepSeek V4 Flash', 'Luna': 'GPT-5.6 Luna', 'GLM': 'GLM-5.3-Flash', 'Qwen': 'Qwen3.6-35B-A3B', 'OSS': 'GPT-OSS 120B'}
STAGE_ORDER = ('Pass', 'Missing', 'Build', 'Public', 'Hidden', 'Isolation')
STAGE_COLORS = {'Pass': '#009E73', 'Missing': '#BDBDBD', 'Build': '#CC79A7', 'Public': '#56B4E9', 'Hidden': '#E69F00', 'Isolation': '#444444'}
STAGE_HATCHES = {'Pass': '', 'Missing': '//', 'Build': 'xx', 'Public': '', 'Hidden': '..', 'Isolation': '\\\\'}
DISPLAY_LABELS = {'Pass': 'Pass', 'Missing': 'No submission', 'Build': 'Build', 'Public': 'Primary', 'Hidden': 'Extended', 'Isolation': 'Isolation'}

BOUNDARY_COLORS = dict(STAGE_COLORS, Missing='#D1D5D9', Build='#7D8791',
                       Public='#78B4D6', Hidden='#176C9E', Isolation='#C77818')

DATA = {
  "first_outcomes": [
    {
      "backend": "Pro",
      "assigned": 150,
      "counts": [
        115,
        0,
        0,
        25,
        10,
        0
      ]
    },
    {
      "backend": "Flash",
      "assigned": 150,
      "counts": [
        108,
        0,
        0,
        26,
        15,
        1
      ]
    },
    {
      "backend": "Luna",
      "assigned": 150,
      "counts": [
        102,
        6,
        3,
        27,
        12,
        0
      ]
    },
    {
      "backend": "GLM",
      "assigned": 150,
      "counts": [
        68,
        38,
        3,
        31,
        8,
        2
      ]
    },
    {
      "backend": "Qwen",
      "assigned": 150,
      "counts": [
        63,
        25,
        6,
        35,
        21,
        0
      ]
    },
    {
      "backend": "OSS",
      "assigned": 150,
      "counts": [
        36,
        2,
        18,
        70,
        23,
        1
      ]
    }
  ]
}

def finish(fig, name):
    for ext in ("pdf", "png"):
        path = OUTPUT_DIR / f"{name}.{ext}"
        fig.savefig(path, format=ext, dpi=300, bbox_inches=None)
        print(path)
    plt.close(fig)


def _text_color(fill_color: str) -> str:
    """Choose readable black/white text from fill color luminance."""
    rgb = np.asarray(to_rgb(fill_color))
    linear = np.where(
        rgb <= 0.04045,
        rgb / 12.92,
        ((rgb + 0.055) / 1.055) ** 2.4,
    )
    luminance = float(linear @ np.asarray([0.2126, 0.7152, 0.0722]))
    return "white" if luminance < 0.34 else INK

def draw_functional():
    data = DATA

    # Expected order from redraw_data:
    # [Pass, Missing, Build, Public, Hidden, Isolation]
    values = np.asarray([row["counts"] for row in data["first_outcomes"]], dtype=int)

    assert values.shape == (len(BACKEND_ORDER), len(STAGE_ORDER))
    assert np.all(values.sum(axis=1) == 150)

    # Headline result for the two strongest configurations.
    pro_flash_failures = int(sum(sum(row["counts"][1:]) for row in data["first_outcomes"][:2]))
    pro_flash_behavioral = int(sum(row["counts"][3] + row["counts"][4] for row in data["first_outcomes"][:2]))
    assert (pro_flash_behavioral, pro_flash_failures) == (76, 77)

    # ----------------------------------------------------------------------
    # Figure / layout
    # ----------------------------------------------------------------------

    fig = plt.figure(figsize=(WIDTH, 3.10))
    ax = fig.add_axes([0.265, 0.30, 0.69, 0.65])

    # fig.text(
    #     0.02,
    #     0.955,
    #     "Functional outcomes and first failed gates",
    #     ha="left",
    #     va="top",
    #     fontsize=9.3,
    #     weight="bold",
    #     color=INK,
    # )

    # fig.text(
    #     0.955,
    #     0.955,
    #     "Pro + Flash: 76/77 failures are Primary/Extended-first",
    #     ha="right",
    #     va="top",
    #     fontsize=7.6,
    #     color=MUTED,
    # )

    # ----------------------------------------------------------------------
    # Stacked horizontal bars
    # ----------------------------------------------------------------------

    y = np.arange(len(BACKEND_ORDER))
    base = np.zeros(len(BACKEND_ORDER), dtype=float)

    for col, stage in enumerate(STAGE_ORDER):
        counts = values[:, col]
        color = BOUNDARY_COLORS[stage]
        hatch = STAGE_HATCHES[stage]

        bars = ax.barh(
            y,
            counts,
            left=base,
            height=0.62,
            color=color,
            hatch=hatch,
            edgecolor="white",
            linewidth=0.65,
            zorder=3,
        )

        # Label sufficiently large segments only.
        for row_idx, (bar, count) in enumerate(zip(bars, counts)):
            if count >= 8:
                ax.text(
                    base[row_idx] + count / 2,
                    row_idx,
                    str(int(count)),
                    ha="center",
                    va="center",
                    fontsize=7.4,
                    color=_text_color(color),
                    weight="semibold" if stage == "Pass" else "normal",
                    bbox=dict(facecolor=color, edgecolor="none", pad=.35),
                    zorder=5,
                )

        base += counts

    # ----------------------------------------------------------------------
    # Axes styling
    # ----------------------------------------------------------------------

    ax.set(
        yticks=y,
        yticklabels=[BACKEND_FULL_NAMES[name] for name in BACKEND_ORDER],
        xlim=(0, 150),
        xticks=[0, 50, 100, 150],
        xlabel="Tasks",
    )

    ax.invert_yaxis()

    ax.tick_params(axis="y", length=0, pad=6, labelsize=8.0)
    ax.tick_params(axis="x", length=3, labelsize=7.9)

    ax.xaxis.label.set_size(8.4)
    ax.xaxis.labelpad = 3

    ax.set_axisbelow(True)
    ax.grid(axis="x", color="#E7ECF0", linewidth=0.6)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#9AA5AD")
    ax.spines["bottom"].set_color("#9AA5AD")
    ax.spines["left"].set_linewidth(0.7)
    ax.spines["bottom"].set_linewidth(0.7)

    # ----------------------------------------------------------------------
    # Legend
    # ----------------------------------------------------------------------

    groups = [
        ('Success', ['Pass'], .12),
        ('Delivery / construction', ['Missing', 'Build'], .37),
        ('Primary / Extended evaluation', ['Public', 'Hidden'], .68),
        ('Isolation', ['Isolation'], .92),
    ]
    for title, stages, x in groups:
        handles = [Patch(facecolor=BOUNDARY_COLORS[stage], edgecolor='#888888',
                         hatch=STAGE_HATCHES[stage], linewidth=.4,
                         label=DISPLAY_LABELS[stage]) for stage in stages]
        fig.legend(handles=handles, title=title, loc='lower center',
                   bbox_to_anchor=(x,.02), ncol=len(stages), columnspacing=.8,
                   handlelength=1.1, handletextpad=.4, fontsize=7.1,
                   title_fontsize=7.4, frameon=False, borderaxespad=0)

    finish(fig, "fig05_evaluation_outcomes")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "output")
    args = parser.parse_args()
    global OUTPUT_DIR
    OUTPUT_DIR = args.output_dir.expanduser().resolve()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    draw_functional()

if __name__ == "__main__":
    main()

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

from matplotlib.patches import Patch, Rectangle
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.transforms import blended_transform_factory
GRID = "#E7ECF0"
RULE = "#8E9AA3"
publish_pdf = lambda path: None

LIFT_COLORS = {
    "Direct": "#0072B2",
    "Adapted": "#E69F00",
    "Composite": "#009E73",
}

COVERAGE_CMAP = LinearSegmentedColormap.from_list(
    "coverage_soft_bluegray",
    [
        (0.00, "#F7F8FA"),
        (0.22, "#E3E8F0"),
        (0.48, "#C2CBD9"),
        (0.74, "#93A1BA"),
        (1.00, "#62738F"),
    ],
)

COVERAGE_NORM = Normalize(vmin=0, vmax=100)

DATA = {
  "mechanism_order": [
    "Code dependencies",
    "Data and state",
    "Framework mechanisms",
    "Environment and resources"
  ],
  "cells": [
    {
      "lift_type": "Direct",
      "mechanism": "Code dependencies",
      "count": 52,
      "denominator": 56,
      "percent": 92.85714285714286
    },
    {
      "lift_type": "Direct",
      "mechanism": "Data and state",
      "count": 54,
      "denominator": 56,
      "percent": 96.42857142857143
    },
    {
      "lift_type": "Direct",
      "mechanism": "Framework mechanisms",
      "count": 22,
      "denominator": 56,
      "percent": 39.285714285714285
    },
    {
      "lift_type": "Direct",
      "mechanism": "Environment and resources",
      "count": 15,
      "denominator": 56,
      "percent": 26.785714285714285
    },
    {
      "lift_type": "Adapted",
      "mechanism": "Code dependencies",
      "count": 69,
      "denominator": 76,
      "percent": 90.78947368421052
    },
    {
      "lift_type": "Adapted",
      "mechanism": "Data and state",
      "count": 64,
      "denominator": 76,
      "percent": 84.21052631578948
    },
    {
      "lift_type": "Adapted",
      "mechanism": "Framework mechanisms",
      "count": 37,
      "denominator": 76,
      "percent": 48.68421052631579
    },
    {
      "lift_type": "Adapted",
      "mechanism": "Environment and resources",
      "count": 24,
      "denominator": 76,
      "percent": 31.57894736842105
    },
    {
      "lift_type": "Composite",
      "mechanism": "Code dependencies",
      "count": 18,
      "denominator": 18,
      "percent": 100.0
    },
    {
      "lift_type": "Composite",
      "mechanism": "Data and state",
      "count": 9,
      "denominator": 18,
      "percent": 50.0
    },
    {
      "lift_type": "Composite",
      "mechanism": "Framework mechanisms",
      "count": 12,
      "denominator": 18,
      "percent": 66.66666666666667
    },
    {
      "lift_type": "Composite",
      "mechanism": "Environment and resources",
      "count": 10,
      "denominator": 18,
      "percent": 55.55555555555556
    }
  ],
  "mechanism_marginals": [
    {
      "mechanism": "Code dependencies",
      "count": 139,
      "denominator": 150,
      "percent": 92.66666666666667
    },
    {
      "mechanism": "Data and state",
      "count": 127,
      "denominator": 150,
      "percent": 84.66666666666667
    },
    {
      "mechanism": "Framework mechanisms",
      "count": 71,
      "denominator": 150,
      "percent": 47.333333333333336
    },
    {
      "mechanism": "Environment and resources",
      "count": 49,
      "denominator": 150,
      "percent": 32.666666666666664
    }
  ],
  "release_lift_counts": {
    "Adapted": 76,
    "Direct": 56,
    "Composite": 18
  }
}

def save_figure(
    fig,
    output_dir: Path,
    basename: str,
    dpi: int,
) -> None:
    """Save one figure as vector PDF and high-resolution PNG."""

    pdf_path = output_dir / f"{basename}.pdf"
    png_path = output_dir / f"{basename}.png"

    fig.savefig(
        pdf_path,
        bbox_inches="tight",
        pad_inches=0.02,
    )

    fig.savefig(
        png_path,
        dpi=dpi,
        bbox_inches="tight",
        pad_inches=0.02,
    )

    publish_pdf(pdf_path)
    plt.close(fig)

    print(pdf_path)
    print(png_path)

def text_color_for_heatmap(value: float) -> str:
    """Choose readable black/white text for a heatmap cell."""

    rgb = np.asarray(COVERAGE_CMAP(COVERAGE_NORM(value))[:3])
    linear = np.where(
        rgb <= 0.04045,
        rgb / 12.92,
        ((rgb + 0.055) / 1.055) ** 2.4,
    )
    luminance = float(linear @ np.asarray([0.2126, 0.7152, 0.0722]))
    return "white" if luminance < 0.30 else INK

def draw_entanglement(
    data,
    n: int,
    output_dir: Path,
    dpi: int,
) -> None:
    """Entanglement mechanisms overall and by lift type."""

    mechanisms = data["mechanism_order"]

    cells = {
        (
            cell["lift_type"],
            cell["mechanism"],
        ): cell
        for cell in data["cells"]
    }

    matrix_rows = [
        data["mechanism_marginals"]
    ] + [
        [
            cells[lift, mechanism]
            for mechanism in mechanisms
        ]
        for lift in LIFT_COLORS
    ]

    counts = np.asarray(
        [
            [
                cell["count"]
                for cell in row
            ]
            for row in matrix_rows
        ]
    )

    denominators = np.asarray(
        [
            n,
            *[
                data[
                    "release_lift_counts"
                ][lift]
                for lift in LIFT_COLORS
            ],
        ]
    )

    # Overall counts must equal the sum over lift types.
    assert np.array_equal(
        counts[0],
        counts[1:].sum(axis=0),
    )

    percentages = (
        100.0
        * counts
        / denominators[:, None]
    )

    expected = np.asarray(
        [
            [
                cell["percent"]
                for cell in row
            ]
            for row in matrix_rows
        ]
    )

    assert np.allclose(
        percentages,
        expected,
    )

    fig = plt.figure(figsize=(3.80, 2.46))
    ax = fig.add_axes((0.30, 0.18, 0.68, 0.64))

    ax.imshow(
        percentages,
        cmap=COVERAGE_CMAP,
        norm=COVERAGE_NORM,
        aspect="auto",
        interpolation="nearest",
    )

    # These are four categorical mechanism headers, not a numerical x-axis.
    # Render them as a compact table header instead of Matplotlib tick labels.
    # This matches the terminology used in Sec. 2.4 of the paper and avoids
    # the uneven baseline/spacing produced by mixed one- and two-line ticks.
    column_labels = [
        "Code\ndependencies",
        "Data &\nstate",
        "Framework\nmechanisms",
        "Environment &\nresources",
    ]
    row_labels = [
        f"All ({n})",
        *[
            f"{lift} ({data['release_lift_counts'][lift]})"
            for lift in LIFT_COLORS
        ],
    ]

    # Suppress the categorical x-axis entirely; the labels below are column
    # headers centered in a fixed-height header band above the heatmap.
    ax.set_xticks([])
    header_trans = blended_transform_factory(ax.transData, ax.transAxes)
    for col, label in enumerate(column_labels):
        ax.text(
            col,
            1.075,
            label,
            transform=header_trans,
            ha="center",
            va="center",
            multialignment="center",
            linespacing=1.02,
            fontsize=6.45,
            color=INK,
            clip_on=False,
        )

    # Left axis: pull labels closer to the grid and keep a strong hierarchy
    # between the aggregate row and the three lift-type rows.
    ax.set_yticks(np.arange(4))
    ax.set_yticklabels(row_labels)
    ax.tick_params(
        axis="y",
        left=False,
        right=False,
        length=0,
        pad=9.0,
        labelsize=7.4,
        labelcolor=INK,
    )
    for i, tick in enumerate(ax.get_yticklabels()):
        tick.set_ha("right")
        tick.set_va("center")
        tick.set_color(INK)
        tick.set_fontweight("bold" if i == 0 else "normal")

    ax.set_xlim(-0.5, 3.5)
    ax.set_ylim(3.5, -0.5)
    ax.set_facecolor("white")
    ax.set_frame_on(False)

    for pos in (0.5, 1.5, 2.5):
        ax.axvline(pos, color="white", linewidth=1.6, zorder=3)
        ax.axhline(pos, color="white", linewidth=1.6, zorder=3)

    ax.axhline(0.5, color="white", linewidth=2.6, zorder=4)
    ax.axhline(0.5, color=RULE, linewidth=0.65, zorder=5)

    for row in range(4):
        for col in range(4):
            value = percentages[row, col]
            text_color = text_color_for_heatmap(value)
            if row == 0:
                percent_text = f"{value:.1f}%"
                percent_size = 8.5
                percent_weight = "bold"
            else:
                percent_text = f"{value:.0f}%"
                percent_size = 8.0
                percent_weight = "normal"

            ax.text(
                col,
                row - 0.14,
                percent_text,
                ha="center",
                va="center",
                fontsize=percent_size,
                fontweight=percent_weight,
                color=text_color,
            )
            ax.text(
                col,
                row + 0.23,
                f"{counts[row, col]}/{denominators[row]}",
                ha="center",
                va="center",
                fontsize=6.4,
                color=text_color,
                alpha=0.82,
            )

    rail = blended_transform_factory(ax.transAxes, ax.transData)
    for row, color in enumerate(LIFT_COLORS.values(), start=1):
        ax.add_patch(
            Rectangle(
                (-0.024, row - 0.34),
                0.012,
                0.68,
                transform=rail,
                facecolor=color,
                edgecolor="none",
                clip_on=False,
                zorder=10,
            )
        )

    box = ax.get_position()
    cax = fig.add_axes((box.x0, 0.048, box.width, 0.026))
    sm = ScalarMappable(norm=COVERAGE_NORM, cmap=COVERAGE_CMAP)
    sm.set_array([])
    cb = fig.colorbar(sm, cax=cax, orientation="horizontal", ticks=[0, 50, 100])
    cb.outline.set_visible(False)
    cb.ax.tick_params(length=0, labelsize=6.2, pad=1.2, colors=INK)
    cb.ax.set_xticklabels(["0", "50", "100"])
    cb.set_label("Coverage (%)", fontsize=6.4, labelpad=1.5, color=INK)

    save_figure(
        fig,
        output_dir,
        "fig03b_entanglement",
        dpi,
    )

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "output")
    args = parser.parse_args()
    global OUTPUT_DIR
    OUTPUT_DIR = args.output_dir.expanduser().resolve()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    draw_entanglement(DATA, 150, OUTPUT_DIR, 300)

if __name__ == "__main__":
    main()

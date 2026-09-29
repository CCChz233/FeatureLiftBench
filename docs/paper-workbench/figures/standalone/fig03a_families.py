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
  "feature_families": [
    {
      "key": "registry_plugin_dispatch",
      "label": "Registry / dispatch",
      "count": 22,
      "lift_counts": {
        "Direct": 3,
        "Adapted": 10,
        "Composite": 9
      }
    },
    {
      "key": "parse_tokenize_decode",
      "label": "Parsing / decoding",
      "count": 31,
      "lift_counts": {
        "Direct": 14,
        "Adapted": 17,
        "Composite": 0
      }
    },
    {
      "key": "config_resolve_discover",
      "label": "Configuration / discovery",
      "count": 18,
      "lift_counts": {
        "Direct": 5,
        "Adapted": 11,
        "Composite": 2
      }
    },
    {
      "key": "validate_normalize_construct",
      "label": "Validation / construction",
      "count": 15,
      "lift_counts": {
        "Direct": 6,
        "Adapted": 9,
        "Composite": 0
      }
    },
    {
      "key": "serialize_format_render",
      "label": "Serialization / rendering",
      "count": 19,
      "lift_counts": {
        "Direct": 10,
        "Adapted": 9,
        "Composite": 0
      }
    },
    {
      "key": "workflow_session_orchestration",
      "label": "Workflow / orchestration",
      "count": 5,
      "lift_counts": {
        "Direct": 2,
        "Adapted": 2,
        "Composite": 1
      }
    },
    {
      "key": "resource_metadata_loading",
      "label": "Resources / metadata",
      "count": 12,
      "lift_counts": {
        "Direct": 3,
        "Adapted": 6,
        "Composite": 3
      }
    },
    {
      "key": "algorithm_data_structure",
      "label": "Algorithms / data structures",
      "count": 11,
      "lift_counts": {
        "Direct": 7,
        "Adapted": 4,
        "Composite": 0
      }
    },
    {
      "key": "protocol_state_transition",
      "label": "Protocol / state transitions",
      "count": 9,
      "lift_counts": {
        "Direct": 3,
        "Adapted": 6,
        "Composite": 0
      }
    },
    {
      "key": "cache_retry_policy",
      "label": "Cache / retry policies",
      "count": 8,
      "lift_counts": {
        "Direct": 3,
        "Adapted": 2,
        "Composite": 3
      }
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


def draw_functional_families(
    data,
    output_dir: Path,
    dpi: int,
) -> None:
    """Functional families partitioned by lift type."""

    families = sorted(
        data["feature_families"],
        key=lambda row: -row["count"],
    )

    fig = plt.figure(figsize=(4.75, 2.55))

    # Long category labels require a generous left margin.
    ax = fig.add_axes((0.40, 0.21, 0.56, 0.76))

    y = np.arange(len(families))
    base = np.zeros(len(families))
    totals = np.asarray([family["count"] for family in families])

    for lift, color in LIFT_COLORS.items():
        values = np.asarray(
            [
                family["lift_counts"][lift]
                for family in families
            ]
        )

        ax.barh(
            y,
            values,
            left=base,
            height=0.62,
            color=color,
            edgecolor="white",
            linewidth=0.6,
            zorder=3,
        )

        base += values

    # Total task count at the end of each bar.
    for i, total in enumerate(totals):
        ax.text(
            total + 0.55,
            i,
            str(total),
            ha="left",
            va="center",
            fontsize=8.2,
            color=INK,
            clip_on=False,
        )

    ax.set(
        yticks=y,
        yticklabels=[family["label"] for family in families],
        xlim=(0, float(totals.max()) + 5.0),
        xticks=[0, 10, 20, 30],
        xlabel="Tasks",
    )

    ax.invert_yaxis()

    ax.tick_params(axis="y", length=0, pad=5, labelsize=8.2, colors=INK)
    ax.tick_params(axis="x", length=3, labelsize=8.0, colors=RULE, labelcolor=INK)

    ax.xaxis.label.set_size(8.2)
    ax.xaxis.labelpad = 2.0
    ax.xaxis.label.set_color(INK)

    for side in ("left", "right", "top"):
        ax.spines[side].set_visible(False)

    ax.spines["bottom"].set_color(RULE)
    ax.spines["bottom"].set_linewidth(0.7)

    ax.set_axisbelow(True)
    ax.grid(axis="x", color=GRID, linewidth=0.55)

    handles = [
        Patch(
            facecolor=color,
            edgecolor="none",
            label=f"{lift} ({data['release_lift_counts'][lift]})",
        )
        for lift, color in LIFT_COLORS.items()
    ]

    fig.legend(
        handles=handles,
        loc="lower left",
        bbox_to_anchor=(0.02, 0.012),
        ncol=3,
        fontsize=7.6,
        columnspacing=1.15,
        handlelength=0.95,
        handleheight=0.72,
        handletextpad=0.40,
        borderaxespad=0,
        frameon=False,
    )

    save_figure(
        fig,
        output_dir,
        "fig03a_families",
        dpi,
    )

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "output")
    args = parser.parse_args()
    global OUTPUT_DIR
    OUTPUT_DIR = args.output_dir.expanduser().resolve()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    draw_functional_families(DATA, OUTPUT_DIR, 300)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Fig. 3: benchmark composition.

Produces two independent panels:

    fig3a_families.pdf
    fig3a_families.png
    fig3b_entanglement.pdf
    fig3b_entanglement.png

Default output:
    docs/paper/figures/output/

Optional:
    python fig3_composition.py --output-dir /some/path

The script is location-independent:
it can be launched from the repository root, the scripts directory,
an IDE, or any other working directory.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

try:
    import numpy as np
    import matplotlib

    # Safe for command-line / headless environments.
    matplotlib.use("Agg")

    from matplotlib import pyplot as plt
    from matplotlib.patches import Patch
    from matplotlib.colors import LinearSegmentedColormap

except ImportError as exc:
    raise SystemExit(
        "\nMissing plotting dependencies.\n\n"
        "Run this script with the Python environment that has matplotlib/numpy.\n"
        "For your Mac, for example:\n\n"
        "    /Users/chz/anaconda3/bin/python "
        "docs/paper/figures/scripts/fig3_composition.py\n\n"
        f"Original error: {exc}\n"
    )


# ---------------------------------------------------------------------------
# Locate project modules robustly
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
FIGURES_DIR = SCRIPT_DIR.parent
DEFAULT_OUTPUT_DIR = FIGURES_DIR / "output"

# Allows project-local imports regardless of the current working directory.
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from redraw_data import task_coverage  # noqa: E402
from figure_common import publish_pdf, render  # noqa: E402
import paper_style  # noqa: E402


# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------

INK = "#17202A"

LIFT_COLORS = {
    "Direct": "#0072B2",
    "Adapted": "#E69F00",
    "Composite": "#009E73",
}

COVERAGE_CMAP = LinearSegmentedColormap.from_list(
    "coverage_gray",
    ["#F7F7F7", "#383838"],
)


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Fig. 3 composition panels."
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help=(
            "Directory for generated PDF/PNG files. "
            "Defaults to ../output relative to this script."
        ),
    )

    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="PNG resolution. Default: 300 dpi.",
    )

    return parser.parse_args()


def resolve_output_dir(raw: Path | None) -> Path:
    """Return a writable output directory.

    If --output-dir is omitted, use:
        docs/paper/figures/output/

    Relative --output-dir paths are interpreted relative to the
    current working directory, which is standard CLI behavior.
    """

    if raw is None:
        output_dir = DEFAULT_OUTPUT_DIR
    else:
        output_dir = raw.expanduser()

        if not output_dir.is_absolute():
            output_dir = Path.cwd() / output_dir

    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    return output_dir


def save_figure(
    fig: plt.Figure,
    output_dir: Path,
    basename: str,
    dpi: int,
) -> None:
    """Save one figure as both vector PDF and high-resolution PNG."""

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


def load_data():
    """Load and sanity-check benchmark composition data."""

    data = task_coverage()

    n = len(data["complete_tasks"])

    assert n == 150, f"Expected 150 tasks, got {n}"
    assert n == data["release_tasks"]
    assert n == data["mechanism_tasks"]

    assert sum(
        f["count"]
        for f in data["feature_families"]
    ) == n

    assert sum(
        data["release_lift_counts"].values()
    ) == n

    return data, n


def text_color_for_heatmap(value: float) -> str:
    """Choose readable black/white text for a heatmap cell."""

    rgb = np.asarray(
        COVERAGE_CMAP(value / 100.0)[:3]
    )

    linear = np.where(
        rgb <= 0.04045,
        rgb / 12.92,
        ((rgb + 0.055) / 1.055) ** 2.4,
    )

    luminance = float(
        linear
        @ np.asarray(
            [0.2126, 0.7152, 0.0722]
        )
    )

    return "white" if luminance < 0.179 else "black"


# ---------------------------------------------------------------------------
# Fig. 3(a)
# ---------------------------------------------------------------------------

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

    fig = plt.figure(
        figsize=(4.75, 2.85)
    )

    # Large left margin because category labels are long.
    ax = fig.add_axes(
        [0.40, 0.20, 0.56, 0.68]
    )

    fig.text(
        0.015,
        0.955,
        "(a) Functional families by lift type",
        ha="left",
        va="top",
        fontsize=9.2,
        weight="bold",
        color=INK,
    )

    y = np.arange(len(families))
    base = np.zeros(len(families))

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
            height=0.68,
            color=color,
            edgecolor="white",
            linewidth=0.45,
            zorder=3,
        )

        base += values

    # Total task count.
    for i, family in enumerate(families):
        ax.text(
            family["count"] + 0.42,
            i,
            str(family["count"]),
            ha="left",
            va="center",
            fontsize=8.4,
            color=INK,
        )

    ax.set(
        yticks=y,
        yticklabels=[
            f["label"]
            for f in families
        ],
        xlim=(0, 34),
        xticks=[0, 10, 20, 30],
        xlabel="Tasks",
    )

    ax.invert_yaxis()

    ax.tick_params(
        axis="y",
        length=0,
        pad=5,
        labelsize=8.3,
    )

    ax.tick_params(
        axis="x",
        length=3,
        labelsize=8.1,
    )

    ax.xaxis.label.set_size(8.3)
    ax.xaxis.labelpad = 1.5

    for side in [
        "left",
        "right",
        "top",
    ]:
        ax.spines[side].set_visible(False)

    ax.spines["bottom"].set_color(
        "#A6AFB5"
    )
    ax.spines["bottom"].set_linewidth(
        0.8
    )

    ax.set_axisbelow(True)

    ax.grid(
        axis="x",
        color="#E7ECF0",
        linewidth=0.6,
    )

    handles = [
        Patch(
            facecolor=color,
            edgecolor="none",
            label=lift,
        )
        for lift, color
        in LIFT_COLORS.items()
    ]

    fig.legend(
        handles=handles,
        loc="lower left",
        bbox_to_anchor=(
            0.015,
            0.012,
        ),
        ncol=3,
        fontsize=7.7,
        columnspacing=1.05,
        handlelength=1.05,
        handletextpad=0.40,
        borderaxespad=0,
        frameon=False,
    )

    save_figure(
        fig,
        output_dir,
        "fig3a_families",
        dpi,
    )


# ---------------------------------------------------------------------------
# Fig. 3(b)
# ---------------------------------------------------------------------------

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

    # All = Direct + Adapted + Composite.
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

    fig = plt.figure(
        figsize=(3.75, 2.95)
    )

    # Enough top room for title and headers,
    # enough left room for complete row labels.
    ax = fig.add_axes(
        [0.31, 0.13, 0.66, 0.62]
    )

    fig.text(
        0.02,
        0.955,
        "(b) Entanglement by lift type",
        ha="left",
        va="top",
        fontsize=9.0,
        weight="bold",
        color=INK,
    )

    ax.imshow(
        percentages,
        cmap=COVERAGE_CMAP,
        vmin=0,
        vmax=100,
        aspect="auto",
        interpolation="nearest",
    )

    column_labels = [
        "Code\ndeps.",
        "Data /\nstate",
        "Framework",
        "Env. /\nresources",
    ]

    # Denominators already appear in the data cells; row names stay minimal.
    row_labels = ["All", *LIFT_COLORS]

    # Column labels.
    ax.set_xticks(
        np.arange(4)
    )
    ax.set_xticklabels(
        column_labels
    )

    ax.tick_params(
        axis="x",
        top=True,
        labeltop=True,
        bottom=False,
        labelbottom=False,
        length=0,
        pad=4,
        labelsize=7.4,
    )

    # Native y labels avoid clipping.
    ax.set_yticks(
        np.arange(4)
    )
    ax.set_yticklabels(
        row_labels
    )

    ax.tick_params(
        axis="y",
        left=False,
        right=False,
        length=0,
        pad=8,
        labelsize=7.8,
    )

    # Benchmark-level summary row emphasized.
    for i, tick in enumerate(
        ax.get_yticklabels()
    ):
        tick.set_color(INK)

        tick.set_fontweight(
            "bold"
            if i == 0
            else "normal"
        )

    # Cell boundaries.
    ax.set_xticks(
        np.arange(-0.5, 4, 1),
        minor=True,
    )

    ax.set_yticks(
        np.arange(-0.5, 4, 1),
        minor=True,
    )

    ax.grid(
        which="minor",
        color="white",
        linewidth=1.05,
    )

    ax.tick_params(
        which="minor",
        bottom=False,
        left=False,
    )

    for spine in ax.spines.values():
        spine.set_visible(False)

    # Visually separate All from lift types.
    ax.axhline(
        0.5,
        color="white",
        linewidth=2.8,
    )

    # Cell values.
    for row in range(4):
        for col in range(4):
            value = percentages[
                row,
                col,
            ]

            text_color = (
                text_color_for_heatmap(
                    value
                )
            )

            if row == 0:
                percent_text = (
                    f"{value:.1f}%"
                )
                percent_size = 8.7
                percent_weight = "bold"
            else:
                percent_text = (
                    f"{value:.0f}%"
                )
                percent_size = 8.2
                percent_weight = "normal"

            ax.text(
                col,
                row - 0.13,
                percent_text,
                ha="center",
                va="center",
                fontsize=percent_size,
                weight=percent_weight,
                color=text_color,
            )

            ax.text(
                col,
                row + 0.22,
                (
                    f"{counts[row, col]}"
                    f"/{denominators[row]}"
                ),
                ha="center",
                va="center",
                fontsize=6.8,
                color=text_color,
            )

    save_figure(
        fig,
        output_dir,
        "fig3b_entanglement",
        dpi,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def draw_coverage(dpi=300):
    output_dir = resolve_output_dir(paper_style.OUTPUT_DIR)
    data, n = load_data()

    draw_functional_families(
        data,
        output_dir,
        dpi,
    )

    draw_entanglement(
        data,
        n,
        output_dir,
        dpi,
    )


def main() -> None:
    args = parse_args()
    render([lambda: draw_coverage(args.dpi)], args.output_dir)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Fig. 3: benchmark composition.

Produces two independent panels:

    fig03a_families.pdf/png
    fig03b_entanglement.pdf/png

Default output:
    docs/paper-workbench/figures/output/

Optional:
    python fig03_benchmark_composition.py --output-dir /some/path

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
    from matplotlib.patches import Patch, Rectangle
    from matplotlib.colors import LinearSegmentedColormap, Normalize
    from matplotlib.cm import ScalarMappable
    from matplotlib.transforms import blended_transform_factory

except ImportError as exc:
    raise SystemExit(
        "\nMissing plotting dependencies.\n\n"
        "Run this script with the Python environment that has matplotlib/numpy.\n"
        "For your Mac, for example:\n\n"
        "    /Users/chz/anaconda3/bin/python "
        "docs/paper-workbench/figures/scripts/fig03_benchmark_composition.py\n\n"
        f"Original error: {exc}\n"
    )


# ---------------------------------------------------------------------------
# Locate project modules robustly
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
FIGURES_DIR = SCRIPT_DIR.parent
DEFAULT_OUTPUT_DIR = FIGURES_DIR / "output"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from redraw_data import task_coverage  # noqa: E402
from figure_common import INK, MUTED, publish_pdf, render  # noqa: E402
import paper_style  # noqa: E402


# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------

GRID = "#E7ECF0"
RULE = "#8E9AA3"

# Okabe-Ito-style, color-blind-friendly categorical colors.
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
    """Return a writable output directory."""

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


def load_data():
    """Load and sanity-check benchmark composition data."""

    data = task_coverage()

    n = len(data["complete_tasks"])

    assert n == 150, f"Expected 150 tasks, got {n}"
    assert n == data["release_tasks"]
    assert n == data["mechanism_tasks"]

    assert sum(
        row["count"]
        for row in data["feature_families"]
    ) == n

    assert sum(
        data["release_lift_counts"].values()
    ) == n

    return data, n


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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def draw_coverage(
    dpi: int = 300,
) -> None:
    output_dir = resolve_output_dir(
        paper_style.OUTPUT_DIR
    )

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

    render(
        [
            lambda: draw_coverage(
                args.dpi
            )
        ],
        args.output_dir,
    )


if __name__ == "__main__":
    main()

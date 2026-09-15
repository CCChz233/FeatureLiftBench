"""Fig. 4: functional outcomes and first failed gates.

Edit this file for this figure's layout, marks, labels, and annotations.

Run directly to update its PDF/PNG, or use --output-dir for a separate preview.

Data preparation is shared in redraw_data.py; styles are in paper_style.py.
"""

from figure_common import INK, MUTED, WIDTH, finish, run_single
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.patches import Patch
from matplotlib.colors import to_rgb

from redraw_data import functional_results
from paper_style import (
    BACKEND_ORDER,
    BACKEND_FULL_NAMES,
    STAGE_ORDER,
    STAGE_COLORS,
    STAGE_HATCHES,
)


# ---------------------------------------------------------------------------
# Labels used in the plot / legend
# ---------------------------------------------------------------------------

DISPLAY_LABELS = {
    "Pass": "Pass",
    "Missing": "No usable submission",
    "Build": "Build",
    "Public": "Primary",
    "Hidden": "Extended",
    "Isolation": "Isolation",
}


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
    data = functional_results()

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

    fig = plt.figure(figsize=(WIDTH, 2.95))
    ax = fig.add_axes([0.265, 0.25, 0.69, 0.60])

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
        color = STAGE_COLORS[stage]
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

    handles = [
        Patch(
            facecolor=STAGE_COLORS[stage],
            edgecolor="#888888",
            hatch=STAGE_HATCHES[stage],
            linewidth=0.4,
            label=DISPLAY_LABELS[stage],
        )
        for stage in STAGE_ORDER
    ]

    fig.legend(
        handles=handles,
        loc="lower center",
        bbox_to_anchor=(0.57, 0.06),
        ncol=6,
        columnspacing=0.85,
        handlelength=1.10,
        handletextpad=0.42,
        fontsize=7.2,
        frameon=False,
        borderaxespad=0,
    )

    finish(fig, "fig4")


def main():
    run_single(draw_functional, __doc__)


if __name__ == "__main__":
    main()
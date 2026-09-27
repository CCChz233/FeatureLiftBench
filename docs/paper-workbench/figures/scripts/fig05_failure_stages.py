"""Fig. 5: functional outcomes and first failed gates.

Edit this file for this figure's layout, marks, labels, and annotations.

Run directly to update its PDF/PNG, or use --output-dir for a separate preview.

Data preparation is shared in redraw_data.py; styles are in paper_style.py.
"""

from figure_common import INK, WIDTH, finish, run_single
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
    "Missing": "No submission",
    "Build": "Build",
    "Public": "Primary",
    "Hidden": "Extended",
    "Isolation": "Isolation",
}


# Related shades group the failure boundaries while retaining individual gates.
BOUNDARY_COLORS = dict(STAGE_COLORS, Missing='#D1D5D9', Build='#7D8791',
                       Public='#78B4D6', Hidden='#176C9E', Isolation='#C77818')


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


def build_compact(width=2.85):
    """Side-by-side candidate at its actual print width; leaves default unchanged."""
    data = functional_results()
    values = np.asarray([row['counts'] for row in data['first_outcomes']], dtype=int)
    assert values.shape == (6, 6) and np.all(values.sum(axis=1) == 150)
    fig, ax = plt.subplots(figsize=(width, 2.35))
    fig.subplots_adjust(left=.38 / width, right=1 - .10 / width, bottom=.35, top=.97)
    base = np.zeros(6)
    for col, stage in enumerate(STAGE_ORDER):
        color = BOUNDARY_COLORS[stage]
        counts = values[:, col]
        ax.barh(np.arange(6), counts, left=base, height=.64, color=color,
                hatch=STAGE_HATCHES[stage], edgecolor='white', linewidth=.4, zorder=3)
        # The figure shows composition; detailed small segment counts are omitted.
        for i, n in enumerate(counts):
            if n >= 20:
                ax.text(base[i] + n/2, i, str(n), ha='center', va='center',
                        fontsize=7.5, color=_text_color(color), zorder=4)
        base += counts
    ax.set(yticks=np.arange(6), yticklabels=BACKEND_ORDER, xlim=(0, 150),
           xticks=[0, 50, 100, 150], xlabel='Tasks')
    ax.invert_yaxis()
    ax.tick_params(axis='y', length=0, labelsize=8, pad=4)
    ax.tick_params(axis='x', labelsize=7.5, length=2.5)
    ax.xaxis.label.set_size(8)
    ax.grid(axis='x', color='#E7ECF0', linewidth=.5)
    for spine in ['top', 'right', 'left']:
        ax.spines[spine].set_visible(False)
    ax.spines['bottom'].set_color('#9AA5AD')
    labels = dict(DISPLAY_LABELS, Missing='No submission')
    handles = [Patch(facecolor=STAGE_COLORS[s], hatch=STAGE_HATCHES[s],
                     edgecolor='#888888', linewidth=.3, label=labels[s]) for s in STAGE_ORDER]
    fig.legend(handles=handles, loc='lower center', bbox_to_anchor=(.5, .01),
               ncol=2, fontsize=7.5, columnspacing=1.0, handlelength=1.2,
               handletextpad=.5, labelspacing=.4, frameon=False)
    return fig, data


def main():
    run_single(draw_functional, __doc__)


if __name__ == "__main__":
    main()

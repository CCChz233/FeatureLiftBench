"""Fig. 8: six-configuration task-adjusted footprint.

Produces two independent panels without in-image titles:

    fig08a_rres.pdf/png
        Task-adjusted RRES ratios.

    fig08b_copy.pdf/png
        Task-adjusted Copy differences in percentage points.

Panel titles belong in the LaTeX caption.

Analysis and bootstrap settings: footprint_analysis.py.
Use --output-dir to preview without replacing manuscript assets.
"""
from pathlib import Path
import numpy as np
from figure_common import finish, run_single, BLUE, INK
from matplotlib import pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter, NullLocator
import redraw_data
from footprint_analysis import analyze, write_outputs

RRES_LIM = (0, 2.0)
COPY_LIM = (-40, 40)
PANEL = dict(figsize=(3.50, 2.55), left=0.22, right=0.98, bottom=0.16, top=0.97)


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


def draw_matched():
    data, draws = analyze()
    rows = data["analyses"]["task_bootstrap"]["rows"]
    payload = dict(
        data,
        geometry="task_adjusted_vertical_bars",
        caption_note=("Task-adjusted successful-artifact footprints: (a) RRES ratios; "
                      "(b) Copy differences in percentage points."),
        figure_analysis="task_bootstrap",
        rres_limits=list(RRES_LIM),
        copy_limits=list(COPY_LIM),
    )
    sources = [redraw_data.ROOT / s["path"] for s in data["sources"]] + [Path(__file__).resolve()]
    redraw_data.export("fig08_artifact_footprint", payload, sources)
    write_outputs(redraw_data.FIGURES_DIR / "data", data, draws, prefix="fig08")
    (redraw_data.FIGURES_DIR / "data/fig08_caption.md").write_text(payload["caption_note"] + "\n")
    _draw_panel(
        rows,
        metric="rres_ratio",
        center=1,
        limits=RRES_LIM,
        ticks=[0, .5, 1, 1.5, 2],
        labels=["0", "0.5×", "1×", "1.5×", "2×"],
        ylabel="Task-adjusted RRES ratio",
        name="fig08a_rres",
    )
    _draw_panel(
        rows,
        metric="copy_pp",
        center=0,
        limits=COPY_LIM,
        ticks=[-40, -20, 0, 20, 40],
        labels=["−40", "−20", "0", "+20", "+40"],
        ylabel="Copy vs. center (pp)",
        name="fig08b_copy",
    )


if __name__ == "__main__":
    run_single(draw_matched, __doc__)

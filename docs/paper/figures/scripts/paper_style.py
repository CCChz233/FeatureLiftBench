"""Shared presentation settings for FeatureLiftBench paper figures.

Project-specific implementation informed by the figures4papers design notes.
See ../FIGURES4PAPERS_ADOPTION.md for sources and adaptation decisions.
Only the shared paper configuration is read at import; no figures are created.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from paper_inputs import MODELS, SHORT, DISPLAY_NAMES

FIGURES_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = FIGURES_DIR / "output"

BACKEND_ORDER = tuple(SHORT[model] for model in MODELS)
BACKEND_FULL_NAMES = DISPLAY_NAMES
BACKEND_COLORS = dict(zip(BACKEND_ORDER, (
    "#0072B2", "#56B4E9", "#D55E00", "#009E73", "#CC79A7", "#666666",
)))
STAGE_ORDER = ("Pass", "Missing", "Build", "Public", "Hidden", "Isolation")
STAGE_COLORS = dict(zip(STAGE_ORDER, (
    "#009E73", "#BDBDBD", "#CC79A7", "#56B4E9", "#E69F00", "#444444",
)))
STAGE_HATCHES = dict(zip(STAGE_ORDER, ("", "//", "xx", "", "..", "\\\\")))


def apply_paper_style(font_size=9):
    """Apply a restrained style at intended print size; no external TeX."""
    import matplotlib as mpl

    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
        "font.size": font_size,
        "axes.labelsize": font_size,
        "axes.titlesize": font_size,
        "xtick.labelsize": font_size - 1,
        "ytick.labelsize": font_size - 1,
        "legend.fontsize": font_size - 1,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.8,
        "axes.axisbelow": True,
        "axes.grid": False,
        "lines.linewidth": 1.2,
        "lines.markersize": 4,
        "legend.frameon": False,
        "text.usetex": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "savefig.transparent": False,
    })


def panel_label(ax, letter, title):
    """Use a left-aligned panel title that participates in layout."""
    ax.set_title(f"({letter}) {title}", loc="left", fontweight="bold", pad=7)


def save_figure(fig, name, *, formats=("pdf", "png"), dpi=300):
    """Export to output/; preserve the chosen canvas size and return paths.

    Prefer constrained_layout at creation time. Avoid tight bounding-box crops
    here because they can change the final physical width between figures.
    The caller controls when to close the figure.
    """
    if not name or Path(name).name != name or Path(name).suffix:
        raise ValueError("Use a plain filename stem, e.g. fig03_failures")
    if not formats or any(fmt not in {"pdf", "png", "svg"} for fmt in formats):
        raise ValueError("Supported formats: pdf, png, svg")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = []
    for fmt in formats:
        path = OUTPUT_DIR / f"{name}.{fmt}"
        fig.savefig(path, format=fmt, dpi=dpi, bbox_inches=None)
        paths.append(path)
    return paths

"""Figure 5: each point pairs two successful artifacts for the same task."""
from figure_data import paired_footprint, prepare_matplotlib
prepare_matplotlib()
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.ticker import NullFormatter
from paper_style import apply_paper_style, panel_label, save_figure


def main():
    data = paired_footprint()
    apply_paper_style()
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 4.5))
    fig.subplots_adjust(left=.09, right=.975, bottom=.24, top=.79, wspace=.34)
    fig.suptitle("Extraction footprint on common successes", x=.09, y=.98, ha="left", fontsize=11, weight="bold")
    fig.text(.09, .926, "Pro and Luna · 97 common passing tasks · One point per matched task", fontsize=8, color="#555555")
    for ax, metric, letter, title in zip(axes, ("rres", "copy"), ("a", "b"),
                                        ("Reference-relative size", "Detected copy fraction")):
        x = np.array([r[f"luna_{metric}"] for r in data["points"]])
        y = np.array([r[f"pro_{metric}"] for r in data["points"]])
        if metric == "rres":
            ax.set_xscale("log")
            ax.set_yscale("log")
            low, high = .01, 100
            ticks = [.01, .1, 1, 10, 100]
            labels = ["0.01", "0.1", "1", "10", "100"]
            ax.set_xticks(ticks, labels)
            ax.set_yticks(ticks, labels)
            ax.xaxis.set_minor_formatter(NullFormatter())
            ax.yaxis.set_minor_formatter(NullFormatter())
            ax.set_xlabel("Luna RRES (log scale)")
            ax.set_ylabel("Pro RRES (log scale)")
        else:
            low, high = -.035, 1.035
            ax.set_xticks([0, .25, .5, .75, 1])
            ax.set_yticks([0, .25, .5, .75, 1])
            ax.set_xlabel("Luna copy fraction")
            ax.set_ylabel("Pro copy fraction")
        assert np.all((x >= low) & (x <= high)) and np.all((y >= low) & (y <= high))
        ax.plot([max(low, 0), min(high, 1)] if metric == "copy" else [low, high],
                [max(low, 0), min(high, 1)] if metric == "copy" else [low, high],
                color="#666666", linestyle="--", linewidth=.9, zorder=1)
        ax.scatter(x, y, s=21, color="#0072B2", edgecolors="white", linewidths=.3, alpha=.65, zorder=3)
        ax.set(xlim=(low, high), ylim=(low, high))
        ax.set_aspect("equal", adjustable="box")
        panel_label(ax, letter, title)
        summary = data["summaries"][metric]
        ax.text(.5, -.20, f'Pro > Luna: {summary["pro_greater"]}   |   Pro < Luna: {summary["luna_greater"]}   |   Ties: {summary["ties"]}',
                transform=ax.transAxes, ha="center", va="top", fontsize=7.5)
    fig.text(.09, .079, "Dashed line: equal values. Above it, Pro has greater size or source overlap, not greater quality.", fontsize=7.5)
    fig.text(.09, .025, "RRES = artifact/reference Python LOC. Log axes retain the full RRES range; zero-copy values remain visible.", fontsize=7.2, color="#555555")
    for path in save_figure(fig, "fig05_paired_footprint"):
        print(path)
    plt.close(fig)


if __name__ == "__main__":
    main()

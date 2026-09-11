"""Draw the revised A/B/C figure set; export PDF/PNG without compiling LaTeX."""
from figure_data import prepare_matplotlib
prepare_matplotlib()
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

from redraw_data import task_coverage, functional_results, footprint
from paper_style import BACKEND_ORDER, BACKEND_FULL_NAMES, STAGE_ORDER, STAGE_COLORS, STAGE_HATCHES, apply_paper_style, panel_label, save_figure

BLUE = "#0072B2"
INK = "#202B33"
MUTED = "#56616A"
WIDTH = 7.2


def heading(fig, title, subtitle, left=.08):
    fig.suptitle(title, x=left, y=.972, ha="left", fontsize=11, weight="bold", color=INK)
    fig.text(left, .905, subtitle, fontsize=8, color=MUTED)


def finish(fig, name):
    for path in save_figure(fig, name):
        if path.suffix == ".pdf":
            (path.parent.parent / path.name).write_bytes(path.read_bytes())
        print(path)
    plt.close(fig)


def draw_coverage():
    data = task_coverage()
    fig = plt.figure(figsize=(WIDTH, 3.72))
    # Separate, explicit denominators: complete release on the left; the
    # consistently normalized mechanism subset on the right.
    left = fig.add_axes([.255, .20, .255, .63])
    ax = fig.add_axes([.645, .285, .323, .48])
    cax = fig.add_axes([.690, .195, .230, .020])
    fig.text(.024, .949, "(a) Functional families and lift types", fontsize=9.4, weight="bold", color=INK)
    fig.text(.024, .891, "Full release (n = 200)", fontsize=8.8, color=MUTED)
    fig.text(.575, .949, "(b) Entanglement coverage", fontsize=9.4, weight="bold", color=INK)
    fig.text(.575, .891, "Common comparison (n = 150)", fontsize=8.8, color=MUTED)
    lift_colors = {"Direct": "#0072B2", "Adapted": "#E69F00", "Composite": "#009E73"}
    families = data["feature_families"]
    y = np.arange(len(families))
    base = np.zeros(len(families))
    for lift, color in lift_colors.items():
        counts = np.array([f["lift_counts"][lift] for f in families])
        left.barh(y, counts, left=base, height=.70, color=color,
                  edgecolor="white", linewidth=.45)
        base += counts
    for i, family in enumerate(families):
        left.text(family["count"] + .9, i, str(family["count"]), va="center", fontsize=8.6, color=INK)
    left.set(yticks=y, yticklabels=[f["label"] for f in families],
             xlim=(0, 44), xticks=[0, 10, 20, 30, 40], xlabel="Tasks")
    left.invert_yaxis()
    left.tick_params(axis="y", length=0, pad=5, labelsize=7.6)
    left.tick_params(axis="x", length=3, labelsize=8)
    left.xaxis.label.set_size(8.5)
    left.spines["left"].set_visible(False)
    left.spines["bottom"].set_color("#A6AFB5")
    left.grid(axis="x", color="#E7ECF0", linewidth=.6)
    handles = [Patch(facecolor=color, label=f'{lift} ({data["release_lift_counts"][lift]})')
               for lift, color in lift_colors.items()]
    fig.legend(handles=handles, loc="lower left", bbox_to_anchor=(.021, .039),
               ncol=3, fontsize=7.8, columnspacing=1.15, handlelength=1.15,
               handletextpad=.45, borderaxespad=0)
    values = np.array([c["percent"] for c in data["cells"]]).reshape(3, 4)
    cmap = LinearSegmentedColormap.from_list("paper_blues", ["#F4F8FB", "#BBD9EB", "#4F96BE", "#075078"])
    im = ax.imshow(values, cmap=cmap, vmin=0, vmax=100, aspect="auto")
    for i in range(3):
        for j in range(4):
            cell = data["cells"][i * 4 + j]
            ax.text(j, i, f'{cell["percent"]:.0f}%\n{cell["count"]}/{cell["denominator"]}',
                    ha="center", va="center", fontsize=8.3, linespacing=1.75,
                    color="white" if values[i, j] >= 80 else INK)
    ax.set_xticks(range(4), ["Code\ndeps.", "Data /\nstate", "Framework\nmechanisms", "Env. /\nresources"])
    ax.set_yticks(range(3), ["Direct", "Adapted", "Composite"])
    ax.xaxis.tick_top()
    ax.tick_params(axis="both", which="major", length=0, pad=6, labelsize=7.8)
    ax.tick_params(axis="x", labelsize=7.2)
    ax.set_xticks(np.arange(-.5, 4, 1), minor=True)
    ax.set_yticks(np.arange(-.5, 3, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=2)
    ax.tick_params(which="minor", bottom=False, left=False, top=False, right=False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    cb = fig.colorbar(im, cax=cax, ticks=[0, 50, 100], orientation="horizontal")
    cb.outline.set_visible(False)
    cb.ax.set_xticklabels(["0%", "50%", "100%"])
    cb.ax.tick_params(length=2, labelsize=7.4, pad=3)
    fig.text(.804, .093, "Within-type coverage", ha="center", fontsize=8, color=MUTED)
    fig.text(.804, .043, "Mechanisms can overlap", ha="center", fontsize=7.7, color=MUTED)
    finish(fig, "figA_task_coverage")


def draw_functional():
    data = functional_results()
    fig, (left, right) = plt.subplots(1, 2, figsize=(WIDTH, 3.55), gridspec_kw={"width_ratios": [1.5, 1]})
    fig.subplots_adjust(left=.245, right=.98, bottom=.285, top=.815, wspace=.36)
    fig.text(.024, .949, "(a) First outcomes by configuration", fontsize=9.4, weight="bold", color=INK)
    fig.text(.024, .886, "Six configurations; 150 tasks each", fontsize=8.8, color=MUTED)
    fig.text(.725, .949, "(b) Task solve frequency", fontsize=9.4, weight="bold", color=INK)
    fig.text(.725, .886, "The same 150 tasks", fontsize=8.8, color=MUTED)
    values = np.array([r["counts"] for r in data["first_outcomes"]])
    base = np.zeros(6)
    for col, stage in enumerate(STAGE_ORDER):
        left.barh(np.arange(6), values[:, col], left=base, height=.65,
            color=STAGE_COLORS[stage], hatch=STAGE_HATCHES[stage], edgecolor="white", linewidth=.65)
        for y, count in enumerate(values[:, col]):
            if count >= 10:
                left.text(base[y] + count / 2, y, str(count), ha="center", va="center", fontsize=7.3,
                          color="white" if stage == "Pass" else INK,
                          bbox={"facecolor": STAGE_COLORS[stage], "edgecolor": "none", "pad": .3})
        base += values[:, col]
    left.set(yticks=np.arange(6), yticklabels=[BACKEND_FULL_NAMES[n] for n in BACKEND_ORDER], xlim=(0, 150), xticks=[0, 50, 100, 150], xlabel="Tasks")
    left.invert_yaxis()
    left.tick_params(axis="y", length=0)
    bins = data["solve_frequency"]
    right.bar(range(7), [r["task_count"] for r in bins], width=.68, color=BLUE, edgecolor="#315B73", linewidth=.5)
    for x, row in enumerate(bins):
        right.text(x, row["task_count"] + .9, str(row["task_count"]), ha="center", fontsize=8)
    right.set(xlabel="Passing configurations", ylabel="Tasks", xticks=range(7), ylim=(0, 42), yticks=[0, 10, 20, 30, 40])
    for ax in (left, right):
        ax.xaxis.label.set_size(8.5)
        ax.yaxis.label.set_size(8.5)
        ax.spines["bottom"].set_color("#89959D")
        ax.spines["left"].set_color("#89959D")
        ax.tick_params(axis="x", length=3)
    legend_labels = {"Pass": "Pass", "Missing": "No submission", "Build": "Build", "Public": "Public", "Hidden": "Hidden", "Isolation": "Isolation"}
    handles = [Patch(facecolor=STAGE_COLORS[k], edgecolor="#888888", hatch=STAGE_HATCHES[k], linewidth=.4, label=legend_labels[k]) for k in STAGE_ORDER]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.53, .100), ncol=6, columnspacing=1.0, handlelength=1.3, fontsize=8)
    failures = sum(sum(r["counts"][1:]) for r in data["first_outcomes"][:2])
    behavioral = sum(sum(r["counts"][3:5]) for r in data["first_outcomes"][:2])
    assert (behavioral, failures) == (76, 77)
    fig.text(.024, .034, f"Pro + Flash: {behavioral} of {failures} failures first occur at Public or Hidden.", fontsize=8, color=INK)
    finish(fig, "figB_functional_results")


def draw_footprint():
    data = footprint()
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH, 3.75), sharey=True)
    fig.subplots_adjust(left=.255, right=.978, bottom=.275, top=.810, wspace=.23)
    fig.text(.024, .949, "Paired artifact differences", fontsize=9.4, weight="bold", color=INK)
    fig.text(.024, .886, "Difference = configuration - DeepSeek V4 Pro; common successes within each pair", fontsize=8.5, color=MUTED)
    comparisons = data["comparisons"]
    # Hash-derived vertical offsets are shared across metrics; x stays exact.
    import hashlib
    offsets = {p["task_id"]: ((int(hashlib.sha256(p["task_id"].encode()).hexdigest()[:8], 16) / (2**32 - 1)) - .5) * .36
               for row in comparisons for p in row["points"]}
    for ax, metric, letter, title in zip(axes, ("rres", "copy"), ("a", "b"),
                                        ("Relative size (RRES)", "Source overlap (Copy)")):
        ax.axvline(0, color="#555555", linestyle="--", linewidth=.9, zorder=1)
        for index, row in enumerate(comparisons):
            values = np.array([p[f"delta_{metric}"] for p in row["points"]])
            yy = index + np.array([offsets[p["task_id"]] for p in row["points"]])
            ax.scatter(values, yy, s=12, color=BLUE, alpha=.38, edgecolors="none", zorder=2)
            summary = row["summaries"][metric]
            ax.plot([summary["q1"], summary["q3"]], [index, index], color=INK,
                    linewidth=2.5, solid_capstyle="round", zorder=3)
            ax.scatter([summary["median"]], [index], s=32, marker="D", color="#D58B24",
                       edgecolors=INK, linewidths=.55, zorder=4)
            ax.axhline(index + .5, color="#E9EDF0", linewidth=.5, zorder=0)
        if metric == "rres":
            ax.set_xscale("symlog", linthresh=.1, linscale=1, base=10)
            ax.set_xlim(-50, 50)
            ticks = [-10, -1, -.1, 0, .1, 1, 10]
            ax.set_xticks(ticks, ["−10", "−1", "−0.1", "0", "0.1", "1", "10"])
            ax.set_xlabel("RRES difference (symmetric log)", fontsize=8)
        else:
            ax.set_xlim(-1.035, 1.035)
            ax.set_xticks([-1, -.5, 0, .5, 1], ["−1", "−0.5", "0", "0.5", "1"])
            ax.set_xlabel("Copy difference (linear)", fontsize=8)
        low, high = ax.get_xlim()
        assert all(low <= p[f"delta_{metric}"] <= high for row in comparisons for p in row["points"])
        ax.set_ylim(4.5, -.5)
        ax.tick_params(axis="y", length=0)
        ax.tick_params(axis="x", length=3, labelsize=8)
        ax.spines["bottom"].set_color("#89959D")
        ax.spines["left"].set_visible(False)
        panel_label(ax, letter, title)
    axes[0].set_yticks(range(5), [f'{BACKEND_FULL_NAMES[row["backend"]]}\n(n = {row["common_passing_tasks"]})' for row in comparisons])
    handles = [Line2D([], [], marker="o", color=BLUE, linestyle="none", markersize=4, alpha=.5, label="Matched task"),
               Line2D([], [], marker="D", markerfacecolor="#D58B24", markeredgecolor=INK, markeredgewidth=.55,
                      linestyle="none", markersize=4.5, label="Median"),
               Line2D([], [], color=INK, linewidth=2.5, label="Interquartile range")]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.57, .106), ncol=3, columnspacing=1.6, fontsize=8)
    fig.text(.024, .036, "Negative: smaller artifact / less detected copying than DeepSeek V4 Pro.", fontsize=8, color=INK)
    finish(fig, "figC_paired_footprint")


def main():
    apply_paper_style()
    draw_coverage()
    draw_functional()
    draw_footprint()


if __name__ == "__main__":
    main()

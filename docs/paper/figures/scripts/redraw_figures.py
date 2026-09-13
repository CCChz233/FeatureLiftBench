"""Draw the revised A/B/C figure set; export PDF/PNG without compiling LaTeX."""
from figure_data import prepare_matplotlib
prepare_matplotlib()
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

from redraw_data import task_coverage, functional_results, footprint, source_ablation
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
    n = len(data['complete_tasks']) if 'complete_tasks' in data else data['release_tasks']
    assert n == data['release_tasks'] == data['mechanism_tasks'] == 150
    assert sum(f['count'] for f in data['feature_families']) == n
    assert sum(data['release_lift_counts'].values()) == n
    fig = plt.figure(figsize=(WIDTH, 3.72))
    # Both panels describe the same fixed 150-task benchmark.
    left = fig.add_axes([.255, .20, .255, .63])
    ax = fig.add_axes([.625, .20, .337, .60])
    fig.text(.024, .949, "(a) Functional families and lift types", fontsize=9.4, weight="bold", color=INK)
    fig.text(.024, .891, f"Benchmark (n = {n})", fontsize=8.8, color=MUTED)
    fig.text(.575, .949, "(b) Entanglement coverage", fontsize=9.4, weight="bold", color=INK)
    fig.text(.575, .891, f"Tasks covered / {n}; non-exclusive", fontsize=8.8, color=MUTED)
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
             xlim=(0, 36), xticks=[0, 10, 20, 30], xlabel="Tasks")
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
    marginals = data["mechanism_marginals"]
    assert [r["count"] for r in marginals] == [139, 127, 71, 49]
    yy = np.arange(4) * 1.25
    ax.barh(yy, [r["count"] for r in marginals], height=.30, color=BLUE)
    for y, row in zip(yy, marginals):
        ax.text(0, y - .29, row["mechanism"], fontsize=7.6, color=INK)
        ax.text(row["count"] - 3, y, f'{row["count"]} ({row["percent"]:.1f}%)',
                ha="right", va="center", color="white", fontsize=7.7, weight="bold")
    ax.set(xlim=(0, 150), ylim=(4.4, -.65), xticks=[0, 50, 100, 150],
           yticks=[], xlabel="Tasks")
    ax.grid(axis="x", color="#E7ECF0", linewidth=.6)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#A6AFB5")
    ax.tick_params(axis="x", length=3, labelsize=8)
    ax.xaxis.label.set_size(8.5)
    fig.text(.625, .045, "A task can involve multiple mechanisms.", fontsize=7.5, color=MUTED)
    finish(fig, "fig3")



def draw_functional():
    data = functional_results()
    fig, (left, right) = plt.subplots(1, 2, figsize=(WIDTH, 3.55), gridspec_kw={"width_ratios": [1.5, 1]})
    fig.subplots_adjust(left=.245, right=.98, bottom=.285, top=.815, wspace=.36)
    fig.text(.024, .949, "(a) Outcomes and first failed gates", fontsize=9.4, weight="bold", color=INK)
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
    legend_labels = {"Pass": "Pass", "Missing": "No submission", "Build": "Build", "Public": "Primary", "Hidden": "Extended", "Isolation": "Isolation"}
    handles = [Patch(facecolor=STAGE_COLORS[k], edgecolor="#888888", hatch=STAGE_HATCHES[k], linewidth=.4, label=legend_labels[k]) for k in STAGE_ORDER]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.53, .100), ncol=6, columnspacing=1.0, handlelength=1.3, fontsize=8)
    failures = sum(sum(r["counts"][1:]) for r in data["first_outcomes"][:2])
    behavioral = sum(sum(r["counts"][3:5]) for r in data["first_outcomes"][:2])
    assert (behavioral, failures) == (76, 77)
    fig.text(.024, .050, f"Pro + Flash: {behavioral} of {failures} failures first occur at Primary or Extended.", fontsize=8, color=INK)
    fig.text(.024, .015, "First failed gate indicates an observed boundary, not a causal diagnosis.", fontsize=7.5, color=MUTED)
    finish(fig, "fig4")


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
    finish(fig, "fig7")


def draw_source_ablation():
    data = source_ablation()
    from paper_inputs import MANIFEST
    names = {m["id"]: m["display"] for m in MANIFEST["models"]}
    fig = plt.figure(figsize=(WIDTH, 3.65))
    left = fig.add_axes([.268, .295, .305, .43])
    right = fig.add_axes([.705, .295, .263, .43], sharey=left)
    fig.text(.024, .953, "Effect of repository evidence", fontsize=10.5, weight="bold", color=INK)
    fig.text(.024, .892, "Same 40 tasks per configuration; missing submissions count as failures", fontsize=8.1, color=MUTED)
    fig.text(.268, .817, "(a) Functional pass rate", fontsize=8.8, weight="bold", color=INK)
    fig.text(.705, .817, "(b) Paired gain and 95% CI", fontsize=8.8, weight="bold", color=INK)
    labels = []
    for y, row in enumerate(data["results"]):
        is_pro = row["model"] == "deepseek-v4-pro"
        labels.append(names[row["model"]] + (" $\\dagger$" if is_pro else ""))
        for ax in (left, right):
            if is_pro:
                ax.axhspan(y - .46, y + .46, color="#F2F3F4", zorder=0)
        contract, full = [100 * row[k] / row["n"] for k in ("contract_pass", "full_pass")]
        left.plot([contract, full], [y, y], color=MUTED, linewidth=1.5,
                  linestyle="--" if is_pro else "-", zorder=2)
        left.scatter(contract, y, s=36, facecolors="white", edgecolors=INK, linewidths=1.2, zorder=3)
        left.scatter(full, y, s=36, marker="D", color=BLUE, edgecolors="white", linewidths=.6, zorder=3)
        left.text(contract, y + .26, f"{contract:.1f}%", ha="center", va="center", fontsize=8, color=INK)
        left.text(full, y - .26, f"{full:.1f}%", ha="center", va="center", fontsize=8, color=BLUE, weight="bold")
        lo, hi = row["paired_bootstrap_95ci_pp"]
        gain = row["delta_pp"]
        right.errorbar(gain, y, xerr=[[gain-lo], [hi-gain]], fmt="D", color=BLUE,
                       markersize=4.5, capsize=3, linewidth=1.3, zorder=3)
        right.text(gain, y - .26, f"+{gain:.1f} [{lo:.1f}, {hi:.1f}]", ha="center", va="center", fontsize=7.6, color=INK)
        right.text(gain, y + .27, f'Full-only / Contract-only: {row["full_only"]} / {row["contract_only"]}',
                   ha="center", va="center", fontsize=6.9, color=MUTED)
    left.set(yticks=range(3), yticklabels=labels, ylim=(2.55, -.55), xlim=(0, 100),
             xticks=[0, 25, 50, 75, 100], xlabel="Functional pass (%)")
    left.tick_params(axis="y", length=0, pad=8, labelsize=7.6)
    right.set(xlim=(0, 75), xticks=[0, 25, 50, 75], xlabel="Full minus Contract only (pp)")
    right.tick_params(axis="y", left=False, labelleft=False)
    right.axvline(0, color=MUTED, linestyle="--", linewidth=.7)
    for ax in (left, right):
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_color("#89959D")
        ax.tick_params(axis="x", labelsize=7.5, length=3)
        ax.xaxis.label.set_size(7.8)
        ax.grid(axis="x", color="#E7ECF0", linewidth=.5)
    handles = [Line2D([], [], marker="o", markerfacecolor="white", markeredgecolor=INK, linestyle="none", label="Contract only"),
               Line2D([], [], marker="D", color=BLUE, linestyle="none", label="Full source + contract")]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.55, .136), ncol=2, fontsize=8)
    fig.text(.024, .073, "$\\dagger$ Pro: 18 Contract-only submissions are missing with LLM timeouts; its gain includes interruptions.", fontsize=7.5, color=INK)
    fig.text(.024, .025, "Intervals quantify paired task variation; they do not remove timeout effects or estimate repeated-run variance.", fontsize=7.1, color=MUTED)
    finish(fig, "fig5")


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only', nargs='+', choices=('coverage', 'functional', 'footprint', 'ablation'),
                        default=['coverage', 'functional', 'footprint', 'ablation'])
    args = parser.parse_args()
    apply_paper_style()
    for name in args.only:
        {'coverage': draw_coverage, 'functional': draw_functional, 'footprint': draw_footprint,
         'ablation': draw_source_ablation}[name]()


if __name__ == "__main__":
    main()

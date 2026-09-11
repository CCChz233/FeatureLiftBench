"""Figure 3: exclusive first outcomes and pooled non-exclusive failure flags."""
from figure_data import failures, prepare_matplotlib
prepare_matplotlib()
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Patch
from paper_style import (BACKEND_ORDER, STAGE_ORDER, STAGE_COLORS, STAGE_HATCHES,
                         apply_paper_style, panel_label, save_figure)


def main():
    data = failures()
    apply_paper_style()
    fig, (left, right) = plt.subplots(1, 2, figsize=(7.2, 3.9),
        gridspec_kw={"width_ratios": [1.28, 1]})
    fig.subplots_adjust(left=.075, right=.97, bottom=.21, top=.74, wspace=.32)
    fig.suptitle("Failure outcomes on FeatureLiftBench", x=.075, y=.98, ha="left", fontsize=11, weight="bold")
    fig.text(.075, .918, "Six configurations · 150 assigned tasks each · 829 delivered artifacts in total", fontsize=8, color="#555555")
    values = np.array([r["counts"] for r in data["first_outcomes"]])
    base = np.zeros(6)
    for col, stage in enumerate(STAGE_ORDER):
        left.barh(np.arange(6), values[:, col], left=base, height=.64,
            color=STAGE_COLORS[stage], hatch=STAGE_HATCHES[stage], edgecolor="white", linewidth=.65)
        for y, count in enumerate(values[:, col]):
            if count >= 8:
                left.text(base[y]+count/2, y, str(count), ha="center", va="center", fontsize=7.5,
                          color="white" if stage == "Pass" else "#222222",
                          bbox={"facecolor": STAGE_COLORS[stage], "edgecolor": "none", "pad": .4})
        base += values[:, col]
    left.set(yticks=np.arange(6), yticklabels=BACKEND_ORDER, xlim=(0, 150),
             xticks=[0, 50, 100, 150], xlabel="Assigned tasks (count)")
    left.invert_yaxis()
    panel_label(left, "a", "First outcome (exclusive)")
    entries = data["gate_flags"]
    yy = np.arange(len(entries))
    right.barh(yy, [r["percent"] for r in entries], height=.56,
        color=[STAGE_COLORS[r["gate"]] for r in entries], edgecolor="#444444", linewidth=.5)
    for y, entry in enumerate(entries):
        right.text(entry["percent"]+1.1, y, f'{entry["percent"]:.1f}%  ({entry["failed"]}/829)',
                   va="center", fontsize=7.5)
    right.set(yticks=yy, yticklabels=[r["gate"] for r in entries], xlim=(0, 57),
              xticks=[0, 20, 40], xlabel="Delivered artifacts with failed flag (%)")
    right.invert_yaxis()
    panel_label(right, "b", "Gate flags (overlapping)")
    handles = [Patch(facecolor=STAGE_COLORS[k], edgecolor="#888888", hatch=STAGE_HATCHES[k],
                     linewidth=.4, label=k) for k in STAGE_ORDER]
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(.51, .895), ncol=6,
               columnspacing=1.35, handlelength=1.5)
    fig.text(.075, .072, "Isolation: 39 failed flags, but only 4 artifacts fail it after passing Build, Public and Hidden.", fontsize=8)
    fig.text(.075, .024, "First-failure order: Missing → Build → Public → Hidden → Isolation. Gate flags can overlap.", fontsize=7.5, color="#555555")
    for ax in (left, right):
        ax.tick_params(axis="y", length=0)
    for path in save_figure(fig, "fig03_failures"):
        print(path)
    plt.close(fig)


if __name__ == "__main__":
    main()

"""Figure 4: observed solve frequency without predefined difficulty groups."""
from figure_data import difficulty, prepare_matplotlib
prepare_matplotlib()
from matplotlib import pyplot as plt
from paper_style import apply_paper_style, save_figure


def main():
    data = difficulty()
    apply_paper_style()
    fig, ax = plt.subplots(figsize=(6.4, 3.7))
    fig.subplots_adjust(left=.10, right=.965, bottom=.23, top=.78)
    fig.suptitle("Task solve frequency on FeatureLiftBench", x=.10, y=.98,
                 ha="left", fontsize=11, weight="bold")
    fig.text(.10, .909, "150 evaluated tasks · 6 configurations · Full recorded outcomes",
             fontsize=8, color="#555555")
    xx = [r["passing_configurations"] for r in data["bins"]]
    counts = [r["task_count"] for r in data["bins"]]
    ax.bar(xx, counts, width=.64, color="#0072B2", edgecolor="#284E65", linewidth=.5)
    for x, count in zip(xx, counts):
        ax.text(x, count+.8, str(count), ha="center", va="bottom", fontsize=9)
    ax.set(xlabel="Number of passing configurations", ylabel="Tasks (count)",
           xticks=xx, ylim=(0, 41), yticks=[0, 10, 20, 30, 40])
    ax.tick_params(axis="x", length=3)
    fig.text(.10, .085, "28 tasks: no passing configuration   ·   105: mixed outcomes   ·   17: all six pass",
             fontsize=8)
    fig.text(.10, .026, "Observed outcomes, not fixed difficulty labels. Includes seven provisionally flagged tasks.",
             fontsize=7.3, color="#555555")
    for path in save_figure(fig, "fig04_difficulty"):
        print(path)
    plt.close(fig)


if __name__ == "__main__":
    main()

"""Fig. 4(c): mechanical-relocation diagnostic on the 40-task subset.

Produces one independent panel without an in-image title:

    fig04c_dse_comparison.pdf/png
        Diagnostic comparison of Luna Contract Only, mechanical relocation,
        and three Full Source agent runs.

Panel title belongs in the LaTeX caption.
"""

import csv
import json
import numpy as np
from matplotlib import pyplot as plt

from figure_common import BLUE, INK, finish, run_single
from paper_inputs import ROOT, input_path
import redraw_data
from redraw_data import source_ablation


PANEL = dict(
    figsize=(2.28, 1.86),
    left=0.31,
    right=0.94,
    bottom=0.30,
    top=0.97,
)


# ===========================================================================
# Frozen diagnostic data and paired 40-task ablation data
# ===========================================================================

def load_data(ablation=None):
    ablation = ablation or source_ablation()
    by_model = {row["model"]: row for row in ablation["results"]}
    assert len(by_model) == 3 and all(row["n"] == 40 for row in by_model.values())

    dse_path = ROOT / "experiments/dse/source_ablation40_v1_2_reviewed_20260926/functional_summary.json"
    dse = json.loads(dse_path.read_text())
    assert dse["schema"] == "featureliftbench.dse_functional_summary.v1"
    paired_path = input_path("source_ablation_statistics").parent / "paired_outcomes.csv"
    with paired_path.open(newline="", encoding="utf-8-sig") as stream:
        paired_tasks = {row["task_id"] for row in csv.DictReader(stream)}
    assert len(paired_tasks) == 40 == dse["all40"]["assigned"]
    assert {row["task_id"] for row in dse["tasks"]} == paired_tasks
    assert dse["all40"]["passed"] == sum(row["functional_pass"] for row in dse["tasks"])

    luna = by_model["gpt-5.6-luna"]
    pro = by_model["deepseek-v4-pro"]
    qwen = by_model["qwen3.6-35b-a3b-fp8"]
    counts = [("Luna CO", luna["contract_pass"], "spec"),
              ("Relocation", dse["all40"]["passed"], "relocation"),
              ("Luna", luna["full_pass"], "agent"),
              ("Pro", pro["full_pass"], "agent"),
              ("Qwen", qwen["full_pass"], "agent")]
    rows = [{"label": label, "pass_n": n, "rate": 100 * n / 40, "style": style}
            for label, n, style in counts]
    redraw_data.export("fig04c_diagnostic", {"task_count": 40, "rows": rows},
                       [dse_path, paired_path, input_path("source_ablation_statistics")])
    return rows


# ===========================================================================
# Drawing
# ===========================================================================

def draw_dse_comparison(ablation=None):

    rows = load_data(ablation)

    fig, ax = plt.subplots(
        figsize=PANEL["figsize"]
    )

    fig.subplots_adjust(
        left=PANEL["left"],
        right=PANEL["right"],
        bottom=PANEL["bottom"],
        top=PANEL["top"],
    )


    # Important:
    # matplotlib barh places larger y values higher.
    # Combined with invert_yaxis(), this gives:
    #
    # Luna Contract Only
    # Relocation
    #
    # Luna
    # Pro
    # Qwen

    y = np.array([
        3.30,
        2.65,
        1.55,
        0.90,
        0.25,
    ])


    # Colors

    spec_color = "#D9E0E5"
    spec_edge = "#65727B"

    relocation_color = "#B9C4CC"
    relocation_edge = "#56636C"

    agent_color = BLUE
    agent_edge = "white"


    bar_height = 0.40


    for yi, row in zip(y, rows):

        if row["style"] == "spec":

            color = spec_color
            edge = spec_edge
            text_color = INK
            weight = None


        elif row["style"] == "relocation":

            color = relocation_color
            edge = relocation_edge
            text_color = INK
            weight = None


        else:

            color = agent_color
            edge = agent_edge
            text_color = agent_color
            weight = "semibold"


        ax.barh(
            yi,
            row["rate"],
            height=bar_height,
            color=color,
            edgecolor=edge,
            linewidth=0.65,
            zorder=3,
        )


        ax.text(
            row["rate"] - 1.1 if row["style"] == "agent" else row["rate"] + 1.1,
            yi,
            f'{row["pass_n"]}/40',
            ha="right" if row["style"] == "agent" else "left",
            va="center",
            fontsize=6.7,
            color="white" if row["style"] == "agent" else text_color,
            weight=weight,
        )


    # ===========================================================================
    # Axes
    # ===========================================================================

    ax.set(
        yticks=y,
        yticklabels=[row["label"] for row in rows],
        ylim=(3.70, -0.10),
        xlim=(0, 100),
        xticks=[0, 25, 50, 75, 100],
        xlabel="Functional pass (%)",
    )

    # Critical for desired ordering
    ax.invert_yaxis()


    ax.tick_params(
        axis="y",
        length=0,
        pad=3,
        labelsize=6.8,
    )


    ax.tick_params(
        axis="x",
        length=3,
        labelsize=6.8,
    )


    ax.xaxis.label.set_size(7.0)
    ax.xaxis.labelpad = 2


    # ===========================================================================
    # Styling
    # ===========================================================================

    ax.set_axisbelow(True)

    ax.grid(
        axis="x",
        color="#E8EDF1",
        linewidth=0.5,
    )


    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)


    ax.spines["bottom"].set_color("#8E9AA3")
    ax.spines["bottom"].set_linewidth(0.7)


    finish(
        fig,
        "fig04c_dse_comparison"
    )


# ===========================================================================
# Entry point
# ===========================================================================

def draw_all():

    draw_dse_comparison()



def main():

    run_single(
        draw_all,
        __doc__
    )



if __name__ == "__main__":

    main()

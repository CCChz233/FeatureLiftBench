#!/usr/bin/env python3
"""Generate and execute the reproducible failure-attribution notebook."""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient


HERE = Path(__file__).resolve().parent
OUT = HERE / "failure_attribution_analysis.ipynb"


def code(source: str):
    return nbf.v4.new_code_cell(source.strip())


def md(source: str):
    return nbf.v4.new_markdown_cell(source.strip())


nb = nbf.v4.new_notebook()
nb["metadata"]["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
nb["metadata"]["language_info"] = {"name": "python", "version": "3.12"}
nb["cells"] = [
    md(
        """
# FeatureLiftBench failure attribution: 550 frozen OpenHands runs

This notebook compares competing bottleneck hypotheses rather than treating token use,
repeated reads, or dynamic labels as causal explanations. It rebuilds the stage-level
audit table from trajectories, evaluator logs, task metadata, oracle manifests, and the
150-task taxonomy. Hidden-test source is not used to derive agent-side behavior features.
"""
    ),
    md(
        """
## Definitions and evidence rules

- **Formal pass** is the frozen suite `run_status == passed` outcome.
- **Dynamic-runtime task (primary definition)** is outcome-blind and requires an annotated
  cross-call/module/process mechanism: dynamic import, global/session/lifecycle state,
  framework lifecycle, environment/config, or packaged-resource coupling. Local parser
  state alone is not sufficient.
- **Earliest failure stage** is a conservative rule-based attribution. Direct evaluator
  import/isolation failures are high confidence; dynamic semantics is at most medium
  confidence because runtime-state gold remains unresolved.
- **Repeated read** means the same source-repository file was viewed again; source files
  are immutable during a run, so these are known unchanged reads.
- Regression controls are descriptive: model, split, task snapshot LOC, reference LOC,
  public-test count, and entanglement count. Condensation and repeated reads are
  post-treatment trajectory variables and are never interpreted causally.
"""
    ),
    code(
        """
from pathlib import Path
import json, os, subprocess, sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path.cwd()
if not (HERE / "build_failure_attribution.py").is_file():
    HERE = HERE / "reports" / "failure_attribution_20260720"
os.environ.setdefault("MPLCONFIGDIR", "/tmp/flb-failure-mpl")
subprocess.run([sys.executable, str(HERE / "build_failure_attribution.py")], cwd=HERE, check=True)

df = pd.read_csv(HERE / "trajectory_stage_labels_550.csv")
stage = pd.read_csv(HERE / "failure_stage_distribution.csv")
funnel = pd.read_csv(HERE / "failure_funnel.csv")
outcome_funnel = pd.read_csv(HERE / "outcome_funnel.csv")
dynamic = pd.read_csv(HERE / "dynamic_comparison.csv")
dynamic_by = pd.read_csv(HERE / "dynamic_by_model_split.csv")
regression = pd.read_csv(HERE / "regression_results.csv")
cases = pd.read_csv(HERE / "representative_cases.csv")
quality = json.loads((HERE / "data_quality.json").read_text())
FIG = HERE / "figures"
FIG.mkdir(exist_ok=True)
quality
"""
    ),
    md("## Data quality and coverage"),
    code(
        """
assert len(df) == 550
assert df.run_id.nunique() == 550
assert df[["model", "task_id"]].drop_duplicates().shape[0] == 550
assert (df.total_tokens == df.prompt_tokens + df.completion_tokens).all()
assert int(df.events_available.sum()) == 550
assert int(df.evaluation_available.sum()) == 533

pd.DataFrame({
    "check": [
        "trajectory logs", "evaluator results", "taxonomy joins", "clean-install executions",
        "runtime/symbol gold completeness",
    ],
    "result": [
        "550/550", "533/550", "550/550", "0/550",
        "unresolved; stage labels are evidence-assisted, not human gold",
    ],
})
"""
    ),
    md(
        """
The largest measurement limitation is not token completeness—it is semantic ground truth.
All token/event records are present, but no run performed a real clean install and the
closure annotations explicitly leave symbol and runtime-state completeness unresolved.
"""
    ),
    md("## Outcome and diagnostic funnels"),
    code(
        """
fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))
for ax, data, title, color in [
    (axes[0], outcome_funnel, "Direct evaluator outcome funnel", "#315B7D"),
    (axes[1], funnel, "Strict evidence-qualified diagnostic funnel", "#9A6B2F"),
]:
    shown = data.iloc[::-1]
    ax.barh(shown.stage, shown.runs, color=color)
    for i, v in enumerate(shown.runs):
        ax.text(v + 7, i, f"{int(v)}", va="center", fontsize=9)
    ax.set_xlim(0, 590)
    ax.set_xlabel("runs")
    ax.set_title(title, loc="left", fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(FIG / "failure_funnels.png", dpi=180, bbox_inches="tight")
plt.show()
funnel
"""
    ),
    md(
        """
The diagnostic funnel is intentionally strict and not a second success-rate measure.
Only 106 formal passes also have every preceding trajectory-derived stage positively
observed. In particular, 216 runs have **unknown**, not failed, direct-dependency status.
The direct outcome funnel remains the authoritative 225/550 pass count.
"""
    ),
    md("## Earliest failure-stage distribution"),
    code(
        """
stage_total = stage.groupby("earliest_failure_stage", as_index=False).agg(
    failures=("failures", "sum"), median_tokens=("median_tokens", "median")
).sort_values("failures")
colors = ["#7A8793" if x == "evaluator_or_environment" else "#B45F3C" if x == "dynamic_semantics" else "#315B7D" for x in stage_total.earliest_failure_stage]
fig, ax = plt.subplots(figsize=(9, 5.5))
ax.barh(stage_total.earliest_failure_stage, stage_total.failures, color=colors)
for i, v in enumerate(stage_total.failures):
    ax.text(v + 1.5, i, f"{int(v)}", va="center")
ax.set_xlabel("non-pass runs attributed to earliest stage")
ax.set_title("Earliest observed failure stage", loc="left", fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(FIG / "failure_stage_distribution.png", dpi=180, bbox_inches="tight")
plt.show()
stage
"""
    ),
    md(
        """
Infrastructure failures (62) are retained in the 550 denominator but separated from agent
bottlenecks. Among 263 non-infrastructure failures, dependency/API closure and ordinary
implementation errors dominate. Dynamic-semantics candidates are a smaller, less certain
category; budget exhaustion is directly observed only for explicit step/timeout/workflow exits.
"""
    ),
    md("## Dynamic-runtime versus relatively static tasks"),
    code(
        """
primary = dynamic[dynamic.group.isin(["dynamic_runtime", "relatively_static"])].copy()
plot = primary.melt(
    id_vars="group",
    value_vars=["pass_rate", "hidden_failure_rate_given_public"],
    var_name="metric", value_name="rate",
)
labels = {"dynamic_runtime": "dynamic runtime", "relatively_static": "relatively static"}
metrics = ["pass_rate", "hidden_failure_rate_given_public"]
x = np.arange(len(metrics)); width = 0.34
fig, ax = plt.subplots(figsize=(8.5, 4.8))
for j, group in enumerate(["dynamic_runtime", "relatively_static"]):
    vals = [float(plot[(plot.group == group) & (plot.metric == m)].rate.iloc[0]) for m in metrics]
    ax.bar(x + (j - .5) * width, vals, width, label=labels[group], color=["#315B7D", "#A7B0B7"][j])
ax.set_xticks(x, ["formal pass", "hidden fail | public pass"])
ax.set_ylim(0, .6)
ax.set_ylabel("rate")
ax.yaxis.set_major_formatter(lambda y, _: f"{y:.0%}")
ax.legend(frameon=False)
ax.set_title("Primary dynamic-runtime comparison", loc="left", fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(FIG / "dynamic_static_comparison.png", dpi=180, bbox_inches="tight")
plt.show()
primary
"""
    ),
    code(
        """
dynamic_by[[
    "model", "split", "dynamic_runtime_task", "runs", "pass_rate",
    "hidden_failure_rate_given_public", "median_tokens", "repeat_read_affected_rate",
    "runtime_probe_rate", "fresh_final_verification_rate",
]].sort_values(["model", "split", "dynamic_runtime_task"])
"""
    ),
    md(
        """
The aggregate difference is near zero and changes across subsets: dynamic tasks underperform
within Core-100 cells but outperform within Hard50 cells where both groups perform poorly.
This interaction and the incomplete model×subset design make pooled causal claims unsafe.
"""
    ),
    md("## Adjusted observational models"),
    code("regression"),
    md(
        """
The primary adjusted odds ratio for **success** on dynamic tasks is 1.16 (95% CI 0.54–2.48).
The split interaction is large but extremely imprecise. Adding condensation and unchanged
repeated reads does not make either significant. These models rule out neither moderate harm
nor moderate benefit; they do rule out treating the observed labels as a demonstrated main cause.
"""
    ),
    md("## Capability, exploration policy, and memory/state management"),
    code(
        """
df[df.earliest_failure_stage.eq("dynamic_semantics")].groupby(
    ["failure_subtype", "attribution_confidence"], as_index=False
).agg(
    runs=("run_id", "size"), tasks=("task_id", "nunique"), median_tokens=("total_tokens", "median"),
    runtime_probes=("runtime_probe_count", "sum"), dynamic_probes=("dynamic_runtime_probe_count", "sum"),
    recognition_rate=("dynamic_dependency_recognized", "mean"),
)
"""
    ),
    md(
        """
Only two cases meet the weak memory-loss heuristic (dynamic information appeared before a
condensation, was absent later, and was not retained by the summary). That is not enough to
identify summarization as a root cause. Most dynamic candidates explicitly recognized the
mechanism and ran targeted probes, leaving capability versus ordinary implementation unresolved.
"""
    ),
    md("## Representative evidence cases"),
    code(
        """
cases[[
    "task_id", "model", "earliest_failure_stage", "failure_subtype",
    "missed_behavior_or_dependency", "agent_actual_behavior",
    "discovered_or_forgotten", "most_likely_intervention",
]]
"""
    ),
    md("## Evidence boundary and causal experiments"),
    md(
        """
### Supported now

- Direct evaluator attrition and outcome funnel counts.
- High-confidence API/dependency and forbidden-import failures.
- Explicit step/timeout/workflow truncation counts.
- Descriptive dynamic/static, condensation, token, probe, and repeated-read associations.

### Not supported now

- Dynamic-runtime coupling as the principal causal bottleneck.
- Repeated reads, high tokens, or condensation as causes of failure.
- A clean-install success rate: the evaluator used path imports in all 533 evaluated runs.
- A reliable memory-loss rate: summaries and runtime-state closure lack adjudicated gold.

### Required causal tests

1. Paired 2×2 on stratified dynamic/static tasks: default policy vs mandatory runtime probe;
   test the task-type×intervention interaction.
2. Dependency-hint arm vs runtime-trace arm vs extra-token arm with fixed model/task/seed and
   identical context window; attribute lift to closure, dynamic evidence, or budget.
3. Default condenser vs evidence-pinned memory at fixed token budget; pre-register retention,
   invalidation, and fresh-final-verification metrics.
4. Add a real wheel/venv clean-install gate before re-estimating packaging/boundary failures.
"""
    ),
]

nbf.write(nb, OUT)
client = NotebookClient(nb, timeout=600, kernel_name="python3", allow_errors=False)
client.execute(cwd=str(HERE))
nbf.write(nb, OUT)
print(OUT)

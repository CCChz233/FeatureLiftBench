#!/usr/bin/env python3
"""Independent consistency checks for the failure-attribution deliverables."""

from __future__ import annotations

import json
import re
from pathlib import Path

import nbformat
import pandas as pd


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = pd.read_csv(ROOT / "reports/token_efficiency_20260720/trajectory_records_550.csv")
AUDIT = pd.read_csv(HERE / "trajectory_stage_labels_550.csv")

checks: list[tuple[str, bool, str]] = []


def check(name: str, condition: bool, detail: str) -> None:
    checks.append((name, bool(condition), detail))


check("base row count", len(BASE) == 550, f"observed={len(BASE)}")
check("audit row count", len(AUDIT) == 550, f"observed={len(AUDIT)}")
check("unique run ids", AUDIT.run_id.nunique() == 550, f"observed={AUDIT.run_id.nunique()}")
check("model-task grain", AUDIT[["model", "task_id"]].drop_duplicates().shape[0] == 550, "expected=550")
check("token identity", bool((AUDIT.total_tokens == AUDIT.prompt_tokens + AUDIT.completion_tokens).all()), "all rows")

formal = BASE.run_status.eq("passed")
public = BASE.public_pass.map(lambda x: str(x).lower() == "true")
hidden = BASE.hidden_pass.map(lambda x: str(x).lower() == "true")
check("formal passes", int(formal.sum()) == 225, f"observed={formal.sum()}")
check("public passes", int(public.sum()) == 401, f"observed={public.sum()}")
check("hidden passes", int(hidden.sum()) == 228, f"observed={hidden.sum()}")
check("evaluator coverage", int(BASE.evaluation_available.sum()) == 533, f"observed={BASE.evaluation_available.sum()}")
check("failure stages sum", int((~AUDIT.formal_pass).sum()) == 325, f"stage_sum={AUDIT.loc[~AUDIT.formal_pass, 'earliest_failure_stage'].value_counts().sum()}")
check("infrastructure failures", int(AUDIT.earliest_failure_stage.eq("evaluator_or_environment").sum()) == 62, "expected=62")

condensation_runs = 0
condensation_events = 0
for rel in BASE.trajectory_path:
    count = 0
    with (ROOT / rel).open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            count += event.get("kind") == "Condensation"
    condensation_events += count
    condensation_runs += count > 0
check("condensation runs", condensation_runs == 288, f"observed={condensation_runs}")
check("condensation events", condensation_events == 552, f"observed={condensation_events}")

clean_install_executed = 0
context_windows: set[int] = set()
for _, row in BASE.iterrows():
    eval_path = ROOT / str(row.evaluation_path)
    if eval_path.is_file():
        result = json.loads(eval_path.read_text())
        phase = result.get("submission_install") or {}
        clean_install_executed += bool(phase and not phase.get("skipped"))
    usage_path = (ROOT / str(row.run_path)).parent / "agent/usage.json"
    usage = json.loads(usage_path.read_text())
    value = (usage.get("context_audit") or {}).get("context_window_tokens")
    if isinstance(value, int):
        context_windows.add(value)
check("clean install executions", clean_install_executed == 0, f"observed={clean_install_executed}")
check("context windows", context_windows == {131072, 204800}, f"observed={sorted(context_windows)}")

dynamic_counts = AUDIT.groupby("dynamic_runtime_task").formal_pass.agg(["size", "sum"]).to_dict("index")
check("dynamic group coverage", sum(v["size"] for v in dynamic_counts.values()) == 550, str(dynamic_counts))
check("representative case count", len(pd.read_csv(HERE / "representative_cases.csv")) == 16, "expected=16")

priorities = pd.read_csv(HERE / "module_improvement_priorities.csv")
expected_direct = {
    "Semantic closure planner": 85,
    "Implementation and repair loop": 80,
    "Budgeted exploration scheduler": 32,
    "Targeted runtime semantics engine": 43,
    "Boundary and packaging planner": 15,
    "Verification state machine": 2,
    "Evidence memory and condenser": 2,
    "Localization": 5,
}
observed_direct = priorities.set_index("module").direct_failures.to_dict()
check("module priority counts", observed_direct == expected_direct, f"observed={observed_direct}")
expected_ceilings = priorities.direct_failures / 550 * 100
check(
    "module ceiling arithmetic",
    bool((priorities.theoretical_ceiling_pp.sub(expected_ceilings).abs() < 0.01).all()),
    "ceiling=direct_failures/550*100",
)
check(
    "PoC threshold arithmetic",
    bool((priorities.twenty_percent_recovery_pp.sub(expected_ceilings * 0.2).abs() < 0.01).all()),
    "20% recovery column is a scenario, not a forecast",
)

artifact = json.loads((HERE / "artifact.json").read_text(encoding="utf-8"))
module_rows = artifact["snapshot"]["datasets"].get("module_priorities", [])
check("module artifact coverage", len(module_rows) == len(priorities), f"observed={len(module_rows)}")

cold_start = pd.read_csv(HERE / "cold_start_entry_actions.csv")
check("cold-start observed entry coverage", int(cold_start.runs.sum()) == 523, f"observed={cold_start.runs.sum()}")
check("cold-start within-five count", int(cold_start.loc[cold_start.action_band.ne(">5"), "runs"].sum()) == 475, "expected=475")
check("explicit closure plans", int(AUDIT.closure_plan_present.sum()) == 62, f"observed={AUDIT.closure_plan_present.sum()}")

nb = nbformat.read(HERE / "failure_attribution_analysis.ipynb", as_version=4)
code_cells = [cell for cell in nb.cells if cell.cell_type == "code"]
errors = [out for cell in code_cells for out in cell.get("outputs", []) if out.get("output_type") == "error"]
check("notebook executed", all(cell.get("execution_count") is not None for cell in code_cells), f"code_cells={len(code_cells)}")
check("notebook error free", not errors, f"errors={len(errors)}")

sensitive = re.compile(r"(?:sk-[A-Za-z0-9_-]{12,}|api[_-]?key\s*[=:]\s*['\"][^\[\s])", re.I)
text_outputs = []
for path in HERE.iterdir():
    if path.is_file() and path.suffix in {".md", ".csv", ".json"}:
        text_outputs.append(path.read_text(encoding="utf-8", errors="replace"))
check("no obvious secrets", not sensitive.search("\n".join(text_outputs)), "scanned md/csv/json outputs")

passed = sum(ok for _, ok, _ in checks)
status = "PASS" if passed == len(checks) else "FAIL"
lines = [
    "# Validation",
    "",
    f"**Status: {status} — {passed}/{len(checks)} checks passed.**",
    "",
    "| Check | Status | Detail |",
    "|---|---|---|",
]
for name, ok, detail in checks:
    lines.append(f"| {name} | {'PASS' if ok else 'FAIL'} | {detail} |")
lines.extend(
    [
        "",
        "The validation establishes arithmetic, coverage, notebook execution, and output hygiene. It does not validate the causal truth of heuristic stage labels; that requires blinded human adjudication and interventions.",
        "",
    ]
)
(HERE / "validation.md").write_text("\n".join(lines), encoding="utf-8")
print(status, f"{passed}/{len(checks)}")
if status != "PASS":
    raise SystemExit(1)

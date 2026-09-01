#!/usr/bin/env python3
"""Export exploratory analysis CSVs into LaTeX table snippets for the FSE draft.

Source of truth remains the Python-150 CSV tables and the Python-200' summary
JSON. Regenerated TeX is written to docs/paper/fse26/tables/. These tables are
not the Python-200' leaderboard.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from analyze_python150 import (
    MODEL_LABELS,
    MODEL_ORDER,
    RESULTS_CSV,
    SHORT_LABELS,
    TABLE_DIR,
    _as_bool,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
TEX_DIR = REPO_ROOT / "docs/paper/fse26/tables"
P200_SUMMARY = (
    REPO_ROOT / "reports/paper_analysis/python200_hard_main_20260829/summary.json"
)


def tex_escape(value: object) -> str:
    text = str(value)
    return (
        text.replace("\\", "\\textbackslash{}")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("_", "\\_")
        .replace("#", "\\#")
    )


def pct(rate: float, digits: int = 1) -> str:
    return f"{100.0 * float(rate):.{digits}f}\\%"


def ratio(passed: int, total: int, digits: int = 1) -> str:
    return f"{int(passed)}/{int(total)} ({pct(passed / total, digits)})"


def wilson_pct(low: float, high: float) -> str:
    return f"[{100.0 * float(low):.1f}, {100.0 * float(high):.1f}]"


def pvalue(value: float) -> str:
    number = float(value)
    if number == 0.0:
        return "$<10^{-19}$"
    if number >= 0.001:
        return f"{number:.3f}"
    exponent = f"{number:.2e}".replace("e-0", "e-").replace("e+0", "e+")
    mantissa, power = exponent.split("e")
    return f"${mantissa}\\times 10^{{{int(power)}}}$"


def write_tex(name: str, body: str) -> None:
    TEX_DIR.mkdir(parents=True, exist_ok=True)
    path = TEX_DIR / name
    path.write_text(body.strip() + "\n", encoding="utf-8")


def first_failure_stage(row: pd.Series) -> str:
    if not bool(row["evaluation_present"]):
        return "eval_missing"
    if not bool(row["build_pass"]):
        return "build"
    if not bool(row["public_pass"]):
        return "public"
    if not bool(row["hidden_pass"]):
        return "hidden"
    if not bool(row["isolation_pass"]):
        return "isolation"
    if bool(row["functional_pass"]):
        return "pass"
    return "other"


def load_results() -> pd.DataFrame:
    results = pd.read_csv(RESULTS_CSV)
    bool_columns = [
        "functional_pass",
        "build_pass",
        "public_pass",
        "hidden_pass",
        "isolation_pass",
        "evaluation_present",
        "context_violation",
    ]
    for column in bool_columns:
        results[column] = _as_bool(results[column])
    results["model_label"] = results["model"].map(MODEL_LABELS)
    results["first_failure"] = results.apply(first_failure_stage, axis=1)
    return results


def export_first_failure(results: pd.DataFrame) -> pd.DataFrame:
    stage_order = ["pass", "eval_missing", "build", "public", "hidden", "isolation", "other"]
    rows = []
    for model_id in MODEL_ORDER:
        subset = results[results["model"] == model_id]
        counts = subset["first_failure"].value_counts().to_dict()
        row = {
            "model": MODEL_LABELS[model_id],
            "model_short": SHORT_LABELS[MODEL_LABELS[model_id]],
            "assigned": int(len(subset)),
        }
        for stage in stage_order:
            row[stage] = int(counts.get(stage, 0))
        rows.append(row)
    frame = pd.DataFrame(rows)
    frame.to_csv(TABLE_DIR / "first_failure_summary.csv", index=False)
    return frame


def tab_python150_functional(models: pd.DataFrame) -> str:
    lines = [
        r"\begin{tabular}{lrrrrrr}",
        r"\toprule",
        r"\textbf{Model} & \textbf{Pass} & \textbf{Rate} & \textbf{Wilson 95\%} & \textbf{Eval missing} & \textbf{Context viol.} & \textbf{Run-status passed} \\",
        r"\midrule",
    ]
    for row in models.itertuples(index=False):
        lines.append(
            f"{tex_escape(row.model)} & {int(row.functional_pass)}/{int(row.assigned)} & "
            f"{pct(row.functional_rate)} & {wilson_pct(row.wilson_low, row.wilson_high)} & "
            f"{int(row.evaluation_missing)} & {int(row.context_violations)} & "
            f"{int(row.run_status_passed)} \\\\"
        )
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines)


def tab_python150_gates(gates: pd.DataFrame) -> str:
    order = ["Build", "Public", "Hidden", "Isolation", "Functional"]
    models = list(gates["model"].drop_duplicates())
    wide = gates.pivot(index="model", columns="gate", values="passed")
    lines = [
        r"\begin{tabular}{l" + "r" * len(order) + "}",
        r"\toprule",
        r"\textbf{Model} & " + " & ".join(rf"\textbf{{{g}}}" for g in order) + r" \\",
        r"\midrule",
    ]
    for model in models:
        cells = [tex_escape(model)]
        for gate in order:
            passed = int(wide.loc[model, gate])
            cells.append(f"{passed}/150")
        lines.append(" & ".join(cells) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines)


def tab_python150_compactness(models: pd.DataFrame) -> str:
    lines = [
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"\textbf{Model} & \textbf{$n$ pass} & \textbf{Median RRES} & \textbf{IQR} & \textbf{Median copy frac.} \\",
        r"\midrule",
    ]
    for row in models.itertuples(index=False):
        lines.append(
            f"{tex_escape(row.model)} & {int(row.functional_pass)} & "
            f"{row.pass_rres_median:.3f} & "
            f"[{row.pass_rres_q1:.3f}, {row.pass_rres_q3:.3f}] & "
            f"{row.pass_copy_fraction_median:.3f} \\\\"
        )
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines)


def tab_python150_cost(models: pd.DataFrame) -> str:
    lines = [
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"\textbf{Model} & \textbf{Median API calls} & \textbf{Mean API calls} & \textbf{Median completion tok.} & \textbf{Agent hours} \\",
        r"\midrule",
    ]
    for row in models.itertuples(index=False):
        lines.append(
            f"{tex_escape(row.model)} & {row.median_api_calls:.1f} & "
            f"{row.mean_api_calls:.1f} & {row.median_completion_tokens:.0f} & "
            f"{row.agent_hours:.1f} \\\\"
        )
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines)


def tab_python150_pairwise(pairs: pd.DataFrame) -> str:
    lines = [
        r"\begin{tabular}{llrrrrrr}",
        r"\toprule",
        r"\textbf{Left} & \textbf{Right} & \textbf{Both pass} & \textbf{Left only} & \textbf{Right only} & \textbf{Both fail} & \textbf{Left adv.} & \textbf{$p$} \\",
        r"\midrule",
    ]
    for row in pairs.itertuples(index=False):
        lines.append(
            f"{tex_escape(row.left)} & {tex_escape(row.right)} & "
            f"{int(row.both_pass)} & {int(row.left_only)} & {int(row.right_only)} & "
            f"{int(row.both_fail)} & {int(row.left_advantage)} & {pvalue(row.mcnemar_exact_p)} \\\\"
        )
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines)


def tab_python150_lift(lift: pd.DataFrame) -> str:
    lines = [
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"\textbf{Lift type} & \textbf{Tasks} & \textbf{Mean models solved} & \textbf{Mean solve frac.} & \textbf{Bootstrap 95\%} \\",
        r"\midrule",
    ]
    for row in lift.itertuples(index=False):
        lines.append(
            f"{tex_escape(row.lift_type)} & {int(row.tasks)} & "
            f"{row.mean_models_solved:.2f} & {pct(row.mean_solve_fraction)} & "
            f"{wilson_pct(row.bootstrap_low, row.bootstrap_high)} \\\\"
        )
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines)


def tab_python150_family(family: pd.DataFrame) -> str:
    lines = [
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"\textbf{Feature family} & \textbf{Tasks} & \textbf{Mean models solved} & \textbf{Mean solve frac.} & \textbf{Bootstrap 95\%} \\",
        r"\midrule",
    ]
    for row in family.itertuples(index=False):
        lines.append(
            f"{tex_escape(row.feature_family)} & {int(row.tasks)} & "
            f"{row.mean_models_solved:.2f} & {pct(row.mean_solve_fraction)} & "
            f"{wilson_pct(row.bootstrap_low, row.bootstrap_high)} \\\\"
        )
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines)


def tab_python150_solve_count(solve: pd.DataFrame) -> str:
    models = sorted(int(v) for v in solve["models_solved"].unique())
    lifts = list(solve["lift_type"].drop_duplicates())
    lines = [
        r"\begin{tabular}{l" + "r" * (len(models) + 1) + "}",
        r"\toprule",
        r"\textbf{Lift type} & "
        + " & ".join(rf"\textbf{{{k} models}}" for k in models)
        + r" & \textbf{Tasks} \\",
        r"\midrule",
    ]
    for lift in lifts:
        subset = solve[solve["lift_type"] == lift]
        total = int(subset["lift_total"].iloc[0])
        cells = [tex_escape(lift)]
        for k in models:
            match = subset[subset["models_solved"] == k]
            cells.append(str(int(match["tasks"].iloc[0])) if not match.empty else "0")
        cells.append(str(total))
        lines.append(" & ".join(cells) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines)


def tab_python150_task_matrix(tasks: pd.DataFrame) -> str:
    mark = {True: "Y", False: "--"}
    header = (
        r"\textbf{Task} & \textbf{Lift} & \textbf{D} & \textbf{Q5} & \textbf{Q6} & \textbf{O} & \textbf{\#} \\"
    )
    renamed = tasks.rename(
        columns={
            "DeepSeek": "deepseek",
            "Qwen3.5": "qwen35",
            "Qwen3.6": "qwen36",
            "GPT-OSS": "gptoss",
        }
    )
    for column in ("deepseek", "qwen35", "qwen36", "gptoss"):
        renamed[column] = _as_bool(renamed[column])
    lines = [
        r"\begin{longtable}{p{0.46\textwidth}lccccr}",
        r"\caption{Task-level Functional Pass on the exploratory frozen Python-150 matrix.",
        r"D~=~DeepSeek V4 Flash, Q5~=~Qwen3.5 122B, Q6~=~Qwen3.6 35B, O~=~GPT-OSS 120B.",
        r"Missing evaluator records are counted as non-passes.}",
        r"\label{tab:python150-task-matrix} \\",
        r"\toprule",
        header,
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        header,
        r"\midrule",
        r"\endhead",
        r"\bottomrule",
        r"\endfoot",
    ]
    for row in renamed.itertuples(index=False):
        lines.append(
            rf"\texttt{{\detokenize{{{row.task_id}}}}} & {tex_escape(row.lift_type)} & "
            f"{mark[bool(row.deepseek)]} & {mark[bool(row.qwen35)]} & "
            f"{mark[bool(row.qwen36)]} & {mark[bool(row.gptoss)]} & "
            f"{int(row.models_solved)} \\\\"
        )
    lines.append(r"\end{longtable}")
    return "\n".join(lines)


def python200_tables(summary: dict) -> dict[str, str]:
    h = summary["headline"]
    splits = summary["by_split"]
    audit = [
        r"\begin{tabular}{lrrr}",
        r"\toprule",
        r"\textbf{Scope} & \textbf{Pass} & \textbf{Assigned} & \textbf{Raw rate} \\",
        r"\midrule",
        rf"Python-150 & {splits['python150']['passed']} & {splits['python150']['total']} & {pct(splits['python150']['rate'])} \\",
        rf"Hard-50 & {splits['hard50']['passed']} & {splits['hard50']['total']} & {pct(splits['hard50']['rate'])} \\",
        rf"Python-200$'$ received package & {h['passed']} & {h['total']} & {pct(h['rate'])} \\",
        r"\bottomrule",
        r"\end{tabular}",
    ]
    elig = summary["eligibility"]
    eligibility = [
        r"\begin{tabular}{lrr}",
        r"\toprule",
        r"\textbf{Partition} & \textbf{Tasks} & \textbf{Passes} \\",
        r"\midrule",
        rf"Agent launched & {elig['agent_attempted']} & -- \\",
        rf"Freeze preflight blocked & {elig['freeze_preflight_blocked']} & 0 \\",
        rf"Dependency-install infrastructure & {elig['dependency_install_failures']} & 0 \\",
        rf"Context-window audit violations & {elig['context_violation_runs']} & {summary['context_audit']['violation_passes']} \\",
        rf"Strict replacement union & {elig['strict_rerun_union']} & unknown \\",
        rf"Fixed subset retained & {elig['fixed_eligible_tasks']} & {elig['fixed_eligible_passes']} \\",
        r"\bottomrule",
        r"\end{tabular}",
    ]
    classes = summary["audit_failure_classes"]
    failure = [
        r"\begin{tabular}{lr}",
        r"\toprule",
        r"\textbf{Outcome class} & \textbf{Tasks} \\",
        r"\midrule",
        rf"Functional pass & {classes['pass']} \\",
        rf"Public behavior & {classes['public_behavior']} \\",
        rf"Hidden-only behavior & {classes['hidden_only_behavior']} \\",
        rf"Agent no-submission & {classes['agent_no_submission']} \\",
        rf"Freeze preflight blocked & {classes['freeze_preflight_blocked']} \\",
        rf"Offline dependency unavailable & {classes['dependency_install_infrastructure']} \\",
        r"\bottomrule",
        r"\end{tabular}",
    ]
    lifts = summary["by_lift_type"]
    lift_rows = [
        r"\begin{tabular}{lrrr}",
        r"\toprule",
        r"\textbf{Lift type} & \textbf{Pass} & \textbf{Assigned} & \textbf{Wilson 95\%} \\",
        r"\midrule",
    ]
    for name in ("Direct", "Adapted", "Composite"):
        item = lifts[name]
        lift_rows.append(
            rf"{name} & {item['passed']} & {item['total']} & {wilson_pct(*item['wilson_95'])} \\"
        )
    lift_rows += [r"\bottomrule", r"\end{tabular}"]
    compact = summary["compactness"]
    compactness = [
        r"\begin{tabular}{lrr}",
        r"\toprule",
        r"\textbf{Split} & \textbf{$n$ pass} & \textbf{Median RRES} \\",
        r"\midrule",
        rf"Python-150 (received) & {splits['python150']['passed']} & {compact['pass_rres_median_by_split']['python150']:.3f} \\",
        rf"Hard-50 (received) & {splits['hard50']['passed']} & {compact['pass_rres_median_by_split']['hard50']:.3f} \\",
        rf"Python-200$'$ received passes & {h['passed']} & {compact['pass_rres_median']:.3f} \\",
        r"\bottomrule",
        r"\end{tabular}",
    ]
    ctx = summary["context_audit"]
    context = [
        r"\begin{tabular}{lrrr}",
        r"\toprule",
        r"\textbf{Slice} & \textbf{Pass} & \textbf{Assigned} & \textbf{Wilson 95\%} \\",
        r"\midrule",
        rf"Context-compliant attempted runs & {ctx['compliant_rate']['passed']} & {ctx['compliant_rate']['total']} & {wilson_pct(*ctx['compliant_rate']['wilson_95'])} \\",
        rf"Context-violation runs & {ctx['violation_rate']['passed']} & {ctx['violation_rate']['total']} & {wilson_pct(*ctx['violation_rate']['wilson_95'])} \\",
        rf"Preflight unavailable & {ctx['unavailable_rate']['passed']} & {ctx['unavailable_rate']['total']} & {wilson_pct(*ctx['unavailable_rate']['wilson_95'])} \\",
        r"\bottomrule",
        r"\end{tabular}",
    ]
    stages = summary["failure_stages"]
    stages_tex = [
        r"\begin{tabular}{lrr}",
        r"\toprule",
        r"\textbf{Recorded first outcome} & \textbf{Python-150} & \textbf{Hard-50} \\",
        r"\midrule",
    ]
    by_split = summary["failure_stages_by_split"]
    for key, label in (
        ("pass", "Pass"),
        ("missing_submission", "Missing"),
        ("build", "Build"),
        ("public", "Public"),
        ("hidden", "Hidden"),
    ):
        p150 = int(by_split["python150"].get(key, 0))
        h50 = int(by_split["hard50"].get(key, 0))
        stages_tex.append(rf"{label} & {p150} & {h50} \\")
    stages_tex += [r"\bottomrule", r"\end{tabular}"]
    return {
        "tab_python200_audit.tex": "\n".join(audit),
        "tab_python200_eligibility.tex": "\n".join(eligibility),
        "tab_python200_failure_classes.tex": "\n".join(failure),
        "tab_python200_lift_candidate.tex": "\n".join(lift_rows),
        "tab_python200_compactness_candidate.tex": "\n".join(compactness),
        "tab_python200_context.tex": "\n".join(context),
        "tab_python200_stages_received.tex": "\n".join(stages_tex),
    }


def main() -> None:
    models = pd.read_csv(TABLE_DIR / "model_summary.csv")
    gates = pd.read_csv(TABLE_DIR / "gate_summary.csv")
    compactness = pd.read_csv(TABLE_DIR / "compactness_summary.csv")
    pairs = pd.read_csv(TABLE_DIR / "pairwise_comparisons.csv")
    lift = pd.read_csv(TABLE_DIR / "lift_type_summary.csv")
    family = pd.read_csv(TABLE_DIR / "feature_family_summary.csv")
    solve = pd.read_csv(TABLE_DIR / "solve_count_by_lift.csv")
    tasks = pd.read_csv(TABLE_DIR / "task_difficulty.csv")
    results = load_results()
    first_fail = export_first_failure(results)
    # pandas names `pass` as a column; itertuples mangles it.
    first_fail = first_fail.rename(columns={"pass": "pass_count"})

    write_tex("tab_python150_functional.tex", tab_python150_functional(models))
    write_tex("tab_python150_gates.tex", tab_python150_gates(gates))
    # rebuild first-fail tex with renamed column
    lines = [
        r"\begin{tabular}{lrrrrrrr}",
        r"\toprule",
        r"\textbf{Model} & \textbf{Pass} & \textbf{Eval missing} & \textbf{Build} & \textbf{Public} & \textbf{Hidden} & \textbf{Isolation} & \textbf{Other} \\",
        r"\midrule",
    ]
    for row in first_fail.itertuples(index=False):
        lines.append(
            f"{tex_escape(row.model)} & {int(row.pass_count)} & {int(row.eval_missing)} & "
            f"{int(row.build)} & {int(row.public)} & {int(row.hidden)} & "
            f"{int(row.isolation)} & {int(row.other)} \\\\"
        )
    lines += [r"\bottomrule", r"\end{tabular}"]
    write_tex("tab_python150_firstfail.tex", "\n".join(lines))
    write_tex("tab_python150_compactness.tex", tab_python150_compactness(compactness))
    write_tex("tab_python150_cost.tex", tab_python150_cost(models))
    write_tex("tab_python150_pairwise.tex", tab_python150_pairwise(pairs))
    write_tex("tab_python150_lift.tex", tab_python150_lift(lift))
    write_tex("tab_python150_family.tex", tab_python150_family(family))
    write_tex("tab_python150_solve_count.tex", tab_python150_solve_count(solve))
    write_tex("tab_python150_task_matrix.tex", tab_python150_task_matrix(tasks))

    summary = json.loads(P200_SUMMARY.read_text(encoding="utf-8"))
    for name, body in python200_tables(summary).items():
        write_tex(name, body)

    manifest = {
        "python150_source": str(TABLE_DIR.relative_to(REPO_ROOT)),
        "python200_source": str(P200_SUMMARY.relative_to(REPO_ROOT)),
        "tex_dir": str(TEX_DIR.relative_to(REPO_ROOT)),
        "note": "Exploratory/candidate tables only. Not the Python-200' leaderboard.",
    }
    (TEX_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote {len(list(TEX_DIR.glob('*.tex')))} tex tables to {TEX_DIR}")


if __name__ == "__main__":
    main()

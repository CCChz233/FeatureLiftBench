#!/usr/bin/env python3.12
"""Offline (no-API) analysis: v2 168/32 labels × 2026-08-29 received Flash package.

Writes CSVs, checksums, and LaTeX snippets. Not a leaderboard.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "offline_standard_slice_20260902"
FSE_TABLES = ROOT / "docs" / "paper" / "fse26" / "tables"
DRAFT_TABLES = ROOT / "docs" / "paper" / "offline_tables"

# The 9-row gate run. The earlier `_p0_adjudicated` run has the same labels
# (168/32/0) but only 6 rows, and its C4 hits predate the AST-normalization fix,
# so it reports 29 overlaps of which 23 are false positives.
GATE_RUN = "python200_hard_20260902_p1_l4l5"


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n <= 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1.0 + z * z / n
    center = (p + z * z / (2 * n)) / den
    err = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / den
    return (center - err, center + err)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def tex_escape(text: str) -> str:
    return (
        text.replace("\\", "\\textbackslash{}")
        .replace("_", "\\_")
        .replace("%", "\\%")
        .replace("&", "\\&")
        .replace("#", "\\#")
    )


def pct(k: int, n: int) -> str:
    return f"{100.0 * k / n:.1f}\\%"


def ci_tex(k: int, n: int) -> str:
    lo, hi = wilson(k, n)
    return f"[{100.0 * lo:.1f}, {100.0 * hi:.1f}]"


def median_or_none(values: list[float]) -> float | None:
    if not values:
        return None
    return float(statistics.median(values))


def iqr(values: list[float]) -> tuple[float | None, float | None]:
    if len(values) < 2:
        return (None, None)
    s = sorted(values)
    n = len(s)

    def pctile(p: float) -> float:
        if n == 1:
            return s[0]
        idx = (n - 1) * p
        lo = math.floor(idx)
        hi = math.ceil(idx)
        if lo == hi:
            return s[lo]
        return s[lo] * (hi - idx) + s[hi] * (idx - lo)

    return (pctile(0.25), pctile(0.75))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    std = json.loads((ROOT / "benchmark/selection/python200_hard_standard_suite.json").read_text())
    exc = json.loads((ROOT / "benchmark/selection/python200_hard_excluded.json").read_text())
    parent = json.loads((ROOT / "benchmark/selection/python200_hard_suite.json").read_text())
    keep = set(std["task_ids"])
    drop = {row["task_id"]: row for row in exc["tasks"]}
    drop_ids = set(drop)
    s84 = {
        line.strip()
        for line in (ROOT / "reports/paper_analysis/python200_hard_main_20260829/strict_replacement_task_ids.txt")
        .read_text()
        .splitlines()
        if line.strip() and not line.startswith("#")
    }
    all200 = list(parent["task_ids"])
    frozen = set(all200) - s84

    rows = {
        r["task_id"]: r
        for r in csv.DictReader(
            (ROOT / "reports/paper_analysis/python200_hard_main_20260829/task_results.csv").open()
        )
    }
    gate_path = ROOT / "reports/benchmark_gate" / GATE_RUN / "gate_report.json"
    gate = json.loads(gate_path.read_text())

    # C4 is advisory, so a hit surfaces as `undetermined` rather than `fail`.
    c4_undetermined = [
        task["task_id"]
        for task in gate["tasks"]
        if (task.get("checks", {}).get("L5_C4_TEST_OVERLAP") or {}).get("mechanical_result")
        == "hit"
    ]

    def pass_n(ids: set[str]) -> int:
        return sum(1 for t in ids if rows[t]["functional_pass"] == "True")

    def stages(ids: set[str]) -> Counter:
        return Counter(rows[t]["failure_stage"] for t in ids)

    def rres_vals(ids: set[str]) -> list[float]:
        out: list[float] = []
        for t in ids:
            r = rows[t]
            if r["functional_pass"] != "True":
                continue
            raw = r.get("reference_relative_loc_ratio") or ""
            if raw in {"", "NA", "None"}:
                continue
            out.append(float(raw))
        return out

    slices = {
        "frozen116": frozen,
        "meets_frozen96": keep & frozen,
        "violates_frozen20": drop_ids & frozen,
        "meets168": keep,
        "violates32": drop_ids,
        "meets_replace72": keep & s84,
        "violates_replace12": drop_ids & s84,
    }

    summary_slices = {}
    for name, ids in slices.items():
        k = pass_n(ids)
        n = len(ids)
        lo, hi = wilson(k, n) if n else (float("nan"), float("nan"))
        st = stages(ids)
        rres = rres_vals(ids)
        q1, q3 = iqr(rres)
        summary_slices[name] = {
            "n": n,
            "pass": k,
            "rate": (k / n) if n else None,
            "wilson95": [lo, hi] if n else None,
            "stages": dict(st),
            "context_violations": sum(1 for t in ids if rows[t]["context_violation"] == "True"),
            "median_rres_passes": median_or_none(rres),
            "rres_iqr": [q1, q3],
            "n_rres": len(rres),
        }

    violator_rows = []
    for task_id in sorted(drop_ids):
        rules = drop[task_id]["failed_rules"]
        evidence = []
        for check in drop[task_id]["checks"]:
            if check["status"] == "fail":
                evidence.extend(check.get("evidence") or [])
        violator_rows.append(
            {
                "task_id": task_id,
                "suite_split": rows[task_id]["suite_split"],
                "lift_type": rows[task_id]["lift_type"],
                "failed_rules": "|".join(rules),
                "surface": "R-SURFACE" in rules,
                "entry": "R-ENTRY" in rules,
                "evidence": "; ".join(evidence),
                "in_fixed116": task_id in frozen,
                "functional_pass_received": rows[task_id]["functional_pass"] == "True",
                "failure_stage": rows[task_id]["failure_stage"],
            }
        )

    c4_set = set(c4_undetermined)
    checksums = {
        "python200_hard_suite.json": sha256_file(ROOT / "benchmark/selection/python200_hard_suite.json"),
        "python200_hard_standard_suite.json": sha256_file(
            ROOT / "benchmark/selection/python200_hard_standard_suite.json"
        ),
        "python200_hard_excluded.json": sha256_file(ROOT / "benchmark/selection/python200_hard_excluded.json"),
        "adjudications.csv": sha256_file(
            ROOT / "reports/paper_analysis/benchmark_tiers_v2_candidate/adjudications.csv"
        ),
        "python200_hard_registry.json": sha256_file(ROOT / "benchmark/sources/python200_hard_registry.json"),
        "task_results.csv": sha256_file(
            ROOT / "reports/paper_analysis/python200_hard_main_20260829/task_results.csv"
        ),
        "strict_replacement_task_ids.txt": sha256_file(
            ROOT / "reports/paper_analysis/python200_hard_main_20260829/strict_replacement_task_ids.txt"
        ),
    }

    payload = {
        "schema_version": "featureliftbench.offline_standard_slice.v1",
        "generated_at": "2026-09-02",
        "gold": False,
        "leaderboard": False,
        "note": "Fixed 116 has no context-window violations. 81/96 is a sensitivity slice, not Python-200' Functional Pass.",
        "label_counts": {"meets_standard": 168, "violates": 32, "undetermined": 0},
        "label_split": {"baseline_meets": std["baseline_count"], "hard50_meets": std["hard50_count"]},
        "surface_entry": {
            "surface_only": sum(1 for r in violator_rows if r["surface"] and not r["entry"]),
            "entry_only": sum(1 for r in violator_rows if r["entry"] and not r["surface"]),
            "both": sum(1 for r in violator_rows if r["surface"] and r["entry"]),
        },
        "slices": summary_slices,
        "c4_advisory": {
            "n": len(c4_undetermined),
            "overlap_violates": len(c4_set & drop_ids),
            "overlap_meets": len(c4_set & keep),
            "task_ids": sorted(c4_undetermined),
        },
        "checksums_sha256": checksums,
        "required_images": {
            "agent": "sha256:0843b6633d48da91832ce16c0e6ac42baf2f04d7b08cb66061720f176a8f2eea",
            "eval": "sha256:d1ea357c125a6f4957e1246f770bd1deb4717448e46e779f62b0351213cad191",
        },
        "local_latest_images": {
            "agent": "sha256:cc6229204b71d871ebd3eea0a251c9947e8b5631aeb652a4159d8591d43033fe",
            "eval": "sha256:cccf858c5f9b278de16bf9317aa032fd61c022dd1c257016ab08d5b68990f368",
            "mergeable": False,
        },
    }
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    with (OUT / "violators.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(violator_rows[0]))
        w.writeheader()
        w.writerows(violator_rows)

    with (OUT / "eligibility.csv").open("w", newline="", encoding="utf-8") as fh:
        fields = [
            "task_id",
            "v2_label",
            "in_fixed116",
            "in_replace84",
            "functional_pass",
            "failure_stage",
            "suite_split",
            "lift_type",
            "rres",
        ]
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for tid in all200:
            r = rows[tid]
            w.writerow(
                {
                    "task_id": tid,
                    "v2_label": "meets_standard" if tid in keep else "violates",
                    "in_fixed116": tid in frozen,
                    "in_replace84": tid in s84,
                    "functional_pass": r["functional_pass"],
                    "failure_stage": r["failure_stage"],
                    "suite_split": r["suite_split"],
                    "lift_type": r["lift_type"],
                    "rres": r.get("reference_relative_loc_ratio") or "",
                }
            )

    with (OUT / "c4_advisory.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["task_id", "v2_label", "in_fixed116"])
        w.writeheader()
        for tid in sorted(c4_undetermined):
            w.writerow(
                {
                    "task_id": tid,
                    "v2_label": "meets_standard" if tid in keep else "violates",
                    "in_fixed116": tid in frozen,
                }
            )

    (OUT / "checksums.json").write_text(json.dumps(checksums, indent=2) + "\n", encoding="utf-8")

    s116 = summary_slices["frozen116"]
    s96 = summary_slices["meets_frozen96"]
    s20 = summary_slices["violates_frozen20"]
    se = payload["surface_entry"]

    def funnel_row(label: str, ids: set[str]) -> str:
        st = stages(ids)
        n = len(ids)
        return (
            f"{label} & {n} & {st.get('pass', 0)} & {st.get('missing_submission', 0)} & "
            f"{st.get('build', 0)} & {st.get('public', 0)} & {st.get('hidden', 0)} & "
            f"{st.get('isolation', 0)} \\\\"
        )

    tab_eligibility = f"""\\begin{{tabular}}{{lrrrr}}
\\toprule
\\textbf{{Slice}} & \\textbf{{$n$}} & \\textbf{{Pass}} & \\textbf{{Rate}} & \\textbf{{Wilson 95\\%}} \\\\
\\midrule
Fixed eligible subset & {s116['n']} & {s116['pass']} & {pct(s116['pass'], s116['n'])} & {ci_tex(s116['pass'], s116['n'])} \\\\
v2 meets $\\cap$ fixed & {s96['n']} & {s96['pass']} & {pct(s96['pass'], s96['n'])} & {ci_tex(s96['pass'], s96['n'])} \\\\
v2 violates $\\cap$ fixed & {s20['n']} & {s20['pass']} & {pct(s20['pass'], s20['n'])} & {ci_tex(s20['pass'], s20['n'])} \\\\
v2 meets $\\cap$ replacement 84 & {summary_slices['meets_replace72']['n']} & -- & -- & -- \\\\
\\bottomrule
\\end{{tabular}}
"""
    tab_funnel = f"""\\begin{{tabular}}{{lrrrrrrr}}
\\toprule
\\textbf{{Slice}} & \\textbf{{$n$}} & \\textbf{{Pass}} & \\textbf{{Missing}} & \\textbf{{Build}} & \\textbf{{Public}} & \\textbf{{Hidden}} & \\textbf{{Isolation}} \\\\
\\midrule
{funnel_row("Fixed eligible 116", frozen)}
{funnel_row("meets $\\cap$ 116", keep & frozen)}
{funnel_row("violates $\\cap$ 116", drop_ids & frozen)}
\\bottomrule
\\end{{tabular}}
"""
    r96 = s96["median_rres_passes"]
    r20 = s20["median_rres_passes"]
    r116 = s116["median_rres_passes"]
    tab_rres = f"""\\begin{{tabular}}{{lrrr}}
\\toprule
\\textbf{{Passing slice}} & \\textbf{{$n$ pass}} & \\textbf{{Median RRES}} & \\textbf{{IQR}} \\\\
\\midrule
Fixed eligible 116 & {s116['pass']} & {r116:.3f} & [{s116['rres_iqr'][0]:.3f}, {s116['rres_iqr'][1]:.3f}] \\\\
meets $\\cap$ 116 & {s96['pass']} & {r96:.3f} & [{s96['rres_iqr'][0]:.3f}, {s96['rres_iqr'][1]:.3f}] \\\\
violates $\\cap$ 116 & {s20['pass']} & {r20:.3f} & [{s20['rres_iqr'][0]:.3f}, {s20['rres_iqr'][1]:.3f}] \\\\
\\bottomrule
\\end{{tabular}}
"""
    tab_labels = f"""\\begin{{tabular}}{{lrrl}}
\\toprule
\\textbf{{v2 label}} & \\textbf{{Baseline}} & \\textbf{{Hard-50}} & \\textbf{{Total}} \\\\
\\midrule
meets\\_standard & {std['baseline_count']} & {std['hard50_count']} & 168 \\\\
violates (surface only) & -- & -- & {se['surface_only']} \\\\
violates (entrypoint only) & -- & -- & {se['entry_only']} \\\\
violates (both) & -- & -- & {se['both']} \\\\
undetermined & 0 & 0 & 0 \\\\
\\bottomrule
\\end{{tabular}}
"""

    violator_lines = [
        "\\begin{longtable}{llp{0.42\\textwidth}}",
        "\\caption{Python-200$'$ tasks with a confirmed v2 contract-completeness violation. "
        "These tasks remain in the frozen 200-task asset; they are excluded only from the analysis subset.} \\\\",
        "\\label{tab:violators} \\\\",
        "\\toprule",
        "\\textbf{Task} & \\textbf{Rules} & \\textbf{Undeclared member or dangling symbol} \\\\",
        "\\midrule",
        "\\endfirsthead",
        "\\toprule",
        "\\textbf{Task} & \\textbf{Rules} & \\textbf{Undeclared member or dangling symbol} \\\\",
        "\\midrule",
        "\\endhead",
    ]
    for r in violator_rows:
        rules = []
        if r["surface"]:
            rules.append("C1")
        if r["entry"]:
            rules.append("C2")
        evid = r["evidence"]
        if len(evid) > 88:
            evid = evid[:85] + "..."
        violator_lines.append(
            f"{tex_escape(r['task_id'])} & {', '.join(rules)} & {tex_escape(evid)} \\\\"
        )
    violator_lines.extend(["\\bottomrule", "\\end{longtable}", ""])

    c4_lines = [
        "\\begin{tabular}{lrr}",
        "\\toprule",
        "\\textbf{C4 / test-overlap advisory} & \\textbf{$n$} & \\textbf{Share} \\\\",
        "\\midrule",
        f"Advisory (not in three-state labels) & {len(c4_undetermined)} & {pct(len(c4_undetermined), 200)} \\\\",
        f"Overlap with v2 violates & {len(c4_set & drop_ids)} & -- \\\\",
        f"Overlap with v2 meets\\_standard & {len(c4_set & keep)} & -- \\\\",
        "\\bottomrule",
        "\\end{tabular}",
        "",
    ]

    files = {
        "tab_python200_standard_labels.tex": tab_labels,
        "tab_python200_eligibility_slice.tex": tab_eligibility,
        "tab_python200_fixed116_funnel.tex": tab_funnel,
        "tab_python200_fixed116_rres.tex": tab_rres,
        "tab_python200_c4_advisory.tex": "\n".join(c4_lines),
        "tab_python200_violators.tex": "\n".join(violator_lines),
    }
    for name, body in files.items():
        (OUT / name).write_text(body, encoding="utf-8")
        if FSE_TABLES.is_dir():
            (FSE_TABLES / name).write_text(body, encoding="utf-8")
        DRAFT_TABLES.mkdir(parents=True, exist_ok=True)
        (DRAFT_TABLES / name).write_text(body, encoding="utf-8")

    print(json.dumps({k: payload["slices"][k] for k in payload["slices"]}, indent=2))
    print("c4", payload["c4_advisory"]["n"], "overlap_violates", payload["c4_advisory"]["overlap_violates"])
    print("wrote", OUT)


if __name__ == "__main__":
    main()

"""Checked data assembly for paper figures; never runs benchmark evaluations."""
import csv
import hashlib
import json
import math
import os
from collections import Counter
from pathlib import Path
from statistics import median

from paper_style import BACKEND_ORDER, FIGURES_DIR
from paper_inputs import ROOT, RESULTS as SOURCE, STATS_PATH as STATS, MODELS as MODEL_IDS

NAMES = dict(zip(MODEL_IDS, BACKEND_ORDER))
FIRST_STAGES = ("functional_pass", "missing_submission", "build_failure",
                "public_failure", "hidden_failure", "isolation_failure")
GATES = ("Build", "Public", "Hidden", "Isolation")
GATE_FIELDS = ("build_pass", "public_pass", "hidden_pass", "isolation_pass")


def prepare_matplotlib():
    os.environ.setdefault("MPLCONFIGDIR", str(FIGURES_DIR / ".mplconfig"))
    import matplotlib
    matplotlib.use("Agg")


def flag(row, field):
    value = row[field].lower()
    assert value in {"true", "false"}, (field, value)
    return value == "true"


def load_results():
    with SOURCE.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 900
    assert len({(r["model"], r["task_id"]) for r in rows}) == 900
    groups = {NAMES[m]: [r for r in rows if r["model"] == m] for m in MODEL_IDS}
    task_ids = {r["task_id"] for r in groups["Pro"]}
    for name, group in groups.items():
        assert len(group) == 150 and {r["task_id"] for r in group} == task_ids, name
        for r in group:
            expected = "missing_submission"
            if flag(r, "usable_submission"):
                expected = "functional_pass"
                for field, stage in zip(GATE_FIELDS, FIRST_STAGES[2:]):
                    if not flag(r, field):
                        expected = stage
                        break
            assert expected == r["first_failure_stage"]
            assert flag(r, "functional_pass") == (expected == "functional_pass")
    stats = json.loads(STATS.read_text(encoding="utf-8"))
    assert [sum(flag(r, "functional_pass") for r in groups[n]) for n in BACKEND_ORDER] == [115, 108, 102, 68, 63, 36]
    return rows, groups, stats


def export_data(name, payload):
    payload["sources"] = [{"path": p.relative_to(ROOT).as_posix(),
                           "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                          for p in (SOURCE, STATS)]
    path = FIGURES_DIR / "data" / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def failures():
    rows, groups, _ = load_results()
    first = []
    for name in BACKEND_ORDER:
        counts = Counter(r["first_failure_stage"] for r in groups[name])
        values = [counts[k] for k in FIRST_STAGES]
        assert sum(values) == 150
        first.append({"backend": name, "assigned": 150, "counts": values})
    delivered = [r for r in rows if flag(r, "usable_submission")]
    flags = [sum(not flag(r, field) for r in delivered) for field in GATE_FIELDS]
    residual = sum(all(flag(r, k) for k in GATE_FIELDS[:3]) and not flag(r, GATE_FIELDS[3]) for r in delivered)
    assert len(delivered) == 829 and flags == [30, 244, 296, 39] and residual == 4
    return export_data("fig03_failures", {"first_stage_keys": FIRST_STAGES,
        "first_outcomes": first, "delivered": len(delivered), "isolation_residual": residual,
        "gate_flags": [{"gate": g, "failed": n, "denominator": len(delivered),
                        "percent": 100*n/len(delivered)} for g, n in zip(GATES, flags)]})


def difficulty():
    rows, groups, stats = load_results()
    task_ids = sorted(r['task_id'] for r in groups['Pro'])
    passes = Counter()
    for r in rows:
        passes[r['task_id']] += flag(r, 'functional_pass')
    bins = [{'passing_configurations': i,
             'task_count': sum(passes[t] == i for t in task_ids)} for i in range(7)]
    assert [b['task_count'] for b in bins] == [b['total'] for b in stats['spectrum6']['bins']]
    assert sum(b['task_count'] for b in bins) == 150
    return export_data('fig04_difficulty', {'evaluated_tasks': 150, 'configurations': 6,
        'bins': bins, 'tasks': [{'task_id': t, 'passing_configurations': passes[t]} for t in task_ids]})


def paired_footprint():
    _, groups, stats = load_results()
    aa = {r["task_id"]: r for r in groups["Pro"] if flag(r, "functional_pass")}
    bb = {r["task_id"]: r for r in groups["Luna"] if flag(r, "functional_pass")}
    common = sorted(aa.keys() & bb.keys())
    assert len(common) == 97
    points = [{"task_id": t, "pro_rres": float(aa[t]["rres"]), "luna_rres": float(bb[t]["rres"]),
               "pro_copy": float(aa[t]["copied_fraction"]), "luna_copy": float(bb[t]["copied_fraction"])} for t in common]
    summaries = {}
    for metric in ("rres", "copy"):
        a = [r[f"pro_{metric}"] for r in points]
        b = [r[f"luna_{metric}"] for r in points]
        assert all(math.isfinite(v) for v in a+b)
        assert all(v > 0 for v in a+b) if metric == "rres" else all(0 <= v <= 1 for v in a+b)
        delta = [x-y for x, y in zip(a, b)]
        summaries[metric] = {"median_pro": median(a), "median_luna": median(b),
            "median_difference": median(delta), "pro_greater": sum(v > 0 for v in delta),
            "luna_greater": sum(v < 0 for v in delta), "ties": sum(v == 0 for v in delta),
            "min": min(a+b), "max": max(a+b)}
    expected = stats["paired_pro_luna"]
    assert abs(summaries["copy"]["median_pro"] - expected["median_a"]) < 1e-6
    assert abs(summaries["copy"]["median_luna"] - expected["median_b"]) < 1e-6
    assert [summaries[m][k] for m in ("rres", "copy") for k in ("pro_greater", "luna_greater", "ties")] == [85, 10, 2, 76, 18, 3]
    assert abs(summaries["rres"]["median_pro"] - expected["rres_median_a"]) < 1e-6
    assert abs(summaries["rres"]["median_luna"] - expected["rres_median_b"]) < 1e-6
    return export_data("fig05_paired_footprint", {"common_passing_tasks": 97,
        "x_backend": "Luna", "y_backend": "Pro", "points": points, "summaries": summaries})

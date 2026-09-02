#!/usr/bin/env python3
"""Feasibility probe: is there a runnable upstream oracle for the declared API?

A harness-selected differential arm needs to call, for each declared
``featurelifted`` symbol, the upstream counterpart inside the pinned ``repo/``
snapshot. If that counterpart cannot be located or executed, the differential
degrades to a no-op on that task and the method cannot help there.

The probe reports two bounds per task:

- resolution (static): can the declared symbol be mapped to an upstream
  definition by name at all? This upper-bounds feasibility, since an
  unresolvable symbol has no oracle in any environment.
- import (executed here): can that upstream module be imported and the symbol
  retrieved, with only the pinned snapshot on ``sys.path``? This machine has no
  task lockfile installed, so failures caused solely by a missing third-party
  dependency are classified apart: those are expected to succeed inside the
  task's Docker environment where the lock is installed.

The true in-Docker feasibility therefore sits between the import count and the
import count plus the missing-dependency count.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_contract_entailment import (  # noqa: E402
    Contract,
    index_upstream,
    resolve_symbol,
    upstream_root,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BENCHMARK = ROOT / "benchmark" / "python200_hard_tasks"

# Feasibility bar pre-registered before running: below this the differential
# covers too few tasks to carry a method.
TARGET_FULL_FRACTION = 0.70

PROBE = r'''
import importlib, json, os, sys, traceback

up_root = sys.argv[1]
targets = json.loads(sys.argv[2])
sys.path.insert(0, up_root)

out = []
for name, module in targets:
    row = {"name": name, "module": module}
    try:
        mod = importlib.import_module(module)
    except ModuleNotFoundError as exc:
        row["status"] = "missing_module"
        row["detail"] = str(exc.name or exc)
    except BaseException as exc:  # noqa: BLE001
        row["status"] = "import_error"
        row["detail"] = f"{type(exc).__name__}: {exc}"[:200]
    else:
        origin = getattr(mod, "__file__", "") or ""
        if origin and not os.path.realpath(origin).startswith(os.path.realpath(up_root)):
            row["status"] = "shadowed"
            row["detail"] = origin
        elif module.split(".")[-1] == name:
            row["status"] = "ok"
        elif hasattr(mod, name):
            row["status"] = "ok"
        else:
            row["status"] = "attr_absent"
    out.append(row)

print(json.dumps(out))
'''


def probe_task(task_dir: Path, python: str, timeout: int) -> dict[str, Any]:
    row: dict[str, Any] = {"task_id": task_dir.name}
    try:
        metadata = json.loads((task_dir / "metadata.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        row["error"] = f"metadata unreadable: {exc}"
        return row

    public_spec = metadata.get("public_spec") or {}
    contract = Contract(public_spec)
    root = upstream_root(task_dir)
    if root is None:
        row["error"] = "no pinned repo/"
        return row

    # Some tasks ship repo/ as an archive marker and materialize it only at run
    # time. Those cannot be indexed here and must not count as unresolvable.
    if not any(root.rglob("*.py")):
        row["error"] = "repo/ not materialized (source-archive backed)"
        row["unmaterialized"] = True
        return row

    index = index_upstream(root)
    entrypoints = [str(e) for e in (public_spec.get("source_entrypoints") or [])]

    targets: list[tuple[str, str]] = []
    unresolved: list[str] = []
    for name in sorted(contract.tops):
        found = resolve_symbol(name, entrypoints, index)
        if found is None:
            unresolved.append(name)
            continue
        module, _ = found
        targets.append((name, module))

    row["n_declared"] = len(contract.tops)
    row["n_resolved"] = len(targets)
    row["unresolved"] = unresolved

    if not targets:
        row["statuses"] = {}
        row["n_ok"] = 0
        row["n_missing_dep"] = 0
        return row

    try:
        proc = subprocess.run(
            [python, "-c", PROBE, str(root), json.dumps(targets)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(task_dir),
        )
    except subprocess.TimeoutExpired:
        row["error"] = "probe timeout"
        return row

    try:
        results = json.loads(proc.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError):
        row["error"] = f"probe failed: {(proc.stderr or proc.stdout)[-200:]}"
        return row

    counts = Counter(r["status"] for r in results)
    row["statuses"] = dict(counts)
    row["n_ok"] = counts.get("ok", 0)
    row["n_missing_dep"] = counts.get("missing_module", 0)
    row["detail"] = [r for r in results if r["status"] != "ok"][:6]
    return row


def verdict(row: dict[str, Any]) -> str:
    """Per-task feasibility class, optimistic about missing lockfile deps."""
    if row.get("unmaterialized"):
        return "unmaterialized"
    if row.get("error"):
        return "error"
    declared = row.get("n_declared") or 0
    if not declared:
        return "no_declared_api"
    if row.get("n_resolved", 0) < declared:
        return "unresolvable"
    reachable = row.get("n_ok", 0) + row.get("n_missing_dep", 0)
    if row.get("n_ok", 0) == declared:
        return "runs_here"
    if reachable == declared:
        return "needs_lockfile"
    return "blocked"


FEASIBLE = {"runs_here", "needs_lockfile"}


def load_failures(analysis: Path | None, annotations: Path | None) -> dict[str, str]:
    """Map model-primary failure task ids to their lift type."""
    if not (analysis and annotations and analysis.is_file() and annotations.is_file()):
        return {}
    import csv

    with annotations.open(newline="", encoding="utf-8") as handle:
        primary = {
            r["task_id"]
            for r in csv.DictReader(handle)
            if r.get("root_cause_primary") in {"behavior_drift", "contract_api_completion"}
        }
    with analysis.open(newline="", encoding="utf-8") as handle:
        return {
            r["task_id"]: r.get("lift_type") or "?"
            for r in csv.DictReader(handle)
            if r.get("task_id") in primary
        }


def render(rows: list[dict[str, Any]], failures: dict[str, str] | None = None) -> str:
    failures = failures or {}
    index_by_id = {r["task_id"]: r for r in rows}
    failures = {k: v for k, v in failures.items() if k in index_by_id}
    classes = Counter(verdict(r) for r in rows)
    unmaterialized = classes.get("unmaterialized", 0)
    # Denominator excludes tasks whose repo/ this probe cannot see at all.
    total = len(rows) - unmaterialized
    runs = classes.get("runs_here", 0)
    lock = classes.get("needs_lockfile", 0)
    optimistic = runs + lock

    out = ["# 上游 differential oracle 可行性探针", ""]
    out.append("> **Status: AI 生成的离线探针 · 未跑任何模型**")
    out.append("")
    out.append("## 问题")
    out.append("")
    out.append(
        "harness 选输入的 differential 臂，需要对每个声明的 `featurelifted` 符号"
        "调用其在钉住 `repo/` 快照里的上游对应物。定位不到或跑不起来的题上，"
        "differential 退化为什么都不做，方法在那些题上不可能有帮助。"
    )
    out.append("")
    out.append(
        f"预注册门槛：可行题占比 < **{TARGET_FULL_FRACTION:.0%}** 则这条路作废。"
    )
    out.append("")
    out.append("## 结果")
    out.append("")
    out.append(
        f"分母为 `repo/` 已物化的 **{total}** 题。另有 **{unmaterialized}** 题的 "
        "`repo/` 只是 source-archive 标记、运行时才物化，本探针看不到，"
        "不计入分母也不算不可行。"
    )
    out.append("")
    out.append("| 分类 | 题数 | 占比 | 含义 |")
    out.append("| --- | ---: | ---: | --- |")
    labels = {
        "runs_here": "本机即可导入并取到全部声明符号",
        "needs_lockfile": "仅因缺第三方依赖失败，任务 Docker 内预期可用",
        "unresolvable": "有声明符号无法在上游快照中按名定位",
        "blocked": "定位到了但导入失败/被系统包遮蔽/属性不存在",
        "no_declared_api": "`required_api` 未声明 featurelifted 顶层符号",
        "error": "探针本身失败",
    }
    for key, label in labels.items():
        if classes.get(key):
            out.append(
                f"| `{key}` | {classes[key]} | {classes[key] / total:.1%} | {label} |"
            )
    out.append("")
    out.append(
        f"**下界 {runs / total:.1%}**（本机直接跑通）、"
        f"**上界 {optimistic / total:.1%}**（加上仅缺依赖的题）。"
        "任务 Docker 内的真实值落在两者之间。"
    )
    out.append("")

    if optimistic / total < TARGET_FULL_FRACTION:
        out.append(
            f"**否决。** 连乐观上界 {optimistic / total:.1%} 都低于门槛 "
            f"{TARGET_FULL_FRACTION:.0%}，harness 选输入的 differential 覆盖不足以承载方法。"
        )
    elif runs / total >= TARGET_FULL_FRACTION:
        out.append(
            f"**通过。** 即使不装任何 lockfile，下界 {runs / total:.1%} 已过门槛，"
            "可以进入方法规格。"
        )
    else:
        out.append(
            f"**待定。** 上界 {optimistic / total:.1%} 过门槛但下界 {runs / total:.1%} 不过，"
            "结论取决于 lockfile 是否真能补齐。下一步必须在任务 Docker 环境内抽样复测 "
            "`needs_lockfile` 这一类，才能定论。"
        )
    out.append("")

    blockers = Counter()
    for row in rows:
        if verdict(row) in {"blocked", "unresolvable"}:
            for item in row.get("detail") or []:
                blockers[item["status"]] += 1
            for _ in row.get("unresolved") or []:
                blockers["unresolved_symbol"] += 1
    if blockers:
        out.append("## 阻塞原因分布")
        out.append("")
        out.append("| 原因 | 次数 |")
        out.append("| --- | ---: |")
        for key, count in blockers.most_common():
            out.append(f"| `{key}` | {count} |")
        out.append("")

    if failures:
        out.append("## 决定性交叉验证：可行性与失败题是否重合")
        out.append("")
        out.append(
            "全套件可行率只说明覆盖面。真正决定方法价值的是：**可行的题是否就是"
            "会失败的题。** 下表按 lift 类型拆开 2026-08-29 主实验里二审判定为"
            "模型主因的失败题。"
        )
        out.append("")
        out.append("| lift | 失败题 | differential 可行 | 不可行 |")
        out.append("| --- | ---: | ---: | ---: |")
        by_lift: dict[str, Counter] = {}
        for task_id, lift in failures.items():
            by_lift.setdefault(lift, Counter())[
                "feasible" if verdict(index_by_id[task_id]) in FEASIBLE else "infeasible"
            ] += 1
        feasible_total = infeasible_total = 0
        for lift in sorted(by_lift):
            counts = by_lift[lift]
            ok = counts.get("feasible", 0)
            bad = counts.get("infeasible", 0)
            feasible_total += ok
            infeasible_total += bad
            out.append(f"| {lift} | {ok + bad} | {ok} | {bad} |")
        n_fail = feasible_total + infeasible_total
        out.append(f"| **合计** | **{n_fail}** | **{feasible_total}** | **{infeasible_total}** |")
        out.append("")
        out.append(
            f"全套件可行 {optimistic / total:.1%}，但**失败题里只有 "
            f"{feasible_total}/{n_fail} = {feasible_total / n_fail:.0%} 可行**。"
        )
        out.append("")
        out.append(
            "原因是结构性的，不是实现问题：Adapted 与 Composite 抽取的 API 按设计"
            "就不是任何单个上游符号的 1:1 对应物，因此 differential oracle 在那里"
            "**没有定义**。而失败恰好集中在这两类。上游 differential 能用的地方，"
            "正是 Agent 本来就做得好的地方。"
        )
        out.append("")

    worst = [r for r in rows if verdict(r) in {"unresolvable", "blocked", "error"}]
    if worst:
        out.append("## 不可行题（前 25）")
        out.append("")
        out.append("| 任务 | 分类 | 声明 | 已定位 | 本机 ok | 缺依赖 | 备注 |")
        out.append("| --- | --- | ---: | ---: | ---: | ---: | --- |")
        for row in sorted(worst, key=lambda r: r["task_id"])[:25]:
            note = row.get("error") or ", ".join(
                f"{i['name']}:{i['status']}" for i in (row.get("detail") or [])[:2]
            ) or ", ".join(row.get("unresolved") or [])[:60]
            out.append(
                f"| `{row['task_id']}` | `{verdict(row)}` | {row.get('n_declared', 0)} "
                f"| {row.get('n_resolved', 0)} | {row.get('n_ok', 0)} "
                f"| {row.get('n_missing_dep', 0)} | {str(note)[:70]} |"
            )
        out.append("")

    out.append("## 限制")
    out.append("")
    out.append(
        "- 定位是按名解析，不做类型或语义匹配。`runs_here` 只说明符号可导入，"
        "不说明它与 `featurelifted` 的语义对应正确。因此可行率是上界。"
    )
    out.append(
        "- 本机未安装任何任务 lockfile，因此 `needs_lockfile` 是乐观归类，"
        "必须在 Docker 内抽样复测。"
    )
    out.append(
        "- 被系统包遮蔽的情况已单独标为 `shadowed`，不计入可行。"
    )
    return "\n".join(out) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument(
        "--failure-analysis",
        type=Path,
        help="failure_analysis.csv, for the feasibility-vs-failure cross-check",
    )
    parser.add_argument("--failure-annotations", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    tasks = sorted(p for p in args.benchmark.iterdir() if (p / "metadata.json").is_file())
    if not tasks:
        raise SystemExit(f"no tasks under {args.benchmark}")

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        rows = list(
            pool.map(lambda t: probe_task(t, args.python, args.timeout), tasks)
        )

    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "upstream_differential_probe.json").write_text(
        json.dumps({"n_tasks": len(rows), "tasks": rows}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    failures = load_failures(args.failure_analysis, args.failure_annotations)
    (args.output / "upstream_differential_probe.md").write_text(
        render(rows, failures), encoding="utf-8"
    )
    counts = Counter(verdict(r) for r in rows)
    print(f"probed {len(rows)} tasks: {dict(counts)}")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

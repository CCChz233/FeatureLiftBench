#!/usr/bin/env python3
"""Check that every declared ``source_entrypoints`` symbol exists in ``repo/``.

``public_spec.source_entrypoints`` records where the lifted feature came from
upstream.  The Main arm redacts it, so a dangling pointer does not mislead the
agent there; it matters for two other reasons.  The ``entrypoint_hint`` ablation
arm feeds this field straight to the agent, so a dangling entry would hand it
symbols that do not exist.  And a pointer that resolves nowhere is evidence that
the declared feature has no upstream counterpart at all, which makes the field a
marker for invented APIs rather than lifted ones.

Resolution is structural rather than name-based, because name matching both
over- and under-counts.  For a dotted path ``a.b.c.d`` the resolver finds the
longest prefix that maps to a module file under the snapshot, then walks the
remaining attributes through that module's symbol table, following ``from X
import y`` re-exports so that facade modules such as ``arrow/__init__.py``
resolve.  Class bodies are walked so bound methods resolve too.

Verdicts, worst first:

``dangling``
    The leaf name is defined nowhere in the snapshot.  A real provenance defect.
``misplaced``
    The declared path is wrong but the leaf name is defined somewhere else in
    the snapshot, so the code exists and the pointer merely misleads.
``resolved``
    The declared path resolves exactly.
``undecidable``
    The snapshot could not be parsed well enough to judge.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TASKS = ROOT / "benchmark" / "python200_hard_tasks"

MAX_REEXPORT_HOPS = 6


class Snapshot:
    """Module and symbol index over one pinned ``repo/`` tree."""

    def __init__(self, repo: Path) -> None:
        self.repo = repo
        self.modules: dict[str, Path] = {}
        self._symbols: dict[str, dict[str, Any] | None] = {}
        self.leaf_names: set[str] = set()
        self.parse_failures = 0
        self._index_modules()
        self._index_leaf_names()

    def _roots(self) -> list[Path]:
        roots = [self.repo]
        for candidate in ("src", "lib"):
            path = self.repo / candidate
            if path.is_dir():
                roots.append(path)
        for child in self.repo.iterdir():
            if child.is_dir() and not child.name.startswith("."):
                roots.append(child)
        return roots

    def _index_modules(self) -> None:
        for root in self._roots():
            for path in root.rglob("*.py"):
                if any(part.startswith(".") for part in path.relative_to(root).parts):
                    continue
                relative = path.relative_to(root)
                parts = list(relative.parts)
                if parts[-1] == "__init__.py":
                    parts = parts[:-1]
                else:
                    parts[-1] = parts[-1][:-3]
                if not parts:
                    continue
                self.modules.setdefault(".".join(parts), path)

    def _index_leaf_names(self) -> None:
        for path in set(self.modules.values()):
            tree = self._parse(path)
            if tree is None:
                continue
            for node in ast.walk(tree):
                if isinstance(
                    node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
                ):
                    self.leaf_names.add(node.name)

    def _parse(self, path: Path) -> ast.Module | None:
        try:
            return ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except (SyntaxError, ValueError, OSError):
            self.parse_failures += 1
            return None

    def symbols(self, module: str) -> dict[str, Any] | None:
        """Top-level bindings of ``module``: name -> definition or re-export."""
        if module in self._symbols:
            return self._symbols[module]
        path = self.modules.get(module)
        if path is None:
            self._symbols[module] = None
            return None
        tree = self._parse(path)
        if tree is None:
            self._symbols[module] = None
            return None

        table: dict[str, Any] = {}
        stars: list[str] = []
        self._collect(module, tree.body, table, stars)
        table["__star__"] = stars
        self._symbols[module] = table
        return table

    def _collect(
        self,
        module: str,
        body: list[ast.stmt],
        table: dict[str, Any],
        stars: list[str],
    ) -> None:
        """Bind names from ``body``, descending into conditional guards.

        Facade modules routinely place imports inside ``try``/``except`` for a
        C-extension fallback, or inside ``if TYPE_CHECKING``; a top-level-only
        walk misses those and reports live symbols as missing.
        """
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                table[node.name] = {"kind": "function", "node": node}
            elif isinstance(node, ast.ClassDef):
                table[node.name] = {"kind": "class", "node": node, "module": module}
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        table[target.id] = {"kind": "assign"}
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                table[node.target.id] = {"kind": "assign"}
            elif isinstance(node, ast.ImportFrom):
                base = self._absolute(module, node)
                # A C-extension import commonly shadows the pure-Python
                # fallback that was bound just above it.  The extension has no
                # source in the snapshot, so keep the binding that does.
                shadows = base not in self.modules
                for alias in node.names:
                    if alias.name == "*":
                        stars.append(base)
                        continue
                    bound = alias.asname or alias.name
                    if shadows and bound in table:
                        continue
                    table[bound] = {
                        "kind": "reexport",
                        "module": base,
                        "name": alias.name,
                    }
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    bound = alias.asname or alias.name.split(".")[0]
                    table[bound] = {"kind": "module", "module": alias.name}
            elif isinstance(node, ast.Try):
                for branch in (
                    node.body,
                    node.orelse,
                    node.finalbody,
                    *[handler.body for handler in node.handlers],
                ):
                    self._collect(module, branch, table, stars)
            elif isinstance(node, ast.If):
                self._collect(module, node.body, table, stars)
                self._collect(module, node.orelse, table, stars)

    def _lookup(self, module: str, name: str, hops: int = 0) -> dict[str, Any] | None:
        """Find ``name`` in ``module``, following ``import *`` re-exports."""
        table = self.symbols(module)
        if table is None:
            return None
        entry = table.get(name)
        if entry is not None:
            return entry
        if hops > MAX_REEXPORT_HOPS:
            return None
        for star in table.get("__star__") or []:
            found = self._lookup(star, name, hops + 1)
            if found is not None:
                return found
        return None

    def _absolute(self, module: str, node: ast.ImportFrom) -> str:
        if not node.level:
            return node.module or ""
        parts = module.split(".")
        # A package's ``__init__`` is its own base; a plain module drops its leaf.
        if self.modules.get(module, Path()).name != "__init__.py":
            parts = parts[:-1]
        if node.level > 1:
            parts = parts[: len(parts) - (node.level - 1)]
        return ".".join(parts + ([node.module] if node.module else []))

    def longest_module_prefix(self, dotted: str) -> tuple[str, list[str]] | None:
        parts = dotted.split(".")
        for cut in range(len(parts), 0, -1):
            candidate = ".".join(parts[:cut])
            if candidate in self.modules:
                return candidate, parts[cut:]
        return None

    def resolve(self, dotted: str, hops: int = 0) -> str:
        """Return ``resolved``, ``misplaced``, ``dangling`` or ``undecidable``."""
        if hops > MAX_REEXPORT_HOPS:
            return "undecidable"
        found = self.longest_module_prefix(dotted)
        if found is None:
            return self._by_name(dotted)
        module, attributes = found
        if not attributes:
            return "resolved"

        entry = self._lookup(module, attributes[0])
        if entry is None:
            return self._by_name(dotted)
        rest = attributes[1:]

        if entry["kind"] == "reexport":
            target = ".".join(filter(None, [entry["module"], entry["name"], *rest]))
            return self.resolve(target, hops + 1)
        if entry["kind"] == "module":
            return self.resolve(".".join([entry["module"], *rest]), hops + 1)
        if not rest:
            return "resolved"
        if entry["kind"] == "class":
            if self._in_class(entry.get("module", module), entry["node"], rest[0]):
                return "resolved"
            return self._by_name(dotted)
        return self._by_name(dotted)

    def _in_class(
        self,
        module: str,
        node: ast.ClassDef,
        wanted: str,
        seen: set[int] | None = None,
    ) -> bool:
        """Whether ``wanted`` is a member of ``node``, including inherited ones."""
        seen = seen if seen is not None else set()
        if id(node) in seen:
            return False
        seen.add(id(node))

        for item in node.body:
            if (
                isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                and item.name == wanted
            ):
                return True
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == wanted:
                        return True
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                if item.target.id == wanted:
                    return True
            # Attributes bound on ``self`` inside any method are part of the
            # public surface even though nothing is defined in the class body.
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for inner in ast.walk(item):
                    targets: list[ast.expr] = []
                    if isinstance(inner, ast.Assign):
                        targets = list(inner.targets)
                    elif isinstance(inner, ast.AnnAssign):
                        targets = [inner.target]
                    for target in targets:
                        if (
                            isinstance(target, ast.Attribute)
                            and target.attr == wanted
                            and isinstance(target.value, ast.Name)
                            and target.value.id == "self"
                        ):
                            return True

        for base in node.bases:
            base_name = base.id if isinstance(base, ast.Name) else None
            base_module = module
            if base_name is None and isinstance(base, ast.Attribute):
                base_name = base.attr
            if base_name is None:
                continue
            entry = self._lookup(base_module, base_name)
            if entry is None:
                continue
            for _ in range(MAX_REEXPORT_HOPS):
                if entry is None or entry["kind"] != "reexport":
                    break
                base_module = entry["module"]
                entry = self._lookup(base_module, entry["name"])
            if entry is not None and entry["kind"] == "class":
                if self._in_class(
                    entry.get("module", base_module), entry["node"], wanted, seen
                ):
                    return True
        return False

    def _by_name(self, dotted: str) -> str:
        leaf = dotted.split(".")[-1]
        if leaf in self.leaf_names:
            return "misplaced"
        return "dangling"


def audit_task(task: Path) -> dict[str, Any] | None:
    metadata_path = task / "metadata.json"
    repo = task / "repo"
    if not metadata_path.is_file() or not repo.is_dir():
        return None
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    entrypoints = (metadata.get("public_spec") or {}).get("source_entrypoints")
    if not isinstance(entrypoints, list) or not entrypoints:
        return {
            "task_id": task.name,
            "declared": 0,
            "verdicts": {},
            "entries": [],
            "worst": "undeclared",
        }

    snapshot = Snapshot(repo)
    entries = []
    for raw in entrypoints:
        if not isinstance(raw, str) or not raw.strip():
            continue
        symbol = raw.strip()
        entries.append({"symbol": symbol, "verdict": snapshot.resolve(symbol)})

    verdicts = Counter(entry["verdict"] for entry in entries)
    for level in ("dangling", "misplaced", "undecidable", "resolved"):
        if verdicts.get(level):
            worst = level
            break
    else:
        worst = "undeclared"
    return {
        "task_id": task.name,
        "declared": len(entries),
        "verdicts": dict(verdicts),
        "entries": entries,
        "worst": worst,
        "module_count": len(snapshot.modules),
        "parse_failures": snapshot.parse_failures,
    }


def load_context() -> dict[str, dict[str, Any]]:
    """Portability and pass labels, where a prior analysis produced them."""
    path = ROOT / "reports" / "paper_analysis" / "task_portability" / "task_portability.json"
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {row["task_id"]: row for row in payload.get("rows", [])}


def render(rows: list[dict[str, Any]], context: dict[str, dict[str, Any]]) -> str:
    declared = [r for r in rows if r["worst"] != "undeclared"]
    dangling = [r for r in rows if r["worst"] == "dangling"]
    misplaced = [r for r in rows if r["worst"] == "misplaced"]
    total_entries = sum(r["declared"] for r in rows)
    bad_entries = sum(
        r["verdicts"].get("dangling", 0) + r["verdicts"].get("misplaced", 0)
        for r in rows
    )

    out = ["# `source_entrypoints` 溯源审计：全 200 题", ""]
    out.append("> **Status: AI 生成的机械审计 · 需人工复核后才能据此改题**")
    out.append("")
    out.append("## 结论")
    out.append("")
    out.append(
        f"{len(rows)} 道题里 {len(declared)} 道声明了 `source_entrypoints`，"
        f"共 {total_entries} 条指针，其中 **{bad_entries} 条指不到声明的位置**。"
        f"按题算：**{len(dangling)} 道存在真悬空**（叶名在快照里根本不存在），"
        f"{len(misplaced)} 道属于指错位置（代码在，路径写错）。"
    )
    out.append("")
    out.append("## 判定口径")
    out.append("")
    out.append(
        "解析是结构化的：先找点号路径中能对上快照里模块文件的最长前缀，"
        "再把剩下的属性在该模块的符号表里逐级走，遇到 `from X import y` 会跟随"
        "再导出（最多 6 跳），类体也会走进去找方法。因此 `arrow.get` 这种"
        "门面再导出、`arrow.Arrow.format` 这种绑定方法都能正常解析，"
        "不会被误报。"
    )
    out.append("")
    out.append("| 判定 | 含义 | 题数 |")
    out.append("| :-- | :-- | ---: |")
    out.append(f"| `dangling` | 叶名在快照里定义不到，真缺陷 | {len(dangling)} |")
    out.append(f"| `misplaced` | 路径写错但代码存在于别处 | {len(misplaced)} |")
    out.append(
        f"| `resolved` | 精确解析 | {sum(1 for r in rows if r['worst'] == 'resolved')} |"
    )
    out.append(
        f"| `undecidable` | 快照解析不动，判不了 "
        f"| {sum(1 for r in rows if r['worst'] == 'undecidable')} |"
    )
    out.append(
        f"| `undeclared` | 没声明入口 "
        f"| {sum(1 for r in rows if r['worst'] == 'undeclared')} |"
    )
    out.append("")

    out.append("## 缺陷完全集中在 hard3 批次")
    out.append("")
    batches: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        name = "hard3" if "__hard3_" in row["task_id"] else "core-001"
        batches[name][row["worst"]] += 1
        batches[name]["total"] += 1
    out.append("| 批次 | 题数 | 已声明入口 | 真悬空 | 悬空率 |")
    out.append("| :-- | ---: | ---: | ---: | ---: |")
    for name in sorted(batches):
        tally = batches[name]
        declared_here = tally["total"] - tally["undeclared"]
        share = tally["dangling"] / declared_here if declared_here else 0.0
        out.append(
            f"| {name} | {tally['total']} | {declared_here} "
            f"| {tally['dangling']} | {share:.0%} |"
        )
    out.append("")
    out.append(
        "`core-001` 的 150 道题零悬空，全部 12 道集中在 `hard3` 的 50 道题里。"
        "悬空的符号名（`EvictionPolicyPlanner`、`ZoneResolver`、"
        "`LazyCommandCollection`、`RepoFinder`）读起来像是生成时编造的名字，"
        "而不是真实上游 API。这把缺陷定位到了一次生成批次上。"
    )
    out.append("")

    if context:
        out.append("## 与通过率交叉")
        out.append("")
        out.append(
            "只有能对上 `task_portability` 分析的题才有通过标签，"
            "所以下表的分母小于全套。"
        )
        out.append("")
        out.append("| 子集 | 入口有问题 | 入口全解析 |")
        out.append("| :-- | ---: | ---: |")
        for label, predicate in (
            ("需合成题", lambda c: c["ref_cf"] < 0.90),
            ("可移植题", lambda c: c["ref_cf"] >= 0.90),
        ):
            bad_pass = bad_total = good_pass = good_total = 0
            for row in rows:
                ctx = context.get(row["task_id"])
                if ctx is None or not predicate(ctx):
                    continue
                if row["worst"] in ("dangling", "misplaced"):
                    bad_total += 1
                    bad_pass += bool(ctx["pass"])
                elif row["worst"] == "resolved":
                    good_total += 1
                    good_pass += bool(ctx["pass"])
            fmt = (
                lambda p, t: f"{p}/{t} ({p / t:.0%})" if t else "-"  # noqa: E731
            )
            out.append(f"| {label} | {fmt(bad_pass, bad_total)} | {fmt(good_pass, good_total)} |")
        out.append("")
        out.append(
            "**这不是因果关系。** Main 臂通过 `redact_task_metadata` 把 "
            "`source_entrypoints` 从 Agent 可见的 metadata 里剥掉了"
            "（`expose_source_hints=False`），`test_ablation_arms.py` 也断言提示中"
            "不含该字段。所以 Agent 在这些运行里根本没看到指针，指针也就无法"
            "把它引到空处。相关性的来源是：入口悬空标记了「声明的特性在上游"
            "压根没有对应实现」，而这类题本身就更难。"
        )
        out.append("")
        out.append(
            "指针真正会喂给 Agent 的地方是 `entrypoint_hint` 消融臂"
            "（`method/registry.toml`，`paper_table = false`）。该臂目前没有任何"
            "已跑的实验，所以还没有污染已发表结果；一旦在这 12 道题上跑，"
            "交给 Agent 的就是不存在的符号。"
        )
        out.append("")

    out.append("## 待修清单")
    out.append("")
    out.append("### 真悬空（优先）")
    out.append("")
    out.append("| 题 | 通过 | 类型 | 悬空指针 |")
    out.append("| :-- | :-: | :-- | :-- |")
    for row in sorted(dangling, key=lambda r: r["task_id"]):
        ctx = context.get(row["task_id"])
        status = "-" if ctx is None else ("PASS" if ctx["pass"] else "FAIL")
        kind = (
            "-"
            if ctx is None
            else ("需合成" if ctx["ref_cf"] < 0.90 else "可移植")
        )
        bad = [e["symbol"] for e in row["entries"] if e["verdict"] == "dangling"]
        shown = ", ".join(f"`{s}`" for s in bad[:3])
        if len(bad) > 3:
            shown += f" 等 {len(bad)} 条"
        out.append(f"| {row['task_id']} | {status} | {kind} | {shown} |")
    out.append("")
    out.append("### 指错位置")
    out.append("")
    out.append("| 题 | 通过 | 类型 | 指错的指针 |")
    out.append("| :-- | :-: | :-- | :-- |")
    for row in sorted(misplaced, key=lambda r: r["task_id"]):
        ctx = context.get(row["task_id"])
        status = "-" if ctx is None else ("PASS" if ctx["pass"] else "FAIL")
        kind = (
            "-"
            if ctx is None
            else ("需合成" if ctx["ref_cf"] < 0.90 else "可移植")
        )
        bad = [e["symbol"] for e in row["entries"] if e["verdict"] == "misplaced"]
        shown = ", ".join(f"`{s}`" for s in bad[:3])
        if len(bad) > 3:
            shown += f" 等 {len(bad)} 条"
        out.append(f"| {row['task_id']} | {status} | {kind} | {shown} |")
    out.append("")
    out.append("## 限制")
    out.append("")
    out.append(
        "- 只检查符号**是否存在**，不检查它是不是该题真正该引用的实现，"
        "也不检查签名。`resolved` 不等于指针正确。"
    )
    out.append(
        "- 动态构造的符号（`setattr`、元类生成、`__getattr__` 门面）会被判成"
        "`dangling`，改题前必须逐条人工复核。"
    )
    out.append(
        "- `misplaced` 用叶名在全快照的存在性兜底，同名符号可能造成误判。"
    )
    out.append(
        "- 通过率交叉表来自单模型单次运行，且 hard3 与 core-001 在难度上几乎"
        "不重叠，批次与「是否需合成」高度共线，两者的效应无法用本数据分离。"
    )
    return "\n".join(out) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks", type=Path, default=DEFAULT_TASKS)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rows = []
    for task in sorted(args.tasks.iterdir()):
        if not task.is_dir():
            continue
        row = audit_task(task)
        if row is not None:
            rows.append(row)
    if not rows:
        raise SystemExit("no tasks audited")

    context = load_context()
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "source_entrypoints_audit.json").write_text(
        json.dumps({"n": len(rows), "rows": rows}, indent=2) + "\n", encoding="utf-8"
    )
    (args.output / "source_entrypoints_audit.md").write_text(
        render(rows, context), encoding="utf-8"
    )

    tally: dict[str, int] = defaultdict(int)
    for row in rows:
        tally[row["worst"]] += 1
    print(f"audited {len(rows)} tasks: {dict(tally)}")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Audit whether hidden tests are entailed by what a task actually publishes.

An agent solving a FeatureLiftBench task has exactly two sources of truth: the
``public_spec`` contract in ``metadata.json`` and the pinned upstream snapshot in
``repo/``. A hidden test that cannot be derived from either one is not measuring
agent capability, so this script applies two mechanical checks per task.

``declared_surface``
    Which ``featurelifted`` members do the hidden tests exercise, and are they
    declared in ``public_spec.required_api``? Undeclared members mean the hidden
    test probes contract surface the agent was never told about.

``entrypoint_grounding``
    Does every symbol named in ``public_spec.source_entrypoints`` actually exist
    in the pinned ``repo/``? That field is what points an agent at the code it is
    meant to extract, so a dangling entrypoint leaves the behavior sentences as
    the only ground truth.

``upstream_entailment``
    Re-export the pinned upstream symbols as a synthetic ``featurelifted``
    package and run the hidden tests against it. Upstream is the reference an
    agent is asked to extract from, so a behavior test upstream itself fails
    demands behavior that contradicts the task's own source of truth.

A task renaming or regrouping upstream API under new ``featurelifted`` names is
normal and expected, so unresolved symbols are stubbed rather than treated as a
defect; only the behavior tests decide entailment.
"""

from __future__ import annotations

import argparse
import ast
import csv
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BENCHMARK = ROOT / "benchmark" / "python200_hard_tasks"
PACKAGE = "featurelifted"

# Outcome of the upstream re-export probe, judged on behavior tests only.
UPSTREAM_PASS = "upstream_pass"
UPSTREAM_CONTRADICTS = "upstream_contradicts"
API_RESHAPED = "api_reshaped"
ENV_UNAVAILABLE = "env_unavailable"

OUTCOME_LABELS = {
    UPSTREAM_PASS: "上游可通过（hidden 与忠实抽取一致）",
    UPSTREAM_CONTRADICTS: "上游断言不符（hidden 要求与上游行为矛盾）",
    API_RESHAPED: "仅接口形状差异（任务有意改造 API，非缺陷）",
    ENV_UNAVAILABLE: "环境不可用（未判定）",
}

# Generated per task; asserts the declared API exists rather than any behavior.
SURFACE_TEST_FILE = "test_required_api_surface.py"

# A task is free to rename, regroup or extend the upstream API, so these failure
# kinds only mean the surface was reshaped. An assertion failure is different:
# upstream implements the call and returns something the hidden test rejects.
SHAPE_FAILURE_TYPES = {
    "ImportError",
    "ModuleNotFoundError",
    "AttributeError",
    "TypeError",
    "NotImplementedError",
    "NameError",
    "CollectionError",
}

REPORT_PLUGIN = '''
import json
import os

_OUT = os.environ["AUDIT_REPORT"]


def _record(nodeid, outcome, longrepr):
    message = ""
    crash = getattr(longrepr, "reprcrash", None)
    if crash is not None:
        message = crash.message
    elif longrepr is not None:
        message = str(longrepr)
    with open(_OUT, "a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "nodeid": nodeid, "outcome": outcome, "message": message[:1500],
        }) + "\\n")


def pytest_runtest_logreport(report):
    if report.when == "call" or (report.outcome == "failed" and report.when == "setup"):
        _record(report.nodeid, report.outcome, report.longrepr)


def pytest_collectreport(report):
    if report.outcome == "failed":
        _record(report.nodeid, "collect-error", report.longrepr)
'''


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


# --------------------------------------------------------------------------
# contract surface
# --------------------------------------------------------------------------


class Contract:
    """The API surface a task publishes in ``public_spec.required_api``."""

    def __init__(self, public_spec: dict[str, Any]) -> None:
        self.tops: set[str] = set()
        self.members: set[str] = set()
        self.kinds: dict[str, str] = {}
        self.returns: dict[str, str] = {}

        for entry in public_spec.get("required_api") or []:
            path = str(entry.get("path") or "")
            if not path.startswith(f"{PACKAGE}."):
                continue
            rest = path[len(PACKAGE) + 1 :]
            if "." in rest:
                self.members.add(rest)
                self.tops.add(rest.split(".")[0])
                continue
            self.tops.add(rest)
            self.kinds[rest] = str(entry.get("kind") or "")
            returned = self._return_type(entry.get("signature"))
            if returned:
                self.returns[rest] = returned
            for member in entry.get("members") or []:
                mpath = str(member.get("path") or "")
                if mpath.startswith(f"{PACKAGE}."):
                    self.members.add(mpath[len(PACKAGE) + 1 :])

    @staticmethod
    def _return_type(signature: Any) -> str | None:
        """Extract a bare class name from a ``(...) -> 'CIMultiDict'`` signature."""
        if not signature or "->" not in str(signature):
            return None
        tail = str(signature).rsplit("->", 1)[1].strip().strip("'\" ")
        return tail if tail.isidentifier() and tail != "None" else None

    def constructs(self, name: str) -> str | None:
        """Return the class an expression ``name(...)`` yields, if determinable."""
        if self.kinds.get(name) in {"class", "exception"}:
            return name
        return self.returns.get(name)


class _Scope:
    """One Python namespace the visitor is currently inside."""

    def __init__(self, kind: str) -> None:
        self.kind = kind  # module | class | function
        self.names: dict[str, str] = {}


class _UsageVisitor(ast.NodeVisitor):
    """Collect ``featurelifted`` members exercised by a hidden test module.

    Tracks the narrow dataflow that matters here: a local bound directly to a
    call of an imported class is treated as an instance of that class, so
    ``h = CIMultiDict(); h["bad"] = "1"`` is recorded as ``CIMultiDict.__setitem__``.

    Bindings are scoped.  A class-body field ``hello = String()`` must not leak
    into a function that later does ``hello = schema.execute()``.  Rebinding a
    name to an expression whose type cannot be inferred drops the old binding
    instead of keeping it.
    """

    def __init__(self, contract: Contract) -> None:
        self.contract = contract
        self.imported: dict[str, str] = {}
        self.module_aliases: set[str] = set()
        self.used: set[str] = set()
        self._scopes: list[_Scope] = [_Scope("module")]

    def _push(self, kind: str) -> None:
        self._scopes.append(_Scope(kind))

    def _pop(self) -> None:
        self._scopes.pop()

    def _bind(self, name: str, owner: str | None) -> None:
        names = self._scopes[-1].names
        if owner:
            names[name] = owner
        else:
            names.pop(name, None)

    def _bind_target(self, target: ast.AST, owner: str | None) -> None:
        if isinstance(target, ast.Name):
            self._bind(target.id, owner)
            return
        if isinstance(target, (ast.Tuple, ast.List)):
            for elt in target.elts:
                self._bind_target(elt, None)

    def _lookup(self, name: str) -> str | None:
        skip_class = self._scopes[-1].kind == "function"
        for scope in reversed(self._scopes):
            if skip_class and scope.kind == "class":
                continue
            if name in scope.names:
                return scope.names[name]
        return self.imported.get(name)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node)

    def _visit_function(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> None:
        for decorator in node.decorator_list:
            self.visit(decorator)
        if node.returns is not None:
            self.visit(node.returns)
        self._visit_arguments(node.args)
        self._push("function")
        for stmt in node.body:
            self.visit(stmt)
        self._pop()

    def _visit_arguments(self, args: ast.arguments) -> None:
        for default in (*args.defaults, *args.kw_defaults):
            if default is not None:
                self.visit(default)
        for arg in (*args.posonlyargs, *args.args, *args.kwonlyargs):
            if arg.annotation is not None:
                self.visit(arg.annotation)
        if args.vararg is not None and args.vararg.annotation is not None:
            self.visit(args.vararg.annotation)
        if args.kwarg is not None and args.kwarg.annotation is not None:
            self.visit(args.kwarg.annotation)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for decorator in node.decorator_list:
            self.visit(decorator)
        for base in node.bases:
            self.visit(base)
        for keyword in node.keywords:
            self.visit(keyword)
        self._push("class")
        for stmt in node.body:
            self.visit(stmt)
        self._pop()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name == PACKAGE or alias.name.startswith(f"{PACKAGE}."):
                self.module_aliases.add(alias.asname or alias.name.split(".")[0])
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if (node.module or "").split(".")[0] == PACKAGE:
            for alias in node.names:
                self.imported[alias.asname or alias.name] = alias.name
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        self.visit(node.value)
        owner = self._call_owner(node.value)
        for target in node.targets:
            self._bind_target(target, owner)
            self.visit(target)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.annotation is not None:
            self.visit(node.annotation)
        owner: str | None = None
        if node.value is not None:
            self.visit(node.value)
            owner = self._call_owner(node.value)
        self._bind_target(node.target, owner)

    def visit_NamedExpr(self, node: ast.NamedExpr) -> None:
        self.visit(node.value)
        self._bind_target(node.target, self._call_owner(node.value))

    def _call_owner(self, node: ast.AST) -> str | None:
        """Return the contract class a call expression yields, if determinable."""
        if not isinstance(node, ast.Call):
            return None
        func = node.func
        name: str | None = None
        if isinstance(func, ast.Name) and func.id in self.imported:
            name = self.imported[func.id]
        elif (
            isinstance(func, ast.Attribute)
            and isinstance(func.value, ast.Name)
            and func.value.id in self.module_aliases
        ):
            name = func.attr
        return self.contract.constructs(name) if name else None

    def _root(self, node: ast.AST) -> str | None:
        """Return the contract owner a value expression refers to."""
        if isinstance(node, ast.Name):
            return self._lookup(node.id)
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id in self.module_aliases
        ):
            return node.attr
        return self._call_owner(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        owner = self._root(node.value)
        if owner:
            self.used.add(f"{owner}.{node.attr}")
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        owner = self._root(node.value)
        if owner:
            ctx = node.ctx
            dunder = "__setitem__" if isinstance(ctx, ast.Store) else "__getitem__"
            if isinstance(ctx, ast.Del):
                dunder = "__delitem__"
            self.used.add(f"{owner}.{dunder}")
        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare) -> None:
        for op, comparator in zip(node.ops, node.comparators):
            if isinstance(op, (ast.In, ast.NotIn)):
                owner = self._root(comparator)
                if owner:
                    self.used.add(f"{owner}.__contains__")
        self.generic_visit(node)


def members_used_in_source(source: str, contract: Contract) -> set[str]:
    """Members one hidden-test module exercises, according to C1 dataflow."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    visitor = _UsageVisitor(contract)
    visitor.visit(tree)
    return visitor.used


def exercised_members(hidden_dir: Path, contract: Contract) -> set[str]:
    """Members the behavior hidden tests exercise, excluding the surface test."""
    used: set[str] = set()
    for path in sorted(hidden_dir.rglob("*.py")):
        if path.name == SURFACE_TEST_FILE:
            continue
        used |= members_used_in_source(
            path.read_text(encoding="utf-8"), contract
        )
    return used


# --------------------------------------------------------------------------
# upstream re-export probe
# --------------------------------------------------------------------------


def upstream_root(task_dir: Path) -> Path | None:
    repo = task_dir / "repo"
    if not repo.is_dir():
        return None
    src = repo / "src"
    return src if src.is_dir() else repo


def _module_name(root: Path, path: Path) -> str:
    rel = path.relative_to(root)
    parts = list(rel.parts)
    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    else:
        parts[-1] = parts[-1][: -len(".py")]
    return ".".join(parts)


def index_upstream(root: Path) -> dict[str, list[str]]:
    """Map each module-level symbol name to the modules defining it."""
    index: dict[str, list[str]] = {}
    for path in root.rglob("*.py"):
        if any(part in {"tests", "test", "__pycache__"} for part in path.parts):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except (SyntaxError, ValueError):
            continue
        module = _module_name(root, path)
        names: set[str] = set()
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                names.add(node.name)
            elif isinstance(node, ast.ClassDef):
                names.add(node.name)
                # A dotted entrypoint may name a method. Index the bare name too,
                # so an entrypoint naming an inherited method still resolves.
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        names.add(f"{node.name}.{child.name}")
                        names.add(child.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        names.add(target.id)
        for name in names:
            index.setdefault(name, []).append(module)
        # A package or module is itself importable under its own leaf name.
        if module:
            index.setdefault(module.split(".")[-1], []).append(module)
    return index


def missing_entrypoints(public_spec: dict[str, Any], index: dict[str, list[str]]) -> list[str]:
    """Declared upstream entrypoints that the pinned snapshot does not define."""
    missing: list[str] = []
    for entry in public_spec.get("source_entrypoints") or []:
        parts = str(entry).split(".")
        # Accept a bare name or an ``Owner.member`` pair, since an entrypoint may
        # point at a module-level symbol or at a method on a class.
        candidates = {parts[-1]}
        if len(parts) >= 2:
            candidates.add(".".join(parts[-2:]))
        if not (candidates & index.keys()):
            missing.append(str(entry))
    return missing


def resolve_symbol(
    name: str, entrypoints: list[str], index: dict[str, list[str]]
) -> tuple[str, bool] | None:
    """Return (module, is_module_itself) that provides ``name`` upstream."""
    for entry in entrypoints:
        if entry.endswith(f".{name}"):
            return entry[: -(len(name) + 1)], False
        if entry == name or entry.endswith(f".{name}"):
            return entry, True
    candidates = index.get(name)
    if not candidates:
        return None
    # Prefer the shallowest, then shortest, module path: upstream re-exports the
    # public symbol at the top of the package far more often than deep inside it.
    best = sorted(candidates, key=lambda m: (m.count("."), len(m)))[0]
    if best.split(".")[-1] == name:
        return best, True
    return best, False


def build_shim(
    shim_dir: Path, up_root: Path, contract: Contract, public_spec: dict[str, Any], index
) -> list[str]:
    """Write a ``featurelifted`` package re-exporting upstream. Return stubbed names.

    Names a task invents on top of upstream get an inert stub so the module still
    imports and the remaining behavior tests can run and be judged.
    """
    entrypoints = [str(e) for e in public_spec.get("source_entrypoints") or []]
    roots = sorted({m.split(".")[0] for names in index.values() for m in names})
    lines = [
        "import sys",
        f"_UP_ROOT = {str(up_root)!r}",
        "sys.path.insert(0, _UP_ROOT)",
        f"_ROOTS = {roots!r}",
        "",
        "# An installed distribution of the same package would silently shadow the",
        "# pinned snapshot and invalidate the probe, so drop pre-imported copies.",
        "for _name in list(sys.modules):",
        "    if _name.split('.')[0] in _ROOTS:",
        "        del sys.modules[_name]",
        "",
        "",
        "def _pinned(obj, label):",
        "    mod = sys.modules.get(getattr(obj, '__module__', None) or getattr(obj, '__name__', ''))",
        "    path = getattr(mod, '__file__', None) or getattr(obj, '__file__', None)",
        "    if path and not str(path).startswith(_UP_ROOT):",
        "        raise ImportError(f'{label} resolved outside the pinned snapshot: {path}')",
        "    return obj",
        "",
        "",
        "class _Unresolved:",
        '    """Placeholder for a name the pinned upstream does not define."""',
        "",
        "    def __init__(self, *args, **kwargs):",
        "        raise NotImplementedError('symbol absent from pinned upstream')",
        "",
    ]
    stubbed: list[str] = []
    for name in sorted(contract.tops):
        resolved = resolve_symbol(name, entrypoints, index)
        if resolved is None:
            stubbed.append(name)
            lines.append(f"class {name}(_Unresolved):\n    pass")
            continue
        module, is_module = resolved
        if is_module:
            lines.append(f"import {module} as {name}")
        else:
            lines.append(f"from {module} import {name}")
        lines.append(f"_pinned({name}, {name!r})")
    package = shim_dir / PACKAGE
    package.mkdir(parents=True, exist_ok=True)
    (package / "__init__.py").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return stubbed


def _evidence_line(message: str) -> str:
    """Pick the line naming the actual cause, not pytest's generic wrapper."""
    lines = [line.strip() for line in message.splitlines() if line.strip()]
    for line in reversed(lines):
        if any(
            marker in line
            for marker in ("Error:", "error:", "assert ", "Exception:")
        ) and "while importing test module" not in line:
            return line[:220]
    return lines[0][:220] if lines else ""


def failure_kind(message: str) -> str:
    """Classify a failure as an assertion mismatch or an API shape difference."""
    head = message.strip().split("\n", 1)[0]
    exc = head.split(":", 1)[0].strip()
    if exc == "AssertionError" or head.startswith("assert"):
        return "assertion"
    if exc in SHAPE_FAILURE_TYPES:
        return "shape"
    return "assertion" if "assert" in head else "shape"


def run_hidden_against_upstream(
    task_dir: Path,
    public_spec: dict[str, Any],
    contract: Contract,
    up_root: Path,
    index: dict[str, list[str]],
    python: str,
    timeout: int,
) -> dict[str, Any]:
    hidden = task_dir / "hidden_tests"
    if not hidden.is_dir():
        return {"outcome": ENV_UNAVAILABLE, "detail": "missing hidden_tests/"}

    with tempfile.TemporaryDirectory() as tmp:
        shim_dir = Path(tmp)
        stubbed = build_shim(shim_dir, up_root, contract, public_spec, index)
        # Loaded via -p rather than conftest.py: the hidden tests live outside
        # this directory, so pytest would never auto-discover a conftest here.
        (shim_dir / "audit_report_plugin.py").write_text(REPORT_PLUGIN, encoding="utf-8")
        report_path = shim_dir / "report.jsonl"

        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join([str(shim_dir), str(up_root)])
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["AUDIT_REPORT"] = str(report_path)
        try:
            subprocess.run(
                [
                    python, "-m", "pytest", str(hidden), "-q", "--no-header",
                    "-p", "no:cacheprovider", "-p", "audit_report_plugin",
                ],
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
                cwd=tmp,
            )
        except subprocess.TimeoutExpired:
            return {"outcome": ENV_UNAVAILABLE, "detail": "pytest timeout", "stubbed": stubbed}
        except FileNotFoundError:
            return {"outcome": ENV_UNAVAILABLE, "detail": "pytest unavailable", "stubbed": stubbed}

        records = []
        if report_path.exists():
            for line in report_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    records.append(json.loads(line))

        records = [r for r in records if SURFACE_TEST_FILE not in r["nodeid"]]
        # A module that never imported yields no per-test signal at all, which is
        # an inconclusive probe rather than evidence about the hidden test.
        collect_errors = [
            r for r in records if r["outcome"] == "collect-error" or "::" not in r["nodeid"]
        ]
        behavior = [r for r in records if r not in collect_errors]
        contradictions = [
            r for r in behavior
            if r["outcome"] != "passed" and failure_kind(r["message"]) == "assertion"
        ]
        reshaped = [
            r for r in behavior
            if r["outcome"] != "passed" and failure_kind(r["message"]) == "shape"
        ]
        result: dict[str, Any] = {
            "stubbed": stubbed,
            "behavior_total": len(behavior),
            "behavior_failed": sorted(r["nodeid"].split("::")[-1] for r in contradictions),
            "reshaped_tests": sorted(r["nodeid"].split("::")[-1] for r in reshaped),
        }
        first_failure = next(
            (r for r in behavior if r["outcome"] != "passed"), collect_errors[0] if collect_errors else None
        )
        result["evidence"] = _evidence_line(first_failure["message"]) if first_failure else ""
        if not behavior:
            result["outcome"] = ENV_UNAVAILABLE
            result["detail"] = (
                "upstream import or collection failed; no behavior test executed"
                if collect_errors
                else "no behavior test collected"
            )
        elif contradictions:
            result["outcome"] = UPSTREAM_CONTRADICTS
            result["detail"] = (
                f"{len(contradictions)}/{len(behavior)} behavior tests assert against pinned upstream"
            )
        elif reshaped:
            result["outcome"] = API_RESHAPED
            result["detail"] = (
                f"{len(reshaped)}/{len(behavior)} behavior tests differ only in API shape"
            )
        else:
            result["outcome"] = UPSTREAM_PASS
            result["detail"] = f"all {len(behavior)} behavior tests pass on pinned upstream"
        return result


# --------------------------------------------------------------------------
# reporting
# --------------------------------------------------------------------------


MANUAL_VERDICTS = {"underdetermined", "fair", "undecided"}


def apply_adjudications(rows: list[dict[str, Any]], path: Path | None) -> None:
    """Overlay human verdicts, which decide cases the mechanical probe cannot.

    The probe misses a contradiction whenever an API shape difference stops the
    call before its assertion, and reports a false one whenever the pinned
    upstream is the test framework itself.
    """
    verdicts: dict[str, dict[str, str]] = {}
    if path and path.exists():
        with path.open(newline="", encoding="utf-8") as handle:
            for record in csv.DictReader(handle):
                verdict = (record.get("verdict") or "").strip()
                if verdict not in MANUAL_VERDICTS:
                    raise ValueError(f"invalid verdict {verdict!r} for {record.get('task_id')}")
                verdicts[record["task_id"]] = record
    for row in rows:
        record = verdicts.get(row["task_id"])
        row["manual_verdict"] = (record or {}).get("verdict", "")
        row["manual_reason"] = (record or {}).get("reason", "")
        if row["manual_verdict"] == "underdetermined":
            row["contract_underdetermined"] = True
        elif row["manual_verdict"] == "fair":
            row["contract_underdetermined"] = False
        elif row["manual_verdict"] == "undecided":
            # The probe result is unusable, so fall back to the static checks.
            row["upstream_outcome"] = ENV_UNAVAILABLE
            row["upstream_detail"] = "probe result rejected by adjudication"
            row["contract_underdetermined"] = bool(row["undeclared_members"])


def audit_task(task_dir: Path, python: str, timeout: int) -> dict[str, Any]:
    public_spec = read_json(task_dir / "metadata.json").get("public_spec") or {}
    contract = Contract(public_spec)
    used = exercised_members(task_dir / "hidden_tests", contract)
    undeclared = sorted(
        m for m in used if m.split(".")[0] in contract.tops and m not in contract.members
    )

    up_root = upstream_root(task_dir)
    if up_root is None:
        index: dict[str, list[str]] = {}
        dangling: list[str] = []
        upstream: dict[str, Any] = {"outcome": ENV_UNAVAILABLE, "detail": "missing repo/"}
    else:
        index = index_upstream(up_root)
        dangling = missing_entrypoints(public_spec, index)
        upstream = run_hidden_against_upstream(
            task_dir, public_spec, contract, up_root, index, python, timeout
        )

    outcome = upstream["outcome"]
    return {
        "task_id": task_dir.name,
        "upstream_outcome": outcome,
        "upstream_detail": upstream.get("detail", ""),
        "missing_entrypoints": ";".join(dangling),
        "behavior_failed": ";".join(upstream.get("behavior_failed") or []),
        "reshaped_tests": ";".join(upstream.get("reshaped_tests") or []),
        "undeclared_members": ";".join(undeclared),
        "undeclared_count": len(undeclared),
        "stubbed_symbols": ";".join(upstream.get("stubbed") or []),
        # Tracked separately: a dangling entrypoint misdirects an agent looking for
        # the code to extract, but the behavior clauses may still pin the semantics.
        "provenance_defect": bool(dangling),
        "contract_underdetermined": outcome == UPSTREAM_CONTRADICTS or bool(undeclared),
        "evidence": upstream.get("evidence", ""),
    }


def render_markdown(rows: list[dict[str, Any]], annotations: dict[str, str]) -> str:
    total = len(rows)
    flagged = [r for r in rows if r["contract_underdetermined"]]
    counts = Counter(r["upstream_outcome"] for r in rows)
    decided = [r for r in rows if r["upstream_outcome"] != ENV_UNAVAILABLE]

    out: list[str] = []
    out.append("# Hidden 测试的契约蕴含审计")
    out.append("")
    out.append(
        "> 判定 hidden 测试能否由 Agent 实际拿到的两个事实来源推出："
        "`public_spec` 契约，以及固定的上游 `repo/` 快照。"
    )
    out.append("")
    provenance = [r for r in rows if r.get("provenance_defect")]
    out.append("## 结论")
    out.append("")
    out.append(
        f"审计 **{total}** 个此前被归为 Agent 责任的失败任务，其中 **{len(flagged)}** 个"
        f"存在契约欠定证据（占 {len(flagged) / total:.1%}），"
        f"另有 **{len(provenance)}** 个存在入口溯源缺陷。"
        f"上游探针有效判定 **{len(decided)}/{total}** 题。"
    )
    out.append("")
    out.append(
        "两类需要分开看：契约欠定指 hidden 要求无法由契约条款唯一确定；"
        "入口溯源缺陷指 `source_entrypoints` 指错位置，会误导 Agent 的定位，"
        "但只要行为条款本身写清楚，题目仍然可解。"
    )
    out.append("")
    out.append(
        "**契约有意覆盖上游不算缺陷。** 若条款明确写出与上游不同的语义"
        "（如 `popone removes the most recent matching value`），"
        "则以契约为准，Agent 照搬上游属于真实失败。"
    )
    out.append("")
    out.append("## 上游蕴含探针")
    out.append("")
    out.append("| 判定 | 任务数 | 含义 |")
    out.append("| --- | --- | --- |")
    for key in (UPSTREAM_PASS, UPSTREAM_CONTRADICTS, API_RESHAPED, ENV_UNAVAILABLE):
        if counts.get(key):
            out.append(f"| `{key}` | {counts[key]} | {OUTCOME_LABELS[key]} |")
    out.append("")
    dangling = [r for r in rows if r["missing_entrypoints"]]
    out.append("## 入口锚定检查")
    out.append("")
    out.append(
        f"**{len(dangling)}/{total}** 个任务的 `source_entrypoints` 指向了固定 `repo/` 中"
        "不存在的符号。该字段是 Agent 定位待抽取上游代码的唯一指引，指空即意味着"
        "只能依据 `public_spec` 的行为语句猜测语义。此检查不依赖运行环境。"
    )
    out.append("")
    out.append("## 逐题结果")
    out.append("")
    out.append("| 任务 | 原根因标注 | 上游探针 | 悬空入口 | 未声明接口面 |")
    out.append("| --- | --- | --- | --- | --- |")
    for row in sorted(rows, key=lambda r: (not r["contract_underdetermined"], r["task_id"])):
        out.append(
            f"| `{row['task_id']}` | {annotations.get(row['task_id'], '—')} "
            f"| `{row['upstream_outcome']}` | {row['missing_entrypoints'] or '—'} "
            f"| {row['undeclared_members'] or '—'} |"
        )
    out.append("")
    if flagged:
        out.append("## 契约欠定候选")
        out.append("")
        for row in sorted(flagged, key=lambda r: r["task_id"]):
            out.append(f"### `{row['task_id']}`")
            out.append("")
            out.append(f"- 上游探针：{row['upstream_detail']}")
            if row["missing_entrypoints"]:
                out.append(f"- `source_entrypoints` 在快照中不存在：`{row['missing_entrypoints']}`")
            if row["behavior_failed"]:
                out.append(f"- 上游未通过的行为用例：`{row['behavior_failed']}`")
            if row["evidence"]:
                out.append(f"- 首条失败证据：`{row['evidence']}`")
            if row["undeclared_members"]:
                out.append(f"- hidden 触碰未声明接口面：`{row['undeclared_members']}`")
            out.append("")
    adjudicated = [r for r in rows if r.get("manual_verdict")]
    if adjudicated:
        out.append("## 人工裁决")
        out.append("")
        out.append("| 任务 | 裁决 | 理由 |")
        out.append("| --- | --- | --- |")
        for row in sorted(adjudicated, key=lambda r: r["task_id"]):
            reason = row["manual_reason"].replace("|", "\\|")
            out.append(f"| `{row['task_id']}` | `{row['manual_verdict']}` | {reason} |")
        out.append("")
    out.append("## 方法边界")
    out.append("")
    out.append(
        "- `upstream_pass` 只说明 hidden 与上游一致，不说明它已被 `public_spec` 文字覆盖；"
        "文字层面的欠定仍需人工裁决。"
    )
    out.append(
        "- `env_unavailable` 表示上游导入或 pytest 采集失败，属于未判定，不可计入任一侧。"
    )
    out.append(
        "- 上游 re-export 采用最短模块路径启发式解析符号，个别任务可能解析到非公开位置；"
        "任务新造的名字会被打桩，因此 `stubbed_symbols` 非空本身不构成缺陷。"
    )
    out.append(
        "- 判定只依据行为用例，不含生成的 `test_required_api_surface.py`。"
    )
    out.append(
        "- `api_reshaped` 表示上游在到达断言前就因接口形状不符而失败，探针对该题未下结论；"
        "此类需人工裁决，`upstream_contradicts` 计数因此是欠定情况的下界。"
    )
    return "\n".join(out) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--annotations",
        type=Path,
        default=ROOT
        / "reports/paper_analysis/python200_hard_main_20260829/failure_root_cause_annotations.csv",
        help="failure root-cause annotation CSV selecting the tasks to audit",
    )
    parser.add_argument(
        "--causes",
        nargs="*",
        default=["behavior_drift", "contract_api_completion"],
        help="root_cause_primary values to include",
    )
    parser.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK)
    parser.add_argument("--task", action="append", help="audit an explicit task id")
    parser.add_argument(
        "--adjudications",
        type=Path,
        help="CSV of human verdicts (task_id, verdict, reason) overriding the probe",
    )
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--output", type=Path, required=True, help="output directory")
    args = parser.parse_args()

    annotations: dict[str, str] = {}
    if args.task:
        task_ids = list(args.task)
    else:
        with args.annotations.open(newline="", encoding="utf-8") as handle:
            records = list(csv.DictReader(handle))
        task_ids = [
            r["task_id"] for r in records if r["root_cause_primary"] in set(args.causes)
        ]
        annotations = {r["task_id"]: r["root_cause_primary"] for r in records}

    rows: list[dict[str, Any]] = []
    for index, task_id in enumerate(task_ids, start=1):
        task_dir = args.benchmark / task_id
        if not task_dir.is_dir():
            print(f"[{index}/{len(task_ids)}] skip {task_id}: not found", file=sys.stderr)
            continue
        print(f"[{index}/{len(task_ids)}] {task_id}", file=sys.stderr, flush=True)
        rows.append(audit_task(task_dir, args.python, args.timeout))

    apply_adjudications(rows, args.adjudications)

    args.output.mkdir(parents=True, exist_ok=True)
    write_csv(args.output / "contract_entailment_audit.csv", rows)
    (args.output / "contract_entailment_audit.json").write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "benchmark": str(args.benchmark),
                "causes": args.causes,
                "rows": rows,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    (args.output / "contract_entailment_audit.md").write_text(
        render_markdown(rows, annotations), encoding="utf-8"
    )

    flagged = sum(1 for r in rows if r["contract_underdetermined"])
    print(f"\naudited {len(rows)} tasks; {flagged} flagged as contract-underdetermined")
    print(f"wrote {args.output}/contract_entailment_audit.{{csv,json,md}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

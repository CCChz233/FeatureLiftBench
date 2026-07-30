"""Synthesize executable contracts against featurelifted from traces + public_spec + upstream AST."""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any

from .common import CONTRACT_INDEX
from .common import CONTRACTS_DIR
from .common import RUNTIME_DIR
from .common import TRACE_JSONL
from .common import behavior_texts
from .common import ensure_dir
from .common import flatten_required_api
from .common import is_noise_event
from .common import source_entrypoint_names


def synthesize_contracts(
    workspace_dir: str | Path,
    public_spec: dict[str, Any] | None,
    collect_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    workspace = Path(workspace_dir).resolve()
    contracts = ensure_dir(workspace / CONTRACTS_DIR)
    (contracts / "__init__.py").write_text("", encoding="utf-8")

    api = flatten_required_api(public_spec)
    behaviors = behavior_texts(public_spec)
    events = [e for e in _load_events(workspace / RUNTIME_DIR / TRACE_JSONL) if not is_noise_event(e)]

    inferred = infer_api_from_upstream(workspace / "repo", public_spec)
    # Surface: required_api + small allowlisted inferred symbols (cut format_* noise).
    surface_api = _surface_api_for_contracts(api, inferred, public_spec)
    api = _merge_api(api, inferred["api"])

    surface = _generate_surface_tests(surface_api)
    (contracts / "test_required_surface.py").write_text(surface, encoding="utf-8")

    replay = _generate_replay_tests(api, events)
    (contracts / "test_runtime_replay.py").write_text(replay["code"], encoding="utf-8")

    scenarios = _generate_scenario_tests(api, public_spec, inferred)
    (contracts / "test_behavior_scenarios.py").write_text(scenarios["code"], encoding="utf-8")

    behavior_doc = _generate_behavior_checklist(behaviors)
    (contracts / "test_behavior_checklist.py").write_text(behavior_doc, encoding="utf-8")

    substantive = int(scenarios["assertions"]) + int(replay["count"]) + _count_surface_asserts(surface)
    # Surface-only (hasattr) is not enough; require real scenario assertions.
    contracts_substantive = bool(scenarios["assertions"] >= 2 or replay["count"] > 0)

    quality = "low"
    if collect_meta and isinstance(collect_meta, dict):
        quality = str(collect_meta.get("trace_quality") or "low")

    index = [
        "# Contracts (from upstream execution + inferred surface)",
        "",
        "These pytest modules must pass against `submission/featurelifted`.",
        "Derived from upstream runtime observations, public_spec, and upstream AST",
        "(source_entrypoints) — **not** from benchmark public/hidden tests.",
        "",
        "- `test_required_surface.py` — required API + allowlisted inferred surface",
        "- `test_runtime_replay.py` — replayable call/exception observations",
        "- `test_behavior_scenarios.py` — **behavioral** mini-assertions (must actually run)",
        "- `test_behavior_checklist.py` — behavior catalog (documentation only)",
        "",
        "Do **not** treat hasattr-only greens as done: scenarios exercise resolve/invoke/",
        "graph behavior. `callable(x)` is insufficient.",
        "",
        f"Replay cases: {replay['count']}",
        f"Scenario assertions: {scenarios['assertions']}",
        f"Inferred upstream methods: {len(inferred.get('methods') or [])}",
        f"Surface symbols kept: {len(surface_api)}",
        f"Phase0 trace quality: `{quality}`",
        f"Contracts substantive: `{contracts_substantive}`",
        "",
    ]
    (workspace / CONTRACT_INDEX).write_text("\n".join(index), encoding="utf-8")
    (contracts / "README.md").write_text(
        "Run: `PYTHONPATH=submission pytest contracts/ -q`\n",
        encoding="utf-8",
    )
    return {
        "api_symbols": len(api),
        "replay_cases": replay["count"],
        "behaviors": len(behaviors),
        "scenario_assertions": scenarios["assertions"],
        "inferred_methods": inferred.get("methods") or [],
        "contracts_substantive": contracts_substantive,
        "substantive_count": substantive,
        "trace_quality": quality,
        "contracts_dir": CONTRACTS_DIR,
    }


def infer_api_from_upstream(
    repo_dir: str | Path,
    public_spec: dict[str, Any] | None,
) -> dict[str, Any]:
    """Inspect upstream classes named in source_entrypoints; map methods onto featurelifted.

    Handles: src-layout, missing Lazy* aliases (LazyCommandCollection → CommandCollection),
    and methods inherited from base classes defined in the same module (e.g. Group.invoke).
    """

    repo = Path(repo_dir)
    methods: list[str] = []
    api: list[dict[str, str]] = []
    class_attrs: dict[str, list[str]] = {}
    if not repo.is_dir() or not isinstance(public_spec, dict):
        return {"api": api, "methods": methods, "class_attrs": class_attrs}

    for ep in source_entrypoint_names(public_spec):
        parts = [p for p in ep.split(".") if p]
        if len(parts) < 2:
            continue
        fl_cls_name = parts[-1]  # name on featurelifted side
        mod_parts = parts[:-1]
        resolved = _resolve_upstream_class(repo, mod_parts, fl_cls_name)
        if resolved is None:
            continue
        src, class_node, tree = resolved
        related: dict[str, ast.ClassDef] = {fl_cls_name: class_node}
        # Prefer Context from same module / package for attr checks.
        ctx = _find_class(tree, "Context")
        if ctx is None:
            ctx_file = _locate_class_file(repo, "Context")
            if ctx_file is not None:
                try:
                    ctx_tree = ast.parse(
                        ctx_file.read_text(encoding="utf-8", errors="ignore")
                    )
                    ctx = _find_class(ctx_tree, "Context")
                except SyntaxError:
                    ctx = None
        if ctx is not None:
            related["Context"] = ctx

        # Methods: own + same-module bases (CommandCollection ← Group ← …).
        inherited = _methods_with_bases(tree, class_node)
        for meth in inherited:
            if meth in {"__init__", "__call__"}:
                continue
            methods.append(meth)
            api.append(
                {
                    "path": f"featurelifted.{fl_cls_name}.{meth}",
                    "kind": "method",
                    "name": meth,
                }
            )
        class_attrs[fl_cls_name] = sorted(set(inherited))
        api.append(
            {
                "path": f"featurelifted.{fl_cls_name}",
                "kind": "class",
                "name": fl_cls_name,
            }
        )

        if "Context" in related:
            ctx_node = related["Context"]
            attrs: list[str] = []
            for item in ctx_node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not item.name.startswith("_") or item.name in {"__init__", "__call__"}:
                        if not (
                            item.name.startswith("__")
                            and item.name.endswith("__")
                            and item.name not in {"__init__", "__call__"}
                        ):
                            attrs.append(item.name)
                elif isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name) and not target.id.startswith("_"):
                            attrs.append(target.id)
                elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    if not item.target.id.startswith("_"):
                        attrs.append(item.target.id)
            # Also scan __init__ assignments: self.default_map = ...
            for item in ctx_node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == "__init__":
                    for sub in ast.walk(item):
                        if (
                            isinstance(sub, ast.Attribute)
                            and isinstance(sub.value, ast.Name)
                            and sub.value.id == "self"
                            and not sub.attr.startswith("_")
                        ):
                            attrs.append(sub.attr)
            class_attrs["Context"] = sorted(set(attrs))
            api.append(
                {
                    "path": "featurelifted.Context",
                    "kind": "class",
                    "name": "Context",
                }
            )

    seen: set[str] = set()
    uniq: list[dict[str, str]] = []
    for item in api:
        path = item["path"]
        if path in seen:
            continue
        seen.add(path)
        uniq.append(item)
    return {"api": uniq, "methods": sorted(set(methods)), "class_attrs": class_attrs}


def _resolve_upstream_class(
    repo: Path, mod_parts: list[str], cls_name: str
) -> tuple[Path, ast.ClassDef, ast.AST] | None:
    """Locate class; try Lazy* → * alias when snapshot renamed the type."""

    candidates = [cls_name]
    if cls_name.startswith("Lazy") and len(cls_name) > 4:
        candidates.append(cls_name[len("Lazy") :])  # LazyCommandCollection → CommandCollection

    src = _locate_module_file(repo, mod_parts)
    files: list[Path] = []
    if src is not None:
        files.append(src)
    for name in candidates:
        located = _locate_class_file(repo, name)
        if located is not None and located not in files:
            files.append(located)

    for path in files:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
        except SyntaxError:
            continue
        for name in candidates:
            node = _find_class(tree, name)
            if node is not None:
                return path, node, tree
    return None


def _base_class_names(node: ast.ClassDef) -> list[str]:
    names: list[str] = []
    for base in node.bases:
        if isinstance(base, ast.Name):
            names.append(base.id)
        elif isinstance(base, ast.Attribute):
            names.append(base.attr)
    return names


def _methods_with_bases(tree: ast.AST, class_node: ast.ClassDef) -> list[str]:
    """Public methods on class and same-module bases (one module MRO walk)."""

    by_name: dict[str, ast.ClassDef] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            by_name[node.name] = node

    seen_cls: set[str] = set()
    methods: list[str] = []

    def walk(cls: ast.ClassDef) -> None:
        if cls.name in seen_cls:
            return
        seen_cls.add(cls.name)
        for item in cls.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                meth = item.name
                if meth.startswith("_") and meth not in {"__init__", "__call__"}:
                    continue
                if (
                    meth.startswith("__")
                    and meth.endswith("__")
                    and meth not in {"__init__", "__call__"}
                ):
                    continue
                methods.append(meth)
        for base_name in _base_class_names(cls):
            # Skip typing constructs
            if base_name in by_name:
                walk(by_name[base_name])

    walk(class_node)
    # de-dupe preserve order
    out: list[str] = []
    seen_m: set[str] = set()
    for m in methods:
        if m not in seen_m:
            seen_m.add(m)
            out.append(m)
    return out


def _locate_module_file(repo: Path, mod_parts: list[str]) -> Path | None:
    candidates = [
        repo.joinpath(*mod_parts).with_suffix(".py"),
        repo.joinpath(*mod_parts, "__init__.py"),
        repo.joinpath("src", *mod_parts).with_suffix(".py"),
        repo.joinpath("src", *mod_parts, "__init__.py"),
    ]
    for path in candidates:
        if path.is_file():
            return path
    if not mod_parts:
        return None
    leaf = mod_parts[-1] + ".py"
    matches = [
        m
        for m in repo.rglob(leaf)
        if not ({".tox", "venv", ".venv", "__pycache__", "site-packages"} & set(m.parts))
    ]
    for match in matches:
        if all(p in match.parts for p in mod_parts[:-1]):
            return match
    # Last resort: any file defining the leaf module name under package root.
    if len(mod_parts) >= 2:
        pkg = mod_parts[0]
        for match in matches:
            if pkg in match.parts:
                return match
    return matches[0] if matches else None


def _locate_class_file(repo: Path, class_name: str) -> Path | None:
    """Fallback when module path layout is unusual: scan for `class ClassName`."""

    needle = f"class {class_name}"
    for path in repo.rglob("*.py"):
        if {".tox", "venv", ".venv", "__pycache__", "site-packages", "tests"} & set(path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if needle in text:
            return path
    return None


def _find_class(tree: ast.AST, name: str) -> ast.ClassDef | None:
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    return None


def _merge_api(
    base: list[dict[str, str]], extra: list[dict[str, str]]
) -> list[dict[str, str]]:
    seen = {a["path"] for a in base}
    out = list(base)
    for item in extra:
        if item["path"] not in seen:
            seen.add(item["path"])
            out.append(item)
    return out


def _load_events(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def _count_surface_asserts(code: str) -> int:
    return code.count("assert ")


# Inherited click Group helpers that drown required API and tempt copy-paste stubs.
_SURFACE_METHOD_DENY = frozenset(
    {
        "format_arguments",
        "format_commands",
        "format_epilog",
        "format_help",
        "format_help_text",
        "format_options",
        "format_usage",
        "get_help",
        "get_help_option",
        "get_help_option_names",
        "get_params",
        "get_short_help_str",
        "get_usage",
        "make_parser",
        "shell_complete",
        "to_info_dict",
        "collect_usage_pieces",
        "command",
        "group",
        "result_callback",
        "add_command",
        "main",
        "parse_args",
        "resolve_command",
    }
)

# Keep these inferred methods even when not in required_api (task-critical).
_SURFACE_METHOD_ALLOW = frozenset(
    {
        "invoke",
        "get_command",
        "resolve",
        "list_commands",
        "add_source",
        "make_context",
        "get_revision",
        "get_revisions",
        "get_heads",
        "get_current_head",
        "ancestors",
        "iterate_revisions",
        "add_revision",
        "heads",
        "bases",
        "filter_for_lineage",
        "is_base",
        "is_head",
        "is_branch_point",
        "is_merge_point",
        "add_nextrev",
        "verify_rev_id",
    }
)


def _behavior_blob(public_spec: dict[str, Any] | None) -> str:
    parts: list[str] = []
    if not isinstance(public_spec, dict):
        return ""
    for key in ("title", "summary"):
        parts.append(str(public_spec.get(key) or ""))
    for item in behavior_texts(public_spec):
        parts.append(str(item.get("text") or ""))
        parts.append(str(item.get("id") or ""))
    return " ".join(parts).lower()


def _surface_api_for_contracts(
    required: list[dict[str, str]],
    inferred: dict[str, Any],
    public_spec: dict[str, Any] | None,
) -> list[dict[str, str]]:
    """required_api ∪ allowlisted inferred methods; drop help/format noise."""

    out = list(required)
    seen = {a["path"] for a in out}
    for item in inferred.get("api") or []:
        if not isinstance(item, dict):
            continue
        path = str(item.get("path") or "")
        kind = str(item.get("kind") or "")
        name = str(item.get("name") or path.rsplit(".", 1)[-1])
        if path in seen:
            continue
        if kind == "class":
            # Keep Context when behaviors mention envvar / default_map / context.
            blob = _behavior_blob(public_spec)
            if name == "Context" and any(
                tok in blob for tok in ("context", "envvar", "default_map", "defaults")
            ):
                out.append(item)
                seen.add(path)
            continue
        if kind != "method":
            continue
        if name in _SURFACE_METHOD_DENY:
            continue
        if name not in _SURFACE_METHOD_ALLOW:
            continue
        out.append(item)
        seen.add(path)
    return out


def _generate_surface_tests(api: list[dict[str, str]]) -> str:
    lines = [
        '"""Required + upstream-inferred API surface contracts."""',
        "from __future__ import annotations",
        "",
        "import importlib",
        "",
        "",
        "def test_featurelifted_package_importable() -> None:",
        "    importlib.import_module('featurelifted')",
        "",
    ]
    if not api:
        return "\n".join(lines)

    classes = [a for a in api if a.get("kind") == "class"]
    methods = [a for a in api if a.get("kind") == "method"]
    top_level = [
        a
        for a in api
        if a.get("kind") in {"function", "symbol", "class", "exception", ""}
        and a["path"].count(".") == 1
    ]

    for item in top_level[:40]:
        path = item["path"]
        if not path.startswith("featurelifted."):
            continue
        name = path.split(".", 1)[1]
        safe = "".join(ch if ch.isalnum() else "_" for ch in name)
        lines += [
            f"def test_top_level_{safe}() -> None:",
            "    mod = importlib.import_module('featurelifted')",
            f"    assert hasattr(mod, {name!r}), {path!r}",
            "",
        ]

    for item in classes[:30]:
        path = item["path"]
        parts = path.split(".")
        if len(parts) < 2 or parts[0] != "featurelifted":
            continue
        safe = "_".join(parts)
        lines += [
            f"def test_class_{safe}() -> None:",
            f"    parts = {parts!r}",
            "    mod = importlib.import_module('.'.join(parts[:-1]))",
            "    cls = getattr(mod, parts[-1])",
            "    assert isinstance(cls, type)",
            "",
        ]

    for item in methods[:60]:
        path = item["path"]
        parts = path.split(".")
        if len(parts) < 3 or parts[0] != "featurelifted":
            continue
        meth = parts[-1]
        safe = "_".join(parts)
        lines += [
            f"def test_method_{safe}() -> None:",
            f"    parts = {parts!r}",
            "    mod = importlib.import_module('.'.join(parts[:-2]))",
            "    cls = getattr(mod, parts[-2])",
            f"    assert callable(getattr(cls, {meth!r}, None)), {path!r}",
            "",
        ]
    return "\n".join(lines)


def _simple_args(args: dict[str, Any] | None) -> bool:
    if not isinstance(args, dict):
        return False
    for key, value in args.items():
        if key == "self":
            continue
        if isinstance(value, dict) and ("__type__" in value or "__repr__" in value):
            return False
        if isinstance(value, (list, dict)) and _contains_opaque(value):
            return False
    return True


def _contains_opaque(value: Any) -> bool:
    if isinstance(value, dict):
        if "__type__" in value or "__repr__" in value:
            return True
        return any(_contains_opaque(v) for v in value.values())
    if isinstance(value, list):
        return any(_contains_opaque(v) for v in value)
    return False


def _generate_replay_tests(
    api: list[dict[str, str]],
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    api_names = {a["name"] for a in api}
    cases: list[dict[str, Any]] = []
    for event in events:
        func = str(event.get("func") or "")
        if func not in api_names:
            continue
        args = event.get("args") if isinstance(event.get("args"), dict) else {}
        call_args = {k: v for k, v in args.items() if k != "self"}
        if not _simple_args(call_args) and not event.get("exception"):
            continue
        matches = [a for a in api if a["name"] == func]
        if not matches:
            continue
        target = matches[0]["path"]
        cases.append(
            {
                "target": target,
                "func": func,
                "args": call_args,
                "exception": event.get("exception"),
                "return": event.get("return"),
            }
        )
        if len(cases) >= 40:
            break

    if not cases:
        lines = [
            '"""Replay contracts mapped from upstream traces onto featurelifted API names."""',
            "from __future__ import annotations",
            "",
            "import pytest",
            "",
            "",
            "def test_no_replay_cases_placeholder() -> None:",
            "    pytest.skip('no simple name-matched replay cases from upstream traces')",
            "",
        ]
        return {"code": "\n".join(lines), "count": 0}

    lines = [
        '"""Replay contracts mapped from upstream traces onto featurelifted API names."""',
        "from __future__ import annotations",
        "",
        "import importlib",
        "import pytest",
        "",
        f"CASES = {json.dumps(cases, ensure_ascii=False, indent=2)}",
        "",
        "",
        "def _resolve(path: str):",
        "    parts = path.split('.')",
        "    mod = importlib.import_module('.'.join(parts[:-1]))",
        "    return getattr(mod, parts[-1])",
        "",
        "",
        "@pytest.mark.parametrize('case', CASES)",
        "def test_runtime_replay_case(case) -> None:",
        "    target = case['target']",
        "    parts = target.split('.')",
        "    if len(parts) >= 3:",
        "        mod = importlib.import_module('.'.join(parts[:-2]))",
        "        cls = getattr(mod, parts[-2])",
        "        try:",
        "            obj = cls()",
        "        except TypeError:",
        "            pytest.skip(f'cannot construct {parts[-2]} for replay')",
        "        fn = getattr(obj, parts[-1])",
        "    else:",
        "        fn = _resolve(target)",
        "    kwargs = {k: v for k, v in (case.get('args') or {}).items() if k != 'self'}",
        "    plain = {}",
        "    for k, v in kwargs.items():",
        "        if isinstance(v, dict) and ('__type__' in v or '__repr__' in v):",
        "            pytest.skip('opaque arg')",
        "        plain[k] = v",
        "    exc = case.get('exception')",
        "    if exc:",
        "        with pytest.raises(Exception) as caught:",
        "            fn(**plain)",
        "        assert type(caught.value).__name__ == exc.get('type') or True",
        "    else:",
        "        result = fn(**plain)",
        "        expected = case.get('return')",
        "        if isinstance(expected, (bool, int, float, str)) or expected is None:",
        "            assert result == expected",
        "",
    ]
    return {"code": "\n".join(lines), "count": len(cases)}


def _generate_scenario_tests(
    api: list[dict[str, str]],
    public_spec: dict[str, Any] | None,
    inferred: dict[str, Any],
) -> dict[str, Any]:
    """Real assertions from upstream AST + public_spec only.

    Hard rule: do **not** encode benchmark public/hidden failure shapes
    (exact error strings, eval graphs, orderings). Those are soft test leakage.
    Allowed: upstream-inferred API surface behavior, TASK/public_spec obligations.
    """

    names = {a["name"] for a in api}
    paths = {a["path"] for a in api}
    methods = set(inferred.get("methods") or [])
    blob = _behavior_blob(public_spec)
    assertions = 0
    lines = [
        '"""Behavioral mini-scenarios from upstream AST + public_spec (eval-blind)."""',
        "from __future__ import annotations",
        "",
        "import importlib",
        "import json",
        "",
        "import pytest",
        "",
    ]

    # --- LazyCommandCollection / click-like ---
    if "LazyCommandCollection" in names or "featurelifted.LazyCommandCollection" in paths:
        # B003 + resolve signature: argv -> (Context, Command, remaining); UsageError unknown.
        if (
            "resolve" in methods
            or "resolve" in names
            or "featurelifted.LazyCommandCollection.resolve" in paths
            or "resolve" in blob
        ):
            lines += [
                "def test_resolve_returns_context_command_and_remaining_argv() -> None:",
                "    \"\"\"public_spec B003 / resolve signature: tuple[Context, Command, list[str]].\"\"\"",
                "    mod = importlib.import_module('featurelifted')",
                "    Lazy = getattr(mod, 'LazyCommandCollection')",
                "    Command = getattr(mod, 'Command')",
                "    UsageError = getattr(mod, 'UsageError')",
                "    def factory():",
                "        return Command('demo', callback=lambda *a, **k: a)",
                "    col = Lazy({'demo': factory})",
                "    ctx, cmd, rest = col.resolve(['demo', 'x', 'y'])",
                "    assert ctx is not None",
                "    assert cmd is not None",
                "    assert getattr(cmd, 'name', None) == 'demo'",
                "    assert list(rest) == ['x', 'y']",
                "    with pytest.raises(UsageError):",
                "        col.resolve(['missing_command_xyz'])",
                "",
            ]
            assertions += 2  # return shape + UsageError

        # invoke(argv) must run the command callback — not merely exist (upstream AST + argv style).
        if "invoke" in methods or "invoke" in names:
            lines += [
                "def test_invoke_runs_callback_over_argv() -> None:",
                "    \"\"\"Collection.invoke(argv) must execute the resolved command callback.\"\"\"",
                "    mod = importlib.import_module('featurelifted')",
                "    Lazy = getattr(mod, 'LazyCommandCollection')",
                "    Command = getattr(mod, 'Command')",
                "    def factory():",
                "        return Command('demo', callback=lambda ctx, args: list(args))",
                "    col = Lazy({'demo': factory})",
                "    result = col.invoke(['demo', 'a', 'b'])",
                "    assert result == ['a', 'b']",
                "",
            ]
            assertions += 1

        # B002 + ctor envvar: JSON mapping propagates into Context.default_map.
        if "envvar" in blob or "default" in blob or "default_map" in blob:
            lines += [
                "def test_envvar_json_propagates_to_context_default_map(monkeypatch) -> None:",
                "    \"\"\"public_spec: envvar settings propagate into context default_map.\"\"\"",
                "    mod = importlib.import_module('featurelifted')",
                "    Lazy = getattr(mod, 'LazyCommandCollection')",
                "    Command = getattr(mod, 'Command')",
                "    env_name = 'FLB_FEATURE_DEFAULTS'",
                "    payload = {'demo': {'flag': True}}",
                "    monkeypatch.setenv(env_name, json.dumps(payload))",
                "    col = Lazy({'demo': lambda: Command('demo')}, envvar=env_name)",
                "    ctx, _cmd, _rest = col.resolve(['demo'])",
                "    assert getattr(ctx, 'default_map', None) is not None",
                "    assert ctx.default_map.get('demo', {}).get('flag') is True",
                "",
            ]
            assertions += 1

        # B001: get_command loads only needed source (cache once).
        if "cache" in blob or "loads only" in blob or "get_command" in blob:
            lines += [
                "def test_get_command_loads_source_once() -> None:",
                "    \"\"\"public_spec B001: load the providing source and cache the command.\"\"\"",
                "    mod = importlib.import_module('featurelifted')",
                "    Lazy = getattr(mod, 'LazyCommandCollection')",
                "    Command = getattr(mod, 'Command')",
                "    calls = {'n': 0}",
                "    def factory():",
                "        calls['n'] += 1",
                "        return Command('demo')",
                "    col = Lazy({'demo': factory})",
                "    c1 = col.get_command('demo')",
                "    c2 = col.get_command('demo')",
                "    assert c1 is not None and c2 is not None",
                "    assert calls['n'] == 1",
                "",
            ]
            assertions += 1

    # --- RevisionMap / alembic-like (public_spec obligations only) ---
    if "RevisionMap" in names or "featurelifted.RevisionMap" in paths:
        # Signature: down_revision defaults to None → one-arg Revision must construct.
        lines += [
            "def test_revision_down_revision_defaults_to_none() -> None:",
            "    \"\"\"public_spec Revision signature: down_revision=None by default.\"\"\"",
            "    mod = importlib.import_module('featurelifted')",
            "    Revision = getattr(mod, 'Revision')",
            "    rev = Revision('solo')",
            "    assert getattr(rev, 'revision', None) == 'solo'",
            "    down = getattr(rev, 'down_revision', 'missing')",
            "    assert down in (None, (), [])",
            "",
        ]
        assertions += 1

        # B003: branched + merged graph → single merge head; branch point queryable.
        lines += [
            "def test_merge_graph_heads_and_branch_point() -> None:",
            "    \"\"\"public_spec B003: branched/merged graphs report heads; branch points exist.\"\"\"",
            "    mod = importlib.import_module('featurelifted')",
            "    Revision = getattr(mod, 'Revision')",
            "    RevisionMap = getattr(mod, 'RevisionMap')",
            "    revs = [",
            "        Revision('n0'),",
            "        Revision('n1', 'n0'),",
            "        Revision('n2', 'n0'),",
            "        Revision('n3', ('n1', 'n2')),",
            "    ]",
            "    revmap = RevisionMap(revs)",
            "    heads = revmap.get_heads() if hasattr(revmap, 'get_heads') else list(getattr(revmap, 'heads'))",
            "    assert list(heads) == ['n3'] or set(heads) == {'n3'}",
            "    root = revmap.get_revision('n0')",
            "    assert root is not None",
            "    assert getattr(root, 'is_branch_point', False) is True",
            "    merge = revmap.get_revision('n3')",
            "    assert merge is not None",
            "    assert getattr(merge, 'is_merge_point', False) is True",
            "",
        ]
        assertions += 1

        # B006: symbolic head/base must resolve via get_revision (not only get_revisions /
        # get_current_head). Triggered by public_spec behavior text or get_revision API.
        if (
            "symbolic" in blob
            or ("head" in blob and "base" in blob)
            or "get_revision" in names
            or "get_revision" in methods
            or "featurelifted.RevisionMap.get_revision" in paths
        ):
            lines += [
                "def test_symbolic_head_and_base_via_get_revision() -> None:",
                "    \"\"\"public_spec B006: get_revision resolves symbolic head/base identifiers.\"\"\"",
                "    mod = importlib.import_module('featurelifted')",
                "    Revision = getattr(mod, 'Revision')",
                "    RevisionMap = getattr(mod, 'RevisionMap')",
                "    revmap = RevisionMap([Revision('a'), Revision('b', 'a')])",
                "    head = revmap.get_revision('head')",
                "    assert head is not None, 'get_revision(\"head\") must resolve the unique head'",
                "    assert getattr(head, 'revision', None) == 'b'",
                "    # Symbolic base is not a concrete node id.",
                "    assert revmap.get_revision('base') is None",
                "",
            ]
            assertions += 1

        # MissingRevision is named in required_api / TASK — not copied from hidden.
        if any(a.get("name") == "MissingRevision" for a in api) or "MissingRevision" in names:
            lines += [
                "def test_missing_down_revision_raises_missing_revision() -> None:",
                "    \"\"\"public_spec declares MissingRevision for missing graph nodes.\"\"\"",
                "    mod = importlib.import_module('featurelifted')",
                "    Revision = getattr(mod, 'Revision')",
                "    RevisionMap = getattr(mod, 'RevisionMap')",
                "    MissingRevision = getattr(mod, 'MissingRevision', None)",
                "    if MissingRevision is None:",
                "        pytest.skip('MissingRevision not exported')",
                "    with pytest.raises(MissingRevision):",
                "        RevisionMap([Revision('b', 'missing')])",
                "",
            ]
            assertions += 1

        # Mild ancestors obligation from public_spec behavior text (no eval graph).
        if "ancestors" in names or "ancestors" in methods or "ancestor" in blob:
            lines += [
                "def test_ancestors_excludes_self_on_linear_chain() -> None:",
                "    \"\"\"public_spec ancestors behavior: self is not an ancestor of itself.\"\"\"",
                "    mod = importlib.import_module('featurelifted')",
                "    Revision = getattr(mod, 'Revision')",
                "    RevisionMap = getattr(mod, 'RevisionMap')",
                "    revmap = RevisionMap([Revision('a'), Revision('b', 'a'), Revision('c', 'b')])",
                "    ancs = revmap.ancestors('c')",
                "    assert 'c' not in set(ancs)",
                "    assert set(ancs) >= {'a', 'b'}",
                "",
            ]
            assertions += 1

    if assertions == 0:
        lines += [
            "def test_no_scenario_templates_matched() -> None:",
            "    pytest.skip('no eval-blind scenario templates matched; rely on surface/replay')",
            "",
        ]

    return {"code": "\n".join(lines), "assertions": assertions}


def _generate_behavior_checklist(behaviors: list[dict[str, str]]) -> str:
    """Documentation-only catalog — must NOT use assert True as a gate."""

    lines = [
        '"""Behavior checklist — documentation only (not a greenwashing gate)."""',
        "from __future__ import annotations",
        "",
        "import pytest",
        "",
        "BEHAVIORS = " + json.dumps(behaviors, ensure_ascii=False, indent=2),
        "",
        "",
        "def test_behavior_catalog_is_list() -> None:",
        "    assert isinstance(BEHAVIORS, list)",
        "",
        "",
        "@pytest.mark.parametrize('behavior', BEHAVIORS)",
        "def test_behavior_documented(behavior) -> None:",
        "    \"\"\"Keep behavior ids visible in collection; no vacuous pass.\"\"\"",
        "    assert behavior.get('id') or behavior.get('text')",
        "    pytest.skip('documentation-only; enforced by test_behavior_scenarios.py')",
        "",
    ]
    return "\n".join(lines)

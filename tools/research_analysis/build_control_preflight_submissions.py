#!/usr/bin/env python3
"""Build reproducible v1.1 control submissions for the two-task feasibility preflight."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SUBMISSIONS = REPO_ROOT / "benchmark/submissions"

BOLTONS_INIT = '''"""Independent compact implementation of the public iterutils contract."""

from .iterutils import backoff, bucketize, chunk_ranges, chunked, get_path, pairwise
from .iterutils import partition, remap, unique, windowed

__all__ = [
    "backoff", "bucketize", "chunk_ranges", "chunked", "get_path", "pairwise",
    "partition", "remap", "unique", "windowed",
]
'''

BOLTONS_CORE = '''"""Small, independently structured iterator helpers for the accepted alternative."""

from __future__ import annotations

import itertools
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from typing import Any, Callable

_MISSING = object()


def chunked(src: Iterable[Any], size: int, count: int | None = None, **kwargs: Any) -> list[list[Any]]:
    if not isinstance(size, int) or size <= 0:
        raise ValueError("expected a positive integer chunk size")
    fill = kwargs.pop("fill", _MISSING)
    if kwargs:
        raise TypeError(f"unexpected options: {', '.join(sorted(kwargs))}")
    iterator = iter(src)
    output: list[list[Any]] = []
    while count is None or len(output) < count:
        group = list(itertools.islice(iterator, size))
        if not group:
            break
        if fill is not _MISSING and len(group) < size:
            group.extend([fill] * (size - len(group)))
        output.append(group)
    return output


def windowed(src: Iterable[Any], size: int) -> list[tuple[Any, ...]]:
    if not isinstance(size, int) or size <= 0:
        raise ValueError("expected a positive integer window size")
    values = list(src)
    return [tuple(values[index:index + size]) for index in range(max(0, len(values) - size + 1))]


def pairwise(src: Iterable[Any]) -> list[tuple[Any, Any]]:
    return [tuple(value) for value in windowed(src, 2)]


def unique(src: Iterable[Any], key: Callable[[Any], Any] | None = None) -> list[Any]:
    seen: set[Any] = set()
    result: list[Any] = []
    for value in src:
        marker = key(value) if key else value
        if marker in seen:
            continue
        seen.add(marker)
        result.append(value)
    return result


def bucketize(
    src: Iterable[Any],
    key: Callable[[Any], Any] = bool,
    value_transform: Callable[[Any], Any] | None = None,
    key_filter: Callable[[Any], bool] | None = None,
) -> dict[Any, list[Any]]:
    result: defaultdict[Any, list[Any]] = defaultdict(list)
    for value in src:
        bucket = key(value)
        if key_filter is not None and not key_filter(bucket):
            continue
        result[bucket].append(value_transform(value) if value_transform else value)
    return dict(result)


def partition(src: Iterable[Any], key: Callable[[Any], Any] = bool) -> tuple[list[Any], list[Any]]:
    truthy: list[Any] = []
    falsy: list[Any] = []
    for value in src:
        (truthy if key(value) else falsy).append(value)
    return truthy, falsy


def get_path(root: Any, path: Sequence[Any] | str, default: Any = _MISSING) -> Any:
    parts = path.split(".") if isinstance(path, str) else path
    current = root
    try:
        for part in parts:
            current = current[int(part)] if isinstance(current, Sequence) and not isinstance(current, (str, bytes)) else current[part]
    except (IndexError, KeyError, TypeError, ValueError):
        if default is _MISSING:
            raise KeyError(path)
        return default
    return current


def remap(
    root: Any,
    visit: Callable[[tuple[Any, ...], Any, Any], Any] | None = None,
    enter: Callable[..., Any] | None = None,
    exit: Callable[..., Any] | None = None,
    **_: Any,
) -> Any:
    def walk(value: Any, path: tuple[Any, ...]) -> Any:
        if isinstance(value, Mapping):
            output: dict[Any, Any] = {}
            for key, child in value.items():
                mapped = walk(child, path + (key,))
                decision = visit(path, key, mapped) if visit else True
                if decision is False:
                    continue
                if isinstance(decision, tuple) and len(decision) == 2:
                    out_key, mapped = decision
                else:
                    out_key = key
                output[out_key] = mapped
            return output
        if isinstance(value, list):
            output = []
            for index, child in enumerate(value):
                mapped = walk(child, path + (index,))
                decision = visit(path, index, mapped) if visit else True
                if decision is not False:
                    output.append(decision[1] if isinstance(decision, tuple) and len(decision) == 2 else mapped)
            return output
        return value
    return walk(root, ())


def chunk_ranges(
    input_size: int,
    chunk_size: int,
    input_offset: int = 0,
    overlap_size: int = 0,
    align: bool = False,
):
    if chunk_size <= 0 or overlap_size < 0 or overlap_size >= chunk_size:
        raise ValueError("invalid chunk or overlap size")
    step = chunk_size - overlap_size
    start = input_offset
    end_limit = input_offset + input_size
    while start < end_limit:
        end = min(start + chunk_size, end_limit)
        yield start, end
        if end >= end_limit:
            break
        start += step


def backoff(start: float, stop: float, count: int | None = None, factor: float = 2.0, jitter: bool = False):
    result: list[float] = []
    current = float(start)
    while current < stop and (count is None or len(result) < count):
        result.append(current)
        current *= factor
    return result
'''

PLUGGY_INIT = '''"""Independent compact hook specification implementation."""

from .core import HookimplMarker, HookspecMarker, PluginManager, PluginValidationError

__all__ = ["HookimplMarker", "HookspecMarker", "PluginManager", "PluginValidationError"]
'''

PLUGGY_ALTERNATIVE = '''"""Minimal independent hook registry preserving the task contract."""

from __future__ import annotations

import inspect
from types import SimpleNamespace
from typing import Any, Callable


class PluginValidationError(Exception):
    pass


class _Marker:
    suffix = ""

    def __init__(self, project_name: str):
        self.project_name = project_name

    def __call__(self, function: Callable[..., Any] | None = None, **options: Any):
        def decorate(target: Callable[..., Any]):
            setattr(target, f"{self.project_name}_{self.suffix}", dict(options))
            return target
        return decorate(function) if function is not None else decorate


class HookspecMarker(_Marker):
    suffix = "spec"


class HookimplMarker(_Marker):
    suffix = "impl"


def _arguments(function: Callable[..., Any]) -> set[str]:
    return {
        name for name, parameter in inspect.signature(function).parameters.items()
        if name not in {"self", "cls"}
        and parameter.kind in {parameter.POSITIONAL_ONLY, parameter.POSITIONAL_OR_KEYWORD, parameter.KEYWORD_ONLY}
    }


class _HookCaller:
    def __init__(self, name: str, spec: Callable[..., Any], options: dict[str, Any]):
        self.name = name
        self.spec = spec
        self.options = options
        self.implementations: list[Callable[..., Any]] = []
        self.history: list[tuple[Callable[[Any], None] | None, dict[str, Any]]] = []

    def add(self, implementation: Callable[..., Any]) -> None:
        self.implementations.append(implementation)
        for callback, kwargs in self.history:
            result = implementation(**kwargs)
            if callback is not None:
                callback(result)

    def call_historic(self, result_callback=None, kwargs=None) -> None:
        if not self.options.get("historic"):
            raise AssertionError("cannot call_historic on a non-historic hook")
        values = dict(kwargs or {})
        self.history.append((result_callback, values))
        for implementation in self.implementations:
            result = implementation(**values)
            if result_callback is not None:
                result_callback(result)

    def __call__(self, **kwargs: Any):
        results = [implementation(**kwargs) for implementation in reversed(self.implementations)]
        return results[0] if self.options.get("firstresult") and results else results


class PluginManager:
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.hook = SimpleNamespace()
        self._hooks: dict[str, _HookCaller] = {}
        self._pending: list[tuple[str, bool]] = []

    def add_hookspecs(self, namespace: Any) -> None:
        marker = f"{self.project_name}_spec"
        found = False
        for name in dir(namespace):
            target = getattr(namespace, name)
            options = getattr(target, marker, None)
            if options is None:
                continue
            found = True
            caller = _HookCaller(name, target, options)
            self._hooks[name] = caller
            setattr(self.hook, name, caller)
        if not found:
            raise ValueError("did not find any hook specifications")

    def register(self, plugin: Any, name: str | None = None):
        marker = f"{self.project_name}_impl"
        for method_name in dir(plugin):
            implementation = getattr(plugin, method_name)
            options = getattr(implementation, marker, None)
            if options is None:
                continue
            caller = self._hooks.get(method_name)
            if caller is None:
                self._pending.append((method_name, bool(options.get("optionalhook"))))
                continue
            unknown = _arguments(implementation) - _arguments(caller.spec)
            if unknown:
                raise PluginValidationError(
                    f"Plugin {plugin!r} for hook {method_name!r} has unknown argument(s): {sorted(unknown)}"
                )
            if options.get("hookwrapper") and not inspect.isgeneratorfunction(implementation):
                raise PluginValidationError("hookwrapper must be a generator function")
            if options.get("hookwrapper") and caller.options.get("historic"):
                raise PluginValidationError("historic incompatible with hookwrapper")
            caller.add(implementation)
        return name or getattr(plugin, "__name__", plugin.__class__.__name__)

    def check_pending(self) -> None:
        pending = [name for name, optional in self._pending if not optional]
        if pending:
            raise PluginValidationError(f"unknown hook(s): {', '.join(sorted(pending))}")
'''

PLUGGY_NARROW = '''"""Public-only negative control; intentionally omits historic and wrapper contracts."""

from __future__ import annotations

import inspect
from types import SimpleNamespace


class PluginValidationError(Exception):
    pass


class _Marker:
    suffix = ""
    def __init__(self, project_name): self.project_name = project_name
    def __call__(self, function=None, **options):
        def decorate(target):
            setattr(target, f"{self.project_name}_{self.suffix}", options)
            return target
        return decorate(function) if function is not None else decorate


class HookspecMarker(_Marker): suffix = "spec"
class HookimplMarker(_Marker): suffix = "impl"


class PluginManager:
    def __init__(self, project_name):
        self.project_name = project_name
        self.hook = SimpleNamespace()
        self.specs = {}
        self.pending = []

    def add_hookspecs(self, namespace):
        for name in dir(namespace):
            value = getattr(namespace, name)
            if hasattr(value, f"{self.project_name}_spec"):
                self.specs[name] = value

    def register(self, plugin, name=None):
        for method_name in dir(plugin):
            impl = getattr(plugin, method_name)
            options = getattr(impl, f"{self.project_name}_impl", None)
            if options is None:
                continue
            spec = self.specs.get(method_name)
            if spec is None:
                self.pending.append((method_name, options.get("optionalhook", False)))
                continue
            spec_args = set(inspect.signature(spec).parameters) - {"self"}
            impl_args = set(inspect.signature(impl).parameters) - {"self"}
            if impl_args - spec_args:
                raise PluginValidationError("unknown hook argument")
        return name or plugin.__class__.__name__

    def check_pending(self):
        if any(not optional for _, optional in self.pending):
            raise PluginValidationError("unknown hook")
'''


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def reset(path: Path, force: bool) -> None:
    if path.exists():
        if not force:
            raise FileExistsError(f"control already exists: {path}; use --force")
        shutil.rmtree(path)
    path.mkdir(parents=True)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def provenance(task_id: str, variant: str, source_files: list[str], notes: str) -> dict:
    return {
        "schema_version": "featureliftbench.provenance.v1",
        "task_id": task_id,
        "variant": variant,
        "included_source_files": source_files,
        "included_source_symbols": [],
        "replaced_dependencies": [],
        "adapters": [],
        "notes": notes,
        "review_status": "author_generated_control",
    }


def build_boltons(force: bool) -> None:
    task_id = "boltons__iterutils_core__001"
    base = SUBMISSIONS / task_id
    alternative = base / "alternative_v11"
    reset(alternative, force)
    write(alternative / "featurelifted/__init__.py", BOLTONS_INIT)
    write(alternative / "featurelifted/iterutils.py", BOLTONS_CORE)
    write(alternative / "featurelift_provenance.json", json.dumps(provenance(
        task_id, "acceptable_alternative", [], "Independent implementation from the public contract."
    ), indent=2))
    for source_name, target_name, variant, notes in (
        ("copy_all", "copy_heavy_v11", "copy_heavy", "Existing full-repository copy control."),
        ("naive", "narrow_v11", "narrow_negative", "Existing shallow public-oriented control."),
    ):
        target = base / target_name
        reset(target, force)
        shutil.copytree(base / source_name / "featurelifted", target / "featurelifted")
        source_files = (
            sorted(f"repo/boltons/{path.name}" for path in (base / source_name / "featurelifted").glob("*.py"))
            if variant == "copy_heavy" else ["repo/boltons/iterutils.py"]
        )
        write(target / "featurelift_provenance.json", json.dumps(provenance(
            task_id, variant, source_files, notes
        ), indent=2))


def build_pluggy(force: bool) -> None:
    task_id = "pluggy__hook_specs_core__001"
    base = SUBMISSIONS / task_id
    alternative = base / "alternative_v11"
    reset(alternative, force)
    write(alternative / "featurelifted/__init__.py", PLUGGY_INIT)
    write(alternative / "featurelifted/core.py", PLUGGY_ALTERNATIVE)
    write(alternative / "featurelift_provenance.json", json.dumps(provenance(
        task_id, "acceptable_alternative", [], "Independent compact hook registry implementation."
    ), indent=2))
    narrow = base / "narrow_v11"
    reset(narrow, force)
    write(narrow / "featurelifted/__init__.py", PLUGGY_INIT)
    write(narrow / "featurelifted/core.py", PLUGGY_NARROW)
    write(narrow / "featurelift_provenance.json", json.dumps(provenance(
        task_id, "narrow_negative", [], "Implements public checks but omits historic/wrapper behavior."
    ), indent=2))
    copy_heavy = base / "copy_heavy_v11"
    reset(copy_heavy, force)
    shutil.copytree(base / "oracle" / "featurelifted", copy_heavy / "featurelifted")
    redundant = copy_heavy / "featurelifted/_redundant_snapshot"
    shutil.copytree(base / "oracle" / "featurelifted", redundant)
    write(redundant / "README_CONTROL.txt", "Intentional duplicate source snapshot for copy-heavy metric validation.\n")
    source_files = [
        "repo/pluggy/__init__.py", "repo/pluggy/_callers.py", "repo/pluggy/_hooks.py",
        "repo/pluggy/_manager.py", "repo/pluggy/_result.py", "repo/pluggy/_tracing.py",
        "repo/pluggy/_version.py",
    ]
    write(copy_heavy / "featurelift_provenance.json", json.dumps(provenance(
        task_id, "copy_heavy", source_files, "Oracle package plus an intentional redundant snapshot."
    ), indent=2))


def main() -> int:
    args = parse_args()
    build_boltons(args.force)
    build_pluggy(args.force)
    print("built 2 tasks x 3 v1.1 control variants")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

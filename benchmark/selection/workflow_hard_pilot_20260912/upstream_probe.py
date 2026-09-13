"""Run authored scenarios against pinned upstream code, not lifted references."""
from __future__ import annotations

from contextvars import ContextVar
from copy import deepcopy
import importlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TREES = ROOT / "benchmark/sources/workflow_hard_pilot/trees"
from cases import CASES


def verify_origin(module, source):
    if not Path(module.__file__).resolve().is_relative_to((TREES / source).resolve()):
        raise RuntimeError(f"Wrong upstream origin: {module.__file__}")


def get_runner(source):
    adapter = (HERE / "adapters" / ("dbt.py" if source == "dbt-core" else source + ".py")).read_text()
    namespace = {"__name__": "upstream_task_adapter"}
    if source == "pip":
        sys.path.insert(0, str(TREES / "pip/src"))
        from pip._internal.index import package_finder as finder
        from pip._internal.models.link import Link
        from pip._internal.utils.hashes import Hashes
        from pip._vendor.packaging.specifiers import SpecifierSet
        from pip._vendor.packaging.tags import Tag
        verify_origin(finder, source)
        class ExplicitTarget:
            def __init__(self, version_info, tags):
                self.py_version_info = tuple(version_info)
                self.py_version = ".".join(map(str, version_info[:2]))
                self.tags = tags
            def get_unsorted_tags(self): return set(self.tags)
        engine = SimpleNamespace(**{name: getattr(finder, name) for name in ["canonicalize_name", "LinkEvaluator", "LinkType", "InstallationCandidate", "CandidateEvaluator"]}, TargetPython=ExplicitTarget, Link=Link, Hashes=Hashes)
        adapter = adapter.replace("from . import _engine as e", "")
        adapter = adapter.replace("from packaging.specifiers import SpecifierSet", "").replace("from packaging.tags import Tag", "")
        namespace.update(e=engine, SpecifierSet=SpecifierSet, Tag=Tag)
        api = "choose_distribution"
        error_types = (ValueError,)
    elif source == "dbt-core":
        sys.path.insert(0, str(TREES / "dbt-core/core"))
        import dbt.graph.cli as cli
        import dbt.graph.selector_spec as spec
        import dbt.graph.selector as selector
        import dbt.graph.selector_methods as methods
        from dbt.graph.graph import Graph
        from dbt_common.exceptions import DbtRuntimeError
        verify_origin(selector, source)
        mode = ContextVar("probe_selection_mode", default="eager")
        cli.get_flags = spec.get_flags = lambda: SimpleNamespace(INDIRECT_SELECTION=mode.get())
        engine = SimpleNamespace(NodeSelector=selector.NodeSelector, Graph=Graph, MethodName=methods.MethodName, is_selected_node=methods.is_selected_node, _mode=mode, parse_union=cli.parse_union, IndirectSelection=spec.IndirectSelection, SelectionDifference=spec.SelectionDifference)
        adapter = adapter.replace("from . import _engine as e", "")
        namespace["e"] = engine
        api = "select_nodes"
        error_types = (ValueError, DbtRuntimeError)
    else:
        sys.path.insert(0, str(TREES / "sqlglot"))
        module = importlib.import_module("sqlglot.lineage")
        verify_origin(module, source)
        adapter = adapter.replace("from ._sqlglot.lineage", "from sqlglot.lineage").replace("from ._sqlglot.errors", "from sqlglot.errors")
        api = "trace_column"
        error_types = (ValueError,)
    exec(compile(adapter, str(HERE / "adapters" / source), "exec"), namespace)
    return namespace[api], error_types


def probe(source):
    run, error_types = get_runner(source)
    results = []
    for scenario in CASES[source]():
        before = deepcopy(scenario["args"])
        try:
            expected = run(**deepcopy(before))
        except error_types as exc:
            if not scenario["error"]:
                raise RuntimeError(f"Unexpected upstream failure in {source}/{scenario['name']}") from exc
            expected = {"raises": "ValueError"}
        else:
            if scenario["error"]:
                raise RuntimeError(f"Expected upstream rejection did not occur: {scenario['name']}")
        results.append({**scenario, "expected": expected})
    output = HERE / "fixtures" / (source + ".json")
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(dict(source=source, cases=len(results), output=str(output))))


if __name__ == "__main__":
    probe(sys.argv[1])

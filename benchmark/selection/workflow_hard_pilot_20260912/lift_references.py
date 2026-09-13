"""Deterministic maintainer extraction. Source-location data never enters TASK."""
from __future__ import annotations

import ast
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
TREES = ROOT / "benchmark/sources/workflow_hard_pilot/trees"


def text(source, path):
    return (TREES / source / path).read_text(encoding="utf-8")


def extract(source, path, names, *, members=None, replacements=()):
    content = text(source, path)
    module = ast.parse(content)
    out = []
    found = set()
    for node in module.body:
        name = getattr(node, "name", None)
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
        if name not in names:
            continue
        found.add(name)
        if members and name in members:
            node.body = [n for n in node.body if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) or n.name in members[name]]
        out.append(ast.unparse(node))
    if found != set(names):
        raise ValueError(f"Missing nodes from {path}: {set(names) - found}")
    result = "\n\n".join(out) + "\n"
    for before, after in replacements:
        if before not in result:
            raise ValueError(f"Missing adaptation target {before!r}")
        result = result.replace(before, after)
    return result


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_pip(dest):
    base = "src/pip/_internal/"
    code = '''from __future__ import annotations
import enum, functools, itertools, logging, os, posixpath, re, urllib.parse, warnings
from dataclasses import dataclass
from typing import *
from collections.abc import Mapping
from packaging import specifiers, version
from packaging.version import Version, InvalidVersion, parse as parse_version
from packaging.tags import Tag
from packaging.utils import canonicalize_name, parse_wheel_filename, BuildTag
from packaging.utils import InvalidWheelFilename as _PackagingInvalidWheelFilename
class InvalidWheelFilename(ValueError): pass
class UnsupportedWheel(ValueError): pass
logger = logging.getLogger(__name__)
# Diagnostic verbosity and deprecation warnings are excluded from the task API.
logger.verbose = logger.debug
def deprecated(**kwargs):
    warnings.warn(kwargs["reason"], DeprecationWarning)
WHEEL_EXTENSION = ".whl"
SUPPORTED_EXTENSIONS = (".zip", ".whl", ".tar.bz2", ".tbz", ".tar.gz", ".tgz", ".tar", ".tar.xz", ".txz", ".tlz", ".tar.lz", ".tar.lzma")
class TargetPython:
    def __init__(self, version_info, tags):
        self.py_version_info = tuple(version_info)
        self.py_version = ".".join(map(str, version_info[:2]))
        self._tags = tags
    def get_unsorted_tags(self): return set(self._tags)
    def get_sorted_tags(self): return list(self._tags)
'''
    code += extract("pip", base + "utils/misc.py", ["splitext"])
    code += extract("pip", base + "utils/packaging.py", ["check_requires_python"])
    code += extract("pip", base + "utils/hashes.py", ["Hashes"], members={"Hashes": {"__init__", "__bool__", "digest_count", "is_hash_allowed"}})
    code += extract("pip", base + "models/link.py", ["_SUPPORTED_HASHES", "LinkHash"])
    # The input boundary supplies ordinary HTTPS URLs with filenames and no auth,
    # UNC, egg or metadata-sidecar inputs; only the reachable Link surface is lifted.
    methods = {"__init__", "__str__", "__repr__", "__hash__", "__eq__", "__lt__", "url", "path", "filename", "splitext", "ext", "is_wheel", "is_yanked", "has_hash", "is_hash_allowed", "_egg_fragment", "redacted_url", "netloc"}
    code += extract("pip", base + "models/link.py", ["Link"], members={"Link": methods})
    code += '\ndef redact_auth_from_url(url): return url\ndef split_auth_from_netloc(netloc): return netloc, (None, None)\n'
    code += extract("pip", base + "models/wheel.py", ["Wheel"])
    code += extract("pip", base + "models/candidate.py", ["InstallationCandidate"])
    code += extract("pip", base + "index/package_finder.py", ["_check_link_requires_python", "LinkType", "LinkEvaluator", "filter_unallowed_hashes", "BestCandidateResult", "CandidateEvaluator", "_find_name_version_sep", "_extract_version_from_fragment"])
    write(dest / "_engine.py", code)
    shutil.copyfile(HERE / "adapters/pip.py", dest / "__init__.py")


def build_dbt(dest):
    base = "core/dbt/graph/"
    code = '''from __future__ import annotations
import os, re, itertools
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import *
from types import SimpleNamespace
from enum import StrEnum
from contextvars import ContextVar
from functools import partial
from itertools import product
from fnmatch import fnmatch
import networkx as nx
class SelectionError(ValueError): pass
DbtRuntimeError = InvalidSelectorError = DbtInternalError = SelectionError
class dbtClassMixin: pass
UniqueId = str
class NodeType:
    Test = "test"
    Unit = "unit_test"
_mode = ContextVar("indirect_selection", default="eager")
def get_flags(): return SimpleNamespace(INDIRECT_SELECTION=_mode.get())
def fire_event(event): pass
def warn_or_error(event): pass
def NoNodesForSelectionCriteria(**kwargs): return kwargs
def SelectorReportInvalidSelector(**kwargs): return kwargs
'''
    code += extract("dbt-core", base + "graph.py", ["Graph"])
    code += extract("dbt-core", base + "selector_methods.py", ["MethodName", "is_selected_node"])
    code += extract("dbt-core", base + "selector_spec.py", ["RAW_SELECTOR_PATTERN", "SELECTOR_METHOD_SEPARATOR", "IndirectSelection", "_probably_path", "_match_to_int", "SelectionSpec", "SelectionCriteria", "BaseSelectionGroup", "SelectionIntersection", "SelectionDifference", "SelectionUnion"])
    code += extract("dbt-core", base + "cli.py", ["INTERSECTION_DELIMITER", "parse_union"])
    methods = {"select_included", "get_nodes_from_criteria", "collect_specified_neighbors", "select_nodes_recursively", "select_nodes", "expand_selection", "incorporate_indirect_nodes"}
    code += extract("dbt-core", base + "selector.py", ["can_select_indirectly", "NodeSelector"], members={"NodeSelector": methods}, replacements=[("class NodeSelector(MethodManager):", "class NodeSelector:")])
    write(dest / "_engine.py", code)
    shutil.copyfile(HERE / "adapters/dbt.py", dest / "__init__.py")


def build_sqlglot(dest):
    # A conservative full-package baseline; explicitly NOT a minimal closure claim.
    for path in sorted((TREES / "sqlglot/sqlglot").rglob("*")):
        if path.is_file() and path.suffix == ".py":
            relative = path.relative_to(TREES / "sqlglot/sqlglot")
            content = path.read_text(encoding="utf-8")
            content = re_namespace(content)
            write(dest / "_sqlglot" / relative, content)
    shutil.copyfile(HERE / "adapters/sqlglot.py", dest / "__init__.py")


def re_namespace(content):
    import re
    # The public contract explicitly selects the upstream pure-Python path.
    content = re.sub(r"try:\n    from sqlglotrs import.*?except ImportError:\n    USE_RS_TOKENIZER = False", "USE_RS_TOKENIZER = False", content, flags=re.DOTALL)
    # Rewrite absolute imports and dynamic module names, including root imports.
    content = re.sub(r"\bfrom sqlglot(?=[ .])", "from featurelifted._sqlglot", content)
    content = re.sub(r"\bimport sqlglot\.([\w.]+) as (\w+)", r"import featurelifted._sqlglot.\1 as \2", content)
    content = re.sub(r"\bimport sqlglot(?=[ \n])", "import featurelifted._sqlglot as sqlglot", content)
    content = content.replace('"sqlglot.', '"featurelifted._sqlglot.').replace("'sqlglot.", "'featurelifted._sqlglot.")
    return content

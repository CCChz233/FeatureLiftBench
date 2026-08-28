#!/usr/bin/env python3.12
"""Swap copy-heavy Hard-50 Flash passes for large-repo thin-oracle tasks."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from materialize_hard50_pilot_oracles import (  # noqa: E402
    PILOT,
    copy_repo,
    copy_rewritten,
    update_oracle_manifest,
    write_lock,
)

PIN = Path("/tmp/flb_hard50_swap_pins")
SWAPPED = PILOT / "_swapped_out"
LEDGER = ROOT / "benchmark/selection/hard50_expansion_20260827.json"
SUBMISSIONS = ROOT / "experiments/hard50_copyheavy_swaps_20260827/submissions"
NAIVE = '''\
"""Intentionally incomplete naive extraction."""

class _Missing:
    def __getattr__(self, name):
        raise NotImplementedError(name)

    def __call__(self, *args, **kwargs):
        raise NotImplementedError

def __getattr__(name):
    return _Missing()
'''


def py_loc(root: Path) -> int:
    total = 0
    for path in root.rglob("*.py"):
        if not path.is_file():
            continue
        total += sum(
            1
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
            if line.strip()
        )
    return total


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def move_old(task_id: str) -> None:
    src = PILOT / task_id
    if not src.exists():
        return
    SWAPPED.mkdir(parents=True, exist_ok=True)
    dest = SWAPPED / task_id
    if dest.exists():
        shutil.rmtree(dest)
    shutil.move(str(src), str(dest))


def common_hidden_api(names: str) -> str:
    return f'''import featurelifted


def test_required_api_surface() -> None:
{names}
'''


def common_no_upstream(pkg: str) -> str:
    return f'''from __future__ import annotations

import re
from pathlib import Path

import featurelifted


def test_no_upstream_import_surface() -> None:
    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from {pkg}|import {pkg})\\b", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8"))
'''


def thin_mimesis_oracle(dest: Path) -> None:
    keep_providers = {"__init__.py", "base.py", "person.py", "address.py"}
    providers = dest / "providers"
    for path in list(providers.iterdir()):
        if path.name not in keep_providers:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
    write_text(
        providers / "__init__.py",
        "from featurelifted.providers.address import Address\n"
        "from featurelifted.providers.base import BaseDataProvider, BaseProvider, ProviderRegistry\n"
        "from featurelifted.providers.person import Person\n"
        "\n"
        "__all__ = ['Address', 'BaseDataProvider', 'BaseProvider', 'Person', 'ProviderRegistry']\n",
    )
    write_text(
        dest / "__init__.py",
        "from featurelifted.exceptions import LocaleError\n"
        "from featurelifted.locales import Locale\n"
        "from featurelifted.providers import Address, Person\n"
        "\n"
        "__all__ = ['Address', 'Locale', 'LocaleError', 'Person']\n",
    )
    for name in ("builder", "plugins"):
        path = dest / name
        if path.exists():
            shutil.rmtree(path)
    for name in ("schema.py", "shortcuts.py", "keys.py", "entrypoints.py", "compat.py"):
        path = dest / name
        if path.exists():
            path.unlink()
    datasets = dest / "datasets"
    keep_top = {"__init__.py", "global", "en"}
    for path in list(datasets.iterdir()):
        if path.name not in keep_top:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
    en = datasets / "en"
    for path in list(en.iterdir()):
        if path.name not in {"person.json", "address.json"}:
            path.unlink()
    write_text(
        datasets / "__init__.py",
        "BLOOD_GROUPS = ('O+', 'A+', 'B+', 'AB+', 'O−', 'A−', 'B−', 'AB−')\n"
        "GENDER_SYMBOLS = ('♂', '♀', '⚲')\n"
        "GENDER_CODES = (0, 1, 2, 9)\n"
        "USERNAMES = ['ada', 'linus', 'grace']\n"
        "EMAIL_DOMAINS = ['@example.com', '@example.org']\n"
        "COUNTRY_CODES = {'a2': ['US', 'GB'], 'a3': ['USA', 'GBR'], 'numeric': ['840', '826']}\n"
        "SHORTENED_ADDRESS_FMT = ['st_num', 'st_name']\n"
        "CONTINENT_CODES = ['AF', 'NA', 'OC', 'AN', 'AS', 'EU', 'SA']\n"
        "CALLING_CODES = ['+1', '+44']\n"
        "IATA_CODES = ['JFK', 'LHR']\n"
        "ICAO_CODES = ['KJFK', 'EGLL']\n",
    )


def append_configfile_export(init_path: Path) -> None:
    text = init_path.read_text(encoding="utf-8")
    if "from .config import ConfigFile" not in text and "from .config import" not in text:
        text = text.rstrip() + "\n\nfrom .config import ConfigFile\n"
        if "__all__" in text and "ConfigFile" not in text:
            text = text.replace("__all__ = [", '__all__ = ["ConfigFile", ', 1)
        init_path.write_text(text, encoding="utf-8")


def build_true_copy_all(clone: Path, dest: Path, src_pkg: str) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    copy_rewritten(clone / src_pkg, dest, src_pkg)
    if src_pkg == "dulwich":
        append_configfile_export(dest / "__init__.py")


def write_submissions(task: Path, clone: Path, src_pkg: str) -> Path:
    oracle_src = task / "reference_solution" / "featurelifted"
    out = SUBMISSIONS / task.name
    oracle = out / "oracle" / "featurelifted"
    naive = out / "naive" / "featurelifted"
    copy_all = out / "copy_all" / "featurelifted"
    if oracle.exists():
        shutil.rmtree(oracle)
    shutil.copytree(oracle_src, oracle, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    if naive.exists():
        shutil.rmtree(naive.parent)
    naive.mkdir(parents=True)
    (naive / "__init__.py").write_text(NAIVE, encoding="utf-8")
    build_true_copy_all(clone, copy_all, src_pkg)
    return copy_all


def materialize_dulwich() -> Path:
    tid = "dulwich__config_parse_core__001"
    clone = PIN / "dulwich__config_parse_core__001"
    task = PILOT / tid
    if task.exists():
        shutil.rmtree(task)
    task.mkdir(parents=True)
    copy_repo(clone, task / "repo")
    dest = task / "reference_solution" / "featurelifted"
    dest.mkdir(parents=True)
    for name in ("config.py", "file.py", "_typing.py"):
        src = clone / "dulwich" / name
        write_text(dest / name, src.read_text(encoding="utf-8"))
    write_text(
        dest / "__init__.py",
        "from .config import ConfigFile\n\n__all__ = ['ConfigFile']\n",
    )
    write_lock(task, [])
    write_text(task / "evaluation" / "forbidden_imports.txt", "dulwich\n")
    write_text(
        task / "public_tests" / "test_public_api.py",
        '''from __future__ import annotations

from io import BytesIO

from featurelifted import ConfigFile


SAMPLE = b"""[core]
\\tfilemode = true
[remote "origin"]
\\turl = git@example.com:lift.git
"""


def test_core_filemode_from_file() -> None:
    cfg = ConfigFile.from_file(BytesIO(SAMPLE), expand_includes=False)
    assert cfg.get((b"core",), b"filemode") == b"true"


def test_subsection_remote_url() -> None:
    cfg = ConfigFile.from_file(BytesIO(SAMPLE), expand_includes=False)
    assert cfg.get((b"remote", b"origin"), b"url") == b"git@example.com:lift.git"
''',
    )
    write_text(
        task / "hidden_tests" / "test_hidden_behavior.py",
        common_no_upstream("dulwich")
        + '''

from io import BytesIO
from pathlib import Path

from featurelifted import ConfigFile


def test_boolean_and_missing_key() -> None:
    cfg = ConfigFile.from_file(
        BytesIO(b"[core]\\n\\tfilemode = true\\n"),
        expand_includes=False,
    )
    assert cfg.get_boolean((b"core",), b"filemode") is True
    try:
        cfg.get((b"core",), b"missing")
    except KeyError:
        return
    raise AssertionError("expected KeyError")


def test_from_path_reads_core_and_remote(tmp_path: Path) -> None:
    path = tmp_path / "config"
    path.write_bytes(
        b'[core]\\n\\tfilemode = true\\n[remote "origin"]\\n\\turl = git@example.com:lift.git\\n'
    )
    cfg = ConfigFile.from_path(path, expand_includes=False)
    assert cfg.get((b"core",), b"filemode") == b"true"
    assert cfg.get((b"remote", b"origin"), b"url") == b"git@example.com:lift.git"
''',
    )
    write_text(
        task / "hidden_tests" / "test_required_api_surface.py",
        common_hidden_api(
            "    assert callable(featurelifted.ConfigFile.from_file)\n"
            "    assert callable(featurelifted.ConfigFile.from_path)\n"
            "    assert callable(featurelifted.ConfigFile.get)\n"
            "    assert callable(featurelifted.ConfigFile.get_boolean)\n"
        ),
    )
    update_oracle_manifest(
        task,
        "dulwich",
        ["dulwich/config.py", "dulwich/file.py", "dulwich/_typing.py"],
        [],
        "Thin ConfigFile oracle; remaining dulwich tree is copy-all decoy.",
    )
    return task


def materialize_mimesis() -> Path:
    tid = "mimesis__person_address_core__001"
    clone = PIN / "mimesis__generic_locale_core__001"
    task = PILOT / tid
    if task.exists():
        shutil.rmtree(task)
    task.mkdir(parents=True)
    copy_repo(clone, task / "repo")
    dest = task / "reference_solution" / "featurelifted"
    copy_rewritten(clone / "mimesis", dest, "mimesis")
    thin_mimesis_oracle(dest)
    write_lock(task, [])
    write_text(task / "evaluation" / "forbidden_imports.txt", "mimesis\n")
    write_text(
        task / "public_tests" / "test_public_api.py",
        '''from __future__ import annotations

from featurelifted import Address, Locale, Person


def test_person_name_is_nonempty_string() -> None:
    person = Person(locale=Locale("en"), seed=7)
    name = person.name()
    assert isinstance(name, str) and name
    assert Person(locale=Locale("en"), seed=7).name() == name


def test_address_city_is_nonempty_string() -> None:
    address = Address(locale=Locale("en"), seed=7)
    city = address.city()
    assert isinstance(city, str) and city
''',
    )
    write_text(
        task / "hidden_tests" / "test_hidden_behavior.py",
        common_no_upstream("mimesis")
        + '''

from featurelifted import Address, Locale, LocaleError, Person


def test_invalid_locale_raises() -> None:
    try:
        Person(locale="not-a-locale")
    except LocaleError:
        return
    raise AssertionError("expected LocaleError")


def test_full_name_contains_first_and_last() -> None:
    person = Person(locale=Locale("en"), seed=3)
    full = person.full_name()
    parts = full.split()
    assert len(parts) >= 2
    assert all(parts)


def test_address_city_is_seed_stable() -> None:
    address = Address(locale=Locale("en"), seed=11)
    city = address.city()
    assert isinstance(city, str) and city
    assert Address(locale=Locale("en"), seed=11).city() == city
''',
    )
    write_text(
        task / "hidden_tests" / "test_required_api_surface.py",
        common_hidden_api(
            "    assert callable(featurelifted.Person)\n"
            "    assert callable(featurelifted.Address)\n"
            "    assert callable(featurelifted.Person.name)\n"
            "    assert callable(featurelifted.Person.full_name)\n"
            "    assert callable(featurelifted.Address.city)\n"
        ),
    )
    update_oracle_manifest(
        task,
        "mimesis",
        [
            "mimesis/__init__.py",
            "mimesis/constants.py",
            "mimesis/enums.py",
            "mimesis/exceptions.py",
            "mimesis/locales.py",
            "mimesis/random.py",
            "mimesis/types.py",
            "mimesis/providers/base.py",
            "mimesis/providers/person.py",
            "mimesis/providers/address.py",
            "mimesis/datasets/en/person.json",
            "mimesis/datasets/en/address.json",
        ],
        [],
        "Person/Address + en datasets only; other locales/providers remain repo decoy.",
    )
    return task


def fill_metadata(task: Path, payload: dict, copy_all: Path | None = None) -> None:
    oracle = task / "reference_solution" / "featurelifted"
    loc = py_loc(oracle)
    copy_loc = py_loc(copy_all) if copy_all and copy_all.exists() else loc
    payload["scoring_reference"] = {
        "oracle_loc": loc,
        "oracle_bytes": sum(p.stat().st_size for p in oracle.rglob("*") if p.is_file()),
        "oracle_dependency_count": len(payload["environment"].get("allowed_dependencies") or []),
        "copy_all_loc": copy_loc,
        "copy_all_bytes": (
            sum(p.stat().st_size for p in copy_all.rglob("*") if p.is_file())
            if copy_all and copy_all.exists()
            else 0
        ),
    }
    (task / "metadata.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def dulwich_meta() -> dict:
    return {
        "task_id": "dulwich__config_parse_core__001",
        "language": "python",
        "difficulty": "hard",
        "status": "materialized_candidate",
        "task_revision": 1,
        "tags": ["hard50", "remaining", "lift", "adapted", "configuration"],
        "source": {
            "name": "Dulwich",
            "url": "https://github.com/jelmer/dulwich",
            "commit": "2f039e67903559e279cb61250c6ea31bfa5f727c",
            "license": "Apache-2.0 OR GPL-2.0-or-later",
        },
        "feature": {
            "name": "Git config parse",
            "description": "Lift Dulwich Git config file parsing without a repository, pack store, or network.",
            "source_entrypoints": ["dulwich.config.ConfigFile"],
            "included_behaviors": [
                "from_file core values",
                "subsection keys",
                "boolean values",
                "missing key KeyError",
            ],
            "excluded_behaviors": ["git protocol", "pack files", "working trees", "network"],
        },
        "entanglement": {
            "level": "high",
            "types": ["config_environment_coupling", "data_model_coupling"],
            "primary": "config_environment_coupling",
            "description": "ConfigFile is a view over gitconfig sections and includes; porcelain and pack code is unused decoy.",
            "signals": ["section tuples", "filemode", "include"],
        },
        "output": {
            "package": "featurelifted",
            "import": "from featurelifted import ConfigFile",
            "callable": "ConfigFile.from_file",
            "signature": "ConfigFile.from_file(f, *, expand_includes=True)",
        },
        "environment": {
            "python": "3.12",
            "network": False,
            "timeout_seconds": 90,
            "dependency_lock": "requirements.lock",
            "allowed_dependencies": [],
            "forbidden_dependencies": ["dulwich"],
            "forbidden_imports": ["dulwich"],
            "forbidden_paths": ["repo/", "dulwich/"],
        },
        "tests": {"public": "public_tests/", "hidden": "hidden_tests/", "command": "pytest"},
        "spec_status": "compliant",
        "public_spec": {
            "title": "Git config parse",
            "summary": "Build a standalone `featurelifted` package that parses Git config files like Dulwich `ConfigFile`, including subsections and booleans, without speaking the Git protocol.",
            "required_api": [
                {
                    "path": "featurelifted.ConfigFile",
                    "kind": "class",
                    "signature": "()",
                    "members": [
                        {
                            "path": "featurelifted.ConfigFile.from_file",
                            "kind": "method",
                            "signature": "(cls, f, *, expand_includes=True)",
                        },
                        {
                            "path": "featurelifted.ConfigFile.from_path",
                            "kind": "method",
                            "signature": "(cls, path, *, expand_includes=True)",
                        },
                        {
                            "path": "featurelifted.ConfigFile.get",
                            "kind": "method",
                            "signature": "(self, section, name)",
                        },
                        {
                            "path": "featurelifted.ConfigFile.get_boolean",
                            "kind": "method",
                            "signature": "(self, section, name)",
                        },
                    ],
                }
            ],
            "optional_api": [],
            "behaviors": [
                {
                    "id": "B001",
                    "text": "`ConfigFile.from_file` on a buffer containing `[core]` / `filemode = true` yields `get((b\"core\",), b\"filemode\") == b\"true\"` when `expand_includes=False`.",
                },
                {
                    "id": "B002",
                    "text": "A `[remote \"origin\"]` `url` setting is readable with `get((b\"remote\", b\"origin\"), b\"url\")`.",
                },
                {
                    "id": "B003",
                    "text": "`get_boolean((b\"core\",), b\"filemode\")` is True for `filemode = true`.",
                },
                {
                    "id": "B004",
                    "text": "`get` on a missing key raises `KeyError`.",
                },
                {
                    "id": "B005",
                    "text": "The package exposes `ConfigFile` with `from_file`, `from_path`, `get`, and `get_boolean`.",
                },
                {
                    "id": "B006",
                    "text": "The submitted package source does not import the forbidden upstream package `dulwich`.",
                },
            ],
            "exclusions": ["git protocol", "pack files", "network", "runtime import of dulwich"],
            "forbidden": {"imports": ["dulwich"], "paths": []},
        },
        "evaluation_spec": {
            "public_clauses": [],
            "hidden_test_mappings": [],
            "required_api_coverage": [],
            "manual_review": {
                "reviewed_at": "2026-08-27",
                "reviewer": "hard50_materialization_agent",
                "reviewer_type": "ai_assisted_task_level_review",
                "checklist_passed": True,
                "notes": "Thin ConfigFile slice; no Git protocol.",
            },
        },
    }


def mimesis_meta() -> dict:
    return {
        "task_id": "mimesis__person_address_core__001",
        "language": "python",
        "difficulty": "hard",
        "status": "materialized_candidate",
        "task_revision": 1,
        "tags": ["hard50", "remaining", "lift", "direct", "tooling"],
        "source": {
            "name": "Mimesis",
            "url": "https://github.com/lk-geimfari/mimesis",
            "commit": "b285fd17ada4c916338c08fc105b8b72bda0630a",
            "license": "MIT",
        },
        "feature": {
            "name": "Person and address fake data",
            "description": "Lift Mimesis Person and Address providers for English locale data without the remaining locale/provider tree.",
            "source_entrypoints": ["mimesis.Person", "mimesis.Address"],
            "included_behaviors": ["seeded name", "city", "invalid locale", "full_name"],
            "excluded_behaviors": ["Generic all-providers", "binary file providers", "schema builder"],
        },
        "entanglement": {
            "level": "high",
            "types": ["data_model_coupling", "resource_coupling"],
            "primary": "data_model_coupling",
            "description": "Person/Address load JSON datasets by locale; other locales and providers are copy-all decoy.",
            "signals": ["Locale", "datasets JSON", "seed"],
        },
        "output": {
            "package": "featurelifted",
            "import": "from featurelifted import Person, Address, Locale, LocaleError",
            "callable": "Person",
            "signature": "Person(locale=Locale(\"en\"), seed=None)",
        },
        "environment": {
            "python": "3.12",
            "network": False,
            "timeout_seconds": 90,
            "dependency_lock": "requirements.lock",
            "allowed_dependencies": [],
            "forbidden_dependencies": ["mimesis"],
            "forbidden_imports": ["mimesis"],
            "forbidden_paths": ["repo/", "mimesis/"],
        },
        "tests": {"public": "public_tests/", "hidden": "hidden_tests/", "command": "pytest"},
        "spec_status": "compliant",
        "public_spec": {
            "title": "Person and address fake data",
            "summary": "Build a standalone `featurelifted` package providing Mimesis-style `Person` and `Address` generators for the English locale, including seeded names and invalid-locale errors.",
            "required_api": [
                {
                    "path": "featurelifted.Person",
                    "kind": "class",
                    "signature": "(locale=..., seed=...)",
                    "members": [
                        {"path": "featurelifted.Person.name", "kind": "method", "signature": "(self, gender=None)"},
                        {"path": "featurelifted.Person.full_name", "kind": "method", "signature": "(self, gender=None, reverse=False)"},
                    ],
                },
                {
                    "path": "featurelifted.Address",
                    "kind": "class",
                    "signature": "(locale=..., seed=...)",
                    "members": [
                        {"path": "featurelifted.Address.city", "kind": "method", "signature": "(self)"}
                    ],
                },
                {"path": "featurelifted.Locale", "kind": "class", "signature": ""},
                {"path": "featurelifted.LocaleError", "kind": "class", "signature": ""},
            ],
            "optional_api": [],
            "behaviors": [
                {
                    "id": "B001",
                    "text": "`Person(locale=Locale(\"en\"), seed=7).name()` returns a non-empty string, and a second instance constructed with the same arguments returns the same name.",
                },
                {
                    "id": "B002",
                    "text": "`Address(locale=Locale(\"en\"), seed=7).city()` returns a non-empty string.",
                },
                {
                    "id": "B003",
                    "text": "`Person(locale=\"not-a-locale\")` raises `LocaleError`.",
                },
                {
                    "id": "B004",
                    "text": "`full_name()` returns a string with at least two whitespace-separated parts for a seeded English person.",
                },
                {
                    "id": "B005",
                    "text": "The package exposes `Person`, `Address`, `Locale`, and `LocaleError`.",
                },
                {
                    "id": "B006",
                    "text": "The submitted package source does not import the forbidden upstream package `mimesis`.",
                },
            ],
            "exclusions": ["Generic provider bundle", "binary files", "runtime import of mimesis"],
            "forbidden": {"imports": ["mimesis"], "paths": []},
        },
        "evaluation_spec": {
            "public_clauses": [],
            "hidden_test_mappings": [],
            "required_api_coverage": [],
            "manual_review": {
                "reviewed_at": "2026-08-27",
                "reviewer": "hard50_materialization_agent",
                "reviewer_type": "ai_assisted_task_level_review",
                "checklist_passed": True,
                "notes": "Person/Address + en datasets; other locales remain in repo.",
            },
        },
    }


def fill_eval_spec(payload: dict, public_tests: list[tuple[str, str]], hidden_tests: list[tuple[str, str]], api_paths: list[str]) -> None:
    payload["evaluation_spec"]["public_clauses"] = [
        {"behavior_id": item["id"], "clause_kind": "included_behavior", "text": item["text"]}
        for item in payload["public_spec"]["behaviors"]
    ]
    payload["evaluation_spec"]["public_test_mappings"] = [
        {"nodeid": node, "behavior_ids": [bid], "mapping_method": "ai_assisted"}
        for bid, node in public_tests
    ]
    payload["evaluation_spec"]["hidden_test_mappings"] = [
        {"nodeid": node, "behavior_ids": [bid], "mapping_method": "ai_assisted"}
        for bid, node in hidden_tests
    ]
    payload["evaluation_spec"]["required_api_coverage"] = [
        {
            "path": path,
            "covered_by_tests": ["hidden_tests/test_required_api_surface.py::test_required_api_surface"],
        }
        for path in api_paths
    ]


def update_ledger() -> None:
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    by_id = {row["task_id"]: row for row in data["rows"]}
    swaps = [
        (
            "django_environ__env_cast_core__001",
            "dulwich__config_parse_core__001",
            {
                "task_id": "dulwich__config_parse_core__001",
                "package": "dulwich",
                "repository_url": "https://github.com/jelmer/dulwich",
                "disposition": "selected",
                "planned_lift_type": "Adapted",
                "feature_family": "config_resolve_discover",
                "entanglement_level": "high",
                "entanglement_types": ["config_environment_coupling", "data_model_coupling"],
                "commit": "2f039e67903559e279cb61250c6ea31bfa5f727c",
                "design_card": "benchmark/selection/hard50_design_cards/dulwich__config_parse_core__001.md",
                "paper_fit": "RQ2: Git config slice inside a large porcelain/pack tree.",
                "why_hard": "Section tuples and includes; copying porcelain fails isolation.",
            },
        ),
        (
            "wcmatch__globmatch_core__001",
            "mimesis__person_address_core__001",
            {
                "task_id": "mimesis__person_address_core__001",
                "package": "mimesis",
                "repository_url": "https://github.com/lk-geimfari/mimesis",
                "disposition": "selected",
                "planned_lift_type": "Direct",
                "feature_family": "direct_tooling_copytrap",
                "entanglement_level": "high",
                "entanglement_types": ["data_model_coupling", "resource_coupling"],
                "commit": "b285fd17ada4c916338c08fc105b8b72bda0630a",
                "design_card": "benchmark/selection/hard50_design_cards/mimesis__person_address_core__001.md",
                "paper_fit": "RQ2: Person/Address vs dozens of unused locale JSON trees.",
                "why_hard": "Must load the right dataset files; copying Generic pulls unused providers.",
            },
        ),
    ]
    for old_id, new_id, new_row in swaps:
        old = by_id[old_id]
        old["disposition"] = "backup"
        old["replaced_by"] = new_id
        old["replace_reason"] = "Flash copy_heavy_pass RRES~1 on small-repo slice"
        if new_id not in by_id:
            data["rows"].append(new_row)
        else:
            by_id[new_id].update(new_row)
    data["status"] = "hard50_copyheavy_swaps_in_progress"
    data["notes"] = (
        "Swapping copy_heavy_pass Flash winners. dulwich replaced django_environ; "
        "mimesis replaced wcmatch. respx/bytecode/fastjsonschema/docutils still pending."
    )
    LEDGER.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    move_old("django_environ__env_cast_core__001")
    move_old("wcmatch__globmatch_core__001")
    dulwich = materialize_dulwich()
    mimesis = materialize_mimesis()
    dmeta = dulwich_meta()
    fill_eval_spec(
        dmeta,
        [
            ("B001", "public_tests/test_public_api.py::test_core_filemode_from_file"),
            ("B002", "public_tests/test_public_api.py::test_subsection_remote_url"),
        ],
        [
            ("B001", "hidden_tests/test_hidden_behavior.py::test_from_path_reads_core_and_remote"),
            ("B002", "hidden_tests/test_hidden_behavior.py::test_from_path_reads_core_and_remote"),
            ("B003", "hidden_tests/test_hidden_behavior.py::test_boolean_and_missing_key"),
            ("B004", "hidden_tests/test_hidden_behavior.py::test_boolean_and_missing_key"),
            ("B006", "hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface"),
            ("B005", "hidden_tests/test_required_api_surface.py::test_required_api_surface"),
        ],
        [
            "featurelifted.ConfigFile",
            "featurelifted.ConfigFile.from_file",
            "featurelifted.ConfigFile.from_path",
            "featurelifted.ConfigFile.get",
            "featurelifted.ConfigFile.get_boolean",
        ],
    )
    mmeta = mimesis_meta()
    fill_eval_spec(
        mmeta,
        [
            ("B001", "public_tests/test_public_api.py::test_person_name_is_nonempty_string"),
            ("B002", "public_tests/test_public_api.py::test_address_city_is_nonempty_string"),
        ],
        [
            ("B001", "hidden_tests/test_hidden_behavior.py::test_full_name_contains_first_and_last"),
            ("B002", "hidden_tests/test_hidden_behavior.py::test_address_city_is_seed_stable"),
            ("B003", "hidden_tests/test_hidden_behavior.py::test_invalid_locale_raises"),
            ("B004", "hidden_tests/test_hidden_behavior.py::test_full_name_contains_first_and_last"),
            ("B006", "hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface"),
            ("B005", "hidden_tests/test_required_api_surface.py::test_required_api_surface"),
        ],
        [
            "featurelifted.Person",
            "featurelifted.Person.name",
            "featurelifted.Person.full_name",
            "featurelifted.Address",
            "featurelifted.Address.city",
            "featurelifted.Locale",
            "featurelifted.LocaleError",
        ],
    )
    d_copy = write_submissions(dulwich, PIN / dulwich.name, "dulwich")
    m_copy = write_submissions(mimesis, PIN / "mimesis__generic_locale_core__001", "mimesis")
    fill_metadata(dulwich, dmeta, d_copy)
    fill_metadata(mimesis, mmeta, m_copy)
    update_ledger()
    print(
        "materialized",
        dulwich.name,
        "oracle_loc",
        dmeta["scoring_reference"]["oracle_loc"],
        "copy_all_loc",
        dmeta["scoring_reference"]["copy_all_loc"],
    )
    print(
        "materialized",
        mimesis.name,
        "oracle_loc",
        mmeta["scoring_reference"]["oracle_loc"],
        "copy_all_loc",
        mmeta["scoring_reference"]["copy_all_loc"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3.12
"""Copy pinned clones into hard50_pilot repo/ and build import-rewritten oracles."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PILOT = ROOT / "benchmark" / "hard50_pilot"
PIN_ROOT = Path("/tmp/flb_hard50_pins")
IGNORE = shutil.ignore_patterns(
    ".git",
    ".github",
    "__pycache__",
    "*.pyc",
    ".mypy_cache",
    "*.egg-info",
    ".tox",
    ".venv",
    "node_modules",
    "docs",
    "imgs",
)

IMPORT_LINE = re.compile(
    r"^(\s*)(from|import)[ \t]+(?P<pkg>{pkg})(\b|\.)",
    re.MULTILINE,
)


def rewrite_text(text: str, old: str, extra: list[tuple[str, str]] | None = None) -> str:
    # Keep `import pkg` as `import featurelifted as pkg` so attribute uses still resolve
    # without rewriting string literals such as Hydra's "hydra.job.name" config keys.
    text = re.sub(
        rf"^(\s*)from {re.escape(old)}(\.| import\b)",
        rf"\1from featurelifted\2",
        text,
        flags=re.M,
    )
    text = re.sub(
        rf"^(\s*)from {re.escape(old)}\b",
        rf"\1from featurelifted",
        text,
        flags=re.M,
    )
    def _import_sub(match: re.Match[str]) -> str:
        indent, rest = match.group(1), match.group(2)
        alias = rest.rsplit(".", 1)[-1]
        return f"{indent}import featurelifted.{rest} as {alias}"

    text = re.sub(
        rf"^(\s*)import {re.escape(old)}\.([A-Za-z0-9_\.]+) as ([A-Za-z0-9_]+)",
        rf"\1import featurelifted.\2 as \3",
        text,
        flags=re.M,
    )
    text = re.sub(
        rf"^(\s*)import {re.escape(old)}\.([A-Za-z0-9_\.]+)",
        _import_sub,
        text,
        flags=re.M,
    )
    text = re.sub(
        rf"^(\s*)import {re.escape(old)}\b as ([A-Za-z0-9_]+)",
        rf"\1import featurelifted as \2",
        text,
        flags=re.M,
    )
    alias = old if old.isidentifier() else "featurelifted"
    if alias == "featurelifted":
        text = re.sub(
            rf"^(\s*)import {re.escape(old)}\b",
            r"\1import featurelifted",
            text,
            flags=re.M,
        )
    else:
        text = re.sub(
            rf"^(\s*)import {re.escape(old)}\b",
            rf"\1import featurelifted as {old}",
            text,
            flags=re.M,
        )
    for src, dst in extra or []:
        text = text.replace(src, dst)
    if old.isidentifier() and re.search(rf"(?<![A-Za-z0-9_]){re.escape(old)}\.", text):
        alias_line = f"import featurelifted as {old}"
        if alias_line not in text:
            futures = list(re.finditer(r"^from __future__ import[^\n]*\n", text, re.M))
            if futures:
                pos = futures[-1].end()
                text = text[:pos] + alias_line + "\n" + text[pos:]
            else:
                text = alias_line + "\n" + text
    return text


def copy_rewritten(src: Path, dest: Path, old: str, extra: list[tuple[str, str]] | None = None) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest, ignore=IGNORE)
    for path in dest.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in {".py", ".pyi", ".typed"} and path.name != "py.typed":
            continue
        if path.suffix not in {".py", ".pyi"}:
            continue
        raw = path.read_text(encoding="utf-8", errors="replace")
        updated = rewrite_text(raw, old, extra)
        if updated != raw:
            path.write_text(updated, encoding="utf-8")


def copy_repo(src: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest, ignore=IGNORE)
    marker = dest / ".source-archive-backed"
    if marker.exists():
        marker.unlink()
    marker.write_text(f"pinned clone {src}\n", encoding="utf-8")


def append_init(dest: Path, block: str) -> None:
    init = dest / "__init__.py"
    current = init.read_text(encoding="utf-8") if init.exists() else ""
    if block.strip() not in current:
        init.write_text(current.rstrip() + "\n\n" + block.strip() + "\n", encoding="utf-8")


def write_lock(task_dir: Path, lines: list[str]) -> None:
    text = "\n".join(lines) + ("\n" if lines else "")
    (task_dir / "requirements.lock").write_text(text or "# no third-party dependencies\n", encoding="utf-8")


def ensure_hydra_grammar(clone: Path) -> None:
    gen = clone / "hydra" / "grammar" / "gen"
    if (gen / "OverrideParser.py").exists():
        return
    work = Path("/tmp/flb_hydra_wheel")
    if work.exists():
        shutil.rmtree(work)
    work.mkdir()
    subprocess.check_call(
        ["python3.12", "-m", "pip", "download", "hydra-core==1.3.2", "--no-deps", "-d", str(work)],
        stdout=subprocess.DEVNULL,
    )
    archive = next(work.glob("hydra_core-*.whl"), None) or next(work.glob("hydra-core-*.tar.gz"))
    extract = work / "extract"
    extract.mkdir()
    if archive.suffix == ".whl":
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(extract)
    else:
        with tarfile.open(archive) as tf:
            tf.extractall(extract)
    src_gen = next(extract.rglob("OverrideParser.py")).parent
    gen.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src_gen, gen, dirs_exist_ok=True)


def update_oracle_manifest(task_dir: Path, package: str, files: list[str], deps: list[str], notes: str) -> None:
    path = task_dir / "evaluation" / "oracle_manifest.json"
    payload = {
        "source_package_name": package,
        "required_source_files": files,
        "runtime_dependencies": deps,
        "notes": notes,
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def materialize() -> None:
    tasks = {
        "confuse__nested_view_core__001": {
            "src_pkg": PIN_ROOT / "confuse__nested_view_core__001" / "confuse",
            "old": "confuse",
            "deps": ["PyYAML==6.0.2"],
            "keep_existing_oracle": False,
        },
        "oslo_config__opt_group_core__001": {
            "src_pkg": PIN_ROOT / "oslo_config__opt_group_core__001" / "oslo_config",
            "old": "oslo_config",
            "deps": [
                "netaddr==1.3.0",
                "rfc3986==2.0.0",
                "stevedore==5.6.0",
                "oslo.i18n==6.6.0",
                "PyYAML==6.0.2",
                "debtcollector==3.0.0",
                "pbr==7.0.3",
                "wrapt==1.17.3",
            ],
            "init": "from .cfg import ConfigOpts, Opt, OptGroup\n",
        },
        "injector__module_bind_core__001": {
            "src_pkg": PIN_ROOT / "injector__module_bind_core__001" / "injector",
            "old": "injector",
            "deps": [],
        },
        "luigi__task_requires_core__001": {
            "src_pkg": PIN_ROOT / "luigi__task_requires_core__001" / "luigi",
            "old": "luigi",
            "deps": [
                "python-dateutil==2.9.0.post0",
                "tenacity==9.1.2",
                "tornado==6.5.2",
                "typing-extensions==4.15.0",
            ],
        },
        "cliff__command_dispatch_core__001": {
            "src_pkg": PIN_ROOT / "cliff__command_dispatch_core__001" / "cliff",
            "old": "cliff",
            "deps": [
                "autopage==0.5.2",
                "cmd2==2.7.0",
                "PrettyTable==3.16.0",
                "stevedore==5.6.0",
                "PyYAML==6.0.2",
            ],
            "init": "from .app import App\nfrom .command import Command\nfrom .commandmanager import CommandManager\n",
        },
        "zope_interface__adapter_registry_core__001": {
            "src_pkg": PIN_ROOT / "zope_interface__adapter_registry_core__001" / "src" / "zope" / "interface",
            "old": "zope.interface",
            "deps": [],
            "init": "from .adapter import AdapterRegistry\nfrom .declarations import implementer, providedBy\nfrom .interface import Interface\n",
        },
        "dogpile_cache__region_backend_core__001": {
            "src_pkg": PIN_ROOT / "dogpile_cache__region_backend_core__001" / "dogpile",
            "old": "dogpile",
            "extra": [
                ('"dogpile.cache.backends', '"featurelifted.cache.backends'),
                ("'dogpile.cache.backends", "'featurelifted.cache.backends"),
                ('"dogpile.util', '"featurelifted.util'),
                ("'dogpile.util", "'featurelifted.util"),
            ],
            "deps": ["decorator==5.2.1", "stevedore==5.6.0"],
            "init": "from .cache import CacheRegion, make_region\nfrom .cache.api import NO_VALUE\n",
        },
        "hydra_core__compose_initialize_core__001": {
            "src_pkg": PIN_ROOT / "hydra_core__compose_initialize_core__001" / "hydra",
            "old": "hydra",
            "deps": ["omegaconf==2.3.0", "PyYAML==6.0.2", "packaging==25.0", "antlr4-python3-runtime==4.9.3"],
            "init": "from .compose import compose\nfrom .core.global_hydra import GlobalHydra\nfrom .initialize import initialize\n",
            "hydra_grammar": True,
            "extra": [
                ('import_module("hydra.', 'import_module("featurelifted.'),
                ('import_module(\'hydra.', "import_module('featurelifted."),
                ('"hydra._internal', '"featurelifted._internal'),
                ("'hydra._internal", "'featurelifted._internal"),
            ],
        },
        "taskiq__broker_task_core__001": {
            "src_pkg": PIN_ROOT / "taskiq__broker_task_core__001" / "taskiq",
            "old": "taskiq",
            "deps": [
                "aiohttp==3.12.15",
                "anyio==4.10.0",
                "packaging==25.0",
                "pycron==3.1.2",
                "pydantic==2.11.7",
                "taskiq-dependencies==1.5.7",
            ],
            "init": (
                "from .abc.broker import AsyncTaskiqDecoratedTask as DecoratedTask\n"
                "from .brokers.inmemory_broker import InMemoryBroker\n"
                "from .result import TaskiqResult as TaskResult\n"
                "from .task import AsyncTaskiqTask as TaskHandle\n"
            ),
        },
        "openapi_core__request_validate_core__001": {
            "src_pkg": PIN_ROOT / "openapi_core__request_validate_core__001" / "openapi_core",
            "old": "openapi_core",
            "deps": [
                "jsonschema>=4.23",
                "openapi-schema-validator>=0.9,<0.10",
                "openapi-spec-validator>=0.9,<0.10",
                "jsonschema-path>=0.5,<0.6",
                "isodate",
                "more-itertools",
                "werkzeug>=2.1",
                "typing-extensions>=4.8",
            ],
            "init": (
                "from .app import OpenAPI\n"
                "from .datatypes import RequestParameters\n"
                "from .exceptions import SpecError\n"
                "from .unmarshalling.request.datatypes import RequestUnmarshalResult as UnmarshalResult\n"
                "from .validation.request.exceptions import MissingRequiredParameter, MissingRequiredRequestBody\n"
                "from .validation.response.exceptions import ResponseValidationError\n"
            ),
        },
    }

    for task_id, spec in tasks.items():
        clone = PIN_ROOT / task_id
        task_dir = PILOT / task_id
        print(f"materializing {task_id}")
        if spec.get("hydra_grammar"):
            ensure_hydra_grammar(clone)
        copy_repo(clone, task_dir / "repo")
        dest = task_dir / "reference_solution" / "featurelifted"
        copy_rewritten(spec["src_pkg"], dest, spec["old"], spec.get("extra"))
        if spec.get("init"):
            append_init(dest, spec["init"])
        if task_id == "hydra_core__compose_initialize_core__001":
            for path in dest.rglob("*.py"):
                raw = path.read_text(encoding="utf-8")
                updated = raw.replace("omegaconf.vendor.antlr4", "antlr4")
                updated = re.sub(r",\s*replace=True", "", updated)
                updated = re.sub(r",\s*use_cache=True", "", updated)
                if updated != raw:
                    path.write_text(updated, encoding="utf-8")
            env_src = Path("/tmp/flb_hydra_wheel/extract/hydra/conf/hydra/env/default.yaml")
            if env_src.exists():
                env_dst = dest / "conf" / "hydra" / "env"
                env_dst.mkdir(parents=True, exist_ok=True)
                shutil.copy2(env_src, env_dst / "default.yaml")
            for path in dest.rglob("*.py"):
                raw = path.read_text(encoding="utf-8")
                updated = raw.replace("pkg://hydra.", "pkg://featurelifted.")
                if updated != raw:
                    path.write_text(updated, encoding="utf-8")
            utils = dest / "core" / "utils.py"
            text = utils.read_text(encoding="utf-8")
            helper = (
                "def _register_resolver(name, resolver, **kwargs):\n"
                "    try:\n"
                "        OmegaConf.register_resolver(name, resolver)\n"
                "    except Exception:\n"
                "        return\n\n"
            )
            if "_register_resolver" not in text:
                text = text.replace(
                    "def setup_globals() -> None:",
                    helper + "def setup_globals() -> None:",
                    1,
                )
                text = text.replace("OmegaConf.register_resolver(", "_register_resolver(")
                utils.write_text(text, encoding="utf-8")
        if task_id == "taskiq__broker_task_core__001":
            init = dest / "__init__.py"
            init.write_text(
                init.read_text(encoding="utf-8").replace(
                    '__version__ = version("taskiq")',
                    'try:\n    __version__ = version("taskiq")\nexcept Exception:\n    __version__ = "0.0.0"',
                    1,
                ),
                encoding="utf-8",
            )
        write_lock(task_dir, spec["deps"])
        py_files = sorted(
            str(p.relative_to(dest.parent)).replace("featurelifted/", f"{spec['old']}/", 1)
            if False
            else str(p.relative_to(dest)).replace("\\", "/")
            for p in dest.rglob("*.py")
        )
        rel = [f"{spec['old']}/{name}" for name in py_files[:40]]
        update_oracle_manifest(
            task_dir,
            spec["old"],
            rel,
            [line.split("==")[0] for line in spec["deps"]],
            "Import-rewritten upstream package used as oracle; copy-all should include extra repo decoys.",
        )


if __name__ == "__main__":
    materialize()

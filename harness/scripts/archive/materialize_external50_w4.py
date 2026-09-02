#!/usr/bin/env python3
"""Materialize External-50 W4 tasks into benchmark/staging/."""

from __future__ import annotations

import importlib.util
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
PILOT = ROOT / "harness" / "scripts" / "materialize_external50_pilot.py"
W1 = ROOT / "harness" / "scripts" / "materialize_external50_w1.py"
PIN_ROOT = Path("/tmp/flb_w345_pins")
STAGING = ROOT / "benchmark" / "staging"

spec = importlib.util.spec_from_file_location("pilot_mat", PILOT)
pilot = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(pilot)

w1_spec = importlib.util.spec_from_file_location("w1_mat", W1)
w1 = importlib.util.module_from_spec(w1_spec)
assert w1_spec.loader is not None
w1_spec.loader.exec_module(w1)

copy_package_tree = w1.copy_package_tree
write_json = pilot.write_json
finalize_metadata = pilot.finalize_metadata
base_metadata = pilot.base_metadata
make_archive_and_register = pilot.make_archive_and_register


def w4_metadata(task_id: str, meta: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    metadata = base_metadata(task_id, meta, **kwargs)
    metadata["tags"] = ["external50", "w4", meta["lift"].lower(), meta["forbidden"]]
    return metadata


def _forbidden_import_test(forbidden: str) -> str:
    return f'''from __future__ import annotations

import re
from pathlib import Path


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\\\s*(?:from {re.escape(forbidden)}\\\\b|import {re.escape(forbidden)}\\\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
'''


def _prepare(task_id: str, meta: dict[str, Any]) -> Path:
    task_dir = STAGING / task_id
    if task_dir.exists():
        shutil.rmtree(task_dir)
    task_dir.mkdir(parents=True)
    shutil.copytree(
        meta["src"],
        task_dir / "repo",
        ignore=shutil.ignore_patterns(
            "__pycache__", "*.pyc", ".flb_pin", "*.tar.gz", "wheels", ".git", "*.dist-info"
        ),
    )
    (task_dir / "evaluation").mkdir(parents=True)
    (task_dir / "public_tests").mkdir()
    (task_dir / "hidden_tests").mkdir()
    return task_dir


def _install_flask_cors(ref: Path) -> None:
    ref.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PIN_ROOT / "flask_cors" / "flask_cors.py", ref / "__init__.py")
    init = ref / "__init__.py"
    text = init.read_text(encoding="utf-8")
    if "collections.abc" not in text:
        text = text.replace("import collections\n", "import collections\nimport collections.abc\n", 1)
    text = text.replace("collections.Iterable", "collections.abc.Iterable")
    init.write_text(text, encoding="utf-8")


def _fix_circular_subimport(ref: Path, submod: str) -> None:
    init = ref / "__init__.py"
    if not init.exists():
        return
    text = init.read_text(encoding="utf-8")
    text = text.replace("from . import featurelifted, parser", f"from . import {submod}, parser")
    text = text.replace("from . import featurelifted", f"from . import {submod}")
    text = text.replace("featurelifted.__doc__", f"{submod}.__doc__")
    text = text.replace("featurelifted.__all__", f"{submod}.__all__")
    init.write_text(text, encoding="utf-8")


def _fix_jwt_local_var_rewrites(ref: Path) -> None:
    for path in ref.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        updated = text
        for method in ("rsplit", "split"):
            updated = re.sub(
                rf"\bfeaturelifted\.{method}\(",
                f"jwt.{method}(",
                updated,
            )
        for method in ("encode", "decode"):
            updated = re.sub(
                rf"\bjwt = featurelifted\.{method}\(",
                f"jwt = jwt.{method}(",
                updated,
            )
        if updated != text:
            path.write_text(updated, encoding="utf-8")


def _install_python_crontab(ref: Path) -> None:
    ref.mkdir(parents=True, exist_ok=True)
    wheel_dir = PIN_ROOT / "python_crontab"
    for name in ("crontab.py", "crontabs.py", "cronlog.py"):
        shutil.copy2(wheel_dir / name, ref / name)
    crontabs = ref / "crontabs.py"
    crontabs.write_text(
        crontabs.read_text(encoding="utf-8").replace(
            "from crontab import", "from featurelifted.crontab import"
        ),
        encoding="utf-8",
    )
    crontab_py = ref / "crontab.py"
    crontab_py.write_text(
        crontab_py.read_text(encoding="utf-8").replace(
            "from cronlog import", "from featurelifted.cronlog import"
        ),
        encoding="utf-8",
    )
    (ref / "__init__.py").write_text(
        '''"""Task-scoped python-crontab CronSlices/CronItem extract."""

from .crontab import CronItem, CronSlices

__all__ = ["CronItem", "CronSlices"]
''',
        encoding="utf-8",
    )


def _force_ijson_python_backend(ref: Path) -> None:
    init = ref / "__init__.py"
    text = init.read_text(encoding="utf-8")
    replacement = """def _default_backend():
    return get_backend('python')
backend = _default_backend()
del _default_backend"""
    text = re.sub(
        r"def _default_backend\(\):.*?del _default_backend",
        replacement,
        text,
        count=1,
        flags=re.DOTALL,
    )
    init.write_text(text, encoding="utf-8")


PINS: dict[str, dict[str, Any]] = {
    "cloudpickle__dumps_loads_core__001": {
        "package": "cloudpickle",
        "url": "https://github.com/cloudpipe/cloudpickle",
        "commit": "7576fff24b9769432f76cc6d2c01282583ee87a9",
        "tag": "v3.1.2",
        "license": "BSD-3-Clause",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "cloudpickle",
        "forbidden": "cloudpickle",
        "lift": "Adapted",
        "pkg_dir": lambda: PIN_ROOT / "cloudpickle" / "cloudpickle",
    },
    "configupdater__ini_roundtrip_core__001": {
        "package": "ConfigUpdater",
        "url": "https://github.com/pyscaffold/configupdater",
        "commit": "18ef0d613324c120a58d051cab717de493c18669",
        "tag": "v3.2",
        "license": "MIT",
        "license_path": "LICENSE.txt",
        "src": PIN_ROOT / "configupdater",
        "forbidden": "configupdater",
        "lift": "Adapted",
        "pkg_dir": lambda: PIN_ROOT / "configupdater" / "src" / "configupdater",
    },
    "flask_cors__cors_options_core__001": {
        "package": "flask-cors",
        "url": "https://github.com/corydolphin/flask-cors",
        "commit": "a0c7ef33ac6a79b84570a81d512f64dcbf9b97a7",
        "tag": "v1.8.0",
        "license": "MIT",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "flask_cors",
        "forbidden": "flask_cors",
        "lift": "Adapted",
        "pkg_dir": lambda: PIN_ROOT / "flask_cors",
    },
    "freezegun__freeze_time_core__001": {
        "package": "freezegun",
        "url": "https://github.com/spulec/freezegun",
        "commit": "c9bf52c5aa12ea1b5b8647a136a92504ea071f2f",
        "tag": "1.5.5",
        "license": "Apache-2.0",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "freezegun",
        "forbidden": "freezegun",
        "lift": "Adapted",
        "pkg_dir": lambda: PIN_ROOT / "freezegun" / "freezegun",
    },
    "furl__url_mutate_core__001": {
        "package": "furl",
        "url": "https://github.com/gruns/furl",
        "commit": "fea659e66f078f3c81b1a70e609192ea3aedfef6",
        "tag": "v2.1.4",
        "license": "Unlicense",
        "license_path": "LICENSE.md",
        "src": PIN_ROOT / "furl",
        "forbidden": "furl",
        "lift": "Adapted",
        "pkg_dir": lambda: PIN_ROOT / "furl" / "furl",
    },
    "hyperlink__url_parse_core__001": {
        "package": "hyperlink",
        "url": "https://github.com/python-hyper/hyperlink",
        "commit": "eae9223fafccfc4b32f8309bfe2b6817c3a88331",
        "tag": "v21.0.0",
        "license": "MIT",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "hyperlink",
        "forbidden": "hyperlink",
        "lift": "Adapted",
        "pkg_dir": lambda: PIN_ROOT / "hyperlink" / "src" / "hyperlink",
    },
    "ijson__event_parse_core__001": {
        "package": "ijson",
        "url": "https://github.com/ICRAR/ijson",
        "commit": "d991ad9ed9afdd140f1e234cb653cc12a7439904",
        "tag": "v3.5.1",
        "license": "BSD-3-Clause",
        "license_path": "LICENSE.txt",
        "src": PIN_ROOT / "ijson",
        "forbidden": "ijson",
        "lift": "Adapted",
        "pkg_dir": lambda: PIN_ROOT / "ijson" / "src" / "ijson",
    },
    "jsonpickle__handler_roundtrip_core__001": {
        "package": "jsonpickle",
        "url": "https://github.com/jsonpickle/jsonpickle",
        "commit": "3e5ce68e62bc55e22a097a010fc10e0b47d065c1",
        "tag": "v4.1.2",
        "license": "BSD-3-Clause",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "jsonpickle",
        "forbidden": "jsonpickle",
        "lift": "Adapted",
        "pkg_dir": lambda: PIN_ROOT / "jsonpickle" / "jsonpickle",
    },
    "packageurl__purl_parse_core__001": {
        "package": "packageurl-python",
        "url": "https://github.com/package-url/packageurl-python",
        "commit": "04b755ccc388d6a53bb5277d1f95de4baa727deb",
        "tag": "v0.17.6",
        "license": "MIT",
        "license_path": "mit.LICENSE",
        "src": PIN_ROOT / "packageurl",
        "forbidden": "packageurl",
        "lift": "Adapted",
        "pkg_dir": lambda: PIN_ROOT / "packageurl" / "src" / "packageurl",
    },
    "pyjwt__encode_decode_core__001": {
        "package": "PyJWT",
        "url": "https://github.com/jpadilla/pyjwt",
        "commit": "7144e4534c34810f4525dc4578a32addd8212cff",
        "tag": "2.13.0",
        "license": "MIT",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "pyjwt",
        "forbidden": "jwt",
        "lift": "Adapted",
        "pkg_dir": lambda: PIN_ROOT / "pyjwt" / "jwt",
    },
    "python_crontab__cron_item_core__001": {
        "package": "python-crontab",
        "url": "https://github.com/lyda/python-crontab",
        "commit": "19f19fbe9a2f462bef0b268842718f3ebd1745ea",
        "tag": "3.3.0",
        "license": "LGPL-3.0",
        "license_path": "COPYING",
        "src": PIN_ROOT / "python_crontab",
        "forbidden": "crontab",
        "lift": "Adapted",
        "pkg_dir": lambda: PIN_ROOT / "python_crontab",
    },
}


def materialize_cloudpickle() -> Path:
    task_id = "cloudpickle__dumps_loads_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "cloudpickle")
    _fix_circular_subimport(ref, "cloudpickle")
    (task_dir / "requirements.lock").write_text("# no third-party dependencies\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("cloudpickle\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "cloudpickle",
            "required_source_files": ["cloudpickle/cloudpickle.py", "cloudpickle/__init__.py"],
            "runtime_dependencies": [],
            "notes": "Adapted dumps/loads for dynamic callables and closures.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import dumps, loads


def test_closure_roundtrip() -> None:
    def make_adder(n: int):
        def add(x: int) -> int:
            return x + n

        return add

    fn = loads(dumps(make_adder(3)))
    assert fn(5) == 8


def test_nested_function() -> None:
    def outer(x: int):
        def inner(y: int) -> int:
            return x + y

        return inner

    restored = loads(dumps(outer(10)))
    assert restored(7) == 17


def test_lambda_roundtrip() -> None:
    fn = loads(dumps(lambda v: v * 2))
    assert fn(4) == 8
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        _forbidden_import_test("cloudpickle")
        + '''

from featurelifted import CloudPickler, dumps, loads


def test_cloudpickler_class() -> None:
    assert CloudPickler is not None


def test_dict_with_function_value() -> None:
    def f() -> int:
        return 1

    payload = {"fn": f}
    restored = loads(dumps(payload))
    assert callable(restored["fn"])
    assert restored["fn"]() == 1
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import CloudPickler, dumps, loads


def test_required_api_surface() -> None:
    assert callable(dumps) and callable(loads)
    assert CloudPickler is not None
''',
        encoding="utf-8",
    )
    metadata = w4_metadata(
        task_id,
        meta,
        feature={
            "name": "cloudpickle dumps loads",
            "description": "Adapted cloudpickle dumps/loads for dynamic callables.",
            "source_entrypoints": ["cloudpickle.dumps", "cloudpickle.loads"],
            "included_behaviors": [
                "dumps/loads roundtrip for nested functions and lambdas",
                "CloudPickler export",
            ],
            "excluded_behaviors": ["interactive __main__ edge cases", "distributed cluster pickling"],
        },
        entanglement={
            "level": "medium",
            "types": ["data_model_coupling"],
            "primary": "data_model_coupling",
            "description": "Dynamic code objects serialized via cloudpickle.",
            "signals": ["closures", "lambdas", "CloudPickler"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import dumps, loads",
            "callable": "dumps",
            "signature": "dumps(obj, protocol=None) -> bytes",
        },
        public_spec={
            "title": "cloudpickle dumps loads",
            "summary": "Extract a task-scoped subset of `cloudpickle` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.dumps", "kind": "function", "signature": "(obj, protocol=None) -> bytes"},
                {"path": "featurelifted.loads", "kind": "function", "signature": "(data: bytes) -> Any"},
                {"path": "featurelifted.CloudPickler", "kind": "class"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: dumps/loads roundtrip for nested functions and closures. Required observable cases include closure roundtrip; nested function."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: lambda roundtrip and dict values containing callables. Required observable cases include lambda roundtrip; dict with function value."},
                {"id": "B003", "text": "CloudPickler class is exported for advanced pickling."},
                {"id": "B004", "text": "No third-party runtime dependencies are required."},
                {"id": "B005", "text": "The package exposes dumps/loads/CloudPickler with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: cloudpickle."},
            ],
            "exclusions": ["interactive __main__ edge cases", "original cloudpickle import at runtime"],
            "forbidden": {"imports": ["cloudpickle"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_configupdater() -> Path:
    task_id = "configupdater__ini_roundtrip_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "configupdater")
    _fix_circular_subimport(ref, "configupdater")
    (task_dir / "requirements.lock").write_text("# no third-party dependencies\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("configupdater\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "configupdater",
            "required_source_files": [
                "src/configupdater/configupdater.py",
                "src/configupdater/parser.py",
            ],
            "runtime_dependencies": [],
            "notes": "Adapted ConfigUpdater read_string + section/option + write(StringIO).",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from io import StringIO

from featurelifted import ConfigUpdater


INI = """[app]
# keep this comment
name = old
enabled = true
"""


def test_read_modify_write_stringio() -> None:
    cu = ConfigUpdater()
    cu.read_string(INI)
    assert cu["app"]["name"].value == "old"
    cu["app"]["name"].value = "new"
    buf = StringIO()
    cu.write(buf)
    out = buf.getvalue()
    assert "# keep this comment" in out
    assert "name = new" in out


def test_section_option_access() -> None:
    cu = ConfigUpdater()
    cu.read_string("[s]\\nkey = v\\n")
    assert "s" in cu
    assert cu["s"]["key"].value == "v"


def test_add_option() -> None:
    cu = ConfigUpdater()
    cu.read_string("[s]\\na = 1\\n")
    cu["s"]["b"] = "2"
    buf = StringIO()
    cu.write(buf)
    assert "b = 2" in buf.getvalue()
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        _forbidden_import_test("configupdater")
        + '''

from io import StringIO

from featurelifted import ConfigUpdater


def test_multiple_sections_roundtrip() -> None:
    text = "[a]\\nx=1\\n\\n[b]\\n# note\\ny=2\\n"
    cu = ConfigUpdater()
    cu.read_string(text)
    cu["b"]["y"].value = "9"
    buf = StringIO()
    cu.write(buf)
    out = buf.getvalue()
    assert "# note" in out
    assert "y = 9" in out
    assert "[a]" in out and "[b]" in out
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import ConfigUpdater


def test_required_api_surface() -> None:
    assert ConfigUpdater is not None
    cu = ConfigUpdater()
    assert hasattr(cu, "read_string") and hasattr(cu, "write")
''',
        encoding="utf-8",
    )
    metadata = w4_metadata(
        task_id,
        meta,
        feature={
            "name": "configupdater ini roundtrip",
            "description": "Adapted ConfigUpdater INI read/modify/write preserving comments.",
            "source_entrypoints": ["configupdater.ConfigUpdater"],
            "included_behaviors": [
                "read_string and section/option access",
                "write to StringIO preserving comments",
            ],
            "excluded_behaviors": ["interpolation beyond declared", "file path IO in tests"],
        },
        entanglement={
            "level": "medium",
            "types": ["config_environment_coupling"],
            "primary": "config_environment_coupling",
            "description": "INI AST mutation with comment-preserving serialization.",
            "signals": ["read_string", "write(fp)", "section/option"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import ConfigUpdater",
            "callable": "ConfigUpdater.read_string",
            "signature": "read_string(string: str) -> ConfigUpdater",
        },
        public_spec={
            "title": "configupdater ini roundtrip",
            "summary": "Extract a task-scoped subset of `ConfigUpdater` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.ConfigUpdater", "kind": "class"},
                {"path": "featurelifted.ConfigUpdater.read_string", "kind": "method"},
                {"path": "featurelifted.ConfigUpdater.write", "kind": "method", "signature": "(fp: TextIO, validate: bool = True)"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: read_string and section/option get/set. Required observable cases include read modify write stringio; section option access."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: write to StringIO preserves comments and spacing. Required observable cases include add option; multiple sections roundtrip."},
                {"id": "B003", "text": "Tests use ConfigUpdater.write(StringIO) rather than to_string()."},
                {"id": "B004", "text": "Mutable INI document supports multiple sections."},
                {"id": "B005", "text": "The package exposes ConfigUpdater with read_string/write with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: configupdater."},
            ],
            "exclusions": ["interpolation beyond declared", "original configupdater import at runtime"],
            "forbidden": {"imports": ["configupdater"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_flask_cors() -> Path:
    task_id = "flask_cors__cors_options_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    _install_flask_cors(ref)
    (task_dir / "requirements.lock").write_text(
        "Flask==3.0.3\nWerkzeug==3.0.3\nsix==1.16.0\n",
        encoding="utf-8",
    )
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("flask_cors\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "flask-cors",
            "required_source_files": ["flask_cors/flask_cors.py"],
            "runtime_dependencies": ["Flask", "six"],
            "notes": "Single-file flask_cors adapted as featurelifted; Flask test client only.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from flask import Flask

from featurelifted import CORS, cross_origin


def test_cors_app_headers() -> None:
    app = Flask(__name__)

    @app.route("/")
    def index():
        return "ok"

    CORS(app)
    client = app.test_client()
    resp = client.get("/", headers={"Origin": "http://example.com"})
    assert resp.status_code == 200
    assert resp.headers.get("Access-Control-Allow-Origin") in (
        "http://example.com",
        "*",
    )


def test_cross_origin_decorator() -> None:
    app = Flask(__name__)

    @app.route("/x")
    @cross_origin(origins="https://a.test")
    def x():
        return "x"

    client = app.test_client()
    resp = client.get("/x", headers={"Origin": "https://a.test"})
    assert resp.headers.get("Access-Control-Allow-Origin") == "https://a.test"
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        _forbidden_import_test("flask_cors")
        + '''

from flask import Flask

from featurelifted import CORS


def test_options_preflight() -> None:
    app = Flask(__name__)

    @app.route("/api", methods=["GET", "POST"])
    def api():
        return "data"

    CORS(app, methods=["GET", "POST"])
    client = app.test_client()
    resp = client.open(
        "/api",
        method="OPTIONS",
        headers={
            "Origin": "http://example.com",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert resp.status_code in {200, 204}
    assert "Access-Control-Allow-Methods" in resp.headers
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import CORS, cross_origin


def test_required_api_surface() -> None:
    assert CORS is not None and callable(cross_origin)
''',
        encoding="utf-8",
    )
    metadata = w4_metadata(
        task_id,
        meta,
        allowed_dependencies=["Flask", "Werkzeug", "six"],
        feature={
            "name": "flask-cors options",
            "description": "Adapted CORS(app) and cross_origin decorator for Flask.",
            "source_entrypoints": ["flask_cors.CORS", "flask_cors.cross_origin"],
            "included_behaviors": [
                "CORS(app) adds Access-Control-Allow-Origin on test client",
                "cross_origin decorator per-route origins",
                "OPTIONS preflight headers",
            ],
            "excluded_behaviors": ["real browsers", "network"],
        },
        entanglement={
            "level": "high",
            "types": ["framework_coupling"],
            "primary": "framework_coupling",
            "description": "Flask after_request hooks for CORS headers.",
            "signals": ["CORS", "cross_origin", "test client"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import CORS, cross_origin",
            "callable": "CORS",
            "signature": "CORS(app=None, **options)",
        },
        public_spec={
            "title": "flask-cors options",
            "summary": "Extract a task-scoped subset of `flask-cors` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.CORS", "kind": "class", "signature": "(app=None, **options)"},
                {"path": "featurelifted.cross_origin", "kind": "function", "signature": "(**options)"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: CORS(app) reflects Origin on GET responses. Required observable cases include cors app headers."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: cross_origin decorator sets per-route ACAO. Required observable cases include cross origin decorator."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: OPTIONS preflight exposes allowed methods. Required observable cases include options preflight."},
                {"id": "B004", "text": "Tests use Flask test client only; Flask is an allowed dependency."},
                {"id": "B005", "text": "The package exposes CORS and cross_origin with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: flask_cors."},
            ],
            "exclusions": ["real browsers", "original flask_cors import at runtime"],
            "forbidden": {"imports": ["flask_cors"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_freezegun() -> Path:
    task_id = "freezegun__freeze_time_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "freezegun")
    (task_dir / "requirements.lock").write_text(
        "python-dateutil==2.9.0.post0\n",
        encoding="utf-8",
    )
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("freezegun\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "freezegun",
            "required_source_files": ["freezegun/api.py", "freezegun/__init__.py"],
            "runtime_dependencies": ["python-dateutil"],
            "notes": "Adapted freeze_time context manager and decorator.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from datetime import datetime

from featurelifted import freeze_time


def test_freeze_context_manager() -> None:
    with freeze_time("2020-01-15 12:00:00"):
        assert datetime.now().year == 2020
        assert datetime.now().month == 1
        assert datetime.now().day == 15


def test_freeze_decorator() -> None:
    @freeze_time("2019-06-01")
    def stamped() -> int:
        return datetime.now().year

    assert stamped() == 2019


def test_unfrozen_after_context() -> None:
    real_year = datetime.now().year
    with freeze_time("2001-01-01"):
        assert datetime.now().year == 2001
    assert datetime.now().year == real_year
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        _forbidden_import_test("freezegun")
        + '''

from datetime import datetime, timedelta

from featurelifted import freeze_time


def test_tick_moves_time() -> None:
    with freeze_time("2020-01-01 00:00:00", tick=True) as frozen:
        t0 = datetime.now()
        frozen.tick(delta=timedelta(hours=1))
        t1 = datetime.now()
        assert t1 > t0
        assert t1.hour == 1


def test_move_to() -> None:
    with freeze_time("2020-01-01") as frozen:
        frozen.move_to("2021-12-25")
        assert datetime.now().year == 2021
        assert datetime.now().month == 12
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import freeze_time


def test_required_api_surface() -> None:
    assert callable(freeze_time)
''',
        encoding="utf-8",
    )
    metadata = w4_metadata(
        task_id,
        meta,
        allowed_dependencies=["python-dateutil"],
        feature={
            "name": "freezegun freeze time",
            "description": "Adapted freeze_time context manager/decorator with tick/move_to.",
            "source_entrypoints": ["freezegun.freeze_time"],
            "included_behaviors": [
                "freeze_time context manager and decorator",
                "tick and move_to on frozen clock",
            ],
            "excluded_behaviors": ["patching third-party C extension clocks"],
        },
        entanglement={
            "level": "medium",
            "types": ["config_environment_coupling"],
            "primary": "config_environment_coupling",
            "description": "Datetime patching must restore after context exit.",
            "signals": ["freeze_time", "tick", "move_to"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import freeze_time",
            "callable": "freeze_time",
            "signature": "freeze_time(time_to_freeze=None, tick: bool = False, ...)",
        },
        public_spec={
            "title": "freezegun freeze time",
            "summary": "Extract a task-scoped subset of `freezegun` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.freeze_time", "kind": "function", "signature": "(time_to_freeze=None, tick: bool = False, ...)"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: freeze_time context manager and decorator. Required observable cases include freeze context manager; freeze decorator; unfrozen after context."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: tick and move_to advance frozen time. Required observable cases include tick moves time; move to."},
                {"id": "B003", "text": "Real clock resumes after the freeze context exits."},
                {"id": "B004", "text": "python-dateutil is the only allowed third-party dependency."},
                {"id": "B005", "text": "The package exposes freeze_time with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: freezegun."},
            ],
            "exclusions": ["C extension clock patching", "original freezegun import at runtime"],
            "forbidden": {"imports": ["freezegun"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_furl() -> Path:
    task_id = "furl__url_mutate_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "furl")
    (task_dir / "requirements.lock").write_text(
        "orderedmultidict==1.0.1\nsix==1.16.0\n",
        encoding="utf-8",
    )
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("furl\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "furl",
            "required_source_files": ["furl/furl.py"],
            "runtime_dependencies": ["orderedmultidict", "six"],
            "notes": "Adapted furl URL/path/query mutation API.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import furl


def test_parse_and_mutate_path() -> None:
    u = furl("https://example.com/a/b")
    u.path.segments.append("c")
    assert "/a/b/c" in u.url


def test_query_args() -> None:
    u = furl("https://example.com/?a=1")
    u.args["b"] = "2"
    assert "a=1" in u.url and "b=2" in u.url


def test_set_scheme_host() -> None:
    u = furl("http://old.test/x")
    u.scheme = "https"
    u.host = "new.test"
    assert u.url.startswith("https://new.test/")
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        _forbidden_import_test("furl")
        + '''

from featurelifted import furl


def test_fragment_and_port() -> None:
    u = furl("https://example.com:8080/path#frag")
    u.port = 9090
    u.fragment = "updated"
    assert ":9090/" in u.url
    assert "#updated" in u.url


def test_remove_query_key() -> None:
    u = furl("https://x.test/?a=1&b=2")
    del u.args["a"]
    assert "a=" not in u.url
    assert "b=2" in u.url
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import furl


def test_required_api_surface() -> None:
    assert callable(furl)
    u = furl("https://example.com")
    assert hasattr(u, "url") and hasattr(u, "path") and hasattr(u, "args")
''',
        encoding="utf-8",
    )
    metadata = w4_metadata(
        task_id,
        meta,
        allowed_dependencies=["orderedmultidict", "six"],
        feature={
            "name": "furl url mutate",
            "description": "Adapted furl mutable URL/path/query API.",
            "source_entrypoints": ["furl.furl"],
            "included_behaviors": [
                "parse and mutate path segments",
                "query args set/remove",
                "scheme/host/port/fragment updates",
            ],
            "excluded_behaviors": ["network fetch"],
        },
        entanglement={
            "level": "medium",
            "types": ["data_model_coupling"],
            "primary": "data_model_coupling",
            "description": "Mutable URL composed of path/query/fragment parts.",
            "signals": ["furl.url", "path.segments", "args"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import furl",
            "callable": "furl",
            "signature": "furl(url: str = '')",
        },
        public_spec={
            "title": "furl url mutate",
            "summary": "Extract a task-scoped subset of `furl` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.furl", "kind": "class", "signature": "(url: str = '')"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: parse and mutate path/query. Required observable cases include parse and mutate path; query args."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: scheme/host/port/fragment mutation. Required observable cases include set scheme host; fragment and port."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: remove query keys. Required observable cases include remove query key."},
                {"id": "B004", "text": "furl.url returns the serialized URL string."},
                {"id": "B005", "text": "The package exposes furl with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: furl."},
            ],
            "exclusions": ["network fetch", "original furl import at runtime"],
            "forbidden": {"imports": ["furl"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_hyperlink() -> Path:
    task_id = "hyperlink__url_parse_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "hyperlink")
    (task_dir / "requirements.lock").write_text("# no third-party dependencies\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("hyperlink\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "hyperlink",
            "required_source_files": ["src/hyperlink/_url.py", "src/hyperlink/__init__.py"],
            "runtime_dependencies": [],
            "notes": "Adapted URL.from_text/replace/click/to_text immutable API.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import URL


def test_from_text_and_to_text() -> None:
    url = URL.from_text("https://example.com/a/b?x=1#frag")
    text = url.to_text()
    assert text.startswith("https://example.com/")
    assert "x=1" in text
    assert "#frag" in text


def test_replace_scheme_host() -> None:
    url = URL.from_text("http://old.test/path")
    updated = url.replace(scheme="https", host="new.test")
    assert updated.to_text().startswith("https://new.test")


def test_click_relative() -> None:
    base = URL.from_text("https://example.com/a/b/")
    clicked = base.click("../c")
    assert "/a/c" in clicked.to_text() or clicked.to_text().endswith("/a/c")
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        _forbidden_import_test("hyperlink")
        + '''

from featurelifted import URL, URLParseError


def test_immutable_replace() -> None:
    original = URL.from_text("https://example.com/x")
    changed = original.replace(path=["y"])
    assert original.to_text().endswith("/x")
    assert changed.to_text().endswith("/y")


def test_parse_error() -> None:
    try:
        URL.from_text("http://[::1/")
        assert False, "expected URLParseError"
    except URLParseError:
        pass
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import URL, URLParseError


def test_required_api_surface() -> None:
    assert URL is not None and URLParseError is not None
    assert hasattr(URL, "from_text")
    url = URL.from_text("https://example.com")
    assert callable(url.to_text) and callable(url.replace) and callable(url.click)
''',
        encoding="utf-8",
    )
    metadata = w4_metadata(
        task_id,
        meta,
        feature={
            "name": "hyperlink url parse",
            "description": "Adapted hyperlink.URL from_text/replace/click/to_text.",
            "source_entrypoints": ["hyperlink.URL"],
            "included_behaviors": [
                "URL.from_text and to_text",
                "immutable replace for scheme/host/path",
                "click relative resolution",
            ],
            "excluded_behaviors": ["network resolve"],
        },
        entanglement={
            "level": "medium",
            "types": ["data_model_coupling"],
            "primary": "data_model_coupling",
            "description": "Immutable URL value object with structural sharing.",
            "signals": ["from_text", "replace", "click"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import URL",
            "callable": "URL.from_text",
            "signature": "from_text(text: str) -> URL",
        },
        public_spec={
            "title": "hyperlink url parse",
            "summary": "Extract a task-scoped subset of `hyperlink` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.URL", "kind": "class"},
                {"path": "featurelifted.URL.from_text", "kind": "method"},
                {"path": "featurelifted.URL.replace", "kind": "method"},
                {"path": "featurelifted.URL.click", "kind": "method"},
                {"path": "featurelifted.URL.to_text", "kind": "method"},
                {"path": "featurelifted.URLParseError", "kind": "exception"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: URL.from_text and to_text roundtrip fields. Required observable cases include from text and to text; replace scheme host."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: click resolves relative refs. Required observable cases include click relative."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: replace returns new URL without mutating original. Required observable cases include immutable replace."},
                {"id": "B004", "text": "URLParseError is raised on malformed authority segments."},
                {"id": "B005", "text": "The package exposes URL/URLParseError with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: hyperlink."},
            ],
            "exclusions": ["network resolve", "original hyperlink import at runtime"],
            "forbidden": {"imports": ["hyperlink"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_ijson() -> Path:
    task_id = "ijson__event_parse_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "ijson")
    _force_ijson_python_backend(ref)
    (task_dir / "requirements.lock").write_text("# no third-party dependencies\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("ijson\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "ijson",
            "required_source_files": ["src/ijson/__init__.py", "src/ijson/backends/python.py"],
            "runtime_dependencies": [],
            "notes": "Adapted parse/items with pure python backend forced.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from io import BytesIO

from featurelifted import items, parse


def test_parse_events() -> None:
    data = BytesIO(b'{"a": 1, "b": [2, 3]}')
    events = list(parse(data))
    assert ("", "map_key", "a") in events
    assert any(ev[1] == "number" for ev in events)


def test_items_object() -> None:
    data = BytesIO(b'{"x": {"y": 9}}')
    found = list(items(data, "x"))
    assert found == [{"y": 9}]


def test_items_array() -> None:
    data = BytesIO(b'{"arr": [1, 2]}')
    assert list(items(data, "arr.item")) == [1, 2]
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        _forbidden_import_test("ijson")
        + '''

from io import BytesIO

from featurelifted import IncompleteJSONError, items, kvitems, parse


def test_kvitems() -> None:
    data = BytesIO(b'{"a": 1, "b": 2}')
    pairs = dict(kvitems(data, ""))
    assert pairs == {"a": 1, "b": 2}


def test_incomplete_json() -> None:
    data = BytesIO(b'{"a":')
    try:
        list(parse(data))
        assert False, "expected IncompleteJSONError"
    except IncompleteJSONError:
        pass
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import IncompleteJSONError, items, kvitems, parse


def test_required_api_surface() -> None:
    assert callable(parse) and callable(items) and callable(kvitems)
    assert IncompleteJSONError is not None
''',
        encoding="utf-8",
    )
    metadata = w4_metadata(
        task_id,
        meta,
        feature={
            "name": "ijson event parse",
            "description": "Adapted ijson parse/items/kvitems with python backend.",
            "source_entrypoints": ["ijson.parse", "ijson.items"],
            "included_behaviors": [
                "parse yields (prefix, event, value) tuples from BytesIO",
                "items/kvitems decode nested values",
                "IncompleteJSONError on truncated JSON",
            ],
            "excluded_behaviors": ["yajl C backend requirement"],
        },
        entanglement={
            "level": "medium",
            "types": ["parser_state_coupling"],
            "primary": "parser_state_coupling",
            "description": "Incremental JSON event stream parsing.",
            "signals": ["parse events", "items prefix", "python backend"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import parse, items",
            "callable": "parse",
            "signature": "parse(file_or_bytes) -> iterator",
        },
        public_spec={
            "title": "ijson event parse",
            "summary": "Extract a task-scoped subset of `ijson` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.parse", "kind": "function"},
                {"path": "featurelifted.items", "kind": "function"},
                {"path": "featurelifted.kvitems", "kind": "function"},
                {"path": "featurelifted.IncompleteJSONError", "kind": "exception"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: parse emits map/number events from BytesIO JSON. Required observable cases include parse events."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: items decodes nested objects and arrays. Required observable cases include items object; items array."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: kvitems and IncompleteJSONError. Required observable cases include kvitems; incomplete json."},
                {"id": "B004", "text": "Pure python backend is used for portability (no yajl)."},
                {"id": "B005", "text": "The package exposes parse/items/kvitems/IncompleteJSONError with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: ijson."},
            ],
            "exclusions": ["yajl C backend", "original ijson import at runtime"],
            "forbidden": {"imports": ["ijson"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_jsonpickle() -> Path:
    task_id = "jsonpickle__handler_roundtrip_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "jsonpickle")
    (task_dir / "requirements.lock").write_text("# no third-party dependencies\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("jsonpickle\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "jsonpickle",
            "required_source_files": [
                "jsonpickle/pickler.py",
                "jsonpickle/unpickler.py",
                "jsonpickle/handlers.py",
            ],
            "runtime_dependencies": [],
            "notes": "Adapted encode/decode with custom handler registration.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import decode, encode, register
from featurelifted.handlers import BaseHandler


class Point:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


class PointHandler(BaseHandler):
    def flatten(self, obj, data):
        data["x"] = obj.x
        data["y"] = obj.y
        return data

    def restore(self, data):
        return Point(data["x"], data["y"])


def test_encode_decode_builtin() -> None:
    payload = {"a": [1, 2], "b": "x"}
    assert decode(encode(payload)) == payload


def test_custom_handler_roundtrip() -> None:
    register(Point, PointHandler)
    p = Point(3, 4)
    restored = decode(encode(p))
    assert isinstance(restored, Point)
    assert restored.x == 3 and restored.y == 4
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        _forbidden_import_test("jsonpickle")
        + '''

from featurelifted import decode, encode


def test_unpicklable_false_dict_mode() -> None:
    class Thing:
        def __init__(self, name: str) -> None:
            self.name = name

    blob = encode(Thing("Ada"), unpicklable=False)
    data = decode(blob)
    assert data["name"] == "Ada"
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import decode, encode, register
from featurelifted.handlers import BaseHandler


def test_required_api_surface() -> None:
    assert callable(encode) and callable(decode) and callable(register)
    assert BaseHandler is not None
''',
        encoding="utf-8",
    )
    metadata = w4_metadata(
        task_id,
        meta,
        feature={
            "name": "jsonpickle handler roundtrip",
            "description": "Adapted jsonpickle encode/decode with handler registration.",
            "source_entrypoints": ["jsonpickle.encode", "jsonpickle.decode", "jsonpickle.register"],
            "included_behaviors": [
                "encode/decode roundtrip for dicts",
                "register custom BaseHandler for classes",
                "unpicklable=False dict mode",
            ],
            "excluded_behaviors": ["numpy/pandas backends"],
        },
        entanglement={
            "level": "medium",
            "types": ["data_model_coupling"],
            "primary": "data_model_coupling",
            "description": "Global handler registry composes with encode/decode.",
            "signals": ["register", "BaseHandler", "unpicklable"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import encode, decode, register",
            "callable": "encode",
            "signature": "encode(obj, unpicklable: bool = True, make_refs: bool = True) -> str",
        },
        public_spec={
            "title": "jsonpickle handler roundtrip",
            "summary": "Extract a task-scoped subset of `jsonpickle` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.encode", "kind": "function"},
                {"path": "featurelifted.decode", "kind": "function"},
                {"path": "featurelifted.register", "kind": "function"},
                {"path": "featurelifted.handlers.BaseHandler", "kind": "class"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: encode/decode roundtrip for dict payloads. Required observable cases include encode decode builtin."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: register BaseHandler restores custom classes. Required observable cases include custom handler roundtrip."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: unpicklable=False yields dict snapshots. Required observable cases include unpicklable false dict mode."},
                {"id": "B004", "text": "Handler registry is global; tests register handlers explicitly."},
                {"id": "B005", "text": "The package exposes encode/decode/register/BaseHandler with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: jsonpickle."},
            ],
            "exclusions": ["numpy/pandas backends", "original jsonpickle import at runtime"],
            "forbidden": {"imports": ["jsonpickle"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_packageurl() -> Path:
    task_id = "packageurl__purl_parse_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "packageurl")
    (task_dir / "requirements.lock").write_text("# no third-party dependencies\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("packageurl\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "packageurl-python",
            "required_source_files": ["src/packageurl/__init__.py"],
            "runtime_dependencies": [],
            "notes": "Adapted PackageURL.from_string/to_string.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import PackageURL


def test_from_string_fields() -> None:
    purl = PackageURL.from_string("pkg:npm/%40scope/foo@1.2.3?a=b#section")
    assert purl.type == "npm"
    assert purl.namespace == "@scope"
    assert purl.name == "foo"
    assert purl.version == "1.2.3"


def test_to_string_roundtrip() -> None:
    original = "pkg:pypi/django@4.2.0"
    purl = PackageURL.from_string(original)
    assert purl.to_string() == original


def test_constructor() -> None:
    purl = PackageURL(type="gem", name="rails", version="7.0.0")
    assert "pkg:gem/rails@7.0.0" == purl.to_string()
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        _forbidden_import_test("packageurl")
        + '''

import pytest
from featurelifted import PackageURL


def test_qualifiers_normalize() -> None:
    purl = PackageURL.from_string("pkg:nuget/Newtonsoft.Json@13.0.1?arch=x86&os=windows")
    text = purl.to_string()
    assert "arch=x86" in text and "os=windows" in text


def test_invalid_purl() -> None:
    with pytest.raises(ValueError):
        PackageURL.from_string("not-a-purl")
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import PackageURL


def test_required_api_surface() -> None:
    assert PackageURL is not None
    assert callable(PackageURL.from_string)
    purl = PackageURL(type="generic", name="x")
    assert callable(purl.to_string)
''',
        encoding="utf-8",
    )
    metadata = w4_metadata(
        task_id,
        meta,
        feature={
            "name": "packageurl purl parse",
            "description": "Adapted PackageURL.from_string/to_string normalize.",
            "source_entrypoints": ["packageurl.PackageURL"],
            "included_behaviors": [
                "from_string parses type/namespace/name/version",
                "to_string roundtrip and qualifier ordering",
                "ValueError on invalid purl",
            ],
            "excluded_behaviors": ["ecosystem network lookups"],
        },
        entanglement={
            "level": "low",
            "types": ["data_model_coupling"],
            "primary": "data_model_coupling",
            "description": "PURL value object parse/serialize.",
            "signals": ["from_string", "to_string", "qualifiers"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import PackageURL",
            "callable": "PackageURL.from_string",
            "signature": "from_string(purl: str) -> PackageURL",
        },
        public_spec={
            "title": "packageurl purl parse",
            "summary": "Extract a task-scoped subset of `packageurl` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.PackageURL", "kind": "class"},
                {"path": "featurelifted.PackageURL.from_string", "kind": "method"},
                {"path": "featurelifted.PackageURL.to_string", "kind": "method"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: from_string exposes type/namespace/name/version. Required observable cases include from string fields; constructor."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: to_string roundtrips canonical purls. Required observable cases include to string roundtrip; qualifiers normalize."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: invalid purls raise ValueError. Required observable cases include invalid purl."},
                {"id": "B004", "text": "Qualifiers are serialized in stable order."},
                {"id": "B005", "text": "The package exposes PackageURL.from_string/to_string with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: packageurl."},
            ],
            "exclusions": ["ecosystem network lookups", "original packageurl import at runtime"],
            "forbidden": {"imports": ["packageurl"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_pyjwt() -> Path:
    task_id = "pyjwt__encode_decode_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "jwt")
    _fix_jwt_local_var_rewrites(ref)
    (task_dir / "requirements.lock").write_text(
        "PyJWT[crypto]==2.13.0\ncryptography==43.0.3\n",
        encoding="utf-8",
    )
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("jwt\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "PyJWT",
            "required_source_files": ["jwt/api_jwt.py", "jwt/exceptions.py"],
            "runtime_dependencies": ["PyJWT", "cryptography"],
            "notes": "Adapted jwt encode/decode HS256 with crypto extra.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

import time

from featurelifted import decode, encode
from featurelifted.exceptions import ExpiredSignatureError, InvalidSignatureError


def test_encode_decode_hs256() -> None:
    token = encode({"sub": "user1"}, "secret", algorithm="HS256")
    payload = decode(token, "secret", algorithms=["HS256"])
    assert payload["sub"] == "user1"


def test_wrong_secret() -> None:
    token = encode({"a": 1}, "k", algorithm="HS256")
    try:
        decode(token, "wrong", algorithms=["HS256"])
        assert False, "expected InvalidSignatureError"
    except InvalidSignatureError:
        pass


def test_expired_token() -> None:
    token = encode({"exp": int(time.time()) - 10}, "k", algorithm="HS256")
    try:
        decode(token, "k", algorithms=["HS256"])
        assert False, "expected ExpiredSignatureError"
    except ExpiredSignatureError:
        pass
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        _forbidden_import_test("jwt")
        + '''

from featurelifted import decode, encode
from featurelifted.exceptions import InvalidTokenError


def test_custom_header() -> None:
    token = encode({"x": 1}, "k", algorithm="HS256", headers={"kid": "1"})
    payload = decode(token, "k", algorithms=["HS256"])
    assert payload["x"] == 1


def test_invalid_token_error_base() -> None:
    assert issubclass(InvalidTokenError, Exception)
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import decode, encode
from featurelifted.exceptions import ExpiredSignatureError, InvalidSignatureError, InvalidTokenError


def test_required_api_surface() -> None:
    assert callable(encode) and callable(decode)
    assert InvalidTokenError is not None
    assert ExpiredSignatureError is not None and InvalidSignatureError is not None
''',
        encoding="utf-8",
    )
    metadata = w4_metadata(
        task_id,
        meta,
        allowed_dependencies=["PyJWT", "cryptography"],
        feature={
            "name": "pyjwt encode decode",
            "description": "Adapted PyJWT encode/decode HS256 with crypto.",
            "source_entrypoints": ["jwt.encode", "jwt.decode"],
            "included_behaviors": [
                "encode/decode HS256",
                "InvalidSignatureError and ExpiredSignatureError",
            ],
            "excluded_behaviors": ["JWKS fetch", "asymmetric algorithms beyond HS256 tests"],
        },
        entanglement={
            "level": "medium",
            "types": ["data_model_coupling"],
            "primary": "data_model_coupling",
            "description": "JWT signing/verification with shared secret.",
            "signals": ["HS256", "exp claim", "InvalidSignatureError"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import encode, decode",
            "callable": "encode",
            "signature": "encode(payload: dict, key: str, algorithm: str = 'HS256', headers: dict | None = None) -> str",
        },
        public_spec={
            "title": "pyjwt encode decode",
            "summary": "Extract a task-scoped subset of `PyJWT` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.encode", "kind": "function"},
                {"path": "featurelifted.decode", "kind": "function"},
                {"path": "featurelifted.exceptions.InvalidTokenError", "kind": "exception"},
                {"path": "featurelifted.exceptions.InvalidSignatureError", "kind": "exception"},
                {"path": "featurelifted.exceptions.ExpiredSignatureError", "kind": "exception"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: encode/decode HS256 roundtrip. Required observable cases include encode decode hs256."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: wrong secret and expired tokens raise signature/expiry errors. Required observable cases include wrong secret; expired token."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: optional headers and InvalidTokenError hierarchy. Required observable cases include custom header; invalid token error base."},
                {"id": "B004", "text": "cryptography is required for HS256 via PyJWT[crypto]."},
                {"id": "B005", "text": "The package exposes encode/decode and JWT exceptions with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: jwt."},
            ],
            "exclusions": ["JWKS fetch", "original jwt import at runtime"],
            "forbidden": {"imports": ["jwt"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_python_crontab() -> Path:
    task_id = "python_crontab__cron_item_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    _install_python_crontab(ref)
    (task_dir / "requirements.lock").write_text("# no third-party dependencies\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("crontab\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "python-crontab",
            "required_source_files": ["crontab.py", "crontabs.py", "cronlog.py"],
            "runtime_dependencies": [],
            "notes": "Wheel flat modules for CronSlices/CronItem without system crontab IO.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import CronItem, CronSlices


def test_cron_slices_valid() -> None:
    assert CronSlices.is_valid("* * * * *")
    slices = CronSlices("* * * * *")
    assert slices.render().startswith("*")


def test_cron_item_from_line() -> None:
    item = CronItem("* * * * * /bin/echo hi")
    assert item.is_valid()
    rendered = item.render()
    assert "/bin/echo" in rendered or "echo" in rendered
    assert item.is_enabled()


def test_cron_item_invalid_line() -> None:
    assert not CronSlices.is_valid("not five fields")
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        _forbidden_import_test("crontab")
        + '''

from featurelifted import CronItem, CronSlices


def test_slices_setall() -> None:
    slices = CronSlices()
    slices.setall("0", "12", "*", "*", "1")
    assert "0" in slices.render() and "12" in slices.render()


def test_special_reboot() -> None:
    slices = CronSlices("@reboot")
    assert "@reboot" in slices.render() or slices.special == "@reboot"
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import CronItem, CronSlices


def test_required_api_surface() -> None:
    assert CronItem is not None and CronSlices is not None
    assert callable(CronSlices.is_valid)
    item = CronItem("* * * * * true")
    assert callable(item.render) and callable(item.is_valid)
''',
        encoding="utf-8",
    )
    metadata = w4_metadata(
        task_id,
        meta,
        feature={
            "name": "python-crontab cron item",
            "description": "Adapted CronSlices/CronItem parse/render/validity.",
            "source_entrypoints": ["crontab.CronSlices", "crontab.CronItem"],
            "included_behaviors": [
                "CronSlices parse/render/is_valid",
                "CronItem constructor render/is_valid",
                "special @reboot handling",
            ],
            "excluded_behaviors": ["reading user crontabs from OS", "CronTab file IO"],
        },
        entanglement={
            "level": "medium",
            "types": ["parser_state_coupling"],
            "primary": "parser_state_coupling",
            "description": "Cron line parse into slices + command render.",
            "signals": ["CronSlices", "CronItem.render", "is_valid"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import CronItem, CronSlices",
            "callable": "CronItem",
            "signature": "CronItem(line: str)",
        },
        public_spec={
            "title": "python-crontab cron item",
            "summary": "Extract a task-scoped subset of `python-crontab` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.CronSlices", "kind": "class"},
                {"path": "featurelifted.CronSlices.is_valid", "kind": "method"},
                {"path": "featurelifted.CronItem", "kind": "class"},
                {"path": "featurelifted.CronItem.render", "kind": "method"},
                {"path": "featurelifted.CronItem.is_valid", "kind": "method"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: CronSlices parse/render/is_valid. Required observable cases include cron slices valid; slices setall."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: CronItem constructor render/is_valid. Required observable cases include cron item from line; cron item invalid line."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: special @reboot slices. Required observable cases include special reboot."},
                {"id": "B004", "text": "No OS crontab file access is required."},
                {"id": "B005", "text": "The package exposes CronSlices/CronItem with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: crontab."},
            ],
            "exclusions": ["OS crontab file IO", "original crontab import at runtime"],
            "forbidden": {"imports": ["crontab"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


BUILDERS: dict[str, Callable[[], Path]] = {
    "cloudpickle__dumps_loads_core__001": materialize_cloudpickle,
    "configupdater__ini_roundtrip_core__001": materialize_configupdater,
    "flask_cors__cors_options_core__001": materialize_flask_cors,
    "freezegun__freeze_time_core__001": materialize_freezegun,
    "furl__url_mutate_core__001": materialize_furl,
    "hyperlink__url_parse_core__001": materialize_hyperlink,
    "ijson__event_parse_core__001": materialize_ijson,
    "jsonpickle__handler_roundtrip_core__001": materialize_jsonpickle,
    "packageurl__purl_parse_core__001": materialize_packageurl,
    "pyjwt__encode_decode_core__001": materialize_pyjwt,
    "python_crontab__cron_item_core__001": materialize_python_crontab,
}


def main(argv: list[str]) -> int:
    targets = argv[1:] or list(BUILDERS)
    for task_id in targets:
        if task_id not in BUILDERS:
            print(f"unknown/not-yet-supported: {task_id}", file=sys.stderr)
            return 1
        path = BUILDERS[task_id]()
        print(f"materialized {task_id} -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

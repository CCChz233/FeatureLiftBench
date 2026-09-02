#!/usr/bin/env python3
"""Materialize External-50 W3 tasks into benchmark/staging/."""

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


def _prepare(task_id: str, meta: dict[str, Any]) -> Path:
    task_dir = STAGING / task_id
    if task_dir.exists():
        shutil.rmtree(task_dir)
    task_dir.mkdir(parents=True)
    shutil.copytree(
        meta["src"],
        task_dir / "repo",
        ignore=shutil.ignore_patterns(
            "__pycache__", "*.pyc", ".flb_pin", "*.tar.gz", "wheels", ".git"
        ),
    )
    (task_dir / "evaluation").mkdir(parents=True)
    (task_dir / "public_tests").mkdir()
    (task_dir / "hidden_tests").mkdir()
    return task_dir


def _w3_metadata(task_id: str, meta: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    metadata = base_metadata(task_id, meta, **kwargs)
    metadata["tags"] = ["external50", "w3", meta["lift"].lower(), meta["forbidden"]]
    return metadata


def _forbidden_surface_test(forbidden: str) -> str:
    return f'''

def test_no_upstream_import_surface() -> None:
    import re
    from pathlib import Path
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(
        rf"^\\s*(?:from {re.escape(forbidden)}\\b|import {re.escape(forbidden)}\\b)",
        re.MULTILINE,
    )
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
'''


PINS: dict[str, dict[str, Any]] = {
    "boolean_py__expr_simplify_core__001": {
        "package": "boolean.py",
        "url": "https://github.com/bastikr/boolean.py",
        "commit": "8a443837e68dc027004294fb17fe1857cf783410",
        "tag": "v5.0",
        "license": "BSD-2-Clause",
        "license_path": "LICENSE.txt",
        "src": PIN_ROOT / "boolean_py",
        "forbidden": "boolean",
        "lift": "Composite",
        "pkg_dir": lambda: PIN_ROOT / "boolean_py" / "boolean",
    },
    "dill__serialize_settings_core__001": {
        "package": "dill",
        "url": "https://github.com/uqfoundation/dill",
        "commit": "d33477195e0433b5add1c16e4ea7c54747b2feaa",
        "tag": "dill-0.3.7",
        "license": "BSD-3-Clause",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "dill",
        "forbidden": "dill",
        "lift": "Adapted",
        "pkg_dir": lambda: PIN_ROOT / "dill" / "dill",
    },
    "huey__task_schedule_core__001": {
        "package": "huey",
        "url": "https://github.com/coleifer/huey",
        "commit": "e3b1d8a8f1fb7423186095698f0668df76b50bfd",
        "tag": "3.3.2",
        "license": "MIT",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "huey",
        "forbidden": "huey",
        "lift": "Composite",
        "pkg_dir": lambda: PIN_ROOT / "huey" / "huey",
    },
    "icalendar__component_roundtrip_core__001": {
        "package": "icalendar",
        "url": "https://github.com/collective/icalendar",
        "commit": "ad87bcf719fde8088a77c724bc2ae8f09545e0e4",
        "tag": "v7.2.2",
        "license": "BSD-2-Clause",
        "license_path": "LICENSE.rst",
        "src": PIN_ROOT / "icalendar",
        "forbidden": "icalendar",
        "lift": "Composite",
        "pkg_dir": lambda: PIN_ROOT / "icalendar" / "src" / "icalendar",
    },
    "invoke__collection_context_core__001": {
        "package": "invoke",
        "url": "https://github.com/pyinvoke/invoke",
        "commit": "ab836f911f7304dcab7653c0068a8327137161a7",
        "tag": "3.0.3",
        "license": "BSD-2-Clause",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "invoke",
        "forbidden": "invoke",
        "lift": "Composite",
        "pkg_dir": lambda: PIN_ROOT / "invoke" / "invoke",
    },
    "joserfc__jwt_claims_core__001": {
        "package": "joserfc",
        "url": "https://github.com/authlib/joserfc",
        "commit": "7facdee77fc8735ad88e586b31c5b0c940ee0a78",
        "tag": "1.7.4",
        "license": "BSD-3-Clause",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "joserfc",
        "forbidden": "joserfc",
        "lift": "Composite",
        "pkg_dir": lambda: PIN_ROOT / "joserfc" / "src" / "joserfc",
    },
    "python_json_logger__json_formatter_core__001": {
        "package": "python-json-logger",
        "url": "https://github.com/nhairs/python-json-logger",
        "commit": "d80c68da770154d9662975b789cabcc9a3e99408",
        "tag": "v4.1.0",
        "license": "BSD-2-Clause",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "python_json_logger",
        "forbidden": "pythonjsonlogger",
        "lift": "Adapted",
        "pkg_dir": lambda: PIN_ROOT / "python_json_logger" / "src" / "pythonjsonlogger",
    },
    "tldextract__suffix_resolve_core__001": {
        "package": "tldextract",
        "url": "https://github.com/john-kurkowski/tldextract",
        "commit": "361f12febf901ef48215d0380551d86c7f0608ac",
        "tag": "5.3.1",
        "license": "BSD-3-Clause",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "tldextract",
        "forbidden": "tldextract",
        "lift": "Composite",
        "pkg_dir": lambda: PIN_ROOT / "tldextract" / "tldextract",
    },
    "vcrpy__cassette_match_core__001": {
        "package": "vcrpy",
        "url": "https://github.com/kevin1024/vcrpy",
        "commit": "c599974b31f3e510df9b98e61513fe6889a50db0",
        "tag": "v8.3.0",
        "license": "MIT",
        "license_path": "LICENSE.txt",
        "src": PIN_ROOT / "vcrpy",
        "forbidden": "vcr",
        "lift": "Composite",
        "pkg_dir": lambda: PIN_ROOT / "vcrpy" / "vcr",
    },
}


def materialize_boolean_py() -> Path:
    task_id = "boolean_py__expr_simplify_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "boolean")
    (task_dir / "requirements.lock").write_text("# no third-party dependencies\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("boolean\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "boolean",
            "required_source_files": ["boolean/boolean.py", "boolean/__init__.py"],
            "runtime_dependencies": [],
            "notes": "Composite BooleanAlgebra.parse + expression.simplify/subs (not algebra.simplify).",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import BooleanAlgebra


def test_parse_and_simplify() -> None:
    algebra = BooleanAlgebra()
    expr = algebra.parse("a & b | ~c")
    simplified = expr.simplify()
    assert simplified == algebra.parse("~c | (a & b)") or str(simplified) == "~c|(a&b)"


def test_subs() -> None:
    algebra = BooleanAlgebra()
    a_sym = algebra.Symbol("a")
    expr = algebra.parse("a & b | ~c")
    subbed = expr.subs({a_sym: algebra.TRUE}, simplify=True)
    assert subbed == algebra.parse("b | ~c") or str(subbed) == "b|~c"


def test_equality() -> None:
    algebra = BooleanAlgebra()
    left = algebra.parse("a | b")
    right = algebra.parse("b | a")
    assert left.simplify() == right.simplify()
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

from featurelifted import BooleanAlgebra, ParseError


def test_parse_error() -> None:
    algebra = BooleanAlgebra()
    try:
        algebra.parse("a &")
        assert False, "expected ParseError"
    except ParseError:
        pass


def test_not_and_constants() -> None:
    algebra = BooleanAlgebra()
    expr = algebra.parse("~TRUE")
    assert expr.simplify() == algebra.FALSE


def test_symbol_roundtrip() -> None:
    algebra = BooleanAlgebra()
    sym = algebra.Symbol("x")
    expr = algebra.parse("x")
    assert expr.subs({sym: algebra.TRUE}) == algebra.TRUE
'''
        + _forbidden_surface_test("boolean"),
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import BooleanAlgebra, ParseError, Symbol


def test_required_api_surface() -> None:
    algebra = BooleanAlgebra()
    assert callable(algebra.parse)
    assert callable(algebra.Symbol)
    assert Symbol is not None and ParseError is not None
''',
        encoding="utf-8",
    )
    metadata = _w3_metadata(
        task_id,
        meta,
        feature={
            "name": "boolean parse simplify",
            "description": "Composite boolean.py BooleanAlgebra.parse + expression.simplify/subs.",
            "source_entrypoints": ["boolean.BooleanAlgebra", "boolean.Expression.simplify"],
            "included_behaviors": [
                "parse boolean expressions",
                "expression.simplify algebraic rewrite",
                "expression.subs substitution",
            ],
            "excluded_behaviors": ["SAT solvers", "algebra.simplify entrypoint"],
        },
        entanglement={
            "level": "medium",
            "types": ["parser_state_coupling"],
            "primary": "parser_state_coupling",
            "description": "Parse tree and algebraic rewrite compose.",
            "signals": ["BooleanAlgebra.parse", "simplify", "subs"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import BooleanAlgebra",
            "callable": "BooleanAlgebra.parse",
            "signature": "parse(expr: str)",
        },
        public_spec={
            "title": "boolean parse simplify",
            "summary": "Extract a task-scoped subset of `boolean.py` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.BooleanAlgebra", "kind": "class"},
                {"path": "featurelifted.BooleanAlgebra.parse", "kind": "method"},
                {"path": "featurelifted.ParseError", "kind": "class"},
                {"path": "featurelifted.Symbol", "kind": "class"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: parse and simplify boolean expressions. Required observable cases include parse and simplify."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: expression.subs with simplify. Required observable cases include subs."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: simplified equality and ParseError on bad input. Required observable cases include equality; parse error."},
                {"id": "B004", "text": "NOT/TRUE/FALSE constants simplify as upstream."},
                {"id": "B005", "text": "The package exposes BooleanAlgebra/parse/ParseError/Symbol with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: boolean."},
            ],
            "exclusions": ["SAT solvers", "original boolean import at runtime"],
            "forbidden": {"imports": ["boolean"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_dill() -> Path:
    task_id = "dill__serialize_settings_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "dill")
    init_path = ref / "__init__.py"
    init_path.write_text(
        init_path.read_text(encoding="utf-8").replace(
            """try: # the package is installed
    from .__info__ import __version__, __author__, __doc__, __license__
except: # pragma: no cover
    import os
    import sys
    parent = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
    sys.path.append(parent)
    # get distribution meta info
    from version import (__version__, __author__,
                         get_license_text, get_readme_as_rst)
    __license__ = get_license_text(os.path.join(parent, 'LICENSE'))
    __license__ = "\\n%s" % __license__
    __doc__ = get_readme_as_rst(os.path.join(parent, 'README.md'))
    del os, sys, parent, get_license_text, get_readme_as_rst""",
            '__version__ = "0.3.7"\n__author__ = "Mike McKerns"\n'
            '__license__ = "BSD-3-Clause"\n__doc__ = "dill"\n',
        ),
        encoding="utf-8",
    )
    (task_dir / "requirements.lock").write_text("# no third-party dependencies\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("dill\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "dill",
            "required_source_files": ["dill/_dill.py", "dill/settings.py"],
            "runtime_dependencies": [],
            "notes": "Adapted dill dumps/loads with settings facade.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import dumps, loads


def test_function_roundtrip() -> None:
    def add(x: int) -> int:
        return x + 1

    restored = loads(dumps(add))
    assert restored(3) == 4


def test_lambda_roundtrip() -> None:
    fn = lambda x: x * 2  # noqa: E731
    assert loads(dumps(fn))(5) == 10


def test_settings_exposed() -> None:
    from featurelifted import settings

    assert settings is not None
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

from featurelifted import dumps, loads


def test_recurse_flag() -> None:
    fn = lambda x: x + 1  # noqa: E731
    payload = dumps(fn, recurse=True)
    assert loads(payload)(2) == 3


def test_nested_function() -> None:
    def outer():
        def inner(y):
            return y + 10

        return inner

    restored = loads(dumps(outer()))
    assert restored(5) == 15
'''
        + _forbidden_surface_test("dill"),
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import dumps, loads, settings


def test_required_api_surface() -> None:
    assert callable(dumps) and callable(loads)
    assert settings is not None
''',
        encoding="utf-8",
    )
    metadata = _w3_metadata(
        task_id,
        meta,
        feature={
            "name": "dill serialize settings",
            "description": "Adapted dill dumps/loads with settings module.",
            "source_entrypoints": ["dill.dumps", "dill.loads", "dill.settings"],
            "included_behaviors": [
                "dumps/loads roundtrip for functions and lambdas",
                "recurse flag",
                "settings module exposed",
            ],
            "excluded_behaviors": ["interactive session dump tricks", "undetected objects"],
        },
        entanglement={
            "level": "medium",
            "types": ["data_model_coupling"],
            "primary": "data_model_coupling",
            "description": "Pickle-compatible API with dill settings flags.",
            "signals": ["dumps", "loads", "settings"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import dumps, loads, settings",
            "callable": "dumps",
            "signature": "dumps(obj, protocol=None, byref=None, fmode=None, recurse=None) -> bytes",
        },
        public_spec={
            "title": "dill serialize settings",
            "summary": "Extract a task-scoped subset of `dill` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.dumps", "kind": "function"},
                {"path": "featurelifted.loads", "kind": "function"},
                {"path": "featurelifted.settings", "kind": "module"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: dumps/loads roundtrip for functions. Required observable cases include function roundtrip; lambda roundtrip."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: settings module is importable. Required observable cases include settings exposed."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: recurse flag and nested functions. Required observable cases include recurse flag; nested function."},
                {"id": "B004", "text": "Restored callables preserve behavior for simple closures."},
                {"id": "B005", "text": "The package exposes dumps/loads/settings with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: dill."},
            ],
            "exclusions": ["interactive session dump tricks", "original dill import at runtime"],
            "forbidden": {"imports": ["dill"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_huey() -> Path:
    task_id = "huey__task_schedule_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "huey")
    (task_dir / "requirements.lock").write_text("# no third-party dependencies\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("huey\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "huey",
            "required_source_files": ["huey/api.py", "huey/storage.py"],
            "runtime_dependencies": [],
            "notes": "Composite MemoryHuey task decorator + crontab + dequeue/execute result.get.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from datetime import datetime

from featurelifted import MemoryHuey, crontab


def _run_task(huey: MemoryHuey, result) -> None:
    task = huey.dequeue()
    assert task is not None
    huey.execute(task)


def test_task_enqueue_and_result() -> None:
    huey = MemoryHuey(utc=False)
    @huey.task()
    def add(a: int, b: int) -> int:
        return a + b

    result = add(1, 2)
    _run_task(huey, result)
    assert result.get(blocking=False) == 3


def test_crontab_helper() -> None:
    schedule = crontab(minute="*/5")
    assert callable(schedule)
    when = datetime(2024, 1, 1, 10, 5, 0)
    assert schedule(when) is True
    assert schedule(datetime(2024, 1, 1, 10, 3, 0)) is False
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

from featurelifted import MemoryHuey


def _run_one(huey: MemoryHuey) -> None:
    task = huey.dequeue()
    assert task is not None
    huey.execute(task)


def test_multiple_tasks() -> None:
    huey = MemoryHuey(utc=False)
    @huey.task()
    def mul(a: int, b: int) -> int:
        return a * b

    r1 = mul(2, 3)
    r2 = mul(4, 5)
    _run_one(huey)
    _run_one(huey)
    assert r1.get(blocking=False) == 6
    assert r2.get(blocking=False) == 20


def test_flush_clears_queue() -> None:
    huey = MemoryHuey(utc=False)
    @huey.task()
    def noop() -> int:
        return 0

    noop()
    assert huey.pending_count() >= 1
    huey.flush()
    assert huey.pending_count() == 0
'''
        + _forbidden_surface_test("huey"),
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import MemoryHuey, crontab


def test_required_api_surface() -> None:
    assert MemoryHuey is not None
    assert callable(crontab)
''',
        encoding="utf-8",
    )
    metadata = _w3_metadata(
        task_id,
        meta,
        feature={
            "name": "huey task schedule",
            "description": "Composite MemoryHuey @task + crontab + result retrieval.",
            "source_entrypoints": ["huey.MemoryHuey", "huey.crontab"],
            "included_behaviors": [
                "define tasks on MemoryHuey",
                "dequeue/execute then result.get",
                "crontab schedule helper",
            ],
            "excluded_behaviors": ["RedisHuey", "consumer process", "signals"],
        },
        entanglement={
            "level": "medium",
            "types": ["framework_coupling"],
            "primary": "framework_coupling",
            "description": "Task decorator, in-memory broker, and result store compose.",
            "signals": ["@task", "MemoryHuey", "crontab"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import MemoryHuey, crontab",
            "callable": "MemoryHuey.task",
            "signature": "task(retries=None, retry_delay=None, ...)",
        },
        public_spec={
            "title": "huey task schedule",
            "summary": "Extract a task-scoped subset of `huey` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.MemoryHuey", "kind": "class"},
                {"path": "featurelifted.crontab", "kind": "function"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: enqueue tasks and read results via result.get after execute. Required observable cases include task enqueue and result."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: crontab schedule helper. Required observable cases include crontab helper."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: multiple tasks and flush clears queue. Required observable cases include multiple tasks; flush clears queue."},
                {"id": "B004", "text": "MemoryHuey is the only broker backend required."},
                {"id": "B005", "text": "The package exposes MemoryHuey and crontab with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: huey."},
            ],
            "exclusions": ["RedisHuey", "consumer process", "original huey import at runtime"],
            "forbidden": {"imports": ["huey"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_icalendar() -> Path:
    task_id = "icalendar__component_roundtrip_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "icalendar")
    (task_dir / "requirements.lock").write_text(
        "python-dateutil==2.9.0.post0\ntzdata==2024.2\n",
        encoding="utf-8",
    )
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("icalendar\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "icalendar",
            "required_source_files": [
                "src/icalendar/cal/calendar.py",
                "src/icalendar/cal/event.py",
            ],
            "runtime_dependencies": ["python-dateutil", "tzdata"],
            "notes": "Composite Calendar.from_ical/to_ical + Event components.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from datetime import datetime

from featurelifted import Calendar, Event


def test_build_and_roundtrip() -> None:
    cal = Calendar()
    event = Event()
    event.add("summary", "Team sync")
    event.add("dtstart", datetime(2024, 6, 1, 9, 0, 0))
    cal.add_component(event)
    raw = cal.to_ical()
    parsed = Calendar.from_ical(raw)
    ev = parsed.subcomponents[0]
    assert ev["summary"].to_ical().decode() == "Team sync"


def test_parse_existing_ics() -> None:
    ics = (
        "BEGIN:VCALENDAR\\r\\n"
        "VERSION:2.0\\r\\n"
        "PRODID:-//FeatureLiftBench//EN\\r\\n"
        "BEGIN:VEVENT\\r\\n"
        "SUMMARY:Demo\\r\\n"
        "DTSTART:20240101T100000\\r\\n"
        "END:VEVENT\\r\\n"
        "END:VCALENDAR\\r\\n"
    )
    cal = Calendar.from_ical(ics)
    assert cal["prodid"].to_ical().decode().startswith("-//")
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

from datetime import datetime

from featurelifted import Calendar, Event


def test_event_dtend() -> None:
    cal = Calendar()
    event = Event()
    event.add("summary", "All day")
    event.add("dtstart", datetime(2024, 1, 1, 0, 0, 0))
    event.add("dtend", datetime(2024, 1, 2, 0, 0, 0))
    cal.add_component(event)
    parsed = Calendar.from_ical(cal.to_ical())
    ev = parsed.subcomponents[0]
    assert "dtend" in ev


def test_multiple_events() -> None:
    cal = Calendar()
    for name in ("a", "b"):
        ev = Event()
        ev.add("summary", name)
        cal.add_component(ev)
    parsed = Calendar.from_ical(cal.to_ical())
    summaries = [c["summary"].to_ical().decode() for c in parsed.subcomponents]
    assert summaries == ["a", "b"]
'''
        + _forbidden_surface_test("icalendar"),
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import Calendar, Event


def test_required_api_surface() -> None:
    assert Calendar is not None and Event is not None
    assert callable(Calendar.from_ical)
    assert callable(getattr(Calendar(), "to_ical"))
''',
        encoding="utf-8",
    )
    metadata = _w3_metadata(
        task_id,
        meta,
        allowed_dependencies=["python-dateutil", "tzdata"],
        feature={
            "name": "icalendar component roundtrip",
            "description": "Composite icalendar Calendar/Event parse and serialize.",
            "source_entrypoints": ["icalendar.Calendar", "icalendar.Event"],
            "included_behaviors": [
                "Calendar.from_ical / to_ical",
                "Event summary/dtstart/dtend",
                "ICS string roundtrip",
            ],
            "excluded_behaviors": ["full RRULE recurrence engines beyond declared"],
        },
        entanglement={
            "level": "medium",
            "types": ["parser_state_coupling"],
            "primary": "parser_state_coupling",
            "description": "Parse and component construction share calendar model.",
            "signals": ["from_ical", "to_ical", "Event"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import Calendar, Event",
            "callable": "Calendar.from_ical",
            "signature": "from_ical(data: str | bytes)",
        },
        public_spec={
            "title": "icalendar component roundtrip",
            "summary": "Extract a task-scoped subset of `icalendar` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.Calendar", "kind": "class"},
                {"path": "featurelifted.Calendar.from_ical", "kind": "method"},
                {"path": "featurelifted.Calendar.to_ical", "kind": "method"},
                {"path": "featurelifted.Event", "kind": "class"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: build Calendar/Event and roundtrip ICS. Required observable cases include build and roundtrip."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: parse existing ICS strings. Required observable cases include parse existing ics."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: dtend and multiple events. Required observable cases include event dtend; multiple events."},
                {"id": "B004", "text": "to_ical returns bytes suitable for from_ical."},
                {"id": "B005", "text": "The package exposes Calendar/Event/from_ical/to_ical with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: icalendar."},
            ],
            "exclusions": ["full RRULE engines", "original icalendar import at runtime"],
            "forbidden": {"imports": ["icalendar"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_invoke() -> Path:
    task_id = "invoke__collection_context_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "invoke")
    init_path = ref / "__init__.py"
    init_path.write_text(
        init_path.read_text(encoding="utf-8").replace(
            '__version__ = metadata.version("invoke")',
            '__version__ = "3.0.3"',
        ),
        encoding="utf-8",
    )
    (task_dir / "requirements.lock").write_text("# no third-party dependencies\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("invoke\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "invoke",
            "required_source_files": [
                "invoke/collection.py",
                "invoke/context.py",
                "invoke/tasks.py",
            ],
            "runtime_dependencies": [],
            "notes": "Composite @task + Collection + Context/MockContext; no real shell.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import Collection, Context, MockContext, task


@task
def hello(c, name: str = "world") -> str:
    return f"hi {name}"


def test_collection_task_call() -> None:
    ns = Collection()
    ns.add_task(hello)
    assert ns["hello"](Context(), name="Ada") == "hi Ada"


@task
def run_cmd(c) -> int:
    c.run("echo hi")
    return 1


def test_mock_context_run() -> None:
    ns = Collection()
    ns.add_task(run_cmd)
    ctx = MockContext(run=True)
    assert ns["run_cmd"](ctx) == 1
    assert ctx.run.called
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

from featurelifted import Collection, Context, UnexpectedExit, task


@task
def add(c, a: int, b: int) -> int:
    return a + b


def test_nested_collection() -> None:
    inner = Collection("tools")
    inner.add_task(add)
    outer = Collection()
    outer.add_collection(inner, "tools")
    assert outer["tools.add"](Context(), 2, 3) == 5


@task
def fail(c) -> None:
    raise UnexpectedExit("boom")


def test_task_exception_type() -> None:
    ns = Collection()
    ns.add_task(fail)
    try:
        ns["fail"](Context())
        assert False, "expected UnexpectedExit"
    except UnexpectedExit:
        pass
'''
        + _forbidden_surface_test("invoke"),
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import Collection, Context, MockContext, UnexpectedExit, task


def test_required_api_surface() -> None:
    assert callable(task)
    assert Collection is not None and Context is not None
    assert MockContext is not None and UnexpectedExit is not None
''',
        encoding="utf-8",
    )
    metadata = _w3_metadata(
        task_id,
        meta,
        feature={
            "name": "invoke collection context",
            "description": "Composite invoke @task + Collection + Context/MockContext.",
            "source_entrypoints": ["invoke.task", "invoke.Collection", "invoke.Context"],
            "included_behaviors": [
                "build Collection namespaces",
                "call tasks with Context",
                "MockContext records run without shell",
            ],
            "excluded_behaviors": ["real SSH fabric", "config file discovery"],
        },
        entanglement={
            "level": "medium",
            "types": ["framework_coupling"],
            "primary": "framework_coupling",
            "description": "Collection namespace and Context execution compose.",
            "signals": ["@task", "Collection", "MockContext"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import task, Collection, Context, MockContext",
            "callable": "task",
            "signature": "task(*args, **kwargs)",
        },
        public_spec={
            "title": "invoke collection context",
            "summary": "Extract a task-scoped subset of `invoke` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.task", "kind": "function"},
                {"path": "featurelifted.Collection", "kind": "class"},
                {"path": "featurelifted.Context", "kind": "class"},
                {"path": "featurelifted.MockContext", "kind": "class"},
                {"path": "featurelifted.UnexpectedExit", "kind": "class"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: Collection task invocation with Context. Required observable cases include collection task call."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: MockContext stubs run without shell. Required observable cases include mock context run."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: nested collections and UnexpectedExit. Required observable cases include nested collection; task exception type."},
                {"id": "B004", "text": "Tasks are accessed via Collection.__getitem__ by name."},
                {"id": "B005", "text": "The package exposes task/Collection/Context/MockContext/UnexpectedExit with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: invoke."},
            ],
            "exclusions": ["real SSH fabric", "original invoke import at runtime"],
            "forbidden": {"imports": ["invoke"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_joserfc() -> Path:
    task_id = "joserfc__jwt_claims_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "joserfc")
    (task_dir / "requirements.lock").write_text("cryptography==43.0.3\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("joserfc\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "joserfc",
            "required_source_files": ["src/joserfc/jwt.py", "src/joserfc/jwk.py"],
            "runtime_dependencies": ["cryptography"],
            "notes": "Composite jwt.encode/decode with OctKey HS256 offline.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import jwt
from featurelifted.jwk import OctKey


def test_encode_decode_hs256() -> None:
    key = OctKey.import_key("secret")
    token = jwt.encode({"alg": "HS256"}, {"sub": "user-1"}, key)
    decoded = jwt.decode(token, key)
    assert decoded.claims["sub"] == "user-1"


def test_generate_key() -> None:
    key = OctKey.generate_key(256)
    token = jwt.encode({"alg": "HS256"}, {"iss": "test"}, key)
    decoded = jwt.decode(token, key)
    assert decoded.claims["iss"] == "test"
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import time

from featurelifted import jwt
from featurelifted.errors import ExpiredTokenError
from featurelifted.jwk import OctKey


def test_exp_claim() -> None:
    from featurelifted.jwt import JWTClaimsRegistry

    key = OctKey.import_key("secretsecretsecret")
    now = int(time.time())
    token = jwt.encode({"alg": "HS256"}, {"sub": "u", "exp": now + 3600}, key)
    decoded = jwt.decode(token, key)
    assert decoded.claims["sub"] == "u"
    expired = jwt.encode({"alg": "HS256"}, {"sub": "u", "exp": now - 10}, key)
    tok = jwt.decode(expired, key)
    try:
        JWTClaimsRegistry().validate(tok.claims)
        assert False, "expected ExpiredTokenError"
    except ExpiredTokenError:
        pass
'''
        + _forbidden_surface_test("joserfc"),
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import jwt
from featurelifted.errors import ExpiredTokenError
from featurelifted.jwk import OctKey


def test_required_api_surface() -> None:
    assert jwt is not None
    assert OctKey is not None
    assert ExpiredTokenError is not None
''',
        encoding="utf-8",
    )
    metadata = _w3_metadata(
        task_id,
        meta,
        allowed_dependencies=["cryptography"],
        feature={
            "name": "joserfc jwt claims",
            "description": "Composite joserfc jwt.encode/decode with OctKey HS256.",
            "source_entrypoints": ["joserfc.jwt", "joserfc.jwk.OctKey"],
            "included_behaviors": [
                "HS256 JWT encode/decode",
                "OctKey import/generate",
                "exp claim validation",
            ],
            "excluded_behaviors": ["JWKS URL fetch", "asymmetric KMS"],
        },
        entanglement={
            "level": "medium",
            "types": ["data_model_coupling"],
            "primary": "data_model_coupling",
            "description": "JWS encode/decode and claims validation pipeline.",
            "signals": ["jwt.encode", "jwt.decode", "OctKey"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import jwt; from featurelifted.jwk import OctKey",
            "callable": "jwt.encode",
            "signature": "encode(header: dict, claims: dict, key) -> str",
        },
        public_spec={
            "title": "joserfc jwt claims",
            "summary": "Extract a task-scoped subset of `joserfc` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.jwt", "kind": "module"},
                {"path": "featurelifted.jwt.encode", "kind": "function"},
                {"path": "featurelifted.jwt.decode", "kind": "function"},
                {"path": "featurelifted.jwt.Token", "kind": "class"},
                {"path": "featurelifted.jwk.OctKey", "kind": "class"},
                {"path": "featurelifted.errors.ExpiredTokenError", "kind": "class"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: HS256 encode/decode roundtrip. Required observable cases include encode decode hs256."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: OctKey import/generate. Required observable cases include generate key."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: exp claim validation raises ExpiredTokenError. Required observable cases include exp claim."},
                {"id": "B004", "text": "Decoded tokens expose .claims mapping."},
                {"id": "B005", "text": "The package exposes jwt/OctKey/ExpiredTokenError with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: joserfc."},
            ],
            "exclusions": ["JWKS URL fetch", "original joserfc import at runtime"],
            "forbidden": {"imports": ["joserfc"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_python_json_logger() -> Path:
    task_id = "python_json_logger__json_formatter_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "pythonjsonlogger")
    init_path = ref / "__init__.py"
    init = init_path.read_text(encoding="utf-8")
    if "JsonFormatter" not in init:
        init_path.write_text(
            init + "\nfrom .json import JsonFormatter\n",
            encoding="utf-8",
        )
    (task_dir / "requirements.lock").write_text("# no third-party dependencies\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("pythonjsonlogger\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "pythonjsonlogger",
            "required_source_files": ["src/pythonjsonlogger/json.py"],
            "runtime_dependencies": [],
            "notes": "Adapted JsonFormatter from pythonjsonlogger.json.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

import json
import logging

from featurelifted import JsonFormatter


def test_basic_json_line() -> None:
    fmt = JsonFormatter("%(message)s %(levelname)s")
    record = logging.LogRecord("app", logging.INFO, __file__, 10, "hello", (), None)
    payload = json.loads(fmt.format(record))
    assert payload["message"] == "hello"
    assert payload["levelname"] == "INFO"


def test_rename_and_static_fields() -> None:
    fmt = JsonFormatter(
        "%(message)s %(levelname)s",
        rename_fields={"levelname": "level"},
        static_fields={"app": "svc"},
    )
    record = logging.LogRecord("app", logging.WARNING, __file__, 1, "warn", (), None)
    payload = json.loads(fmt.format(record))
    assert payload["level"] == "WARNING"
    assert payload["app"] == "svc"
    assert "levelname" not in payload
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import json
import logging

from featurelifted import JsonFormatter


def test_custom_fmt_fields() -> None:
    fmt = JsonFormatter("%(message)s %(name)s")
    record = logging.LogRecord("worker", logging.ERROR, __file__, 3, "boom", (), None)
    payload = json.loads(fmt.format(record))
    assert payload["message"] == "boom"
    assert payload["name"] == "worker"
'''
        + _forbidden_surface_test("pythonjsonlogger"),
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import JsonFormatter


def test_required_api_surface() -> None:
    assert JsonFormatter is not None
''',
        encoding="utf-8",
    )
    metadata = _w3_metadata(
        task_id,
        meta,
        feature={
            "name": "python json logger formatter",
            "description": "Adapted pythonjsonlogger JsonFormatter field rename/reshape.",
            "source_entrypoints": ["pythonjsonlogger.json.JsonFormatter"],
            "included_behaviors": [
                "format LogRecord to JSON string",
                "rename_fields mapping",
                "static_fields injection",
            ],
            "excluded_behaviors": ["SocketHandler networking"],
        },
        entanglement={
            "level": "low",
            "types": ["config_environment_coupling"],
            "primary": "config_environment_coupling",
            "description": "Formatter options reshape log record output.",
            "signals": ["JsonFormatter", "rename_fields", "static_fields"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import JsonFormatter",
            "callable": "JsonFormatter.format",
            "signature": "format(record: logging.LogRecord) -> str",
        },
        public_spec={
            "title": "python json logger formatter",
            "summary": "Extract a task-scoped subset of `python-json-logger` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.JsonFormatter", "kind": "class"},
                {"path": "featurelifted.JsonFormatter.format", "kind": "method"},
            ],
            "optional_api": [{"path": "featurelifted.json.JsonFormatter", "kind": "class"}],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: format LogRecord to JSON. Required observable cases include basic json line."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: rename_fields and static_fields. Required observable cases include rename and static fields."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: custom fmt and json submodule import. Required observable cases include custom fmt fields; from json submodule."},
                {"id": "B004", "text": "Output is a single JSON object line per record."},
                {"id": "B005", "text": "The package exposes JsonFormatter with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: pythonjsonlogger."},
            ],
            "exclusions": ["SocketHandler networking", "original pythonjsonlogger import at runtime"],
            "forbidden": {"imports": ["pythonjsonlogger"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_tldextract() -> Path:
    task_id = "tldextract__suffix_resolve_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "tldextract")
    (ref / "_version.py").write_text('version = "5.3.1"\n', encoding="utf-8")
    (task_dir / "requirements.lock").write_text(
        "\n".join(
            [
                "idna==3.7",
                "requests==2.32.3",
                "requests-file==2.1.0",
                "filelock==3.16.1",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("tldextract\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "tldextract",
            "required_source_files": [
                "tldextract/tldextract.py",
                "tldextract/.tld_set_snapshot",
            ],
            "runtime_dependencies": ["idna", "requests", "requests-file", "filelock"],
            "notes": "Composite TLDExtract offline with suffix_list_urls=().",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import TLDExtract, extract


def test_tldextract_offline() -> None:
    ext = TLDExtract(suffix_list_urls=())
    result = ext("https://www.google.co.uk/path")
    assert result.subdomain == "www"
    assert result.domain == "google"
    assert result.suffix == "co.uk"


def test_extract_convenience() -> None:
    ext = TLDExtract(suffix_list_urls=())
    result = ext("blog.example.com")
    assert result.domain == "example"
    assert result.suffix == "com"
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

from featurelifted import TLDExtract


def test_registered_domain() -> None:
    ext = TLDExtract(suffix_list_urls=())
    result = ext("https://foo.bar.co.uk")
    assert f"{result.domain}.{result.suffix}" == "bar.co.uk"


def test_no_subdomain() -> None:
    ext = TLDExtract(suffix_list_urls=())
    result = ext("example.com")
    assert result.subdomain == ""
    assert result.domain == "example"
    assert result.suffix == "com"
'''
        + _forbidden_surface_test("tldextract"),
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import ExtractResult, TLDExtract, extract


def test_required_api_surface() -> None:
    assert TLDExtract is not None and callable(extract)
    assert ExtractResult is not None
''',
        encoding="utf-8",
    )
    metadata = _w3_metadata(
        task_id,
        meta,
        allowed_dependencies=["idna", "requests", "requests-file", "filelock"],
        feature={
            "name": "tldextract suffix resolve",
            "description": "Composite tldextract TLDExtract offline extract.",
            "source_entrypoints": ["tldextract.TLDExtract", "tldextract.extract"],
            "included_behaviors": [
                "TLDExtract with suffix_list_urls=()",
                "extract subdomain/domain/suffix",
                "extract convenience function",
            ],
            "excluded_behaviors": ["live PSL download"],
        },
        entanglement={
            "level": "medium",
            "types": ["resource_coupling"],
            "primary": "resource_coupling",
            "description": "Bundled suffix snapshot plus extract logic.",
            "signals": ["TLDExtract", "suffix_list_urls", "ExtractResult"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import TLDExtract, extract",
            "callable": "TLDExtract",
            "signature": "TLDExtract(cache_dir=False, suffix_list_urls=())",
        },
        public_spec={
            "title": "tldextract suffix resolve",
            "summary": "Extract a task-scoped subset of `tldextract` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.TLDExtract", "kind": "class"},
                {"path": "featurelifted.extract", "kind": "function"},
                {"path": "featurelifted.ExtractResult", "kind": "class"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: offline TLDExtract splits URLs. Required observable cases include tldextract offline."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: extract convenience helper. Required observable cases include extract convenience."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: registered domain and bare hosts. Required observable cases include registered domain; no subdomain."},
                {"id": "B004", "text": "suffix_list_urls=() disables network suffix fetch."},
                {"id": "B005", "text": "The package exposes TLDExtract/extract/ExtractResult with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: tldextract."},
            ],
            "exclusions": ["live PSL download", "original tldextract import at runtime"],
            "forbidden": {"imports": ["tldextract"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


VCR_CASSETTE = """version: 1
interactions:
- request:
    body: null
    headers:
      Accept:
      - '*/*'
    method: GET
    uri: http://example.com/
  response:
    body:
      string: hello-vcr
    headers:
      Content-Type:
      - text/plain
    status:
      code: 200
      message: OK
"""


def materialize_vcrpy() -> Path:
    task_id = "vcrpy__cassette_match_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "vcr")
    (task_dir / "requirements.lock").write_text(
        "PyYAML==6.0.2\nwrapt==1.16.0\nurllib3==2.7.0\n",
        encoding="utf-8",
    )
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("vcr\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "vcrpy",
            "required_source_files": ["vcr/config.py", "vcr/cassette.py", "vcr/matchers.py"],
            "runtime_dependencies": ["PyYAML", "wrapt", "urllib3"],
            "notes": "Composite use_cassette replay with pre-recorded yaml; record_mode=none.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        f'''from __future__ import annotations

import urllib.request

from featurelifted import use_cassette

CASSETTE = """{VCR_CASSETTE.strip()}"""


def test_use_cassette_replay(tmp_path) -> None:
    path = tmp_path / "example.yaml"
    path.write_text(CASSETTE, encoding="utf-8")
    with use_cassette(str(path), record_mode="none"):
        resp = urllib.request.urlopen("http://example.com/")
        assert resp.read().decode() == "hello-vcr"


def test_vcr_factory() -> None:
    from featurelifted import VCR

    v = VCR(record_mode="none", match_on=["method", "uri"])
    assert v.record_mode == "none"
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        f'''from __future__ import annotations

import urllib.request

from featurelifted import VCR, use_cassette

CASSETTE = """{VCR_CASSETTE.strip()}"""


def test_match_on_method_uri(tmp_path) -> None:
    path = tmp_path / "match.yaml"
    path.write_text(CASSETTE, encoding="utf-8")
    with VCR(record_mode="none", match_on=["method", "uri"]).use_cassette(str(path)):
        body = urllib.request.urlopen("http://example.com/").read()
        assert body == b"hello-vcr"


def test_cassette_path_record_mode_none(tmp_path) -> None:
    path = tmp_path / "replay.yaml"
    path.write_text(CASSETTE, encoding="utf-8")
    with use_cassette(str(path), record_mode="none") as cass:
        urllib.request.urlopen("http://example.com/")
        assert cass.play_count >= 1
'''
        + _forbidden_surface_test("vcr"),
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import VCR, use_cassette


def test_required_api_surface() -> None:
    assert callable(use_cassette)
    assert VCR is not None
''',
        encoding="utf-8",
    )
    metadata = _w3_metadata(
        task_id,
        meta,
        allowed_dependencies=["PyYAML", "wrapt", "urllib3"],
        feature={
            "name": "vcrpy cassette match",
            "description": "Composite vcr use_cassette replay with matchers.",
            "source_entrypoints": ["vcr.use_cassette", "vcr.VCR"],
            "included_behaviors": [
                "use_cassette replay pre-recorded yaml",
                "record_mode none",
                "match_on method/uri",
            ],
            "excluded_behaviors": ["recording against internet", "selenium"],
        },
        entanglement={
            "level": "medium",
            "types": ["framework_coupling"],
            "primary": "framework_coupling",
            "description": "Matchers, cassette store, and HTTP replay compose.",
            "signals": ["use_cassette", "VCR", "match_on"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import use_cassette, VCR",
            "callable": "use_cassette",
            "signature": "use_cassette(path, record_mode='none', ...)",
        },
        public_spec={
            "title": "vcrpy cassette match",
            "summary": "Extract a task-scoped subset of `vcrpy` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.use_cassette", "kind": "function"},
                {"path": "featurelifted.VCR", "kind": "class"},
                {"path": "featurelifted.VCR.use_cassette", "kind": "method"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: replay cassette via use_cassette with urllib. Required observable cases include use cassette replay."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: VCR factory with record_mode and match_on. Required observable cases include vcr factory."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: match_on method/uri and play_count. Required observable cases include match on method uri; cassette path record mode none."},
                {"id": "B004", "text": "record_mode='none' never records new interactions in tests."},
                {"id": "B005", "text": "The package exposes use_cassette and VCR with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: vcr."},
            ],
            "exclusions": ["recording against internet", "original vcr import at runtime"],
            "forbidden": {"imports": ["vcr"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


BUILDERS: dict[str, Callable[[], Path]] = {
    "boolean_py__expr_simplify_core__001": materialize_boolean_py,
    "dill__serialize_settings_core__001": materialize_dill,
    "huey__task_schedule_core__001": materialize_huey,
    "icalendar__component_roundtrip_core__001": materialize_icalendar,
    "invoke__collection_context_core__001": materialize_invoke,
    "joserfc__jwt_claims_core__001": materialize_joserfc,
    "python_json_logger__json_formatter_core__001": materialize_python_json_logger,
    "tldextract__suffix_resolve_core__001": materialize_tldextract,
    "vcrpy__cassette_match_core__001": materialize_vcrpy,
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

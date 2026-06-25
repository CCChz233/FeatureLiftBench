#!/usr/bin/env python3
"""Scaffold batch-3 benchmark tasks from site-packages snapshots."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
SITE = Path("/Users/chz/anaconda3/lib/python3.12/site-packages")

TASKS = {
    "werkzeug__routing_core__001": {
        "package": "werkzeug",
        "copy": lambda src, dst: _copy_pkg(
            src,
            dst,
            exclude_dirs={"middleware", "debug", "__pycache__"},
            exclude_files={"serving.py", "test.py", "testapp.py", "_reloader.py"},
        ),
    },
    "typer__command_parser_core__001": {
        "package": "typer",
        "copy": lambda src, dst: (
            _copy_pkg(src / "typer", dst / "typer", exclude_dirs={"__pycache__"}),
            _copy_pkg(src / "click", dst / "click", exclude_dirs={"__pycache__"}),
        ),
    },
    "importlib_metadata__entry_points_core__001": {
        "package": "importlib_metadata",
        "copy": lambda src, dst: (
            _copy_pkg(src / "importlib_metadata", dst / "importlib_metadata"),
            _copy_pkg(src / "zipp", dst / "zipp"),
        ),
    },
    "h11__message_parse_core__001": {
        "package": "h11",
        "copy": lambda src, dst: _copy_pkg(
            src,
            dst,
            exclude_dirs={"tests", "__pycache__"},
        ),
    },
    "redis__resp_parser_core__001": {
        "package": "redis",
        "copy": lambda src, dst: _copy_pkg(
            src / "redis",
            dst / "redis",
            include_only_prefixes=(
                "_parsers/",
                "exceptions.py",
                "typing.py",
                "utils.py",
            ),
        ),
    },
}


def _copy_pkg(
    src: Path,
    dst: Path,
    *,
    exclude_dirs: set[str] | None = None,
    exclude_files: set[str] | None = None,
    include_only_prefixes: tuple[str, ...] | None = None,
) -> None:
    exclude_dirs = exclude_dirs or set()
    exclude_files = exclude_files or set()
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True, exist_ok=True)
    for path in sorted(src.rglob("*")):
        rel = path.relative_to(src).as_posix()
        if any(part in exclude_dirs for part in path.parts):
            continue
        if path.name in exclude_files:
            continue
        if include_only_prefixes:
            if not any(rel.startswith(prefix) for prefix in include_only_prefixes):
                continue
        target = dst / rel
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        if path.suffix not in {".py", ".typed", ".pyi"}:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def _write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _forbidden(pkg: str) -> None:
    pass


METADATA = {
    "werkzeug__routing_core__001": {
        "task_id": "werkzeug__routing_core__001",
        "language": "python",
        "difficulty": "hard",
        "tags": [
            "extreme",
            "multi-task-repo",
            "functional-discriminator",
            "decoupling-discriminator",
            "framework_coupling",
            "pure-python",
            "multi-module",
        ],
        "source": {
            "name": "werkzeug",
            "url": "https://github.com/pallets/werkzeug",
            "commit": "3.0.3-installed-snapshot",
            "license": "BSD-3-Clause",
        },
        "feature": {
            "name": "URL routing map and adapter",
            "description": "Extract Werkzeug URL routing: Map, Rule, converters, match, and build.",
            "source_entrypoints": [
                "werkzeug.routing.Map",
                "werkzeug.routing.Rule",
                "werkzeug.routing.MapAdapter",
                "werkzeug.routing.Subdomain",
                "werkzeug.routing.Submount",
            ],
            "included_behaviors": [
                "define URL rules with converters and HTTP methods",
                "match paths to endpoints with argument extraction",
                "build URLs from endpoints and arguments",
                "subdomain and submount rule factories",
                "redirect and alias redirect exceptions on match",
            ],
            "excluded_behaviors": [
                "WSGI request/response wrappers",
                "development server and middleware",
                "form parsing and file uploads",
                "original project tests and CLI",
            ],
        },
        "entanglement": {
            "level": "high",
            "types": [
                "framework_coupling",
                "data_model_coupling",
                "implicit_dependency_coupling",
            ],
            "primary": "framework_coupling",
            "description": "Routing couples rule factories, converters, host binding, and WSGI host helpers.",
            "signals": [
                "Map/MapAdapter framework objects",
                "converter registry and validation",
                "subdomain and mount prefix composition",
            ],
        },
        "output": {
            "package": "featurelifted",
            "import": "from featurelifted.routing import Map, Rule, MapAdapter, Subdomain, Submount",
            "callable": "featurelifted.routing.Map",
            "signature": "Map(rules=None, default_subdomain='', **options)",
        },
        "environment": {
            "python": "3.11",
            "network": False,
            "timeout_seconds": 60,
            "dependency_lock": "requirements.lock",
            "allowed_dependencies": [],
            "forbidden_dependencies": ["werkzeug"],
            "forbidden_imports": ["werkzeug"],
        },
        "tests": {"public": "public_tests/", "hidden": "hidden_tests/", "command": "pytest"},
    },
    "typer__command_parser_core__001": {
        "task_id": "typer__command_parser_core__001",
        "language": "python",
        "difficulty": "hard",
        "tags": [
            "extreme",
            "cli",
            "functional-discriminator",
            "decoupling-discriminator",
            "framework_coupling",
            "pure-python",
            "multi-module",
        ],
        "source": {
            "name": "typer",
            "url": "https://github.com/fastapi/typer",
            "commit": "0.20.0-installed-snapshot",
            "license": "MIT",
        },
        "feature": {
            "name": "Typer command parser and CLI runner",
            "description": "Extract Typer CLI command building, type-hint parameter parsing, and CliRunner invocation.",
            "source_entrypoints": [
                "typer.Typer",
                "typer.run",
                "typer.testing.CliRunner",
                "typer.Argument",
                "typer.Option",
            ],
            "included_behaviors": [
                "build commands from type-annotated functions",
                "parse options, arguments, defaults, and choices",
                "invoke Typer apps through CliRunner",
                "nested subcommands and context passing",
                "usage errors for invalid parameters",
            ],
            "excluded_behaviors": [
                "shell completion integration",
                "rich markup rendering beyond basic echo",
                "documentation and release tooling",
            ],
        },
        "entanglement": {
            "level": "high",
            "types": [
                "framework_coupling",
                "third_party_dependency_coupling",
                "implicit_dependency_coupling",
            ],
            "primary": "framework_coupling",
            "description": "Typer couples Click decorators, type-hint introspection, and CliRunner invocation.",
            "signals": [
                "Typer/Click command framework",
                "type-hint to parameter conversion",
                "CliRunner test harness",
            ],
        },
        "output": {
            "package": "featurelifted",
            "import": "import featurelifted as typer; from featurelifted.testing import CliRunner",
            "callable": "featurelifted.Typer",
            "signature": "Typer(name=None, **kwargs)",
        },
        "environment": {
            "python": "3.11",
            "network": False,
            "timeout_seconds": 60,
            "dependency_lock": "requirements.lock",
            "allowed_dependencies": [],
            "forbidden_dependencies": ["typer", "click"],
            "forbidden_imports": ["typer", "click"],
        },
        "tests": {"public": "public_tests/", "hidden": "hidden_tests/", "command": "pytest"},
    },
    "importlib_metadata__entry_points_core__001": {
        "task_id": "importlib_metadata__entry_points_core__001",
        "language": "python",
        "difficulty": "hard",
        "tags": [
            "extreme",
            "functional-discriminator",
            "decoupling-discriminator",
            "config_environment_coupling",
            "pure-python",
            "multi-module",
        ],
        "source": {
            "name": "importlib_metadata",
            "url": "https://github.com/python/importlib_metadata",
            "commit": "7.0.1-installed-snapshot",
            "license": "Apache-2.0",
        },
        "feature": {
            "name": "Entry point discovery and selection",
            "description": "Extract importlib_metadata entry point parsing, EntryPoints selection, and PathDistribution metadata reading.",
            "source_entrypoints": [
                "importlib_metadata.entry_points",
                "importlib_metadata.EntryPoint",
                "importlib_metadata.EntryPoints",
                "importlib_metadata.PathDistribution",
                "importlib_metadata.Sectioned",
            ],
            "included_behaviors": [
                "parse entry point definitions from metadata",
                "select entry points by group and name",
                "load entry point targets",
                "read entry points from PathDistribution metadata directories",
                "parse INI-style sectioned entry point config",
            ],
            "excluded_behaviors": [
                "full distribution discovery across sys.path",
                "package file listing and requirements resolution",
                "original project tests and CLI",
            ],
        },
        "entanglement": {
            "level": "high",
            "types": [
                "config_environment_coupling",
                "data_model_coupling",
                "third_party_dependency_coupling",
                "implicit_dependency_coupling",
            ],
            "primary": "config_environment_coupling",
            "description": "Entry points couple metadata file formats, distribution objects, and environment scanning.",
            "signals": [
                "metadata INI section parsing",
                "PathDistribution filesystem layout",
                "EntryPoints selection API",
            ],
        },
        "output": {
            "package": "featurelifted",
            "import": "from featurelifted import EntryPoint, EntryPoints, PathDistribution, Sectioned",
            "callable": "featurelifted.EntryPoints.select",
            "signature": "EntryPoints.select(**params) -> EntryPoints",
        },
        "environment": {
            "python": "3.11",
            "network": False,
            "timeout_seconds": 60,
            "dependency_lock": "requirements.lock",
            "allowed_dependencies": [],
            "forbidden_dependencies": ["importlib_metadata", "importlib-metadata"],
            "forbidden_imports": ["importlib_metadata"],
        },
        "tests": {"public": "public_tests/", "hidden": "hidden_tests/", "command": "pytest"},
    },
    "h11__message_parse_core__001": {
        "task_id": "h11__message_parse_core__001",
        "language": "python",
        "difficulty": "hard",
        "tags": [
            "extreme",
            "functional-discriminator",
            "decoupling-discriminator",
            "parser_state_coupling",
            "pure-python",
            "multi-module",
        ],
        "source": {
            "name": "h11",
            "url": "https://github.com/python-hyper/h11",
            "commit": "0.14.0-installed-snapshot",
            "license": "MIT",
        },
        "feature": {
            "name": "HTTP/1.1 message parse and state machine",
            "description": "Extract h11 Connection state machine for parsing and framing HTTP/1.1 request/response messages.",
            "source_entrypoints": [
                "h11.Connection",
                "h11.Request",
                "h11.Response",
                "h11.Data",
                "h11.EndOfMessage",
            ],
            "included_behaviors": [
                "parse request and response start-lines and headers",
                "frame bodies with content-length and chunked encoding",
                "drive client/server role state transitions",
                "surface protocol errors for malformed messages",
                "serialize events back to wire bytes",
            ],
            "excluded_behaviors": [
                "socket I/O and TLS",
                "HTTP/2 or WebSocket upgrades beyond state flags",
                "original project tests",
            ],
        },
        "entanglement": {
            "level": "high",
            "types": [
                "parser_state_coupling",
                "data_model_coupling",
                "implicit_dependency_coupling",
            ],
            "primary": "parser_state_coupling",
            "description": "HTTP parsing couples connection role state, incremental buffers, and event readers/writers.",
            "signals": [
                "Connection state machine",
                "incremental receive buffer",
                "reader/writer dispatch tables",
            ],
        },
        "output": {
            "package": "featurelifted",
            "import": "from featurelifted import Connection, CLIENT, SERVER, Request, Response, Data, EndOfMessage, NEED_DATA",
            "callable": "featurelifted.Connection",
            "signature": "Connection(our_role, max_incomplete_event_size=16384)",
        },
        "environment": {
            "python": "3.11",
            "network": False,
            "timeout_seconds": 60,
            "dependency_lock": "requirements.lock",
            "allowed_dependencies": [],
            "forbidden_dependencies": ["h11"],
            "forbidden_imports": ["h11"],
        },
        "tests": {"public": "public_tests/", "hidden": "hidden_tests/", "command": "pytest"},
    },
    "redis__resp_parser_core__001": {
        "task_id": "redis__resp_parser_core__001",
        "language": "python",
        "difficulty": "hard",
        "tags": [
            "extreme",
            "functional-discriminator",
            "decoupling-discriminator",
            "parser_state_coupling",
            "pure-python",
            "multi-module",
        ],
        "source": {
            "name": "redis",
            "url": "https://github.com/redis/redis-py",
            "commit": "8.0.1-installed-snapshot",
            "license": "MIT",
        },
        "feature": {
            "name": "RESP2/RESP3 wire parser",
            "description": "Extract redis-py synchronous RESP2/RESP3 parsing and command encoding without network I/O.",
            "source_entrypoints": [
                "redis._parsers._RESP2Parser",
                "redis._parsers._RESP3Parser",
                "redis._parsers.Encoder",
                "redis._parsers.SocketBuffer",
            ],
            "included_behaviors": [
                "parse RESP simple, bulk, and multi-bulk replies",
                "decode bulk strings with optional byte preservation",
                "map Redis error prefixes to exception classes",
                "encode commands to RESP bulk arrays",
                "buffer incremental socket reads via SocketBuffer",
            ],
            "excluded_behaviors": [
                "TCP/TLS connection management",
                "Redis command client and cluster logic",
                "pub/sub push notification handlers",
                "hiredis C extension parser",
            ],
        },
        "entanglement": {
            "level": "high",
            "types": [
                "parser_state_coupling",
                "implicit_dependency_coupling",
            ],
            "primary": "parser_state_coupling",
            "description": "RESP parsing couples incremental buffers, encoder settings, and error classification tables.",
            "signals": [
                "SocketBuffer incremental reads",
                "parser rewind on partial reads",
                "Encoder decode_responses flag",
            ],
        },
        "output": {
            "package": "featurelifted",
            "import": "from featurelifted._parsers import _RESP2Parser, _RESP3Parser, Encoder",
            "callable": "featurelifted._parsers._RESP2Parser.read_response",
            "signature": "read_response(disable_decoding=False, timeout=SENTINEL)",
        },
        "environment": {
            "python": "3.11",
            "network": False,
            "timeout_seconds": 60,
            "dependency_lock": "requirements.lock",
            "allowed_dependencies": [],
            "forbidden_dependencies": ["redis"],
            "forbidden_imports": ["redis"],
        },
        "tests": {"public": "public_tests/", "hidden": "hidden_tests/", "command": "pytest"},
    },
}


def _write_tests(task_id: str, task_dir: Path) -> None:
    public = task_dir / "public_tests"
    hidden = task_dir / "hidden_tests"
    public.mkdir(parents=True, exist_ok=True)
    hidden.mkdir(parents=True, exist_ok=True)

    if task_id == "werkzeug__routing_core__001":
        (public / "test_public_api.py").write_text(
            WERKZEUG_PUBLIC,
            encoding="utf-8",
        )
        (hidden / "test_hidden_behavior.py").write_text(
            WERKZEUG_HIDDEN,
            encoding="utf-8",
        )
    elif task_id == "typer__command_parser_core__001":
        (public / "test_public_api.py").write_text(TYPER_PUBLIC, encoding="utf-8")
        (hidden / "test_hidden_behavior.py").write_text(TYPER_HIDDEN, encoding="utf-8")
    elif task_id == "importlib_metadata__entry_points_core__001":
        (public / "test_public_api.py").write_text(IM_PUBLIC, encoding="utf-8")
        (hidden / "test_hidden_behavior.py").write_text(IM_HIDDEN, encoding="utf-8")
    elif task_id == "h11__message_parse_core__001":
        (public / "test_public_api.py").write_text(H11_PUBLIC, encoding="utf-8")
        (hidden / "test_hidden_behavior.py").write_text(H11_HIDDEN, encoding="utf-8")
    elif task_id == "redis__resp_parser_core__001":
        (public / "test_public_api.py").write_text(REDIS_PUBLIC, encoding="utf-8")
        (hidden / "test_hidden_behavior.py").write_text(REDIS_HIDDEN, encoding="utf-8")


WERKZEUG_PUBLIC = '''\
from __future__ import annotations

from featurelifted.routing import Map, Rule


def test_match_and_build_simple_rules() -> None:
    mapping = Map(
        [
            Rule("/", endpoint="index"),
            Rule("/users/<int:user_id>", endpoint="user"),
        ]
    )
    adapter = mapping.bind("example.com")
    assert adapter.match("/") == ("index", {})
    assert adapter.match("/users/42") == ("user", {"user_id": 42})
    assert adapter.build("user", {"user_id": 7}) == "/users/7"
'''

WERKZEUG_HIDDEN = '''\
from __future__ import annotations

import pytest

from featurelifted.routing import Map, Rule, Subdomain, Submount
from featurelifted.routing.exceptions import RequestRedirect


def test_subdomain_and_submount_routing() -> None:
    mapping = Map(
        [
            Subdomain(
                "api",
                [Rule("/v1/status", endpoint="api_status")],
            ),
            Submount(
                "/blog",
                [Rule("/", endpoint="blog_index"), Rule("/<slug>", endpoint="blog_post")],
            ),
        ],
        default_subdomain="www",
    )
    api = mapping.bind("example.com", subdomain="api")
    assert api.match("/v1/status") == ("api_status", {})

    www = mapping.bind("example.com")
    assert www.match("/blog/") == ("blog_index", {})
    assert www.match("/blog/hello-world") == ("blog_post", {"slug": "hello-world"})


def test_strict_slashes_redirect() -> None:
    mapping = Map([Rule("/about/", endpoint="about", strict_slashes=True)])
    adapter = mapping.bind("example.com")
    with pytest.raises(RequestRedirect) as exc:
        adapter.match("/about")
    assert exc.value.new_url.endswith("/about/")
'''

TYPER_PUBLIC = '''\
from __future__ import annotations

import featurelifted as typer
from featurelifted.testing import CliRunner


def test_typed_options_and_arguments() -> None:
    app = typer.Typer()

    @app.command()
    def greet(name: str, count: int = 1, formal: bool = False):
        prefix = "Hello" if not formal else "Greetings"
        typer.echo(f"{prefix} {name} " * count)

    runner = CliRunner()
    result = runner.invoke(app, ["Ada", "--count", "2", "--formal"])
    assert result.exit_code == 0
    assert result.output.strip() == "Greetings Ada Greetings Ada"
'''

TYPER_HIDDEN = '''\
from __future__ import annotations

from typing import Literal, Optional

import featurelifted as typer
from featurelifted.testing import CliRunner


def test_subcommands_and_optional_path() -> None:
    app = typer.Typer()
    users = typer.Typer()
    app.add_typer(users, name="users")

    @users.command()
    def create(name: str, email: Optional[str] = None):
        typer.echo(f"create:{name}:{email or ''}")

    runner = CliRunner()
    ok = runner.invoke(app, ["users", "create", "Ada", "--email", "a@example.com"])
    assert ok.exit_code == 0
    assert ok.output.strip() == "create:Ada:a@example.com"

    bad = runner.invoke(app, ["users", "create"])
    assert bad.exit_code != 0


def test_choice_validation() -> None:
    app = typer.Typer()

    @app.command()
    def mode(value: Literal["fast", "slow"] = "fast"):
        typer.echo(value)

    runner = CliRunner()
    bad = runner.invoke(app, ["--value", "turbo"])
    assert bad.exit_code != 0
'''

IM_PUBLIC = '''\
from __future__ import annotations

from featurelifted import EntryPoint, EntryPoints, Sectioned


def test_entry_point_value_parsing_and_selection() -> None:
    ep = EntryPoint(name="console", value="pkg.mod:main", group="console_scripts")
    assert ep.module == "pkg.mod"
    assert ep.attr == "main"
    selected = EntryPoints((ep,)).select(group="console_scripts", name="console")
    assert len(selected) == 1
    assert selected["console"].matches(name="console", group="console_scripts")


def test_sectioned_entry_point_config() -> None:
    sample = """
    [console_scripts]
    tool = pkg.tool:run
    """
    pairs = list(Sectioned.section_pairs(sample))
    assert pairs[0].name == "console_scripts"
    assert pairs[0].value.name == "tool"
    assert pairs[0].value.value == "pkg.tool:run"
'''

IM_HIDDEN = '''\
from __future__ import annotations

from pathlib import Path

from featurelifted import EntryPoint, EntryPoints, PathDistribution


def _write_dist_info(root: Path, name: str, version: str, entry_text: str) -> Path:
    dist_info = root / f"{name}-{version}.dist-info"
    dist_info.mkdir(parents=True)
    (dist_info / "METADATA").write_text(
        f"Metadata-Version: 2.1\\nName: {name}\\nVersion: {version}\\n",
        encoding="utf-8",
    )
    (dist_info / "entry_points.txt").write_text(entry_text, encoding="utf-8")
    return dist_info


def test_path_distribution_entry_points(tmp_path: Path) -> None:
    meta = _write_dist_info(
        tmp_path,
        "demo",
        "1.0",
        "[console_scripts]\\ndemo = demo.cli:main\\n",
    )
    dist = PathDistribution(meta)
    eps = EntryPoints(dist.entry_points)
    assert len(eps.select(group="console_scripts")) == 1
    ep = eps["demo"]
    assert isinstance(ep, EntryPoint)
    assert ep.name == "demo"
    assert ep.value == "demo.cli:main"
'''

H11_PUBLIC = '''\
from __future__ import annotations

from featurelifted import CLIENT, Connection, NEED_DATA, Request, SERVER


def _collect(conn: Connection, data: bytes):
    conn.receive_data(data)
    events = []
    while True:
        event = conn.next_event()
        if event is NEED_DATA:
            break
        events.append(event)
    return events


def test_parse_simple_http_request() -> None:
    conn = Connection(SERVER)
    events = _collect(
        conn,
        b"GET /hello HTTP/1.1\\r\\nHost: example.com\\r\\n\\r\\n",
    )
    assert len(events) == 2
    assert events[0].method == b"GET"
    assert events[0].target == b"/hello"
    assert events[1].__class__.__name__ == "EndOfMessage"


def test_client_request_serialization() -> None:
    conn = Connection(CLIENT)
    payload = conn.send(Request(method="GET", target="/", headers=[("Host", "example.com")]))
    assert b"GET / HTTP/1.1" in payload
'''

H11_HIDDEN = '''\
from __future__ import annotations

from featurelifted import CLIENT, Connection, Data, EndOfMessage, Request, Response, SERVER
from featurelifted import NEED_DATA
from featurelifted import RemoteProtocolError


def _feed(conn: Connection, data: bytes):
    conn.receive_data(data)
    events = []
    while True:
        event = conn.next_event()
        if event is NEED_DATA:
            break
        events.append(event)
    return events


def test_chunked_response_body() -> None:
    conn = Connection(CLIENT)
    wire = (
        b"HTTP/1.1 200 OK\\r\\n"
        b"Transfer-Encoding: chunked\\r\\n"
        b"\\r\\n"
        b"5\\r\\n"
        b"hello\\r\\n"
        b"0\\r\\n"
        b"\\r\\n"
    )
    events = _feed(conn, wire)
    assert any(isinstance(e, Response) for e in events)
    data_events = [e for e in events if isinstance(e, Data)]
    assert b"".join(e.data for e in data_events) == b"hello"
    assert any(isinstance(e, EndOfMessage) for e in events)


def test_malformed_request_raises() -> None:
    conn = Connection(SERVER)
    conn.receive_data(b"NOT HTTP\\r\\n\\r\\n")
    try:
        conn.next_event()
        raised = False
    except RemoteProtocolError:
        raised = True
    assert raised
'''

REDIS_PUBLIC = '''\
from __future__ import annotations

from featurelifted._parsers import Encoder, _RESP2Parser


class _FakeSocket:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload
        self._pos = 0

    def recv(self, size: int) -> bytes:
        chunk = self._payload[self._pos : self._pos + size]
        self._pos += len(chunk)
        return chunk

    def settimeout(self, _timeout) -> None:
        return None


class _FakeConnection:
    def __init__(self, payload: bytes) -> None:
        self.encoder = Encoder("utf-8", "strict", True)
        self.socket_timeout = None
        self._sock = _FakeSocket(payload)


def test_resp2_simple_and_bulk_replies() -> None:
    parser = _RESP2Parser(4096)
    parser.on_connect(_FakeConnection(b":42\\r\\n"))
    assert parser.read_response() == 42

    parser.on_connect(_FakeConnection(b"$3\\r\\nfoo\\r\\n"))
    assert parser.read_response() == "foo"


def test_resp2_array_reply() -> None:
    parser = _RESP2Parser(4096)
    parser.on_connect(_FakeConnection(b"*2\\r\\n:1\\r\\n:2\\r\\n"))
    assert parser.read_response() == [1, 2]
'''

REDIS_HIDDEN = '''\
from __future__ import annotations

from featurelifted._parsers import Encoder, _RESP2Parser, _RESP3Parser
from featurelifted.exceptions import ResponseError


class _FakeSocket:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload
        self._pos = 0

    def recv(self, size: int) -> bytes:
        chunk = self._payload[self._pos : self._pos + size]
        self._pos += len(chunk)
        return chunk

    def settimeout(self, _timeout) -> None:
        return None


class _FakeConnection:
    def __init__(self, payload: bytes, *, decode: bool = True) -> None:
        self.encoder = Encoder("utf-8", "strict", decode)
        self.socket_timeout = None
        self._sock = _FakeSocket(payload)


def test_resp2_error_reply_returns_response_error() -> None:
    parser = _RESP2Parser(4096)
    parser.on_connect(_FakeConnection(b"-ERR unknown command\\r\\n"))
    result = parser.read_response()
    assert isinstance(result, ResponseError)
    assert "unknown command" in str(result)


def test_resp3_null_and_boolean() -> None:
    parser = _RESP3Parser(4096)
    parser.on_connect(_FakeConnection(b"_\\r\\n"))
    assert parser.read_response() is None

    parser.on_connect(_FakeConnection(b"#t\\r\\n"))
    assert parser.read_response() is True


def test_encoder_rejects_bool() -> None:
    enc = Encoder("utf-8", "strict", True)
    try:
        enc.encode(True)
        raised = False
    except Exception:
        raised = True
    assert raised
'''


def main() -> None:
    for task_id, spec in TASKS.items():
        task_dir = _REPO_ROOT / "benchmark" / "tasks" / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        repo_dir = task_dir / "repo"
        pkg = spec["package"]
        src = SITE / pkg
        if not src.is_dir():
            raise SystemExit(f"missing package in site-packages: {src}")
        spec["copy"](SITE, repo_dir)
        _write_json(task_dir / "metadata.json", METADATA[task_id])
        (task_dir / "requirements.lock").write_text("\n", encoding="utf-8")
        eval_dir = task_dir / "evaluation"
        eval_dir.mkdir(exist_ok=True)
        forbidden = METADATA[task_id]["environment"]["forbidden_imports"][0]
        (eval_dir / "forbidden_imports.txt").write_text(forbidden + "\n", encoding="utf-8")
        _write_json(eval_dir / "oracle_manifest.json", {})
        _write_tests(task_id, task_dir)
        print(f"scaffolded {task_id}")
    print("done")


if __name__ == "__main__":
    main()

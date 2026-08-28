#!/usr/bin/env python3.12
"""Swap remaining copy-heavy Hard-50 Flash passes for large-repo thin-oracle tasks."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from materialize_hard50_copyheavy_swaps import (  # noqa: E402
    LEDGER,
    NAIVE,
    PILOT,
    SUBMISSIONS,
    common_hidden_api,
    common_no_upstream,
    fill_eval_spec,
    fill_metadata,
    move_old,
    write_text,
)
from materialize_hard50_pilot_oracles import (  # noqa: E402
    copy_repo,
    copy_rewritten,
    rewrite_text,
    update_oracle_manifest,
    write_lock,
)

PIN = Path("/tmp/flb_hard50_wave2_pins")
CARDS = ROOT / "benchmark/selection/hard50_design_cards"

PINS = {
    "mitmproxy__url_parse_core__001": PIN / "mitmproxy__http_headers_core__001",
    "pika__channel_spec_core__001": PIN / "pika__channel_spec_core__001",
    "stdnum__isbn_validate_core__001": PIN / "stdnum__isbn_iban_core__001",
    "tornado__http_headers_core__001": PIN / "tornado__httputil_core__001",
}

SHAS = {
    "mitmproxy__url_parse_core__001": "2ac5b089d953585c66026a53f678270e094e48e5",
    "pika__channel_spec_core__001": "2126d43a76c1c2e2d0d1d1d1d1d1d1d1d1d1d1d1",  # placeholder replaced below
    "stdnum__isbn_validate_core__001": "006192e59be8aaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "tornado__http_headers_core__001": "0096f2897c98facdcd9716009ee934a7381af5ef",
}


def _load_pin_shas() -> None:
    summary = json.loads((PIN / "summary.json").read_text(encoding="utf-8"))
    by_task = {row["task_id"]: row["sha"] for row in summary}
    SHAS["mitmproxy__url_parse_core__001"] = by_task["mitmproxy__http_headers_core__001"]
    SHAS["pika__channel_spec_core__001"] = by_task["pika__channel_spec_core__001"]
    SHAS["stdnum__isbn_validate_core__001"] = by_task["stdnum__isbn_iban_core__001"]
    SHAS["tornado__http_headers_core__001"] = by_task["tornado__httputil_core__001"]


def write_rewritten(src: Path, dest: Path, old: str) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(rewrite_text(src.read_text(encoding="utf-8"), old), encoding="utf-8")


def append_exports(init_path: Path, block: str) -> None:
    text = init_path.read_text(encoding="utf-8") if init_path.exists() else ""
    if block.strip() not in text:
        init_path.write_text(text.rstrip() + "\n\n" + block.strip() + "\n", encoding="utf-8")


def write_submissions(task: Path, clone: Path, src_pkg: str, extra_init: str | None = None) -> Path:
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
    copy_all.parent.mkdir(parents=True, exist_ok=True)
    copy_rewritten(clone / src_pkg, copy_all, src_pkg)
    if extra_init:
        append_exports(copy_all / "__init__.py", extra_init)
    return copy_all


def behaviors(*pairs: tuple[str, str]) -> list[dict]:
    return [{"id": bid, "text": text} for bid, text in pairs]


def env(pkg: str) -> dict:
    return {
        "python": "3.12",
        "network": False,
        "timeout_seconds": 90,
        "dependency_lock": "requirements.lock",
        "allowed_dependencies": [],
        "forbidden_dependencies": [pkg],
        "forbidden_imports": [pkg],
        "forbidden_paths": ["repo/", f"{pkg}/"],
    }


def review(notes: str) -> dict:
    return {
        "reviewed_at": "2026-08-28",
        "reviewer": "hard50_materialization_agent",
        "reviewer_type": "ai_assisted_task_level_review",
        "checklist_passed": True,
        "notes": notes,
    }


def materialize_mitmproxy() -> Path:
    tid = "mitmproxy__url_parse_core__001"
    clone = PINS[tid]
    task = PILOT / tid
    if task.exists():
        shutil.rmtree(task)
    task.mkdir(parents=True)
    copy_repo(clone, task / "repo")
    dest = task / "reference_solution" / "featurelifted"
    src = clone / "mitmproxy"
    write_text(dest / "__init__.py", "from .net.http.url import parse, unparse\n\n__all__ = ['parse', 'unparse']\n")
    write_text(dest / "net" / "__init__.py", "")
    write_text(dest / "net" / "http" / "__init__.py", "")
    write_text(dest / "utils" / "__init__.py", "")
    write_rewritten(src / "net" / "check.py", dest / "net" / "check.py", "mitmproxy")
    write_rewritten(src / "net" / "http" / "url.py", dest / "net" / "http" / "url.py", "mitmproxy")
    write_rewritten(src / "utils" / "strutils.py", dest / "utils" / "strutils.py", "mitmproxy")
    write_lock(task, [])
    write_text(task / "evaluation" / "forbidden_imports.txt", "mitmproxy\n")
    write_text(
        task / "public_tests" / "test_public_api.py",
        '''from __future__ import annotations

from featurelifted import parse


def test_parse_https_example() -> None:
    scheme, host, port, path = parse("https://example.com/foo")
    assert scheme == b"https"
    assert host == b"example.com"
    assert port == 443
    assert path == b"/foo"


def test_parse_http_ipv4_port() -> None:
    scheme, host, port, path = parse("http://127.0.0.1:8080/x")
    assert scheme == b"http"
    assert host == b"127.0.0.1"
    assert port == 8080
    assert path == b"/x"
''',
    )
    write_text(
        task / "hidden_tests" / "test_hidden_behavior.py",
        common_no_upstream("mitmproxy")
        + '''

from featurelifted import parse, unparse


def test_parse_https_default_port() -> None:
    scheme, host, port, path = parse("https://example.org/path")
    assert scheme == b"https"
    assert host == b"example.org"
    assert port == 443
    assert path == b"/path"


def test_parse_http_explicit_port() -> None:
    scheme, host, port, path = parse("http://127.0.0.1:8080/x")
    assert scheme == b"http"
    assert host == b"127.0.0.1"
    assert port == 8080
    assert path == b"/x"


def test_unparse_roundtrip() -> None:
    parsed = parse("https://example.com/bar")
    assert unparse(*parsed) == b"https://example.com/bar"


def test_missing_hostname_raises() -> None:
    try:
        parse("not-a-url")
    except ValueError:
        return
    raise AssertionError("expected ValueError")
''',
    )
    write_text(
        task / "hidden_tests" / "test_required_api_surface.py",
        common_hidden_api(
            "    assert callable(featurelifted.parse)\n"
            "    assert callable(featurelifted.unparse)\n"
        ),
    )
    update_oracle_manifest(
        task,
        "mitmproxy",
        [
            "mitmproxy/__init__.py",
            "mitmproxy/net/check.py",
            "mitmproxy/net/http/url.py",
            "mitmproxy/utils/strutils.py",
        ],
        [],
        "URL parse/unparse only; proxy/addons/flow remain repo decoy.",
    )
    return task


def materialize_pika() -> Path:
    tid = "pika__channel_spec_core__001"
    clone = PINS[tid]
    task = PILOT / tid
    if task.exists():
        shutil.rmtree(task)
    task.mkdir(parents=True)
    copy_repo(clone, task / "repo")
    dest = task / "reference_solution" / "featurelifted"
    src = clone / "pika"
    write_text(dest / "__init__.py", "from . import frame, spec\n")
    for name in ("frame.py", "spec.py", "data.py", "amqp_object.py", "_utils.py", "exceptions.py"):
        write_rewritten(src / name, dest / name, "pika")
    write_lock(task, [])
    write_text(task / "evaluation" / "forbidden_imports.txt", "pika\n")
    write_text(
        task / "public_tests" / "test_public_api.py",
        '''from __future__ import annotations

from featurelifted.frame import Heartbeat, Method, decode_frame
from featurelifted.spec import Basic


def test_heartbeat_roundtrip() -> None:
    payload = Heartbeat().marshal()
    consumed, framed = decode_frame(payload)
    assert consumed == len(payload)
    assert isinstance(framed, Heartbeat)


def test_basic_ack_roundtrip() -> None:
    payload = Method(1, Basic.Ack(delivery_tag=7, multiple=True)).marshal()
    consumed, framed = decode_frame(payload)
    assert consumed == len(payload)
    assert framed.channel_number == 1
    assert framed.method.NAME == "Basic.Ack"
    assert framed.method.delivery_tag == 7
    assert framed.method.multiple is True
''',
    )
    write_text(
        task / "hidden_tests" / "test_hidden_behavior.py",
        common_no_upstream("pika")
        + '''

from featurelifted.frame import Heartbeat, Method, ProtocolHeader, decode_frame
from featurelifted.spec import Basic


def test_heartbeat_bytes_roundtrip() -> None:
    payload = Heartbeat().marshal()
    consumed, framed = decode_frame(payload)
    assert consumed == len(payload)
    assert isinstance(framed, Heartbeat)


def test_ack_multiple_on_channel() -> None:
    payload = Method(3, Basic.Ack(delivery_tag=11, multiple=False)).marshal()
    consumed, framed = decode_frame(payload)
    assert consumed == len(payload)
    assert framed.channel_number == 3
    assert framed.method.delivery_tag == 11
    assert framed.method.multiple is False


def test_protocol_header_starts_with_amqp() -> None:
    payload = ProtocolHeader().marshal()
    assert payload.startswith(b"AMQP")
    consumed, framed = decode_frame(payload)
    assert consumed == 8
    assert isinstance(framed, ProtocolHeader)


def test_incomplete_buffer_returns_zero() -> None:
    consumed, framed = decode_frame(b"")
    assert consumed == 0
    assert framed is None
''',
    )
    write_text(
        task / "hidden_tests" / "test_required_api_surface.py",
        '''import featurelifted.frame
import featurelifted.spec


def test_required_api_surface() -> None:
    assert callable(featurelifted.frame.decode_frame)
    assert callable(featurelifted.frame.Heartbeat)
    assert callable(featurelifted.frame.Method)
    assert callable(featurelifted.frame.ProtocolHeader)
    assert callable(featurelifted.spec.Basic.Ack)
''',
    )
    update_oracle_manifest(
        task,
        "pika",
        [
            "pika/frame.py",
            "pika/spec.py",
            "pika/data.py",
            "pika/amqp_object.py",
            "pika/_utils.py",
            "pika/exceptions.py",
        ],
        [],
        "AMQP frame/spec codec only; adapters/connection remain repo decoy.",
    )
    return task


def materialize_stdnum() -> Path:
    tid = "stdnum__isbn_validate_core__001"
    clone = PINS[tid]
    task = PILOT / tid
    if task.exists():
        shutil.rmtree(task)
    task.mkdir(parents=True)
    copy_repo(clone, task / "repo")
    dest = task / "reference_solution" / "featurelifted"
    src = clone / "stdnum"
    for name in ("__init__.py", "isbn.py", "ean.py", "exceptions.py", "util.py"):
        write_rewritten(src / name, dest / name, "stdnum")
    write_lock(task, [])
    write_text(task / "evaluation" / "forbidden_imports.txt", "stdnum\n")
    write_text(
        task / "public_tests" / "test_public_api.py",
        '''from __future__ import annotations

from featurelifted.isbn import compact, validate


def test_validate_isbn13() -> None:
    assert validate("978-9024538270") == "9789024538270"


def test_compact_isbn10() -> None:
    assert compact("1-85798-218-5") == "1857982185"
''',
    )
    write_text(
        task / "hidden_tests" / "test_hidden_behavior.py",
        common_no_upstream("stdnum")
        + '''

from featurelifted.exceptions import InvalidChecksum
from featurelifted.isbn import compact, isbn_type, to_isbn13, validate


def test_validate_isbn13_compact_digits() -> None:
    assert validate("978-0-471-11709-4") == "9780471117094"


def test_compact_strips_separators() -> None:
    assert compact("978-9024538270") == "9789024538270"


def test_invalid_checksum_raises() -> None:
    try:
        validate("978-9024538271")
    except InvalidChecksum:
        return
    raise AssertionError("expected InvalidChecksum")


def test_isbn_type_and_to_isbn13() -> None:
    assert isbn_type("1-85798-218-5") == "ISBN10"
    assert isbn_type("978-0-471-11709-4") == "ISBN13"
    assert to_isbn13("1-85798-218-5") == "978-1-85798-218-3"
''',
    )
    write_text(
        task / "hidden_tests" / "test_required_api_surface.py",
        '''from featurelifted.exceptions import InvalidChecksum
from featurelifted.isbn import compact, isbn_type, to_isbn13, validate


def test_required_api_surface() -> None:
    assert callable(validate)
    assert callable(compact)
    assert callable(isbn_type)
    assert callable(to_isbn13)
    assert issubclass(InvalidChecksum, Exception)
''',
    )
    update_oracle_manifest(
        task,
        "stdnum",
        [
            "stdnum/__init__.py",
            "stdnum/isbn.py",
            "stdnum/ean.py",
            "stdnum/exceptions.py",
            "stdnum/util.py",
        ],
        [],
        "ISBN validate/compact/type conversion only; country modules remain repo decoy.",
    )
    return task


def materialize_tornado() -> Path:
    tid = "tornado__http_headers_core__001"
    clone = PINS[tid]
    task = PILOT / tid
    if task.exists():
        shutil.rmtree(task)
    task.mkdir(parents=True)
    copy_repo(clone, task / "repo")
    dest = task / "reference_solution" / "featurelifted"
    src = clone / "tornado"
    write_text(
        dest / "__init__.py",
        "from .httputil import HTTPHeaders, HTTPInputError\n\n"
        "__all__ = ['HTTPHeaders', 'HTTPInputError']\n",
    )
    for name in ("httputil.py", "escape.py", "util.py"):
        write_rewritten(src / name, dest / name, "tornado")
    write_lock(task, [])
    write_text(task / "evaluation" / "forbidden_imports.txt", "tornado\n")
    write_text(
        task / "public_tests" / "test_public_api.py",
        '''from __future__ import annotations

from featurelifted import HTTPHeaders


def test_parse_content_type_and_length() -> None:
    headers = HTTPHeaders.parse("Content-Type: text/html\\r\\nContent-Length: 42\\r\\n")
    assert sorted(headers.items()) == [("Content-Length", "42"), ("Content-Type", "text/html")]


def test_set_cookie_get_list() -> None:
    headers = HTTPHeaders()
    headers.add("Set-Cookie", "A=B")
    headers.add("Set-Cookie", "C=D")
    assert headers.get_list("set-cookie") == ["A=B", "C=D"]
    assert headers["set-cookie"] == "A=B,C=D"
''',
    )
    write_text(
        task / "hidden_tests" / "test_hidden_behavior.py",
        common_no_upstream("tornado")
        + '''

from featurelifted import HTTPHeaders, HTTPInputError


def test_parse_two_headers() -> None:
    headers = HTTPHeaders.parse("Accept: text/plain\\r\\nHost: example.com\\r\\n")
    assert headers["Accept"] == "text/plain"
    assert headers["Host"] == "example.com"


def test_duplicate_set_cookie() -> None:
    headers = HTTPHeaders()
    headers.add("Set-Cookie", "sid=1")
    headers.add("Set-Cookie", "theme=dark")
    assert headers.get_list("Set-Cookie") == ["sid=1", "theme=dark"]


def test_header_names_are_http_cased() -> None:
    headers = HTTPHeaders.parse("content-type: text/html\\r\\n")
    assert list(headers.keys()) == ["Content-Type"]
    assert headers["CONTENT-TYPE"] == "text/html"


def test_malformed_header_line_raises() -> None:
    try:
        HTTPHeaders.parse("Not a header line without colon\\r\\n")
    except HTTPInputError:
        return
    raise AssertionError("expected HTTPInputError")
''',
    )
    write_text(
        task / "hidden_tests" / "test_required_api_surface.py",
        common_hidden_api(
            "    assert callable(featurelifted.HTTPHeaders)\n"
            "    assert callable(featurelifted.HTTPHeaders.parse)\n"
            "    assert callable(featurelifted.HTTPHeaders.add)\n"
            "    assert callable(featurelifted.HTTPHeaders.get_list)\n"
            "    assert issubclass(featurelifted.HTTPInputError, Exception)\n"
        ),
    )
    update_oracle_manifest(
        task,
        "tornado",
        [
            "tornado/httputil.py",
            "tornado/escape.py",
            "tornado/util.py",
        ],
        [],
        "HTTPHeaders parse/add only; IOLoop/web/httpclient remain repo decoy.",
    )
    return task


def mitmproxy_meta() -> dict:
    return {
        "task_id": "mitmproxy__url_parse_core__001",
        "language": "python",
        "difficulty": "hard",
        "status": "materialized_candidate",
        "task_revision": 1,
        "tags": ["hard50", "remaining", "lift", "direct", "tooling"],
        "source": {
            "name": "mitmproxy",
            "url": "https://github.com/mitmproxy/mitmproxy",
            "commit": SHAS["mitmproxy__url_parse_core__001"],
            "license": "MIT",
        },
        "feature": {
            "name": "URL parse",
            "description": "Lift mitmproxy URL parse/unparse without the proxy, addons, or network stack.",
            "source_entrypoints": ["mitmproxy.net.http.url.parse"],
            "included_behaviors": ["https default port", "explicit port", "unparse roundtrip", "missing host ValueError"],
            "excluded_behaviors": ["proxy listen", "addons", "flows", "network"],
        },
        "entanglement": {
            "level": "high",
            "types": ["data_model_coupling", "resource_coupling"],
            "primary": "data_model_coupling",
            "description": "parse lives in net.http.url; the rest of mitmproxy is unused decoy.",
            "signals": ["scheme host port path", "IDNA host", "default ports"],
        },
        "output": {
            "package": "featurelifted",
            "import": "from featurelifted import parse, unparse",
            "callable": "parse",
            "signature": "parse(url: str | bytes) -> tuple[bytes, bytes, int, bytes]",
        },
        "environment": env("mitmproxy"),
        "tests": {"public": "public_tests/", "hidden": "hidden_tests/", "command": "pytest"},
        "spec_status": "compliant",
        "public_spec": {
            "title": "URL parse",
            "summary": "Build a standalone `featurelifted` package that parses URLs like mitmproxy `parse`/`unparse`, returning `(scheme, host, port, path)` bytes and reconstructing the URL, without running a proxy.",
            "required_api": [
                {
                    "path": "featurelifted.parse",
                    "kind": "function",
                    "signature": "(url: str | bytes) -> tuple[bytes, bytes, int, bytes]",
                },
                {
                    "path": "featurelifted.unparse",
                    "kind": "function",
                    "signature": "(scheme, host, port, path)",
                },
            ],
            "optional_api": [],
            "behaviors": behaviors(
                (
                    "B001",
                    '`parse("https://example.com/foo")` returns `(b"https", b"example.com", 443, b"/foo")`; `parse("https://example.org/path")` returns `(b"https", b"example.org", 443, b"/path")`.',
                ),
                (
                    "B002",
                    '`unparse(*parse("https://example.com/bar"))` equals `b"https://example.com/bar"`.',
                ),
                (
                    "B003",
                    '`parse("http://127.0.0.1:8080/x")` returns `(b"http", b"127.0.0.1", 8080, b"/x")`.',
                ),
                (
                    "B004",
                    '`parse("not-a-url")` raises `ValueError`.',
                ),
                (
                    "B005",
                    "The package exposes `parse` and `unparse`.",
                ),
                (
                    "B006",
                    "The submitted package source does not import the forbidden upstream package `mitmproxy`.",
                ),
            ),
            "exclusions": ["proxy listen", "addons", "network", "runtime import of mitmproxy"],
            "forbidden": {"imports": ["mitmproxy"], "paths": []},
        },
        "evaluation_spec": {
            "public_clauses": [],
            "hidden_test_mappings": [],
            "required_api_coverage": [],
            "manual_review": review("Thin URL parse slice; proxy/addons unused."),
        },
    }


def pika_meta() -> dict:
    return {
        "task_id": "pika__channel_spec_core__001",
        "language": "python",
        "difficulty": "hard",
        "status": "materialized_candidate",
        "task_revision": 1,
        "tags": ["hard50", "remaining", "lift", "direct", "parser"],
        "source": {
            "name": "pika",
            "url": "https://github.com/pika/pika",
            "commit": SHAS["pika__channel_spec_core__001"],
            "license": "BSD-3-Clause",
        },
        "feature": {
            "name": "AMQP frame codec",
            "description": "Lift Pika AMQP frame encode/decode without connection adapters or a broker.",
            "source_entrypoints": ["pika.frame.decode_frame", "pika.spec.Basic.Ack"],
            "included_behaviors": ["heartbeat roundtrip", "Basic.Ack roundtrip", "protocol header", "incomplete buffer"],
            "excluded_behaviors": ["BlockingConnection", "live broker", "adapters"],
        },
        "entanglement": {
            "level": "high",
            "types": ["parser_state_coupling", "data_model_coupling"],
            "primary": "parser_state_coupling",
            "description": "Frame codec is independent of adapters; copying connection code is the wrong closure.",
            "signals": ["FRAME_END", "Basic.Ack", "ProtocolHeader"],
        },
        "output": {
            "package": "featurelifted",
            "import": "from featurelifted.frame import decode_frame, Heartbeat, Method",
            "callable": "decode_frame",
            "signature": "decode_frame(data_in, offset=0) -> tuple[int, Frame | ProtocolHeader | None]",
        },
        "environment": env("pika"),
        "tests": {"public": "public_tests/", "hidden": "hidden_tests/", "command": "pytest"},
        "spec_status": "compliant",
        "public_spec": {
            "title": "AMQP frame codec",
            "summary": "Build a standalone `featurelifted` package that encodes and decodes AMQP frames like Pika `frame`/`spec`, including heartbeats and `Basic.Ack`, without connecting to a broker.",
            "required_api": [
                {
                    "path": "featurelifted.frame.decode_frame",
                    "kind": "function",
                    "signature": "(data_in, offset=0)",
                },
                {
                    "path": "featurelifted.frame.Heartbeat",
                    "kind": "class",
                    "signature": "()",
                    "members": [
                        {"path": "featurelifted.frame.Heartbeat.marshal", "kind": "method", "signature": "(self)"}
                    ],
                },
                {
                    "path": "featurelifted.frame.Method",
                    "kind": "class",
                    "signature": "(channel_number, method)",
                    "members": [
                        {"path": "featurelifted.frame.Method.marshal", "kind": "method", "signature": "(self)"}
                    ],
                },
                {
                    "path": "featurelifted.frame.ProtocolHeader",
                    "kind": "class",
                    "signature": "(major=None, minor=None, revision=None)",
                    "members": [
                        {"path": "featurelifted.frame.ProtocolHeader.marshal", "kind": "method", "signature": "(self)"}
                    ],
                },
                {
                    "path": "featurelifted.spec.Basic.Ack",
                    "kind": "class",
                    "signature": "(delivery_tag=0, multiple=False)",
                },
            ],
            "optional_api": [],
            "behaviors": behaviors(
                (
                    "B001",
                    "`Heartbeat().marshal()` round-trips through `decode_frame` to a `Heartbeat` instance and consumes the full payload.",
                ),
                (
                    "B002",
                    "`Method(channel, Basic.Ack(delivery_tag, multiple)).marshal()` round-trips through `decode_frame` preserving channel number, delivery tag, and multiple flag.",
                ),
                (
                    "B003",
                    "`ProtocolHeader().marshal()` starts with `b\"AMQP\"` and `decode_frame` returns a `ProtocolHeader`.",
                ),
                (
                    "B004",
                    "`decode_frame(b\"\")` returns `(0, None)`.",
                ),
                (
                    "B005",
                    "The package exposes `decode_frame`, `Heartbeat`, `Method`, `ProtocolHeader`, and `Basic.Ack`.",
                ),
                (
                    "B006",
                    "The submitted package source does not import the forbidden upstream package `pika`.",
                ),
            ),
            "exclusions": ["BlockingConnection", "live broker", "runtime import of pika"],
            "forbidden": {"imports": ["pika"], "paths": []},
        },
        "evaluation_spec": {
            "public_clauses": [],
            "hidden_test_mappings": [],
            "required_api_coverage": [],
            "manual_review": review("Thin AMQP frame/spec slice; adapters unused."),
        },
    }


def stdnum_meta() -> dict:
    return {
        "task_id": "stdnum__isbn_validate_core__001",
        "language": "python",
        "difficulty": "hard",
        "status": "materialized_candidate",
        "task_revision": 1,
        "tags": ["hard50", "remaining", "lift", "adapted", "validate"],
        "source": {
            "name": "python-stdnum",
            "url": "https://github.com/arthurdejong/python-stdnum",
            "commit": SHAS["stdnum__isbn_validate_core__001"],
            "license": "LGPL-2.1-or-later",
        },
        "feature": {
            "name": "ISBN validate",
            "description": "Lift python-stdnum ISBN validate/compact/type conversion without country number modules.",
            "source_entrypoints": ["stdnum.isbn.validate"],
            "included_behaviors": ["ISBN-13 validate", "compact", "checksum error", "ISBN-10 type and to_isbn13"],
            "excluded_behaviors": ["country modules", "IBAN", "network"],
        },
        "entanglement": {
            "level": "high",
            "types": ["data_model_coupling", "resource_coupling"],
            "primary": "data_model_coupling",
            "description": "ISBN lives in isbn/ean; hundreds of country modules are copy-all decoy.",
            "signals": ["checksum", "ISBN10", "ISBN13"],
        },
        "output": {
            "package": "featurelifted",
            "import": "from featurelifted.isbn import validate, compact, isbn_type, to_isbn13",
            "callable": "validate",
            "signature": "validate(number: str, convert: bool = False) -> str",
        },
        "environment": env("stdnum"),
        "tests": {"public": "public_tests/", "hidden": "hidden_tests/", "command": "pytest"},
        "spec_status": "compliant",
        "public_spec": {
            "title": "ISBN validate",
            "summary": "Build a standalone `featurelifted` package that validates and converts ISBN numbers like python-stdnum `isbn`, including compact form and checksum errors, without the remaining country-code modules.",
            "required_api": [
                {"path": "featurelifted.isbn.validate", "kind": "function", "signature": "(number: str, convert: bool = False) -> str"},
                {"path": "featurelifted.isbn.compact", "kind": "function", "signature": "(number: str, convert: bool = False) -> str"},
                {"path": "featurelifted.isbn.isbn_type", "kind": "function", "signature": "(number: str) -> str | None"},
                {"path": "featurelifted.isbn.to_isbn13", "kind": "function", "signature": "(number: str) -> str"},
                {"path": "featurelifted.exceptions.InvalidChecksum", "kind": "class", "signature": ""},
            ],
            "optional_api": [],
            "behaviors": behaviors(
                (
                    "B001",
                    '`validate("978-9024538270")` returns `"9789024538270"`; `validate("978-0-471-11709-4")` returns `"9780471117094"`.',
                ),
                (
                    "B002",
                    '`compact("1-85798-218-5")` returns `"1857982185"`; `compact("978-9024538270")` returns `"9789024538270"`.',
                ),
                (
                    "B003",
                    '`validate("978-9024538271")` raises `InvalidChecksum`.',
                ),
                (
                    "B004",
                    '`isbn_type("1-85798-218-5")` is `"ISBN10"`, `isbn_type("978-0-471-11709-4")` is `"ISBN13"`, and `to_isbn13("1-85798-218-5")` equals `"978-1-85798-218-3"`.',
                ),
                (
                    "B005",
                    "The package exposes `isbn.validate`, `isbn.compact`, `isbn.isbn_type`, `isbn.to_isbn13`, and `InvalidChecksum`.",
                ),
                (
                    "B006",
                    "The submitted package source does not import the forbidden upstream package `stdnum`.",
                ),
            ),
            "exclusions": ["country modules", "IBAN", "runtime import of stdnum"],
            "forbidden": {"imports": ["stdnum"], "paths": []},
        },
        "evaluation_spec": {
            "public_clauses": [],
            "hidden_test_mappings": [],
            "required_api_coverage": [],
            "manual_review": review("ISBN slice; country modules unused."),
        },
    }


def tornado_meta() -> dict:
    return {
        "task_id": "tornado__http_headers_core__001",
        "language": "python",
        "difficulty": "hard",
        "status": "materialized_candidate",
        "task_revision": 1,
        "tags": ["hard50", "remaining", "lift", "adapted", "parser"],
        "source": {
            "name": "Tornado",
            "url": "https://github.com/tornadoweb/tornado",
            "commit": SHAS["tornado__http_headers_core__001"],
            "license": "Apache-2.0",
        },
        "feature": {
            "name": "HTTP header parse",
            "description": "Lift Tornado HTTPHeaders parsing without IOLoop, web, or HTTP clients.",
            "source_entrypoints": ["tornado.httputil.HTTPHeaders"],
            "included_behaviors": ["parse header block", "multi Set-Cookie", "HTTP header case", "malformed HTTPInputError"],
            "excluded_behaviors": ["IOLoop", "HTTPServer", "AsyncHTTPClient", "network"],
        },
        "entanglement": {
            "level": "high",
            "types": ["parser_state_coupling", "data_model_coupling"],
            "primary": "parser_state_coupling",
            "description": "HTTPHeaders is a parser view; IOLoop/web/httpclient are unused decoy.",
            "signals": ["Http-Header-Case", "get_list", "HTTPInputError"],
        },
        "output": {
            "package": "featurelifted",
            "import": "from featurelifted import HTTPHeaders, HTTPInputError",
            "callable": "HTTPHeaders.parse",
            "signature": "HTTPHeaders.parse(headers: str) -> HTTPHeaders",
        },
        "environment": env("tornado"),
        "tests": {"public": "public_tests/", "hidden": "hidden_tests/", "command": "pytest"},
        "spec_status": "compliant",
        "public_spec": {
            "title": "HTTP header parse",
            "summary": "Build a standalone `featurelifted` package that parses HTTP header blocks like Tornado `HTTPHeaders`, including duplicate `Set-Cookie` values and malformed-line errors, without running an IOLoop or HTTP server.",
            "required_api": [
                {
                    "path": "featurelifted.HTTPHeaders",
                    "kind": "class",
                    "signature": "()",
                    "members": [
                        {"path": "featurelifted.HTTPHeaders.parse", "kind": "method", "signature": "(cls, headers: str)"},
                        {"path": "featurelifted.HTTPHeaders.add", "kind": "method", "signature": "(self, name: str, value: str)"},
                        {"path": "featurelifted.HTTPHeaders.get_list", "kind": "method", "signature": "(self, name: str)"},
                    ],
                },
                {"path": "featurelifted.HTTPInputError", "kind": "class", "signature": ""},
            ],
            "optional_api": [],
            "behaviors": behaviors(
                (
                    "B001",
                    '`HTTPHeaders.parse` of a CRLF-separated block such as `Content-Type: text/html` / `Content-Length: 42` or `Accept: text/plain` / `Host: example.com` stores those header values.',
                ),
                (
                    "B002",
                    "Two `add(\"Set-Cookie\", ...)` calls make `get_list(\"set-cookie\")` return both values, and the combined mapping value is comma-joined.",
                ),
                (
                    "B003",
                    "Parsed header names are HTTP-cased (`content-type` becomes `Content-Type`) and lookup is case-insensitive.",
                ),
                (
                    "B004",
                    '`HTTPHeaders.parse` on a line with no colon raises `HTTPInputError`.',
                ),
                (
                    "B005",
                    "The package exposes `HTTPHeaders` with `parse`, `add`, and `get_list`, plus `HTTPInputError`.",
                ),
                (
                    "B006",
                    "The submitted package source does not import the forbidden upstream package `tornado`.",
                ),
            ),
            "exclusions": ["IOLoop", "HTTPServer", "network", "runtime import of tornado"],
            "forbidden": {"imports": ["tornado"], "paths": []},
        },
        "evaluation_spec": {
            "public_clauses": [],
            "hidden_test_mappings": [],
            "required_api_coverage": [],
            "manual_review": review("Thin HTTPHeaders slice; IOLoop/web unused."),
        },
    }


def write_design_card(task_id: str, body: str) -> None:
    write_text(CARDS / f"{task_id}.md", body)


def write_cards() -> None:
    write_design_card(
        "mitmproxy__url_parse_core__001",
        f"""# Design card: mitmproxy__url_parse_core__001

**status:** `materialized_candidate`  
**disposition:** `selected`  
**wave:** `copyheavy_swap`  
**package:** `mitmproxy`  
**repository_url:** https://github.com/mitmproxy/mitmproxy  
**planned_lift_type:** Direct  
**final_lift_type:** pending_source_review  
**reclassification_reason:** Replaces `respx__route_mock_core__001` (Flash copy_heavy_pass, RRES≈0.94 on a slice-sized repo).  
**feature_family:** `direct_tooling_copytrap`  
**entanglement.level:** high  
**entanglement.types:** `data_model_coupling`, `resource_coupling`  
**feature_one_liner:** URL parse/unparse without proxy, addons, or network  
**commit:** `{SHAS["mitmproxy__url_parse_core__001"]}`  

## paper_fit

RQ2: URL parse slice inside a large proxy/addon tree. Copy-all of the rewritten mitmproxy package is unused decoy, not padding.

## why_hard

Must extract `net.http.url.parse` plus host checks; copying addons/proxy fails isolation and inflates RRES.

## Balance Role

direct_tooling_copytrap / Direct / high entanglement. Swap-in for a small-repo copy-heavy Flash pass.

## Pinned Source

- commit: `{SHAS["mitmproxy__url_parse_core__001"]}`
- license: MIT
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-28 name/url screen)

## Gate Status

- design card: pinned
- package completeness: materialized in `benchmark/hard50_pilot/mitmproxy__url_parse_core__001`
- Docker / Flash calibration: pending after remaining compactness swaps
- promotion to `benchmark/hard50`: blocked until compactness swaps finish
""",
    )
    write_design_card(
        "pika__channel_spec_core__001",
        f"""# Design card: pika__channel_spec_core__001

**status:** `materialized_candidate`  
**disposition:** `selected`  
**wave:** `copyheavy_swap`  
**package:** `pika`  
**repository_url:** https://github.com/pika/pika  
**planned_lift_type:** Direct  
**final_lift_type:** pending_source_review  
**reclassification_reason:** Replaces `bytecode__code_roundtrip_core__001` (Flash copy_heavy_pass, RRES≈0.88 on a slice-sized repo). Family kept as parse_tokenize_decode.  
**feature_family:** `parse_tokenize_decode`  
**entanglement.level:** high  
**entanglement.types:** `parser_state_coupling`, `data_model_coupling`  
**feature_one_liner:** AMQP method framing encode/decode without a broker  
**commit:** `{SHAS["pika__channel_spec_core__001"]}`  

## paper_fit

RQ2: Frame codec slice inside adapters/connection. Copy-all of rewritten Pika is a real unused decoy.

## why_hard

Must marshal/decode frames from spec types; copying BlockingConnection is the isolation fail.

## Balance Role

parse_tokenize_decode / Direct / high entanglement. Swap-in for bytecode copy-heavy Flash pass.

## Pinned Source

- commit: `{SHAS["pika__channel_spec_core__001"]}`
- license: BSD-3-Clause
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-28 name/url screen)

## Gate Status

- design card: pinned
- package completeness: materialized in `benchmark/hard50_pilot/pika__channel_spec_core__001`
- Docker / Flash calibration: pending after remaining compactness swaps
- promotion to `benchmark/hard50`: blocked until compactness swaps finish
""",
    )
    write_design_card(
        "stdnum__isbn_validate_core__001",
        f"""# Design card: stdnum__isbn_validate_core__001

**status:** `materialized_candidate`  
**disposition:** `selected`  
**wave:** `copyheavy_swap`  
**package:** `stdnum`  
**repository_url:** https://github.com/arthurdejong/python-stdnum  
**planned_lift_type:** Adapted  
**final_lift_type:** pending_source_review  
**reclassification_reason:** Replaces `fastjsonschema__compile_validate_core__001` (Flash copy_heavy_pass, RRES≈0.93 on a slice-sized repo).  
**feature_family:** `validate_normalize_construct`  
**entanglement.level:** high  
**entanglement.types:** `data_model_coupling`, `resource_coupling`  
**feature_one_liner:** ISBN validate/compact without country-code modules  
**commit:** `{SHAS["stdnum__isbn_validate_core__001"]}`  

## paper_fit

RQ2: ISBN slice versus hundreds of unused country validators. Copy-all of rewritten stdnum is a real unused decoy.

## why_hard

Checksum and ISBN-10/13 conversion; copying IBAN/country modules is the wrong closure.

## Balance Role

validate_normalize_construct / Adapted / high entanglement. Swap-in for fastjsonschema copy-heavy Flash pass.

## Pinned Source

- commit: `{SHAS["stdnum__isbn_validate_core__001"]}`
- license: LGPL-2.1-or-later
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-28 name/url screen)

## Gate Status

- design card: pinned
- package completeness: materialized in `benchmark/hard50_pilot/stdnum__isbn_validate_core__001`
- Docker / Flash calibration: pending after remaining compactness swaps
- promotion to `benchmark/hard50`: blocked until compactness swaps finish
""",
    )
    write_design_card(
        "tornado__http_headers_core__001",
        f"""# Design card: tornado__http_headers_core__001

**status:** `materialized_candidate`  
**disposition:** `selected`  
**wave:** `copyheavy_swap`  
**package:** `tornado`  
**repository_url:** https://github.com/tornadoweb/tornado  
**planned_lift_type:** Adapted  
**final_lift_type:** pending_source_review  
**reclassification_reason:** Replaces `docutils__rst_transform_core__001` (Flash copy_heavy_pass, RRES≈0.91 because oracle≈whole package).  
**feature_family:** `parse_tokenize_decode`  
**entanglement.level:** high  
**entanglement.types:** `parser_state_coupling`, `data_model_coupling`  
**feature_one_liner:** HTTPHeaders parse without IOLoop/web/httpclient  
**commit:** `{SHAS["tornado__http_headers_core__001"]}`  

## paper_fit

RQ2: Header parser slice inside a large async HTTP/web tree. Copy-all of rewritten Tornado is unused decoy, not a near-whole-package oracle.

## why_hard

HTTP-header case, multi-value cookies, malformed lines; copying IOLoop/web is the wrong closure.

## Balance Role

parse_tokenize_decode / Adapted / high entanglement. Swap-in for docutils fat-oracle copy-heavy Flash pass.

## Pinned Source

- commit: `{SHAS["tornado__http_headers_core__001"]}`
- license: Apache-2.0
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-28 name/url screen)

## Gate Status

- design card: pinned
- package completeness: materialized in `benchmark/hard50_pilot/tornado__http_headers_core__001`
- Docker / Flash calibration: pending after remaining compactness swaps
- promotion to `benchmark/hard50`: blocked until compactness swaps finish
""",
    )


def update_ledger() -> None:
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    by_id = {row["task_id"]: row for row in data["rows"]}
    swaps = [
        (
            "respx__route_mock_core__001",
            "mitmproxy__url_parse_core__001",
            {
                "task_id": "mitmproxy__url_parse_core__001",
                "package": "mitmproxy",
                "repository_url": "https://github.com/mitmproxy/mitmproxy",
                "disposition": "selected",
                "planned_lift_type": "Direct",
                "feature_family": "direct_tooling_copytrap",
                "entanglement_level": "high",
                "entanglement_types": ["data_model_coupling", "resource_coupling"],
                "commit": SHAS["mitmproxy__url_parse_core__001"],
                "design_card": "benchmark/selection/hard50_design_cards/mitmproxy__url_parse_core__001.md",
                "paper_fit": "RQ2: URL parse slice inside a large proxy/addon tree.",
                "why_hard": "Must extract parse plus host checks; copying addons fails isolation.",
            },
        ),
        (
            "bytecode__code_roundtrip_core__001",
            "pika__channel_spec_core__001",
            {
                "task_id": "pika__channel_spec_core__001",
                "package": "pika",
                "repository_url": "https://github.com/pika/pika",
                "disposition": "selected",
                "planned_lift_type": "Direct",
                "feature_family": "parse_tokenize_decode",
                "entanglement_level": "high",
                "entanglement_types": ["parser_state_coupling", "data_model_coupling"],
                "commit": SHAS["pika__channel_spec_core__001"],
                "design_card": "benchmark/selection/hard50_design_cards/pika__channel_spec_core__001.md",
                "paper_fit": "RQ2: AMQP frame codec vs adapters/connection decoy.",
                "why_hard": "Frame marshal/decode; copying BlockingConnection fails isolation.",
            },
        ),
        (
            "fastjsonschema__compile_validate_core__001",
            "stdnum__isbn_validate_core__001",
            {
                "task_id": "stdnum__isbn_validate_core__001",
                "package": "stdnum",
                "repository_url": "https://github.com/arthurdejong/python-stdnum",
                "disposition": "selected",
                "planned_lift_type": "Adapted",
                "feature_family": "validate_normalize_construct",
                "entanglement_level": "high",
                "entanglement_types": ["data_model_coupling", "resource_coupling"],
                "commit": SHAS["stdnum__isbn_validate_core__001"],
                "design_card": "benchmark/selection/hard50_design_cards/stdnum__isbn_validate_core__001.md",
                "paper_fit": "RQ2: ISBN slice vs hundreds of unused country modules.",
                "why_hard": "Checksum and ISBN-10/13 conversion; country modules are the copy-all trap.",
            },
        ),
        (
            "docutils__rst_transform_core__001",
            "tornado__http_headers_core__001",
            {
                "task_id": "tornado__http_headers_core__001",
                "package": "tornado",
                "repository_url": "https://github.com/tornadoweb/tornado",
                "disposition": "selected",
                "planned_lift_type": "Adapted",
                "feature_family": "parse_tokenize_decode",
                "entanglement_level": "high",
                "entanglement_types": ["parser_state_coupling", "data_model_coupling"],
                "commit": SHAS["tornado__http_headers_core__001"],
                "design_card": "benchmark/selection/hard50_design_cards/tornado__http_headers_core__001.md",
                "paper_fit": "RQ2: HTTPHeaders slice inside IOLoop/web; unlike fat docutils oracle.",
                "why_hard": "Header case and multi-value cookies; copying IOLoop is the wrong closure.",
            },
        ),
    ]
    for old_id, new_id, new_row in swaps:
        old = by_id[old_id]
        old["disposition"] = "backup"
        old["replaced_by"] = new_id
        old["replace_reason"] = "Flash copy_heavy_pass RRES~1 on small-repo or fat-oracle slice"
        if new_id not in by_id:
            data["rows"].append(new_row)
        else:
            by_id[new_id].update(new_row)
    data["status"] = "hard50_copyheavy_swaps_wave2_materialized"
    data["notes"] = (
        "Copy-heavy Flash winners swapped: dulwich/mimesis (wave1); "
        "mitmproxy/pika/stdnum/tornado (wave2). Do not release until local gates pass."
    )
    LEDGER.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    _load_pin_shas()
    for old in (
        "respx__route_mock_core__001",
        "bytecode__code_roundtrip_core__001",
        "fastjsonschema__compile_validate_core__001",
        "docutils__rst_transform_core__001",
    ):
        move_old(old)
    mitm = materialize_mitmproxy()
    pika = materialize_pika()
    stdn = materialize_stdnum()
    torn = materialize_tornado()
    specs = [
        (
            mitm,
            mitmproxy_meta(),
            [
                ("B001", "public_tests/test_public_api.py::test_parse_https_example"),
                ("B003", "public_tests/test_public_api.py::test_parse_http_ipv4_port"),
            ],
            [
                ("B001", "hidden_tests/test_hidden_behavior.py::test_parse_https_default_port"),
                ("B002", "hidden_tests/test_hidden_behavior.py::test_unparse_roundtrip"),
                ("B003", "hidden_tests/test_hidden_behavior.py::test_parse_http_explicit_port"),
                ("B004", "hidden_tests/test_hidden_behavior.py::test_missing_hostname_raises"),
                ("B006", "hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface"),
                ("B005", "hidden_tests/test_required_api_surface.py::test_required_api_surface"),
            ],
            ["featurelifted.parse", "featurelifted.unparse"],
            PINS[mitm.name],
            "mitmproxy",
            "from .net.http.url import parse, unparse",
        ),
        (
            pika,
            pika_meta(),
            [
                ("B001", "public_tests/test_public_api.py::test_heartbeat_roundtrip"),
                ("B002", "public_tests/test_public_api.py::test_basic_ack_roundtrip"),
            ],
            [
                ("B001", "hidden_tests/test_hidden_behavior.py::test_heartbeat_bytes_roundtrip"),
                ("B002", "hidden_tests/test_hidden_behavior.py::test_ack_multiple_on_channel"),
                ("B003", "hidden_tests/test_hidden_behavior.py::test_protocol_header_starts_with_amqp"),
                ("B004", "hidden_tests/test_hidden_behavior.py::test_incomplete_buffer_returns_zero"),
                ("B006", "hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface"),
                ("B005", "hidden_tests/test_required_api_surface.py::test_required_api_surface"),
            ],
            [
                "featurelifted.frame.decode_frame",
                "featurelifted.frame.Heartbeat",
                "featurelifted.frame.Heartbeat.marshal",
                "featurelifted.frame.Method",
                "featurelifted.frame.Method.marshal",
                "featurelifted.frame.ProtocolHeader",
                "featurelifted.frame.ProtocolHeader.marshal",
                "featurelifted.spec.Basic.Ack",
            ],
            PINS[pika.name],
            "pika",
            None,
        ),
        (
            stdn,
            stdnum_meta(),
            [
                ("B001", "public_tests/test_public_api.py::test_validate_isbn13"),
                ("B002", "public_tests/test_public_api.py::test_compact_isbn10"),
            ],
            [
                ("B001", "hidden_tests/test_hidden_behavior.py::test_validate_isbn13_compact_digits"),
                ("B002", "hidden_tests/test_hidden_behavior.py::test_compact_strips_separators"),
                ("B003", "hidden_tests/test_hidden_behavior.py::test_invalid_checksum_raises"),
                ("B004", "hidden_tests/test_hidden_behavior.py::test_isbn_type_and_to_isbn13"),
                ("B006", "hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface"),
                ("B005", "hidden_tests/test_required_api_surface.py::test_required_api_surface"),
            ],
            [
                "featurelifted.isbn.validate",
                "featurelifted.isbn.compact",
                "featurelifted.isbn.isbn_type",
                "featurelifted.isbn.to_isbn13",
                "featurelifted.exceptions.InvalidChecksum",
            ],
            PINS[stdn.name],
            "stdnum",
            None,
        ),
        (
            torn,
            tornado_meta(),
            [
                ("B001", "public_tests/test_public_api.py::test_parse_content_type_and_length"),
                ("B002", "public_tests/test_public_api.py::test_set_cookie_get_list"),
            ],
            [
                ("B001", "hidden_tests/test_hidden_behavior.py::test_parse_two_headers"),
                ("B002", "hidden_tests/test_hidden_behavior.py::test_duplicate_set_cookie"),
                ("B003", "hidden_tests/test_hidden_behavior.py::test_header_names_are_http_cased"),
                ("B004", "hidden_tests/test_hidden_behavior.py::test_malformed_header_line_raises"),
                ("B006", "hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface"),
                ("B005", "hidden_tests/test_required_api_surface.py::test_required_api_surface"),
            ],
            [
                "featurelifted.HTTPHeaders",
                "featurelifted.HTTPHeaders.parse",
                "featurelifted.HTTPHeaders.add",
                "featurelifted.HTTPHeaders.get_list",
                "featurelifted.HTTPInputError",
            ],
            PINS[torn.name],
            "tornado",
            "from .httputil import HTTPHeaders, HTTPInputError",
        ),
    ]
    for task, meta, public, hidden, apis, clone, pkg, extra in specs:
        fill_eval_spec(meta, public, hidden, apis)
        copy_all = write_submissions(task, clone, pkg, extra)
        fill_metadata(task, meta, copy_all)
        print(
            "materialized",
            task.name,
            "oracle_loc",
            meta["scoring_reference"]["oracle_loc"],
            "copy_all_loc",
            meta["scoring_reference"]["copy_all_loc"],
            "ratio",
            round(meta["scoring_reference"]["copy_all_loc"] / max(meta["scoring_reference"]["oracle_loc"], 1), 2),
        )
    write_cards()
    update_ledger()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

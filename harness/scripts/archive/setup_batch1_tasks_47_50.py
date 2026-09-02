#!/usr/bin/env python3
"""Scaffold batch-1 staging tasks #47-50 (h2, referencing, wsproto, astroid)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAGING = ROOT / "benchmark" / "staging"
SITE = Path("/Users/chz/anaconda3/lib/python3.12/site-packages")
DESIGNS = ROOT / "docs" / "task_designs"

TASK_IDS = [
    "h2__frame_parse_core__001",
    "referencing__json_schema_refs_core__001",
    "wsproto__frame_parse_core__001",
    "astroid__nodes_core__001",
]

IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache")


def _copy_pkg(src_name: str, dst: Path) -> None:
    src = SITE / src_name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=IGNORE)


def _write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _license_text(pkg: str) -> str:
  dists = sorted(SITE.glob(f"{pkg}-*.dist-info"))
  if not dists:
    return "MIT\n"
  meta = (dists[-1] / "METADATA").read_text(encoding="utf-8", errors="ignore")
  for line in meta.splitlines():
    if line.lower().startswith("license:"):
      return line.split(":", 1)[1].strip() + "\n"
  return "MIT\n"


def copy_h2_repo(repo: Path) -> None:
    _copy_pkg("h2", repo / "h2")
    _copy_pkg("hyperframe", repo / "hyperframe")
    (repo / "LICENSE").write_text(_license_text("h2"), encoding="utf-8")


def copy_referencing_repo(repo: Path) -> None:
    _copy_pkg("referencing", repo / "referencing")
    (repo / "LICENSE").write_text(_license_text("referencing"), encoding="utf-8")


def copy_wsproto_repo(repo: Path) -> None:
    _copy_pkg("wsproto", repo / "wsproto")
    _copy_pkg("h11", repo / "h11")
    (repo / "LICENSE").write_text(_license_text("wsproto"), encoding="utf-8")


def copy_astroid_repo(repo: Path) -> None:
    _copy_pkg("astroid", repo / "astroid")
    (repo / "LICENSE").write_text(_license_text("astroid"), encoding="utf-8")


REPO_SETUP = {
    "h2__frame_parse_core__001": copy_h2_repo,
    "referencing__json_schema_refs_core__001": copy_referencing_repo,
    "wsproto__frame_parse_core__001": copy_wsproto_repo,
    "astroid__nodes_core__001": copy_astroid_repo,
}

TASK_SPECS: dict[str, dict] = {
    "h2__frame_parse_core__001": {
        "source_name": "h2",
        "source_url": "https://github.com/python-hyper/h2",
        "commit": "4.3.0-installed-snapshot",
        "license": "MIT",
        "feature_name": "HTTP/2 frame parse and buffer",
        "description": "Extract hyperframe HTTP/2 frame serialization and h2 FrameBuffer reassembly without connection/stream state machines.",
        "entrypoints": [
            "hyperframe.frame.Frame.parse_frame_header",
            "hyperframe.frame.DataFrame.serialize",
            "h2.frame_buffer.FrameBuffer",
        ],
        "included": [
            "parse and serialize HTTP/2 frames (DATA, HEADERS, PING, SETTINGS, etc.)",
            "FrameBuffer incremental parsing with continuation reassembly",
            "HTTP/2 connection preamble validation for server mode",
            "frame size limits and typed protocol errors",
        ],
        "excluded": [
            "h2 connection and stream state machines",
            "HPACK header compression and flow control windows",
            "network sockets and asyncio integration",
            "original h2 or hyperframe imports at runtime",
        ],
        "entanglement": {
            "level": "high",
            "types": ["parser_state_coupling", "data_model_coupling", "implicit_dependency_coupling"],
            "primary": "parser_state_coupling",
            "description": "Frame parsing couples binary struct layouts, flag validation, continuation backlog state, and cross-package hyperframe/h2 error types.",
            "signals": [
                "FrameBuffer tracks partial headers blocks across CONTINUATION frames",
                "hyperframe frame classes enforce stream-id association rules",
                "server preamble bytes consumed before frame iteration",
                "full h2 package includes large connection/stream modules",
            ],
        },
        "output_import": (
            "from featurelifted.hyperframe.frame import Frame, DataFrame, PingFrame, HeadersFrame, SettingsFrame; "
            "from featurelifted.h2.frame_buffer import FrameBuffer; "
            "from featurelifted.h2.exceptions import ProtocolError, FrameTooLargeError; "
            "from featurelifted.hyperframe.exceptions import InvalidDataError, InvalidFrameError"
        ),
        "callable": "featurelifted.hyperframe.frame.Frame.parse_frame_header",
        "signature": "Frame.parse_frame_header(memoryview) -> tuple[Frame, int]",
        "forbidden": ["h2", "hyperframe"],
        "allowed_dependencies": [],
        "manifest_package": "h2",
        "manifest_notes": "Oracle is hyperframe framing plus h2 FrameBuffer; repo includes full h2 and hyperframe for copy-all penalty.",
    },
    "referencing__json_schema_refs_core__001": {
        "source_name": "referencing",
        "source_url": "https://github.com/python-jsonschema/referencing",
        "commit": "0.30.2-installed-snapshot",
        "license": "MIT",
        "feature_name": "JSON Schema $ref resolution",
        "description": "Extract referencing Registry/Resolver $ref, anchor, and fragment resolution for JSON Schema dialects without jsonschema validator implementations.",
        "entrypoints": [
            "referencing.Registry",
            "referencing.Registry.resolver",
            "referencing.jsonschema.DRAFT202012",
            "referencing.jsonschema.lookup_recursive_ref",
        ],
        "included": [
            "Registry resource registration and base URI resolution",
            "$ref pointer and external URI chaining",
            "$anchor and JSON Schema dialect specifications",
            "typed unresolvable and unknown dialect errors",
        ],
        "excluded": [
            "jsonschema validation keyword implementations",
            "network retrieval of remote schemas",
            "referencing test suite and original package import",
        ],
        "entanglement": {
            "level": "high",
            "types": ["data_model_coupling", "parser_state_coupling", "third_party_dependency_coupling"],
            "primary": "data_model_coupling",
            "description": "Ref resolution couples immutable Registry graphs, Specification dialect hooks, fragment pointer walks, and rpds-backed resolver stacks.",
            "signals": [
                "Specification objects vary anchor and id extraction across draft versions",
                "Resolver maintains dynamic scope for recursive refs",
                "Registry merges resources with URI normalization",
                "repo includes upstream tests for copy-all penalty",
            ],
        },
        "output_import": (
            "from featurelifted import Registry, Resource; "
            "from featurelifted.jsonschema import DRAFT202012, DRAFT7, UnknownDialect; "
            "from featurelifted.exceptions import Unresolvable, NoSuchAnchor"
        ),
        "callable": "featurelifted.Registry.resolver",
        "signature": "Registry.resolver(base_uri: str) -> Resolver",
        "forbidden": ["referencing"],
        "allowed_dependencies": ["attrs", "rpds"],
        "manifest_package": "referencing",
        "manifest_notes": "Oracle is referencing runtime modules; repo includes referencing/tests for copy-all penalty.",
    },
    "wsproto__frame_parse_core__001": {
        "source_name": "wsproto",
        "source_url": "https://github.com/python-hyper/wsproto",
        "commit": "1.3.2-installed-snapshot",
        "license": "MIT",
        "feature_name": "WebSocket frame protocol",
        "description": "Extract wsproto RFC6455 frame parsing, masking, fragmentation, and control frames without HTTP handshake or connection lifecycle.",
        "entrypoints": [
            "wsproto.frame_protocol.FrameProtocol",
            "wsproto.frame_protocol.Opcode",
            "wsproto.frame_protocol.ParseFailed",
        ],
        "included": [
            "parse and serialize text/binary WebSocket frames",
            "client/server masking rules and XOR payload decoding",
            "fragmented message reassembly across continuation frames",
            "ping/pong/close control frames with close codes",
        ],
        "excluded": [
            "HTTP/1.1 upgrade handshake (h11 integration)",
            "WSConnection state machine and extensions negotiation I/O",
            "original wsproto import at runtime",
        ],
        "entanglement": {
            "level": "high",
            "types": ["parser_state_coupling", "resource_coupling", "data_model_coupling"],
            "primary": "parser_state_coupling",
            "description": "Frame protocol couples header length parsing, masking key rotation, message assembly state, and role-specific validation rules.",
            "signals": [
                "FrameDecoder buffers partial headers until length known",
                "server rejects unmasked client frames and vice versa",
                "MessageDecoder tracks continuation opcode sequences",
                "repo includes h11 sibling package for copy-all penalty",
            ],
        },
        "output_import": (
            "from featurelifted.frame_protocol import FrameProtocol, Opcode, ParseFailed, CloseReason, Frame"
        ),
        "callable": "featurelifted.frame_protocol.FrameProtocol",
        "signature": "FrameProtocol(client: bool, extensions: list) -> FrameProtocol",
        "forbidden": ["wsproto"],
        "allowed_dependencies": [],
        "manifest_package": "wsproto",
        "manifest_notes": "Oracle is frame_protocol closure; repo includes wsproto and h11 for copy-all penalty.",
    },
    "astroid__nodes_core__001": {
        "source_name": "astroid",
        "source_url": "https://github.com/PyCQA/astroid",
        "commit": "2.14.2-installed-snapshot",
        "license": "LGPL-2.1-or-later",
        "feature_name": "Astroid parse and nodes subset",
        "description": "Extract astroid string parsing into NodeNG trees via TreeRebuilder without inference, brain plugins, or import introspection.",
        "entrypoints": [
            "astroid.builder.parse",
            "astroid.rebuilder.TreeRebuilder",
            "astroid.nodes",
        ],
        "included": [
            "parse Python source into astroid Module trees",
            "rebuild functions, classes, async, and match statements",
            "preserve docstrings, annotations, and default arguments",
            "NodeNG as_string and basic structural attributes",
        ],
        "excluded": [
            "inference engine and brain module overrides",
            "live object introspection and import graph analysis",
            "pylint integration and original astroid import",
        ],
        "entanglement": {
            "level": "high",
            "types": ["data_model_coupling", "parser_state_coupling", "framework_coupling"],
            "primary": "data_model_coupling",
            "description": "AST rebuilding couples stdlib ast parsing, TreeRebuilder visitor dispatch, scoped node graphs, and manager transform hooks.",
            "signals": [
                "TreeRebuilder maintains global/import-from/delayed-assattr stacks",
                "nodes package mirrors stdlib AST with extra inference hooks",
                "builder applies transform visitors after rebuild",
                "full astroid includes large brain/ inference subsystems",
            ],
        },
        "output_import": "from featurelifted import parse, nodes; from featurelifted.nodes import Module, ClassDef, FunctionDef, AsyncFunctionDef, Match",
        "callable": "featurelifted.parse",
        "signature": "parse(code: str, module_name: str = '', path: str | None = None) -> Module",
        "forbidden": ["astroid"],
        "allowed_dependencies": ["wrapt"],
        "manifest_package": "astroid",
        "manifest_notes": "Oracle is parse/rebuilder/nodes closure without brain or inference; repo is full astroid package.",
    },
}

PUBLIC_TESTS = {
    "h2__frame_parse_core__001": '''\
from __future__ import annotations

from featurelifted.h2.frame_buffer import FrameBuffer
from featurelifted.hyperframe.frame import DataFrame, Frame, PingFrame


def test_ping_frame_roundtrip() -> None:
    raw = PingFrame(0).serialize()
    header = memoryview(raw)[:9]
    frame, _length = Frame.parse_frame_header(header)
    frame.parse_body(memoryview(raw)[9:])
    assert isinstance(frame, PingFrame)
    assert frame.stream_id == 0


def test_data_frame_via_frame_buffer() -> None:
    buf = FrameBuffer()
    buf.max_frame_size = 16384
    payload = DataFrame(1)
    payload.data = b"hello"
    buf.add_data(payload.serialize())
    frames = list(buf)
    assert len(frames) == 1
    assert frames[0].data == b"hello"
''',
    "referencing__json_schema_refs_core__001": '''\
from __future__ import annotations

from featurelifted import Registry
from featurelifted.jsonschema import DRAFT202012


def test_external_ref_resolution() -> None:
    target = DRAFT202012.create_resource({"type": "integer"})
    wrapper = DRAFT202012.create_resource({"$ref": "https://example.com/target"})
    registry = Registry().with_resources(
        [
            ("https://example.com/target", target),
            ("https://example.com/wrapper", wrapper),
        ]
    )
    resolver = registry.resolver("https://example.com/wrapper")
    resolved = resolver.lookup("#").resolver.lookup("https://example.com/target")
    assert resolved.contents == {"type": "integer"}
''',
    "wsproto__frame_parse_core__001": '''\
from __future__ import annotations

from featurelifted.frame_protocol import FrameProtocol


def test_client_receives_unmasked_text() -> None:
    fp = FrameProtocol(client=True, extensions=[])
    fp.receive_bytes(b"\\x81\\x05hello")
    frame = next(fp.received_frames())
    assert frame.payload == "hello"


def test_client_send_data() -> None:
    fp = FrameProtocol(client=True, extensions=[])
    out = fp.send_data("hi", fin=True)
    assert out[0] & 0x0F == 0x1
''',
    "astroid__nodes_core__001": '''\
from __future__ import annotations

from featurelifted import parse


def test_parse_function_and_class() -> None:
    module = parse(
        "class C:\\n"
        "    def m(self, x: int = 1) -> int:\\n"
        "        return x + 1\\n"
    )
    cls = module.body[0]
    assert cls.name == "C"
    fn = cls.body[0]
    assert fn.name == "m"
    assert fn.returns.as_string() == "int"
''',
}

HIDDEN_TESTS = {
    "h2__frame_parse_core__001": '''\
from __future__ import annotations

import pytest

from featurelifted.h2.exceptions import FrameTooLargeError, ProtocolError
from featurelifted.h2.frame_buffer import FrameBuffer
from featurelifted.hyperframe.exceptions import InvalidDataError
from featurelifted.hyperframe.frame import (
    ContinuationFrame,
    DataFrame,
    Frame,
    HeadersFrame,
    PingFrame,
)


def test_ping_stream_id_must_be_zero() -> None:
    with pytest.raises(InvalidDataError):
        PingFrame(1)


def test_frame_buffer_rejects_bad_preamble() -> None:
    buf = FrameBuffer(server=True)
    with pytest.raises(ProtocolError):
        buf.add_data(b"NOTHTTP2")


def test_frame_buffer_enforces_max_frame_size() -> None:
    buf = FrameBuffer()
    buf.max_frame_size = 4
    frame = DataFrame(1)
    frame.data = b"12345"
    with pytest.raises(FrameTooLargeError):
        buf.add_data(frame.serialize())
        list(buf)


def test_continuation_reassembly() -> None:
    buf = FrameBuffer()
    buf.max_frame_size = 16384
    headers = HeadersFrame(3)
    headers.data = b"part-a"
    cont = ContinuationFrame(3)
    cont.data = b"part-b"
    cont.flags.add("END_HEADERS")
    buf.add_data(headers.serialize() + cont.serialize())
    out = list(buf)
    assert len(out) == 1
    assert isinstance(out[0], HeadersFrame)
    assert out[0].data == b"part-apart-b"
''',
    "referencing__json_schema_refs_core__001": '''\
from __future__ import annotations

import pytest

from featurelifted import Registry
from featurelifted.exceptions import NoSuchAnchor, Unresolvable
from featurelifted.jsonschema import DRAFT202012, UnknownDialect


def test_fragment_ref_into_defs() -> None:
    doc = DRAFT202012.create_resource(
        {
            "type": "object",
            "properties": {"child": {"$ref": "#/$defs/inner"}},
            "$defs": {"inner": {"type": "string"}},
        }
    )
    registry = Registry().with_resource("https://example.com/doc", doc)
    resolved = registry.resolver("https://example.com/doc").lookup("#/$defs/inner")
    assert resolved.contents == {"type": "string"}


def test_anchor_lookup() -> None:
    doc = DRAFT202012.create_resource({"$anchor": "foo", "type": "number"})
    registry = Registry().with_resource("https://example.com/doc", doc)
    resolved = registry.resolver("https://example.com/doc").lookup("#foo")
    assert resolved.contents["type"] == "number"


def test_unknown_dialect_and_missing_anchor() -> None:
    from featurelifted import Resource

    with pytest.raises(UnknownDialect):
        Resource.from_contents({"$schema": "https://example.com/unknown"})

    doc = DRAFT202012.create_resource({"type": "string"})
    registry = Registry().with_resource("https://example.com/doc", doc)
    with pytest.raises(NoSuchAnchor):
        registry.resolver("https://example.com/doc").lookup("#missing")


def test_unresolvable_external_ref() -> None:
    wrapper = DRAFT202012.create_resource({"$ref": "https://example.com/missing"})
    registry = Registry().with_resource("https://example.com/here", wrapper)
    resolved = registry.resolver("https://example.com/here").lookup("#")
    with pytest.raises(Unresolvable):
        resolved.resolver.lookup("https://example.com/missing")
''',
    "wsproto__frame_parse_core__001": '''\
from __future__ import annotations

import pytest

from featurelifted.frame_protocol import CloseReason, FrameProtocol, ParseFailed


def test_server_decodes_masked_client_frame() -> None:
    fp = FrameProtocol(client=False, extensions=[])
    key = bytes([1, 2, 3, 4])
    payload = b"abc"
    masked = bytearray([0x81, 0x80 | len(payload)]) + bytearray(key)
    masked += bytearray(payload[i] ^ key[i % 4] for i in range(len(payload)))
    fp.receive_bytes(masked)
    frame = next(fp.received_frames())
    assert frame.payload == "abc"


def test_fragmented_message_reassembly() -> None:
    fp = FrameProtocol(client=True, extensions=[])
    fp.receive_bytes(b"\\x01\\x05hello")
    fp.receive_bytes(b"\\x00\\x03wor")
    frames = list(fp.received_frames())
    assert frames[0].payload == "hello"
    assert frames[1].payload == "wor"
    assert frames[1].message_finished is False


def test_close_frame_code_and_reason() -> None:
    sender = FrameProtocol(client=True, extensions=[])
    payload = sender.close(code=1000, reason="bye")
    receiver = FrameProtocol(client=False, extensions=[])
    receiver.receive_bytes(payload)
    frame = next(receiver.received_frames())
    code, reason = frame.payload
    assert code == 1000
    assert reason == "bye"


def test_role_masking_validation() -> None:
    fp = FrameProtocol(client=False, extensions=[])
    with pytest.raises(ParseFailed):
        fp.receive_bytes(b"\\x81\\x05hello")
        list(fp.received_frames())
''',
    "astroid__nodes_core__001": '''\
from __future__ import annotations

from featurelifted import parse


def test_async_and_match_statements() -> None:
    async_mod = parse("async def f():\\n    await g()\\n")
    assert async_mod.body[0].name == "f"
    assert async_mod.body[0].body[0].value.func.name == "g"

    match_mod = parse("match x:\\n  case 1:\\n    pass\\n")
    match_stmt = match_mod.body[0]
    assert match_stmt.__class__.__name__ == "Match"
    assert match_stmt.cases[0].pattern.value == 1


def test_defaults_and_docstring() -> None:
    module = parse(
        "class C:\\n"
        '    """docstring"""\\n'
        "\\n"
        "    def m(self, x: int = 1) -> int:\\n"
        "        return x + 1\\n"
    )
    cls = module.body[0]
    assert cls.doc_node.value == "docstring"
    fn = cls.body[0]
    assert fn.args.annotations[1].as_string() == "int"
    assert fn.args.defaults[0].value == 1


def test_module_as_string_contains_def() -> None:
    module = parse("def f():\\n    return 1\\n")
    text = module.as_string()
    assert "def f" in text
    assert "return 1" in text
''',
}

DESIGN_PROBES = {
    "h2__frame_parse_core__001": [
        ("hyperframe frames", "`featurelifted/hyperframe/frame.py`", "`test_ping_stream_id_must_be_zero`"),
        ("FrameBuffer", "`featurelifted/h2/frame_buffer.py`", "`test_continuation_reassembly`"),
        ("h2 exceptions", "`featurelifted/h2/exceptions.py`", "`test_frame_buffer_rejects_bad_preamble`"),
    ],
    "referencing__json_schema_refs_core__001": [
        ("Registry core", "`featurelifted/_core.py`", "`test_unresolvable_external_ref`"),
        ("JSON Schema dialect", "`featurelifted/jsonschema.py`", "`test_unknown_dialect_and_missing_anchor`"),
        ("Exceptions", "`featurelifted/exceptions.py`", "`test_anchor_lookup`"),
    ],
    "wsproto__frame_parse_core__001": [
        ("Frame fragmentation", "`featurelifted/frame_protocol.py`", "`test_fragmented_message_reassembly`"),
        ("Frame masking rules", "`featurelifted/frame_protocol.py`", "`test_role_masking_validation`"),
        ("Masked server decode", "`featurelifted/frame_protocol.py`", "`test_server_decodes_masked_client_frame`"),
    ],
    "astroid__nodes_core__001": [
        ("TreeRebuilder", "`featurelifted/rebuilder.py`", "`test_async_and_match_statements`"),
        ("Nodes package", "`featurelifted/nodes/`", "`test_defaults_and_docstring`"),
        ("Builder", "`featurelifted/builder.py`", "`test_module_as_string_contains_def`"),
    ],
}

def write_naive(task_id: str) -> None:
    naive_root = ROOT / "benchmark" / "submissions" / task_id / "naive"
    if naive_root.exists():
        shutil.rmtree(naive_root)
    writers = {
        "h2__frame_parse_core__001": _write_naive_h2,
        "referencing__json_schema_refs_core__001": _write_naive_referencing,
        "wsproto__frame_parse_core__001": _write_naive_wsproto,
        "astroid__nodes_core__001": _write_naive_astroid,
    }
    writers[task_id]()


def _write_naive_h2() -> None:
    root = ROOT / "benchmark" / "submissions" / "h2__frame_parse_core__001" / "naive" / "featurelifted"
    (root / "hyperframe").mkdir(parents=True, exist_ok=True)
    (root / "h2").mkdir(parents=True, exist_ok=True)
    (root / "hyperframe" / "frame.py").write_text(H2_NAIVE_HYPERFRAME_FRAME, encoding="utf-8")
    (root / "hyperframe" / "exceptions.py").write_text(
        "class InvalidDataError(Exception):\n    pass\n\n\nclass InvalidFrameError(Exception):\n    pass\n",
        encoding="utf-8",
    )
    (root / "h2" / "frame_buffer.py").write_text(H2_NAIVE_FRAME_BUFFER, encoding="utf-8")
    (root / "h2" / "exceptions.py").write_text(
        "class ProtocolError(Exception):\n    pass\n\n\nclass FrameTooLargeError(ProtocolError):\n    pass\n",
        encoding="utf-8",
    )
    (root / "__init__.py").write_text('"""Naive h2 frame stub."""\n', encoding="utf-8")


H2_NAIVE_HYPERFRAME_FRAME = '''\
from __future__ import annotations

import struct

from featurelifted.hyperframe.exceptions import InvalidDataError


class Frame:
    type: int | None = None

    @classmethod
    def parse_frame_header(cls, data: memoryview) -> tuple["Frame", int]:
        length = (data[0] << 16) | (data[1] << 8) | data[2]
        ftype = data[3]
        stream_id = struct.unpack(">I", data[5:9])[0] & 0x7FFFFFFF
        frame_cls = {
            0x0: DataFrame,
            0x1: HeadersFrame,
            0x6: PingFrame,
            0x9: ContinuationFrame,
        }.get(ftype, Frame)
        if frame_cls is Frame:
            frame = Frame()
        else:
            frame = frame_cls(stream_id)
        frame.stream_id = stream_id
        frame.body_len = length
        return frame, length

    def parse_body(self, data: memoryview) -> None:
        self.data = bytes(data)


class DataFrame(Frame):
    def __init__(self, stream_id: int) -> None:
        self.stream_id = stream_id
        self.data = b""

    def serialize(self) -> bytes:
        body = self.data
        header = bytes([0, 0, len(body), 0, 0]) + struct.pack(">I", self.stream_id)
        return header + body


class PingFrame(Frame):
    def __init__(self, stream_id: int) -> None:
        self.stream_id = stream_id

    def serialize(self) -> bytes:
        body = b"\\x00" * 8
        header = bytes([0, 0, len(body), 6, 0]) + struct.pack(">I", self.stream_id)
        return header + body


class HeadersFrame(Frame):
    def __init__(self, stream_id: int) -> None:
        self.stream_id = stream_id
        self.data = b""
        self.flags = set()


class ContinuationFrame(Frame):
    def __init__(self, stream_id: int) -> None:
        self.stream_id = stream_id
        self.data = b""
        self.flags = set()


class SettingsFrame(Frame):
    pass
'''

H2_NAIVE_FRAME_BUFFER = '''\
from __future__ import annotations

from featurelifted.hyperframe.frame import (
    ContinuationFrame,
    DataFrame,
    Frame,
    HeadersFrame,
)


class FrameBuffer:
    def __init__(self, server: bool = False) -> None:
        self._data = bytearray()
        self.max_frame_size = 2**14
        self._preamble = b"PRI * HTTP/2.0\\r\\n\\r\\nSM\\r\\n\\r\\n" if server else b""

    def add_data(self, data: bytes) -> None:
        if self._preamble:
            if not data.startswith(self._preamble[: min(len(self._preamble), len(data))]):
                from featurelifted.h2.exceptions import ProtocolError

                raise ProtocolError("bad preamble")
            data = data[len(self._preamble) :]
            self._preamble = b""
        self._data += data

    def __iter__(self):
        while len(self._data) >= 9:
            frame, length = Frame.parse_frame_header(memoryview(self._data[:9]))
            total = 9 + length
            if len(self._data) < total:
                break
            if length > self.max_frame_size:
                from featurelifted.h2.exceptions import FrameTooLargeError

                raise FrameTooLargeError(length)
            frame.parse_body(memoryview(self._data[9:total]))
            del self._data[:total]
            yield frame
'''


def _write_naive_referencing() -> None:
    root = ROOT / "benchmark" / "submissions" / "referencing__json_schema_refs_core__001" / "naive" / "featurelifted"
    root.mkdir(parents=True, exist_ok=True)
    (root / "__init__.py").write_text(REF_NAIVE_INIT, encoding="utf-8")
    (root / "jsonschema.py").write_text(REF_NAIVE_JSONSCHEMA, encoding="utf-8")
    (root / "exceptions.py").write_text(
        "class Unresolvable(Exception):\n    pass\n\n\nclass NoSuchAnchor(Exception):\n    pass\n",
        encoding="utf-8",
    )


REF_NAIVE_INIT = '''\
"""Naive one-hop $ref resolver."""

from __future__ import annotations

from typing import Any

from featurelifted.exceptions import NoSuchAnchor, Unresolvable
from featurelifted.jsonschema import DRAFT202012, DRAFT7, UnknownDialect


class _Resolved:
    def __init__(self, contents: Any, resolver: "_Resolver | None" = None) -> None:
        self.contents = contents
        self.resolver = resolver or _Resolver.empty()


class Resource:
    def __init__(self, contents: Any) -> None:
        self.contents = contents

    @classmethod
    def from_contents(cls, contents: Any) -> "Resource":
        if isinstance(contents, dict) and contents.get("$schema") == "https://example.com/unknown":
            raise UnknownDialect(contents["$schema"])
        return cls(contents)


class _Resolver:
    empty_registry: "Registry | None" = None

    def __init__(self, registry: "Registry", base_uri: str) -> None:
        self._registry = registry
        self._base = base_uri

    @classmethod
    def empty(cls) -> "_Resolver":
        if cls.empty_registry is None:
            cls.empty_registry = Registry()
        return cls(registry=cls.empty_registry, base_uri="")

    def lookup(self, ref: str) -> _Resolved:
        if ref == "#":
            doc = self._registry._docs.get(self._base, {})
            return _Resolved(self._resolve_once(doc), resolver=self)
        if ref.startswith("http"):
            doc = self._registry._docs.get(ref)
            if doc is None:
                raise Unresolvable(ref)
            return _Resolved(self._resolve_once(doc), resolver=self)
        raise Unresolvable(ref)

    def _resolve_once(self, doc: dict[str, Any]) -> dict[str, Any]:
        while isinstance(doc, dict) and "$ref" in doc:
            target = doc["$ref"]
            if target.startswith("http"):
                doc = self._registry._docs.get(target, doc)
            else:
                break
        return doc


class Registry:
    def __init__(self) -> None:
        self._docs: dict[str, Any] = {}

    def with_resource(self, uri: str, resource: Resource) -> "Registry":
        out = Registry()
        out._docs = dict(self._docs)
        out._docs[uri] = resource.contents
        return out

    def with_resources(self, pairs: list[tuple[str, Resource]]) -> "Registry":
        out = Registry()
        out._docs = dict(self._docs)
        for uri, resource in pairs:
            out._docs[uri] = resource.contents
        return out

    def resolver(self, base_uri: str) -> _Resolver:
        return _Resolver(self, base_uri)


__all__ = ["Registry", "Resource", "DRAFT202012", "DRAFT7", "UnknownDialect"]
'''

REF_NAIVE_JSONSCHEMA = '''\
from __future__ import annotations

from typing import Any


class UnknownDialect(Exception):
    def __init__(self, uri: str) -> None:
        self.uri = uri


class _Spec:
    def create_resource(self, contents: Any):
        if isinstance(contents, dict) and contents.get("$schema") == "https://example.com/unknown":
            raise UnknownDialect(contents["$schema"])
        from featurelifted import Resource

        return Resource(contents)


DRAFT202012 = _Spec()
DRAFT7 = _Spec()
'''


def _write_naive_wsproto() -> None:
    root = ROOT / "benchmark" / "submissions" / "wsproto__frame_parse_core__001" / "naive" / "featurelifted"
    root.mkdir(parents=True, exist_ok=True)
    (root / "frame_protocol.py").write_text(WS_NAIVE_FRAME_PROTOCOL, encoding="utf-8")
    (root / "events.py").write_text(
        "class Frame:\n    def __init__(self, opcode, payload, frame_finished=True, message_finished=True):\n"
        "        self.opcode = opcode\n        self.payload = payload\n"
        "        self.frame_finished = frame_finished\n        self.message_finished = message_finished\n",
        encoding="utf-8",
    )
    (root / "__init__.py").write_text('"""Naive wsproto frame stub."""\n', encoding="utf-8")


WS_NAIVE_FRAME_PROTOCOL = '''\
from __future__ import annotations

from enum import IntEnum

from featurelifted.events import Frame


class Opcode(IntEnum):
    TEXT = 0x1
    CLOSE = 0x8


class ParseFailed(Exception):
    pass


class CloseReason:
    NORMAL_CLOSURE = 1000


class FrameProtocol:
    def __init__(self, client: bool, extensions: list) -> None:
        self.client = client
        self._buf = bytearray()

    def receive_bytes(self, data: bytes) -> None:
        self._buf += data

    def received_frames(self):
        while len(self._buf) >= 2:
            b0, b1 = self._buf[0], self._buf[1]
            length = b1 & 0x7F
            offset = 2
            total = offset + length
            if len(self._buf) < total:
                return
            payload = bytes(self._buf[offset:total])
            del self._buf[:total]
            opcode = Opcode(b0 & 0x0F)
            if opcode == Opcode.TEXT:
                payload = payload.decode("utf-8")
            yield Frame(opcode, payload)

    def send_data(self, payload: str | bytes = b"", fin: bool = True) -> bytearray:
        if isinstance(payload, str):
            payload = payload.encode("utf-8")
        return bytearray([0x80 | 0x1, len(payload)]) + bytearray(payload)

    def close(self, code: int | None = None, reason: str | None = None) -> bytearray:
        body = bytearray()
        if code is not None:
            body += code.to_bytes(2, "big")
            if reason:
                body += reason.encode("utf-8")
        return bytearray([0x88, len(body)]) + body
'''


def _write_naive_astroid() -> None:
    root = ROOT / "benchmark" / "submissions" / "astroid__nodes_core__001" / "naive" / "featurelifted"
    root.mkdir(parents=True, exist_ok=True)
    (root / "__init__.py").write_text(ASTROID_NAIVE, encoding="utf-8")


ASTROID_NAIVE = '''\
"""Naive ast parse wrapper using stdlib ast only."""

from __future__ import annotations

import ast
from types import SimpleNamespace


class nodes:
    Module = SimpleNamespace
    ClassDef = SimpleNamespace
    FunctionDef = SimpleNamespace
    AsyncFunctionDef = SimpleNamespace
    Match = SimpleNamespace


def _wrap(node: ast.AST) -> SimpleNamespace:
    ns = SimpleNamespace()
    ns.__class__.__name__ = type(node).__name__
    for field, value in ast.iter_fields(node):
        if isinstance(value, list):
            setattr(ns, field, [_wrap(x) if isinstance(x, ast.AST) else x for x in value])
        elif isinstance(value, ast.AST):
            setattr(ns, field, _wrap(value))
        else:
            setattr(ns, field, value)
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        anns = [None] * len(node.args.args)
        for index, arg in enumerate(node.args.args):
            if arg.annotation is not None:
                anns[index] = SimpleNamespace(as_string=lambda a=arg.annotation: ast.unparse(a))
        ns.args = SimpleNamespace(annotations=anns, defaults=list(node.args.defaults))
        ns.returns = SimpleNamespace(as_string=lambda: ast.unparse(node.returns) if node.returns else "None")
    if isinstance(node, ast.ClassDef) and ast.get_docstring(node):
        ns.doc_node = SimpleNamespace(value=ast.get_docstring(node))
    if isinstance(node, ast.Module):
        ns.as_string = lambda n=node: ast.unparse(n)
    return ns


def parse(code: str, module_name: str = "", path: str | None = None):
    return _wrap(ast.parse(code))
'''


def write_design(task_id: str, spec: dict) -> None:
    probes = DESIGN_PROBES[task_id]
    rows = "\n".join(f"| {a} | {b} | {c} |" for a, b, c in probes)
    text = f"""# Task Design: `{task_id}`

Status: draft-spike

## Practical reuse

1. **Reuse module** — {spec["description"]}
2. **Who imports it** — Teams building protocol stacks, schema tooling, or static analysis without vendoring full upstream packages.
3. **Why not copy-all** — Curated snapshot includes sibling modules; compact closure keeps {spec["feature_name"].lower()} only.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
{rows}

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | |
| Hidden tests | pass | |
| ExtractionRatio | 0.20 – 0.60 | |
| Copy-All delta | ≥ 0.25 | |

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| | | | | | Flash deferred (batch-1 #47-50) |
"""
    (DESIGNS / f"{task_id}.md").write_text(text, encoding="utf-8")


def write_task(task_id: str) -> None:
    spec = TASK_SPECS[task_id]
    task_dir = STAGING / task_id
    for sub in ("public_tests", "hidden_tests", "evaluation"):
        (task_dir / sub).mkdir(parents=True, exist_ok=True)
    repo = task_dir / "repo"
    repo.mkdir(exist_ok=True)
    REPO_SETUP[task_id](repo)
    (task_dir / "requirements.lock").write_text("", encoding="utf-8")
    forbidden = spec["forbidden"]
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text(
        "\n".join(forbidden) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "source_package_name": spec["manifest_package"],
        "required_source_files": [],
        "notes": spec["manifest_notes"],
    }
    _write_json(task_dir / "evaluation" / "oracle_manifest.json", manifest)
    metadata = {
        "task_id": task_id,
        "language": "python",
        "difficulty": "hard",
        "tags": [
            "batch-1",
            spec["source_name"].replace("-", "_"),
            "hard-first",
            "functional-discriminator",
            spec["entanglement"]["primary"],
        ],
        "source": {
            "name": spec["source_name"],
            "url": spec["source_url"],
            "commit": spec["commit"],
            "license": spec["license"],
        },
        "feature": {
            "name": spec["feature_name"],
            "description": spec["description"],
            "source_entrypoints": spec["entrypoints"],
            "included_behaviors": spec["included"],
            "excluded_behaviors": spec["excluded"],
        },
        "entanglement": spec["entanglement"],
        "output": {
            "package": "featurelifted",
            "import": spec["output_import"],
            "callable": spec["callable"],
            "signature": spec["signature"],
        },
        "environment": {
            "python": "3.11",
            "network": False,
            "timeout_seconds": 60,
            "dependency_lock": "requirements.lock",
            "allowed_dependencies": spec.get("allowed_dependencies", []),
            "forbidden_dependencies": forbidden,
            "forbidden_imports": forbidden,
        },
        "tests": {
            "public": "public_tests/",
            "hidden": "hidden_tests/",
            "command": "pytest",
        },
    }
    _write_json(task_dir / "metadata.json", metadata)
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        PUBLIC_TESTS[task_id],
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        HIDDEN_TESTS[task_id],
        encoding="utf-8",
    )
    write_design(task_id, spec)
    write_naive(task_id)
    print(f"scaffolded {task_id}")


def main() -> None:
    for task_id in TASK_IDS:
        write_task(task_id)


if __name__ == "__main__":
    main()

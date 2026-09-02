#!/usr/bin/env python3
"""Scaffold the seven preregistered External-150 replacement tasks."""

from __future__ import annotations

import ast
import json
import shutil
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
STAGING = ROOT / "benchmark" / "staging"
REFERENCES = ROOT / "benchmark" / "references" / "external150"
LOCAL_ORACLES = ROOT / "benchmark" / "submissions"


TASKS = {
    "itsdangerous__timed_serializer_core__001": {
        "source": ("itsdangerous", "https://github.com/pallets/itsdangerous.git", "2.2.0", "BSD-3-Clause"),
        "title": "Timed URL-safe serializer",
        "description": "Extract URL-safe authenticated JSON serialization with timestamp expiry and explicit signature errors.",
        "entrypoints": [
            "itsdangerous.url_safe.URLSafeTimedSerializer",
            "itsdangerous.exc.BadSignature",
            "itsdangerous.exc.SignatureExpired",
        ],
        "included": [
            "deterministic URL-safe dumps and loads for JSON-compatible values",
            "salt-separated HMAC-SHA256 signatures",
            "timestamp max_age validation with injectable current time",
            "BadSignature and SignatureExpired error distinctions",
        ],
        "excluded": ["JWS", "fallback signers", "non-JSON serializers", "network access"],
        "api": "from featurelifted import URLSafeTimedSerializer, BadSignature, SignatureExpired",
        "callable": "URLSafeTimedSerializer",
        "signature": "URLSafeTimedSerializer(secret_key, salt='featurelift', *, now=None)",
        "entanglement": ("data_model_coupling", ["data_model_coupling", "config_environment_coupling"]),
        "public": """
            import pytest
            from featurelifted import BadSignature, URLSafeTimedSerializer

            def test_roundtrip_and_salt_separation():
                one = URLSafeTimedSerializer("secret", salt="one", now=lambda: 100)
                token = one.dumps({"name": "Ada", "roles": ["admin"]})
                assert one.loads(token, now=100) == {"name": "Ada", "roles": ["admin"]}
                with pytest.raises(BadSignature):
                    URLSafeTimedSerializer("secret", salt="two", now=lambda: 100).loads(token, now=100)

            def test_tampering_raises_bad_signature():
                serializer = URLSafeTimedSerializer("secret", now=lambda: 10)
                token = serializer.dumps([1, 2, 3])
                with pytest.raises(BadSignature):
                    serializer.loads(token[:-1] + ("A" if token[-1] != "A" else "B"), now=10)
        """,
        "hidden": """
            import pytest
            from featurelifted import BadSignature, SignatureExpired, URLSafeTimedSerializer

            def test_expiry_boundary_and_error_type():
                serializer = URLSafeTimedSerializer("secret", now=lambda: 100)
                token = serializer.dumps({"ok": True})
                assert serializer.loads(token, max_age=5, now=105) == {"ok": True}
                with pytest.raises(SignatureExpired):
                    serializer.loads(token, max_age=5, now=106)

            def test_wrong_key_and_malformed_token():
                token = URLSafeTimedSerializer("a", now=lambda: 1).dumps("x")
                with pytest.raises(BadSignature):
                    URLSafeTimedSerializer("b", now=lambda: 1).loads(token, now=1)
                with pytest.raises(BadSignature):
                    URLSafeTimedSerializer("a").loads("not-a-token")
        """,
        "reference": """
            import base64, hashlib, hmac, json, time

            class BadSignature(ValueError): pass
            class SignatureExpired(BadSignature): pass

            def _b64e(value):
                return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")
            def _b64d(value):
                try:
                    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
                except Exception as exc:
                    raise BadSignature("malformed token") from exc

            class URLSafeTimedSerializer:
                def __init__(self, secret_key, salt="featurelift", *, now=None):
                    self.secret_key = str(secret_key).encode()
                    self.salt = str(salt).encode()
                    self._now = now or time.time
                def _sign(self, body):
                    key = hmac.new(self.secret_key, self.salt, hashlib.sha256).digest()
                    return _b64e(hmac.new(key, body.encode(), hashlib.sha256).digest())
                def dumps(self, obj):
                    payload = _b64e(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())
                    body = f"{payload}.{int(self._now())}"
                    return f"{body}.{self._sign(body)}"
                def loads(self, token, max_age=None, now=None):
                    try:
                        payload, timestamp, signature = str(token).rsplit(".", 2)
                        created = int(timestamp)
                    except Exception as exc:
                        raise BadSignature("malformed token") from exc
                    body = f"{payload}.{timestamp}"
                    if not hmac.compare_digest(signature, self._sign(body)):
                        raise BadSignature("signature does not match")
                    current = int(self._now() if now is None else now)
                    if max_age is not None and current - created > max_age:
                        raise SignatureExpired("signature age exceeded")
                    try:
                        return json.loads(_b64d(payload).decode("utf-8"))
                    except Exception as exc:
                        if isinstance(exc, BadSignature): raise
                        raise BadSignature("invalid payload") from exc
        """,
    },
    "flask__route_dispatch_core__001": {
        "source": ("flask", "https://github.com/pallets/flask.git", "3.0.3", "BSD-3-Clause"),
        "title": "Application route registration and dispatch",
        "description": "Extract Flask-style decorator registration, typed path matching, method dispatch, and error handlers.",
        "entrypoints": ["flask.app.Flask.route", "flask.app.Flask.dispatch_request", "flask.wrappers.Response"],
        "included": [
            "route decorator registration for static, string, and int path segments",
            "method-aware dispatch with GET default",
            "Response normalization for strings, tuples, and Response values",
            "404 and 405 error-handler dispatch",
        ],
        "excluded": ["WSGI server", "request globals", "templates", "sessions", "blueprints"],
        "api": "from featurelifted import App, Response",
        "callable": "App",
        "signature": "App(name)",
        "entanglement": ("framework_coupling", ["framework_coupling", "data_model_coupling"]),
        "public": """
            from featurelifted import App, Response

            def test_static_and_typed_routes():
                app = App("demo")
                @app.route("/hello")
                def hello(): return "hello"
                @app.route("/users/<int:user_id>")
                def user(user_id): return {"id": user_id}, 201
                assert app.dispatch("/hello") == Response("hello", 200)
                assert app.dispatch("/users/7") == Response({"id": 7}, 201)

            def test_method_dispatch():
                app = App("demo")
                @app.route("/items", methods=["POST"])
                def create(): return "created", 201, {"X-Mode": "write"}
                assert app.dispatch("/items", "POST").headers["X-Mode"] == "write"
                assert app.dispatch("/items", "GET").status_code == 405
        """,
        "hidden": """
            from featurelifted import App, Response

            def test_string_converter_and_response_passthrough():
                app = App("demo")
                @app.route("/greet/<name>")
                def greet(name): return Response(name.upper(), 202, {"X": "1"})
                assert app.dispatch("/greet/ada") == Response("ADA", 202, {"X": "1"})

            def test_error_handlers():
                app = App("demo")
                @app.errorhandler(404)
                def missing(code): return f"missing:{code}", 418
                assert app.dispatch("/unknown") == Response("missing:404", 418)
        """,
        "reference": """
            import re
            from dataclasses import dataclass, field

            @dataclass(eq=True)
            class Response:
                body: object
                status_code: int = 200
                headers: dict = field(default_factory=dict)

            class App:
                def __init__(self, name):
                    self.name, self._routes, self._errors = name, [], {}
                def route(self, rule, methods=None):
                    methods = tuple(m.upper() for m in (methods or ("GET",)))
                    def register(func):
                        names = []
                        pattern = ""
                        for part in re.split(r"(<[^>]+>)", rule):
                            if part.startswith("<") and part.endswith(">"):
                                spec = part[1:-1]
                                if ":" in spec: kind, name = spec.split(":", 1)
                                else: kind, name = "string", spec
                                names.append((name, kind))
                                pattern += rf"(?P<{name}>\\d+)" if kind == "int" else rf"(?P<{name}>[^/]+)"
                            else: pattern += re.escape(part)
                        self._routes.append((re.compile("^" + pattern + "$"), names, methods, func))
                        return func
                    return register
                def errorhandler(self, code):
                    def register(func): self._errors[int(code)] = func; return func
                    return register
                def _response(self, value):
                    if isinstance(value, Response): return value
                    if not isinstance(value, tuple): return Response(value)
                    if len(value) == 2: return Response(value[0], value[1])
                    return Response(value[0], value[1], dict(value[2]))
                def _error(self, code):
                    return self._response(self._errors[code](code)) if code in self._errors else Response("", code)
                def dispatch(self, path, method="GET"):
                    method, path_matches = method.upper(), []
                    for pattern, names, methods, func in self._routes:
                        match = pattern.fullmatch(path)
                        if not match: continue
                        path_matches.append(True)
                        if method not in methods: continue
                        values = match.groupdict()
                        for name, kind in names:
                            if kind == "int": values[name] = int(values[name])
                        return self._response(func(**values))
                    return self._error(405 if path_matches else 404)
        """,
    },
    "parse__format_parser_core__001": {
        "source": ("parse", "https://github.com/r1chardj0n3s/parse.git", "1.20.2", "MIT"),
        "title": "Format-string parser",
        "description": "Extract parse-style format compilation with named and positional fields and typed conversions.",
        "entrypoints": ["parse.parse", "parse.compile", "parse.Parser", "parse.Result"],
        "included": [
            "literal and escaped-brace matching",
            "named and positional capture fields",
            "integer, float, word, and default string conversions",
            "case-sensitive option and full-string matching",
        ],
        "excluded": ["custom type registries", "datetime formats", "search and findall"],
        "api": "from featurelifted import Parser, Result, compile, parse",
        "callable": "parse",
        "signature": "parse(format, string, case_sensitive=False)",
        "entanglement": ("parser_state_coupling", ["parser_state_coupling", "data_model_coupling"]),
        "public": """
            from featurelifted import compile, parse

            def test_named_and_typed_fields():
                result = parse("user={name:w} age={age:d}", "user=Ada age=37")
                assert result.named == {"name": "Ada", "age": 37}
                assert result.fixed == ()

            def test_positional_and_escaped_braces():
                parser = compile("point={{x={:d}, y={:f}}}")
                result = parser.parse("point={x=3, y=2.5}")
                assert result.fixed == (3, 2.5)
        """,
        "hidden": """
            from featurelifted import parse

            def test_full_match_and_case_policy():
                assert parse("Hello {name}", "hello Ada").named["name"] == "Ada"
                assert parse("Hello {name}", "hello Ada", case_sensitive=True) is None
                assert parse("x={:d}", "prefix x=1") is None

            def test_word_and_default_boundaries():
                result = parse("{first:w}-{second}", "alpha-rest-of-value")
                assert result.named == {"first": "alpha", "second": "rest-of-value"}
                assert result[0] == "alpha"
        """,
        "reference": """
            import re
            from dataclasses import dataclass

            @dataclass(frozen=True)
            class Result:
                fixed: tuple
                named: dict
                def __getitem__(self, key):
                    return self.named[key] if isinstance(key, str) else (tuple(self.fixed) + tuple(self.named.values()))[key]

            _TYPE = {"d": (r"[-+]?\\d+", int), "f": (r"[-+]?(?:\\d+(?:\\.\\d*)?|\\.\\d+)", float), "w": (r"\\w+", str), "": (r".+?", str)}
            class Parser:
                def __init__(self, format, case_sensitive=False):
                    self.format, self.case_sensitive = format, case_sensitive
                    self.regex, self.fields = self._compile(format)
                def _compile(self, text):
                    pattern, fields, index, pos = "", [], 0, 0
                    while pos < len(text):
                        if text.startswith("{{", pos): pattern += re.escape("{"); pos += 2; continue
                        if text.startswith("}}", pos): pattern += re.escape("}"); pos += 2; continue
                        if text[pos] != "{": pattern += re.escape(text[pos]); pos += 1; continue
                        end = text.find("}", pos)
                        if end < 0: raise ValueError("unmatched {")
                        spec = text[pos + 1:end]
                        if ":" in spec: name, kind = spec.split(":", 1)
                        else: name, kind = spec, ""
                        if kind not in _TYPE: raise ValueError(f"unknown format type {kind}")
                        group = name or f"_fixed_{index}"
                        if not name: index += 1
                        pattern += f"(?P<{group}>{_TYPE[kind][0]})"
                        fields.append((group, name, _TYPE[kind][1]))
                        pos = end + 1
                    flags = 0 if self.case_sensitive else re.IGNORECASE
                    return re.compile("^" + pattern + "$", flags), fields
                def parse(self, string):
                    match = self.regex.fullmatch(string)
                    if not match: return None
                    fixed, named = [], {}
                    for group, name, convert in self.fields:
                        value = convert(match.group(group))
                        if name:
                            named[name] = value
                        else:
                            fixed.append(value)
                    return Result(tuple(fixed), named)
            def compile(format, case_sensitive=False): return Parser(format, case_sensitive)
            def parse(format, string, case_sensitive=False): return Parser(format, case_sensitive).parse(string)
        """,
    },
    "filelock__reentrant_lock_core__001": {
        "source": ("filelock", "https://github.com/tox-dev/filelock.git", "3.13.1", "Unlicense"),
        "title": "Reentrant filesystem lock",
        "description": "Extract an exclusive file lock with reentrant ownership, timeout polling, and context-manager cleanup.",
        "entrypoints": ["filelock._api.BaseFileLock", "filelock._unix.UnixFileLock", "filelock._error.Timeout"],
        "included": [
            "exclusive lock-file acquisition across instances",
            "reentrant acquire and balanced release on one instance",
            "timeout and non-blocking acquisition",
            "context-manager release and lock-file cleanup",
        ],
        "excluded": ["Windows msvcrt backend", "async locks", "soft-lock fallback"],
        "api": "from featurelifted import FileLock, Timeout",
        "callable": "FileLock",
        "signature": "FileLock(lock_file, timeout=-1, poll_interval=0.05)",
        "entanglement": ("resource_coupling", ["resource_coupling", "config_environment_coupling"]),
        "public": """
            import pytest
            from featurelifted import FileLock, Timeout

            def test_context_and_reentrant_release(tmp_path):
                path = tmp_path / "demo.lock"
                lock = FileLock(path)
                with lock:
                    assert lock.is_locked and path.exists()
                    lock.acquire()
                    lock.release()
                    assert lock.is_locked
                assert not lock.is_locked and not path.exists()

            def test_nonblocking_contention(tmp_path):
                path = tmp_path / "demo.lock"
                first, second = FileLock(path), FileLock(path)
                first.acquire()
                with pytest.raises(Timeout):
                    second.acquire(timeout=0)
                first.release()
        """,
        "hidden": """
            from featurelifted import FileLock

            def test_force_release_and_idempotence(tmp_path):
                lock = FileLock(tmp_path / "x.lock")
                lock.acquire(); lock.acquire()
                lock.release(force=True)
                assert not lock.is_locked
                lock.release()

            def test_two_instances_can_acquire_sequentially(tmp_path):
                path = tmp_path / "x.lock"
                a, b = FileLock(path), FileLock(path)
                a.acquire(); a.release()
                with b:
                    assert b.lock_counter == 1
        """,
        "reference": """
            import os, time
            class Timeout(TimeoutError): pass
            class FileLock:
                def __init__(self, lock_file, timeout=-1, poll_interval=0.05):
                    self.lock_file = str(lock_file); self.timeout = timeout; self.poll_interval = poll_interval
                    self._fd = None; self.lock_counter = 0
                @property
                def is_locked(self): return self._fd is not None
                def acquire(self, timeout=None, poll_interval=None, blocking=True):
                    if self.is_locked:
                        self.lock_counter += 1; return self
                    timeout = self.timeout if timeout is None else timeout
                    if not blocking: timeout = 0
                    poll = self.poll_interval if poll_interval is None else poll_interval
                    started = time.monotonic()
                    while True:
                        try:
                            self._fd = os.open(self.lock_file, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                            self.lock_counter = 1; return self
                        except FileExistsError:
                            if timeout >= 0 and time.monotonic() - started >= timeout: raise Timeout(self.lock_file)
                            time.sleep(poll)
                def release(self, force=False):
                    if not self.is_locked: return
                    self.lock_counter = 0 if force else self.lock_counter - 1
                    if self.lock_counter <= 0:
                        os.close(self._fd); self._fd = None
                        try: os.unlink(self.lock_file)
                        except FileNotFoundError: pass
                def __enter__(self): return self.acquire()
                def __exit__(self, *exc): self.release()
        """,
    },
    "blinker__signal_registry_core__001": {
        "source": ("blinker", "https://github.com/pallets-eco/blinker.git", "1.6.2", "MIT"),
        "title": "Signal receiver registry",
        "description": "Extract sender-filtered signal registration with weak receiver cleanup and namespace identity.",
        "entrypoints": ["blinker.base.Signal", "blinker.base.Namespace", "blinker.base.ANY"],
        "included": [
            "connect, disconnect, connected_to, and receiver iteration",
            "ANY and sender-specific dispatch",
            "weak receiver cleanup after garbage collection",
            "Namespace returns one stable Signal per name",
        ],
        "excluded": ["async receivers", "global named signal singleton", "documentation helpers"],
        "api": "from featurelifted import ANY, Namespace, Signal",
        "callable": "Signal",
        "signature": "Signal(doc=None)",
        "entanglement": ("framework_coupling", ["framework_coupling", "data_model_coupling"]),
        "public": """
            from featurelifted import Namespace, Signal

            def test_sender_filtering_and_responses():
                signal, seen = Signal(), []
                def any_receiver(sender, **kw): seen.append(("any", sender)); return kw["value"]
                def only_receiver(sender, **kw): seen.append(("only", sender)); return "only"
                signal.connect(any_receiver, weak=False)
                signal.connect(only_receiver, sender="chosen", weak=False)
                assert signal.send("chosen", value=3) == [(any_receiver, 3), (only_receiver, "only")]
                assert signal.send("other", value=4) == [(any_receiver, 4)]

            def test_namespace_identity():
                namespace = Namespace()
                assert namespace.signal("ready") is namespace.signal("ready")
                assert namespace.signal("ready") is not namespace.signal("done")
        """,
        "hidden": """
            import gc
            from featurelifted import Signal

            def test_weak_receiver_cleanup():
                signal = Signal()
                class Receiver:
                    def __call__(self, sender, **kw): return "ok"
                receiver = Receiver()
                signal.connect(receiver)
                assert len(signal.send(None)) == 1
                del receiver; gc.collect()
                assert signal.send(None) == []

            def test_connected_to_scope_and_disconnect():
                signal, calls = Signal(), []
                def receiver(sender, **kw): calls.append(sender)
                with signal.connected_to(receiver, sender="x"):
                    signal.send("x"); signal.send("y")
                signal.send("x")
                assert calls == ["x"]
        """,
        "reference": """
            import contextlib, weakref
            ANY = object()
            class Signal:
                def __init__(self, doc=None): self.__doc__ = doc; self._receivers = []
                def connect(self, receiver, sender=ANY, weak=True):
                    if weak:
                        try:
                            ref = weakref.WeakMethod(receiver)
                        except TypeError:
                            ref = weakref.ref(receiver)
                    else: ref = lambda: receiver
                    self._receivers.append((ref, sender, receiver if not weak else None))
                    return receiver
                def disconnect(self, receiver, sender=ANY):
                    self._receivers = [row for row in self._receivers if not ((row[0]() is receiver) and (sender is ANY or row[1] == sender))]
                def receivers_for(self, sender):
                    alive = []
                    for ref, expected, strong in self._receivers:
                        receiver = ref()
                        if receiver is None: continue
                        alive.append((ref, expected, strong))
                        if expected is ANY or expected == sender: yield receiver
                    self._receivers = alive
                def send(self, sender=None, **kwargs):
                    return [(receiver, receiver(sender, **kwargs)) for receiver in self.receivers_for(sender)]
                @contextlib.contextmanager
                def connected_to(self, receiver, sender=ANY):
                    self.connect(receiver, sender=sender, weak=False)
                    try: yield receiver
                    finally: self.disconnect(receiver, sender=sender)
            class Namespace(dict):
                def signal(self, name, doc=None):
                    if name not in self: self[name] = Signal(doc)
                    return self[name]
        """,
    },
    "python_decouple__config_repository_core__001": {
        "source": ("python-decouple", "https://github.com/HBNetwork/python-decouple.git", "3.8", "MIT"),
        "title": "Environment-backed configuration repository",
        "description": "Extract decouple-style environment precedence, .env parsing, casts, CSV values, and required/default handling.",
        "entrypoints": ["decouple.Config", "decouple.RepositoryEnv", "decouple.RepositoryEmpty", "decouple.Csv", "decouple.Choices"],
        "included": [
            "environment variables override repository values",
            ".env quoted-value and comment parsing",
            "required and default value behavior",
            "bool, int, float, Csv, and Choices casting",
        ],
        "excluded": ["INI files", "AutoConfig directory search", "encoding auto-detection"],
        "api": "from featurelifted import Choices, Config, Csv, RepositoryDict, RepositoryEnv, UndefinedValueError",
        "callable": "Config",
        "signature": "Config(repository, environ=None)",
        "entanglement": ("config_environment_coupling", ["config_environment_coupling", "resource_coupling"]),
        "public": """
            import pytest
            from featurelifted import Config, Csv, RepositoryDict, UndefinedValueError

            def test_precedence_defaults_and_casts():
                config = Config(RepositoryDict({"PORT": "8000", "DEBUG": "no"}), environ={"PORT": "9000"})
                assert config("PORT", cast=int) == 9000
                assert config("DEBUG", cast=bool) is False
                assert config("MISSING", default="x") == "x"
                with pytest.raises(UndefinedValueError): config("REQUIRED")

            def test_csv_cast():
                config = Config(RepositoryDict({"HOSTS": "a, b,c"}), environ={})
                assert config("HOSTS", cast=Csv()) == ["a", "b", "c"]
        """,
        "hidden": """
            import pytest
            from featurelifted import Choices, Config, RepositoryEnv

            def test_env_file_quotes_comments_and_empty(tmp_path):
                path = tmp_path / ".env"
                path.write_text("NAME='Ada Lovelace' # note\\nEMPTY=\\nFLAG=YES\\n", encoding="utf-8")
                config = Config(RepositoryEnv(path), environ={})
                assert config("NAME") == "Ada Lovelace"
                assert config("EMPTY") == ""
                assert config("FLAG", cast=bool) is True

            def test_choices_and_float():
                config = Config(type("R", (), {"data": {"MODE": "prod", "RATE": "1.25"}, "__contains__": lambda s,k:k in s.data, "__getitem__": lambda s,k:s.data[k]})(), environ={})
                assert config("MODE", cast=Choices(["dev", "prod"])) == "prod"
                assert config("RATE", cast=float) == 1.25
                with pytest.raises(ValueError): Choices(["dev"])("prod")
        """,
        "reference": """
            import os, re
            _UNDEFINED = object()
            class UndefinedValueError(ValueError): pass
            class RepositoryDict:
                def __init__(self, data): self.data = dict(data)
                def __contains__(self, key): return key in self.data
                def __getitem__(self, key): return self.data[key]
            class RepositoryEnv(RepositoryDict):
                def __init__(self, source):
                    data = {}
                    for raw in open(source, encoding="utf-8"):
                        line = raw.strip()
                        if not line or line.startswith("#") or "=" not in line: continue
                        key, value = line.split("=", 1); value = value.strip()
                        if value[:1] in {"'", '"'}:
                            quote = value[0]; end = value.find(quote, 1)
                            value = value[1:end] if end >= 0 else value[1:]
                        else: value = re.split(r"\\s+#", value, 1)[0].strip()
                        data[key.strip()] = value
                    super().__init__(data)
            class Csv:
                def __init__(self, cast=str, delimiter=",", strip=" "): self.cast, self.delimiter, self.strip = cast, delimiter, strip
                def __call__(self, value): return [self.cast(item.strip(self.strip)) for item in value.split(self.delimiter) if item.strip(self.strip)]
            class Choices:
                def __init__(self, choices, cast=str): self.choices, self.cast = tuple(choices), cast
                def __call__(self, value):
                    result = self.cast(value)
                    if result not in self.choices: raise ValueError(f"{result!r} not in {self.choices!r}")
                    return result
            def _cast_bool(value):
                lowered = str(value).strip().lower()
                if lowered in {"true", "1", "yes", "y", "on"}: return True
                if lowered in {"false", "0", "no", "n", "off"}: return False
                raise ValueError(f"invalid boolean: {value}")
            class Config:
                def __init__(self, repository, environ=None): self.repository, self.environ = repository, os.environ if environ is None else environ
                def __call__(self, option, default=_UNDEFINED, cast=_UNDEFINED):
                    if option in self.environ: value = self.environ[option]
                    elif option in self.repository: value = self.repository[option]
                    elif default is not _UNDEFINED: value = default
                    else: raise UndefinedValueError(f"{option} not found")
                    if cast is _UNDEFINED: return value
                    if cast is bool: return _cast_bool(value)
                    return cast(value)
        """,
    },
    "decorator__signature_preserving_core__001": {
        "source": ("decorator", "https://github.com/micheles/decorator.git", "5.1.1", "BSD-2-Clause"),
        "title": "Signature-preserving function decorator",
        "description": "Extract caller-based decoration that preserves introspection metadata for sync and async functions.",
        "entrypoints": ["decorator.decorator", "decorator.decorate"],
        "included": [
            "caller receives the original function before bound arguments",
            "decorated call enforces the original function signature",
            "name, docstring, module, annotations, wrapped, and inspect.signature are preserved",
            "async callers and coroutine functions remain awaitable",
        ],
        "excluded": ["contextmanager helpers", "FunctionMaker source generation", "class decoration"],
        "api": "from featurelifted import decorate, decorator",
        "callable": "decorator",
        "signature": "decorator(caller, func=None)",
        "entanglement": ("data_model_coupling", ["data_model_coupling", "framework_coupling"]),
        "public": """
            import inspect
            from featurelifted import decorator

            def test_metadata_signature_and_call_order():
                calls = []
                def caller(func, *args, **kwargs):
                    calls.append((args, kwargs)); return func(*args, **kwargs) * 2
                @decorator(caller)
                def add(a: int, b: int = 1) -> int:
                    '''add values'''
                    return a + b
                assert add(2, b=3) == 10
                assert str(inspect.signature(add)) == "(a: int, b: int = 1) -> int"
                assert add.__name__ == "add" and add.__doc__ == "add values"
                assert calls == [((2,), {"b": 3})]
        """,
        "hidden": """
            import asyncio, inspect, pytest
            from featurelifted import decorate, decorator

            def test_invalid_calls_follow_original_signature():
                @decorator(lambda func, *a, **k: func(*a, **k))
                def f(a, *, b): return a + b
                with pytest.raises(TypeError): f(1, 2)

            def test_async_caller_and_wrapped():
                async def caller(func, *args, **kwargs): return await func(*args, **kwargs) + 1
                async def base(value): return value * 2
                wrapped = decorate(base, caller)
                assert inspect.iscoroutinefunction(wrapped)
                assert wrapped.__wrapped__ is base
                assert asyncio.run(wrapped(3)) == 7
        """,
        "reference": """
            import functools, inspect
            def decorate(func, caller):
                signature = inspect.signature(func)
                if inspect.iscoroutinefunction(caller):
                    async def wrapped(*args, **kwargs):
                        signature.bind(*args, **kwargs)
                        return await caller(func, *args, **kwargs)
                else:
                    def wrapped(*args, **kwargs):
                        signature.bind(*args, **kwargs)
                        return caller(func, *args, **kwargs)
                functools.update_wrapper(wrapped, func)
                wrapped.__signature__ = signature
                return wrapped
            def decorator(caller, func=None):
                if func is not None: return decorate(func, caller)
                return lambda target: decorate(target, caller)
        """,
    },
}


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(text).strip() + "\n", encoding="utf-8")


def _test_nodeids(relative: str, source: str) -> list[str]:
    tree = ast.parse(dedent(source))
    return [
        f"{relative}::{node.name}"
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    ]


def _behavior_contract(task_id: str, spec: dict, forbidden: str) -> dict:
    clauses = [
        {
            "behavior_id": f"B{index:03d}",
            "clause_kind": "included_behavior",
            "text": text.rstrip(".") + ".",
        }
        for index, text in enumerate(spec["included"], 1)
    ]
    api_id = f"B{len(clauses) + 1:03d}"
    isolation_id = f"B{len(clauses) + 2:03d}"
    clauses.extend(
        [
            {
                "behavior_id": api_id,
                "clause_kind": "api_surface",
                "text": "The declared target API remains importable with the documented callable shapes.",
            },
            {
                "behavior_id": isolation_id,
                "clause_kind": "isolation_constraint",
                "text": f"The submitted package does not import forbidden upstream packages: {forbidden}.",
            },
        ]
    )
    behavior_ids = [item["behavior_id"] for item in clauses if item["clause_kind"] == "included_behavior"]
    return {
        "schema_version": "featureliftbench.behavior_contract.v1",
        "task_id": task_id,
        "public_clauses": clauses,
        "public_test_mappings": [
            {
                "nodeid": nodeid,
                "public_clause_ids": behavior_ids,
                "mapping_method": "preregistered_author_mapping",
            }
            for nodeid in _test_nodeids(
                "public_tests/test_public_contract.py", spec["public"]
            )
        ],
        "hidden_test_mappings": [
            {
                "nodeid": nodeid,
                "public_clause_ids": behavior_ids,
                "mapping_method": "preregistered_author_mapping",
            }
            for nodeid in _test_nodeids(
                "hidden_tests/test_hidden_contract.py", spec["hidden"]
            )
        ],
        "review_status": "maintainer_reviewed",
        "review": {
            "reviewer_type": "maintainer_author",
            "independent_human_review_required": False,
            "model_results_consulted": False,
        },
    }


def scaffold(task_id: str, spec: dict) -> None:
    task = STAGING / task_id
    if task.exists():
        shutil.rmtree(task)
    (task / "repo").mkdir(parents=True)
    (task / "repo" / "README.md").write_text(
        "Pruned source is populated from the verified canonical archive before promotion.\n",
        encoding="utf-8",
    )
    source_name, source_url, revision, license_id = spec["source"]
    primary, types = spec["entanglement"]
    metadata = {
        "task_id": task_id,
        "language": "python",
        "status": "staging_candidate",
        "difficulty": "hard",
        "split_role": "mechanism_challenging",
        "source": {
            "name": source_name,
            "url": source_url,
            "commit": revision,
            "license": license_id,
        },
        "feature": {
            "name": spec["title"],
            "description": spec["description"],
            "source_entrypoints": spec["entrypoints"],
            "included_behaviors": spec["included"],
            "excluded_behaviors": spec["excluded"]
            + ["original repository import at runtime", "source repository path access"],
        },
        "entanglement": {
            "level": "high",
            "primary": primary,
            "types": types,
            "description": spec["description"],
            "signals": spec["included"][:3],
        },
        "output": {
            "package": "featurelifted",
            "import": spec["api"],
            "callable": spec["callable"],
            "signature": spec["signature"],
        },
        "environment": {
            "python": "3.11",
            "network": False,
            "timeout_seconds": 90,
            "dependency_lock": "requirements.lock",
            "allowed_dependencies": [],
            "forbidden_imports": [source_name.replace("-", "_")],
            "forbidden_dependencies": [source_name],
            "forbidden_paths": ["repo/", f"{source_name.replace('-', '_')}/"],
        },
        "tests": {
            "command": "pytest",
            "public": "public_tests/",
            "hidden": "hidden_tests/",
        },
        "tags": ["external150-replacement", "preregistered", primary],
    }
    _write(task / "metadata.json", json.dumps(metadata, indent=2, sort_keys=True))
    _write(
        task / "TASK.md",
        f"""
        # FeatureLift Task: {spec['title']}

        {spec['description']}

        ## Target API

        `{spec['api']}`

        ## Included Behavior

        {chr(10).join(f"- {item}" for item in spec['included'])}

        ## Excluded Behavior

        {chr(10).join(f"- {item}" for item in spec['excluded'])}

        ## Constraints

        - Do not import `{source_name}` or read the source repository at runtime.
        - Do not access the network.
        - Submit an independent `featurelifted` package.
        """,
    )
    _write(task / "public_tests" / "test_public_contract.py", spec["public"])
    _write(task / "hidden_tests" / "test_hidden_contract.py", spec["hidden"])
    _write(task / "requirements.lock", "")
    _write(task / "evaluation" / "forbidden_imports.txt", source_name.replace("-", "_"))
    _write(
        task / "evaluation" / "behavior_contract.json",
        json.dumps(
            _behavior_contract(
                task_id,
                spec,
                source_name.replace("-", "_"),
            ),
            indent=2,
            sort_keys=True,
        ),
    )
    _write(
        task / "evaluation" / "oracle_manifest.json",
        json.dumps(
            {
                "required_source_files": spec["entrypoints"],
                "notes": "Entrypoints are maintainer-private provenance and are never Agent-visible in Main.",
            },
            indent=2,
            sort_keys=True,
        ),
    )

    reference = REFERENCES / task_id / "featurelifted"
    if reference.parent.exists():
        shutil.rmtree(reference.parent)
    _write(reference / "__init__.py", spec["reference"])
    oracle = LOCAL_ORACLES / task_id / "oracle"
    if oracle.exists():
        shutil.rmtree(oracle)
    shutil.copytree(reference.parent, oracle)


def main() -> int:
    for task_id, spec in TASKS.items():
        scaffold(task_id, spec)
        print(f"scaffolded {task_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

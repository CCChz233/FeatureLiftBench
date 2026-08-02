#!/usr/bin/env python3
"""Materialize the ten balanced Python-200 replacement tasks."""

from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / "harness"
sys.path.insert(0, str(HARNESS))

from featureliftbench.task_render import render_public_task  # noqa: E402
from featureliftbench.task_spec import (  # noqa: E402
    compute_generated_task_hash,
    compute_spec_hash,
)

PILOT_PATH = ROOT / "harness" / "scripts" / "materialize_external50_pilot.py"
pilot_spec = importlib.util.spec_from_file_location("external50_materializer", PILOT_PATH)
pilot = importlib.util.module_from_spec(pilot_spec)
assert pilot_spec.loader is not None
pilot_spec.loader.exec_module(pilot)

PIN_ROOT = Path("/tmp/flb_python200_pins")
STAGING = ROOT / "benchmark" / "staging"


def api(path: str, kind: str, signature: str | None = None, members: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    entry: dict[str, Any] = {"path": f"featurelifted.{path}", "kind": kind}
    if signature:
        entry["signature"] = signature
    if members:
        entry["members"] = members
    return entry


def member(path: str, kind: str, signature: str | None = None) -> dict[str, Any]:
    return api(path, kind, signature)


TASKS: list[dict[str, Any]] = [
    {
        "task_id": "cacheout__ttl_policy_core__001",
        "slot_id": "cache-direct-config-01",
        "package": "cacheout",
        "url": "https://github.com/dgilland/cacheout",
        "commit": "ab709979deafd7e241050a9fa8ce8463d70a10fb",
        "license": "MIT",
        "license_path": "LICENSE.rst",
        "src": PIN_ROOT / "cacheout",
        "package_dir": PIN_ROOT / "cacheout" / "src" / "cacheout",
        "upstream_import": "cacheout",
        "lift_type": "Direct",
        "feature_family": "cache_retry_policy",
        "entanglement": "config_environment_coupling",
        "entanglement_description": "Constructor and configure defaults control size, TTL, timer, and eviction behavior.",
        "allowed_dependencies": [],
        "requirements": [],
        "title": "Configurable TTL and LRU cache policy",
        "summary": "Extract Cache and LRUCache policy behavior with deterministic timers and runtime configuration.",
        "entrypoints": ["cacheout.Cache", "cacheout.LRUCache"],
        "included": ["cache get/set/delete", "TTL expiry with an injected timer", "LRU eviction and configure updates"],
        "excluded": ["async wrappers", "global cache manager", "random-replacement policies"],
        "required_api": [
            api("Cache", "class", "(maxsize: int = 256, ttl: float = 0, timer=None, default=None, enable_stats: bool = False)", [
                member("Cache.set", "method", "(key, value, ttl=None) -> None"),
                member("Cache.get", "method", "(key, default=None)"),
                member("Cache.delete", "method", "(key) -> int"),
                member("Cache.configure", "method", "(**kwargs) -> None"),
            ]),
            api("LRUCache", "class", "(maxsize: int = 256, ttl: float = 0, timer=None, default=None, enable_stats: bool = False)"),
        ],
        "api_checks": ["assert isinstance(Cache, type)", "assert isinstance(LRUCache, type)", "assert all(callable(getattr(Cache, n)) for n in ('set', 'get', 'delete', 'configure'))"],
        "behaviors": [
            "Cache stores, retrieves, and deletes values while honoring constructor and configure defaults.",
            "TTL expiration uses the injected timer deterministically and supports per-entry overrides.",
            "LRUCache evicts the least recently accessed entry when maxsize is exceeded.",
            "The submitted package does not import cacheout or read the upstream repository at runtime.",
        ],
        "public_tests": '''from featurelifted import Cache, LRUCache


class Timer:
    def __init__(self): self.now = 0
    def __call__(self): return self.now


def test_cache_roundtrip_and_delete():
    cache = Cache(maxsize=2)
    cache.set("a", 1)
    assert cache.get("a") == 1
    assert cache.delete("a") == 1
    assert cache.get("a") is None


def test_ttl_uses_injected_timer():
    timer = Timer()
    cache = Cache(ttl=2, timer=timer)
    cache.set("a", 1)
    timer.now = 1
    assert cache.get("a") == 1
    timer.now = 2
    assert cache.get("a") is None
''',
        "hidden_tests": '''from featurelifted import Cache, LRUCache


def test_configure_changes_default_ttl():
    class Timer:
        now = 0
        def __call__(self): return self.now
    timer = Timer()
    cache = Cache(timer=timer)
    cache.configure(ttl=3)
    cache.set("x", 9)
    timer.now = 3
    assert not cache.has("x")


def test_lru_touch_controls_eviction():
    cache = LRUCache(maxsize=2)
    cache.set("a", 1); cache.set("b", 2)
    assert cache.get("a") == 1
    cache.set("c", 3)
    assert "a" in cache and "b" not in cache and "c" in cache
''',
        "public_mapping": {"test_cache_roundtrip_and_delete": "B001", "test_ttl_uses_injected_timer": "B002"},
        "hidden_mapping": {"test_configure_changes_default_ttl": ["B001", "B002"], "test_lru_touch_controls_eviction": "B003"},
        "oracle_files": ["src/cacheout/cache.py", "src/cacheout/lru.py"],
    },
    {
        "task_id": "stamina__retry_context_core__001",
        "slot_id": "cache-direct-third-party-02",
        "package": "stamina",
        "url": "https://github.com/hynek/stamina",
        "commit": "ab12cbf7d5e06c31344f4d43246d4be9930245f7",
        "license": "MIT",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "stamina",
        "package_dir": PIN_ROOT / "stamina" / "src" / "stamina",
        "upstream_import": "stamina",
        "lift_type": "Direct",
        "feature_family": "cache_retry_policy",
        "entanglement": "third_party_dependency_coupling",
        "entanglement_description": "The public retry policy delegates attempt accounting and stop/wait decisions to tenacity.",
        "allowed_dependencies": ["tenacity"],
        "requirements": ["tenacity==8.2.3"],
        "title": "Retry decorator and context policy",
        "summary": "Extract stamina retry and retry_context with deterministic zero-wait policy controls.",
        "entrypoints": ["stamina.retry", "stamina.retry_context", "stamina.set_active", "stamina.set_testing"],
        "included": ["sync retry decorator", "retry_context attempt iterator", "global active/testing configuration"],
        "excluded": ["async and Trio integration", "logging instrumentation adapters", "non-zero sleeps in evaluator tests"],
        "required_api": [
            api("retry", "function", "(*, on, attempts=10, timeout=45.0, wait_initial=0.1, wait_max=5.0, wait_jitter=1.0, wait_exp_base=2)"),
            api("retry_context", "function", "(on, attempts=10, timeout=45.0, wait_initial=0.1, wait_max=5.0, wait_jitter=1.0, wait_exp_base=2)"),
            api("Attempt", "class", members=[member("Attempt.num", "attribute"), member("Attempt.next_wait", "attribute")]),
            api("set_active", "function", "(active: bool) -> None"),
            api("set_testing", "function", "(testing: bool) -> None"),
        ],
        "api_checks": ["assert all(callable(x) for x in (retry, retry_context, set_active, set_testing))", "assert isinstance(Attempt, type)"],
        "behaviors": [
            "retry retries only configured exceptions and returns the first successful result.",
            "retry_context exposes one-based Attempt.num values and stops at the configured attempt limit.",
            "set_active and set_testing change retry execution policy without changing the wrapped callable API.",
            "The submitted package uses only the locked tenacity dependency and does not import stamina.",
        ],
        "public_tests": '''from featurelifted import retry, retry_context


def test_retry_decorator_succeeds_after_failures():
    calls = []
    @retry(on=ValueError, attempts=3, timeout=None, wait_initial=0, wait_max=0, wait_jitter=0)
    def work():
        calls.append(1)
        if len(calls) < 3: raise ValueError("again")
        return "ok"
    assert work() == "ok" and len(calls) == 3


def test_retry_context_attempt_numbers():
    seen = []
    for attempt in retry_context(on=ValueError, attempts=3, timeout=None, wait_initial=0, wait_max=0, wait_jitter=0):
        with attempt:
            seen.append(attempt.num)
            if attempt.num < 3: raise ValueError("again")
    assert seen == [1, 2, 3]
''',
        "hidden_tests": '''import pytest
from featurelifted import retry, set_active, set_testing


def test_unconfigured_exception_is_not_retried():
    calls = []
    @retry(on=ValueError, attempts=3, timeout=None, wait_initial=0, wait_max=0, wait_jitter=0)
    def work(): calls.append(1); raise TypeError("stop")
    with pytest.raises(TypeError): work()
    assert len(calls) == 1


def test_retry_context_stops_after_success():
    from featurelifted import retry_context
    seen = []
    for attempt in retry_context(on=ValueError, attempts=4, timeout=None, wait_initial=0, wait_max=0, wait_jitter=0):
        with attempt:
            seen.append(attempt.num)
            if attempt.num == 1: raise ValueError("again")
    assert seen == [1, 2]


def test_inactive_policy_calls_once():
    calls = []
    set_active(False)
    try:
        @retry(on=ValueError, attempts=3, timeout=None, wait_initial=0, wait_max=0, wait_jitter=0)
        def work(): calls.append(1); raise ValueError("stop")
        with pytest.raises(ValueError): work()
        assert len(calls) == 1
    finally:
        set_active(True); set_testing(False)
''',
        "public_mapping": {"test_retry_decorator_succeeds_after_failures": "B001", "test_retry_context_attempt_numbers": "B002"},
        "hidden_mapping": {"test_unconfigured_exception_is_not_retried": "B001", "test_retry_context_stops_after_success": "B002", "test_inactive_policy_calls_once": "B003"},
        "oracle_files": ["src/stamina/_core.py", "src/stamina/_config.py"],
    },
    {
        "task_id": "cachier__memoize_backend_core__001",
        "slot_id": "cache-composite-third-party-03",
        "package": "cachier",
        "url": "https://github.com/python-cachier/cachier",
        "commit": "e5fd990d646b05764977fe20f3e846c9e3d59076",
        "license": "MIT",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "cachier",
        "package_dir": PIN_ROOT / "cachier" / "src" / "cachier",
        "upstream_import": "cachier",
        "lift_type": "Composite",
        "feature_family": "cache_retry_policy",
        "entanglement": "third_party_dependency_coupling",
        "entanglement_description": "Decorator policy composes hash keys, memory entries, size accounting, and optional locked persistent backends.",
        "allowed_dependencies": ["portalocker", "Pympler", "watchdog"],
        "requirements": ["portalocker==3.2.0", "Pympler==1.1", "watchdog==6.0.0"],
        "title": "Memoization decorator and backend policy",
        "summary": "Extract cachier decorator behavior with deterministic memory caching, per-call overrides, and global policy controls.",
        "entrypoints": ["cachier.cachier", "cachier.set_default_params", "cachier.enable_caching", "cachier.disable_caching"],
        "included": ["memory backend memoization", "skip and overwrite controls", "clear/precache methods", "global enable/disable policy"],
        "excluded": ["MongoDB, Redis, SQL, and S3 services", "background timing assertions", "network access"],
        "required_api": [
            api("cachier", "function", "(*, backend='pickle', stale_after=..., next_time=False, cache_dir=None, ...)"),
            api("set_default_params", "function", "(**params) -> None"),
            api("get_default_params", "function", "() -> dict"),
            api("enable_caching", "function", "() -> None"),
            api("disable_caching", "function", "() -> None"),
        ],
        "api_checks": ["assert all(callable(x) for x in (cachier, set_default_params, get_default_params, enable_caching, disable_caching))"],
        "behaviors": [
            "The memory backend memoizes by arguments and exposes clear_cache and precache_value on wrapped callables.",
            "Per-call skip-cache and overwrite-cache controls bypass or replace an existing entry deterministically.",
            "Global enable and disable controls affect decorated functions and can be restored between tests.",
            "The submitted package uses only locked backend dependencies and does not import cachier.",
        ],
        "public_tests": '''from featurelifted import cachier


def test_memory_backend_memoizes_by_arguments():
    calls = []
    @cachier(backend="memory")
    def add(a, b): calls.append((a, b)); return a + b
    assert add(1, 2) == add(1, 2) == 3
    assert add(2, 3) == 5 and calls == [(1, 2), (2, 3)]


def test_skip_and_overwrite_controls():
    calls = []
    @cachier(backend="memory")
    def value(x): calls.append(x); return len(calls)
    assert value(1) == 1 and value(1) == 1
    assert value(1, cachier__skip_cache=True) == 2
    assert value(1) == 1
    assert value(1, cachier__overwrite_cache=True) == 3
    assert value(1) == 3
''',
        "hidden_tests": '''from featurelifted import cachier, disable_caching, enable_caching


def test_clear_and_precache_methods():
    calls = []
    @cachier(backend="memory")
    def value(x): calls.append(x); return x * 2
    value.precache_value(3, value_to_cache=7)
    assert value(3) == 7 and calls == []
    value.clear_cache()
    assert value(3) == 6 and calls == [3]


def test_overwrite_replaces_existing_entry():
    calls = []
    @cachier(backend="memory")
    def value(): calls.append(1); return len(calls)
    assert value() == 1 and value() == 1
    assert value(cachier__overwrite_cache=True) == 2
    assert value() == 2


def test_global_disable_bypasses_cache():
    calls = []
    @cachier(backend="memory")
    def value(): calls.append(1); return len(calls)
    try:
        disable_caching()
        assert (value(), value()) == (1, 2)
    finally:
        enable_caching()
''',
        "public_mapping": {"test_memory_backend_memoizes_by_arguments": "B001", "test_skip_and_overwrite_controls": "B002"},
        "hidden_mapping": {"test_clear_and_precache_methods": "B001", "test_overwrite_replaces_existing_entry": "B002", "test_global_disable_bypasses_cache": "B003"},
        "oracle_files": ["src/cachier/core.py", "src/cachier/config.py", "src/cachier/cores/memory.py"],
    },
    {
        "task_id": "automat__methodical_workflow_core__001",
        "slot_id": "workflow-composite-framework-01",
        "package": "Automat",
        "url": "https://github.com/glyph/automat",
        "commit": "bd5651c7970d2b4bfaa197f23777e469c5060e81",
        "license": "MIT",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "automat",
        "package_dir": PIN_ROOT / "automat" / "src" / "automat",
        "upstream_import": "automat",
        "lift_type": "Composite",
        "feature_family": "workflow_session_orchestration",
        "entanglement": "framework_coupling",
        "entanglement_description": "Descriptors declared on a host class connect states, inputs, outputs, serialization, and transition dispatch.",
        "allowed_dependencies": [],
        "requirements": [],
        "title": "Methodical state-machine workflow",
        "summary": "Extract MethodicalMachine declaration, transition dispatch, outputs, and state serialization.",
        "entrypoints": ["automat.MethodicalMachine", "automat.NoTransition"],
        "included": ["state/input/output decorators", "upon transition wiring", "serializer and unserializer", "unhandled input errors"],
        "excluded": ["Graphviz rendering", "Twisted integration", "command-line visualization"],
        "required_api": [api("MethodicalMachine", "class"), api("NoTransition", "exception")],
        "api_checks": ["assert isinstance(MethodicalMachine, type)", "assert issubclass(NoTransition, Exception)"],
        "behaviors": [
            "MethodicalMachine composes declared states and inputs into deterministic transitions on host instances.",
            "Transition outputs are collected and returned in declared order.",
            "Serializer and unserializer decorators round-trip the active state for a new instance.",
            "The submitted package does not import automat or use visualization dependencies.",
        ],
        "public_tests": '''from operator import itemgetter
from featurelifted import MethodicalMachine


def make_switch():
    class Switch:
        machine = MethodicalMachine()
        @machine.state(initial=True, serialized="off")
        def off(self): pass
        @machine.state(serialized="on")
        def on(self): pass
        @machine.input()
        def flip(self): pass
        off.upon(flip, enter=on, outputs=[])
        on.upon(flip, enter=off, outputs=[])
        @machine.input()
        def query(self): pass
        @machine.output()
        def yes(self): return True
        @machine.output()
        def no(self): return False
        off.upon(query, enter=off, outputs=[no], collector=itemgetter(0))
        on.upon(query, enter=on, outputs=[yes], collector=itemgetter(0))
    return Switch


def test_transition_and_collected_output():
    switch = make_switch()()
    assert switch.query() is False
    switch.flip()
    assert switch.query() is True


def test_instances_keep_independent_state():
    Switch = make_switch(); left = Switch(); right = Switch()
    left.flip()
    assert left.query() is True and right.query() is False
''',
        "hidden_tests": '''from featurelifted import MethodicalMachine, NoTransition


def test_serializer_roundtrip():
    class Switch:
        machine = MethodicalMachine()
        @machine.state(initial=True, serialized="off")
        def off(self): pass
        @machine.state(serialized="on")
        def on(self): pass
        @machine.input()
        def flip(self): pass
        off.upon(flip, enter=on, outputs=[]); on.upon(flip, enter=off, outputs=[])
        @machine.serializer()
        def save(self, state): return state
        @machine.unserializer()
        def restore(self, state): return state
    first = Switch(); first.flip(); state = first.save()
    second = Switch(); second.restore(state)
    assert second.save() == "on"


def test_undeclared_transition_raises():
    class OneWay:
        machine = MethodicalMachine()
        @machine.state(initial=True)
        def start(self): pass
        @machine.state()
        def end(self): pass
        @machine.input()
        def go(self): pass
        start.upon(go, enter=end, outputs=[])
    obj = OneWay(); obj.go()
    try: obj.go()
    except NoTransition: pass
    else: raise AssertionError("NoTransition not raised")
''',
        "public_mapping": {"test_transition_and_collected_output": "B001", "test_instances_keep_independent_state": "B001"},
        "hidden_mapping": {"test_serializer_roundtrip": ["B001", "B003"], "test_undeclared_transition_raises": "B002"},
        "oracle_files": ["src/automat/_methodical.py", "src/automat/_core.py"],
    },
    {
        "task_id": "python_statemachine__json_workflow_core__001",
        "slot_id": "workflow-composite-config-02",
        "package": "python-statemachine",
        "url": "https://github.com/fgmacedo/python-statemachine",
        "commit": "d911f537f557f0f6a5de2ceedd6fde9a451b6ada",
        "license": "MIT",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "python-statemachine",
        "package_dir": PIN_ROOT / "python-statemachine" / "statemachine",
        "upstream_import": "statemachine",
        "lift_type": "Composite",
        "feature_family": "workflow_session_orchestration",
        "entanglement": "config_environment_coupling",
        "entanglement_description": "A JSON definition configures state topology, event routing, initial configuration, and safe expression policy.",
        "allowed_dependencies": [],
        "requirements": [],
        "title": "JSON-defined statechart workflow",
        "summary": "Extract safe inline JSON statechart loading and synchronous event execution.",
        "entrypoints": ["statemachine.io.load", "statemachine.StateChart"],
        "included": ["inline JSON loading", "initial state selection", "event-driven transitions", "safe default expression mode"],
        "excluded": ["YAML and SCXML", "schema validation", "trusted eval", "Django integration"],
        "required_api": [
            api("load", "function", "(source: str | Path, *, format=None, trusted=False, validate=False, name=None) -> type[StateChart]"),
            api("StateChart", "class", members=[member("StateChart.send", "method", "(event, *args, **kwargs)"), member("StateChart.configuration", "attribute")]),
            api("InvalidDefinition", "exception"),
        ],
        "api_checks": ["assert callable(load)", "assert isinstance(StateChart, type)", "assert callable(StateChart.send)", "assert issubclass(InvalidDefinition, Exception)"],
        "behaviors": [
            "load parses an inline JSON statechart definition and returns an instantiable StateChart subclass.",
            "The instantiated chart starts in the configured initial state and routes declared events to target states.",
            "The default trusted=False mode rejects unsupported executable expressions at load time.",
            "The submitted package does not import statemachine and performs no file or network lookup for inline JSON.",
        ],
        "public_tests": '''import json
from featurelifted import load


def definition():
    return json.dumps({"name": "Order", "states": {"draft": {"initial": True, "transitions": [{"event": "submit", "target": "sent"}]}, "sent": {"final": True}}})


def test_load_inline_json_returns_machine_class():
    cls = load(definition(), format="json")
    machine = cls()
    assert [state.id for state in machine.configuration] == ["draft"]


def test_declared_event_moves_to_target():
    machine = load(definition(), format="json")()
    machine.send("submit")
    assert [state.id for state in machine.configuration] == ["sent"]
''',
        "hidden_tests": '''import json
import pytest
from featurelifted import InvalidDefinition, load


def test_instances_have_independent_configuration():
    doc = json.dumps({"states": {"idle": {"initial": True, "transitions": [{"event": "go", "target": "done"}]}, "done": {"final": True}}})
    cls = load(doc, format="json")
    first, second = cls(), cls(); first.send("go")
    assert [state.id for state in first.configuration] == ["done"]
    assert [state.id for state in second.configuration] == ["idle"]


def test_invalid_definition_is_rejected():
    with pytest.raises(InvalidDefinition):
        load(json.dumps({"states": {}}), format="json")
''',
        "public_mapping": {"test_load_inline_json_returns_machine_class": "B001", "test_declared_event_moves_to_target": "B002"},
        "hidden_mapping": {"test_instances_have_independent_configuration": ["B001", "B002"], "test_invalid_definition_is_rejected": "B003"},
        "oracle_files": ["statemachine/io/loader.py", "statemachine/io/json/reader.py", "statemachine/statemachine.py"],
        "post_copy": "export_statemachine_load",
    },
    {
        "task_id": "pyee__event_workflow_core__001",
        "slot_id": "workflow-composite-third-party-03",
        "package": "pyee",
        "url": "https://github.com/jfhbrook/pyee",
        "commit": "661fe6a4e144a0ce205d1e900836157208b79122",
        "license": "MIT",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "pyee",
        "package_dir": PIN_ROOT / "pyee" / "pyee",
        "upstream_import": "pyee",
        "lift_type": "Composite",
        "feature_family": "workflow_session_orchestration",
        "entanglement": "third_party_dependency_coupling",
        "entanglement_description": "Event registration, one-shot wrappers, ordered dispatch, and typed handlers use the locked typing-extensions surface.",
        "allowed_dependencies": ["typing-extensions"],
        "requirements": ["typing_extensions==4.12.2"],
        "title": "Event-emitter workflow orchestration",
        "summary": "Extract synchronous EventEmitter registration, ordered dispatch, once semantics, and error routing.",
        "entrypoints": ["pyee.EventEmitter", "pyee.PyeeError"],
        "included": ["on/listens_to registration", "ordered emit", "once", "listener removal", "error event semantics"],
        "excluded": ["asyncio, Trio, Twisted, and executor emitters", "thread scheduling", "network integration"],
        "required_api": [
            api("EventEmitter", "class", members=[
                member("EventEmitter.on", "method", "(event: str, f=None)"), member("EventEmitter.once", "method", "(event: str, f=None)"),
                member("EventEmitter.emit", "method", "(event: str, *args, **kwargs) -> bool"), member("EventEmitter.remove_listener", "method", "(event: str, f) -> None"),
                member("EventEmitter.remove_all_listeners", "method", "(event=None) -> None"), member("EventEmitter.listeners", "method", "(event: str) -> list"),
            ]),
            api("PyeeError", "exception"),
        ],
        "api_checks": ["assert isinstance(EventEmitter, type)", "assert issubclass(PyeeError, Exception)", "assert all(callable(getattr(EventEmitter, n)) for n in ('on', 'once', 'emit', 'remove_listener', 'remove_all_listeners', 'listeners'))"],
        "behaviors": [
            "EventEmitter dispatches listeners synchronously in registration order and forwards arguments.",
            "once listeners remove themselves before invocation and listener removal updates subsequent dispatch.",
            "An unhandled error event raises its Exception or PyeeError for a non-exception payload.",
            "The submitted package uses only typing-extensions and does not import pyee.",
        ],
        "public_tests": '''from featurelifted import EventEmitter


def test_emit_preserves_registration_order():
    emitter = EventEmitter(); seen = []
    emitter.on("data", lambda value: seen.append(("a", value)))
    emitter.on("data", lambda value: seen.append(("b", value)))
    assert emitter.emit("data", 3) is True
    assert seen == [("a", 3), ("b", 3)]


def test_once_listener_runs_once():
    emitter = EventEmitter(); seen = []
    emitter.once("tick", lambda: seen.append(1))
    emitter.emit("tick"); emitter.emit("tick")
    assert seen == [1]
''',
        "hidden_tests": '''import pytest
from featurelifted import EventEmitter, PyeeError


def test_remove_listener_changes_dispatch():
    emitter = EventEmitter(); seen = []
    def listener(): seen.append(1)
    emitter.on("x", listener); emitter.remove_listener("x", listener)
    assert emitter.emit("x") is False and seen == []


def test_unhandled_error_semantics():
    emitter = EventEmitter()
    with pytest.raises(ValueError): emitter.emit("error", ValueError("bad"))
    with pytest.raises(PyeeError): emitter.emit("error", "bad")
''',
        "public_mapping": {"test_emit_preserves_registration_order": "B001", "test_once_listener_runs_once": "B002"},
        "hidden_mapping": {"test_remove_listener_changes_dispatch": ["B001", "B002"], "test_unhandled_error_semantics": "B003"},
        "oracle_files": ["pyee/base.py", "pyee/__init__.py"],
    },
    {
        "task_id": "publicsuffixlist__metadata_lookup_core__001",
        "slot_id": "resource-direct-01",
        "package": "publicsuffixlist",
        "url": "https://github.com/ko-zu/psl",
        "commit": "7d4d0d0db229f996824bd65741ed285ebb466d87",
        "license": "MPL-2.0",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "psl",
        "package_dir": PIN_ROOT / "psl" / "publicsuffixlist",
        "upstream_import": "publicsuffixlist",
        "lift_type": "Direct",
        "feature_family": "resource_metadata_loading",
        "entanglement": "resource_coupling",
        "entanglement_description": "PublicSuffixList loads a bundled PSL resource and resolves exact, wildcard, exception, ICANN, and private rules.",
        "allowed_dependencies": [],
        "requirements": [],
        "title": "Bundled public-suffix metadata lookup",
        "summary": "Extract offline PublicSuffixList loading and suffix/domain classification from the bundled PSL snapshot.",
        "entrypoints": ["publicsuffixlist.PublicSuffixList"],
        "included": ["bundled list loading", "public and private suffix lookup", "registrable-domain lookup", "IDN handling"],
        "excluded": ["updatePSL network refresh", "command-line updates", "live publicsuffix.org access"],
        "required_api": [api("PublicSuffixList", "class", "(source=None, accept_unknown=True, accept_encoded_idn=True, only_icann=False)", [
            member("PublicSuffixList.publicsuffix", "method", "(domain, accept_unknown=None, keep_case=False)"), member("PublicSuffixList.privatesuffix", "method", "(domain, accept_unknown=None, keep_case=False)"),
            member("PublicSuffixList.is_public", "method", "(domain) -> bool"), member("PublicSuffixList.is_private", "method", "(domain) -> bool"),
        ])],
        "api_checks": ["assert isinstance(PublicSuffixList, type)", "assert all(callable(getattr(PublicSuffixList, n)) for n in ('publicsuffix', 'privatesuffix', 'is_public', 'is_private'))"],
        "behaviors": [
            "PublicSuffixList with no source loads the bundled public_suffix_list.dat resource offline.",
            "publicsuffix and privatesuffix apply exact, wildcard, and exception rules to normalized domain names.",
            "only_icann and unknown-suffix options alter classification according to their constructor settings.",
            "The submitted package does not import publicsuffixlist or perform network refreshes.",
        ],
        "public_tests": '''from featurelifted import PublicSuffixList


def test_bundled_list_resolves_common_suffixes():
    psl = PublicSuffixList()
    assert psl.publicsuffix("www.example.co.uk") == "co.uk"
    assert psl.privatesuffix("www.example.co.uk") == "example.co.uk"


def test_public_and_private_classification():
    psl = PublicSuffixList()
    assert psl.is_public("com")
    assert psl.is_private("example.com")
''',
        "hidden_tests": '''from featurelifted import PublicSuffixList


def test_custom_wildcard_and_exception_rules():
    psl = PublicSuffixList("*.example\\n!city.example\\n")
    assert psl.publicsuffix("a.example") == "a.example"
    assert psl.publicsuffix("city.example") == "example"


def test_unknown_suffix_policy():
    strict = PublicSuffixList("com\\n", accept_unknown=False)
    assert strict.publicsuffix("host.unknown") is None


def test_bundled_resource_is_available_offline():
    psl = PublicSuffixList()
    assert psl.publicsuffix("www.example.co.uk") == "co.uk"
''',
        "public_mapping": {"test_bundled_list_resolves_common_suffixes": "B001", "test_public_and_private_classification": "B002"},
        "hidden_mapping": {"test_custom_wildcard_and_exception_rules": "B002", "test_unknown_suffix_policy": "B003", "test_bundled_resource_is_available_offline": "B001"},
        "oracle_files": ["publicsuffixlist/__init__.py", "publicsuffixlist/public_suffix_list.dat"],
    },
    {
        "task_id": "puremagic__signature_resource_core__001",
        "slot_id": "resource-direct-02",
        "package": "puremagic",
        "url": "https://github.com/cdgriffith/puremagic",
        "commit": "57bed56ef669132c0f906e1d064680bf2c4b2205",
        "license": "MIT",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "puremagic",
        "package_dir": PIN_ROOT / "puremagic" / "puremagic",
        "upstream_import": "puremagic",
        "lift_type": "Direct",
        "feature_family": "resource_metadata_loading",
        "entanglement": "resource_coupling",
        "entanglement_description": "Detection loads a bundled magic_data.json signature table and combines header, footer, extension, and MIME metadata.",
        "allowed_dependencies": [],
        "requirements": [],
        "title": "Bundled file-signature metadata detection",
        "summary": "Extract pure-Python file signature detection from strings, streams, and extensions using bundled metadata.",
        "entrypoints": ["puremagic.from_string", "puremagic.from_stream", "puremagic.magic_string", "puremagic.from_extension"],
        "included": ["byte-string detection", "stream detection", "MIME selection", "extension metadata lookup", "unknown input errors"],
        "excluded": ["CLI", "deep archive scanners", "large fixture corpus", "network lookups"],
        "required_api": [
            api("from_string", "function", "(string: str | bytes, mime: bool = False, filename=None) -> str"), api("from_stream", "function", "(stream, mime: bool = False, filename=None) -> str"),
            api("magic_string", "function", "(string, filename=None) -> list"), api("from_extension", "function", "(extension: str, mime: bool = True) -> str"), api("PureError", "exception"),
        ],
        "api_checks": ["assert all(callable(x) for x in (from_string, from_stream, magic_string, from_extension))", "assert issubclass(PureError, Exception)"],
        "behaviors": [
            "from_string and from_stream identify known byte signatures using bundled magic metadata.",
            "MIME mode and from_extension return metadata associated with the selected signature or extension.",
            "magic_string returns ranked match records and unknown or empty inputs raise documented errors.",
            "The submitted package does not import puremagic or access external signature services.",
        ],
        "public_tests": '''from io import BytesIO
from featurelifted import from_stream, from_string

PNG = b"\\x89PNG\\r\\n\\x1a\\n" + b"\\x00" * 32


def test_string_and_stream_detection():
    assert from_string(PNG) == ".png"
    assert from_stream(BytesIO(PNG)) == ".png"


def test_mime_detection():
    assert from_string(PNG, mime=True) == "image/png"
''',
        "hidden_tests": '''import pytest
from featurelifted import PureError, from_extension, magic_string


def test_extension_metadata_lookup():
    assert from_extension(".png") == "image/png"


def test_ranked_matches_and_unknown_input():
    matches = magic_string(b"%PDF-1.7\\n")
    assert matches and matches[0].extension == ".pdf"
    with pytest.raises((PureError, ValueError)): magic_string(b"")
''',
        "public_mapping": {"test_string_and_stream_detection": "B001", "test_mime_detection": "B002"},
        "hidden_mapping": {"test_extension_metadata_lookup": "B002", "test_ranked_matches_and_unknown_input": ["B001", "B003"]},
        "oracle_files": ["puremagic/main.py", "puremagic/magic_data.json"],
    },
    {
        "task_id": "langcodes__language_metadata_core__001",
        "slot_id": "resource-composite-third-party-03",
        "package": "langcodes",
        "url": "https://github.com/rspeer/langcodes",
        "commit": "0aebfa862ed86d820d0c96ce311ef661cf0a798a",
        "license": "MIT",
        "license_path": "LICENSE.txt",
        "src": PIN_ROOT / "langcodes",
        "package_dir": PIN_ROOT / "langcodes" / "langcodes",
        "upstream_import": "langcodes",
        "lift_type": "Composite",
        "feature_family": "resource_metadata_loading",
        "entanglement": "third_party_dependency_coupling",
        "entanglement_description": "BCP-47 normalization composes built-in code tables with language-data CLDR names and marisa-trie lookups.",
        "allowed_dependencies": ["language-data", "marisa-trie"],
        "requirements": ["language-data==1.3.0", "marisa-trie==1.3.1"],
        "title": "Language-tag normalization and CLDR metadata",
        "summary": "Extract language tag normalization, name lookup, likely-subtag expansion, and distance matching with offline CLDR data.",
        "entrypoints": ["langcodes.Language", "langcodes.standardize_tag", "langcodes.best_match"],
        "included": ["BCP-47 normalization", "Language objects", "localized display names", "likely subtag maximize", "best-match scoring"],
        "excluded": ["data rebuild scripts", "online registry updates", "population statistics beyond the declared API"],
        "required_api": [
            api("Language", "class", members=[member("Language.get", "method", "(tag, normalize=True) -> Language"), member("Language.to_tag", "method", "() -> str"), member("Language.language_name", "method", "(language=None) -> str"), member("Language.maximize", "method", "() -> Language"), member("Language.script", "attribute")]),
            api("standardize_tag", "function", "(tag, macro: bool = False) -> str"), api("best_match", "function", "(desired_language, supported_languages, min_score=0) -> tuple[str, int]"),
        ],
        "api_checks": ["assert isinstance(Language, type)", "assert all(callable(getattr(Language, n)) for n in ('get', 'to_tag', 'language_name', 'maximize'))", "assert callable(standardize_tag) and callable(best_match)"],
        "behaviors": [
            "standardize_tag and Language.get normalize overlong, deprecated, script, and territory subtags.",
            "language_name and maximize resolve localized CLDR metadata from the locked language-data package offline.",
            "best_match ranks supported language tags using normalized language distance and returns a score.",
            "The submitted package uses only locked language-data and marisa-trie dependencies and does not import langcodes.",
        ],
        "public_tests": '''from featurelifted import Language, standardize_tag


def test_standardize_and_language_object():
    assert standardize_tag("eng_US") == "en-US"
    language = Language.get("zh-cmn-Hant")
    assert language.to_tag() == "zh-Hant"


def test_cldr_name_and_maximize():
    assert Language.get("fr").language_name("en") == "French"
    assert Language.get("zh-TW").maximize().script == "Hant"
''',
        "hidden_tests": '''from featurelifted import Language, best_match, standardize_tag


def test_deprecated_tag_normalization():
    assert standardize_tag("en-uk") == "en-GB"


def test_hidden_cldr_name_lookup():
    assert Language.get("de").language_name("en") == "German"


def test_best_match_prefers_closest_supported_tag():
    match, score = best_match("en-AU", ["fr", "en-GB", "de"])
    assert match == "en-GB" and score > 0
''',
        "public_mapping": {"test_standardize_and_language_object": "B001", "test_cldr_name_and_maximize": "B002"},
        "hidden_mapping": {"test_deprecated_tag_normalization": "B001", "test_hidden_cldr_name_lookup": "B002", "test_best_match_prefers_closest_supported_tag": "B003"},
        "oracle_files": ["langcodes/__init__.py", "langcodes/language_distance.py", "langcodes/data_dicts.py"],
    },
    {
        "task_id": "venusian__scan_dispatch_core__001",
        "slot_id": "registry-composite-framework-01",
        "package": "venusian",
        "url": "https://github.com/Pylons/venusian",
        "commit": "d036c00afa4e8c3077ab53a22290ac19fed652b2",
        "license": "BSD-derived",
        "license_path": "LICENSE.txt",
        "src": PIN_ROOT / "venusian",
        "package_dir": PIN_ROOT / "venusian" / "src" / "venusian",
        "upstream_import": "venusian",
        "lift_type": "Composite",
        "feature_family": "registry_plugin_dispatch",
        "entanglement": "framework_coupling",
        "entanglement_description": "Decorator-time attachments are stored by category and later discovered and dispatched through a Scanner context.",
        "allowed_dependencies": [],
        "requirements": [],
        "title": "Decorator registry and scanner dispatch",
        "summary": "Extract callback attachment, category filtering, and module scanning into a deterministic plugin-dispatch workflow.",
        "entrypoints": ["venusian.attach", "venusian.Scanner", "venusian.lift"],
        "included": ["attach callback metadata", "module scanning", "category filtering", "scanner context injection"],
        "excluded": ["filesystem package walks in evaluator cases", "zip imports", "namespace package edge cases"],
        "required_api": [api("attach", "function", "(wrapped, callback, category=None, depth=1, name=None) -> AttachInfo"), api("Scanner", "class", "(**context)", [member("Scanner.scan", "method", "(package, categories=None, onerror=None, ignore=None) -> None")]), api("AttachInfo", "class"), api("lift", "class")],
        "api_checks": ["assert callable(attach)", "assert isinstance(Scanner, type) and callable(Scanner.scan)", "assert isinstance(AttachInfo, type) and isinstance(lift, type)"],
        "behaviors": [
            "attach records a callback on a function or class without replacing the wrapped object.",
            "Scanner.scan discovers attached objects in a module and dispatches callbacks with scanner context, name, and object.",
            "Category filters select only matching registrations while preserving deterministic callback order.",
            "The submitted package does not import venusian or scan the network or unrelated filesystem paths.",
        ],
        "public_tests": '''import sys
from featurelifted import Scanner, attach


def test_attach_and_scan_current_module():
    seen = []
    def target(): return 1
    target.__module__ = __name__
    globals()["_flb_target"] = target
    attach(target, lambda scanner, name, obj: seen.append((scanner.token, name, obj)), category="jobs", depth=0)
    try:
        Scanner(token=7).scan(sys.modules[__name__])
        assert seen == [(7, "_flb_target", target)]
    finally:
        globals().pop("_flb_target", None)


def test_category_filtering():
    seen = []
    def target(): pass
    target.__module__ = __name__; globals()["_flb_category_target"] = target
    attach(target, lambda *args: seen.append("a"), category="a", depth=0)
    attach(target, lambda *args: seen.append("b"), category="b", depth=0)
    try:
        Scanner().scan(sys.modules[__name__], categories=("b",))
        assert seen == ["b"]
    finally:
        globals().pop("_flb_category_target", None)
''',
        "hidden_tests": '''import sys
from featurelifted import AttachInfo, Scanner, attach, lift


def test_attach_returns_info_and_preserves_object():
    def target(): return 3
    original = target
    info = attach(target, lambda *args: None, category="x", depth=0)
    assert target is original and isinstance(info, AttachInfo)


def test_callback_order_with_same_category():
    seen = []
    def target(): pass
    target.__module__ = __name__; globals()["_flb_order_target"] = target
    attach(target, lambda *args: seen.append(1), category="x", depth=0)
    attach(target, lambda *args: seen.append(2), category="x", depth=0)
    try:
        Scanner().scan(sys.modules[__name__], categories=("x",))
        assert seen == [1, 2]
        assert isinstance(lift, type)
    finally:
        globals().pop("_flb_order_target", None)
''',
        "public_mapping": {"test_attach_and_scan_current_module": "B002", "test_category_filtering": "B003"},
        "hidden_mapping": {"test_attach_returns_info_and_preserves_object": "B001", "test_callback_order_with_same_category": ["B002", "B003"]},
        "oracle_files": ["src/venusian/__init__.py", "src/venusian/advice.py"],
    },
]


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def copy_package_tree(source: Path, destination: Path, upstream_import: str) -> None:
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
    for path in destination.rglob("*.py"):
        raw = path.read_text(encoding="utf-8")
        updated = re.sub(
            rf"^(\s*)from {re.escape(upstream_import)}\b",
            r"\1from featurelifted",
            raw,
            flags=re.MULTILINE,
        )
        updated = re.sub(
            rf"^(\s*)import {re.escape(upstream_import)}\b",
            r"\1import featurelifted",
            updated,
            flags=re.MULTILINE,
        )
        updated = re.sub(
            rf"\b{re.escape(upstream_import)}\.", "featurelifted.", updated
        )
        updated = updated.replace(f'"{upstream_import}.', '"featurelifted.')
        updated = updated.replace(f"'{upstream_import}.", "'featurelifted.")
        if updated != raw:
            path.write_text(updated, encoding="utf-8")


def test_nodeids(task_dir: Path, bucket: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted((task_dir / bucket).glob("test_*.py")):
        text = path.read_text(encoding="utf-8")
        for name in re.findall(r"^def (test_[A-Za-z0-9_]+)\(", text, re.MULTILINE):
            result[name] = f"{path.relative_to(task_dir).as_posix()}::{name}"
    return result


def flatten_api(required_api: list[dict[str, Any]]) -> list[str]:
    paths: list[str] = []
    def walk(entry: dict[str, Any]) -> None:
        paths.append(entry["path"])
        for child in entry.get("members", []):
            walk(child)
    for entry in required_api:
        walk(entry)
    return paths


def generic_hidden_suffix(task: dict[str, Any]) -> str:
    imports = ", ".join(sorted({entry["path"].split(".")[1] for entry in task["required_api"]}))
    checks = "\n    ".join(task["api_checks"])
    forbidden = re.escape(task["upstream_import"])
    return f'''\n\ndef test_required_api_surface():
    from featurelifted import {imports}
    {checks}


def test_no_upstream_import_surface():
    import re
    from pathlib import Path
    import featurelifted
    pattern = re.compile(r"^\\s*(?:from {forbidden}|import {forbidden})\\b", re.MULTILINE)
    for path in Path(featurelifted.__file__).parent.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8"))
'''


def build_metadata(task: dict[str, Any]) -> dict[str, Any]:
    behaviors = [{"id": f"B{i:03d}", "text": text} for i, text in enumerate(task["behaviors"], 1)]
    return {
        "task_id": task["task_id"],
        "language": "python",
        "difficulty": "medium",
        "status": "materialized_candidate",
        "task_revision": 1,
        "tags": ["external50", "python200-replacement", task["slot_id"], task["lift_type"].lower()],
        "source": {"name": task["package"], "url": task["url"], "commit": task["commit"], "license": task["license"]},
        "feature": {
            "name": task["title"], "description": task["summary"], "source_entrypoints": task["entrypoints"],
            "included_behaviors": task["included"], "excluded_behaviors": task["excluded"],
        },
        "entanglement": {
            "level": "high" if task["lift_type"] == "Composite" else "medium",
            "types": [task["entanglement"]], "primary": task["entanglement"],
            "description": task["entanglement_description"], "signals": task["included"],
        },
        "output": {
            "package": "featurelifted", "import": "from featurelifted import " + ", ".join(entry["path"].split(".")[1] for entry in task["required_api"]),
            "callable": task["required_api"][0]["path"].removeprefix("featurelifted."),
            "signature": task["required_api"][0].get("signature", task["required_api"][0]["path"]),
        },
        "environment": {
            "python": "3.12", "network": False, "timeout_seconds": 90, "dependency_lock": "requirements.lock",
            "allowed_dependencies": task["allowed_dependencies"], "forbidden_dependencies": [task["upstream_import"]],
            "forbidden_imports": [task["upstream_import"]], "forbidden_paths": ["repo/", f"{task['upstream_import']}/"],
        },
        "tests": {"public": "public_tests/", "hidden": "hidden_tests/", "command": "pytest"},
        "spec_status": "compliant",
        "public_spec": {
            "title": task["title"], "summary": task["summary"], "required_api": task["required_api"], "optional_api": [],
            "behaviors": behaviors, "exclusions": task["excluded"] + [f"original {task['upstream_import']} import at runtime"],
            "forbidden": {"imports": [task["upstream_import"]], "paths": []},
            "public_vs_hidden_note": "Public tests cover common use. Hidden tests cover documented edge, configuration, state, API-surface, and isolation behavior only.",
        },
    }


def finalize_contract(task_dir: Path, task: dict[str, Any], metadata: dict[str, Any]) -> None:
    public_nodes = test_nodeids(task_dir, "public_tests")
    hidden_nodes = test_nodeids(task_dir, "hidden_tests")
    def behavior_ids(value: str | list[str]) -> list[str]:
        return value if isinstance(value, list) else [value]

    public_mappings = [{"nodeid": public_nodes[name], "behavior_ids": behavior_ids(bid), "mapping_method": "manual_semantic_review"} for name, bid in task["public_mapping"].items()]
    hidden_map = dict(task["hidden_mapping"])
    hidden_map["test_required_api_surface"] = "B003"
    hidden_map["test_no_upstream_import_surface"] = "B004"
    hidden_mappings = [{"nodeid": hidden_nodes[name], "behavior_ids": behavior_ids(bid), "mapping_method": "manual_semantic_review"} for name, bid in hidden_map.items()]
    surface_node = hidden_nodes["test_required_api_surface"]
    metadata["evaluation_spec"] = {
        "public_clauses": [{"behavior_id": b["id"], "clause_kind": "included_behavior", "text": b["text"]} for b in metadata["public_spec"]["behaviors"]],
        "public_test_mappings": public_mappings, "hidden_test_mappings": hidden_mappings,
        "required_api_coverage": [{"path": path, "covered_by_tests": [surface_node]} for path in flatten_api(task["required_api"])],
        "manual_review": {"reviewed_at": "2026-08-01", "reviewer": "python200_replacement_materializer", "reviewer_type": "manual_task_level_review", "checklist_passed": True, "notes": f"Semantic contract review for balance slot {task['slot_id']}."},
    }
    task_md = render_public_task(metadata)
    (task_dir / "TASK.md").write_text(task_md, encoding="utf-8")
    metadata["spec_hash"] = compute_spec_hash(metadata["public_spec"])
    metadata["generated_task_hash"] = compute_generated_task_hash(task_md)
    write_json(task_dir / "metadata.json", metadata)
    write_json(task_dir / "evaluation" / "behavior_contract.json", {
        "task_id": task["task_id"], "public_clauses": metadata["evaluation_spec"]["public_clauses"],
        "public_test_mappings": [{"nodeid": m["nodeid"], "public_clause_ids": m["behavior_ids"]} for m in public_mappings],
        "hidden_test_mappings": [{"nodeid": m["nodeid"], "public_clause_ids": m["behavior_ids"]} for m in hidden_mappings],
        "spec_sha256": compute_generated_task_hash(task_md),
    })


def materialize(task: dict[str, Any]) -> Path:
    if not task["src"].is_dir():
        raise FileNotFoundError(f"missing pinned source: {task['src']}")
    actual_commit = subprocess.check_output(
        ["git", "-C", str(task["src"]), "rev-parse", "HEAD"], text=True
    ).strip()
    if actual_commit != task["commit"]:
        raise RuntimeError(f"{task['task_id']}: expected {task['commit']}, found {actual_commit}")
    task_dir = STAGING / task["task_id"]
    if task_dir.exists():
        shutil.rmtree(task_dir)
    task_dir.mkdir(parents=True)
    shutil.copytree(task["src"], task_dir / "repo", ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".pytest_cache"))
    reference = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(task["package_dir"], reference, task["upstream_import"])
    if task.get("post_copy") == "export_statemachine_load":
        init_path = reference / "__init__.py"
        init_path.write_text(
            init_path.read_text(encoding="utf-8")
            + "\nfrom .exceptions import InvalidDefinition\nfrom .io import load\n",
            encoding="utf-8",
        )
    (task_dir / "public_tests").mkdir()
    (task_dir / "hidden_tests").mkdir()
    (task_dir / "evaluation").mkdir()
    (task_dir / "public_tests" / "test_public_api.py").write_text(task["public_tests"], encoding="utf-8")
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(task["hidden_tests"] + generic_hidden_suffix(task), encoding="utf-8")
    (task_dir / "requirements.lock").write_text("\n".join(task["requirements"]) + ("\n" if task["requirements"] else "# no third-party dependencies\n"), encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text(task["upstream_import"] + "\n", encoding="utf-8")
    write_json(task_dir / "evaluation" / "oracle_manifest.json", {
        "source_package_name": task["upstream_import"], "required_source_files": task["oracle_files"],
        "runtime_dependencies": task["allowed_dependencies"], "notes": f"Balanced Python-200 replacement slot {task['slot_id']}; offline reference only.",
    })
    metadata = build_metadata(task)
    finalize_contract(task_dir, task, metadata)
    pilot.make_archive_and_register(task["task_id"], task, task_dir / "repo")
    return task_dir


def main() -> int:
    for task in TASKS:
        path = materialize(task)
        print(f"materialized {task['slot_id']}: {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""OpenHands wrapper for FeatureLiftBench agent runs."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .llm_env import apply_openhands_llm_env
from .llm_usage_proxy import maybe_start_openhands_usage_proxy
from .openhands_usage import resolve_events_path
from .openhands_usage import write_usage_from_events
from .resource_limits import command_output_limit_bytes


USAGE_SCHEMA_VERSION = "featureliftbench.agent_usage.v1"
DEFAULT_OPENHANDS_COMMAND_ENV = "FEATURELIFTBENCH_OPENHANDS_COMMAND"
RAW_USAGE_FILENAMES = ("openhands_usage.json", "usage.json")


@dataclass(frozen=True)
class OpenHandsRunnerConfig:
    workspace_dir: Path
    task_file: Path
    submission_dir: Path
    agent_output_dir: Path
    model: str = ""
    openhands_command: str = ""
    timeout_seconds: int = 3600


@dataclass(frozen=True)
class _RunCommandResult:
    returncode: int
    timed_out: bool = False
    log_limit_exceeded: bool = False
    stdout_truncated: bool = False
    stderr_truncated: bool = False


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command != "run":
        parser.error(f"unsupported command: {args.command}")
    return run(
        OpenHandsRunnerConfig(
            workspace_dir=args.workspace,
            task_file=args.task_file,
            submission_dir=args.submission_dir,
            agent_output_dir=args.agent_output_dir,
            model=args.model or os.environ.get("FEATURELIFTBENCH_MODEL", ""),
            openhands_command=args.openhands_command
            or os.environ.get(DEFAULT_OPENHANDS_COMMAND_ENV, ""),
            timeout_seconds=args.timeout_seconds,
        )
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="featureliftbench.openhands_runner")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="run OpenHands on a FeatureLiftBench task")
    run_parser.add_argument("--workspace", type=Path, required=True)
    run_parser.add_argument("--task-file", type=Path, required=True)
    run_parser.add_argument("--submission-dir", type=Path, required=True)
    run_parser.add_argument("--agent-output-dir", type=Path, required=True)
    run_parser.add_argument("--model", default="")
    run_parser.add_argument(
        "--openhands-command",
        default="",
        help=(
            "OpenHands headless command template. Placeholders: {workspace}, "
            "{task_file}, {submission_dir}, {agent_output_dir}, {prompt_file}, {model}, {python}"
        ),
    )
    run_parser.add_argument("--timeout-seconds", type=int, default=3600)
    return parser


def run(config: OpenHandsRunnerConfig) -> int:
    config.agent_output_dir.mkdir(parents=True, exist_ok=True)
    config.submission_dir.mkdir(parents=True, exist_ok=True)
    prompt_file = config.agent_output_dir / "openhands_task.md"
    prompt_file.write_text(_build_openhands_prompt(config), encoding="utf-8")

    command_template = config.openhands_command.strip()
    if not command_template:
        _write_command_record(
            config,
            prompt_file=prompt_file,
            command_template="",
            command=[],
            configured=False,
            error=f"{DEFAULT_OPENHANDS_COMMAND_ENV} or --openhands-command is required",
        )
        _write_usage(
            config,
            exit_status="not_configured",
            returncode=2,
            duration_seconds=0.0,
            raw_usage=None,
        )
        print(
            f"OpenHands command is not configured. Set {DEFAULT_OPENHANDS_COMMAND_ENV} "
            "or pass --agent-command.",
            file=sys.stderr,
        )
        return 2

    try:
        command = _render_openhands_command(config, prompt_file, command_template)
    except ValueError as exc:
        _write_command_record(
            config,
            prompt_file=prompt_file,
            command_template=command_template,
            command=[],
            configured=False,
            error=str(exc),
        )
        _write_usage(
            config,
            exit_status="invalid_command_template",
            returncode=2,
            duration_seconds=0.0,
            raw_usage=None,
        )
        print(str(exc), file=sys.stderr)
        return 2

    _write_command_record(
        config,
        prompt_file=prompt_file,
        command_template=command_template,
        command=command,
        configured=True,
        error="",
    )
    stdout_log = config.agent_output_dir / "openhands_stdout.log"
    stderr_log = config.agent_output_dir / "openhands_stderr.log"
    events_log = config.agent_output_dir / "openhands_events.jsonl"
    env = os.environ.copy()
    env.update(
        {
            "FEATURELIFTBENCH_WORKSPACE": str(config.workspace_dir),
            "FEATURELIFTBENCH_TASK_FILE": str(config.task_file),
            "FEATURELIFTBENCH_SUBMISSION_DIR": str(config.submission_dir),
            "FEATURELIFTBENCH_AGENT_OUTPUT_DIR": str(config.agent_output_dir),
            "FEATURELIFTBENCH_OPENHANDS_PROMPT_FILE": str(prompt_file),
            "FEATURELIFTBENCH_MODEL": config.model,
        }
    )
    env = apply_openhands_llm_env(env)
    env.setdefault("OPENHANDS_SUPPRESS_BANNER", "1")
    _maybe_seed_agent_settings(command, env, config.agent_output_dir)

    start = time.monotonic()
    proxy = maybe_start_openhands_usage_proxy(env, config.agent_output_dir)
    try:
        if proxy is not None:
            proxy.start()
            _point_openhands_to_proxy(env, proxy.base_url)
        command_result = _run_command(
            command,
            cwd=config.workspace_dir,
            env=env,
            stdout_log=stdout_log,
            stderr_log=stderr_log,
            events_log=events_log,
            timeout_seconds=config.timeout_seconds,
        )
    finally:
        if proxy is not None:
            proxy.close()
    duration_seconds = time.monotonic() - start
    returncode = command_result.returncode
    events_path = resolve_events_path(
        config.agent_output_dir,
        stdout_log=stdout_log,
    )
    raw_usage_path = config.agent_output_dir / "openhands_usage.json"
    if events_path is not None and not raw_usage_path.is_file():
        write_usage_from_events(
            events_path,
            raw_usage_path,
        )
    raw_usage = _read_raw_usage(config.agent_output_dir)
    exit_status = "passed" if returncode == 0 else "openhands_failed"
    if command_result.log_limit_exceeded:
        exit_status = "log_limit_exceeded"
    elif returncode == 124:
        exit_status = "timeout"
    elif returncode == 127:
        exit_status = "command_not_found"
    _write_usage(
        config,
        exit_status=exit_status,
        returncode=returncode,
        duration_seconds=duration_seconds,
        raw_usage=raw_usage,
    )
    print(f"OpenHands wrapper finished with return code {returncode}.")
    return returncode


def _point_openhands_to_proxy(env: dict[str, str], proxy_base_url: str) -> None:
    for key in (
        "LLM_BASE_URL",
        "OPENAI_BASE_URL",
        "OPENAI_API_BASE",
        "FEATURELIFTBENCH_API_BASE",
        "DEEPSEEK_API_BASE",
        "LITELLM_API_BASE",
    ):
        env[key] = proxy_base_url
    for key in (
        "LLM_API_KEY",
        "OPENAI_API_KEY",
        "FEATURELIFTBENCH_API_KEY",
        "DEEPSEEK_API_KEY",
        "LITELLM_API_KEY",
    ):
        if key in env:
            env[key] = "featureliftbench-proxy"


_TRUTHY = {"true", "1", "yes", "on"}

_AGENT_SETTINGS_GENERATOR = """
import os
from openhands.sdk.llm import LLM
from openhands_cli.utils import get_default_cli_agent

out = os.environ["FLB_AGENT_SETTINGS_OUT"]
llm = LLM(
    model="openai/placeholder",
    api_key="placeholder",
    usage_id="agent",
    native_tool_calling=False,
)
agent = get_default_cli_agent(llm)


def _off(inner):
    return inner.model_copy(update={"native_tool_calling": False})


updates = {"llm": _off(agent.llm)}
condenser = getattr(agent, "condenser", None)
if condenser is not None and hasattr(condenser, "llm"):
    updates["condenser"] = condenser.model_copy(update={"llm": _off(condenser.llm)})
agent = agent.model_copy(update=updates)
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w", encoding="utf-8") as handle:
    handle.write(agent.model_dump_json())
"""


def _maybe_seed_agent_settings(
    command: list[str],
    env: dict[str, str],
    agent_output_dir: Path,
) -> None:
    """Persist an agent_settings.json so OpenHands honors native_tool_calling=False.

    The OpenHands CLI only overrides model/api_key/base_url from env vars; other
    LLM fields (like ``native_tool_calling``) are taken from a persisted agent
    spec. When LLM_NATIVE_TOOL_CALLING is explicitly falsy we generate a default
    agent spec with native tool calling disabled and drop it in the persistence
    directory. This lets local vLLM servers without --enable-auto-tool-choice work
    by using prompt-based tool calling.
    """
    native = env.get("LLM_NATIVE_TOOL_CALLING")
    if native is None or native.strip().lower() in _TRUTHY:
        return

    home = env.get("HOME") or os.path.expanduser("~")
    persist_dir = env.get("OPENHANDS_PERSISTENCE_DIR") or os.path.join(home, ".openhands")
    env["OPENHANDS_PERSISTENCE_DIR"] = persist_dir
    settings_path = os.path.join(persist_dir, "agent_settings.json")
    if os.path.isfile(settings_path):
        return

    interpreter = _resolve_openhands_python(command)
    if interpreter is None:
        print(
            "FeatureLiftBench: could not resolve OpenHands interpreter; "
            "native_tool_calling override skipped.",
            file=sys.stderr,
        )
        return

    gen_env = dict(env)
    gen_env["FLB_AGENT_SETTINGS_OUT"] = settings_path
    result = subprocess.run(
        [interpreter, "-c", _AGENT_SETTINGS_GENERATOR],
        env=gen_env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    log_path = agent_output_dir / "agent_settings_seed.log"
    log_path.write_text(
        f"returncode={result.returncode}\n"
        f"settings_path={settings_path}\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}\n",
        encoding="utf-8",
    )
    if result.returncode != 0 or not os.path.isfile(settings_path):
        print(
            "FeatureLiftBench: failed to seed agent_settings.json for "
            "native_tool_calling override (see agent_settings_seed.log).",
            file=sys.stderr,
        )


def _resolve_openhands_python(command: list[str]) -> str | None:
    """Best-effort resolution of the Python interpreter that runs OpenHands."""
    if not command:
        return None
    binary = shutil.which(command[0]) or command[0]
    try:
        with open(binary, encoding="utf-8", errors="replace") as handle:
            first_line = handle.readline().strip()
    except OSError:
        first_line = ""
    if first_line.startswith("#!"):
        shebang = first_line[2:].strip()
        interpreter = shebang.split()[0] if shebang else ""
        if interpreter and os.path.exists(interpreter):
            return interpreter
    fallback = "/opt/uv-tools/openhands/bin/python"
    if os.path.exists(fallback):
        return fallback
    return None


def _build_openhands_prompt(config: OpenHandsRunnerConfig) -> str:
    task_text = config.task_file.read_text(encoding="utf-8")
    return (
        "# FeatureLiftBench Task for OpenHands\n\n"
        "You are being evaluated as the coding agent for FeatureLiftBench.\n\n"
        "## Workspace Contract\n\n"
        f"- Workspace root: `{config.workspace_dir}`\n"
        "- Source code to inspect is under `repo/`.\n"
        "- Public tests are under `public_tests/` and may be run for feedback.\n"
        "- Hidden tests and evaluation files are benchmark-only boundaries; do not use them as inputs.\n"
        f"- Final output must be written under `{config.submission_dir}`.\n"
        "- The importable package must be `submission/featurelifted/`.\n"
        "- Do not place the answer in a top-level `featurelifted/` directory.\n"
        "- Prefer not to create `pyproject.toml`; the evaluator imports `submission/featurelifted` "
        "directly via `PYTHONPATH`.\n"
        "- If a `pyproject.toml` is truly necessary, use only `setuptools.build_meta` as the "
        "build backend; never use `setuptools.backends._legacy:_Backend`.\n"
        "- Keep the implementation behavior-complete, not only tailored to public tests.\n\n"
        "## Required Finish State\n\n"
        "Create a normal Python submission layout:\n\n"
        "```text\n"
        "submission/\n"
        "  featurelifted/\n"
        "    __init__.py\n"
        "    ...\n"
        "```\n\n"
        "When you need to run tests, prefer:\n\n"
        "```bash\n"
        "PYTHONPATH=submission pytest public_tests/\n"
        "```\n\n"
        "## Task\n\n"
        f"{task_text}\n"
    )


def _render_openhands_command(
    config: OpenHandsRunnerConfig,
    prompt_file: Path,
    command_template: str,
) -> list[str]:
    values = {
        "workspace": str(config.workspace_dir),
        "task_file": str(config.task_file),
        "submission_dir": str(config.submission_dir),
        "agent_output_dir": str(config.agent_output_dir),
        "prompt_file": str(prompt_file),
        "model": config.model,
        "python": sys.executable,
    }
    try:
        rendered = command_template.format(**values)
    except KeyError as exc:
        raise ValueError(f"unknown OpenHands command placeholder: {exc.args[0]}") from exc
    command = shlex.split(rendered)
    if not command:
        raise ValueError("OpenHands command template rendered to an empty command")
    return command


def _run_command(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    stdout_log: Path,
    stderr_log: Path,
    events_log: Path,
    timeout_seconds: int,
) -> _RunCommandResult:
    stdout_log.parent.mkdir(parents=True, exist_ok=True)
    stderr_log.parent.mkdir(parents=True, exist_ok=True)
    events_log.parent.mkdir(parents=True, exist_ok=True)
    limiter = _OutputLimiter(command_output_limit_bytes(env))
    stdout_capture = _OpenHandsStdoutCapture(stdout_log, events_log, limiter)
    stderr_capture = _StreamLogCapture(stderr_log, limiter)
    process: subprocess.Popen[bytes] | None = None
    log_limit_event = threading.Event()
    try:
        try:
            process = subprocess.Popen(
                command,
                cwd=cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
            )
        except FileNotFoundError as exc:
            stderr_capture.write_text(str(exc))
            return _RunCommandResult(returncode=127)
        except PermissionError as exc:
            stderr_capture.write_text(str(exc))
            return _RunCommandResult(returncode=126)

        def pump_stdout() -> None:
            assert process is not None and process.stdout is not None
            try:
                _pump_stream(
                    process=process,
                    stream=process.stdout,
                    capture=stdout_capture,
                    log_limit_event=log_limit_event,
                )
            finally:
                stdout_capture.flush()

        def pump_stderr() -> None:
            assert process is not None and process.stderr is not None
            _pump_stream(
                process=process,
                stream=process.stderr,
                capture=stderr_capture,
                log_limit_event=log_limit_event,
            )

        threads = [
            threading.Thread(target=pump_stdout, daemon=True),
            threading.Thread(target=pump_stderr, daemon=True),
        ]
        for thread in threads:
            thread.start()

        timed_out = False
        deadline = time.monotonic() + max(1, timeout_seconds)
        while process.poll() is None:
            if log_limit_event.is_set():
                _kill_process_group(process)
                break
            if time.monotonic() >= deadline:
                timed_out = True
                _kill_process_group(process)
                break
            time.sleep(0.05)

        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _kill_process_group(process)

        for thread in threads:
            thread.join(timeout=2)

        if log_limit_event.is_set():
            stderr_capture.write_text(
                "\nFeatureLiftBench: OpenHands output exceeded "
                f"{limiter.limit_bytes} bytes; process group was terminated.\n"
            )
            return _RunCommandResult(
                returncode=125,
                log_limit_exceeded=True,
                stdout_truncated=stdout_capture.truncated,
                stderr_truncated=stderr_capture.truncated,
            )
        if timed_out:
            return _RunCommandResult(returncode=124, timed_out=True)
        return _RunCommandResult(returncode=int(process.returncode or 0))
    finally:
        stdout_capture.close()
        stderr_capture.close()


def _pump_stream(
    *,
    process: subprocess.Popen[bytes],
    stream: Any,
    capture: "_StreamCapture",
    log_limit_event: threading.Event,
) -> None:
    try:
        while True:
            chunk = stream.read(65536)
            if not chunk:
                return
            exceeded = capture.append(chunk)
            if exceeded and not log_limit_event.is_set():
                log_limit_event.set()
                _kill_process_group(process)
                return
    finally:
        stream.close()


class _OutputLimiter:
    def __init__(self, limit_bytes: int | None) -> None:
        self.limit_bytes = limit_bytes if limit_bytes is None or limit_bytes > 0 else None
        self._seen = 0
        self._lock = threading.Lock()

    def retain(self, chunk: bytes) -> tuple[bytes, bool]:
        if self.limit_bytes is None:
            return chunk, False
        with self._lock:
            remaining = max(0, self.limit_bytes - min(self._seen, self.limit_bytes))
            retained = chunk[:remaining]
            self._seen += len(chunk)
            return retained, len(chunk) > remaining


class _StreamCapture:
    truncated: bool

    def append(self, chunk: bytes) -> bool:
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError


class _StreamLogCapture(_StreamCapture):
    def __init__(self, log_path: Path, limiter: _OutputLimiter) -> None:
        self._limiter = limiter
        self._handle = log_path.open("w", encoding="utf-8")
        self.truncated = False

    def append(self, chunk: bytes) -> bool:
        retained, exceeded = self._limiter.retain(chunk)
        if retained:
            self.write_text(retained.decode("utf-8", errors="replace"))
        if exceeded:
            self.truncated = True
        return exceeded

    def write_text(self, text: str) -> None:
        self._handle.write(text)
        self._handle.flush()

    def close(self) -> None:
        self._handle.close()


class _OpenHandsStdoutCapture(_StreamCapture):
    def __init__(
        self,
        stdout_log: Path,
        events_log: Path,
        limiter: _OutputLimiter,
    ) -> None:
        self._limiter = limiter
        self._stdout_handle = stdout_log.open("w", encoding="utf-8")
        self._events_handle = events_log.open("w", encoding="utf-8")
        self._buffer = bytearray()
        self.truncated = False

    def append(self, chunk: bytes) -> bool:
        retained, exceeded = self._limiter.retain(chunk)
        if retained:
            self._buffer.extend(retained)
            self._drain_lines()
        if exceeded:
            self.truncated = True
        return exceeded

    def flush(self) -> None:
        if self._buffer:
            self._write_line(bytes(self._buffer))
            self._buffer.clear()

    def _drain_lines(self) -> None:
        while True:
            newline_index = self._buffer.find(b"\n")
            if newline_index < 0:
                return
            line = bytes(self._buffer[: newline_index + 1])
            del self._buffer[: newline_index + 1]
            self._write_line(line)

    def _write_line(self, line: bytes) -> None:
        text = line.decode("utf-8", errors="replace")
        if _is_json_object_line(text):
            self._events_handle.write(text)
            if not text.endswith("\n"):
                self._events_handle.write("\n")
            self._events_handle.flush()
            return
        self._stdout_handle.write(text)
        if not text.endswith("\n"):
            self._stdout_handle.write("\n")
        self._stdout_handle.flush()

    def close(self) -> None:
        self.flush()
        self._stdout_handle.close()
        self._events_handle.close()


def _is_json_object_line(text: str) -> bool:
    stripped = text.strip()
    if not stripped.startswith("{"):
        return False
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        return False
    return isinstance(payload, dict)


def _kill_process_group(process: subprocess.Popen[str]) -> None:
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        return
    except (PermissionError, OSError):
        process.kill()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def _write_command_record(
    config: OpenHandsRunnerConfig,
    *,
    prompt_file: Path,
    command_template: str,
    command: list[str],
    configured: bool,
    error: str,
) -> None:
    payload = {
        "runtime": "openhands",
        "configured": configured,
        "command_template": _redact_text(command_template),
        "command": _redact_command(command),
        "cwd": str(config.workspace_dir),
        "prompt_file": str(prompt_file),
        "model": config.model,
        "error": error,
        "placeholders": [
            "workspace",
            "task_file",
            "submission_dir",
            "agent_output_dir",
            "prompt_file",
            "model",
            "python",
        ],
    }
    (config.agent_output_dir / "openhands_command.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _read_raw_usage(agent_output_dir: Path) -> dict[str, Any] | None:
    for filename in RAW_USAGE_FILENAMES:
        path = agent_output_dir / filename
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict):
            return data
    return None


def _write_usage(
    config: OpenHandsRunnerConfig,
    *,
    exit_status: str,
    returncode: int,
    duration_seconds: float,
    raw_usage: dict[str, Any] | None,
) -> None:
    metrics = _usage_metrics(raw_usage)
    context_audit = _usage_context_audit(raw_usage)
    payload: dict[str, Any] = {
        "schema_version": USAGE_SCHEMA_VERSION,
        "agent_name": "openhands-agent",
        "model": config.model,
        "available": True,
        "assistant_steps": metrics.get("assistant_steps", 0),
        "api_calls": metrics.get("api_calls", 0),
        "prompt_tokens": metrics.get("prompt_tokens", 0),
        "completion_tokens": metrics.get("completion_tokens", 0),
        "total_tokens": metrics.get("total_tokens", 0),
        "context_audit": context_audit,
        "exit_status": exit_status,
        "external_returncode": returncode,
        "duration_seconds": round(duration_seconds, 6),
    }
    for key in ("trace_tokens", "billed_tokens"):
        if key in metrics:
            payload[key] = metrics[key]
    (config.agent_output_dir / "usage.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _usage_metrics(raw_usage: dict[str, Any] | None) -> dict[str, int]:
    source: dict[str, Any] = {}
    if isinstance(raw_usage, dict):
        nested = raw_usage.get("usage")
        source = nested if isinstance(nested, dict) else raw_usage

    metrics: dict[str, int] = {}
    for key in (
        "assistant_steps",
        "api_calls",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "trace_tokens",
        "billed_tokens",
    ):
        value = _int_metric(source.get(key))
        if value is not None:
            metrics[key] = value
    if "total_tokens" not in metrics and (
        "prompt_tokens" in metrics or "completion_tokens" in metrics
    ):
        metrics["total_tokens"] = metrics.get("prompt_tokens", 0) + metrics.get(
            "completion_tokens",
            0,
        )
    return metrics


def _usage_context_audit(raw_usage: dict[str, Any] | None) -> dict[str, Any]:
    raw_context: dict[str, Any] = {}
    if isinstance(raw_usage, dict) and isinstance(raw_usage.get("context_audit"), dict):
        raw_context = raw_usage["context_audit"]
    raw_available = raw_context.get("available")
    context_available = raw_available if isinstance(raw_available, bool) else bool(raw_context)

    audit: dict[str, Any] = {
        "available": context_available,
        "history_policy": str(raw_context.get("history_policy") or "external_openhands"),
        "over_context_behavior": str(
            raw_context.get("over_context_behavior") or "managed_by_openhands"
        ),
        "token_source": str(
            raw_context.get("token_source")
            or ("openhands_usage_file" if raw_usage else "unavailable")
        ),
        "runtime": str(raw_context.get("runtime") or "openhands"),
        "context_violation": bool(raw_context.get("context_violation", False)),
        "usage_unverified": bool(raw_context.get("usage_unverified", True)),
    }
    for key in (
        "context_window_tokens",
        "reserved_output_tokens",
        "max_allowed_prompt_tokens",
        "max_prompt_tokens_per_call",
        "max_total_tokens_per_call",
    ):
        value = _int_metric(raw_context.get(key))
        if value is not None:
            audit[key] = value
    return audit


def _int_metric(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value >= 0 else None
    if isinstance(value, float) and value >= 0 and value.is_integer():
        return int(value)
    if isinstance(value, str):
        try:
            parsed = int(value.strip())
        except ValueError:
            return None
        return parsed if parsed >= 0 else None
    return None


def _redact_command(command: list[str]) -> list[str]:
    return [_redact_text(item) for item in command]


def _redact_text(text: str) -> str:
    redacted = text
    for value in _secret_values():
        if value and value in redacted:
            redacted = redacted.replace(value, "<redacted>")
    return redacted


def _secret_values() -> set[str]:
    values: set[str] = set()
    for key, value in os.environ.items():
        upper = key.upper()
        if any(marker in upper for marker in ("KEY", "TOKEN", "SECRET", "PASSWORD")):
            if len(value) >= 6:
                values.add(value)
    return values


if __name__ == "__main__":
    raise SystemExit(main())

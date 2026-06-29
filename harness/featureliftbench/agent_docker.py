"""Run FeatureLiftBench agents inside short-lived Docker containers."""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import dataclass
from dataclasses import replace
from pathlib import Path

from .agent_adapters import AgentCommandResult
from .agent_adapters import AgentRunConfig
from .agent_adapters import AgentRunContext
from .agent_adapters import get_agent_adapter
from .paths import HARNESS_ROOT
from .resource_limits import command_output_limit_bytes
from .resource_limits import detect_resource_limited

DEFAULT_AGENT_IMAGE = "featureliftbench-agent:latest"
DEFAULT_AGENT_DOCKER_MEMORY = "8g"
DEFAULT_AGENT_DOCKER_CPUS = "2"
DEFAULT_AGENT_DOCKER_PIDS = "512"
DEFAULT_AGENT_DOCKER_NETWORK = "bridge"
DEFAULT_AGENT_DOCKER_TMPFS = "/tmp:rw,nosuid,nodev,size=2g"

CONTAINER_WORKSPACE = Path("/flb/workspace")
CONTAINER_AGENT_OUTPUT = Path("/flb/agent")
CONTAINER_HARNESS = Path("/flb/harness")


@dataclass(frozen=True)
class AgentDockerInvocation:
    command: list[str]
    report_command: list[str]
    env: dict[str, str]
    container_name: str


def run_agent_in_docker(
    context: AgentRunContext,
    config: AgentRunConfig,
    *,
    image: str = DEFAULT_AGENT_IMAGE,
    stdout_log: Path | None = None,
    stderr_log: Path | None = None,
) -> AgentCommandResult:
    invocation = build_agent_docker_invocation(context, config, image=image)
    start = time.monotonic()
    redact_values = _redaction_values(config.env)
    output_limit = command_output_limit_bytes(invocation.env)
    stdout_capture = _BoundedRedactedLog(stdout_log, output_limit, redact_values)
    stderr_capture = _BoundedRedactedLog(stderr_log, output_limit, redact_values)
    process: subprocess.Popen[bytes] | None = None
    log_limit_event = threading.Event()
    try:
        process = subprocess.Popen(
            invocation.command,
            env=invocation.env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        stderr_text = _redact_text(str(exc), redact_values)
        stderr_capture.write_text(stderr_text)
        return AgentCommandResult(
            name=f"{config.agent}-docker",
            command=invocation.command,
            report_command=invocation.report_command,
            returncode=127,
            duration_seconds=time.monotonic() - start,
            stdout="",
            stderr=stderr_text,
            reason="docker executable not found",
        )
    finally:
        if process is None:
            stdout_capture.close()
            stderr_capture.close()

    assert process is not None
    threads = [
        threading.Thread(
            target=_pump_stream,
            args=(process.stdout, stdout_capture, log_limit_event),
            daemon=True,
        ),
        threading.Thread(
            target=_pump_stream,
            args=(process.stderr, stderr_capture, log_limit_event),
            daemon=True,
        ),
    ]
    for thread in threads:
        thread.start()

    timed_out = False
    deadline = start + max(1, int(config.timeout_seconds))
    while process.poll() is None:
        if log_limit_event.is_set():
            _kill_container(invocation.container_name)
            _wait_or_kill_process(process)
            break
        if time.monotonic() >= deadline:
            timed_out = True
            _kill_container(invocation.container_name)
            _wait_or_kill_process(process)
            break
        time.sleep(0.05)

    for thread in threads:
        thread.join(timeout=2)
    stdout = stdout_capture.text()
    stderr = stderr_capture.text()
    if timed_out and not stderr:
        stderr = f"agent docker timed out after {config.timeout_seconds}s"
        stderr_capture.write_text(stderr)
    stdout_capture.close()
    stderr_capture.close()
    returncode = 124 if timed_out else int(process.returncode or 0)
    log_limit_exceeded = log_limit_event.is_set()
    resource_limited = (
        False
        if log_limit_exceeded
        else detect_resource_limited(returncode=returncode, stderr=stderr)
    )
    reason = _result_reason(
        returncode=returncode,
        timed_out=timed_out,
        log_limit_exceeded=log_limit_exceeded,
        resource_limited=resource_limited,
        timeout_seconds=config.timeout_seconds,
    )
    return AgentCommandResult(
        name=f"{config.agent}-docker",
        command=invocation.command,
        report_command=invocation.report_command,
        returncode=returncode,
        duration_seconds=time.monotonic() - start,
        stdout=stdout,
        stderr=stderr,
        timed_out=timed_out,
        reason=reason,
        resource_limited=resource_limited,
        stdout_truncated=stdout_capture.truncated,
        stderr_truncated=stderr_capture.truncated,
        log_limit_exceeded=log_limit_exceeded,
    )


def build_agent_docker_invocation(
    context: AgentRunContext,
    config: AgentRunConfig,
    *,
    image: str = DEFAULT_AGENT_IMAGE,
) -> AgentDockerInvocation:
    container_name = _container_name()
    container_context = AgentRunContext(
        workspace_dir=CONTAINER_WORKSPACE,
        task_file=CONTAINER_WORKSPACE / "TASK.md",
        submission_dir=CONTAINER_WORKSPACE / "submission",
        agent_output_dir=CONTAINER_AGENT_OUTPUT,
        task_text=context.task_text,
    )
    container_config = _container_config(config)
    adapter = get_agent_adapter(config.agent)
    inner_command = _normalize_inner_command(adapter.build_command(container_context, container_config))
    report_inner_command = _normalize_inner_command(
        adapter.build_report_command(container_context, container_config)
    )
    env_keys, process_env = _docker_env(config)

    command = [
        "docker",
        "run",
        "--rm",
        "--name",
        container_name,
        "--network",
        _env_default("FEATURELIFTBENCH_AGENT_DOCKER_NETWORK", DEFAULT_AGENT_DOCKER_NETWORK),
        "--memory",
        _env_default("FEATURELIFTBENCH_AGENT_DOCKER_MEMORY", DEFAULT_AGENT_DOCKER_MEMORY),
        "--cpus",
        _env_default("FEATURELIFTBENCH_AGENT_DOCKER_CPUS", DEFAULT_AGENT_DOCKER_CPUS),
        "--pids-limit",
        _env_default("FEATURELIFTBENCH_AGENT_DOCKER_PIDS", DEFAULT_AGENT_DOCKER_PIDS),
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "--tmpfs",
        _env_default("FEATURELIFTBENCH_AGENT_DOCKER_TMPFS", DEFAULT_AGENT_DOCKER_TMPFS),
        "--user",
        _uid_gid(),
        "-w",
        str(CONTAINER_WORKSPACE),
        "-v",
        f"{context.workspace_dir.resolve()}:{CONTAINER_WORKSPACE}:rw",
        "-v",
        f"{context.agent_output_dir.resolve()}:{CONTAINER_AGENT_OUTPUT}:rw",
        "-v",
        f"{HARNESS_ROOT.resolve()}:{CONTAINER_HARNESS}:ro",
    ]
    for key in sorted(env_keys):
        command.extend(["--env", key])
    command.extend([image, *inner_command])

    report_command = list(command[: len(command) - len(inner_command)])
    report_command.extend(report_inner_command)
    return AgentDockerInvocation(
        command=command,
        report_command=report_command,
        env=process_env,
        container_name=container_name,
    )


def _container_config(config: AgentRunConfig) -> AgentRunConfig:
    if config.agent.strip().lower().replace("_", "-") in {"mini", "mini-swe-agent", "minisweagent"}:
        return replace(config, agent_bin="mini")
    return config


def _normalize_inner_command(command: list[str]) -> list[str]:
    if len(command) >= 3 and command[0] == sys.executable and command[1:3] == [
        "-m",
        "featureliftbench.mini_live_runner",
    ]:
        return ["python", *command[1:]]
    return command


def _docker_env(config: AgentRunConfig) -> tuple[set[str], dict[str, str]]:
    process_env = os.environ.copy()
    env_keys: set[str] = set()
    if config.env:
        for key, value in config.env.items():
            process_env[key] = value
            env_keys.add(key)

    fixed_env = {
        "FEATURELIFTBENCH_WORKSPACE": str(CONTAINER_WORKSPACE),
        "FEATURELIFTBENCH_TASK_FILE": str(CONTAINER_WORKSPACE / "TASK.md"),
        "FEATURELIFTBENCH_SUBMISSION_DIR": str(CONTAINER_WORKSPACE / "submission"),
        "FEATURELIFTBENCH_AGENT_OUTPUT_DIR": str(CONTAINER_AGENT_OUTPUT),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONPATH": str(CONTAINER_HARNESS),
        "HOME": "/tmp/flb-home",
    }
    for key, value in fixed_env.items():
        process_env[key] = value
        env_keys.add(key)
    return env_keys, process_env


def _kill_container(container_name: str) -> None:
    subprocess.run(
        ["docker", "kill", container_name],
        capture_output=True,
        text=True,
        check=False,
    )


def _pump_stream(
    stream: object,
    capture: "_BoundedRedactedLog",
    log_limit_event: threading.Event,
) -> None:
    if stream is None:
        return
    try:
        while True:
            chunk = stream.read(65536)  # type: ignore[attr-defined]
            if not chunk:
                return
            if capture.append(chunk) and not log_limit_event.is_set():
                log_limit_event.set()
                return
    finally:
        stream.close()  # type: ignore[attr-defined]


def _wait_or_kill_process(process: subprocess.Popen[bytes]) -> None:
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass


def _result_reason(
    *,
    returncode: int,
    timed_out: bool,
    log_limit_exceeded: bool,
    resource_limited: bool,
    timeout_seconds: int,
) -> str:
    if log_limit_exceeded:
        return "agent docker output exceeded log limit"
    if timed_out:
        return f"agent docker timed out after {timeout_seconds}s"
    if resource_limited:
        return "agent docker exceeded container resource limits"
    if returncode != 0:
        return f"agent docker exited with return code {returncode}"
    return ""


class _BoundedRedactedLog:
    def __init__(
        self,
        path: Path | None,
        limit_bytes: int | None,
        redact_values: tuple[str, ...],
    ) -> None:
        self.path = path
        self.limit_bytes = limit_bytes if limit_bytes is None or limit_bytes > 0 else None
        self.redact_values = redact_values
        self._raw_bytes = 0
        self._parts: list[str] = []
        self.truncated = False
        self._lock = threading.Lock()
        self._handle = None
        if path is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
            self._handle = path.open("w", encoding="utf-8")

    def append(self, chunk: bytes) -> bool:
        with self._lock:
            if self.limit_bytes is None:
                retained = chunk
                exceeded = False
            else:
                remaining = max(0, self.limit_bytes - self._raw_bytes)
                retained = chunk[:remaining]
                self._raw_bytes += len(retained)
                exceeded = len(chunk) > remaining
                if exceeded:
                    self.truncated = True
            if retained:
                self._write_text_locked(
                    _redact_text(retained.decode("utf-8", errors="replace"), self.redact_values)
                )
            return exceeded

    def write_text(self, text: str) -> None:
        with self._lock:
            self._write_text_locked(_redact_text(text, self.redact_values))

    def _write_text_locked(self, text: str) -> None:
        self._parts.append(text)
        if self._handle is not None:
            self._handle.write(text)
            self._handle.flush()

    def text(self) -> str:
        with self._lock:
            return "".join(self._parts)

    def close(self) -> None:
        with self._lock:
            if self._handle is not None:
                self._handle.close()
                self._handle = None


def _redaction_values(env: dict[str, str] | None) -> tuple[str, ...]:
    if not env:
        return ()
    values = []
    secret_markers = ("KEY", "TOKEN", "SECRET", "PASSWORD", "CREDENTIAL", "AUTH")
    for key, value in env.items():
        if not isinstance(value, str) or len(value) < 4:
            continue
        upper_key = key.upper()
        if any(marker in upper_key for marker in secret_markers):
            values.append(value)
    return tuple(sorted(set(values), key=len, reverse=True))


def _redact_text(text: str, redact_values: tuple[str, ...]) -> str:
    redacted = text
    for value in redact_values:
        redacted = redacted.replace(value, "[REDACTED]")
    return redacted


def _container_name() -> str:
    return f"flb-agent-{os.getpid()}-{uuid.uuid4().hex[:12]}"


def _env_default(name: str, default: str) -> str:
    value = os.environ.get(name, "").strip()
    return value or default


def _uid_gid() -> str:
    if hasattr(os, "getuid") and hasattr(os, "getgid"):
        return f"{os.getuid()}:{os.getgid()}"
    return "1000:1000"

"""Agent adapter implementations for FeatureLiftBench runs."""

from __future__ import annotations

import os
import shlex
import signal
import subprocess
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .active_agent_processes import register_process
from .active_agent_processes import terminate_active_agent_processes
from .active_agent_processes import unregister_process


@dataclass(frozen=True)
class AgentRunContext:
    """Paths and prompt content passed to an agent adapter."""

    workspace_dir: Path
    task_file: Path
    submission_dir: Path
    agent_output_dir: Path
    task_text: str


@dataclass(frozen=True)
class AgentRunConfig:
    """User-configurable options for running an agent."""

    agent: str = "mini-swe-agent"
    agent_bin: str | None = None
    model: str | None = None
    config: str | None = None
    yolo: bool = False
    timeout_seconds: int = 3600
    command: str | None = None
    extra_args: tuple[str, ...] = ()
    env: dict[str, str] | None = None
    profile: str = ""


@dataclass(frozen=True)
class AgentCommandResult:
    """Captured result from an agent subprocess."""

    name: str
    command: list[str]
    report_command: list[str]
    returncode: int
    duration_seconds: float
    stdout: str
    stderr: str
    timed_out: bool = False
    reason: str = ""

    @property
    def passed(self) -> bool:
        return self.returncode == 0 and not self.timed_out

    def payload(self, *, stdout_log: Path | None = None, stderr_log: Path | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "command": self.report_command,
            "returncode": self.returncode,
            "passed": self.passed,
            "duration_seconds": round(self.duration_seconds, 6),
            "timed_out": self.timed_out,
            "reason": self.reason,
        }
        if stdout_log is not None:
            payload["stdout_log"] = str(stdout_log)
        if stderr_log is not None:
            payload["stderr_log"] = str(stderr_log)
        return payload


class AgentAdapter:
    """Base class for an agent command adapter."""

    name = "agent"

    def build_command(self, context: AgentRunContext, config: AgentRunConfig) -> list[str]:
        raise NotImplementedError

    def build_report_command(self, context: AgentRunContext, config: AgentRunConfig) -> list[str]:
        return self.build_command(context, config)

    def run(
        self,
        context: AgentRunContext,
        config: AgentRunConfig,
        *,
        stdout_log: Path | None = None,
        stderr_log: Path | None = None,
    ) -> AgentCommandResult:
        command = self.build_command(context, config)
        report_command = self.build_report_command(context, config)
        env = os.environ.copy()
        if config.env:
            env.update(config.env)
        env.update(
            {
                "FEATURELIFTBENCH_WORKSPACE": str(context.workspace_dir),
                "FEATURELIFTBENCH_TASK_FILE": str(context.task_file),
                "FEATURELIFTBENCH_SUBMISSION_DIR": str(context.submission_dir),
                "FEATURELIFTBENCH_AGENT_OUTPUT_DIR": str(context.agent_output_dir),
                "PYTHONDONTWRITEBYTECODE": "1",
            }
        )

        start = time.monotonic()
        try:
            if stdout_log is not None or stderr_log is not None:
                return self._run_streaming(
                    command=command,
                    report_command=report_command,
                    cwd=context.workspace_dir,
                    env=env,
                    timeout_seconds=config.timeout_seconds,
                    start=start,
                    stdout_log=stdout_log,
                    stderr_log=stderr_log,
                )
            completed = subprocess.run(
                command,
                cwd=context.workspace_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=config.timeout_seconds,
                check=False,
            )
        except FileNotFoundError as exc:
            return AgentCommandResult(
                name=self.name,
                command=command,
                report_command=report_command,
                returncode=127,
                duration_seconds=time.monotonic() - start,
                stdout="",
                stderr=str(exc),
                reason=f"agent executable not found: {command[0]}",
            )
        except subprocess.TimeoutExpired as exc:
            return AgentCommandResult(
                name=self.name,
                command=command,
                report_command=report_command,
                returncode=124,
                duration_seconds=time.monotonic() - start,
                stdout=exc.stdout or "",
                stderr=exc.stderr or f"agent timed out after {config.timeout_seconds}s",
                timed_out=True,
                reason=f"agent timed out after {config.timeout_seconds}s",
            )

        return AgentCommandResult(
            name=self.name,
            command=command,
            report_command=report_command,
            returncode=completed.returncode,
            duration_seconds=time.monotonic() - start,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

    def _run_streaming(
        self,
        *,
        command: list[str],
        report_command: list[str],
        cwd: Path,
        env: dict[str, str],
        timeout_seconds: int,
        start: float,
        stdout_log: Path | None,
        stderr_log: Path | None,
    ) -> AgentCommandResult:
        if stdout_log is not None:
            stdout_log.parent.mkdir(parents=True, exist_ok=True)
        if stderr_log is not None:
            stderr_log.parent.mkdir(parents=True, exist_ok=True)

        stdout_chunks: list[str] = []
        stderr_chunks: list[str] = []
        process: subprocess.Popen[str] | None = None
        try:
            process = subprocess.Popen(
                command,
                cwd=cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                start_new_session=True,
            )
            register_process(process)
        except FileNotFoundError as exc:
            return AgentCommandResult(
                name=self.name,
                command=command,
                report_command=report_command,
                returncode=127,
                duration_seconds=time.monotonic() - start,
                stdout="",
                stderr=str(exc),
                reason=f"agent executable not found: {command[0]}",
            )

        def pump(stream, log_path: Path | None, chunks: list[str]) -> None:
            assert stream is not None
            log_handle = log_path.open("w", encoding="utf-8") if log_path is not None else None
            try:
                for line in iter(stream.readline, ""):
                    chunks.append(line)
                    if log_handle is not None:
                        log_handle.write(line)
                        log_handle.flush()
            finally:
                if log_handle is not None:
                    log_handle.close()
                stream.close()

        threads = []
        if process.stdout is not None:
            threads.append(
                threading.Thread(
                    target=pump,
                    args=(process.stdout, stdout_log, stdout_chunks),
                    daemon=True,
                )
            )
        if process.stderr is not None:
            threads.append(
                threading.Thread(
                    target=pump,
                    args=(process.stderr, stderr_log, stderr_chunks),
                    daemon=True,
                )
            )
        for thread in threads:
            thread.start()

        try:
            try:
                returncode = process.wait(timeout=timeout_seconds)
            except subprocess.TimeoutExpired:
                _kill_process_group(process)
                process.wait(timeout=5)
                for thread in threads:
                    thread.join(timeout=1)
                return AgentCommandResult(
                    name=self.name,
                    command=command,
                    report_command=report_command,
                    returncode=124,
                    duration_seconds=time.monotonic() - start,
                    stdout="".join(stdout_chunks),
                    stderr="".join(stderr_chunks) or f"agent timed out after {timeout_seconds}s",
                    timed_out=True,
                    reason=f"agent timed out after {timeout_seconds}s",
                )

            for thread in threads:
                thread.join()
            return AgentCommandResult(
                name=self.name,
                command=command,
                report_command=report_command,
                returncode=returncode,
                duration_seconds=time.monotonic() - start,
                stdout="".join(stdout_chunks),
                stderr="".join(stderr_chunks),
            )
        finally:
            unregister_process(process)


def _kill_process_group(process: subprocess.Popen[str]) -> None:
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        return
    except (PermissionError, OSError):
        process.kill()


class MiniSweAgentAdapter(AgentAdapter):
    """Adapter for the ``mini`` CLI from SWE-agent/mini-swe-agent."""

    name = "mini-swe-agent"

    def build_command(self, context: AgentRunContext, config: AgentRunConfig) -> list[str]:
        agent_bin = config.agent_bin or "mini"
        trajectory_path = context.agent_output_dir / "trajectory.json"
        command = [
            agent_bin,
            "--task",
            context.task_text,
            "--output",
            str(trajectory_path),
            "--exit-immediately",
        ]
        if config.model:
            command.extend(["--model", config.model])
        if config.config:
            command.extend(["--config", config.config])
        if config.yolo:
            command.append("--yolo")
        command.extend(config.extra_args)
        return command

    def build_report_command(self, context: AgentRunContext, config: AgentRunConfig) -> list[str]:
        command = self.build_command(context, config)
        return ["@TASK.md" if item == context.task_text else item for item in command]


class CommandAgentAdapter(AgentAdapter):
    """Adapter for a user-provided command template."""

    name = "command"

    def build_command(self, context: AgentRunContext, config: AgentRunConfig) -> list[str]:
        if not config.command:
            raise ValueError("--agent-command is required when --agent command is used")
        rendered = config.command.format(
            workspace=context.workspace_dir,
            task_file=context.task_file,
            submission_dir=context.submission_dir,
            agent_output_dir=context.agent_output_dir,
        )
        command = shlex.split(rendered)
        command.extend(config.extra_args)
        return command


def get_agent_adapter(name: str) -> AgentAdapter:
    """Return an adapter for a supported agent name."""

    normalized = name.strip().lower().replace("_", "-")
    if normalized in {"mini", "mini-swe-agent", "minisweagent"}:
        return MiniSweAgentAdapter()
    if normalized in {"command", "custom"}:
        return CommandAgentAdapter()
    raise ValueError(f"unsupported agent: {name}")


SUPPORTED_AGENTS = ("mini-swe-agent", "command")

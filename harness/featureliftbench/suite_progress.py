"""Rich progress UI for FeatureLiftBench suite runs."""

from __future__ import annotations

import collections
import contextlib
import json
import re
import threading
import time
from datetime import timedelta
from pathlib import Path
from typing import Any
from typing import Iterator
from typing import Literal

from rich.console import Group
from rich.live import Live
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

_MINI_STEP_TOKEN_RE = re.compile(
    r"mini-swe-agent \(step (\d+), (\d+) tokens\)",
    re.IGNORECASE,
)
_MINI_STEP_COST_RE = re.compile(
    r"mini-swe-agent \(step (\d+), \$[\d.]+\)",
    re.IGNORECASE,
)
_MINI_STEP_ONLY_RE = re.compile(
    r"mini-swe-agent \(step (\d+)[,\)]",
    re.IGNORECASE,
)
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
_RICH_TAG_RE = re.compile(r"\[[/\w]+\]")


def _shorten_str(value: str, max_len: int, *, shorten_left: bool = False) -> str:
    if not shorten_left:
        text = value[: max_len - 3] + "..." if len(value) > max_len else value
    else:
        text = "..." + value[-max_len + 3 :] if len(value) > max_len else value
    return f"{text:<{max_len}}"


def _strip_ansi(value: str) -> str:
    return _ANSI_RE.sub("", value)


def _normalize_log_text(value: str) -> str:
    return _RICH_TAG_RE.sub("", _strip_ansi(value))


def _is_noise_log_line(line: str) -> bool:
    cleaned = line.strip()
    if not cleaned:
        return True
    if cleaned.startswith("─") or cleaned.startswith("="):
        return True
    if cleaned in {"User:", "System:", "Assistant:"}:
        return True
    return False


def parse_mini_progress_from_log(path: Path) -> str | None:
    """Extract the latest mini-swe-agent step/token status from agent stdout."""

    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    normalized = _normalize_log_text(text)
    token_matches = list(_MINI_STEP_TOKEN_RE.finditer(normalized))
    if token_matches:
        last = token_matches[-1]
        return f"Step {last.group(1)} ({last.group(2)} toks)"

    cost_matches = list(_MINI_STEP_COST_RE.finditer(normalized))
    if cost_matches:
        last = cost_matches[-1]
        return f"Step {last.group(1)}"

    step_matches = list(_MINI_STEP_ONLY_RE.finditer(normalized))
    if step_matches:
        return f"Step {step_matches[-1].group(1)}"

    for line in reversed(text.splitlines()):
        cleaned = _normalize_log_text(line).strip()
        if _is_noise_log_line(cleaned):
            continue
        return _shorten_str(cleaned, 30)
    return None


def _int_metric(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _format_token_count(value: int) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 10_000:
        return f"{value // 1000}k"
    return f"{value:,}"


def parse_mini_token_total_from_trajectory(path: Path) -> int | None:
    """Sum prompt/completion tokens from mini trajectory message usage."""

    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None

    prompt_tokens = 0
    completion_tokens = 0
    saw_usage = False
    for message in data.get("messages") or []:
        if not isinstance(message, dict):
            continue
        extra = message.get("extra")
        if not isinstance(extra, dict):
            continue
        response = extra.get("response")
        if not isinstance(response, dict):
            continue
        usage = response.get("usage")
        if not isinstance(usage, dict):
            continue

        prompt = _int_metric(usage.get("prompt_tokens"))
        completion = _int_metric(usage.get("completion_tokens"))
        if prompt is not None:
            prompt_tokens += prompt
            saw_usage = True
        if completion is not None:
            completion_tokens += completion
            saw_usage = True

    if not saw_usage:
        return None
    return prompt_tokens + completion_tokens


def parse_mini_step_from_trajectory(path: Path) -> str | None:
    """Return Step N from assistant message count in a live trajectory snapshot."""

    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None

    assistant_steps = 0
    for message in data.get("messages") or []:
        if isinstance(message, dict) and message.get("role") == "assistant":
            assistant_steps += 1
    if assistant_steps <= 0:
        return None
    return f"Step {assistant_steps}"


def resolve_agent_log_dir(
    output_dir: Path,
    task_id: str,
    *,
    layout: Literal["suite", "flat"] = "suite",
) -> Path:
    if layout == "flat":
        return output_dir / "agent"
    return output_dir / task_id / "agent"


def poll_agent_task_status(agent_dir: Path) -> tuple[str | None, int | None]:
    """Resolve step text and token totals from stdout.log with trajectory fallback."""

    step_status = parse_mini_progress_from_log(agent_dir / "stdout.log")
    trajectory_path = agent_dir / "trajectory.json"
    if step_status is None:
        step_status = parse_mini_step_from_trajectory(trajectory_path)
    tokens = parse_mini_token_total_from_trajectory(trajectory_path)
    if tokens is None and step_status is not None:
        match = re.search(r"\((\d+) toks\)", step_status)
        if match:
            tokens = int(match.group(1))
    if step_status is None and tokens is None:
        return None, None
    if step_status is None:
        step_status = "running"
    status, tokens = format_mini_task_status(step_status=step_status, tokens=tokens)
    return status, tokens


def format_mini_task_status(*, step_status: str, tokens: int | None) -> tuple[str, int | None]:
    """Combine step text from stdout with token totals from trajectory."""

    if tokens is None:
        return step_status, None
    token_text = _format_token_count(tokens)
    if re.search(r"\(\d+ toks\)", step_status):
        return step_status, tokens
    if step_status.startswith("Step "):
        return f"{step_status} ({token_text} toks)", tokens
    return f"{step_status} ({token_text} toks)", tokens


class SuiteBatchProgressManager:
    """Manage overall and per-task progress for a FeatureLiftBench suite run."""

    def __init__(
        self,
        num_tasks: int,
        *,
        layout: Literal["suite", "flat"] = "suite",
    ) -> None:
        self._layout = layout
        self._lock = threading.Lock()
        self._start_time = time.time()
        self._total_tasks = num_tasks
        self._spinner_tasks: dict[str, TaskID] = {}
        self._active_tasks: set[str] = set()
        self._task_tokens: dict[str, int] = {}
        self._instances_by_exit_status: dict[str | None, list[str]] = collections.defaultdict(list)

        self._main_progress_bar = Progress(
            SpinnerColumn(spinner_name="dots2"),
            TextColumn("[progress.description]{task.description} ({task.fields[total_tokens]} toks)"),
            BarColumn(),
            MofNCompleteColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TextColumn("[cyan]{task.fields[eta]}[/cyan]"),
            speed_estimate_period=60 * 5,
        )
        self._task_progress_bar = Progress(
            SpinnerColumn(spinner_name="dots2"),
            TextColumn("{task.fields[label]}"),
            TextColumn("{task.fields[status]}"),
            TimeElapsedColumn(),
        )
        self._main_task_id = self._main_progress_bar.add_task(
            "[cyan]Overall Progress",
            total=num_tasks,
            total_tokens="0",
            eta="",
        )
        self.render_group = Group(self._main_progress_bar, Table(), self._task_progress_bar)

    @property
    def n_completed(self) -> int:
        return sum(len(items) for items in self._instances_by_exit_status.values())

    def active_task_ids(self) -> list[str]:
        with self._lock:
            return sorted(self._active_tasks)

    def _get_eta_text(self) -> str:
        completed = self.n_completed
        if completed <= 0:
            return ""
        try:
            elapsed = time.time() - self._start_time
            remaining = elapsed / completed * (self._total_tasks - completed)
            return f"eta: {timedelta(seconds=int(remaining))}"
        except ZeroDivisionError:
            return ""

    def _total_tokens_text(self) -> str:
        with self._lock:
            total = sum(self._task_tokens.values())
            if total <= 0:
                return "0"
            return _format_token_count(total)

    def _update_main_bar(self) -> None:
        self._main_progress_bar.update(
            self._main_task_id,
            total_tokens=self._total_tokens_text(),
            eta=self._get_eta_text(),
        )

    def update_exit_status_table(self) -> None:
        table = Table()
        table.add_column("Exit Status")
        table.add_column("Count", justify="right", style="bold cyan")
        table.add_column("Most recent tasks")
        with self._lock:
            sorted_items = sorted(
                self._instances_by_exit_status.items(),
                key=lambda item: len(item[1]),
                reverse=True,
            )
            for status, tasks in sorted_items:
                label = status or "unknown"
                recent = _shorten_str(", ".join(reversed(tasks)), 55)
                table.add_row(label, str(len(tasks)), recent)
        self.render_group.renderables[1] = table

    def on_task_start(self, task_id: str) -> None:
        with self._lock:
            self._active_tasks.add(task_id)
            self._spinner_tasks[task_id] = self._task_progress_bar.add_task(
                description=f"Task {task_id}",
                status="starting",
                total=None,
                label=_shorten_str(task_id, 25, shorten_left=True),
            )
        self._update_main_bar()

    def update_task_status(self, task_id: str, message: str, *, tokens: int | None = None) -> None:
        with self._lock:
            spinner_id = self._spinner_tasks.get(task_id)
            if spinner_id is None:
                return
            if tokens is not None:
                self._task_tokens[task_id] = tokens
            self._task_progress_bar.update(
                spinner_id,
                status=_shorten_str(message, 30),
                label=_shorten_str(task_id, 25, shorten_left=True),
            )
        self._update_main_bar()

    def on_task_end(self, task_id: str, exit_status: str | None) -> None:
        with self._lock:
            self._active_tasks.discard(task_id)
            self._task_tokens.pop(task_id, None)
            try:
                self._task_progress_bar.remove_task(self._spinner_tasks.pop(task_id))
            except KeyError:
                pass
            self._instances_by_exit_status[exit_status].append(task_id)
            self._main_progress_bar.update(self._main_task_id, advance=1, eta=self._get_eta_text())
        self.update_exit_status_table()
        self._update_main_bar()

    def poll_task_logs(self, output_dir: Path) -> None:
        for task_id in self.active_task_ids():
            agent_dir = resolve_agent_log_dir(output_dir, task_id, layout=self._layout)
            status, tokens = poll_agent_task_status(agent_dir)
            if status is None:
                continue
            self.update_task_status(task_id, status, tokens=tokens)


@contextlib.contextmanager
def live_suite_progress(
    *,
    num_tasks: int,
    output_dir: Path,
    refresh_per_second: float = 4.0,
    layout: Literal["suite", "flat"] = "suite",
) -> Iterator[SuiteBatchProgressManager]:
    """Render suite progress with Rich Live and poll running agent logs."""

    manager = SuiteBatchProgressManager(num_tasks, layout=layout)
    stop_event = threading.Event()

    def poll_loop() -> None:
        while not stop_event.wait(1.0):
            manager.poll_task_logs(output_dir)

    poll_thread = threading.Thread(target=poll_loop, name="featureliftbench-suite-progress", daemon=True)
    with Live(manager.render_group, refresh_per_second=refresh_per_second, transient=False):
        poll_thread.start()
        try:
            yield manager
        finally:
            stop_event.set()
            poll_thread.join(timeout=2.0)

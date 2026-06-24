"""Repository path constants for FeatureLiftBench."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_ROOT = REPO_ROOT / "benchmark"
TASKS_DIR = BENCHMARK_ROOT / "tasks"
SUBMISSIONS_DIR = BENCHMARK_ROOT / "submissions"
SOURCES_DIR = BENCHMARK_ROOT / "sources"
VENDOR_WHEELS_DIR = BENCHMARK_ROOT / "vendor-wheels"
EXPERIMENTS_DIR = REPO_ROOT / "experiments"
HARNESS_ROOT = REPO_ROOT / "harness"
CONFIG_DIR = HARNESS_ROOT / "config"
SCRIPTS_DIR = HARNESS_ROOT / "scripts"
DOCS_DIR = REPO_ROOT / "docs"
DEFAULT_AGENT_CONFIG = CONFIG_DIR / "agents.toml"
DEFAULT_AGENT_CONFIG_EXAMPLE = CONFIG_DIR / "agents.example.toml"


def resolve_task_input(path: str | Path) -> Path:
    """Resolve benchmark shorthand paths to the task dataset root."""

    resolved = Path(path).resolve()
    if resolved in {BENCHMARK_ROOT, TASKS_DIR}:
        return TASKS_DIR
    legacy_tasks = REPO_ROOT / "tasks"
    if resolved == legacy_tasks and TASKS_DIR.is_dir():
        return TASKS_DIR
    return resolved

"""Workspace install + prompt appendices for exec_contract."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import CONTRACT_FAILURES
from .common import CONTRACTS_DIR
from .common import FACTS_FILE
from .common import RUNTIME_DIR
from .common import ensure_dir


EXEC_CONTRACT_ENV = "FEATURELIFTBENCH_EXEC_CONTRACT_PHASE"


def install_exec_contract_workspace(workspace_dir: str | Path) -> dict[str, Any]:
    workspace = Path(workspace_dir).resolve()
    submission = workspace / "submission"
    if submission.is_file() or submission.is_symlink():
        submission.unlink()
    submission.mkdir(exist_ok=True)
    ensure_dir(workspace / RUNTIME_DIR)
    ensure_dir(workspace / CONTRACTS_DIR)
    if not (workspace / FACTS_FILE).exists():
        (workspace / FACTS_FILE).write_text(
            "# Runtime Facts\n\n_(pending Phase-0 collection)_\n",
            encoding="utf-8",
        )
    return {
        "exec_contract": True,
        "runtime_dir": RUNTIME_DIR,
        "contracts_dir": CONTRACTS_DIR,
        "facts_file": FACTS_FILE,
    }


def phase1_task_appendix() -> str:
    return (
        "### Execution-Guided Contract — Implement from upstream runtime facts\n\n"
        "Before you start coding, this workspace already contains:\n\n"
        f"1. `{FACTS_FILE}` — observations from running **upstream `repo/` tests** "
        "(inputs/outputs/exceptions/env keys). These are ground truth, not guesses.\n"
        f"2. `{CONTRACTS_DIR}/` — executable pytest contracts targeting "
        "`submission/featurelifted`.\n"
        f"3. `{RUNTIME_DIR}/` — raw traces for reference.\n\n"
        "Your job:\n"
        "1. Implement `submission/featurelifted/` per TASK.md **and** the runtime facts.\n"
        "2. Run `PYTHONPATH=submission pytest contracts/ -q` and make it **all** pass "
        "(including `test_behavior_scenarios.py` — not just surface hasattr checks).\n"
        "3. Do **not** delete/weaken contracts to force green.\n"
        "4. Do **not** import the original `repo/` package from submission.\n"
        "5. `callable(invoke)` is not enough: if scenarios call `invoke(argv)` / "
        "`resolve(argv)` / graph queries, those behaviors must work and return "
        "correct values.\n"
        "6. Prefer TASK `public_spec` signatures (e.g. optional args with defaults) "
        "over copying upstream call shapes that disagree with the TASK API.\n"
        "7. If TASK mentions symbolic identifiers (e.g. `head` / `base`), "
        "`get_revision('head')` / `get_revision('base')` must resolve them — "
        "wiring symbols only into `get_revisions` or `get_current_head` is insufficient.\n"
    )


def prepare_repair_workspace(
    workspace_dir: str | Path,
    *,
    verify_result: dict[str, Any],
    task_markdown: str,
) -> str:
    """Append contract failure feedback for a repair round."""

    workspace = Path(workspace_dir).resolve()
    body = [
        "# Contract verification failures",
        "",
        f"- ok: `{verify_result.get('ok')}`",
        f"- returncode: `{verify_result.get('returncode')}`",
        f"- backend: `{verify_result.get('backend')}`",
        "",
        "## stdout (tail)",
        "",
        "```",
        str(verify_result.get("stdout_tail") or ""),
        "```",
        "",
        "## stderr (tail)",
        "",
        "```",
        str(verify_result.get("stderr_tail") or ""),
        "```",
        "",
        "Fix `submission/featurelifted` so `PYTHONPATH=submission pytest contracts/ -q` passes.",
        "Do not weaken the contracts.",
        "",
    ]
    (workspace / CONTRACT_FAILURES).write_text("\n".join(body), encoding="utf-8")

    appendix = (
        "### Execution-Guided Contract — Repair round\n\n"
        f"Contract verification failed. See `{CONTRACT_FAILURES}`.\n"
        "Repair the submission so contracts pass; do not weaken contracts.\n"
    )
    # strip prior exec-contract appendices
    import re

    base = re.sub(
        r"\n## Execution-Guided Contract.*",
        "",
        task_markdown,
        flags=re.DOTALL,
    ).rstrip()
    new_task = base + "\n\n## Execution-Guided Contract Repair\n\n" + appendix
    (workspace / "TASK.md").write_text(new_task + "\n", encoding="utf-8")
    return new_task

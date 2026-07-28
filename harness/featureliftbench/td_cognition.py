"""TD-Cognition two-phase protocol: cognition scaffold, then implementation.

Phase 1 — Agent produces COGNITION.md + executable probes/ (no submission required).
Phase 2 — Same workspace keeps those artifacts; prompt injects them; Agent implements submission/.

See docs/METHOD_TEST_DRIVEN_COGNITION.md and docs/EXPERIMENT_ARMS.md.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


COGNITION_FILE = "COGNITION.md"
PROBES_DIR = "probes"
PHASE_AUDIT_FILE = "td_cognition_phase.json"
TD_PHASE_ENV = "FEATURELIFTBENCH_TD_COGNITION_PHASE"

REQUIRED_COGNITION_HEADINGS = (
    "## Critical Use Cases",
    "## Required Surface",
    "## Support Set Hypothesis",
    "## Exclusions",
    "## Probes",
)

MIN_USE_CASES = 3


@dataclass(frozen=True)
class CognitionGateResult:
    ok: bool
    errors: tuple[str, ...]
    details: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "errors": list(self.errors),
            "details": self.details,
        }


def install_td_cognition_workspace(workspace_dir: str | Path) -> dict[str, Any]:
    """Seed cognition templates; keep a normal writable submission/ directory."""

    workspace = Path(workspace_dir).resolve()
    submission = workspace / "submission"
    if submission.is_file() or submission.is_symlink():
        submission.unlink()
    submission.mkdir(exist_ok=True)

    cognition = workspace / COGNITION_FILE
    if not cognition.exists():
        cognition.write_text(cognition_template(), encoding="utf-8")

    probes = workspace / PROBES_DIR
    probes.mkdir(exist_ok=True)
    (probes / "__init__.py").write_text("", encoding="utf-8")
    readme = probes / "README.md"
    if not readme.exists():
        readme.write_text(
            "# Cognition probes\n\n"
            "Write pytest modules here that exercise contract understanding against "
            "`repo/` or standalone assertions.\n"
            "Do **not** import `submission.featurelifted` in phase-1 probes — they must "
            "pass without an implementation package.\n",
            encoding="utf-8",
        )

    return {
        "td_cognition": True,
        "protocol": "two_phase",
        "submission_locked": False,
        "cognition_file": COGNITION_FILE,
        "probes_dir": PROBES_DIR,
    }


def cognition_template() -> str:
    return (
        "# Cognition Scaffold (TD-Cognition)\n\n"
        "Complete every section in the cognition phase. Do not implement "
        "`submission/featurelifted/` yet.\n\n"
        "## Critical Use Cases\n\n"
        "List at least 3 concrete use cases (precondition / action / observable result).\n\n"
        "1. ...\n"
        "2. ...\n"
        "3. ...\n\n"
        "## Required Surface\n\n"
        "- Exports / public API:\n"
        "- Exceptions / error modes:\n"
        "- Resources / config / data files:\n\n"
        "## Support Set Hypothesis\n\n"
        "- Modules/files likely needed from `repo/`:\n\n"
        "## Exclusions\n\n"
        "- Subsystems that must NOT be copied into the package:\n\n"
        "## Probes\n\n"
        "- Probe files under `probes/` and what each asserts:\n"
    )


def phase1_task_appendix() -> str:
    return (
        "### TD-Cognition Phase 1 — Cognition only\n\n"
        "This run is **phase 1 of 2**. Your only job is to build understanding "
        "scaffolding. Here \"tests\" means **your own cognitive probes**, not "
        "benchmark evaluator tests.\n\n"
        "Required outputs before you finish:\n\n"
        "1. Complete `COGNITION.md` (all required headings, ≥3 concrete use cases).\n"
        "2. Write executable pytest probes under `probes/` that validate understanding "
        "against `repo/` or standalone contract checks.\n"
        "3. Run `pytest probes/ -q` and make the probes pass.\n\n"
        "**Do not** implement `submission/featurelifted/` in this phase. "
        "An empty `submission/` directory may exist; leave it empty.\n"
    )


def phase2_task_appendix(*, cognition_text: str, probe_files: list[str]) -> str:
    probe_list = "\n".join(f"- `{name}`" for name in probe_files) or "- (no probe files found)"
    body = cognition_text.strip() if cognition_text.strip() else "_(COGNITION.md missing or empty)_"
    return (
        "### TD-Cognition Phase 2 — Implement from cognition scaffold\n\n"
        "Phase 1 already produced a cognition scaffold. Treat it as your working "
        "understanding of the contract. Implement `submission/featurelifted/` "
        "accordingly; refine the scaffold only if you discover a concrete error.\n\n"
        "Available probe files:\n"
        f"{probe_list}\n\n"
        "You may re-run probes or write new checks against the submission after it exists.\n\n"
        "#### Phase-1 COGNITION.md\n\n"
        f"{body}\n"
    )


def openhands_phase1_appendix() -> str:
    return phase1_task_appendix()


def openhands_phase2_appendix(*, workspace_dir: str | Path) -> str:
    workspace = Path(workspace_dir)
    cognition_path = workspace / COGNITION_FILE
    cognition_text = (
        cognition_path.read_text(encoding="utf-8") if cognition_path.is_file() else ""
    )
    probe_files: list[str] = []
    probes = workspace / PROBES_DIR
    if probes.is_dir():
        probe_files = sorted(
            str(p.relative_to(workspace))
            for p in probes.rglob("*.py")
            if p.name != "__init__.py" and p.is_file()
        )
    return phase2_task_appendix(cognition_text=cognition_text, probe_files=probe_files)


# Back-compat name used by older docs/tests.
def openhands_td_cognition_appendix() -> str:
    return phase1_task_appendix()


def validate_cognition_scaffold(workspace_dir: str | Path) -> CognitionGateResult:
    """Validate COGNITION.md schema without running probes."""

    workspace = Path(workspace_dir).resolve()
    errors: list[str] = []
    details: dict[str, Any] = {}
    cognition_path = workspace / COGNITION_FILE
    if not cognition_path.is_file():
        errors.append(f"missing {COGNITION_FILE}")
        return CognitionGateResult(False, tuple(errors), details)

    text = cognition_path.read_text(encoding="utf-8")
    details["cognition_bytes"] = len(text.encode("utf-8"))
    missing = [h for h in REQUIRED_COGNITION_HEADINGS if h not in text]
    if missing:
        errors.append("missing required headings: " + ", ".join(missing))
    use_cases = _count_use_cases(text)
    details["use_case_count"] = use_cases
    if use_cases < MIN_USE_CASES:
        errors.append(
            f"need at least {MIN_USE_CASES} numbered use cases under "
            f"'## Critical Use Cases' (found {use_cases})"
        )
    if re.search(r"1\.\s*\.\.\.\s*\n2\.\s*\.\.\.\s*\n3\.\s*\.\.\.", text):
        errors.append("replace template placeholders in Critical Use Cases")
    return CognitionGateResult(not errors, tuple(errors), details)


def validate_probes(workspace_dir: str | Path, *, run_pytest: bool = True) -> CognitionGateResult:
    """Require at least one probe module and (optionally) a green pytest run."""

    workspace = Path(workspace_dir).resolve()
    errors: list[str] = []
    details: dict[str, Any] = {}
    probes = workspace / PROBES_DIR
    if not probes.is_dir():
        errors.append(f"missing {PROBES_DIR}/ directory")
        return CognitionGateResult(False, tuple(errors), details)

    probe_files = sorted(
        p for p in probes.rglob("*.py") if p.name != "__init__.py" and p.is_file()
    )
    details["probe_files"] = [str(p.relative_to(workspace)) for p in probe_files]
    if not probe_files:
        errors.append(
            f"no probe modules under {PROBES_DIR}/ "
            "(need at least one *.py besides __init__.py)"
        )
        return CognitionGateResult(False, tuple(errors), details)

    banned = []
    for path in probe_files:
        body = path.read_text(encoding="utf-8", errors="replace")
        if re.search(r"\bsubmission\.featurelifted\b|\bfrom\s+submission\b", body):
            banned.append(str(path.relative_to(workspace)))
    if banned:
        errors.append(
            "phase-1 probes must not import submission: " + ", ".join(banned)
        )

    if run_pytest and not errors:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", str(probes), "-q", "--tb=no"],
            cwd=str(workspace),
            capture_output=True,
            text=True,
            check=False,
        )
        details["pytest_returncode"] = proc.returncode
        details["pytest_stdout_tail"] = (proc.stdout or "")[-2000:]
        details["pytest_stderr_tail"] = (proc.stderr or "")[-2000:]
        if proc.returncode != 0:
            errors.append(
                f"pytest {PROBES_DIR}/ failed (exit {proc.returncode}); "
                "probes must pass without submission/"
            )

    return CognitionGateResult(not errors, tuple(errors), details)


def evaluate_phase1_artifacts(workspace_dir: str | Path, *, run_pytest: bool = True) -> CognitionGateResult:
    """Full phase-1 quality check (recorded; phase 2 still proceeds)."""

    scaffold = validate_cognition_scaffold(workspace_dir)
    probes = validate_probes(workspace_dir, run_pytest=run_pytest)
    errors = list(scaffold.errors) + list(probes.errors)
    details = {"scaffold": scaffold.details, "probes": probes.details}
    return CognitionGateResult(not errors, tuple(errors), details)


def prepare_phase2_workspace(workspace_dir: str | Path, task_markdown: str) -> str:
    """Reset submission/ and rewrite TASK.md with phase-2 injection."""

    workspace = Path(workspace_dir).resolve()
    submission = workspace / "submission"
    if submission.is_file() or submission.is_symlink():
        submission.unlink()
    elif submission.is_dir():
        shutil.rmtree(submission)
    submission.mkdir(parents=True)

    # Strip any prior TD appendix blocks, then append phase-2 injection.
    base = re.sub(
        r"\n## TD-Cognition.*",
        "",
        task_markdown,
        flags=re.DOTALL,
    ).rstrip()
    appendix = openhands_phase2_appendix(workspace_dir=workspace)
    new_task = base + "\n\n## TD-Cognition Phase 2\n\n" + appendix
    (workspace / "TASK.md").write_text(new_task + "\n", encoding="utf-8")
    return new_task


def write_phase_audit(
    output_dir: str | Path,
    *,
    phase1_result: CognitionGateResult,
    phase1_agent: dict[str, Any] | None,
    phase2_agent: dict[str, Any] | None = None,
) -> Path:
    path = Path(output_dir).resolve() / PHASE_AUDIT_FILE
    payload = {
        "schema_version": "featureliftbench.td_cognition_phase.v1",
        "protocol": "two_phase",
        "phase1": {
            "gate": phase1_result.to_dict(),
            "agent": _compact_agent(phase1_agent),
        },
        "phase2": {
            "agent": _compact_agent(phase2_agent),
        },
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _compact_agent(agent: dict[str, Any] | None) -> dict[str, Any] | None:
    if not agent:
        return None
    keep = (
        "name",
        "passed",
        "returncode",
        "duration_seconds",
        "timed_out",
        "reason",
        "resource_limited",
    )
    return {k: agent.get(k) for k in keep}


def _count_use_cases(text: str) -> int:
    match = re.search(
        r"## Critical Use Cases\s*\n(.*?)(?:\n## |\Z)",
        text,
        flags=re.DOTALL,
    )
    if not match:
        return 0
    return len(re.findall(r"(?m)^\s*\d+\.\s+\S+", match.group(1)))

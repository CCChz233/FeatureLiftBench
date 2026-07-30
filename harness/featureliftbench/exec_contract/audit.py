"""Audit writer for exec_contract runs."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .common import AUDIT_FILE


def compute_contract_gate_ok(
    *,
    collect_meta: dict[str, Any] | None,
    synthesize_meta: dict[str, Any] | None,
    verify_final: dict[str, Any] | None,
) -> bool:
    """Gate is green only when verify passes AND contracts are substantive.

    Vacuous surface-only suites cannot count as gate ok even if pytest is green.
    Require at least two scenario assertions (behavioral), not hasattr-only.
    """

    if not (verify_final or {}).get("ok"):
        return False
    syn = synthesize_meta or {}
    if not syn.get("contracts_substantive", False):
        return False
    scen = int(syn.get("scenario_assertions") or 0)
    if scen < 2:
        return False
    # Reject verify "green" that is mostly skips (hasattr noise / doc skips).
    stdout = str((verify_final or {}).get("stdout_tail") or "")
    m = re.search(r"(\d+)\s+passed.*?(\d+)\s+skipped", stdout)
    if m:
        passed_n, skipped_n = int(m.group(1)), int(m.group(2))
        if passed_n > 0 and skipped_n >= passed_n:
            return False
    return True


def write_exec_contract_audit(
    output_dir: str | Path,
    *,
    collect_meta: dict[str, Any] | None,
    synthesize_meta: dict[str, Any] | None,
    verify_initial: dict[str, Any] | None,
    verify_final: dict[str, Any] | None,
    repair_rounds_used: int,
    agent_primary: dict[str, Any] | None = None,
    agent_repair: dict[str, Any] | None = None,
) -> Path:
    path = Path(output_dir).resolve() / AUDIT_FILE
    gate_ok = compute_contract_gate_ok(
        collect_meta=collect_meta,
        synthesize_meta=synthesize_meta,
        verify_final=verify_final,
    )
    payload = {
        "schema_version": "featureliftbench.exec_contract_phase.v2",
        "protocol": "exec_contract",
        "phase0": {
            "collect": collect_meta or {},
            "synthesize": synthesize_meta or {},
        },
        "phase1": {"agent": _compact(agent_primary)},
        "phase2": {
            "verify_initial": verify_initial or {},
            "verify_final": verify_final or {},
            "repair_rounds_used": repair_rounds_used,
            "contract_gate_ok": gate_ok,
            "contracts_substantive": bool((synthesize_meta or {}).get("contracts_substantive")),
            "agent_repair": _compact(agent_repair),
        },
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _compact(agent: dict[str, Any] | None) -> dict[str, Any] | None:
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

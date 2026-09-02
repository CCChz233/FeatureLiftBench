#!/usr/bin/env python3
"""Run a direct structured evidence Agent over small calibration canaries."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO / "harness"))

from featureliftbench.agent_adapters import AgentRunConfig
from featureliftbench.agent_config import load_agent_run_config
from featureliftbench.agentic_evidence.direct_auditor import coerce_confidence
from featureliftbench.agentic_evidence.direct_auditor import finalize_proposed_record
from featureliftbench.agentic_evidence.direct_auditor import parse_json_response
from featureliftbench.agentic_evidence.direct_auditor import render_case_prompt
from featureliftbench.agentic_evidence.schema import validate_audit_record


def _normalize_openai_model(model: str) -> str:
    """Strip LiteLLM-style provider prefixes for raw OpenAI-compatible APIs."""

    if "/" not in model:
        return model
    provider, name = model.split("/", 1)
    if provider in {"deepseek", "openai", "hosted_vllm"}:
        return name
    return model


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("suite", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--agent-profile")
    parser.add_argument("--agent-config", type=Path)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--model")
    parser.add_argument("--agent-id")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--max-output-tokens", type=int, default=16384)
    parser.add_argument(
        "--retry-max-output-tokens",
        type=int,
        default=32768,
        help="Second-pass max tokens when the first response truncates or fails JSON.",
    )
    return parser


def _usage_payload(response: Any) -> dict[str, Any]:
    usage = getattr(response, "usage", None)
    if usage is None:
        return {}
    return {
        "prompt_tokens": getattr(usage, "prompt_tokens", None),
        "completion_tokens": getattr(usage, "completion_tokens", None),
        "total_tokens": getattr(usage, "total_tokens", None),
    }


def _merge_usage(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    if not left:
        return dict(right)
    if not right:
        return dict(left)
    merged: dict[str, Any] = {}
    for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
        a = left.get(key)
        b = right.get(key)
        if isinstance(a, int) and isinstance(b, int):
            merged[key] = a + b
        elif isinstance(b, int):
            merged[key] = b
        elif isinstance(a, int):
            merged[key] = a
    return merged


def _looks_truncated(raw: str, usage: dict[str, Any], max_tokens: int) -> bool:
    completion = usage.get("completion_tokens")
    if isinstance(completion, int) and completion >= max(1, max_tokens - 8):
        return True
    stripped = raw.strip()
    if not stripped:
        return False
    try:
        parse_json_response(raw)
    except (json.JSONDecodeError, ValueError):
        return True
    return False


def _call_once(
    client: Any,
    *,
    model: str,
    prompt: str,
    max_tokens: int,
    case_dir: Path,
    case_id: str,
    agent_id: str,
) -> tuple[dict[str, Any] | None, list[str], str, dict[str, Any]]:
    errors: list[str] = []
    record: dict[str, Any] | None = None
    raw = ""
    usage: dict[str, Any] = {}
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=max_tokens,
        )
        message = response.choices[0].message
        raw = message.content or getattr(message, "reasoning_content", None) or ""
        usage = _usage_payload(response)
        proposal = parse_json_response(raw)
        record = finalize_proposed_record(
            proposal,
            task_dir=case_dir,
            agent_id=agent_id,
        )
        errors.extend(validate_audit_record(record))
        packet = json.loads(
            (case_dir / "audit_packet.json").read_text(encoding="utf-8")
        )
        if record.get("task_id") != case_id:
            errors.append("record task_id does not match case directory")
        if record.get("nodeid") != packet.get("nodeid"):
            errors.append("record nodeid does not match audit packet")
    except Exception as exc:  # API/provider failures are recorded per case.
        errors.append(f"{type(exc).__name__}: {exc}")
    return record, errors, raw, usage


def main() -> int:
    args = _parser().parse_args()
    cases_root = args.suite.resolve() / "cases"
    if not cases_root.is_dir():
        print(f"missing canary cases directory: {cases_root}", file=sys.stderr)
        return 2
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()) and not args.resume:
        print(
            f"output already exists and is not empty: {output}; pass --resume",
            file=sys.stderr,
        )
        return 2
    output.mkdir(parents=True, exist_ok=True)
    loaded = load_agent_run_config(
        base_config=AgentRunConfig(agent="mini-swe-agent", model=args.model),
        config_path=args.agent_config,
        profile_name=args.agent_profile,
        env_file=args.env_file,
    )
    env = loaded.run_config.env or {}
    api_key = env.get("OPENAI_API_KEY") or env.get("FEATURELIFTBENCH_API_KEY")
    api_base = env.get("OPENAI_BASE_URL") or env.get("FEATURELIFTBENCH_API_BASE")
    model = _normalize_openai_model(str(loaded.run_config.model or ""))
    if not api_key or not api_base or not model:
        print("selected profile must resolve API key, API base, and model", file=sys.stderr)
        return 2
    try:
        from openai import OpenAI
    except ImportError:
        print("openai Python package is required for the direct canary runner", file=sys.stderr)
        return 2
    client = OpenAI(api_key=api_key, base_url=api_base)
    agent_id = args.agent_id or f"{args.agent_profile or model}-direct-auditor-r1"
    case_dirs = sorted(path for path in cases_root.iterdir() if path.is_dir())
    if args.limit is not None:
        case_dirs = case_dirs[: max(0, args.limit)]
    results: list[dict[str, Any]] = []
    for case_dir in case_dirs:
        case_id = case_dir.name
        case_output = output / case_id
        validation_path = case_output / "validation.json"
        if args.resume and validation_path.is_file():
            existing = json.loads(validation_path.read_text(encoding="utf-8"))
            if existing.get("valid"):
                results.append(existing)
                continue
        case_output.mkdir(parents=True, exist_ok=True)
        prompt = render_case_prompt(case_dir, agent_id=agent_id)
        record, errors, raw, usage = _call_once(
            client,
            model=model,
            prompt=prompt,
            max_tokens=args.max_output_tokens,
            case_dir=case_dir,
            case_id=case_id,
            agent_id=agent_id,
        )
        retried = False
        if errors and _looks_truncated(raw, usage, args.max_output_tokens):
            retried = True
            retry_record, retry_errors, retry_raw, retry_usage = _call_once(
                client,
                model=model,
                prompt=prompt,
                max_tokens=args.retry_max_output_tokens,
                case_dir=case_dir,
                case_id=case_id,
                agent_id=agent_id,
            )
            usage = _merge_usage(usage, retry_usage)
            raw = retry_raw
            record = retry_record
            errors = retry_errors
        (case_output / "raw_response.txt").write_text(raw, encoding="utf-8")
        if record is not None:
            (case_output / "audit_record.json").write_text(
                json.dumps(record, indent=2, ensure_ascii=False, sort_keys=True)
                + "\n",
                encoding="utf-8",
            )
        validation = {
            "case_id": case_id,
            "agent_id": agent_id,
            "model": model,
            "valid": not errors,
            "errors": sorted(set(errors)),
            "record_verdict": record.get("verdict") if record else None,
            "usage": usage,
            "retried_on_truncation": retried,
        }
        validation_path.write_text(
            json.dumps(validation, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        results.append(validation)
        print(
            f"{case_id}: {'valid' if validation['valid'] else 'invalid'} "
            f"verdict={validation['record_verdict']}"
            + (" (retried)" if retried else "")
        )
    summary = {
        "schema_version": "featureliftbench.agentic_evidence.direct_canary_run.v1",
        "suite": str(args.suite.resolve()),
        "agent_id": agent_id,
        "model": model,
        "agent_config": loaded.summary,
        "case_count": len(results),
        "valid_count": sum(bool(row.get("valid")) for row in results),
        "results": results,
    }
    (output / "run.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return 0 if summary["valid_count"] == summary["case_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

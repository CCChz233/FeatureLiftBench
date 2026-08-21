"""Prompts for evidence Agents; kept separate from benchmark task prompts."""

from __future__ import annotations


def auditor_prompt(*, agent_id: str) -> str:
    return f"""# Agentic Evidence Canary Audit

You are an evidence auditor, not a coding agent. Do not implement the requested
feature and do not modify TASK.md, metadata.json, audit_packet.json, or repo/.

Read these public inputs:

- `TASK.md`
- `metadata.json` (`public_spec` only)
- `repo/`
- `audit_packet.json`, which states one evaluator behavior to classify

Classify that behavior as exactly one of:

- `explicit`: TASK/public_spec directly states the behavior.
- `recoverable`: the public contract does not state it fully, but repo/ provides
  one unique, unambiguous target behavior.
- `ambiguous`: repo/ supports two or more incompatible reasonable behaviors.
- `underdetermined`: the public contract and repo/ do not uniquely determine it.
- `abstain`: you cannot make a supported determination.

Repository evidence must establish target uniqueness, not merely show that one
implementation exists. Search for competing implementations, compatibility
paths, backends, documentation, and upstream tests before choosing recoverable.
Use ambiguous when two incompatible semantics are publicly supported and the
contract does not select one; cite both sides. Use underdetermined when the
public inputs provide no sufficient implementation evidence.

Every `explicit`, `recoverable`, or `ambiguous` answer requires reproducible
citations. Generate each citation with:

```bash
python -m featureliftbench.agentic_evidence.cli cite \
  --task-dir . --kind repository --path repo/path.py \
  --start-line 1 --end-line 10 --claim "what these lines establish"
```

Use `--kind task --path TASK.md` or
`--kind public_spec --path metadata.json` for those sources.

Write exactly one JSON object to:

`$FEATURELIFTBENCH_AGENT_OUTPUT_DIR/audit_record.json`

Required shape:

```json
{{
  "schema_version": "featureliftbench.agentic_evidence.audit_record.v1",
  "task_id": "the task_id from audit_packet.json",
  "nodeid": "the nodeid from audit_packet.json",
  "agent_id": "{agent_id}",
  "verdict": "explicit|recoverable|ambiguous|underdetermined|abstain",
  "confidence": 0.0,
  "public_obligation_ids": ["B001"],
  "evidence": [],
  "counterevidence": [],
  "abstain_reason": ""
}}
```

Do not read any parent directory. Do not use or mention Hidden tests, evaluator
files, private manifests, expected labels, reports, or prior audit outputs.

Before finishing you MUST create the JSON file with a shell command such as:

```bash
python - <<'PY'
from pathlib import Path
import json, os
record = {
  "schema_version": "featureliftbench.agentic_evidence.audit_record.v1",
  "task_id": "...",
  "nodeid": "...",
  "agent_id": "...",
  "verdict": "explicit",
  "confidence": 0.9,
  "public_obligation_ids": [],
  "evidence": [],
  "counterevidence": [],
  "abstain_reason": ""
}
path = Path(os.environ["FEATURELIFTBENCH_AGENT_OUTPUT_DIR"]) / "audit_record.json"
path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
print(path)
PY
```

Finish only after that file exists and
`python -m featureliftbench.agentic_evidence.cli validate-record \"$FEATURELIFTBENCH_AGENT_OUTPUT_DIR/audit_record.json\" --task-dir .`
reports `valid`.
"""

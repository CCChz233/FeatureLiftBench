# Python-200 Contract V2

**Status:** candidate remediation workspace  
**Base suite:** `python200-full-repository-no-hint-20260801-v1`

This directory defines a versioned contract repair layer. It never modifies the
frozen Python-150 task trees or the existing Python-200 v1 symlinks.

- `repairs.json` records reviewed semantic and API adjudications.
- `overrides/<task_id>/` contains test or evaluator files that cannot be expressed
  as metadata operations.
- `suite.json` records the generated candidate tree digest.
- `generated_tasks/` is reproducible output and is intentionally ignored by Git.
- `generated_references/` contains copied v1 references plus reviewed v2-only
  reference overrides; it is also reproducible and ignored.

```bash
python -B scripts/generate_contract_api_patches.py
python -B scripts/materialize_python200_contract_v2.py --apply
python -B scripts/materialize_python200_contract_v2.py --check
python -B benchmark/selection/scripts/audit_python200_wheels.py \
  --suite benchmark/contract_v2/suite.json --python-version 311
```

Generated API candidates are never applied to tasks outside the explicit task list
in `repairs.json`.

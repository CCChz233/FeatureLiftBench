# Recovered execution-effort inputs (v2)

`records.json` contains one derived row per official run (900 total), source-member hashes, three independent eligibility flags/reasons, and observed checkpoint measurements. Raw prompts and tool content are not embedded. `analysis.json` is deterministically regenerated from these records; `provenance.json` identifies the seven immutable delivery archives.

- Table 3: 764 complete run totals. Prefer verified complete provider audit; otherwise require valid persisted agent/condenser usage, exact numeric deduplication of shared parent/child response IDs, per-role cumulative reconciliation, the same number of recorded requests and usage entries, successful audit statuses, and agreement with any observed audit component totals. Complete totals do not require an observed passing checkpoint or full event-ID coverage.
- Fig.4(a): 317 final successes. Additionally require a known reconstructed passing checkpoint, evaluated history and final tree/eval agreement, bijective usage/event response IDs, one-to-one audit order with adjacent timestamps, and matching observed per-call token fields. Condensation participates in token alignment and accounting.
- Fig.4(b): 403 final successes with eligible reconstructed checkpoint histories and located observation boundaries. Counts unique ActionEvent/MessageEvent response IDs first appearing after the boundary. Does not count Condensation responses or unobserved HTTP retries; token availability is not an eligibility condition.

Persistent SDK usage is historical evidence, not an estimate or an independent new provider audit. Caches are included once as part of input. Parent/child copies with conflicting numeric token components are rejected. Missing usage is not zero. No model or Docker evaluation runs during paper generation.

From the repository root:

```bash
python -B docs/paper/execution_effort.py --check
python -B docs/paper/writing/execution_effort_tables.py --check
python -B -m unittest discover -s docs/paper -p test_execution_effort.py
```

To rebuild from the complete raw delivery at the path in `import_execution_effort.py`:

```bash
python -B docs/paper/execution_effort.py --import-raw-delivery
python -B docs/paper/writing/execution_effort_tables.py
python -B docs/paper/figures/scripts/fig04_execution_effort.py
```

Normal checking, plotting and Overleaf packaging use the curated records and do not require the large archives. Keep the original delivery unchanged. Reconstruction granularity and configuration-specific recoverability limit inference; these are success-conditional descriptions, not causal efficiency rankings or guaranteed token savings.

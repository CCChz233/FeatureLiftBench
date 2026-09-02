# FeatureLiftBench current bundle

> **Documentation status: current · Last verified: 2026-09-02**

The paper main suite is **Python-200′**: frozen Python-150 + Hard-50
(`--benchmark python200_hard`). It is unreleased. Do not treat Python-150 or
150+External-50 as the current main table.

| Need | Entry |
| --- | --- |
| Local run | [RUN.md](RUN.md) |
| Server run | [docs/SERVER_RUNBOOK_PYTHON200.md](docs/SERVER_RUNBOOK_PYTHON200.md) |
| Freeze hashes and available results | [docs/STATUS.md](docs/STATUS.md) |

```bash
./scripts/run_benchmark.sh --benchmark python200_hard --agent openhands --method main
```

The v3 Python-150 frozen-transfer notes (150 oracles, 132 source archives,
freeze `846b8147…`) are in
[docs/archive/runbooks/BUNDLE_PYTHON150_V3.md](docs/archive/runbooks/BUNDLE_PYTHON150_V3.md).
Do not use that runner for new paper tables.

`--benchmark python200_hard_standard` still resolves to the v1 163 provisional
subset. Do not start new experiments on it.

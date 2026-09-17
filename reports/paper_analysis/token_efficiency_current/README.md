# Token efficiency current (server run)

Offline analysis of the official Python-150 comparison (150 tasks × 6 configurations = 900 runs).
Does not rerun agents, mutate original experiment records, or edit the paper.

Official functional-pass counts (unchanged): Pro 115, Flash 108, Luna 102, GLM 68, Qwen 63, OSS 36.

Use Python 3.12 (`tomllib`). Do not resample `pilot/pilot_manifest.csv`.

## Commands actually used

```bash
PYTHONPATH=harness python3.12 -B harness/scripts/analyze_token_efficiency_current.py inventory --manifest docs/paper/paper_sources.json --output reports/paper_analysis/token_efficiency_current/inventory
PYTHONPATH=harness python3.12 -B harness/scripts/analyze_token_efficiency_current.py pilot --seed 20260916 --output reports/paper_analysis/token_efficiency_current/pilot
PYTHONPATH=harness python3.12 -B harness/scripts/analyze_token_efficiency_current.py parse-spotcheck --output reports/paper_analysis/token_efficiency_current/spotcheck_parse
PYTHONPATH=harness python3.12 -B harness/scripts/analyze_token_efficiency_current.py run --scope paper150 --resume --workers 8 --output reports/paper_analysis/token_efficiency_current/full
# three crash recoveries after sanitizing null-byte commands and directory-as-file editor writes:
PYTHONPATH=harness python3.12 -B harness/scripts/analyze_token_efficiency_current.py run --scope paper150 --resume --workers 3 --output reports/paper_analysis/token_efficiency_current/full \
  --run-id gpt-5.6-luna/python_box__config_box_core__001 \
  --run-id gpt-5.6-luna/starlette__route_matching_core__hard3_001 \
  --run-id gpt-oss-120b/lark__parse_tree_core__001
PYTHONPATH=harness python3.12 -B harness/scripts/analyze_token_efficiency_current.py summarize --input reports/paper_analysis/token_efficiency_current/full
PYTHONPATH=harness python3.12 -B harness/scripts/analyze_token_efficiency_current.py package --input reports/paper_analysis/token_efficiency_current/full
```

Pinned evaluator: `featureliftbench-eval:python200-prime-212930ea` (never `latest`).
Pinned replay image: `featureliftbench-agent:python200-prime-212930ea`.
Resume: skip when `full/runs/<configuration>/<task_id>/metrics.json` exists.

Local eval image id is `sha256:53752765…`; some original `run.json` freeze records use `sha256:bacb3078…`. Tag and benchmark-id `212930ea` match.

## Status

- Inventory 900/900, identity conflicts 0.
- Pilot 20/20 tree + four-gate match (not prevalence).
- Full 900/900 `metrics.json` after retrying 3 worker crashes.
- Other-config Docker spotchecks: the preselected 8 runs were evaluated inside the 900 (see `spotcheck_parse/docker_spotcheck.json`). GLM fail `aiohttp` is partial/unresolved and was not replaced.
- Primary PSF (total input+output, exact T* only): Pro 102/115, Flash 94/108, Qwen 49/63, OSS 32/36. Luna 0/102 and GLM 0/68 because per-call usage is missing (`per_call_usage_null`), reported as `--` in the candidate table.
- Candidate RQ5 is **not** supported as a six-configuration PSF ranking. Effort and artifact-history are available more broadly; PSF is limited to Pro/Flash/Qwen/OSS exact subsets.

## Known limitations (do not hide)

- 116 unresolved reconstructions (incomplete timeline / partial replay). These are not `never_sufficient`.
- Original `eval/result.json` missing on 62 runs (inventory `unresolved.csv`).
- `responses__request_matcher_core__hard3_001` re-eval reports dependency-install failure; Luna original pass vs current fail is an environment mismatch and is excluded from PSF.
- Figure PNG/PDF were not rendered (matplotlib not installed); `figures/psf_ecdf.json` and `paper_ready/figure_source.json` are the redraw source.
- Three recovered runs remain partial/unresolved after sanitizing editor/terminal crashes; they have metrics.json and are in the 900-row table.

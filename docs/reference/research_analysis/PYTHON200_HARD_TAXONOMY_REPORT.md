# FeatureLiftBench Python-200' Task Taxonomy

> **Documentation status: generated/reference · Last verified: 2026-08-28**  
> Version `python200_hard_v1`. Analysis layer, not a release gate.  
> Does not include Functional Pass, RRES, or trajectories.

- Rows: **200** (`python150` 150 + `hard50` 50)
- Copy-trap flag: **5** (Hard-50 selection slot only)
- CSV: `artifacts/research_analysis/python200_hard_task_taxonomy.csv`
- 150 coverage: taxonomy v2 + lift JSONL (`v2_full`)
- Hard-50 coverage: ledger + `benchmark/hard50/*/metadata.json` (`ledger_seed`)
- `direct_tooling_copytrap` is a RQ2 flag, not an 11th feature family;
  those five tasks still have a v2 behavior family.
- Do not mix this table with superseded 150+External-50 balance counts.
- `construction_split_150` is the old 150 core100/hard50 construction
  stratum. It is **not** the new Hard-50 expansion split.

### Paper situation (200')

| label | n | share |
| --- | ---: | ---: |
| `parse_codec` | 64 | 32.0% |
| `plugin_registry` | 38 | 19.0% |
| `schema_validate` | 33 | 16.5% |
| `config_merge` | 26 | 13.0% |
| `session_lifecycle` | 22 | 11.0% |
| `resource_or_copytrap` | 17 | 8.5% |

### Feature family v2 (200')

| label | n | share |
| --- | ---: | ---: |
| `registry_plugin_dispatch` | 38 | 19.0% |
| `parse_tokenize_decode` | 37 | 18.5% |
| `config_resolve_discover` | 26 | 13.0% |
| `validate_normalize_construct` | 22 | 11.0% |
| `serialize_format_render` | 19 | 9.5% |
| `workflow_session_orchestration` | 14 | 7.0% |
| `resource_metadata_loading` | 14 | 7.0% |
| `algorithm_data_structure` | 11 | 5.5% |
| `protocol_state_transition` | 11 | 5.5% |
| `cache_retry_policy` | 8 | 4.0% |

### Lift type (200')

| label | n | share |
| --- | ---: | ---: |
| `Adapted` | 100 | 50.0% |
| `Direct` | 68 | 34.0% |
| `Composite` | 32 | 16.0% |

### Hard-50 selection family (includes copytrap slot)

| label | n | share |
| --- | ---: | ---: |
| `registry_plugin_dispatch` | 16 | 32.0% |
| `workflow_session_orchestration` | 9 | 18.0% |
| `config_resolve_discover` | 8 | 16.0% |
| `validate_normalize_construct` | 7 | 14.0% |
| `parse_tokenize_decode` | 5 | 10.0% |
| `direct_tooling_copytrap` | 5 | 10.0% |

### Python-150 paper situation

| label | n | share |
| --- | ---: | ---: |
| `parse_codec` | 59 | 39.3% |
| `schema_validate` | 26 | 17.3% |
| `plugin_registry` | 22 | 14.7% |
| `config_merge` | 18 | 12.0% |
| `session_lifecycle` | 13 | 8.7% |
| `resource_or_copytrap` | 12 | 8.0% |

### Hard-50 paper situation

| label | n | share |
| --- | ---: | ---: |
| `plugin_registry` | 16 | 32.0% |
| `session_lifecycle` | 9 | 18.0% |
| `config_merge` | 8 | 16.0% |
| `schema_validate` | 7 | 14.0% |
| `parse_codec` | 5 | 10.0% |
| `resource_or_copytrap` | 5 | 10.0% |

## Reproduction

```bash
python3.12 tools/research_analysis/build_python200_hard_taxonomy.py --check
```

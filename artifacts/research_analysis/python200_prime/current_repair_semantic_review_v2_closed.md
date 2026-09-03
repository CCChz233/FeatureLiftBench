# Python-200-prime repair semantic review (closed)

> **Status: complete · semantic scope gate: `true` · publication ready: `false`**

This record closes the 38-task repair-scope review for freeze v2.
It is AI-assisted plus maintainer adjudication, not independent human gold.

The JSON file is authoritative:
`artifacts/research_analysis/python200_prime/current_repair_semantic_review_v2_closed.json`.

## Gate

| Measure | Value |
| --- | ---: |
| Changed tasks | 38 |
| `scope_preserved` | 38 |
| `scope_changed` | 0 |
| `insufficient_evidence` | 0 |

Freeze v2 may proceed on this scope gate. Residual AI notes on surface or
hidden fairness for a few tasks are not treated as scope changes.

## Maintainer overrides

Six AI reviews were closed without changing task packages:

- `authlib__oauth2_server_core__001`: C1 disclosure of Hidden-used `OAuth2Request.payload`
- `beaker__session_cache_core__001`: C1 disclosure of Hidden-used Session mapping/`id`
- `deepdiff__deep_compare_core__001`: C1 disclosure of Hidden-used `DeepDiff.__contains__`
- `python_frontmatter__roundtrip_core__001`: protocol failure; Hidden uses `Post.__getitem__`
- `websockets__handshake_parse_core__001`: protocol failure; Hidden uses `Headers.__getitem__`
- `installer__wheel_record_core__hard3_001`: protocol failure; C2 provenance only

Evidence: `current_repair_maintainer_adjudication_v2.json`.

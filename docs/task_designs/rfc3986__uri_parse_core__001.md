# Task Design: `rfc3986__uri_parse_core__001`

Status: agent-calibrated (B-tier exception promote)

## Practical reuse

1. **Reuse module** — RFC3986 URI parser/builder for HTTP clients, config URLs, and service discovery.
2. **Who imports it** — Libraries needing hyper/rfc3986 semantics without the validators/IRI extras.
3. **Why not copy-all** — Full package ships IRI and Validator stacks beyond parse/build/normalize core.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Authority split | `featurelifted/parseresult.py` | `test_authority_userinfo_host_port` |
| Normalizers | `featurelifted/normalizers.py` | `test_normalize_uri_path_dots` |
| Builder | `featurelifted/builder.py` | `test_builder_from_uri_roundtrip` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | |
| Hidden tests | pass | |
| ExtractionRatio | 0.20 – 0.60 | |
| Copy-All delta | ≥ 0.25 | |

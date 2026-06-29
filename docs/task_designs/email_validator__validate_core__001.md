# Task Design: `email_validator__validate_core__001`

Status: agent-calibrated (B-tier exception promote)

## Why This Task

Email syntax validation is a common embedded utility (forms, auth, CRM imports). python-email-validator couples quoting state machines, IDNA encoding, RFC length tables, reserved-domain policy, and ValidatedEmail field assembly—much stronger than a regex shim.

## Practical reuse

1. **Reuse module** — Standalone offline email syntax validator returning normalized addresses and typed errors.
2. **Who imports it** — API gateways, ETL pipelines, and form backends that validate emails without DNS lookups or vendoring the full library CLI/tests.
3. **Why not copy-all** — Upstream bundles deliverability/DNS modules, CLI, and a large upstream test corpus; compact closure keeps syntax core only.

## Source

| Field | Value |
| --- | --- |
| Source repo | https://github.com/JoshData/python-email-validator |
| Commit | `b73d010bb3db70547199f39fd85d2286a7f6f476` |
| License | Unlicense |
| Difficulty | hard |
| Tags | batch-1, functional-discriminator, parser_state_coupling |

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Syntax parser | `featurelifted/syntax.py` | `test_idna_domain_normalization` |
| RFC constants | `featurelifted/rfc_constants.py` | `test_reserved_domain_rejected` |
| Orchestration | `featurelifted/validate_email.py` | `test_unicode_nfc_local_part` |

## Public Tests

- Basic ASCII `validate_email` normalization fields
- Plus-addressing local part
- `EmailSyntaxError` / `EmailNotValidError` on missing `@` and empty local

## Hidden Tests

- IDNA domain (`jeff@臺網中心.tw`)
- Quoted local de-quoting with `allow_quoted_local=True`
- Display name parsing with `allow_display_name=True`
- POSTMASTER case folding in `test_environment`
- Reserved `.invalid` domain rejection
- `test_environment` allows `.test` subdomains
- Unicode NFC local-part normalization
- SMTPUTF8 internationalized local parts
- IPv4 domain literal bracket form
- No runtime `email_validator` import surface

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | pass (oracle, copy_all, naive) |
| Hidden tests | pass | pass (oracle, copy_all); **fail** (naive) |
| Forbidden import check | pass | pass |
| Oracle LOC | ~680 | 682 |
| Source repo Python LOC | ~1740 | 1743 |
| ExtractionRatio | 0.20 – 0.60 | oracle **0.391** |
| Copy-All ExtractionRatio | > oracle + margin | **0.928** (Δ=0.537) |
| Module probes | ≥3 verified | **3/3 OK** |

Expected closure shape:

```text
featurelifted/
  __init__.py
  exceptions.py
  rfc_constants.py
  syntax.py
  types.py
  validate_email.py
```

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| `email_validator__validate_core__001-flash-001` | deepseek_v4_flash | yes (all tests) | 0.382 | 0.618 | **B-tier: 全过，ext≈0.38≈oracle 0.39** |

## Go / No-Go Criteria

- Oracle passes with `check_deliverability=False` only (no network).
- Naive regex baseline fails hidden IDNA/quoting/NFC tests.
- Copy-all extraction clearly above oracle.

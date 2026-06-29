# Task Design: phonenumbers__parse_format_core__001

Status: agent-calibrated (B-tier exception promote)

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Phone util | `phonenumberutil.py` | `test_gb_national_equals_e164_parse` |
| US metadata | `data/region_US.py` | `test_is_valid_and_e164_us` |
| GB metadata | `data/region_GB.py` | `test_gb_national_equals_e164_parse` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | |
| Hidden tests | pass | |
| ExtractionRatio | 0.20 – 0.60 | |
| Copy-All delta | ≥ 0.25 | |

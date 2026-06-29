# Task Design: `configobj__roundtrip_config_core__001`

Status: agent-calibrated (B-tier exception promote)

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| `configobj__roundtrip_config_core__001-flash-001` | deepseek_v4_flash | yes (all tests) | 0.578 | 0.422 | **B-tier:** near-oracle compact copy; hidden 未挡住 Flash |

**Promoted:** B 档例外（与 pydantic 同类）；hidden 未挡住 Flash 近 oracle 拷贝，但 naive fail + module probes 成立。

## Spike Decision

**GO for staging.**

Round-trip ConfigObj with configspec validation; distinct from smoke `iniconfig` (no comment round-trip / Validator).

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-1 | `featurelifted/validate.py` | `test_configspec_validation_failure_flattened` |
| Probe-2 | `featurelifted/interpolation.py` | `test_configparser_interpolation_resolves` |
| Probe-3 | `featurelifted/errors.py` | `test_duplicate_section_raises` |

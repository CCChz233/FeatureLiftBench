# Task Design: attrs__validators_core__001

Status: oracle-verified

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-1 | `featurelifted/validators.py` | `test_matches_re_and_deep_iterable` |
| Probe-2 | `featurelifted/_make.py` | `test_deep_mapping_validates_keys_and_values` |
| Probe-3 | `featurelifted/_config.py` | `test_set_disabled_skips_validation` |

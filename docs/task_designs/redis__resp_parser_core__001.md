# Task Design: redis__resp_parser_core__001

Status: oracle-verified

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-1 | `featurelifted/_parsers/resp2.py` | `test_resp2_simple_and_bulk_replies` |
| Probe-2 | `featurelifted/_parsers/resp3.py` | `test_resp3_null_and_boolean` |
| Probe-3 | `featurelifted/_parsers/encoders.py` | `test_encoder_rejects_bool` |

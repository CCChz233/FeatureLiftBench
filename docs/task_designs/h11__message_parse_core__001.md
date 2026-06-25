# Task Design: h11__message_parse_core__001

Status: oracle-verified

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-1 | `featurelifted/_connection.py` | `test_chunked_response_body` |
| Probe-2 | `featurelifted/_readers.py` | `test_parse_simple_http_request` |
| Probe-3 | `featurelifted/_events.py` | `test_malformed_request_raises` |

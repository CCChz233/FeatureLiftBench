# Task Design: werkzeug__routing_core__001

Status: oracle-verified

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-1 | `featurelifted/routing/map.py` | `test_subdomain_and_submount_routing` |
| Probe-2 | `featurelifted/routing/rules.py` | `test_strict_slashes_redirect` |
| Probe-3 | `featurelifted/routing/converters.py` | `test_match_and_build_simple_rules` |

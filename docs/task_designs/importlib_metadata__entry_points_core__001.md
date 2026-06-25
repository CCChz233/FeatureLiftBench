# Task Design: importlib_metadata__entry_points_core__001

Status: oracle-verified

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-1 | `featurelifted/_collections.py` | `test_entry_point_value_parsing_and_selection` |
| Probe-2 | `featurelifted/_text.py` | `test_sectioned_entry_point_config` |
| Probe-3 | `featurelifted/_itertools.py` | `test_path_distribution_entry_points` |

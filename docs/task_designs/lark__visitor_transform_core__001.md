# Task Design: lark__visitor_transform_core__001

Status: oracle-verified

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-1 | `featurelifted/visitors.py` | `test_discard_removes_nodes` |
| Probe-2 | `featurelifted/tree.py` | `test_visitor_walks_tree_nodes` |
| Probe-3 | `featurelifted/lark.py` | `test_v_args_tree_mode` |

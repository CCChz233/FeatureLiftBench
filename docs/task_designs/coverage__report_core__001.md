# Task Design: coverage__report_core__001

Status: oracle-verified

## Why This Task

Extract Cobertura XML reporting from coverage.py where report options, Analysis objects, and DOM serialization are coupled through CoverageConfig.

## Source

| Field | Value |
| --- | --- |
| Source repo | `https://github.com/coveragepy/coveragepy` |
| Commit | `f0dcf65f47120d9f74f6777134d3b8e92515ce6f` |
| License | Apache-2.0 |
| Difficulty | hard |
| Tags | extreme, multi-task-repo, config_environment_coupling |

## Output API

```python
from featurelifted import Analysis, CoverageConfig, XmlReporter, rate, serialize_xml
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| XML writer | `xmlreport.py` | `test_xml_file_emits_line_elements` (public) |
| Analysis model | `results.py` | `test_skip_empty_omits_zero_statement_files` |
| Config options | `config.py` (`xml_package_depth`, `skip_empty`) | `test_xml_package_depth_truncates_package_name` |

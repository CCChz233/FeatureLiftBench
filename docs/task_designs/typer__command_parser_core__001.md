# Task Design: typer__command_parser_core__001

Status: oracle-verified

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-1 | `featurelifted/core.py` | `test_subcommands_and_optional_path` |
| Probe-2 | `featurelifted/main.py` | `test_typed_options_and_arguments` |
| Probe-3 | `featurelifted/params.py` | `test_choice_validation` |

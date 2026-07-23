# Representative failure dossiers

These cases were selected by a deterministic stage-diversity rule. Runtime-state labels are candidates, not adjudicated causal gold.

## 1. `pytest__fixture_resolve_core__001` — `openai/Qwen3-Coder-30B-A3B-Instruct`

- **Key coupling:** framework_lifecycle; FixtureManager arg2fixturedefs registry with nodeid scoping; getfixtureclosure expands fixture argnames transitively; scope-ordered teardown/setup sequencing encoded in closure sort
- **What the agent knew:** correct entry file; target symbol; public contract passed; dynamic mechanism explicitly discussed
- **Actual behavior:** closure-read coverage 100%; runtime probes 3, dynamic-targeted probes 2; fresh post-edit verification yes; condensations 0
- **Earliest failure:** `boundary_recovery` / `verification` (high confidence)
- **Missed behavior or dependency:** fixture lookup error lists available
- **Visibility:** workflow/boundary evidence
- **Could tools expose it?:** yes—at least one targeted runtime probe was executed
- **Discovery vs memory:** recognized and retained/used incompletely
- **Most likely intervention:** forbidden-import audit plus clean isolation check
- **Evidence:** `experiments/python/openhands/qwen3-coder-30b-a3b-instruct/main-20260702-212731/pytest__fixture_resolve_core__001/agent/openhands_events.jsonl`; `experiments/python/openhands/qwen3-coder-30b-a3b-instruct/main-20260702-212731/pytest__fixture_resolve_core__001/eval/result.json`

## 2. `responses__request_matcher_core__hard3_001` — `openai/Qwen3.6-35B-A3B-FP8`

- **Key coupling:** third_party_contract; query param matcher compares parsed query strings; header matcher validates request headers; once responses are removed after first match
- **What the agent knew:** correct entry file; target symbol; public contract passed; dynamic mechanism explicitly discussed
- **Actual behavior:** closure-read coverage 100%; runtime probes 7, dynamic-targeted probes 5; fresh post-edit verification yes; condensations 0
- **Earliest failure:** `boundary_recovery` / `verification` (high confidence)
- **Missed behavior or dependency:** query and header matchers and once behavior
- **Visibility:** workflow/boundary evidence
- **Could tools expose it?:** yes—at least one targeted runtime probe was executed
- **Discovery vs memory:** recognized and retained/used incompletely
- **Most likely intervention:** forbidden-import audit plus clean isolation check
- **Evidence:** `experiments/python/openhands/qwen3.6-35b-a3b-fp8/hard50-qwen3.6-35b-a3b-fp8-20260720-022800/responses__request_matcher_core__hard3_001/agent/openhands_events.jsonl`; `experiments/python/openhands/qwen3.6-35b-a3b-fp8/hard50-qwen3.6-35b-a3b-fp8-20260720-022800/responses__request_matcher_core__hard3_001/eval/result.json`

## 3. `lark__visitor_transform_core__001` — `openai/Qwen3.6-27B-FP8`

- **Key coupling:** dynamic_import_plugin;parser_state; Tree child list shape drives dispatch; Transformer method naming conventions; v_args metadata on callbacks
- **What the agent knew:** correct entry file; target symbol; public contract not established; dynamic mechanism explicitly discussed
- **Actual behavior:** closure-read coverage unknown; runtime probes 0, dynamic-targeted probes 0; fresh post-edit verification yes; condensations 5
- **Earliest failure:** `budget_exhaustion` / `exploration_policy_or_budget` (medium confidence)
- **Missed behavior or dependency:** missing exported API: Discard
- **Visibility:** workflow/boundary evidence
- **Could tools expose it?:** unclear—the trajectory did not execute a usable runtime probe
- **Discovery vs memory:** possible post-condensation loss; weak heuristic only
- **Most likely intervention:** phase budget with earlier stop/prune policy
- **Evidence:** `experiments/python/openhands/qwen3.6-27b-fp8/qwen36-27b-fp8-main-20260704-001328/lark__visitor_transform_core__001/agent/openhands_events.jsonl`; `experiments/python/openhands/qwen3.6-27b-fp8/qwen36-27b-fp8-main-20260704-001328/lark__visitor_transform_core__001/eval/result.json`

## 4. `pygments__lexer_core__001` — `openai/Qwen3-Coder-30B-A3B-Instruct`

- **Key coupling:** dynamic_import_plugin;global_state_registry;parser_state; RegexLexer state stack and rule matching; token type hierarchy shared with filters; lexer cache and alias mapping in lexers package
- **What the agent knew:** correct entry file; target symbol; public contract not established; dynamic mechanism explicitly discussed
- **Actual behavior:** closure-read coverage unknown; runtime probes 17, dynamic-targeted probes 0; fresh post-edit verification yes; condensations 5
- **Earliest failure:** `budget_exhaustion` / `exploration_policy_or_budget` (medium confidence)
- **Missed behavior or dependency:** string and comment tokens are distinct
- **Visibility:** workflow/boundary evidence
- **Could tools expose it?:** yes—runtime probes were available but not targeted at the failing mechanism
- **Discovery vs memory:** possible post-condensation loss; weak heuristic only
- **Most likely intervention:** phase budget with earlier stop/prune policy
- **Evidence:** `experiments/python/openhands/qwen3-coder-30b-a3b-instruct/main-20260702-212731/pygments__lexer_core__001/agent/openhands_events.jsonl`; `experiments/python/openhands/qwen3-coder-30b-a3b-instruct/main-20260702-212731/pygments__lexer_core__001/eval/result.json`

## 5. `isort__settings_resolver_core__hard3_001` — `openai/Qwen3.6-35B-A3B-FP8`

- **Key coupling:** config_environment; Profile settings are lower priority than config files and runtime overrides.; pyproject.toml, setup.cfg, .isort.cfg, tox.ini, and .editorconfig use different sections.; src_paths are resolved relative to the config directory.
- **What the agent knew:** correct entry file; target symbol; public contract passed; dynamic mechanism explicitly discussed
- **Actual behavior:** closure-read coverage 100%; runtime probes 2, dynamic-targeted probes 0; fresh post-edit verification yes; condensations 3
- **Earliest failure:** `dependency_discovery` / `verification` (high confidence)
- **Missed behavior or dependency:** missing exported API: ProfileDoesNotExist
- **Visibility:** statically visible API/dependency closure
- **Could tools expose it?:** yes—runtime probes were available but not targeted at the failing mechanism
- **Discovery vs memory:** recognized and retained/used incompletely
- **Most likely intervention:** dependency/API closure hint and import-surface checklist
- **Evidence:** `experiments/python/openhands/qwen3.6-35b-a3b-fp8/hard50-qwen3.6-35b-a3b-fp8-20260720-022800/isort__settings_resolver_core__hard3_001/agent/openhands_events.jsonl`; `experiments/python/openhands/qwen3.6-35b-a3b-fp8/hard50-qwen3.6-35b-a3b-fp8-20260720-022800/isort__settings_resolver_core__hard3_001/eval/result.json`

## 6. `passlib__hash_context_core__001` — `openai/Qwen3-Coder-30B-A3B-Instruct`

- **Key coupling:** dynamic_import_plugin;global_state_registry; handler registry and scheme deprecation; context policy for rounds and identify; pbkdf2_sha256 handler wiring
- **What the agent knew:** correct entry file; target symbol; public contract passed; dynamic mechanism explicitly discussed
- **Actual behavior:** closure-read coverage unknown; runtime probes 6, dynamic-targeted probes 0; fresh post-edit verification yes; condensations 4
- **Earliest failure:** `dependency_discovery` / `verification` (high confidence)
- **Missed behavior or dependency:** missing behavior/API member: identify
- **Visibility:** statically visible API/dependency closure
- **Could tools expose it?:** yes—runtime probes were available but not targeted at the failing mechanism
- **Discovery vs memory:** possible post-condensation loss; weak heuristic only
- **Most likely intervention:** dependency/API closure hint and import-surface checklist
- **Evidence:** `experiments/python/openhands/qwen3-coder-30b-a3b-instruct/main-20260702-212731/passlib__hash_context_core__001/agent/openhands_events.jsonl`; `experiments/python/openhands/qwen3-coder-30b-a3b-instruct/main-20260702-212731/passlib__hash_context_core__001/eval/result.json`

## 7. `pendulum__parse_format_core__001` — `deepseek/deepseek-v4-flash`

- **Key coupling:** dynamic_import_plugin;global_state_registry;parser_state; iso8601 parser handles classic, ordinal, and week-calendar date forms; duration parsing splits Y/M/D and T-segment components with validation; Formatter token expansion shares locale lookups and escape brackets
- **What the agent knew:** correct entry file; target symbol; public contract passed; dynamic mechanism explicitly discussed
- **Actual behavior:** closure-read coverage 78%; runtime probes 15, dynamic-targeted probes 0; fresh post-edit verification yes; condensations 4
- **Earliest failure:** `dependency_discovery` / `verification` (high confidence)
- **Missed behavior or dependency:** missing behavior/API member: remaining_days
- **Visibility:** statically visible API/dependency closure
- **Could tools expose it?:** yes—runtime probes were available but not targeted at the failing mechanism
- **Discovery vs memory:** recognized and retained/used incompletely
- **Most likely intervention:** dependency/API closure hint and import-surface checklist
- **Evidence:** `experiments/python/openhands/deepseek-v4-flash/main-flash-20260705-232429/pendulum__parse_format_core__001/agent/openhands_events.jsonl`; `experiments/python/openhands/deepseek-v4-flash/main-flash-20260705-232429/pendulum__parse_format_core__001/eval/result.json`

## 8. `transitions__state_machine_core__hard3_001` — `deepseek/deepseek-v4-flash`

- **Key coupling:** dynamic_import_plugin;global_state_registry; conditional transitions skip when condition is false; before and after callbacks run around state changes; nested state names use dotted paths
- **What the agent knew:** correct entry file; target symbol; public contract passed; no explicit dynamic-mechanism discussion
- **Actual behavior:** closure-read coverage 100%; runtime probes 16, dynamic-targeted probes 0; fresh post-edit verification yes; condensations 0
- **Earliest failure:** `dependency_discovery` / `verification` (high confidence)
- **Missed behavior or dependency:** missing behavior/API member: parent
- **Visibility:** statically visible API/dependency closure
- **Could tools expose it?:** yes—runtime probes were available but not targeted at the failing mechanism
- **Discovery vs memory:** not explicitly discovered in agent-authored reasoning
- **Most likely intervention:** dependency/API closure hint and import-surface checklist
- **Evidence:** `experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260707-wave2wave4/transitions__state_machine_core__hard3_001/agent/openhands_events.jsonl`; `experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260707-wave2wave4/transitions__state_machine_core__hard3_001/eval/result.json`

## 9. `celery__signal_dispatch_core__hard3_001` — `openai/Qwen3.6-35B-A3B-FP8`

- **Key coupling:** global_state_registry; weak receiver cleanup after sender deletion; sender filtering limits dispatch; exception capture in send responses
- **What the agent knew:** correct entry file; target symbol; public contract passed; dynamic mechanism explicitly discussed
- **Actual behavior:** closure-read coverage 100%; runtime probes 4, dynamic-targeted probes 0; fresh post-edit verification yes; condensations 1
- **Earliest failure:** `dynamic_semantics` / `memory_state_management` (weak confidence)
- **Missed behavior or dependency:** weak receiver cleanup after sender deletion
- **Visibility:** runtime-coupled candidate; the exact causal mechanism still lacks runtime gold
- **Could tools expose it?:** yes—runtime probes were available but not targeted at the failing mechanism
- **Discovery vs memory:** possible post-condensation loss; weak heuristic only
- **Most likely intervention:** evidence-pinned memory with invalidation
- **Evidence:** `experiments/python/openhands/qwen3.6-35b-a3b-fp8/hard50-qwen3.6-35b-a3b-fp8-20260720-022800/celery__signal_dispatch_core__hard3_001/agent/openhands_events.jsonl`; `experiments/python/openhands/qwen3.6-35b-a3b-fp8/hard50-qwen3.6-35b-a3b-fp8-20260720-022800/celery__signal_dispatch_core__hard3_001/eval/result.json`

## 10. `configobj__roundtrip_config_core__001` — `openai/Qwen3-Coder-30B-A3B-Instruct`

- **Key coupling:** config_environment; Section/ConfigObj ordered dict semantics; write() round-trip comment handling; Validator type coercion and bounds checks
- **What the agent knew:** correct entry file; target symbol; public contract passed; dynamic mechanism explicitly discussed
- **Actual behavior:** closure-read coverage 100%; runtime probes 11, dynamic-targeted probes 2; fresh post-edit verification yes; condensations 1
- **Earliest failure:** `dynamic_semantics` / `capability_or_implementation` (medium confidence)
- **Missed behavior or dependency:** comment preserved on write
- **Visibility:** runtime-coupled candidate; the exact causal mechanism still lacks runtime gold
- **Could tools expose it?:** yes—at least one targeted runtime probe was executed
- **Discovery vs memory:** recognized and retained/used incompletely
- **Most likely intervention:** runtime trace plus behavior-differential probe
- **Evidence:** `experiments/python/openhands/qwen3-coder-30b-a3b-instruct/main-20260702-212731/configobj__roundtrip_config_core__001/agent/openhands_events.jsonl`; `experiments/python/openhands/qwen3-coder-30b-a3b-instruct/main-20260702-212731/configobj__roundtrip_config_core__001/eval/result.json`

## 11. `dynaconf__settings_merge_core__001` — `openai/Qwen3-Coder-30B-A3B-Instruct`

- **Key coupling:** config_environment;dynamic_import_plugin; object_merge list_merge shallow/deep/full_path semantics; Dynaconf layered environments and envvar_prefix; settings_loader merges multiple TOML files
- **What the agent knew:** correct entry file; target symbol; public contract passed; dynamic mechanism explicitly discussed
- **Actual behavior:** closure-read coverage unknown; runtime probes 8, dynamic-targeted probes 3; fresh post-edit verification yes; condensations 2
- **Earliest failure:** `dynamic_semantics` / `capability_or_implementation` (medium confidence)
- **Missed behavior or dependency:** layered toml environments
- **Visibility:** runtime-coupled candidate; the exact causal mechanism still lacks runtime gold
- **Could tools expose it?:** yes—at least one targeted runtime probe was executed
- **Discovery vs memory:** recognized and retained/used incompletely
- **Most likely intervention:** runtime trace plus behavior-differential probe
- **Evidence:** `experiments/python/openhands/qwen3-coder-30b-a3b-instruct/main-20260702-212731/dynaconf__settings_merge_core__001/agent/openhands_events.jsonl`; `experiments/python/openhands/qwen3-coder-30b-a3b-instruct/main-20260702-212731/dynaconf__settings_merge_core__001/eval/result.json`

## 12. `phonenumbers__parse_format_core__001` — `openai/Qwen3-Coder-30B-A3B-Instruct`

- **Key coupling:** dynamic_import_plugin; region metadata lazy loading for US/GB; national vs international formatting patterns; country code inference from E.164 input
- **What the agent knew:** correct entry file; target symbol; public contract passed; no explicit dynamic-mechanism discussion
- **Actual behavior:** closure-read coverage unknown; runtime probes 6, dynamic-targeted probes 0; fresh post-edit verification yes; condensations 3
- **Earliest failure:** `dynamic_semantics` / `exploration_policy` (medium confidence)
- **Missed behavior or dependency:** is valid and e164 us
- **Visibility:** runtime-coupled candidate; the exact causal mechanism still lacks runtime gold
- **Could tools expose it?:** yes—runtime probes were available but not targeted at the failing mechanism
- **Discovery vs memory:** not explicitly discovered in agent-authored reasoning
- **Most likely intervention:** targeted runtime trace/probe policy
- **Evidence:** `experiments/python/openhands/qwen3-coder-30b-a3b-instruct/main-20260702-212731/phonenumbers__parse_format_core__001/agent/openhands_events.jsonl`; `experiments/python/openhands/qwen3-coder-30b-a3b-instruct/main-20260702-212731/phonenumbers__parse_format_core__001/eval/result.json`

## 13. `pygments__formatter_core__001` — `openai/Qwen3-Coder-30B-A3B-Instruct`

- **Key coupling:** dynamic_import_plugin;framework_lifecycle;global_state_registry;parser_state; formatter option validation and defaults; style and token class translation; highlight() lexer-formatter pipeline
- **What the agent knew:** correct entry file; target symbol; public contract passed; dynamic mechanism explicitly discussed
- **Actual behavior:** closure-read coverage unknown; runtime probes 1, dynamic-targeted probes 0; fresh post-edit verification yes; condensations 4
- **Earliest failure:** `implementation` / `verification` (medium confidence)
- **Missed behavior or dependency:** full document and keyword highlighting
- **Visibility:** execution-visible behavioral mismatch
- **Could tools expose it?:** yes—runtime probes were available but not targeted at the failing mechanism
- **Discovery vs memory:** possible post-condensation loss; weak heuristic only
- **Most likely intervention:** targeted failing-behavior probe
- **Evidence:** `experiments/python/openhands/qwen3-coder-30b-a3b-instruct/main-20260702-212731/pygments__formatter_core__001/agent/openhands_events.jsonl`; `experiments/python/openhands/qwen3-coder-30b-a3b-instruct/main-20260702-212731/pygments__formatter_core__001/eval/result.json`

## 14. `pygments__lexer_core__001` — `openai/Qwen3.6-27B-FP8`

- **Key coupling:** dynamic_import_plugin;global_state_registry;parser_state; RegexLexer state stack and rule matching; token type hierarchy shared with filters; lexer cache and alias mapping in lexers package
- **What the agent knew:** correct entry file; target symbol; public contract passed; dynamic mechanism explicitly discussed
- **Actual behavior:** closure-read coverage unknown; runtime probes 20, dynamic-targeted probes 0; fresh post-edit verification yes; condensations 3
- **Earliest failure:** `implementation` / `verification` (medium confidence)
- **Missed behavior or dependency:** stripall option removes whitespace tokens
- **Visibility:** execution-visible behavioral mismatch
- **Could tools expose it?:** yes—runtime probes were available but not targeted at the failing mechanism
- **Discovery vs memory:** recognized and retained/used incompletely
- **Most likely intervention:** targeted failing-behavior probe
- **Evidence:** `experiments/python/openhands/qwen3.6-27b-fp8/qwen36-27b-fp8-main-20260704-001328/pygments__lexer_core__001/agent/openhands_events.jsonl`; `experiments/python/openhands/qwen3.6-27b-fp8/qwen36-27b-fp8-main-20260704-001328/pygments__lexer_core__001/eval/result.json`

## 15. `scrapy__item_loader_core__hard3_001` — `deepseek/deepseek-v4-flash`

- **Key coupling:** dynamic_import_plugin;framework_lifecycle;global_state_registry; input and output processor composition; nested item loader inherits parent defaults; default processor overrides per field
- **What the agent knew:** correct entry file; target symbol; public contract passed; dynamic mechanism explicitly discussed
- **Actual behavior:** closure-read coverage unknown; runtime probes 52, dynamic-targeted probes 0; fresh post-edit verification yes; condensations 3
- **Earliest failure:** `implementation` / `verification` (medium confidence)
- **Missed behavior or dependency:** missing field raises
- **Visibility:** execution-visible behavioral mismatch
- **Could tools expose it?:** yes—runtime probes were available but not targeted at the failing mechanism
- **Discovery vs memory:** recognized and retained/used incompletely
- **Most likely intervention:** targeted failing-behavior probe
- **Evidence:** `experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260707-wave2wave4/scrapy__item_loader_core__hard3_001/agent/openhands_events.jsonl`; `experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260707-wave2wave4/scrapy__item_loader_core__hard3_001/eval/result.json`

## 16. `license_expression__policy_core__hard3_001` — `openai/Qwen3.6-35B-A3B-FP8`

- **Key coupling:** global_state_registry;parser_state; AND binds tighter than OR unless parentheses override it.; WITH is only valid with exception symbols.; Aliases normalize to canonical license keys.
- **What the agent knew:** correct entry file; target symbol; public contract not established; no explicit dynamic-mechanism discussion
- **Actual behavior:** closure-read coverage 100%; runtime probes 0, dynamic-targeted probes 0; fresh post-edit verification no; condensations 1
- **Earliest failure:** `verification` / `implementation` (medium confidence)
- **Missed behavior or dependency:** AND binds tighter than OR unless parentheses override it.
- **Visibility:** workflow/boundary evidence
- **Could tools expose it?:** unclear—the trajectory did not execute a usable runtime probe
- **Discovery vs memory:** not explicitly discovered in agent-authored reasoning
- **Most likely intervention:** mandatory fresh public/install verification after final edit
- **Evidence:** `experiments/python/openhands/qwen3.6-35b-a3b-fp8/hard50-qwen3.6-35b-a3b-fp8-20260720-022800/license_expression__policy_core__hard3_001/agent/openhands_events.jsonl`; `experiments/python/openhands/qwen3.6-35b-a3b-fp8/hard50-qwen3.6-35b-a3b-fp8-20260720-022800/license_expression__policy_core__hard3_001/eval/result.json`

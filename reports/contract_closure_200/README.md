# Python-200 Contract-Closure Audit

**Status:** review complete; remediation required  
**Audit date:** 2026-08-04  
**Scope:** `python200-full-repository-no-hint-20260801-v1`

本审计区分“任务可以运行”和“evaluator contract 可以从公开证据推导”。只有 API
surface、behavior、dependency/environment 三个闭包都成立，并且每个 evaluator test
都有公开证据时，任务才记为 `closed`。

## Final Result

| Metric | Result |
| --- | ---: |
| Reviewed tasks | 200 / 200 |
| Reviewed evaluator tests | 1,471 / 1,471 |
| Unique/missing/extra task IDs | 200 / 0 / 0 |
| `closed` | 17 |
| `underspecified` | 168 |
| `contradictory` | 15 |
| API surface closed | 47 / 200 |
| Behavior closed | 115 / 200 |
| Dependency/environment closed | 159 / 200 |
| Critical/high/medium issues | 159 / 232 / 98 |

这意味着 200 条任务已经全部审完，但不能把当前 Python-200 描述为
`200/200 contract-closed`。最主要的问题是 evaluator 使用的 callable、method、返回对象字段
或动态协议没有完整进入公开 API contract；其次是行为承诺大于 hidden-test 证据，或者
adapted endpoint 缺少可追溯的 upstream/adapter derivation。

机器门禁当前结果：strict validation `169/200`，behavior-contract metadata
`143/200`，completed reviews `200/200`。最终 `--check` 失败是预期且必要的
fail-closed 行为，不代表审计未完成。

## Remediation Order

1. **P0 - 15 contradictory tasks:** 先统一 contract、tests、API kind/signature 和 oracle
   语义；无法统一的任务退出正式实验集。
2. **P1 - 168 underspecified tasks:** 先补 API/result protocol，再补行为边界测试和
   upstream/adapter provenance。API 是最大瓶颈：153 条任务的 API component 未 closed。
3. **P2 - 17 closed tasks:** 仅处理 medium 级 mapping/metadata 清理，然后进入双人复核。
4. 修复后重跑 strict validator、reference、isolation 和完整 contract-closure check；不得只让
   reference solution 通过测试就宣称修复完成。

P0 task IDs：

```text
bidict__bidirectional_map_core__001
dateparser__parse_settings_pipeline_core__001
distlib__wheel_metadata_core__hard3_001
email_validator__validate_core__001
freezegun__freeze_time_core__001
multidict__multidict_mutation_core__hard3_001
pendulum__parse_format_core__001
pyjwt__encode_decode_core__001
python_dateutil__relativedelta_core__001
python_dateutil__rrule_core__001
ruamel_yaml__roundtrip_core__001
unidiff__patch_hunk_core__001
wheel__metadata_normalize_core__hard3_001
xmltodict__xml_parse_core__001
yarl__url_model_core__001
```

## Artifacts

- `machine_audit.json`: 自动提取的 tests、assertions、API、mapping 和 validator 证据。
- `summary.csv`: 200 条任务的机器审计索引。
- `decisions.jsonl`: 200 条 reviewer-authored 最终判定和修复要求。
- `dossiers/<task_id>.md`: 每条任务供复审使用的可读证据包。
- `reviews/<task_id>.json`: 覆盖每个 test nodeid 的权威逐题审计台账。
- `api_patch_candidates.json`: 153 条 API 未闭包任务的 481 个结构化候选操作；仅供复审，生成器不会直接修改任务。

`reviews/` 由 `decisions.jsonl` 幂等物化。checker 要求全部测试节点都有最终 verdict 和
非空 evidence basis。

## Verdicts

- `closed`: evaluator obligation 可从公开 contract、pinned upstream evidence 或明确的
  adapter rule 推导。
- `underspecified`: evaluator behavior 看起来合理，但无法从可见证据完整推导。
- `contradictory`: public contract、tests、reference 或 upstream evidence 互相冲突。

## Commands

```bash
PYTHONPATH=harness python -B scripts/audit_python200_contract_closure.py --write-templates
PYTHONPATH=harness python -B scripts/materialize_contract_closure_reviews.py
PYTHONPATH=harness python -B scripts/materialize_contract_closure_reviews.py --check
PYTHONPATH=harness python -B scripts/audit_python200_contract_closure.py --check
python -B scripts/generate_contract_api_patches.py --check
```

最后一个命令会持续 fail closed，直到 200 条任务完成实际修复，而不只是完成审计。

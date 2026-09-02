# Hidden 测试的契约蕴含审计

> 判定 hidden 测试能否由 Agent 实际拿到的两个事实来源推出：`public_spec` 契约，以及固定的上游 `repo/` 快照。

## 结论

审计 **25** 个此前被归为 Agent 责任的失败任务，其中 **2** 个存在契约欠定证据（占 8.0%），另有 **5** 个存在入口溯源缺陷。上游探针有效判定 **11/25** 题。

两类需要分开看：契约欠定指 hidden 要求无法由契约条款唯一确定；入口溯源缺陷指 `source_entrypoints` 指错位置，会误导 Agent 的定位，但只要行为条款本身写清楚，题目仍然可解。

**契约有意覆盖上游不算缺陷。** 若条款明确写出与上游不同的语义（如 `popone removes the most recent matching value`），则以契约为准，Agent 照搬上游属于真实失败。

## 上游蕴含探针

| 判定 | 任务数 | 含义 |
| --- | --- | --- |
| `upstream_pass` | 1 | 上游可通过（hidden 与忠实抽取一致） |
| `upstream_contradicts` | 2 | 上游断言不符（hidden 要求与上游行为矛盾） |
| `api_reshaped` | 8 | 仅接口形状差异（任务有意改造 API，非缺陷） |
| `env_unavailable` | 14 | 环境不可用（未判定） |

## 入口锚定检查

**5/25** 个任务的 `source_entrypoints` 指向了固定 `repo/` 中不存在的符号。该字段是 Agent 定位待抽取上游代码的唯一指引，指空即意味着只能依据 `public_spec` 的行为语句猜测语义。此检查不依赖运行环境。

## 逐题结果

| 任务 | 原根因标注 | 上游探针 | 悬空入口 | 未声明接口面 |
| --- | --- | --- | --- | --- |
| `aiohttp__url_params_core__hard3_001` | contract_api_completion | `env_unavailable` | aiohttp.helpers.build_url | CIMultiDict.__getitem__;CIMultiDict.__setitem__ |
| `python_decouple__config_repository_core__001` | behavior_drift | `api_reshaped` | — | — |
| `alembic__revision_map_core__hard3_001` | behavior_drift | `env_unavailable` | — | — |
| `build__pyproject_backend_core__hard3_001` | behavior_drift | `env_unavailable` | build._builder.parse_build_system_table | — |
| `celery__signal_dispatch_core__hard3_001` | behavior_drift | `env_unavailable` | — | — |
| `cookiecutter__repo_finder_core__hard3_001` | behavior_drift | `env_unavailable` | cookiecutter.repository.RepoFinder | — |
| `dateutil__zone_resolver_core__hard3_001` | contract_api_completion | `env_unavailable` | dateutil.zoneinfo.ZoneResolver | — |
| `decorator__signature_preserving_core__001` | behavior_drift | `upstream_pass` | — | — |
| `flake8__plugin_options_core__hard3_001` | contract_api_completion | `api_reshaped` | — | — |
| `flask__route_dispatch_core__001` | behavior_drift | `api_reshaped` | — | — |
| `importlib_resources__traversable_tree_core__hard3_001` | behavior_drift | `api_reshaped` | — | — |
| `installer__wheel_record_core__hard3_001` | contract_api_completion | `env_unavailable` | installer.records.parse_wheel_record | — |
| `jupyter_core__paths_resolver_core__hard3_001` | behavior_drift | `api_reshaped` | — | — |
| `keyring__backend_select_core__hard3_001` | behavior_drift | `env_unavailable` | — | — |
| `mkdocs__plugin_config_core__hard3_001` | behavior_drift | `env_unavailable` | — | — |
| `multidict__multidict_mutation_core__hard3_001` | behavior_drift | `upstream_contradicts` | — | CIMultiDict.__getitem__;MultiDict.__getitem__ |
| `pygments__lexer_core__001` | behavior_drift | `upstream_contradicts` | — | — |
| `pylint__config_find_core__001` | contract_api_completion | `api_reshaped` | — | — |
| `pytest__marker_registry_core__hard3_001` | behavior_drift | `env_unavailable` | — | — |
| `responses__request_matcher_core__hard3_001` | behavior_drift | `api_reshaped` | — | — |
| `scrapy__item_loader_core__hard3_001` | behavior_drift | `env_unavailable` | — | — |
| `tox__factor_expression_core__hard3_001` | behavior_drift | `env_unavailable` | — | — |
| `typer__command_parser_core__001` | contract_api_completion | `env_unavailable` | — | — |
| `yamale__schema_validate_core__hard3_001` | behavior_drift | `env_unavailable` | — | — |
| `zope_interface__adapter_registry_core__001` | behavior_drift | `api_reshaped` | — | — |

## 契约欠定候选

### `aiohttp__url_params_core__hard3_001`

- 上游探针：upstream import or collection failed; no behavior test executed
- `source_entrypoints` 在快照中不存在：`aiohttp.helpers.build_url`
- 首条失败证据：`E   ImportError: cannot import name 'build_url' from 'aiohttp.helpers' (/Users/chz/anaconda3/lib/python3.12/site-packages/aiohttp/helpers.py)`
- hidden 触碰未声明接口面：`CIMultiDict.__getitem__;CIMultiDict.__setitem__`

### `python_decouple__config_repository_core__001`

- 上游探针：2/2 behavior tests differ only in API shape
- 首条失败证据：`TypeError: Config.__init__() got an unexpected keyword argument 'environ'`

## 人工裁决

| 任务 | 裁决 | 理由 |
| --- | --- | --- |
| `aiohttp__url_params_core__hard3_001` | `underdetermined` | B003 says "Invalid header names raise InvalidHeaderName" without naming the entry that validates. required_api declares only CIMultiDict.getall as a member, yet the hidden test drives validation through CIMultiDict.__setitem__. Placing the check in normalize_headers, as the submission did, satisfies every declared clause. |
| `multidict__multidict_mutation_core__hard3_001` | `fair` | Contract wins over upstream and says so. B002 states "popone removes the most recent matching value", which is exactly what the hidden test asserts; pinned upstream returns the first value instead. __getitem__ is intrinsic to the mapping types the contract declares and B004 names "lookup" explicitly, so the undeclared-member flag is a false positive here. |
| `pygments__lexer_core__001` | `fair` | Contract wins over upstream and says so. B004 states "honor lexer options such as stripall ... Required observable cases include stripall option removes whitespace tokens", which determines the hidden assertion that no Token.Text survives. Pinned upstream only strips leading/trailing input whitespace, so the probe's upstream_contradicts result reflects a deliberate contract override, not an underspecified clause. The agent followed upstream instead of the contract: genuine agent failure. |
| `pytest__marker_registry_core__hard3_001` | `undecided` | Probe artifact, not a contract finding: the pinned upstream is pytest itself, so loading the snapshot inside the running pytest process breaks fixture scope resolution ("Could not obtain a node for scope Scope.Session"). Judging this task needs an out-of-process runner. |
| `python_decouple__config_repository_core__001` | `underdetermined` | Probe stops at Config(environ=) before reaching the assertion, so this verdict rests on running the pinned repo/decouple.py directly: on the hidden input NAME='Ada Lovelace' # note it yields "'Ada Lovelace' # note" while the hidden test demands 'Ada Lovelace'. Unlike pygments and multidict the contract does not override upstream anywhere: B002 says only ".env quoted-value and comment parsing" and the echoed case name "env file quotes comments and empty" does not state that a trailing comment must be stripped from a quoted value on the same line. |

## 方法边界

- `upstream_pass` 只说明 hidden 与上游一致，不说明它已被 `public_spec` 文字覆盖；文字层面的欠定仍需人工裁决。
- `env_unavailable` 表示上游导入或 pytest 采集失败，属于未判定，不可计入任一侧。
- 上游 re-export 采用最短模块路径启发式解析符号，个别任务可能解析到非公开位置；任务新造的名字会被打桩，因此 `stubbed_symbols` 非空本身不构成缺陷。
- 判定只依据行为用例，不含生成的 `test_required_api_surface.py`。
- `api_reshaped` 表示上游在到达断言前就因接口形状不符而失败，探针对该题未下结论；此类需人工裁决，`upstream_contradicts` 计数因此是欠定情况的下界。

# Python-200″ freeze v2 修复设计

> **Status: freeze v2 published · Updated 2026-09-03**
> C1/C2/C4 修复已写入 canonical 包。门禁台账
> `reports/benchmark_gate/python200_hard_20260903_v2_repair2/` 为
> **200 `meets_standard` / 0 `violates` / 0 `undetermined`**。
> Final freeze `6c20ff0307762503a73cbb9ff32e9992c6446e4b17483a68373027be58cbf419`
> / candidate `212930ea5363f21824afd5454c4da125052ad7a7d7186886e3dddef145811254`。
> 成员不变，`task_set_sha256` 仍为 `a28c301e…`；`suite_id` 仍为
> `python200-hard-full-repository-no-hint-unreleased`（该文件已纳入 candidate 哈希）。
> 旧 Flash 132/200 只挂 v1 freeze `474862c2…`。

## 1. 为什么需要 v2

门禁 v2.p0 在 Python-200′ 上跑满 9 行 × 200 题（台账
`reports/benchmark_gate/python200_hard_20260902_p1_l4l5/`），确认了 **38 道题带缺陷**：

| 缺陷类 | 门禁行 | 题数 | 状态 | 阻断性 |
| --- | --- | ---: | --- | --- |
| 未声明接口面 | `L2_C1_SURFACE` | 21 | `fail` | blocking |
| 入口溯源缺陷 | `L2_C2_ENTRYPOINT` | 12 | `fail` | blocking |
| public/hidden 测试重复 | `L5_C4_TEST_OVERLAP` | 6 | `undetermined` | advisory |

三类去重后并集 **38 题**（`aiohttp__url_params_core__hard3_001` 同时命中 C1 与 C2；
C4 的 6 题与前两类**不相交**）。C4 非阻断，所以 `label_counts` 是
**168 meets_standard / 32 violates / 0 undetermined**——那 6 题仍在 168 里。当前处理办法
是把 32 道 blocking 违反排除成分析子集，这是绕开而不是修好。

全部 33 条 blocking 失败均带 `provenance: v2-adjudication-20260902` 的人工裁决
`confirmed_violation`，**没有一条是待复议的机械命中**。下面的修复清单因此是确定的，
不含"先看看是不是假阳性"的悬置项。

`L1_PACKAGE`、`SOURCE_IDENTITY`、`L3_ORACLE_N3`、`L3_G2PRIME_UPSTREAM`、
`L4_ISOLATION_N3`、`L5_TASK_LEAKAGE` 均 200/200 pass，**这六项不需要 v2 介入**。

## 2. 修复原则

1. **不改当前 200。** v2 是新 freeze、新 `suite_id`、新 candidate ID；成员不变时
   task-ID-set `task_set_sha256` 保持不变。旧结果按旧
   freeze 报告，不与 v2 混排。
2. **优先改声明，不改 Hidden。** C1 的正确修法是把 Hidden 已经在行使的成员写进
   `required_api.members`，而不是从 Hidden 删掉那些用法。理由：这些用法多数在语义上是公平
   的（见 §3.1），删掉会削弱题目；而标准要求的是**显式声明**。
3. **不为制造方法增益而改题**（TASK_DESIGN_RULES §9.4）。修复只针对已确认的 `failed_rules`。
4. **surface 与 fairness 正交。** 一道题可以 `hidden_fairness=fair` 同时
   `surface_compliance=fail`。修 surface 不等于承认 Hidden 不公平，也不豁免 Hidden 公平性
   的独立审计。
5. **改完必须从证据刷新开始重跑全链**，不是改完就算（§13.5）。
6. **不得逐题豁免已发布的显式 API 规则。** 若要让 Python protocol 隐式通过，必须先全局
   修订 TASK_DESIGN_RULES 并升协议版本，再统一重标 200 道（见 §5 的备选方案 B）。

## 3. 逐类修复方案

### 3.1 C1 未声明接口面（21 题）

分两个子类，修法不同。

**A. 仅缺 Python protocol dunder（13 题）**

| 任务 | 未声明成员 |
| --- | --- |
| `aiohttp__url_params_core__hard3_001` | `CIMultiDict.__getitem__`, `__setitem__` |
| `cachetools__cache_eviction_core__001` | `LFUCache` / `LRUCache` / `TTLCache` 各自的 `__contains__`, `__getitem__`, `__setitem__`（共 9 条） |
| `configobj__roundtrip_config_core__001` | `ConfigObj.__getitem__` |
| `deepdiff__deep_compare_core__001` | `DeepDiff.__contains__` |
| `importlib_metadata__entry_points_core__001` | `EntryPoints.__getitem__` |
| `intervaltree__interval_tree_core__001` | `IntervalTree.__contains__`, `__getitem__` |
| `jsonpointer__resolve_core__001` | `JsonPointer.__contains__` |
| `multidict__multidict_mutation_core__hard3_001` | `CIMultiDict.__getitem__`, `MultiDict.__getitem__` |
| `packaging__requirement_marker_specifier__001` | `SpecifierSet.__contains__` |
| `python_frontmatter__roundtrip_core__001` | `Post.__getitem__` |
| `sortedcontainers__sorted_list_core__001` | `SortedList.__delitem__` |
| `stevedore__extension_manager_core__hard3_001` | `ExtensionManager.__getitem__` |
| `websockets__handshake_parse_core__001` | `Headers.__getitem__` |

**修法：** 在对应 `required_api` 条目的 `members` 里增加显式路径，例如
`featurelifted.CIMultiDict.__getitem__`，`kind` 为 `method`，带签名。Hidden 测试不动。
这些题的 `hidden_fairness` 多为 `fair`（映射类型支持下标是固有接口），缺的只是声明。

**副作用（必须一并处理）：** `metadata.json` 变更会改 `spec_hash`；`TASK.md` 由
`render(public_spec)` 生成，会随之变化，`generated_task_hash` 也要重算。加固后的
`hidden_tests/test_required_api_surface.py` 若按现有惯例断言声明成员可调用，需同步补断言
——这正是 2026-09-01 那次对 48 道基线题做的事情，流程已验证可行（见
`experiments/registry/python200_prime_provenance_repair_20260902.md`）。

**B. 缺具名成员（8 题）**

| 任务 | 未声明成员 |
| --- | --- |
| `apispec__plugin_documenter_core__001` | `APISpec.components` |
| `asttokens__token_annotate_core__001` | `ASTTokens.tree` |
| `authlib__oauth2_server_core__001` | `OAuth2Request.payload` |
| `beaker__session_cache_core__001` | `Session.__setitem__`, `Session.get`, `Session.id` |
| `oslo_config__opt_group_core__001` | `ConfigOpts.host`, `.port`, `.timeout`, `.worker` |
| `python_configuration__layered_config_core__001` | `Configuration.__getitem__`, `Configuration.y`, `ConfigurationSet.left`, `.right`, `.shared` |
| `spiffworkflow__bpmn_engine_core__001` | `BpmnWorkflow.data` |
| `webob__request_response_core__001` | `Response.body`, `.content_type`, `.json_body`, `.status_code` |

前 6 项里的 `apispec`、`asttokens`、`authlib`、`beaker`、`spiffworkflow`、`webob` 是普通
的固定成员，**修法与 A 完全相同**：补进 `required_api.members` 即可。

`oslo_config` 与 `python_configuration` 这两道要单独说明，因为它们是**动态属性访问**：
Hidden 绑定的 `ConfigOpts.host` / `Configuration.y` / `ConfigurationSet.left` 等名字由
`__getattr__` 转发到配置数据，不是类上写死的属性。裁决意见已明确
（"Declaring `__getattr__` does not list the members Hidden binds; do not waive C1"）：
按现行标准声明 `__getattr__` **不算**声明了这些名字，所以这是真违反，不是数据流误报。
两条可行修法：

- **枚举。** 若该题的 option / key 集合由 spec 固定（`oslo_config` 的四个 opt 看起来是），
  就把它们逐个写进 `members`，`kind` 记为 `attribute`。这是方案 A 的直接延伸。
- **标准修订。** 定义"`__getattr__` 背后的数据驱动名字如何声明"（例如允许声明一个带
  枚举域的 `dynamic_attribute`）。这属于 §5 方案 B 的范畴，需要改 TASK_DESIGN_RULES 并
  升协议版本，不能只对这两道开口子。

**建议先试枚举。** 只有在 key 集合确实不由 spec 固定时才升级到标准修订。

### 3.2 C2 入口溯源缺陷（12 题）

`public_spec.source_entrypoints` 指向固定快照里不存在的符号。分两子类，**修法相同**，
区分子类只为归因。

**A. 把题目新造的 `featurelifted` 名字误存成上游入口（7 题）**

| 任务 | dangling 符号 |
| --- | --- |
| `build__pyproject_backend_core__hard3_001` | `build._builder.parse_build_system_table` |
| `click__lazy_command_core__hard3_001` | `click.core.LazyCommandCollection` |
| `cookiecutter__repo_finder_core__hard3_001` | `cookiecutter.repository.RepoFinder` |
| `dateutil__zone_resolver_core__hard3_001` | `dateutil.zoneinfo.ZoneResolver` |
| `diskcache__eviction_policy_core__hard3_001` | `diskcache.core.EvictionPolicyPlanner` |
| `fs__url_opener_core__hard3_001` | `fs.opener.registry.FSOpenerRegistry`（同题 `parse_fs_url` 已 resolved） |
| `installer__wheel_record_core__hard3_001` | `installer.records.parse_wheel_record` |

**B. 模块路径或叶子名写错，上游确实没有该定义（5 题）**

| 任务 | dangling 符号 |
| --- | --- |
| `aiohttp__url_params_core__hard3_001` | `aiohttp.helpers.build_url` |
| `hatch__project_metadata_core__hard3_001` | `hatchling.metadata.core.normalize_project_metadata` |
| `readme_renderer__content_type_core__hard3_001` | `readme_renderer.render_readme` |
| `setuptools_scm__version_normalize_core__hard3_001` | `setuptools_scm.version.version_from_scm` |
| `virtualenv__interpreter_spec_core__hard3_001` | `virtualenv.discovery.py_info.parse_spec` |

**修法：** 把 `source_entrypoints` 改成 pinned 快照里**真实存在**的、该特征实际抽取自的
符号；确认不存在对应上游锚点的，删掉该指针（`undeclared` 在 R-ENTRY 下机械通过）。
**不要**为了让检查过关而编造一个能解析的符号。

注意 A 类的错误模式值得单独记进论文的失败归因：Hard-50 出题流程会把 `featurelifted`
侧的目标 API 名回填到上游 provenance 字段。v2 的出题模板应该在这两个字段之间加类型隔离。

### 3.3 C4 public/hidden 测试重复（6 题）

6 题各有 1 条 public 与 hidden 函数体逐字相同的测试（`overlap_ratio` 0.25–0.50），
判定依据见 [BENCHMARK_VALIDATION_GATE.md](BENCHMARK_VALIDATION_GATE.md) L5 节。

| 任务 | public / hidden 同体测试 |
| --- | --- |
| `anyio__task_group_core__001` | `test_fail_after_timeout` / `test_fail_after_timeout_is_timeout_error` |
| `copier__template_answers_core__001` | `test_invalid_choice_raises` / `test_invalid_choice_raises_value_error` |
| `mitmproxy__url_parse_core__001` | `test_parse_http_ipv4_port` / `test_parse_http_explicit_port` |
| `pika__channel_spec_core__001` | `test_heartbeat_roundtrip` / `test_heartbeat_bytes_roundtrip` |
| `pre_commit__config_load_core__001` | `test_default_minimum_pre_commit_version` / `test_empty_repos_default_version` |
| `pylint__config_find_core__001` | `test_configuration_file_disable_turns_message_off`（同名） |

**修法：** 改写 hidden 侧那一条，使它检验 public 没检验的行为；或删除它并确认对应
behavior clause 仍有其他 hidden 覆盖（`constitution_validate` 会强制这一点）。
**不要**改 public 侧——public 允许做浅层 smoke（§4.2.6）。

危害程度低（该 hidden 断言不提供 public 之外的信息，不是题目失效），所以 C4 保持
advisory，这 6 题**不**从 168 题分析子集中排除。

**试修结果（2026-09-02）：好修。** 6 道全部只改 hidden、不改 public / `public_spec`，
C4 清零、constitution 通过、oracle `functional_gate == 1.0`（镜像
`featureliftbench-eval:python200-prime-769f2486`）。补丁已写入
`benchmark/hard50/*/hidden_tests/test_hidden_behavior.py`。明细
[c4_overlap_trial_20260902.md](../experiments/registry/c4_overlap_trial_20260902.md)。
这**不是** freeze v2：C1/C2 的 32 题未动，也没有重算 `task_set_sha256`。

## 4. 已锁死的决定（2026-09-02/03 试修）

两道抽样已在
[c1c2_rescue_trial_20260902.md](../experiments/registry/c1c2_rescue_trial_20260902.md)
跑通，做法不再讨论：

| 决定 | 选择 | 理由 |
| --- | --- | --- |
| 修法 | **方案 A：补声明** | jsonpointer 补 `__contains__`、installer 改入口，C1/C2 机械过、constitution 过、oracle 1.0。方案 B 要改标准并重标 200 道，32 道里只有 13 道受益 |
| Hidden / public | **一律不动** | 缺陷在声明，不在测试 |
| 工作副本 | **git 分支上改 canonical 包**（`benchmark/tasks/` 与 `benchmark/hard50/`） | `python200_hard_tasks/` 已是 symlink；再复制 200 棵树没有隔离收益。C4 的 6 道 hidden 已经写进 hard50 |
| 发布形态 | **新 freeze / 新 `suite_id` / 新 candidate ID** | C1 改 `public_spec`，`spec_hash` 必变；成员未变，task-ID-set hash 保持不变。旧 Flash 结果仍挂旧 freeze |
| 动态属性两道 | **枚举 Hidden 实际绑定的名字** | 不升协议。见 §6 波次 3 |

C4 6 道已在工作区修好，随同一刀 freeze 切进去，不必单独再做。

## 5. 每题固定流水（不要手改 JSON 忘哈希）

C1 与 C2 共用收尾，中间步骤不同。试修里已经跑通的顺序：

1. 改 `metadata.json` 的 `public_spec`（C1 加 `members`，C2 改 `source_entrypoints`）。
2. C1 额外：用 `_explicit_surface_text` 重写 `api_surface` 条款（通常是 B005）及其
   `evaluation_spec.public_clauses` 对应行；给新 path 补
   `required_api_coverage`（hidden 行为测试 + `test_required_api_surface`）。
3. `render_public_task` → 写 `TASK.md`。
4. `sync_spec_hashes`；`task_revision += 1`。
5. `_write_required_api_surface_test` 重生成 surface 断言（C2 也可跑，无害）。
6. `validate_constitution` 必须空错误。
7. 机械门禁：C1 用 `_surface_check`，C2 用 `_entrypoint_check`（`Snapshot(task/repo)`
   或物化后的 canonical source）。
8. Docker oracle 1 次，镜像钉
   `featureliftbench-eval:python200-prime-769f2486`。

签名：能从 oracle / 上游源 `inspect.signature` 就用真实签名；dunder 惯例是
`__getitem__/__contains__(self, key)`、`__setitem__(self, key, value)`、
`__delitem__(self, key)`。`kind`：dunder 与 `Session.get` 为 `method`，
`.body` / `.host` 为 `attribute`。

**禁止：** 为过 C2 编造快照里没有的符号；从 Hidden 删用法来消 C1；改 public 测试。

## 6. 波次

每波结束必须：该波机械 C1/C2 = pass，constitution = pass，oracle 1-rep
`functional_gate == 1.0`。失败停在该波，不累积到下一波。

### 波次 1 — C1 protocol dunder（13 题）

与 jsonpointer 同构。成员清单见 §3.1A，以门禁台账
`python200_hard_20260902_p1_l4l5` 为准，不要凭记忆减条（`cachetools` 是 9 条，
不是 3 条）。

脚本输入：`{task_id: [{path, kind, signature}]}`。不要 13 次手贴 metadata。

### 波次 2 — C1 固定具名成员（6 题）

`apispec.components`、`asttokens.tree`、`authlib.payload`、`beaker` 的
`Session.__setitem__/.get/.id`、`spiffworkflow.data`、`webob` 的四个 `Response.*`。
流水同波次 1，多数 `kind=attribute`。`beaker` 混有 dunder，仍走同一脚本。

### 波次 3 — C1 动态属性（2 题，人工核对名字）

不改 TASK_DESIGN_RULES。把 Hidden **实际绑定**、且已在行为条款示例里出现的名字写成
`attribute` 成员。`__getattr__` 已经声明过，**不够**。

| 任务 | 枚举这些名字 | 依据 |
| --- | --- | --- |
| `oslo_config__opt_group_core__001` | `ConfigOpts.host`, `.port`, `.timeout`, `.worker` | Hidden 注册并读取的 opt/group 名；B001–B004 已写 attribute access |
| `python_configuration__layered_config_core__001` | `Configuration.__getitem__`, `Configuration.y`, `ConfigurationSet.left/.right/.shared` | Hidden 的 `cfg.y.z` 与 `merged.left/right/shared`；B001 已承诺 item+attribute |

若枚举后 C1 仍报新名字，只补 Hidden 用到的，不预先声明公共测试里的 `cfg.db.host` 等
未在 C1 证据中的路径。

### 波次 4 — C2 入口（12 题，先表后写）

**先产出一张可审查对照表**（JSON + markdown），再一次性 apply。表列：
`task_id, dangling, verdict_now, proposed, basis`。`proposed` 只能是
`resolved` 符号或 `delete`。installer 已有答案：
`parse_wheel_record` → `installer.records.parse_record_file`。

查找顺序：

1. 叶子名在 `Snapshot.leaf_names` 里 → 用真实模块路径（`misplaced` 变 `resolved`）。
2. 不在：对照 `required_api` / `oracle_manifest.required_source_files`，在那些文件里找
   真正被抽取的 `def`/`class`（installer 就是这样找到 `parse_record_file` 的）。
3. 仍没有上游锚点 → **删除该指针**，不要编。同题其他已 `resolved` 的入口保留
   （`fs` 的 `parse_fs_url` 就是这种情况）。

7 道 A 类（featurelifted 名回填）和 5 道 B 类（路径写错）用同一查找顺序，只是归因不同。
`aiohttp__url_params_core__hard3_001` 两波都要做：波次 1 补 dunder，波次 4 修入口。

**波次 4 结果（2026-09-03）：** 对照表
`experiments/validation/c1c2_repair_v2/c2_mapping.md`，12 道全部写成快照里
`resolved` 的真实符号（没有删到空列表，没有编造叶子）。constitution 空、机械 C2
pass、oracle 1-rep 12/12 `functional_gate == 1.0`（镜像
`featureliftbench-eval:python200-prime-769f2486`）。明细
[c1c2_repair_v2_wave4_20260903.md](../experiments/registry/c1c2_repair_v2_wave4_20260903.md)。

### 波次 5 — 收口 freeze

只在 32 题机械清零之后：

1. 32 题 oracle N=3（C1 改了 surface 测试；C2 理论上不变，仍跑，避免漏 aiohttp）。C4 6 道 hidden 已改，一并 N=3。
2. 全量 200 门禁 9 行，要求 C1=0 fail、C2=0 fail、C4=0 hit、`undetermined=0`。
3. G2′ 至少覆盖声明或 hidden 已变的 38 题并写回 200 份 summary（隔离/行为分类可能变）。
4. 新 freeze **不能**再用 `materialize_python200_hard_frozen_input.py` 的
   `BASE_REF=f822ff28`（那是 v1 加固前的 150 题档案，会覆盖本次声明修复）。
5. 保留成员不变的 task-ID-set `task_set_sha256`，生成新的 candidate ID、freeze ID
   和 `suite_id`（例如 `python200-hard-full-repository-no-hint-v2`）。内容变化由
   per-task revision/spec/tree hash 与 candidate/freeze ID 表达。
6. 发布选择关系：**预期 200 `meets_standard` / 0 `violates`**，168 分析子集作废。
7. 更新 `STATUS.md`、`suites.toml`、`benchmark/README.md`、论文表注。
   **旧 132/200 与 81/96 不得改挂到新 freeze 上**——要写「v1 freeze 上的分数」。

**波次 5 已完成的证据（2026-09-03）：** 上表 1–3。Oracle N=3：32 修复题 96/96 +
C4 6 题 18/18，指纹稳定。G2′ 38/38 pass（aiohttp 的 first_block 从 build 变为
public，证实必须重跑）。全量门禁
`python200_hard_20260903_v2_repair2`：**9 行全 200 pass，200 meets_standard**。
中间一次 `repair` 台账是 185/15，原因是 C1 改 TASK.md 后未同步
`evaluation/behavior_contract.json` 的 `spec_sha256`；已补进两个 repair 脚本。
**已做（2026-09-03 续）：** 38 道修复语义范围闭环（AI 辅助 + 维护者裁决，
38/38 `scope_preserved`，非 human gold）；HEAD candidate；linux/amd64 镜像
`featureliftbench-eval:python200-prime-212930ea` /
`featureliftbench-agent:python200-prime-212930ea`；该镜像上 200×3 Oracle
600/600；final freeze 与 200/0 选题文件（168/32 归档）。中间一次 freeze
`45b7fd43` / candidate `180dc917` 绑定了修复后题包，但 `harness/config/experiments`
仍是 168/32 覆盖层，已作废。
修复接收规则与生成台账见
[`BENCHMARK_REPAIR_PROTOCOL.md`](BENCHMARK_REPAIR_PROTOCOL.md) 和
`artifacts/research_analysis/python200_prime/current_repair_ledger_v2.json`。

## 7. 工作量与风险

| 波次 | 题数 | 性质 | 主要风险 |
| --- | ---: | --- | --- |
| 1 dunder | 13 | 脚本 | `cachetools` 漏类；surface 条款漏刷 |
| 2 具名 | 6 | 脚本 | `kind` 写成 method |
| 3 动态 | 2 | 人工 | 枚举过宽（把未行使的 opt 写进去）或过窄（C1 仍 hit） |
| 4 入口 | 12 | 先表后写 | 找不到锚点时硬编符号；漏删 aiohttp 的 dangling |
| 5 freeze | 32+200 | 评测 | 镜像不是 `769f2486`；N=3 指纹漂 |

Oracle 1-rep 试修两道合计约 12 秒级到 1 分钟级。32 道 1-rep 用 3 worker 大约数分钟；
N=3 约 15–20 分钟。G2′ 全量约 10 分钟。没有 API 预算项。

## 8. 验收条件

v2 freeze 只有在下列全部成立时才能发布：

```text
门禁 9 行 × 200，无 fail、无 undetermined
L2_C1_SURFACE      = 0 fail
L2_C2_ENTRYPOINT   = 0 fail
L5_C4_TEST_OVERLAP = 0 hit
oracle N=3 覆盖 32 道修复题，fingerprint 稳定
G2′ 无 functional_gate == 1.0
38 道修复 semantic review 全部为 scope_preserved，无 insufficient_evidence
materialize --check 通过，输入 SHA 与 freeze 记录一致
分析标签 200 meets_standard / 0 violates（旧 168/32 归档）
```

**仍可延期：** 全 200 Hidden 公平性 universal claim、G2_naive / G3 / G4 内容缺口、
方案 B 协议修订。Flash-33 双审计与机械 clear 题分层抽样用于论文 claim boundary；
把旧 Flash 主表重跑到新 freeze 属于 freeze 后实验，不属于修题步骤。

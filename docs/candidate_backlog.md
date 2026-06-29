# 候选仓库 / 功能 Backlog（Python batch-1）

**目标：** 为 **新增 50 道** 主榜题（batch-1）储备候选；**batch-0 五十题不修改**。

**最后更新：** 2026-06-28

**流程：** 先看仓库池 [BATCH1_REPO_SELECTION.md](BATCH1_REPO_SELECTION.md)，再按 [EXPANSION.md](EXPANSION.md) 和 [BATCH1_PLAYBOOK.md](../BATCH1_PLAYBOOK.md) 出题。

**边界：** 本文件记录“功能切片/题目想法”；repo 是否值得占用 batch-1 名额，以 [BATCH1_REPO_SELECTION.md](BATCH1_REPO_SELECTION.md) 为准。

**状态：** `idea` → `shortlist` → `staging` → `promoted`（已入 `benchmark/tasks/`）| `dropped`

---

## 统计

| 状态 | 数量（手动更新） |
| --- | ---: |
| idea | 12 |
| shortlist | 0 |
| staging | 0 |
| promoted | 36 |
| dropped | 0 |

---

## Batch-0 已覆盖源库（勿重复切面）

扩题前用 [benchmark_tasks.md](benchmark_tasks.md) 核对。已覆盖库示例（非完整列表）：

sqlparse, coverage, jinja2, pytest, vibe_app, click, typer, marshmallow, lark, pygments, redis, jsonschema, …

**同库新题允许**，但必须是 **不同可复用功能切面**（design note 必说明）。

---

## 候选表

| # | source / repo | 候选功能（reuse 一句话） | entanglement 粗标 | 状态 | staging / task_id | 备注 |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | httpx | Request/URL/Headers/QueryParams/Cookies 数据模型与 client/request 合并语义，可复用为独立 HTTP request builder | parser_state + data_model + config_environment | **promoted** | `httpx__request_model_core__001` | batch-1 首题入榜；oracle 0.318 extraction；Flash public pass / hidden fail |
| 2 | urllib3 | Retry / Timeout 策略解析、退避时间和状态码判定，可复用为请求策略模块 | config_environment + data_model | idea | | 有用但上游已较独立，难度可能不够；保留作后续 control / medium-hard |
| 3 | websockets | HTTP upgrade header / handshake 校验，可复用为协议握手解析器 | parser_state + resource | idea | | hidden 可测 header folding、大小写、错误类型 |
| 4 | python-multipart | multipart/form-data 流式解析，可复用为上传表单解析模块 | parser_state + resource | **promoted** | `python_multipart__form_parse_core__001` | batch-1 #24；oracle 0.385；Step 5 全绿 |
| 5 | email-validator | 邮箱地址解析、规范化和错误分类，可复用为输入校验模块 | parser_state + third_party_dependency | idea | | 可能涉及 idna / DNS，必须禁网并裁剪 |
| 6 | python-dateutil | `rrule` / `rrulestr` 解析与迭代，可复用为日程重复规则模块 | parser_state + global_state_registry | **promoted** | `python_dateutil__rrule_core__001` | batch-1 #3；oracle 0.277；Flash compact pass final≈0.72 |
| 7 | python-dateutil | `relativedelta` 运算与归一化，可复用为日期偏移模块 | data_model | **promoted** | `python_dateutil__relativedelta_core__001` | batch-1 #28；oracle 0.259；与 rrule 题不同 reuse 切面 |
| 8 | croniter | cron 表达式解析与 next/prev 时间计算，可复用为调度规则模块 | parser_state + config_environment | idea | | hidden 覆盖 DST、范围、step |
| 9 | configobj | INI-like 配置解析、写回、注释保留和 configspec 校验，可复用为 round-trip 配置模块 | parser_state + config_environment | shortlist | `configobj__roundtrip_config_core__001` | 与 iniconfig 不重复：强调 round-trip / validation |
| 10 | python-dotenv | `.env` 解析、quote/escape、变量展开，可复用为环境配置加载器 | config_environment + parser_state | **promoted** | `python_dotenv__env_parse_core__001` | batch-1 #23；oracle 0.237 |
| 11 | environs | 环境变量类型转换与默认值处理，可复用为 typed env loader | config_environment + data_model | **promoted** | `environs__typed_env_core__001` | batch-1 #26；oracle 0.355；Flash 待补 |
| 12 | dynaconf | 分层 settings 合并与 env override，可复用为配置合并核心 | config_environment + framework_coupling | idea | | 风险：框架面较大，先做 spike |
| 13 | pydantic v1 | `BaseModel` 字段解析、validator/root_validator、错误树与 model config，可复用为 schema validation core | data_model + framework_coupling + global_state_registry | **promoted** | `pydantic_v1__validation_error_core__001` | batch-1 #2 入榜；oracle 0.567 extraction；Flash copy-heavy pass（final≈0.44） |
| 14 | cerberus | schema validation、coerce、错误路径，可复用为轻量数据校验器 | data_model | **staging** | `cerberus__schema_validate_core__001` | hidden 覆盖 nested schema / coerce / error tree；naive hidden fail |
| 15 | voluptuous | schema 编译、组合 validator 和错误聚合，可复用为配置校验器 | data_model + implicit_dependency | idea | | closure 可能较紧凑 |
| 16 | cattrs | attrs/dataclass structuring / unstructuring，可复用为对象转换模块 | data_model + third_party_dependency | idea | | 与 attrs 题切面不同；需白名单依赖策略 |
| 17 | dataclasses-json | dataclass encode/decode 与字段命名策略，可复用为 JSON model mapper | data_model + framework_coupling | **promoted** | `dataclasses_json__serde_core__001` | batch-1 #27；oracle 0.263 / naive hidden fail / copy-all 0.913 |
| 18 | sortedcontainers | SortedList / SortedDict 核心不变量，可复用为有序集合模块 | data_model | **staging** | `sortedcontainers__sorted_list_core__001` | hidden 覆盖 bisect、切片、重复值；naive hidden fail |
| 19 | bidict | 双向映射不变量、冲突策略和 inverse view，可复用为双向索引模块 | data_model | idea | | compact oracle 应可建 |
| 20 | cachetools | LRU / TTL cache 淘汰策略，可复用为缓存容器模块 | data_model + global_state_registry | idea | | hidden 覆盖时间源注入和 eviction |
| 21 | jsonpath-ng | JSONPath parser + evaluator，可复用为 JSON 查询表达式引擎 | parser_state + data_model | shortlist | `jsonpath_ng__expression_eval_core__001` | hard；需限制 grammar 范围，注意 PLY/docstring 依赖 |
| 22 | jsonpointer | JSON Pointer 解析、转义和 resolve/set，可复用为 JSON 文档定位模块 | parser_state + data_model | idea | | 可能偏 medium；可做 smaller task |
| 23 | deepdiff | path expression / exclude matcher，可复用为结构化 diff 过滤器 | data_model + parser_state | idea | | 避免整库 diff 引擎过大 |
| 24 | xmltodict | XML SAX 到 dict 的解析和命名空间处理，可复用为 XML 映射模块 | parser_state + resource | idea | | hidden 覆盖 attrs、cdata、namespace |
| 25 | python-frontmatter | Markdown front matter 解析与 dump，可复用为内容元数据模块 | parser_state + config_environment | idea | | 需明确 YAML 依赖白名单 |
| 26 | docutils | reStructuredText inline markup 子集，可复用为轻量标记解析器 | parser_state + framework_coupling | idea | | 风险大；适合后置 spike |
| 27 | mako | template lexer / expression tokenizer 子集，可复用为模板预处理模块 | parser_state + framework_coupling | idea | | 与 jinja2 不重复：不同模板语法 |
| 28 | tabulate | 表格布局、宽度计算和格式输出，可复用为纯文本 formatter | data_model + resource | **promoted** | `tabulate__table_format_core__001` | batch-1 #22；oracle 0.302 |
| 29 | pathvalidate | 文件名/路径清洗与平台规则，可复用为跨平台路径校验模块 | config_environment + parser_state | idea | | hidden 覆盖 Windows 保留名 |
| 30 | yarl | URL 对象解析、join、query 操作，可复用为 URL 数据模型 | parser_state + data_model | **promoted** | `yarl__url_model_core__001` | batch-1 #21；oracle 0.229；与 httpx 不同切面（immutable URL model） |

（复制上表行继续添加；目标 **≥80** 条 idea，其中 **≥50** 进 staging 且 oracle 绿。）

### Useful + hard + testable 入榜硬门

batch-1 的主榜题必须同时满足 **useful + hard + testable**。有用但不难、或很难但不好稳定评估的切片，只能留作 control、sanity、research note 或 dropped，不进入主榜。

入榜判断采用以下 gate：

- **非平凡闭包**：预估 compact oracle 至少跨 6 个运行时文件或约 1200 LOC；单文件/薄 wrapper 默认不入主榜。
- **跨关注点耦合**：目标功能至少牵涉 parser/state、data model、config/environment、resource、registry/metaclass 中的两类。
- **hidden 可判别**：能设计组合行为、错误恢复、顺序/保真、边界输入或状态交互测试；不能只测 happy path。
- **copy-heavy 有惩罚空间**：Copy-All 与 oracle 的 extraction_ratio 应显著拉开；若整库很小或核心本来独立，优先淘汰。
- **仍有现实复用价值**：提取物应能作为独立 package 被真实项目 import，而不是为了难度人为切怪接口。
- **可评估**：public/hidden 必须是离线 deterministic pytest；不能依赖网络、真实时钟漂移、外部服务、平台专有资源或人工判断。
- **失败可归因**：至少 3 个 module probes 能分别触发不同 hidden failure；如果失败只能表现为整体 import 崩溃，说明边界或测试设计不够好。
- **baseline 可分层**：oracle 应过且 compact；copy-all 应过但 extraction 高；naive/shallow baseline 应在 hidden 上失败。

### 首批 shortlist 结论

首批 5 个进入 `shortlist`：

| 排名 | task_id 草案 | 推荐动作 | 选择理由 | 主要风险 |
| ---: | --- | --- | --- | --- |
| 1 | `httpx__request_model_core__001` | **先做 staging pilot** | HTTPX API 明确有 URL、Headers、Cookies、Client build/merge 语义；提取成 request builder 很有用，且从 client/transport/streaming 中切出才有难度 | 需控制 `idna` / content helpers，不带网络 transport；评估上要固定离线 body/header/cookie 语义 |
| 2 | `pydantic_v1__validation_error_core__001` | **promoted** | `BaseModel`、field validators、root validators、config、error tree 都是真实复用面；足够难，能测框架/数据模型解耦 | oracle 0.567 extraction；naive hidden fail；Flash copy-heavy pass，后续可考虑加强 hidden 对 bulk-copy 的判别 |
| 3 | `python_dateutil__rrule_core__001` | hard 题优先推进 | iCalendar recurrence 真实复杂，`rrule` / `rrulestr` / `rruleset` hidden 判别力强 | oracle closure 可能牵到 parser/tz/easter；测试必须固定 timezone/naive datetime，避免本机 tzdata 漂移 |
| 4 | `jsonpath_ng__expression_eval_core__001` | **promoted** | parser + AST + evaluator；表达式 first-class，适合测试 find/update/filter/path | Flash copy-heavy A-tier（ext 1.0, final 0.0） |
| 5 | `configobj__roundtrip_config_core__001` | **promoted** | round-trip、注释/顺序、configspec 校验都适合 hidden；与 smoke `iniconfig` 切面不同 | Flash B-tier（ext≈0.58）；B 档例外 promote |

暂不把 `urllib3`、`xmltodict`、`python-multipart` 放进首批：它们功能真实，但候选切片偏独立或偏小，容易变成“复制核心文件”，难度不稳定。可以留作后续 control、medium-hard 或 sanity 附录候选。

---

## 新库探索清单（idea 来源，可选）

以下为 **未在 batch-0 出现** 的库类方向，供 brainstorming（不保证入榜）：

- HTTP / 协议：httpx, urllib3 子模块, websockets
- 序列化：orjson 替代路径, msgpack 子集
- 模板 / 文本：mako, chameleon, docutils 子集
- 配置：dynaconf, configobj, python-box
- 日期 / 时区：pendulum, dateutil 子集
- 数据结构：sortedcontainers, bidict
- 校验：pydantic v1 子集（注意体积）
- CLI 以外工具：rich 子模块（batch-0 有 markup）、textual 子集

入榜仍以 **reuse + oracle 可建** 为准，上表仅作 backlog 种子。

---

## 变更日志

| 日期 | 说明 |
| --- | --- |
| 2026-06-28 | batch-1 #47–49 promote：`h2__frame_parse_core__001` (0.20)、`referencing__json_schema_refs_core__001` (0.48)、`wsproto__frame_parse_core__001` (0.317)；#50 `astroid__nodes_core__001` skip（oracle fail，extraction 0.713） |
| 2026-06-27 | `httpx__request_model_core__001` promote 至主榜（batch-1 首题） |
| 2026-06-27 | `sortedcontainers__sorted_list_core__001` promote 至主榜（batch-1 #5，55/100） |
| 2026-06-27 | `configobj__roundtrip_config_core__001` promote（batch-1 #6，56/100，B 档例外） |
| 2026-06-27 | `croniter__cron_parse_core__001` promote（batch-1 #7，57/100，B 档例外） |
| 2026-06-27 | `websockets__handshake_parse_core__001` promote（batch-1 #8，58/100，B 档例外） |
| 2026-06-27 | `voluptuous__schema_validate_core__001` promote（batch-1 #9，59/100，B 档例外） |
| 2026-06-28 | 第四批 batch-1 promote **20** 题（80→100）：boltons、humanize、isodate、rfc3986、python_box、arrow、bleach、markdown、deepdiff、passlib、h2、referencing、wsproto、ruamel_yaml、parso、phonenumbers、pydantic_settings、chameleon、dynaconf、astroid |
| 2026-06-27 | 第三批 batch-1 promote **10** 题（71→80）：yarl、tabulate、python_dotenv、python_multipart、intervaltree、environs、dataclasses_json、python_dateutil relativedelta、msgpack、pendulum |
| 2026-06-27 | 第二批 batch-1 promote **10** 题（61→70）：bidict、jsonpointer、pathvalidate、email_validator、xmltodict、cachetools、python_frontmatter、cattrs、mako、urllib3_retry |
| 2026-06-27 | `cerberus__schema_validate_core__001` promote（batch-1 #10，60/100，B 档例外） |
| 2026-06-27 | `jsonpath_ng__expression_eval_core__001` promote 至主榜（batch-1 #4，54/100） |
| 2026-06-27 | `python_dateutil__rrule_core__001` promote 至主榜（batch-1 #3，53/100） |

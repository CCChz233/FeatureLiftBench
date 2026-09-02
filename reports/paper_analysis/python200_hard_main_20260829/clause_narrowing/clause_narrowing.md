# Hidden 首败：义务是否已被契约确定

> **Status: AI 初标，非 human gold · 单一模型单次运行**

## 口径

分母为整场主实验中 **Hidden 首败**的 8 题，即 build 与全部可见测试通过、仅隐藏测试失败的运行。Public 首败不计入：那类失败中 Agent 手里就有测试，反映的是未运行或未修复，与契约文本的解释无关。

## 结果

| 义务状态 | 题数 | 含义 |
| --- | ---: | --- |
| `stated` | 2 | 契约已判定：条款或 required_api 足以确定该断言 |
| `scope_open` | 2 | 范围开放：义务已写明，但适用入口/目标未指定 |
| `value_open` | 1 | 取值开放：期望值或异常类型无法从契约推出 |
| `contradicted` | 2 | 契约相反：声明的签名或条款与隐藏断言不相容 |
| `absent` | 1 | 契约未涉及该义务 |

**4/8** 题的义务可从公开契约恢复（`stated` + `scope_open`）。这部分失败不是信息缺失，补充信息不会改善，改进必须作用在 Agent 如何解释与验证义务上。

其余 **4/8** 题无法由契约恢复，属于基准侧缺陷：任何作用于 Agent 的方法改进都无法覆盖，只能改题。这构成本次运行中方法类改进的可达上限。

| 可恢复义务下的 Agent 行为 | 题数 | 含义 |
| --- | ---: | --- |
| `narrowed` | 2 | 窄化：实现满足义务的一个投影，不满足义务本身 |
| `contrary` | 1 | 相反：实现了另一套自洽语义（通常照搬上游） |
| `absent` | 1 | 缺失：完全未实现该义务 |

## 逐题

| 任务 | 义务状态 | Agent 行为 | 依据 |
| --- | --- | --- | --- |
| `aiohttp__url_params_core__hard3_001` | `scope_open` | `narrowed` | B003 只说“Invalid header names raise InvalidHeaderName”，未指定校验点；测试经由 CIMultiDict.__setitem__ 触发，而该成员未在 required_api 声明。提交在 normalize_headers 中做了校验，__setitem__ 未做——义务被收窄到单一入口。 |
| `dateutil__zone_resolver_core__hard3_001` | `scope_open` | `narrowed` | B003 的主语是 ZoneResolver 整体“follows aliases to the canonical zone”，未指定哪些方法须解析别名。提交只在 get 中调用 _resolve，load_zone 直接 name not in tzdata 即抛 UnknownZoneError。 |
| `installer__wheel_record_core__hard3_001` | `contradicted` | `na` | required_api 声明 find_dist_info(names) -> 'str \| None'，即失败时返回 None；隐藏测试要求多个 .dist-info 时 pytest.raises(ValueError)。契约签名与断言方向相反，非 Agent 可恢复。 |
| `pygments__lexer_core__001` | `stated` | `contrary` | B004 原文即“stripall option removes whitespace tokens”，无“首个”等限定，足以判定 all(ttype is not token.Text)。提交照搬上游 pygments（copied_fraction 0.97），上游只剥输入首尾空白。同题 CGVL 运行中 Agent 自报 oracle_source='pygments.lexer.Lexer options (2.15.1)'，即以上游而非条款为准。 |
| `pytest__marker_registry_core__hard3_001` | `value_open` | `na` | B003 只说 check_unknown “warns or raises”，signature 为 -> 'None'，全篇未出现 KeyError。提交抛 UnknownMarkerWarning 与条款相容；隐藏测试要求的具体异常类型不可从契约推出。 |
| `python_decouple__config_repository_core__001` | `stated` | `absent` | B002 明确命名 “.env quoted-value and comment parsing”，两项操作合起来可判定 'Ada Lovelace' # note -> Ada Lovelace。提交两项都未实现，返回原始行。注：契约蕴含审计曾判为 underdetermined（依据是上游不剥行内注释），该判定回答的是另一个问题；此标签为本测量中分歧最大的一条。 |
| `responses__request_matcher_core__hard3_001` | `absent` | `na` | call_history 虽在 required_api 声明为 attribute、B004 说 reset 清空它，但没有任何条款说明未命中的 find 也要写入 call_history。测试要求两次 find（第二次未命中）后长度为 2，该义务契约全无。 |
| `zope_interface__adapter_registry_core__001` | `contradicted` | `na` | required_api 声明 unregister(...) -> bool，而隐藏测试对成功删除的那次调用也断言 not unregister(...)，即要求成功时返回假值（上游隐式返回 None）。提交按 -> bool 在成功路径 return True。契约签名与断言不相容。 |

## 限制

- n=8，单模型单次运行，比例不可外推到其他模型或其他 split。
- 标注为 AI 初标。论文使用前需第二位独立标注者按同一证据包复核，并报告一致性。
- `stated` 与 `scope_open` 的边界依赖对条款措辞的判断，是本测量最主要的分歧来源。

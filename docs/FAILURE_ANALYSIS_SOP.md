# FeatureLiftBench 失败语义标注 SOP

> **Status: current · SOP version: v1 · Last verified: 2026-09-05**  
> **标签与分母的定义**以 [FAILURE_ANALYSIS_PROTOCOL.md](FAILURE_ANALYSIS_PROTOCOL.md) 为准。  
> **本文只规定怎么执行一轮可复现的 5.3 / Finding 3 标注。**  
> 论文章节顺序与可否写 Finding 见 [paper/08_experimental_analysis_chapter.md](paper/08_experimental_analysis_chapter.md)。

Agent 触发：`.agents/skills/featureliftbench-annotate-failures/SKILL.md`。

## 0. 先分清三份文档

| 文档 | 回答 |
| --- | --- |
| Protocol | 标签叫什么、证据最低要求、四个分母、Hidden 脱敏、双人复核 |
| 本文 SOP | 一轮分析按什么顺序做、何时停、什么算出金标、产物放哪 |
| paper/08 §5.3 | Finding 3 什么时候能写进论文 |

不要用 20260829 v1 的 132/200 目录当 freeze v2 输入。不要改 `suite.json`、评测日志或任务包。题目缺陷只记录，不在本轮静默改 freeze。

## 1. 什么时候用这套 SOP

对某个 **已收工 suite** 回答「有包失败为什么失败」时使用。包括：Python-150 / Python-200′ 主表、新模型补跑、抽样复核。

不要用这套 SOP 去：

- 算 Functional Pass 漏斗（那是 5.1–5.2，机械脚本）；
- 标空卷过程原因当语义根因（空卷留在 5.2.1）；
- 从 `run.status` 或评测最后一行自动出饼图。

## 2. 分母（写进报告第一段）

对每个模型单独计数：

| 集合 | 定义 | 进 5.3？ |
| --- | --- | --- |
| Assigned | 该 split 下全部题 | 否（5.1） |
| 空卷 | `submission/` 无文件 | 否（5.2.1） |
| 有包失败 | 有可评测提交且 Functional Pass = 0 | **候选** |
| `benchmark_invalid_candidate` | 公开测试与契约冲突等 | **剔除后再标 Agent 原因** |
| `valid_agent_evidence` | 有包失败且非 infra / 非题目缺陷 / 非证据缺失 | **根因比例分母** |

Functional Pass = `build ∧ public ∧ hidden ∧ isolation`。空提交计失败，但不进 5.3。

约定最小集（论文 5.3）：先 **最强 1–2 个模型的全部有包失败** 精读；其余模型后抽。不要宣称五模型机制，直到后抽完成。

## 3. 三档质量（必须写在报告里）

| 档 | 每条做了什么 | 论文用途 |
| --- | --- | --- |
| **L0 筛查** | 机械首败 + 公开测试 vs `required_api` 缺陷扫描 + 日志摘要包 | 只能出待标表和题目缺陷候选 |
| **L1 精读** | 按 §5 对每条读契约、提交、首败日志，写 primary | `assistant_first_pass`；Finding 3 **暂定** |
| **L2 金标** | 独立人工双审（Protocol §9）：≥20–30% 抽样 + 全部 unknown / 缺陷 / Hidden-only | 才能把根因比例写进主文 |

AI 连做两遍 ≠ 两位独立 reviewer。L0 残差全部标成 `behavior_drift` 再加总成「94% closure」**禁止**。

## 4. 一轮怎么跑

```text
身份核对 → 机械漏斗 → L0 缺陷扫描 → L1 逐条精读 → （可选）轨迹层 → 汇总与 Finding 闸门 → L2 复核
```

### 4.1 身份核对

确认 freeze id、镜像、suite 目录、split（例如只切 Python-150）。写下模型列表。未收工模型不进表。

### 4.2 机械漏斗（不标语义）

用现有 suite 分析脚本生成逐题 `first_failure_stage`、`artifact_fail`、空卷。检查：

- Pro/Flash 一类强模型 Build 是否为 0（若否，先查 infra）；
- Isolation 是否稀有（全表个位数则 packaging 不会是主因）。

产物：`task_results.csv` 或等价表。不要在这一步写 Finding 3。

### 4.3 L0：题目缺陷扫描（先于 Agent 归因）

对每个 **public_failure** 任务：

1. 读 `metadata.json` 的 `public_spec.required_api` 与 `evaluation/behavior_contract.json` 的 public clauses；
2. 读 `public_tests/` 里**第一个失败**的测试函数；
3. 若测试调用了契约未声明的方法/属性/输出标记，标 `task_or_evaluator_defect` + `validity_override=benchmark_invalid_candidate`，**不进 Agent 分母**。

辅助脚本：

```bash
python3 .agents/skills/featureliftbench-annotate-failures/scripts/screen_public_vs_required_api.py \
  <task_id> [--test-name test_...]
```

历史已确认的 v2 冲突类型（发现新的就追加，不回改 freeze）：测试调用未声明 API、公开条款只要求小写而测试还要连字符、测试检查与渲染无关的字面标记。

Hidden-only 失败另走 Protocol §11，不要在 L0 用隐藏断言反推缺陷。

### 4.4 L1：逐条精读（有包失败 ∩ 非缺陷）

**禁止**只看证据包摘要就写 primary。每条至少打开：

1. 首败 gate 日志（只打开这一份 stdout/stderr）；
2. `submission/featurelifted/`（或实际包根）里与失败调用相关的实现；
3. 对应 public clause 文本；Hidden 失败只引用 clause ID，不抄测试名/输入/断言。

然后按 Protocol §5.1 **从上到下停在第一条命中**：

```text
空提交 → 题目/评测缺陷 → 缺导出/成员/必要分支
  → 缺 helper/资源/注册表 → API 在但语义不同
  → 包无法独立暴露 → 轨迹证明定位错误 → unknown
```

对照检查（防残差桶）：

| 若看到 | 不要直接标 | 应先确认 |
| --- | --- | --- |
| `AssertionError` | `behavior_drift` | 实现的是否同一功能？还是 PEP/键名/模块整错（可能是定位，但无轨迹则 `unknown`） |
| `AttributeError` 缺方法 | `behavior_drift` | 该方法是否在 `required_api`？不在则可能是题目缺陷 |
| 空列表 / 空 dict | `dependency_closure` | 读 `load`/`parse`：是缺依赖，还是绑定约定/读了错误字段 |
| AST 上方法 body 为空 | `contract_api_completion` | 是否只是 `abc`/`@overload` stub |
| 两模型同一题 | 复制标签 | 各自读提交；允许 Pro 缺方法、Flash 签名错误这种分叉 |
| Hidden 日志两段 repr 很像 | `behavior_drift` | 分不清就 `unknown` |

`localization`：必须同时有轨迹（读了错误区域 / 没读相关实现）和提交证据。轨迹 `repo_reads=0` 往往是事件解析失败，**不能**据此标定位失败，也**不能**据此宣称定位已解决。OpenHands 主路径动作是 `terminal`/`file_editor`，要用命令字符串和 `action.path` 判断是否读了 `repo/`。

写 `evidence_summary`：一句可观察事实，无心理动词，无 `hidden_tests/`、`test_hidden`、`::test_`。

### 4.5 轨迹层（可选，Finding 3 不依赖）

只有要写过程机制（没读入口、没做 probe、预算耗尽）时才做 Protocol §6 / §8.C。输出侧 `behavior_drift` ≠ 「没理解契约」。

### 4.6 汇总与 Finding 闸门

报告必须同时有：

- 有包失败 n、缺陷剔除 n、有效分母 n；
- primary 计数（含 `unknown`）；
- **证据分层表**（L0/L1/L2 各覆盖多少条）；
- 闭合类定义：`contract_api_completion` + `dependency_closure` + **经精读确认**的一部分 `behavior_drift`。

**可以写 Finding 3 当且仅当：**

1. 有效分母上的标签主要来自 L1 精读，不是 L0 残差；
2. 闭合类明显多于 `localization`（且 localization 不是「没标」）；
3. 不是「缺包」故事（Build 已过的有包失败）；
4. `unknown` 若高，正文写 uncoded fraction，不为饼图消掉。

否则 5.3 只报分层事实，Finding 3 标暂定或不写。

### 4.7 L2 复核

按 Protocol §9。未做则 `independent_human_review=false`，`review_status=assistant_first_pass`。

## 5. 单条记录字段

与 Protocol §7 对齐，并固定增加：

```text
validity_override
validity_reason
independent_human_review
```

`contract_clause_ids` 形如 `B001;B003`（无空格）。`task_or_evaluator_defect` 必须配 `benchmark_invalid_candidate`。空卷若进入标注表，只能是 `agent_process_non_delivery`。

校验：

```bash
python3 .agents/skills/featureliftbench-annotate-failures/scripts/validate_annotation_csv.py \
  path/to/failure_root_cause_annotations.csv
```

有单模型 `failure_audit.csv` 时，也可用 `harness/scripts/analyze_failure_taxonomy.py`。

## 6. 产物布局

```text
reports/paper_analysis/<split>_..._<YYYYMMDD>/
  README.md                              # 5.1–5.6；5.3 必须含证据分层
  task_results.csv                       # 机械
  failure_root_cause_annotations.csv     # 语义
  f3_annotation_summary.json             # 计数
  f3_evidence_packets.json               # 可选 L0 包；不得当 L1 完成证明
```

CSV 与 JSON 可经脚本生成，但 **primary 必须来自 L1 人工/助手精读表**，不能从 packets 规则引擎灌出来。

## 7. 明确禁止

1. 用 Public/Hidden 失败人数命名 contract-closure。
2. 把 L0 残差全部叫做 `behavior_drift` 再加总。
3. 把 `localization=0`（未标）写成定位已解决。
4. 对外写出 Hidden 测试名、输入、断言。
5. 把 Qwen TVE 空卷改写成「有效分母变小、准确率变高」。
6. 用 `run.status` 替代 Functional Pass。
7. 改 freeze / 主榜题包来「修」本轮缺陷；缺陷记入候选，下次 freeze 再修。
8. 未收工模型进主表或进 Finding 3 分母。

## 8. 当前仓库指针

- Protocol：[FAILURE_ANALYSIS_PROTOCOL.md](FAILURE_ANALYSIS_PROTOCOL.md)
- 词表：[paper/05_failure_taxonomy.md](paper/05_failure_taxonomy.md)
- 章节闸门：[paper/08_experimental_analysis_chapter.md](paper/08_experimental_analysis_chapter.md)
- 机械分析示例：`reports/paper_analysis/python150_prime_v2_analysis_20260905/`
- 该目录的 F3 标注截至 2026-09-06 为 **L1 助手精读 + 轨迹/过程筛（Pro+Flash 普查）** 与 **Luna/Qwen/OSS 分层后抽**，不是 L2 金标；后抽不得并进普查分母。

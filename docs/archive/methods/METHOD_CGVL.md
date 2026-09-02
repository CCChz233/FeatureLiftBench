# Contract-Guided Verification Loop（CGVL）

> **Status: archived · Last verified: 2026-09-02**
> 本文件是 **CGVL** 的唯一规范。不是 Official Main，数字不进 Python-200' 主表。
> CGVL-v1 的 Flash-12 已 **Kill**；v2 只允许重跑同一 12 题筛选。不要叠 Public-feedback、Spec-adversarial、TFL、2M cap，也不要扩到 200。

## 与已 Kill 臂的差别

| 臂 | 谁写槽位 | 怎样算测过 |
| --- | --- | --- |
| Spec-adversarial | Harness：每条 Bxxx 一个空 stub | `FILLED` 且函数返回即可 |
| TFL / Self-Contract | 模型自己出题 | 自选用例冻结 |
| Pre-submit audit | 无槽位 | 自然语言清单 |
| **CGVL-v2** | Harness：每条功能 Bxxx 一个紧凑闭合格；另展开 union、pairwise、状态保护与未被 Bxxx 覆盖的异常 | 精确调用 Harness 给定公开入口；执行 actual/expected 断言和反例；隔离扫描通过；checker 红由运行时拒绝 finish |

每条功能 Bxxx 必有一个完整语义格；pairwise 只额外展开失败分析里出现过的显式维度（quote×comment、alias×load_zone、brace×factor），不会把条款里每一个 "and" 都拆成格子。相同参数的 union arms 合并到一个格子，非 callable 的 module/attribute 只做导入面检查，不再消耗 Agent 格子。

不要让 Agent 从 TASK 自由生成 JSON 契约表。那会把同一盲点写进验收，重复 TFL。

独立验证器仍是 **机械 checker**，不是第二份同模型 LLM。v2 使用精确导入别名/实例方法调用解析、显式 Python `assert`、结构化 actual/expected、checker 重算的反例区分性、union 覆盖清单、失败前后状态相等检查和 forbidden-import 扫描。LLM verifier 不进本筛选臂。

## 定义

同一 128k / 120-step / No-Hint / 无 2M Main 信封。只改 workspace：

- `cgvl_matrix.json`：Harness 生成的 v2 紧凑行为矩阵，Agent 不得增删行
- `cgvl_cells/C*.py`：按格填公开入口探针、断言与反例
- `./run_cgvl_check.py`：语义、union、状态和隔离证据门禁
- `cgvl_evidence.json`：闭合表
- `agent/cgvl_finish_gate.json`：运行时最终门禁结果；红灯时 OpenHands wrapper 返回 `cgvl_gate_failed`

| 维度 | Main | CGVL |
| --- | --- | --- |
| Prompt | `standard` | 同左 + CGVL 附录 |
| `public_tests/` / Hidden | 不挂载 | 不挂载 |
| Runtime `ablation_arm` | `main` | `cgvl` |

机器可读冻结：[`harness/config/methods/cgvl.json`](../../../harness/config/methods/cgvl.json)。

## 切片与 Kill

12 道二审 **模型主因**（含 pylint/typer 预算题，**不含** Cookiecutter/Decorator/Installer/Yamale）：

v1 冻结清单：[`harness/config/experiments/cgvl_model_primary12_v1.txt`](../../../harness/config/experiments/cgvl_model_primary12_v1.txt)。

v2 重跑清单（题目不变）：[`harness/config/experiments/cgvl_model_primary12_v2.txt`](../../../harness/config/experiments/cgvl_model_primary12_v2.txt)。

同日必须重跑这 12 题 Main。Alembic 若 `public.stdout` 首败是未声明 `is_merge_point`，从切片拿掉后再记分。

| 结果 | 动作 |
| --- | --- |
| Functional 0→1 **&lt; 3/12**，或 Hidden 子集（aiohttp / pygments / decouple / zope）0→1 = **0** | **Kill** |
| 只抬 Public、Hidden 不动 | Kill，那是 RQ6 故事 |
| Hidden ≥2 翻盘且格子对得上首败条款 | 可写机制，仍不进主表 |

## CGVL-v1 筛选结果（Kill，历史结果）

套件：`experiments/methods/ablation/cgvl-model-primary12-deepseek-v4-flash-20260901-175148/`。
模型 DeepSeek V4 Flash；对照为 20260829 Flash Main（切片 12 题当时全败）。未重跑同日 Main。

| 指标 | 结果 |
| --- | --- |
| Functional | **2/12**（pylint、importlib_resources） |
| Hidden 子集 aiohttp / pygments / decouple / zope | Functional 0→1 = **0** |
| checker `ok=true` | 已评完的格子几乎全绿 |

两条 Kill 线都触发。checker 绿不能代替 Hidden。不要扩面。

## v1 失效原因与 v2 对应修复

| v1 问题 | v2 修复 | 预期可观测指标 |
| --- | --- | --- |
| 只展开少数特殊语义，完整 Bxxx 可能没有格子 | 每条非 API-surface Bxxx 强制一个完整语义格 | `behavior_id` 覆盖全部功能 Bxxx |
| Pygments 等返回布尔 flags 也会变绿 | 必须执行 `assert`，并记录通过的 actual/expected | `assertion_records > 0` |
| `KILLS_MUTANTS` 只是声明 | 返回 observed 与 mutant_expected；checker 重算是否可区分 | `counterexamples_killed > 0` |
| 只按方法名判断公开入口，可能误认同名调用 | 解析 featurelifted import alias、构造实例和精确方法路径 | `public_entries_called` 为精确路径 |
| Typer / Zope 功能正确但隔离失败 | checker 在 finish 前扫描公开 forbidden imports | `isolation_ok=true` |
| prompt 说红灯不能 finish，但运行时未实现 | wrapper 结束时重新执行 checker，红灯返回 `cgvl_gate_failed` | `runtime_finish_gate_ok=true` |
| 入口/属性格过多，挤占语义探索预算 | module/attribute 只做自动导入检查；union arms 合并 | 同 12 题矩阵由 v1 161 格降至 v2 121 格 |

v2 仍不自动发明 `public_spec` 未写出的具体 oracle。Agent 必须从 TASK 与仓库实现中构造公开场景；因此 v2 是否有效只能由同日配对筛选决定。

## 怎么跑

先跑 Hidden-4 工程烟雾；它只检查 v2 是否能驱动 Agent 和门禁，不作为方法效果数字：

```bash
./scripts/run_benchmark.sh --benchmark python200_hard --agent openhands --method cgvl \
  --task-file harness/config/experiments/cgvl_hidden4_v2_smoke.txt
```

四题均能生成 `assertion_records`、`counterexamples_killed`、`isolation_ok=true` 和 `runtime_finish_gate_ok=true` 后，再跑同日配对 12 题：

```bash
./scripts/run_benchmark.sh --benchmark python200_hard --agent openhands --method main \
  --task-file harness/config/experiments/cgvl_model_primary12_v2.txt
./scripts/run_benchmark.sh --benchmark python200_hard --agent openhands --method cgvl \
  --task-file harness/config/experiments/cgvl_model_primary12_v2.txt
```

检查矩阵（不跑 Agent）：

```bash
PYTHONPATH=harness python3.12 -m featureliftbench.cgvl \
  benchmark/python200_hard_tasks/scrapy__item_loader_core__hard3_001
```

## 论文可用句（筛选通过后）

> 通过 Harness 展开的契约覆盖矩阵、必须走公开入口的区分性探针，以及证据化完成门禁，减少跨模块功能抽取中的错误契约闭合。

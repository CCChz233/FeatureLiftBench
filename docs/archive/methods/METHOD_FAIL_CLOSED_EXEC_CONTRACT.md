# Fail-Closed Execution Contract（FCEC）

> **Documentation status: archived · Indexed: 2026-08-04**

**状态：** 已实现；open dev-6 no-API preflight 为 **0/6 admission**，暂不调用模型。

## 目标

FCEC 只保留 Exec-Contract 中最小且可审计的部分：

1. 从 TASK/public_spec 选一个上游测试文件；
2. 在隔离环境中按项目元数据安装 runtime、build 与 test dependencies；
3. 只 trace `source_entrypoints` 对应源文件；
4. 生成 Required API、published signature、public clause 和动态证据的 closure capsule；
5. 只有证据硬门通过时才给实现 Agent；否则删除全部方法产物并回退 Main；
6. 只进行一次实现 Agent 调用，不做 PDR 式第二轮自由探针/修复。

## 硬门

进入 FCEC implementation 必须同时满足：

- selected upstream pytest exit 0；
- 至少一个 relevant trace event，且 trace quality 为 high；
- Required API closure 完整；
- 所有 published signatures 被机械覆盖；
- 至少一个动态观察绑定到公开 TASK clause；
- 至少一个真正可执行的 behavioral assertion。

构造器只算 API/signature closure，不算 behavioral assertion。实例方法的单次
call trace 不包含 receiver pre-state，不能在新对象上伪造 replay；FCEC 因此
不接受无状态快照生成的实例方法合约。

## Dependency doctor

doctor 使用且只使用仓库派生元数据：

- PEP 621 project dependencies / extras；
- PEP 735 dependency groups；
- Poetry test group，缺失时才回退 legacy dev group；
- build-system requirements；
- monorepo sibling projects；
- pytest minversion；
- pytest addopts 中显式 `-p` 插件。

报告/并行类 addopts 被清空，必要 `-p` 插件被显式恢复，避免 coverage 与
`sys.settrace` 抢占同一 tracing hook。依赖环境位于 Docker tmpfs，不写回
benchmark workspace；安装失败不再 `|| true`。

## 动态证据约束

- trace 在 import pytest 后开启，避免框架初始化耗尽事件预算；
- watch scope 优先使用 source entrypoint 精确文件；
- vendor、class-body、无关 dunder 被过滤；
- `self` / `cls` 不做 repr，只记录 owner 与显式参数；
- replay 只能落到 TASK Required API；
- 参数名、默认形状和返回值必须与 published signature 兼容；
- 不把 upstream inferred helpers 变成新的 benchmark 要求；
- 不读取 public/hidden/formal evaluator 结果。

## Dev-6 preflight

完整证据见
`experiments/methods/fcec_dev6_20260731/PREFLIGHT_RESULTS.json`。

| Task | upstream pytest | useful trace | clause-bound | executable behavior | admission |
| --- | ---: | ---: | ---: | ---: | --- |
| Pyramid | pass | 4,999 | 2 | 0 | fallback |
| Pytest | pass | 5,000 | 0 | 0 | fallback |
| setuptools-scm | pass | 0 | 0 | 0 | fallback |
| Poetry Core | pass | 3,324 | 3 | 0 | fallback |
| returns | pass | 11 | 4 | 0 | fallback |
| Parsel | pass | 4,745 | 4 | 0 | fallback |

这不是 collector 失败：六题 selected upstream pytest 已 **6/6 通过**。失败
发生在更深的一层——这些 FLB 任务通常把上游状态机重新封装、重命名或改签名，
raw call replay 无法自动重建 receiver pre-state，也无法诚实跨越 adapter
边界。若放宽门，会重新产生“闸门绿、故事错”的假进展。

## 结论

FCEC 修好了 clean3 的依赖与假绿基础设施，但作为提升 Functional 的方法，
当前形式 **NO-GO**：dev-6 上 0/6 能获得非空、可执行、clause-bound 的行为
合约。运行模型只会得到 6 个 Main fallback，不能形成方法证据。

下一步若继续动态分析，只应研究一个更小的新原语：
**state-transition capture**（显式记录 receiver 的可投影 pre/post state 与
触发它的 upstream test node），而不是继续增加自由 probe、批评轮或第二个
Agent。该原语必须先在 dev tasks 上证明能重建一个真实状态场景，再画新的
held-out cohort。

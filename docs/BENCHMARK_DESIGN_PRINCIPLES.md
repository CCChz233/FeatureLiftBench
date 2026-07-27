# FeatureLiftBench 设计原则

**状态：** Full-Repository / No-Hint Main 的权威目标规范

**版本：** hardened v3（2026-07-27）
**适用范围：** Python External Main；历史结果按实际 source-context 单列

## 一句话定义

> FeatureLiftBench 给 Agent 一个完整、固定版本的真实 Python 仓库和完整的
> 目标功能契约，要求其自主定位、理解、抽取并验证目标功能，最终提交独立、
> 行为完整且尽量紧凑的功能模块。

论文结论的默认适用范围是 **real-world Python library repositories**。
若要外推到应用、服务或任意软件仓库，必须另建并单独报告扩展 split。

## Main 的信息边界

| 阶段 | 内容 |
| --- | --- |
| Agent 可见 | 完整 pinned upstream repository、完整公开功能契约、提交 API 与包布局、依赖锁、允许的运行环境 |
| Agent 不可见 | source entrypoints、源文件/符号/行号提示、依赖闭包、reference、Benchmark public/hidden tests、evaluation 配置、难度与纠缠提示 |
| Agent 输出 | `submission/featurelifted/` 下的独立可安装功能包 |
| 交卷后评测 | Build、public、hidden、isolation/forbidden，以及独立报告的 compactness |

上游仓库原有的 tests、docs、examples、配置和资源属于完整仓库的一部分，
在 Main 中保持可见。Benchmark 自建的 public 与 hidden tests 均只在交卷后运行。

## 八条设计原则

### 1. 完整仓库输入

Main 使用固定 revision 的完整 upstream tracked source tree，不按目标功能裁剪。
允许排除的只能是对所有任务一致、与目标语义无关的内容，例如 `.git/`、
cache、虚拟环境、构建产物和未跟踪文件。

完整纳入、revision resolution、tree/archive digest 和 registry 规则以
[FULL_REPOSITORY_SOURCE_POLICY.md](FULL_REPOSITORY_SOURCE_POLICY.md) 为准。

### 2. 完整公开契约

任务必须公开说明：

- 目标功能及合理使用场景；
- 必需提交 API、签名、默认值、成员和异常；
- 输入、输出、边界、状态和可观察行为；
- exclusions、forbidden imports/paths 和运行约束。

Hidden tests 可以加深样例、组合和边界覆盖，但不能增加公开契约之外的
API、行为类别或环境假设。

### 3. Main 不提供源码定位提示

Main 不提供 source entrypoints、源文件路径、上游符号名、行号、调用链或
依赖文件清单。Agent 必须利用功能描述、目标提交 API 和完整仓库自行定位。

目标**提交侧** API 不是定位提示：它用于统一交付接口，不应包含上游内部路径。

### 4. Agent 自主完成全过程

Agent 自主完成：

```text
理解契约 → 搜索仓库 → 定位实现 → 发现依赖 → 利用/构造测试
→ 解耦与封装 → 自行验证 → 提交
```

Benchmark 不强制特定搜索、推理、测试或停止流程。

### 5. 提交必须独立运行

提交不得在运行时：

- import 原上游包；
- 读取原仓库路径或 evaluator 文件；
- 使用网络、私有服务或未声明环境；
- 依赖未在任务中允许的第三方包。

Functional container 只接收 submission、source-free evaluation capsule、
允许 wheels、harness 和输出目录；原仓、source registry/archive、
reference/oracle 与 compactness registry 均不得挂载。Compactness/provenance
在 container 退出后的只读 metrics stage 计算，该阶段不得执行 submission。

### 6. 功能正确性是主指标

单题 Functional Pass 定义为：

```text
BuildPass
∧ PublicTestsPass
∧ HiddenTestsPass
∧ IsolationPass
```

论文 headline 报告一次独立运行的 evaluator **Functional Pass@1**。
Agent 工作流的 `run.status`、基础设施失败和缺失提交必须单独报告，不能代替
或悄悄改变 Functional Pass@1。

### 7. 紧凑性是独立次要指标

Compactness 只在功能结果之外独立报告，并相对 frozen reference
implementation 或经审核的 reference support set 计算。完整 upstream
repository LOC 不能作为紧凑性分母，也不应把功能正确性与紧凑性合成唯一
headline 分数。

### 8. 实验条件必须显式分层

| 条件 | 仓库上下文 | 定位提示 | Benchmark tests |
| --- | --- | --- | --- |
| **Full-Repository / No-Hint Main** | 完整 | 无 | 全盲 |
| Entrypoint-Hint | 完整 | 有 | 全盲 |
| Public-Feedback | 完整 | 无 | public 可见 |
| Pruned-Context | 裁剪 | 按实验定义 | 全盲 |
| Short-Prompt | 完整 | 无 | 全盲；仅压缩文案 |

每个结果必须记录 task/spec/source/evaluator/environment freeze。不同 source
context、提示可见性或 evaluator 可见性的结果不得混报。

## 版本边界

- 当前历史 Python-150 结果属于 `mixed_snapshot_v1`，并且 Agent-visible
  metadata 含 source entrypoints；它们可保留为 mixed/pruned-context
  条件的证据。
- 当前完整仓库 materialization、Main 定位提示移除、reference-relative
  compactness、source-free evaluator、Oracle 重验和 provenance freeze 已
  完成 150/150；原 `vibe_app` 7 题已移入独立 Curated split。

当前逐题证据见
[v3_main_readiness.md](../reports/audits/v3_main_readiness.md)。

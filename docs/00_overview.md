# FeatureLiftBench Overview

**整体思路（优先阅读）：** [BENCHMARK_DESIGN.md](BENCHMARK_DESIGN.md)  
**出题宪法：** [TASK_DESIGN_RULES.md](TASK_DESIGN_RULES.md)  
**研究入口：** [CURRENT_RESEARCH.md](CURRENT_RESEARCH.md)

## Benchmark Goal

FeatureLiftBench evaluates whether coding agents can **decouple a target feature** from a real repository and produce a **behavior-complete, independently installable, and compact** module, given **source entrypoints** and a **public functional contract**.

目标功能可带不同类型的仓库级耦合；不要求整个 upstream「处处高度纠缠」。紧凑性由 `extraction_ratio` **代理**；评测**不声称**证明唯一最小闭包。Benchmark **不规定** Agent 的探索/测试/停止流程。

论文路线：**Benchmark 基础（规格/门禁）+ 方法研究（Contract/API closure recovery）**。当前工程优先冻结评测基础；方法在合规任务上验证。

## Core Difference from SWE-bench

| Dimension | SWE-bench style | FeatureLiftBench |
|---|---|---|
| Input | Issue + repo | Entrypoints + public contract + repo snapshot |
| Output | Patch to original repo | Standalone package under `submission/` |
| Main skill | Fix in place | Extract, decouple, package, preserve behavior |
| Runtime | Original repo remains target | Must run without importing original package |
| Anti-gaming | Tests | Public+hidden, forbidden import, compactness |

## Information Layers

- **Agent-visible:** `public_spec` → generated TASK, `repo/` including retained upstream tests/docs/examples, lockfiles.  
- **Agent-hidden in Main:** Benchmark `public_tests/`, `hidden_tests/`,
  `evaluation_spec`, entanglement analysis tags, reference.  
- **Post-submit eval:** always both private evaluator tiers + isolation + compactness.

详见 [EXPERIMENT_ARMS.md](EXPERIMENT_ARMS.md)。

## Current Scope

- Python main: **150** tasks in `benchmark/tasks/` — **150 compliant** / **0 legacy**（2026-07-24）。见 [CONSTITUTION_MIGRATION.md](CONSTITUTION_MIGRATION.md)。
- Go: calibration / seed under `benchmark/go/`（非 paper-ready main）。  
- 状态：[STATUS.md](STATUS.md)

## Expected Output

Python（典型）：

```text
submission/
  featurelifted/
    ...
```

（`pyproject.toml` 非必须；evaluator 常经 `PYTHONPATH` 导入。）

Go：`submission/go.mod` + 源码。不变量：独立于原仓运行时，暴露 `required_api`。

## Evaluation Philosophy

1. **Functional gate：** build/install、API、public、hidden、forbidden/isolation。  
2. **Compactness proxy：** `final_score = gate × max(0, 1 − extraction_ratio)`。  

Public 与 hidden **共享同一公开行为契约**；hidden 可加深覆盖，不得新增未声明义务（宪法 §4）。

## Current Priority

规格迁移与 validate 已完成 **150/150**。当前优先独立人工 paper-gold 审核与新合规 core-100 模型校准；见 [CONSTITUTION_MIGRATION.md](CONSTITUTION_MIGRATION.md) · [CURRENT_RESEARCH.md](CURRENT_RESEARCH.md)。

# FeatureLift Task Definition

**权威细则：** [TASK_DESIGN_RULES.md](TASK_DESIGN_RULES.md)  
**整体思路：** [BENCHMARK_DESIGN.md](BENCHMARK_DESIGN.md)

## Task Summary

A FeatureLift task asks an agent to extract one reusable feature from a repository snapshot and package it as an independent library. The target behavior already exists in the source; the agent must **decouple** it into a **behavior-complete, independently installable, compact** package under the **public functional contract** (`required_api` surface, behaviors, exclusions, forbidden) and given **source entrypoints**.

评测**不要求**证明唯一最小闭包；**不规定** Agent 工作流。论文保留 Benchmark + 方法双线：先规格合规，再在合规题上验证契约恢复方法。

## Input (Agent-visible)

逻辑输入（**compliant 题：** 由 `public_spec` 生成唯一 TASK；**legacy 题：** 仍可能双轨，见 [CONSTITUTION_MIGRATION.md](CONSTITUTION_MIGRATION.md)）：

- Source repository snapshot (`repo/`)，pinned commit  
- Generated feature specification / TASK（含 `required_api`、behaviors、exclusions、forbidden、entrypoints）  
- Packaging / output layout requirements under `submission/`  
- Redacted public metadata（legacy harness prompt 仍可能含 entanglement 等；compliant 用 `render(public_spec)`）  
- **Repository evidence:** upstream tests/docs/examples retained inside `repo/` when available  
- Dependency lock / language environment files as applicable  

**Not agent-visible in Main:** Benchmark `public_tests/`, `hidden_tests/`,
`evaluation_spec`, entanglement analysis fields, reference/oracle internals.

**Public-feedback arm:** explicit ablation that mounts the basic evaluator tier.
The default Main remains test-blind. See [EXPERIMENT_ARMS.md](EXPERIMENT_ARMS.md).

## Output

Standalone package under `submission/` (Python: typically `submission/featurelifted/`). Must expose every `required_api` symbol and must not import the original package or rely on `repo/` at runtime.

## Constraints

- No original-package imports; no path/symlink leakage to source or hidden/eval artifacts  
- No network (unless a future task explicitly allows and documents reproducibility)  
- Must satisfy evaluator gates including **hidden** tests  
- Prefer compact extraction (scored via compactness proxy)  
- Must not learn hidden-only behavior by reading hidden/eval files  

## API contract shape

- `required_api`: must all exist; hidden must cover each  
- `optional_api`: may exist; hidden must not require  
- public/hidden may only use declared API  

Do **not** treat “target API” as an optional export superset.

## Behaviors

Each required behavior is an observable obligation (precondition · action · observable result). Public and hidden tests map to behavior IDs; every required behavior must be covered by at least one hidden test.

## Functional Success

Binary gate (implementation-defined conjuncts), typically including: clean install/import/build, public tests, hidden tests, forbidden/isolation checks. Compactness is separate and combined into `final_score`.

## Difference from Issue Repair / Greenfield / Completion

- **Issue repair:** patches the original repo; FeatureLift emits a new package.  
- **Greenfield generation:** can ignore upstream; FeatureLift must preserve upstream-observable behavior under the public contract.  
- **Completion:** local prediction; FeatureLift is repository-level decoupling under explicit API/behavior obligations.

## Stable Contract Across Languages

Python and Go share task semantics, RQs, and scoring philosophy; packaging differs. Spec visibility rules in TASK_DESIGN_RULES apply to all splits unless a language doc explicitly narrows an engineering detail (not the scientific contract).

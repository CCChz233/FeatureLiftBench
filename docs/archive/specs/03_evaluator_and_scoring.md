# Evaluator and Scoring

> **Documentation status: archived · Last verified: 2026-08-04**
> 已由 [EVALUATION.md](../../EVALUATION.md) 替代，仅供历史复查。

契约与可见性以 [TASK_DESIGN_RULES.md](../../TASK_DESIGN_RULES.md) 为准；实验臂
以 [EXPERIMENT_ARMS.md](EXPERIMENT_ARMS.md) 为准。

## 原则

- 唯一 headline：evaluator Functional Pass@1；
- compactness 是 reference-relative 次指标，不与功能门相乘；
- Agent completion、step/context limit、token 和 infra failure 单列；
- public/hidden 都是 submission 后运行的 evaluator tiers；
- 完整 upstream LOC 不作为 compactness 分母。

## Main pipeline

1. 校验 task、active freeze 和 canonical source mapping。
2. 从 immutable archive 物化完整 pinned source tree。
3. 构造只含 `TASK.md`、完整 source、锁定依赖和空 `submission/` 的
   No-Hint workspace。
4. 在 agent Docker 中运行一次 Agent。
5. 收集 `submission/`；不把原仓库加入 runtime `PYTHONPATH`。
6. 为功能评测构造 source-free capsule，只复制 sanitized metadata、
   dependency lock、public/hidden tests、forbidden import list 和 harness。
7. 在 functional eval Docker 中只挂载 capsule、submission、允许 wheels、
   harness 和输出目录；不挂载 task `repo/`、source archives/registry、
   reference/oracle 或 compactness registry。
8. 在 `--network none`、只读 rootfs、`cap-drop ALL` 环境中运行 build、
   private public tier、private hidden tier和结构化 isolation gates；运行时
   audit hook 记录并阻断 submission 发起的 subprocess、socket、DNS、HTTP、
   evaluator-private path 和 forbidden upstream import。
9. functional container 退出后，trusted metrics stage 只读分析 submission、
   source/reference；该阶段不 import、安装或执行 submission。
10. 写逐题 `result.json`、logs 和 suite index。metrics 失败不改变
    FunctionalPass，但结果标为 `compactness_status != ok`，不得进入论文表。

## Functional Pass

实现位于 `harness/featureliftbench/scoring.py`：

```text
FunctionalPass =
  BuildPass
  ∧ PublicTestsPass
  ∧ HiddenTestsPass
  ∧ IsolationPass
```

- `BuildPass`：submission 在干净环境中可安装或导入；
- `PublicTestsPass`：基础 regression layer 全过；
- `HiddenTestsPass`：更深边界/组合行为 layer 全过；
- `IsolationPass`：forbidden imports/dependencies、runtime audit、
  runtime import origin、source filesystem absence、network disabled、
  submission location 和 functional mount allowlist 全部通过。

兼容字段 `test_pass = public_tests_pass ∧ hidden_tests_pass`，
`original_import_pass = isolation_pass`；`final_score = functional_gate`。

`functional_gate` 为 0/1。一次完整 task attempt 对应一次 Pass@1 观察。

OpenHands `run.status` 还会编码 Agent 是否正常结束工作流。若 Agent
step-limit 后留下 evaluator 可通过的 submission：

- evaluator Functional Pass = pass；
- Agent completion = fail；
- step-limit = true。

三者必须分别报告，不能用 `run.status` 覆盖 benchmark correctness。

## Compactness

每题从 frozen reference registry 获取 reference LOC/file measurements，
然后报告：

```text
reference_relative_loc_ratio = submitted_loc / reference_loc
compactness_score = min(1, reference_loc / submitted_loc)
```

以及：

- submitted/reference file count；
- copied file count；
- copied LOC/fraction；
- runtime/external dependency count；
- unapproved external dependencies；
- path leakage / forbidden source import；
- excess copied LOC（仅 closure file gold 完整时）；
- compactness class。

Reference 是一个可行紧凑实现，不是唯一最小解。因此这些值用于比较和诊断，
不能解释为数学最小性证明。

兼容字段：

- `extraction_ratio` = `reference_relative_loc_ratio`；
- `final_score` = `functional_gate`。

它们不再使用完整源仓库 LOC，也不再形成
`functional × (1 - extraction_ratio)` composite。

## 逐题结果

当前 Python evaluator 的主要字段：

```json
{
  "task_id": "example__feature_core__001",
  "status": "passed",
  "build_pass": true,
  "public_tests_pass": true,
  "hidden_tests_pass": true,
  "isolation_pass": true,
  "test_pass": true,
  "original_import_pass": true,
  "evaluation_capsule_digest": "<sha256>",
  "compactness_status": "ok",
  "isolation": {
    "forbidden_imports_pass": true,
    "forbidden_dependencies_pass": true,
    "forbidden_runtime_capabilities_pass": true,
    "runtime_import_origin_pass": true,
    "source_filesystem_absent": true,
    "network_disabled": true,
    "submission_location_pass": true,
    "mount_allowlist_pass": true,
    "verification_mode": "docker_functional_capsule_v1"
  },
  "public_tests": {"passed": true},
  "hidden_tests": {"passed": true},
  "metrics": {
    "loc": 500,
    "reference_loc": 400
  },
  "compactness": {
    "status": "ok",
    "reference_loc": 400,
    "submitted_loc": 500,
    "reference_file_count": 4,
    "submitted_file_count": 5,
    "copied_loc": 250,
    "copied_fraction": 0.5,
    "runtime_dependency_count": 2
  },
  "scores": {
    "functional_gate": 1.0,
    "extraction_ratio": 1.25,
    "reference_relative_loc_ratio": 1.25,
    "compactness_score": 0.8,
    "final_score": 1.0
  }
}
```

实际 paper table 必须读取当前 JSON，不应依赖这段示例字段的完整性。

## Suite metrics

### Headline

- assigned/completed；
- Functional Pass@1；
- pass rate 和 uncertainty；
- paired task-level deltas。

### Correctness funnel

- build/import；
- public；
- hidden；
- isolation；
- agent/evaluator mismatch；
- infra/context/step failures。

### Compactness and cost

- reference-relative LOC/file/copy/dependency vector；
- tokens、API calls、steps；
- agent/eval/wall-clock time；
- copy-heavy functional passes。

## Scoring invariants

- Hidden 是功能成功的一部分，不是 bonus。
- Hidden 不得引入公开契约之外的新义务。
- Compactness 不得让小而错误的 submission 获得功能分。
- Copy-all 可以 functional pass，但 compactness 必须很差。
- 不同 source/visibility/attempt 条件不得合并成同一 leaderboard。
- Python 和未来 Go 可以使用不同 build adapters，但概念指标必须同名。

已知限制见 [limitations.md](../../paper/limitations.md)，当前状态见
[STATUS.md](../../STATUS.md)。

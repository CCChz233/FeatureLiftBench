# Incremental Task Rules

> **Documentation status: current · Last verified: 2026-08-04**

本文规定新任务进入 Python Main 的生命周期。出题宪法见
[TASK_DESIGN_RULES.md](../TASK_DESIGN_RULES.md)，package schema 见
[06_task_schema.md](06_task_schema.md)。

## Principles

1. 新任务先进入 `benchmark/staging/` 或 `benchmark/batch3_pilot/`，不直接写
   `benchmark/tasks/`。
2. 来源必须先进入 canonical source registry；Main 不接受 target-aware
   source slice。
3. `public_spec` 是唯一公开契约，`TASK.md` 由它生成。
4. public/hidden/evaluation/reference 都是 private evaluator assets。
5. promotion 依赖可执行证据，不依赖文档宣称。
6. 独立人工审核不是硬门禁；若使用人工复核，按真实 provenance 报告。
7. 任务或 source 变化后必须生成新的 benchmark freeze。

## Lifecycle

| Status | Meaning |
| --- | --- |
| `design_only` | 功能和契约草案；尚不可运行 |
| `materialized_candidate` | source、task package、tests、reference 已存在 |
| `validated_candidate` | source/contract/reference/isolation gates 通过 |
| `hard_candidate` | 设计难度和 calibration evidence 已记录 |
| `main` | 已 promotion 且进入 active freeze |
| `blocked` | 无法在不伪造来源/行为/结果的情况下继续 |
| `sanity` | harness smoke；永不进入 leaderboard |
| `archived` | 退休或被替代 |

允许路径：

```text
design_only
  → materialized_candidate
  → validated_candidate
  → hard_candidate
  → main

any candidate → blocked | archived
```

Main membership 由目录、manifest 和 benchmark freeze 共同定义。历史任务
metadata 可没有 `status=main`；新任务应显式记录。

## Landing zones

| Work | Location |
| --- | --- |
| New Python task | local `benchmark/staging/<task_id>/` |
| Larger pilot/calibration | local `benchmark/batch3_pilot/<task_id>/` |
| Python smoke | `benchmark/sanity/<task_id>/` |
| Go calibration | `benchmark/go/tasks/<task_id>/` |
| Oracle/reference | `benchmark/submissions/<task_id>/` |
| Canonical source metadata | `benchmark/sources/registry.json` |
| Source archive cache | `benchmark/sources/archives/`（ignored） |

## Promotion gates

### 1. Selection gate

- 真实可复用 feature；
- extraction，不是 bug fixing 或 prompt-only toy rewrite；
- behavior 可离线确定性测试；
- 依赖、资源和时间预算有界；
- 许可证和再分发方案明确；
- 记录 candidate 来源、纳入/排除原因和淘汰状态。

### 2. Source gate

- canonical URL/source kind；
- immutable resolved revision；
- source/archive digest；
- license path；
- full tracked tree 或 policy 允许的 curated source tree；
- 统一、非目标相关的 exclusion policy；
- upstream tests/docs/examples/config/resources 被保留；
- 同 repo+revision 共享 digest；
- registry `status=ready`。

### 3. Contract gate

- `required_api` surface 完整；
- behaviors 可观察、编号、可测试；
- exclusions/forbidden/isolation 明确；
- `evaluation_spec` 双向映射；
- hidden 不引入新 API/behavior；
- `TASK.md` hash 与 `public_spec` 一致；
- Main workspace 无 entrypoints、paths、symbols、lines 或 closure hints。

### 4. Package gate

Python candidate 至少有：

```text
metadata.json
TASK.md
requirements.lock
repo/                    # staging provenance; not canonical v3 source proof
public_tests/
hidden_tests/
evaluation/
```

Tests import `featurelifted`，不 import `submission` 或原项目包。

### 5. Reference gate

- reference/oracle 在干净环境通过 public+hidden；
- repeated run deterministic；
- reference 不依赖 Agent 不可获得的 runtime service；
- compactness reference record 已生成；
- naive/stub 失败；
- copy-all 的 compactness 明显差。

### 6. Isolation gate

- forbidden imports/dependencies/paths 生效；
- submission 不在 source tree 中运行；
- evaluator network off；
- hidden/public/reference/evaluation 不进入 Agent workspace；
- symlink、absolute path、runtime source loading 有对应检查。

### 7. Difficulty/calibration gate

- 记录 source size、task footprint 和 entanglement；
- `hard` 先作为设计标签，不伪装成经验结果；
- strong-agent calibration 用固定协议记录，不按期望通过率反复改 hidden；
- empirical difficulty 在冻结 baseline 后重新计算；
- 不因“太容易/太难”在看过最终模型结果后静默删题。

### 8. Freeze gate

Promotion 后必须：

- 更新 manifest/registry/reference records；
- 全量 lifecycle 和 v3 readiness 通过；
- 重新运行受影响的 Oracle/isolation/determinism；
- 生成新的 content-addressed benchmark freeze；
- 旧 freeze 保持可追溯但不再 active。

## Required commands

```bash
PYTHONPATH=harness .venv/bin/python -B -m featureliftbench.cli \
  validate-task benchmark/staging/<task_id>

python3 scripts/check_task_lifecycle.py
python3 scripts/build_source_registry.py --check
python3 scripts/materialize_full_sources.py --check
python3 scripts/audit_v3_main_readiness.py --strict
python3 scripts/build_v3_benchmark_freeze.py --check
```

具体 task creation/validation/promotion 应使用仓库中的
`featureliftbench-create-task`、`featureliftbench-validate-task` 和
`featureliftbench-promote-task` skills；promotion skill 只在所有 gate 证据
已齐时运行。

## Never do

- 直接把新目录复制进 Main；
- 按目标功能白名单裁剪“完整仓库”；
- 向 Main Agent 暴露 source entrypoints；
- 让 hidden 要求未公开义务；
- 为了提高区分度而事后改答案；
- 伪造 commit、LOC、测试、Oracle 或模型结果；
- 把 AI-assisted review 写成 independent human review；
- 不重建 freeze 就修改 task/source/evaluator。

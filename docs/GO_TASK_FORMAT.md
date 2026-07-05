# Go 任务格式（GO_TASK_FORMAT）

**最后更新：** 2026-07-05

Go track 的机器可读契约。Python 任务见 [TASK_FORMAT.md](TASK_FORMAT.md)。论文口径见 [BENCHMARK_SPEC.md](BENCHMARK_SPEC.md) §11。

---

## 1. 目录布局

```text
benchmark/go/staging/<task_id>/     # promote 前
benchmark/go/tasks/<task_id>/       # promote 后

<task_id>/
  metadata.json
  TASK.md
  repo/                             # 只读源快照（与 Python 相同政策）
  public_tests/
    *_test.go                       # agent 可见
  hidden_tests/
    *_test.go                       # eval 阶段使用；agent 不可见
  evaluation/
    forbidden_imports.txt           # 原模块 import 路径，每行一个
    module_probes.json              # 至少 3 个 probe
    scoring_reference.json          # 可选；agent 不可见
  environment/
    go.mod                          # 测试 harness module（可 import featurelifted）
    go.sum                          # 可选
```

Submission（oracle / naive / copy_all）：

```text
benchmark/submissions/<task_id>/<variant>/
  go.mod                            # module 名建议 featurelifted 或题目约定
  *.go                              # package featurelifted
```

---

## 2. metadata.json

```json
{
  "task_id": "semver__version_parse_core__001",
  "language": "go",
  "version": "1.0",
  "difficulty": "hard",
  "source": {
    "name": "semver",
    "url": "https://github.com/Masterminds/semver",
    "commit": "<40-char-sha>",
    "license": "MIT"
  },
  "environment": {
    "go": "1.22",
    "network": false,
    "timeout_seconds": 120,
    "cgo_enabled": false
  },
  "tests": {
    "public": "public_tests",
    "hidden": "hidden_tests",
    "command": "go test"
  },
  "tags": ["multi-package", "parser"],
  "entanglement": {
    "level": "high",
    "types": ["internal_packages", "global_registry"]
  }
}
```

**必填字段（Go 特有）：**

| 字段 | 说明 |
| --- | --- |
| `language` | 必须为 `"go"` |
| `environment.go` | 最低 Go 版本 |
| `environment.cgo_enabled` | 默认 `false` |
| `environment.module_path` | submission module path，通常为 `featurelifted` |
| `tests.public` / `tests.hidden` | public/hidden test 目录 |

---

## 2.5 Hard Boundary Contract

Go hard 任务必须以 **symbol / behavior** 为边界，而不是 `.go` 文件为边界。

禁止：

- `oracle == 从 repo 复制若干完整 .go 文件 + 改 package name`
- 文件名或注释出现 `excluded`、`noise`、`non-target` 等提示
- TASK 或 public tests 暗示目标文件名
- hidden 只验证 public happy path 的重复行为

要求：

- 至少两个源文件同时包含 target 和 non-target symbols。
- oracle 需要裁剪、重组或改写函数/类型/方法依赖。
- copy_all pass，但 extraction 明显高于 oracle。
- `docs/go_task_designs/<task_id>.md` 必须填写 Boundary Plan。

---

## 3. TASK.md（给 Agent）

与 Python 相同结构，差异点：

- 输出包路径：`import "featurelifted"` 或 `metadata` 中声明的 module path
- 明确 **禁止** `import` 原仓库 module path（列在 `forbidden_imports.txt`）
- 说明 public tests 如何运行：`go test`
- 不要求 agent 实现 hidden tests
- 不透露目标文件名、hidden 覆盖点或 oracle 文件列表

---

## 4. 测试约定

| 规则 | 说明 |
| --- | --- |
| 框架 | 标准库 `testing`；可用 `testify` 若 lock 在 `environment/go.mod` |
| 包名 | public：`package publictests` 或 `package semver_test`（external test） |
| 确定性 | 无 `time.Now()` 断言；无真实网络；`t.Parallel()` 需 fixture 隔离 |
| Hidden | 覆盖组合、错误、边界；**不得**与 public 重复同一断言逻辑 |
| Probes | `module_probes.json` 映射到 hidden 失败点 |

**external test 推荐：**

```go
package featurelifted_test

import (
    "testing"
    featurelifted "example.com/featurelifted"
)
```

---

## 5. forbidden_imports.txt

每行一个禁止的 import path（前缀匹配由 harness 定义）：

```text
github.com/Masterminds/semver
github.com/Masterminds/semver/v3
```

---

## 6. module_probes.json

```json
{
  "probes": [
    {
      "id": "prerelease_ordering",
      "remove_path": "version_prerelease.go",
      "maps_to_hidden": "hidden_tests/prerelease_test.go:TestPrereleaseOrdering"
    }
  ]
}
```

至少 3 个 probe；oracle 必须通过；每个 probe 必须映射到具体 hidden failure。对 hard 题，probe 应优先删 symbol-level 文件或 package piece；如果 probe 只是证明某个明显目标文件存在，设计需要重新审查。

---

## 7. 评分

与 Python 共用公式（见 TASK_FORMAT / BENCHMARK_SPEC）：

- `functional_gate`：public + hidden 全过 → 1.0，否则 0.0
- `extraction_ratio`：featurelifted 闭包 LOC / 源相关 LOC（Go 口径在 harness 文档登记）
- `final_score`：`functional_gate * (1 - extraction_penalty(...))`

Go 分区报告时**只与 Go 题互比** extraction 分布。

---

## 7. Go LOC 口径

与 Python `count_python_loc` 对称，由 `metrics.count_go_loc` 实现：

- 统计 submission / `repo/` 下所有 `*.go` 文件
- 跳过空行与以 `//` 开头的注释行
- **不**统计 `*_test.go`（submission 内）
- `extraction_ratio = submission_loc / source_loc`（仅 Go 分区内比较）

---

## 8. promote 检查

```bash
PYTHONPATH=harness python -m featureliftbench.cli validate-task benchmark/go/staging/<task_id>
PYTHONPATH=harness python -m featureliftbench.cli audit_output_imports benchmark/go/staging/<task_id> \
  benchmark/submissions/<task_id>/oracle --fail-on-gap
```

Hard paper-ready promote 时：

```bash
git mv benchmark/go/staging/<task_id> benchmark/go/tasks/<task_id>
```

并更新 `docs/go_candidate_backlog.md`、`docs/benchmark_tasks.md`（Go 分区）。`promote_calibration` 只保留 evidence，不进入 hard 主表。

---

## 9. 与 Python 的差异摘要

| 项 | Python | Go |
| --- | --- | --- |
| 测试运行 | `pytest` | `go test` |
| 包布局 | `featurelifted/` + `pyproject.toml` | submission 根目录 `*.go` package `featurelifted` + `go.mod` |
| 依赖锁 | `requirements.lock` | `go.sum` |
| 禁止依赖 | `forbidden_dependencies` in metadata | `forbidden_imports.txt` |
| Eval 镜像 | Python 3.11 | + Go toolchain |

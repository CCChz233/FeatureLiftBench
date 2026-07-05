# Go Harness 实现计划

**最后更新：** 2026-07-05

Go track 的**工程阻塞项**。在 Phase 0 完成前，不要 promote 任何 Go staging 题到 `benchmark/go/tasks/`。

相关：[GO_PILOT_PLAYBOOK.md](GO_PILOT_PLAYBOOK.md) · [GO_TASK_FORMAT.md](GO_TASK_FORMAT.md) · [BENCHMARK_SPEC.md](BENCHMARK_SPEC.md) §11

---

## 1. 目标

让 `featureliftbench eval` / `run-agent` 对 `metadata.language == "go"` 的题目：

1. 在隔离环境（优先 Docker eval）中 `go test` public + hidden
2. 安装 submission 为独立 Go module（根目录 `*.go` + `go.mod`）
3. 检查 forbidden import（原模块路径）
4. 计算与 Python 相同的 footprint / `extraction_ratio` / `final_score`
5. 产出结构化 `result.json`（与 Python 字段对齐）

---

## 2. 非目标（Phase 0）

- `cgo` / 跨平台汇编题
- 需要 `docker run --privileged` 的题
- 依赖外部服务的集成测试
- Agent Docker 内嵌完整 Go toolchain 的一键方案（可 Phase 1 简化：eval Docker 先带 Go，agent 仍宿主）

---

## 3. 实现清单

### 3.1 元数据与校验

| 项 | 文件 | 说明 |
| --- | --- | --- |
| schema 扩展 | `harness/featureliftbench/schemas/task_metadata.schema.json` | `language: "go"`；`environment.go` 版本 |
| validate | `harness/featureliftbench/validate.py` | 校验 `go.mod` 路径、`_test.go` 包名、`evaluation/` |
| redaction | `agent_runner.py` | 与 Python 相同：隐藏 hidden 路径、scoring_reference |

### 3.2 Evaluator

| 项 | 说明 |
| --- | --- |
| `go_eval.py` 或扩展 `evaluator.py` | 分支 `language == go` |
| 安装 | `go mod download` + `replace` 指向 submission；或 `go work` |
| 测试 | `go test -count=1 ./public_tests/...` 与 hidden（hidden 仅 eval 阶段挂载） |
| 指标 | 复用 `metrics.py`：统计 `.go` 文件 LOC、依赖数 |
| forbidden | `go list -deps` 或静态 import 扫描 + `forbidden_imports.txt` |
| Docker | 扩展 `featureliftbench-eval` 镜像：安装 Go 1.22+；`network=none` |

### 3.3 CLI

```bash
PYTHONPATH=harness python -m featureliftbench.cli validate-task benchmark/go/staging/<task_id>
PYTHONPATH=harness python -m featureliftbench.cli eval benchmark/go/staging/<task_id> \
  benchmark/submissions/<task_id>/oracle --output /tmp/out --docker
```

### 3.4 脚本（与 Python 对齐）

| 脚本 | 用途 |
| --- | --- |
| `build_go_oracle_submission.py` | 构建 Go oracle/naive/copy_all submissions |
| `verify_module_probes.py` | Go import 探针 |
| `verify_all_oracles.py` | 批量 oracle |
| staging gate 脚本 | `experiments/go-pilot/<task_id>/review/` 生成 `gate_report.json` |

### 3.5 Docker 镜像

| 镜像 | 变更 |
| --- | --- |
| `featureliftbench-eval` | 基础镜像加 `golang:1.22` 或 slim + apt install go |
| `featureliftbench-agent` | Phase 1+：可选加 Go（若 agent 需在容器内 `go test` public） |

环境变量（建议）：

```bash
FEATURELIFTBENCH_EVAL_GO_VERSION=1.22
```

---

## 4. 测试策略

| 层级 | 内容 |
| --- | --- |
| 单元 | `harness/tests/test_go_eval.py` — mock `go test` 输出 |
| 集成 | 1 道最小 Go sanity 题（仿 `iniconfig` smoke） |
| 回归 | oracle eval 在 CI 中跑 staging pilot |

---

## 5. Phase 0 完成定义（DoD）

- [x] `validate-task` 对 Go staging 目录 exit 0
- [x] oracle submission `eval` 产生 `status=passed` 的 `result.json`（`eval --docker` 镜像已含 Go 1.22）
- [x] naive / copy_all 在 pilot 题上呈现预期分层（G2/G3）
- [x] `docs/GO_PILOT_PLAYBOOK.md` Step 5 命令可运行（`run_go_pilot_review.sh`）
- [x] `limitations.md` 已更新为 Go pilot harness MVP

---

## 6. 风险与缓解

| 风险 | 缓解 |
| --- | --- |
| `go test` 缓存/网络 | `--count=1`；`GOPROXY=off` + vendor 或 module cache 预置 |
| 路径依赖 | 禁止 `t.TempDir()` 以外的绝对路径；hidden 用相对 fixture |
| LOC 口径与 Python 不一致 | 文档写明 Go 统计规则；论文只跨题比较 Go 分区 |
| Agent 不会写 `go.mod` | `TASK.md` 给模板；public test 覆盖 module 布局 |

---

## 7. 排期（建议）

| 周 | 交付 |
| --- | --- |
| 1 | schema + validate + 最小 `go test` eval（宿主） |
| 2 | Docker eval + forbidden import + metrics |
| 3 | pilot 题 + gate 脚本 + 文档命令跑通 |

完成后再进入 [GO_PILOT_PLAYBOOK.md](GO_PILOT_PLAYBOOK.md) Phase 1。

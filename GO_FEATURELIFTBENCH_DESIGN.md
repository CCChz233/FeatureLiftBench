# Go FeatureLiftBench 设计文档

## 0. 结论

Go 方向值得做，但不建议直接开工 100 题。当前 Python v1 已经有 100 题、Docker eval、agent Docker 和一套验收口径；Go 应作为 **v2 language partition** 进入，而不是临时复制一套不兼容流程。

配套执行文档：

- [docs/GO_V2_MINI_SPEC.md](docs/GO_V2_MINI_SPEC.md)：Go task、submission、evaluator、Docker、gate 的最低契约；
- [docs/GO_PILOT_PLAYBOOK.md](docs/GO_PILOT_PLAYBOOK.md)：第一批 5 题 pilot 的任务清单、证据包和验收流程。

推荐路线：

1. 先做 **Go pilot 5 题**，证明 Go evaluator、Docker、metadata、oracle、copy-all、naive 全闭环。
2. 再做 **Go alpha 20 题**，覆盖 parser/config/reflection/concurrency/vibe_app。
3. 通过稳定性和 agent 校准后冻结 **Go batch-0 50 题**。
4. 最后扩到 **Go batch-1 +50**。

核心原则：

- Go 任务仍然测 **feature-level decoupling**，不是 bug fix、repo patch 或纯算法题。
- Go 任务必须和 Python 任务共享 headline 指标：Functional Pass、Extraction Ratio、Final Score。
- Go 任务需要独立 evaluator dispatch；不能拿 Python pytest evaluator 硬套。
- 并发任务是 Go 的特色，但不能让 benchmark 变成 flaky concurrency test suite。

## 1. Go 版目标

Go FeatureLiftBench 评估代码 Agent 是否能从真实 Go 仓库中抽取目标功能，形成独立、可编译、可测试的 Go module。

Go 版额外强调：

- 静态类型和编译期约束；
- Go module isolation；
- import path / `go.mod` / `replace` 规则；
- interface、reflection、struct tag；
- goroutine、channel、context、sync 等并发语义。

核心问题不变：

> Agent 是真正完成了可复用 feature lifting，还是只是 copy-heavy 地复制源代码？

## 2. 与现有 Python Benchmark 的关系

Go 是 v2 language partition，不替换 Python v1。

| 项 | Python v1 | Go v2 |
|---|---|---|
| 主榜 | 100 Python hard | 目标 100 Go hard |
| 输出 | `submission/featurelifted/` Python package | `submission/go.mod` + `submission/featurelifted/` Go package |
| evaluator | Python venv + pytest | Go toolchain + `go test` |
| Docker eval | `featureliftbench-eval` | 新增 Go eval image 或 unified eval image |
| agent Docker | Python + mini-swe-agent | 需要包含 Go toolchain，供 agent 跑 public tests |
| scoring | FunctionalGate x `(1 - ExtractionRatio)` | 同一公式，LOC 换成 Go LOC |

不建议 Go pilot 直接混进 Python `benchmark/tasks/` 并要求现有 evaluator 通过。建议先用 staging/pilot 目录做闭环；v2 harness 完成后，再纳入统一主榜目录和 catalog。

## 3. 推荐执行顺序

### G0：Go Harness Pilot

目标：只做 5 题，但每题证据完整。

必须实现：

- `metadata.language == "go"` 的 validate 逻辑；
- Go evaluator dispatch；
- Go eval Docker image；
- Go agent Docker image 或在现有 agent image 中加入 Go toolchain；
- Go task prompt；
- Go oracle / naive / copy-all baseline 构建方式；
- suite summary 能按 `language=go` 分组。

建议 pilot 题：

| task_id 示例 | 来源 | 类型 | 原因 |
|---|---|---|---|
| `semver__constraint_core__001` | `Masterminds/semver` | parser/data model | 小而稳定，适合验证 module/import/LOC |
| `doublestar__glob_match_core__001` | `bmatcuk/doublestar` | matcher/path | hidden 好写，copy-all 明显偏大 |
| `mapstructure__decode_hook_core__001` | `mitchellh/mapstructure` | reflection/tags | Go 特色明显 |
| `singleflight__group_core__001` | `golang/sync` | concurrency | 并发 pilot，但规模可控 |
| `go_vibe_app__pubsub_core__001` | curated | channel lifecycle | 可控地测试 close/cancel/leak |

### G1：Go Alpha 20

目标：验证题型分布和 agent 难度。

建议配比：

| 类型 | 数量 |
|---|---:|
| Parser / config / DSL | 5 |
| Reflection / validator / schema | 4 |
| CLI / matcher / path | 3 |
| Concurrency | 5 |
| Curated Go vibe_app | 3 |

### G2：Go Batch-0 50

冻结前必须跑至少一轮 strong agent calibration，并记录 A/B/C 难度标签。Go batch-0 建议：

| 类型 | 数量 |
|---|---:|
| 普通 OSS feature lifting | 35 |
| concurrency-focused | 10 |
| curated Go vibe_app | 5 |

### G3：Go Batch-1 +50

在 batch-0 稳定后再扩，不要边修 evaluator 边扩题。

最终 Go 100 推荐比例：

| 类型 | 数量 |
|---|---:|
| 普通 OSS feature lifting | 60 |
| concurrency-focused | 25 |
| curated Go vibe_app | 15 |

## 4. Go 任务定义

每道 Go 任务包含：

- 固定 commit 的 Go 源仓库；
- 功能规格；
- public Go tests；
- hidden Go tests；
- forbidden import / forbidden module 规则；
- Go module eval 环境；
- Docker 化评测。

Agent 需要提交：

```text
submission/
  go.mod
  featurelifted/
    *.go
```

推荐固定 module path：

```text
module featurelifted.local/<task_id>
```

测试文件应 import：

```go
import flb "featurelifted.local/<task_id>/featurelifted"
```

这样 public/hidden tests 可以稳定引用 agent 输出，不依赖 agent 自定义 module path。Evaluator 可以在 runtime copy 中校验或重写 `go.mod` 的 module path，但必须把这个行为写入 spec。

提交要求：

1. `go test ./...` 通过；
2. `go.mod` 存在；
3. `go.mod` module path 合法且符合任务约定；
4. 不 import 原仓库 module path；
5. 不 `require` 原仓库 module；
6. 不 `replace` 到原仓库、workspace、host path 或 hidden path；
7. 不依赖网络下载；
8. public tests 和 hidden tests 全部通过；
9. 并发任务额外通过稳定性检查；
10. 尽量减少复制代码量。

## 5. Go Evaluator 设计

### 5.1 基础流程

Go evaluator 不应在 mounted submission 上直接写入。流程应和 Python Docker eval 一致：

1. 将 submission 复制到 runtime temp dir；
2. 校验 `go.mod`、import、replace、forbidden module；
3. 将 public/hidden tests 注入 runtime copy；
4. 设置离线 Go 环境；
5. 运行 `go test ./...`；
6. 统计 Go LOC、依赖、score；
7. 写结构化 `result.json`。

建议 eval 命令：

```bash
GONOSUMDB=*
GOPROXY=off
GOWORK=off
GOFLAGS=-mod=mod
go test ./... -count=1 -timeout=30s
```

注意：如果要求完全离线，`go test` 不能临时下载 module。第一版建议：

- pilot 任务默认不允许 external deps；
- 如果需要 external deps，必须在 eval image 中预置 module cache 或 vendor；
- `go.mod` 中只允许白名单依赖；
- 不挂 host Go module cache，避免本机状态污染结果。

### 5.2 Forbidden Import / Module Gate

必须检查：

- 所有 `.go` 文件 import path；
- `go.mod` 的 `require`；
- `go.mod` 的 `replace`；
- `go.work` 是否存在；
- `vendor/modules.txt` 是否引入原仓库；
- symlink 是否逃逸 submission runtime。

禁止：

```text
import "<original-module-path>/..."
require <original-module-path>
replace <original-module-path> => ...
replace ... => ../repo
replace ... => /host/path
```

建议用两层检查：

1. 静态解析 `.go` import + `go.mod`；
2. `go list -deps -json ./...` 后检查 resolved import/module path。

### 5.3 Go LOC 统计

Extraction Ratio：

```text
SubmissionGoLOC / SourceRepoGoLOC
```

建议统计规则：

- 只统计 `.go`；
- 默认排除 `_test.go`；
- 默认排除 `vendor/`；
- 默认排除 generated files，但必须有可审计规则，如文件头含 `Code generated`;
- source repo LOC 用 task 的 pinned `repo/`；
- submission LOC 用 runtime copy 的 `featurelifted/`。

## 6. Docker 设计

### 6.1 Eval Docker

Go eval container 默认：

```text
network: none
memory: 4g-8g
cpus: 2
pids-limit: 256
root filesystem: read-only
/tmp: tmpfs
Go build cache: tmpfs or runtime temp
host mounts: task ro, submission ro, output rw, harness ro
```

需要新增：

- `docker/Dockerfile.eval-go`，或把 Go toolchain 加到 unified eval image；
- `docker/build_go_eval_image.sh`；
- Go module cache strategy；
- structured sandbox failure result。

### 6.2 Agent Docker

Go agent 需要能跑 public Go tests，所以 agent Docker 也必须有 Go toolchain。

当前 Python agent image 只装 Python/mini-swe-agent，不够。Go v2 需要：

- 新增 `docker/Dockerfile.agent-go`；或
- 把 Go toolchain 加到 `featureliftbench-agent` image，并记录 image version。

Agent Docker 仍默认允许网络，因为需要模型 API；文件系统边界仍只挂：

```text
prepared workspace: rw
agent output: rw
harness: ro
```

不挂：

```text
benchmark root
hidden tests
.env
host home
Docker socket
host Go module cache
```

## 7. 并发任务规则

原计划里同时写了：

```bash
CGO_ENABLED=0 go test ./...
go test ./... -race
```

这两者有冲突：Go race detector 通常需要 cgo 和额外工具链。建议规则：

### 7.1 默认 functional eval

```bash
CGO_ENABLED=0 go test ./... -count=1 -timeout=30s
```

### 7.2 race-marked task 额外 eval

只对 `metadata.concurrency.race_test=true` 的任务运行：

```bash
CGO_ENABLED=1 go test ./... -race -count=1 -timeout=60s
```

这要求 eval image 安装支持 race detector 的工具链。race fail 单独报告，不一定和普通 hidden fail 混在一起。

### 7.3 stress eval

只跑稳定、短时、确定性的 stress：

```bash
go test ./... -run <StressPattern> -count=20 -timeout=60s
```

不要依赖真实 sleep 长时间等待；优先用 fake clock、barrier、context timeout 和 deterministic scheduler hooks。

并发 hidden tests 应覆盖：

- 100+ goroutine 同时调用；
- context cancel；
- worker pool shutdown；
- channel close；
- duplicate suppression；
- panic recovery；
- goroutine leak；
- race / deadlock / timeout。

但任何 flaky 或依赖机器负载的测试不得进入主榜。

## 8. Metadata Schema 草案

Go 任务应扩展现有 schema，而不是新建完全不同格式。

```json
{
  "task_id": "singleflight__group_core__001",
  "language": "go",
  "source": {
    "name": "sync",
    "url": "https://github.com/golang/sync",
    "commit": "...",
    "license": "BSD-3-Clause",
    "module_path": "golang.org/x/sync"
  },
  "feature": {
    "name": "singleflight group",
    "description": "Extract duplicate-suppression calls for concurrent keys.",
    "source_entrypoints": [
      "singleflight/singleflight.go"
    ],
    "included_behaviors": [
      "Do",
      "DoChan",
      "Forget",
      "shared result semantics"
    ],
    "excluded_behaviors": [
      "unrelated x/sync packages"
    ]
  },
  "output": {
    "module": "featurelifted.local/singleflight__group_core__001",
    "package": "featurelifted",
    "import": "featurelifted.local/singleflight__group_core__001/featurelifted",
    "symbols": [
      "Group",
      "Result"
    ]
  },
  "environment": {
    "go": "1.22",
    "network": false,
    "timeout_seconds": 30,
    "allowed_modules": [],
    "forbidden_modules": [
      "golang.org/x/sync"
    ],
    "forbidden_imports": [
      "golang.org/x/sync"
    ]
  },
  "entanglement": {
    "level": "hard",
    "primary": "singleflight_state",
    "types": [
      "singleflight_state",
      "goroutine_lifecycle",
      "mutex_state"
    ],
    "description": "Duplicate suppression depends on shared inflight state and synchronization."
  },
  "concurrency": {
    "enabled": true,
    "race_test": true,
    "stress_count": 20,
    "timeout_seconds": 60
  },
  "difficulty": "hard",
  "tags": [
    "go",
    "concurrency",
    "functional-discriminator"
  ]
}
```

## 9. Go Entanglement Taxonomy

建议保留 Python 的高层 taxonomy，同时增加 Go-specific secondary tags。

### 9.1 Primary categories

| primary | 含义 |
|---|---|
| `parser_state_coupling` | lexer / parser / AST 状态 |
| `config_environment_coupling` | env、default、override、merge |
| `data_model_coupling` | struct、interface、encoding model |
| `reflection_tag_coupling` | reflect、struct tag、decode hook |
| `global_state_registry_coupling` | registry、default instance、global mutable state |
| `resource_coupling` | io.Reader/Writer、file/path/time |
| `concurrency_coupling` | goroutine/channel/context/sync |
| `legacy_vibe_clutter` | curated messy application code |

### 9.2 Go-specific secondary tags

| tag | 含义 |
|---|---|
| `goroutine_lifecycle` | goroutine 创建、退出、等待 |
| `channel_lifecycle` | send / receive / close |
| `context_cancellation` | timeout、cancel 传播 |
| `mutex_state` | Mutex、RWMutex、Cond、死锁风险 |
| `worker_pool` | queue、limit、shutdown、wait |
| `concurrent_cache` | 并发读写、TTL、loader、eviction |
| `rate_limiter` | token refill、burst、wait |
| `pubsub_state` | subscriber registry、broadcast、unsubscribe |
| `singleflight_state` | inflight request 合并 |
| `pipeline_backpressure` | 多阶段 pipeline、阻塞、提前退出 |

## 10. 推荐仓库池

### 10.1 优先标准

优先选择：

- 纯 Go；
- 不需要外部服务；
- 不需要 codegen；
- 可离线测试；
- module 依赖少；
- 源码规模适中；
- license 清楚；
- 可写 compact oracle；
- copy-all 明显比 oracle 大；
- hidden tests 能区分 shallow / public-only / copy-heavy。

第一版不建议大量使用：

| 类型 | 原因 |
|---|---|
| Kubernetes / Docker / Terraform 主仓 | 过大，依赖和生成链复杂 |
| Gin / Echo / Fiber 主流程 | 容易变成 Web 框架复刻 |
| DB driver / Redis client | 容易依赖外部服务 |
| gRPC / protobuf | codegen 和工具链复杂 |
| Cloud SDK | 依赖重，离线测试成本高 |

### 10.2 Candidate pool

| Repo | 类型 | 建议优先级 | 备注 |
|---|---|---|---|
| `Masterminds/semver` | semver parser / constraints | P0 | 小而稳定 |
| `hashicorp/go-version` | version constraints | P0 | 与 semver 切面不同 |
| `bmatcuk/doublestar` | glob matcher | P0 | hidden 好写 |
| `gobwas/glob` | glob compiler | P1 | 可做 parser/matcher |
| `mitchellh/mapstructure` | map -> struct decoder | P0 | reflection 代表 |
| `go-playground/validator` | struct validator | P1 | 需控制 scope |
| `BurntSushi/toml` | TOML parser / decoder | P1 | 注意 closure 大小 |
| `go-yaml/yaml` | YAML parser / encoder | P1 | 控制 hidden 范围 |
| `tidwall/gjson` | JSON query | P0 | parser/data model |
| `tidwall/sjson` | JSON mutation | P1 | 和 gjson 区分 |
| `robfig/cron` | cron parser / scheduler | P1 | scheduler 部分慎用 |
| `spf13/cobra` | CLI command parser | P1 | 控制框架复刻风险 |
| `urfave/cli` | CLI framework | P2 | 容易过大 |
| `golang/sync` | singleflight / errgroup / semaphore | P0 | Go concurrency pilot |
| `sourcegraph/conc` | structured concurrency | P1 | 高价值但需稳定性验证 |
| `cenkalti/backoff` | retry / backoff | P0 | context/time hidden 好写 |
| `juju/ratelimit` | token bucket | P1 | 需要 fake clock 或短时测试 |
| `jellydator/ttlcache` | TTL cache | P1 | 并发 + time，需防 flake |
| `patrickmn/go-cache` | in-memory cache | P2 | 可作为 simpler cache |

任务数不要先按 repo 平均分配。每个 repo 先做 1 个 slice，通过 gate 后再追加第 2/3 个。

## 11. Curated Go vibe_app

建议保留 curated Go vibe_app，但不要占比过高。最终 100 题中 15 题左右即可。

候选模块：

| 模块 | 可出任务 | 主要难点 |
|---|---|---|
| `configx` | env + yaml + default merge | config environment |
| `rules` | rule parser + evaluator | parser state / registry |
| `router` | route pattern matcher | matcher / priority |
| `session` | session registry | global state / concurrency |
| `schema` | struct tag validator | reflection / tag parser |
| `workflow` | DAG parser + executor | graph / scheduler |
| `auditlog` | formatter + redaction | formatter / policy |
| `perm` | RBAC policy parser | rule matching |
| `pubsub` | subscribe / broadcast / close | channel lifecycle |
| `workerx` | bounded worker pool | goroutine lifecycle |
| `cachex` | TTL cache + loader | concurrent cache |
| `ratelimitx` | token bucket | time / concurrency |
| `retryx` | retry + backoff + context | cancellation |
| `pipelinex` | multi-stage pipeline | backpressure / cancellation |
| `singleflightx` | duplicate suppression | inflight registry |

Curated tasks 的作用是补足真实 OSS 不好稳定复现的业务缠绕，不应替代真实 OSS 主叙事。

## 12. Go 质量 Gate

每题进入 Go 主榜前必须有 evidence packet。

| Gate | 要求 |
|---|---|
| G0 task shape | validate 通过；metadata/schema/layout 完整 |
| G1 oracle | oracle functional pass；extraction 合理 |
| G2 naive | naive public-only 或 shallow baseline hidden fail |
| G3 copy-all | copy-all functional pass；extraction 明显高于 oracle |
| G4 forbidden | oracle/copy-all 不触犯 forbidden import/module；agent submission 会被检查 |
| G5 offline | eval Docker `--network none` 下 oracle pass |
| G6 stability | 连跑 20 次无 flake；并发任务额外 stress/race 稳定 |
| G7 agent calibration | 至少跑 Flash 或等价 strong agent，记录 A/B/C 难度标签 |

Go 任务不要因为 Flash 能 functional pass 就直接淘汰。和 Python batch-1 一样，functional pass 与 extraction quality 要一起报告。

## 13. 评测指标

沿用 Python headline：

| 指标 | 含义 |
|---|---|
| Functional Pass | build + tests + forbidden import/module gate |
| Extraction Ratio | `submission Go LOC / source repo Go LOC` |
| Final Score | `FunctionalGate * (1 - ExtractionRatio)` |
| Compact Pass | pass 且 extraction 低 |
| Copy-heavy Pass | pass 但 extraction 高 |
| Hidden Fail | public 过、hidden 挂 |

Go-specific diagnostics：

| 指标 | 含义 |
|---|---|
| Compile Fail | `go test` 编译失败 |
| Forbidden Module Fail | import/require/replace 原仓库 |
| Offline Dependency Fail | 离线 module 解析失败 |
| Race Fail | `go test -race` 失败 |
| Timeout Fail | deadlock 或长时间阻塞 |
| Leak Fail | goroutine 未清理 |
| Cancel Fail | context cancel 后未退出 |
| Double Close Panic | channel close 语义错误 |

## 14. 论文叙事

加入 Go 后，FeatureLiftBench 可以从单语言 benchmark 扩展为跨语言 feature-lifting benchmark：

> FeatureLiftBench contains feature-lifting tasks across Python and Go, covering both dynamic and statically typed ecosystems.

Go 版独特价值：

> Python tasks stress dynamic dependency closure and runtime behavior, while Go tasks additionally stress static module isolation, compile-time typing, and concurrency-aware feature lifting.

最终主张仍应谨慎：

> Across Python and Go, agents can often make extracted packages pass functional tests, but functional success frequently comes from copy-heavy extraction rather than clean decoupling.

并发任务可以支撑新发现：

> In Go, concurrency-oriented feature lifting exposes additional failure modes, including race conditions, goroutine leaks, cancellation failures, and incorrect channel lifecycle handling.

## 15. 当前最优下一步

不要马上做 100 条。下一步应该是：

1. 写 Go v2 mini spec，明确 module path、test injection、offline deps、scoring。
2. 实现 Go evaluator dispatch + Go Docker eval image。
3. 实现 Go agent Docker image，确保 agent 能跑 public Go tests。
4. 做 5 个 pilot tasks。
5. 每题补 oracle / naive / copy-all / Flash evidence。
6. 连跑 stability check。
7. 再决定是否扩到 alpha 20。

如果 pilot 5 题中任意一项不稳定，不应继续扩题；优先修 evaluator 和 task contract。

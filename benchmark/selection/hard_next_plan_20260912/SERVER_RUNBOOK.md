# 服务器执行手册

本手册里的新题包、研究 registry、输入锁和 reviewer 结论需要按主方案生成后才存在。
命令是针对当前仓库 CLI 核对过参数的模板，未在本机 Linux/Docker 环境执行；不等价于已通过集成验证。
仅使用 Linux 服务器。不要用本机 `screen.py` 的临时 source-tools agent 代替 Official Main。

## 1. 设置专用目录与环境

在你准备好的独立研究 checkout 根目录运行。先填入实际模型配置、镜像和 task ID；不要把占位符原样执行。
先按 `INPUTS.md` 备齐历史证据和当前研究资产。下面命令展示的是单个已准备好任务的执行流程；不负责自动生成 P0 配置或 P2 题包。

```bash
set -euo pipefail
export PYTHONPATH="$PWD/harness"
export PYTHONDONTWRITEBYTECODE=1

# 均为后续物化阶段创建的专用研究资产；不覆盖主榜注册表。
export FEATURELIFTBENCH_SOURCE_REGISTRY="$PWD/benchmark/sources/hard_mechanism_study_registry.json"
export FEATURELIFTBENCH_REFERENCE_REGISTRY="$PWD/benchmark/references/hard_mechanism_study_compactness.json"

TASK_ROOT="$PWD/benchmark/staging"
AGENT_CONFIG="$PWD/harness/config/hard_mechanism_study.local.toml"
ENV_FILE="$PWD/.env.hard-mechanism.local"

read -r -p '实际 agent 镜像 tag 或 digest: ' AGENT_IMAGE
read -r -p '实际 evaluator 镜像 tag 或 digest: ' EVAL_IMAGE
read -r -p '经审计的 Flash profile 名: ' PROFILE
read -r -p '本次研究 task_id: ' TASK_ID

TASK_DIR="$TASK_ROOT/$TASK_ID"
RUN_ROOT="$PWD/experiments/calibration/hard_mechanism_study"
mkdir -p "$RUN_ROOT"
```

输入 profile 不能只凭名称看起来像 baseline：实际内容应禁用所有方法增强，指定正确模型、上下文规则、120 steps。固定其 hash，命令行再明确设置信息条件。
`*.local.toml` 的新文件不一定自动被忽略：里面仅放无密钥的 profile 配置，密钥只放已由 `.env.*` 规则忽略的 ENV_FILE，确认 `git check-ignore "$ENV_FILE"` 返回该文件。
不要导出/归档 ENV_FILE，也不要打印环境变量全集。

```bash
test -f "$TASK_DIR/metadata.json"
test -f "$AGENT_CONFIG"
test -f "$ENV_FILE"
test -f "$FEATURELIFTBENCH_SOURCE_REGISTRY"
test -f "$FEATURELIFTBENCH_REFERENCE_REGISTRY"
docker info --format '{{.OSType}}'
docker image inspect "$AGENT_IMAGE" --format '{{.Id}}'
docker image inspect "$EVAL_IMAGE" --format '{{.Id}}'
git rev-parse HEAD
sha256sum "$AGENT_CONFIG"
```

## 2. 来源与题包验证

初次构造时使用 `scripts/build_source_registry.py --tasks-root <仅含研究任务的临时元数据根> --output <研究registry>`，然后合并各 pinned snapshot 的可验证来源证据；不要把整个混合 staging 的任务全注册到研究池。
修改后的研究 task ID 必须出现在 snapshot 的 task_ids，O/C/N 共用同一真实 source snapshot。原题 task ID 及原 registry 不变。

```bash
python3 scripts/materialize_full_sources.py \
  --registry "$FEATURELIFTBENCH_SOURCE_REGISTRY" --check --task-id "$TASK_ID"

python3 -B -m featureliftbench.cli validate-task "$TASK_DIR" --json
python3 .agents/skills/featureliftbench-validate-task/scripts/audit_featurelift_task.py "$TASK_DIR" --json
```

还要运行项目现行契约/隐藏公平性、来源、隔离和泄漏门禁。轻量 preflight 通过不替代语义审查；对实验副本不要自动写入 Main freeze。
审查结束生成独立研究输入锁，覆盖 metadata/TASK/requirements/tests/evaluation/reference 与 source registry/archive digest；哈希匹配是封存条件，不写伪造 `gate_pass=true` 的主榜 freeze。

## 3. 三次 Docker 参考解

下面的 eval 假定内联参考目录按模板存在。依赖 wheel 必须预先准备；运行 evaluator 时断网。

```bash
for REP in 1 2 3; do
  STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
  OUT="$RUN_ROOT/oracle-${TASK_ID}-r${REP}-${STAMP}"
  test ! -e "$OUT" || exit 1
  python3 -B -m featureliftbench.cli eval \
    "$TASK_DIR" "$TASK_DIR/reference_solution" \
    --docker --docker-image "$EVAL_IMAGE" --output "$OUT" || exit 1
done
```

逐份读取 result，确认 build/public/hidden/isolation 都为 true，并记录输入锁、capsule/source/参考指纹。
失败先修题/环境，另建版本并保留失败记录，不运行模型碰运气。

## 4. 单次模型尝试

只有 P0 环境通过、该版本 oracle/语义审查通过且输入锁校验通过后才执行。
下面不会自动重跑失败，重复实验必须另开输出目录。

```bash
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$RUN_ROOT/flash-${TASK_ID}-r1-${STAMP}"
test ! -e "$OUT" || exit 1

python3 -B -m featureliftbench.cli run-agent "$TASK_DIR" \
  --agent openhands \
  --agent-profile "$PROFILE" --agent-config "$AGENT_CONFIG" \
  --env-file "$ENV_FILE" \
  --agent-docker --agent-docker-image "$AGENT_IMAGE" \
  --eval-docker --eval-docker-image "$EVAL_IMAGE" \
  --source-context full_repository \
  --no-agent-source-hints --no-agent-public-tests --prompt-style standard \
  --timeout-seconds 3600 \
  --extra-agent-passes 0 --max-task-attempts 1 \
  --retry-rate-limit 1 --retry-transient-api 1 \
  --output "$OUT"
```

`r1` 是本次独立尝试的标签，确认轮改为 r2/r3；不能用 `--resume` 将失败重做后覆盖为成功。
调度最大并发 2；同一版本的重复也必须有独立会话，不能挂载前次 submission。
每轮结束校验输入锁仍未改变，并核对 run 中生效 profile/模型/镜像/No-Hint 与封存配置相同。

## 5. 如何判结果

以 `eval/result.json` 的四项功能门为准，分别记录 `run.status` 与退出原因。
例如 agent step-limited 但四项全过，仍记录功能通过；没交代码是无提交功能失败，但不能因此自动断定任务有效且很难。

记录两套视图：

1. 所有计划尝试及结果：包括未交付、API/环境失败和协议不合规运行，保留完整分母；
2. 可解释的难度证据：仅讨论输入/环境有效的运行，明确哪些不能归因于任务难度，不静默删除这些尝试。

每个结果填 `templates/run_record.json`。检测到上下文超限、来源 digest 空值、参考缺失或模型版本漂移时标记有效性问题，不自行修改原评分。

## 6. 交回什么

每个阶段交回一个维护者私有归档，含 README、experiment matrix、环境/profile（无密钥）、输入锁、registry、评审结论、变更说明、suite/run/result、usage/context audit、日志与 submissions。
新题包/参考/隐藏测试另放受控维护者目录，不直接给 agent。来源归档可独立交付并在总清单中记录 hash。
生成 SHA256SUMS，写清任务数、计划/实际尝试数、缺失项、功能结果与有效性异常。不要只交 Excel 或口头通过率。

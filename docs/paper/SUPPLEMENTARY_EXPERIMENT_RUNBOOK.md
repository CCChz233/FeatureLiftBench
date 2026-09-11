# FeatureLiftBench 补充实验：设计与服务器执行指南

> **Status: current · Last verified: 2026-09-11**
> 本文是一份执行方案，不是实验结果。当前已固定任务清单；尚未实现 Contract-only 和新的机械 baseline，也未启动模型调用。

## 1. 先跑什么

**第一阶段：40 题 × GPT-5.6 Luna × 2 个条件，共 80 次正式 agent 运行。**

- Full Source：完整 source repository + public behavioral contract。
- Contract Only：同一 public behavioral contract，移除仓库实现证据。
- 正式运行前，用另外 3 题测试两个条件，共 6 次 smoke；smoke 不计入统计。
- 如果预算允许，再用 DeepSeek V4 Pro 跑同一 40 题的两组，增加 80 次正式运行。是否增加模型由预定预算决定，不因第一阶段差异好不好看决定。
- 第二阶段：同一 40 题的机械提取 baseline，无 LLM 调用，40 次 evaluator 运行。
- source-location hint 第三臂暂不做。

这批是**补充对照实验**。论文仍然是 200 题 benchmark、150 题六配置主比较、另外 50 题五配置扩展。不要用这 40 题替换主比较，也不要把新的 Full 分数覆盖到原主表。

按作者选择，第一阶段使用 GPT-5.6 Luna；第二模型建议保留 DeepSeek V4 Pro。两个模型是这组补充对照的合理规模，不必扩展到主表全部六个模型。两模型均完成时为 40 题 × 2 模型 × 2 条件 = 160 次正式运行；结论限于所测模型与样本，不保证统计显著或跨模型普遍成立。

## 2. 研究问题与可得结论

### 实验 A：仓库实现证据是否帮助行为重建？

问题：在相同任务、agent、模型与预算下，提供完整仓库，相比仅提供契约，如何改变功能通过率？

主指标为 task-level functional pass。Full 与 Contract-only 的差值是主效应；失败门分布是辅助观察。

Full 提供源码、仓库文档、上游测试与资源，因此测到的是**完整仓库证据的总收益**，不能单独称为“源代码文本收益”。Contract-only 仍保留模型预训练知识；不能声称模型从未见过该项目。

不要预设 `70% → 35%`。Full 更高支持仓库证据有益；接近说明这组任务/模型/预算下未观察到明确收益；Full 更低可能涉及上下文负担或错误复用，需要再看轨迹。小样本不显著不等于两个条件等价。

### 实验 B：一个固定机械算法能解决多少任务？

问题：不调用 LLM，仅用公开 API 名称检索、模块复制和静态依赖处理，能达到怎样的功能通过率？

低分只能说明**这个明确实现的算法**覆盖有限，不能证明所有传统方法均无效，也不能直接证明 agent 的内部“理解”。高分不自动使 benchmark 无效：本任务允许复制、适配和重实现；独立执行与行为保持是硬要求，最小化不是硬要求。

## 3. 固定任务清单

正式清单：[source_ablation_40.json](experiments/source_ablation_40.json)。纯题号：[source_ablation_40.txt](experiments/source_ablation_40.txt)。调试题：[source_ablation_smoke_3.txt](experiments/source_ablation_smoke_3.txt)。生成脚本：[select_tasks.py](experiments/select_tasks.py)。

从主比较 150 题中，按**构建批次 × 提取类型**比例分层，用最大余数法分配 40 个名额，再按固定 SHA256 次序抽取。没有读取模型成功/失败结果来选择任务。样本含 38 个仓库。

| 构建批次 | 提取类型 | 150 题中的数量 | 抽取数量 |
| --- | --- | ---: | ---: |
| 较早 | Direct | 53 | 14 |
| 较早 | Adapted | 44 | 12 |
| 较早 | Composite | 3 | 1 |
| 较晚 | Direct | 3 | 1 |
| 较晚 | Adapted | 32 | 8 |
| 较晚 | Composite | 15 | 4 |
| 合计 | | 150 | 40 |

这里的“较晚批次”是 **150 题内部的 50 题**，不是扩展评测的另外 50 题；它不是新的 benchmark 分类或难度等级。任务 ID 和存储字段中的旧名称保持不动。

40 题的功能类别分布也保存在 JSON；不保证每类足够做显著性比较。三个调试题从剩余 110 题中各取一种 lift type，与正式样本不重叠。

运行前校验固定清单：

```bash
python3 -B docs/paper/experiments/select_tasks.py --check
```

执行后不要因为任务难、Full 失败或 No-source 反而成功而换题。如果基础设施确实阻断一题，保留记录并标为待完成，先解决环境，不偷偷改变样本。

## 4. 两组必须相同、必须不同的内容

| 项目 | Full Source | Contract Only |
| --- | --- | --- |
| 公开行为契约、API、排除项、交付要求 | 相同 | 相同 |
| 新包名称、输出目录 | 相同 | 相同 |
| 完整原仓库：代码、docs、上游 tests、资源 | 可见 | 不可见 |
| benchmark Public / Hidden tests | 不可见 | 不可见 |
| reference solution、隐藏 metadata、源码定位 hints | 不可见 | 不可见 |
| agent、model、provider、tools、压缩设置 | 相同 | 相同 |
| 允许的第三方依赖与离线安装材料 | 相同 | 相同 |
| 模型调用以外的互联网访问 | 阻断 | 阻断 |
| agent 工作区与会话 | 每题独立 | 每题独立 |
| source-free evaluator 和四个门 | 相同 | 相同 |

契约本身的示例、项目名、API 名称保持一致；不要为了 No-source 改写需求。只允许修改“源码是否可用、去哪里查看”的环境说明，以及明显要求读取源码的操作提示；保存完整 prompt 和两组 diff，不新增解题提示。

目标源码包不得通过预安装 distribution、pip cache、wheel、压缩包、`.git`、旧 workspace 或工具搜索重新出现。先检查允许依赖是否传递引入原项目；若引入，需解决两组共同环境的可见性，不能只在 No-source 删除第三方依赖造成另一种消融。

source-free 是 **evaluator 环境**约束；本实验还要额外保证 No-source 的 **agent 阶段**看不到仓库。仅把 evaluator 设为断网不足以实现消融。

### 固定预算

Luna 沿用已有主实验配置作为起点；Pro 使用对应 Main 配置，并核对服务器本地 profile：

- OpenHands；Luna profile：`openhands_gpt_5_6_luna_paper`；Pro profile：`openhands_deepseek_v4_pro_main`。
- 已保存 Luna 主实验记录的 model 为 `openai/gpt-5.6-luna`。当前 `agents.example.toml` 未包含上述 Luna profile；服务器须从已有 Luna 主实验配置保留/恢复，并核对工具兼容、provider 和压缩设置，不能直接把 Flash profile 改名视为相同配置。这里的 Luna 指现有 API 模型配置，运行仍使用 OpenHands。
- 120 steps；context window 131072；reserved output 8192；逐题 agent timeout 3600 秒。
- token condenser，保留设置一致；不额外增加 2M 总 token cap。
- 每个模型–任务–条件一个正式 attempt；不对失败追加 repair pass。
- provider/model ID、temperature/seed 等实际支持的参数完整记录；不支持 seed 就记录不支持，不宣称确定性。

运行顺序使用 JSON 中的 `arm_order`：20 题先 Full，20 题先 Contract-only，题目次序也固定。尽量成对就近运行，减少服务时间变化影响。

## 5. 当前代码支持到哪里：正式运行前必须完成

这是本方案唯一的软件准备环节，**不是现有 benchmark 或主实验有版本问题**。

| 能力 | 当前状态 | 处理 |
| --- | --- | --- |
| Full repository、No-hint、隐藏 benchmark tests | 已有 | 复用 CLI 和 Main profile |
| 真正 Contract-only | **未实现** | 增加 `source_context=contract_only` 并测试整个路径 |
| source-location hint | 已有 | 本轮不启用 |
| 单提交 Docker evaluator | 已有 | 用于 agent 与机械产物 |
| 正式机械 baseline | **未实现** | 按第 9 节另建通用算法 |
| 配对汇总分析 | **需补充** | 按第 10 节输出，不能直接把两组并入原表 |

### 5.1 Contract-only 实现清单（可交给服务器上的编码助手）

1. 在 `harness/featureliftbench/cli.py` 的 `--source-context` 和 `ablation.py` 的枚举、arm ID、环境变量序列化中加入 `contract_only`；运行记录必须显示真实条件。
2. 修改 `agent_runner.py` 的 `prepare_agent_workspace()`：No-source 不调用源码物化、裁剪或 fallback 复制。当前 `else` 会物化完整仓库，只改枚举是不够的。
3. 处理后续假定 `repo/` 必须存在的路径和 prompt 生成。完整任务、测试、source registry 仍由主机/evaluator 正常使用，不删除 benchmark 资产；只改变 agent 可见工作区。记录任务对应的 source identity，同时明确 `agent_source_available=false`。
4. 两臂使用同一受控 runtime。当前 `agent_docker.py` 默认网络为 `bridge`，还会只读挂载整个 `harness/`；其中 scripts/tests 可能含任务专用参考构造器或泄露答案。改为只暴露必要运行代码，检查镜像内文件和挂载内容。只读不等于不可读。
5. 配置两臂相同的出站限制：通过隔离网络及仅允许模型 API 的网关/代理调用模型，禁止访问源码站点、包索引及任意远端内容。仅设置代理环境变量而允许直接联网不算隔离；也不能直接 `--network none` 把模型调用一起切断。
6. 保存可见文件清单、挂载、网络策略测试结果和最终 prompt。网络网关配置因服务器部署而异，当前仓库没有可直接套用的完整防泄露网关。
7. 增加针对工作区、prompt、arm metadata 的测试，并做真实容器 smoke，确认 Full 可读源码、No-source 不可读，而两者模型 API 正常。

**不能替代 Contract-only 的已有选项：** `pruned_context` 仍提供代码；`short_prompt` 改的是 prompt；`--no-source-materialization` 属于 benchmark 检查而非 agent 输入消融；提示“不要看源码”也不等于移除源码。

### 5.2 Smoke 的验收条件

用三个调试题，检查两臂都能开始模型调用、写 submission、进入同一 evaluator；允许功能失败，smoke 不以成功率为验收。

- No-source 工作区及可访问挂载中没有原仓库、压缩源码、任务测试、reference 或任务专用生成器。
- 容器内不能取得原项目代码；既检查文件与可安装包，也检查直接网络访问。Full 同样不能下载额外材料。
- 两组契约文本与评分资产相同；prompt diff 仅涉及源码可用性说明。
- 逐题 metadata 记录正确 arm；两臂使用同一 evaluator，指标能落盘。
- 普通失败只产生一个正式 attempt；不同条件没有共享 workspace、会话或模型生成代码。

全部通过后才开始正式 40 题。若改了算法或 prompt，只重做 smoke，不把旧 smoke 成功值算入正式分数。

## 6. 服务器准备

下列命令使用 Linux Bash；从仓库根目录执行。服务器需要现有完整任务、源码 archive、受保护 evaluator 资产、离线依赖以及镜像。**仅 clone GitHub 不保证包含这些本地大文件。** 沿用你已用于主实验的服务器数据目录；新 checkout 需单独传输这些材料并确认链接目标可用。

```bash
python3 --version                       # >= 3.11
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .              # pyproject.toml 在根目录，不在 harness/
python -B docs/paper/experiments/select_tasks.py --check
python -B -m featureliftbench.cli run-agent --help
docker version
```

保留已有 `.env` / `harness/config/agents.toml`，不存在时才从 example 建配置，填入服务器自己的 API 参数。不要把凭据写进本文命令、日志或传输给其他人。

校验 43 个任务目录：

```bash
python - <<'PY'
import json
from pathlib import Path
data = json.loads(Path('docs/paper/experiments/source_ablation_40.json').read_text())
ids = [t['task_id'] for t in data['tasks']] + data['smoke_task_ids']
assert len(set(ids)) == 43
for task_id in ids:
    p = Path('benchmark/tasks') / task_id
    assert (p / 'TASK.md').is_file(), p
    assert (p / 'metadata.json').is_file(), p
print('43 task packages found; source archives/evaluator assets still require smoke verification')
PY
```

在第 5 节实现完成后，指定两组共同使用的镜像，记录 ID。下面名称必须替换成服务器实际准备好的镜像，不提供猜测的 tag：

```bash
export FLB_AGENT_IMAGE='YOUR_PREPARED_AGENT_IMAGE'
export FLB_EVAL_IMAGE='YOUR_EXISTING_EVALUATOR_IMAGE'
docker image inspect "$FLB_AGENT_IMAGE" --format '{{.Id}}'
docker image inspect "$FLB_EVAL_IMAGE" --format '{{.Id}}'
git rev-parse HEAD
```

API 经隔离网关可达的 Docker network 由服务器配置后指定：`FEATURELIFTBENCH_AGENT_DOCKER_NETWORK`。默认 bridge 不能作为已通过输入隔离的证明。环境资源先以一个 worker 做 smoke，再按实测 RAM、CPU、磁盘增长和 API 并发限额决定是否增加并行度。

## 7. 运行命令

### 7.1 单题模板

**以下 Contract-only 命令是实现第 5 节以后使用的接口约定；当前 checkout 会拒绝该枚举值。不要直接批量运行。** Full 使用现有枚举。两个条件均须先通过新的可见性 smoke。

```bash
export FLB_TASK_ID='TASK_ID_FROM_THE_FIXED_LIST'
export FLB_SOURCE_CONTEXT='full_repository'  # 第二臂改为 contract_only
export FLB_RUN_ID='source-ablation-40-r1'
export FLB_PROFILE='openhands_gpt_5_6_luna_paper'
export FLB_MODEL_DIR='gpt-5.6-luna'

python -B -m featureliftbench.cli run-agent \
  "benchmark/tasks/$FLB_TASK_ID" \
  --agent openhands --agent-profile "$FLB_PROFILE" \
  --agent-config harness/config/agents.toml --env-file .env \
  --source-context "$FLB_SOURCE_CONTEXT" --prompt-style standard \
  --no-agent-source-hints --no-agent-public-tests \
  --no-td-cognition --no-exec-contract --no-self-contract --no-test-first-lift \
  --agent-docker --agent-docker-image "$FLB_AGENT_IMAGE" \
  --eval-docker --eval-docker-image "$FLB_EVAL_IMAGE" \
  --timeout-seconds 3600 --num-workers 1 \
  --extra-agent-passes 0 --max-task-attempts 1 \
  --retry-rate-limit 1 --retry-transient-api 1 \
  --output "experiments/python/openhands/$FLB_MODEL_DIR/$FLB_RUN_ID/$FLB_SOURCE_CONTEXT/$FLB_TASK_ID"
```

模板显式关闭 runner 的整题自动恢复重试；SDK 的请求级重试另记在配置中，两组一致。每次启动必须用不存在的新输出目录，CLI 本身可能归档并覆盖已存在的 run。

正式 40 题按 JSON `tasks` 顺序执行，每题按 `arm_order` 运行两次上述模板。smoke 另用 `source-ablation-smoke-r1` 目录及三题清单。第二模型只改 profile、model directory，仍使用同一任务与条件次序；可反转每题两臂次序作为第二模型的预定执行顺序并记录。

### 7.2 中断与恢复

**不要直接使用默认 `--resume` 或 `--skip-completed`。** 当前 CLI 的默认 retry statuses 包含 failed/missing_submission，可能重新尝试失败题。

恢复调度时按每个 task/arm 的 `run.json` 判断：

1. 已有完整 terminal run：跳过，失败也跳过。
2. 已启动但无 terminal run：保留整个目录，标为 interruption；先判定是外部中断还是任务超时。达到 3600 秒的任务超时计失败，不算可无限重试的基础设施故障。
3. 确认的外部中断可放到新 attempt 目录恢复，记录原因和采用哪次结果，不覆盖旧文件，不选择最好一次。
4. 尚未启动：按原次序运行。

纯 API 不可用、Docker 启动失败、缺资产等先列为 infrastructure pending；不得按成功率有选择地修复。主分析在 40 个配对齐全后出表；若最终无法补齐，同时给 assigned-40 的保守结果和完整配对结果，并列出缺失原因。

CLI 退出码 1 可能只是功能失败，不能自动认为实验系统崩溃；以 `run.json` 和 evaluator 记录判断。终止后先确认服务器没有对应活动容器/进程，再恢复同一任务。

## 8. 成本和工期控制

| 范围 | agent 次数 | evaluator 次数（通常至少） |
| --- | ---: | ---: |
| Luna smoke：3 题 × 两臂 | 6 | 6 |
| Luna 正式：40 题 × 两臂 | 80 | 80 |
| 可选 Pro 正式 | +80 | +80 |
| 可选机械 baseline | 0 | +40 |

80 次正式调用在每题 3600 秒上限下，串行 agent 时间上界为 80 小时，另外还有评测与启动开销。不是预计耗时。若增加并发，理想时间约按 worker 数缩短，但 API 限流和资源争用会改变实际情况。

先用 6 次 smoke 记录实际 tokens、缓存计费、wall time 和账单。粗估单模型正式费用为两臂各自 smoke 平均每题费用乘 40 后相加；三个任务只能粗估，需留预算余量。不使用未经核对的单价估算。

预算不足时，优先完成一个模型的完整两臂，不要给两臂不同 steps 或 timeout。复用已有 Full 是节省 40 次调用的可选方案，但必须按同一 40 题逐题匹配，并说明运行时间和网络/可见性设置的差异；本方案默认重新做成对 Full，主实验原分数保持不动。

## 9. 第二阶段：机械提取 baseline 规格

名称建议：**Static Import-Closure Copy**。固定同一 40 题，提交同一个 evaluator。

### 输入和算法

输入限于与 Full 相同的仓库、public contract 和允许依赖。不得读取 reference、benchmark tests、source-location hints，或仅作者 metadata 中的答案映射。

1. 从公开契约提取要求的导出 API。用固定解析规则，记录原文位置。未能解析的条目记为 unresolved，不靠人工逐题补答案。
2. 用 AST 索引仓库中的函数/类/赋值及导出，按完整名称、末级名称和公开模块路径匹配。固定歧义排序规则，保存全部候选和最终选择；不要依据 hidden test 选入口。
3. 对选中的模块递归计算静态本地 import closure，复制模块及必要父包。相对导入、包 `__init__` 和显式重新导出必须处理；第三方依赖使用原允许列表。
4. 将本地模块整体放入新包内部命名空间，改写能静态解析的本地 import；按公开输出 API 生成薄导出适配层。复制选中包目录的非代码资源，保留相对路径；具体排除 `.git`/cache/build 等规则在正式评测前固定。
5. 不改函数行为、不用 LLM 补代码、不做基于 evaluator feedback 的修复循环。动态 import、注册机制和无法机械解决的 API reshape 记录为算法限制。
6. 产物必须实际包含搬移的源码，不能只 `import` 原项目。生成一次，评测一次；把检索失败、复制失败、API mapping 失败与 evaluator 的失败门分开保存。

在三道 smoke 题上调通通用代码并冻结算法后，再做正式 40 题。不能看正式失败后逐题加例外再称为原 baseline。

### 现有代码如何复用

`harness/scripts/audit_upstream_direct_submission.py`、`audit_contract_entailment.py` 和 `build_oracle_submission.py` 可供阅读模块复制与评测接口；其中有历史 gate 规则、任务特例、reference 依赖或缺 API 的 stub。**不能直接把这些旧校准分数当成这次公平 baseline**，也不要把其“复制通过即缺陷”的旧判据带入论文。

新的构造器尚未实现，建议放在 `harness/scripts/`，输入 public task/workspace 与输出路径，写出 `baseline_manifest.json`：API 匹配、复制文件、import rewrite、资源策略、未解决项、耗时、代码 revision。构造器只能访问 agent-visible staging view；不要让它任意读取完整 task directory。

生成产物后的评测已有真实 CLI：

```bash
python -B -m featureliftbench.cli eval \
  "benchmark/tasks/$FLB_TASK_ID" \
  "experiments/methods/static_import_closure/r1/$FLB_TASK_ID/submission" \
  --docker --docker-image "$FLB_EVAL_IMAGE" \
  --output "experiments/methods/static_import_closure/r1/$FLB_TASK_ID/eval"
```

如果大量失败只是 API 名称解析没工作，先在 smoke 修通解析再启动正式批次。正式结果仍需报告这类失败，不能丢弃分母。可选 broad vendoring 是另一种 baseline，不能失败后临时切换算法并合并分数。

## 10. 结果怎么整理、怎么写进论文

### 10.1 保存内容

原始运行进入第 7 节的 `experiments/python/openhands/...`；机械运行进入 `experiments/methods/static_import_closure/...`。派生汇总放 `reports/paper_analysis/source_ablation_40/`。小型运行登记放 `experiments/registry/`。

每个 task/arm 至少保存：

- task ID、model/provider/profile、arm、attempt、调度次序与开始结束时间。
- 实际配置、可见 prompt、工作区可见文件清单、源码可用性检查、镜像 ID、执行命令（去凭据）。
- `run.json`、`eval/result.json`、最终 submission、完整轨迹与 stdout/stderr。
- Build / Public / Hidden / Isolation、functional gate、first failure gate、steps、token 各计数字段、wall time。
- 基础设施异常与重试原因、计入分析的 attempt ID；缓存 token 与总 token 分开，缺失 usage 不填零。

功能通过只读 evaluator 的 `scores.functional_gate`，不要把 agent status 或“生成了文件”当作通过。所有四个门通过才算 pass。明确 first failure 是评分顺序上的首个失败，不是已证明的因果根因。

单题调度输出不自动构成原有 `suite.json` 格式；不要直接套 `analyze_benchmark_suite.py` 并期待它遍历所有嵌套单题目录。补充分析器应按固定 JSON 的 40 个 ID，逐个读取两臂 `run.json` / `eval/result.json`，验证每格唯一后汇总。

### 10.2 主结果表

| Model | N pairs | Full pass | Contract-only pass | Δ (percentage points) | Full-only | No-source-only | 95% paired CI |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-5.6 Luna | 40 | 待运行 | 待运行 | 待运行 | 待运行 | 待运行 | 待运行 |
| DeepSeek V4 Pro（可选） | 40 | 待运行 | 待运行 | 待运行 | 待运行 | 待运行 | 待运行 |

令 b 为 Full 成功且 No-source 失败的任务数，c 为相反情况；则 Δ = 100 × (b − c) / 40。另保留 both-pass、both-fail，四类之和必须为 40。

- 两侧 exact McNemar：在 b+c 个不一致配对上做 p=0.5 的精确二项检验；b+c=0 时 p=1。
- 差值区间：同一 task 的两臂始终一起 bootstrap，10000 次，固定 seed。样本有 38 个仓库，再给 repository-cluster bootstrap 敏感性区间：抽仓库并保留其全部已选任务。
- 分层配额有四舍五入，主结论写“on the 40-task stratified sample”；若估计 150 题总体效应，额外按 population_n/sample_n 做分层加权并匹配相应重采样。不要把样本比例未经解释当作总体精确估计。
- 若把两个模型的 p 值作为两个确认性检验，报告 Holm 调整；效果量和不一致配对数优先于单个 p 值。
- 不把 80 次运行当作 80 道独立任务；不从 40 题细分成很多小类别后作强泛化。

辅助图用两臂 **40 题为同一分母** 的 first-outcome 堆叠条形图，标出 pass、无可用产物、Build、Public、Hidden、Isolation 等互斥类别。若另外画 failures-only 图，必须标出各自失败总数，不能混用分母。

机械 baseline 表报告：40 题 functional pass、构造阶段失败、评分门分布、耗时；可对比同样 40 题的 Full agent。RRES/Copy 只对成功产物统计，注明分母，不把大小或 overlap 纳入 pass，不用单纯低 overlap 推断“理解”。

### 10.3 论文落点

在实验协议增加一个 `Source-evidence ablation` 小节；结果中用一张紧凑配对表回答仓库证据收益。机械 baseline 放同一补充实验小节或附录，根据结果信息量决定。

在完成前不往 Abstract 填预期结论。完成后按数据写，例如：

> On a fixed, stratified sample of 40 tasks, providing the complete source repository changed functional success from X/40 to Y/40 under the same agent and resource budget. The paired difference was Z percentage points (...).

该实验隔离“仓库证据是否可用”；它不单独证明所有行为失败属于 contract closure，也不替代系统失败归因。

## 11. 完成标准与交接

- [ ] 保存固定 40 题与 3 个 smoke 题；不根据结果换题。
- [ ] 实现并验收 Contract-only、两臂相同的网络和文件可见性控制。
- [ ] 六个 smoke 运行流程正常；确定预算、重试政策和正式配置。
- [ ] 第一模型 80 个正式单元完整，40 个配对可核对。
- [ ] 原始结果、submission、usage、轨迹及异常登记保存齐全。
- [ ] 配对表、首失败门图、统计区间和分母检查完成。
- [ ] 可选第二模型与机械 baseline 按预先决定的预算执行。
- [ ] 回传运行登记、汇总与原始目录；不覆盖原主实验和论文表格。

**当前可直接完成的是服务器数据准备和清单核对。正式运行前，先按第 5 节补齐 No-source 的输入隔离，再依次 smoke → Luna 两臂 → 配对分析；机械 baseline 第二阶段做。**

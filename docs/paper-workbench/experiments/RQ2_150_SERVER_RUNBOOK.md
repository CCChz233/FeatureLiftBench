# RQ2 全量扩展：服务器补实验与交付清单

日期：2026-09-27。状态：**操作方案；尚未运行新的 150 题 Contract Only 实验**。从项目根目录执行本文件中的相对路径命令。本文件不改变当前论文的结果数字；只有收到并核验新数据后才更新 `docs/paper/main.tex`。

## 1. 要回答什么，怎样最大限度复用现有结果

RQ2 包含两个不同问题：① 上游仓库证据是否帮助 feature lifting；② 这种帮助能否简化为机械搬运源码。当前论文已经有三个模型在同一 40 题上的 Full Source / Contract Only 配对实验，以及同一 40 题的 DSE 诊断实验。**这两部分先保留，尤其不要用主榜结果替换原 40 题 Full Source。**

**省成本方案**是新增 Luna × Python-150 × Contract Only，共 150 个新运行，复用主实验已有的 Luna × Python-150 Full Source 150 个结果，观察结论在全任务集上的覆盖情况。它能直接写成论文中的**描述性覆盖性检查**，不能升级为“150 题控制消融”的主效应。若目标是让 **150 题成为 RQ2 的受控主结果**，应执行表中 300 个新运行的严格方案。选择 Luna 是因为它已有完整主榜和已完成的 40 题配对组，并且不用把 Pro 的服务超时问题带入新的全量主比较。**扩展和模型选择发生在原 40 题结果已知之后**，写论文时如实披露，不称预注册或 outcome-blind model selection。除非另有研究目标，本轮不新增模型、不扩 DSE 到 150，也不改 150 道题或 evaluator。

| 分析 | 已有可复用 | 本次新增 | 可以写出的结论 |
| --- | --- | --- | --- |
| 原 40 题配对消融（主因果证据） | Luna / Pro / Qwen 各 40×2；固定题单及配对统计 | 0 | 在原实验控制条件下，仓库可见性与成功率有关 |
| 150 题覆盖性扩展（推荐） | 主榜 Luna Full Source 150 | Luna Contract Only 150 | 两个**不同运行批次**在同一 150 题上的描述性差异；不能称严格控制的 150 题消融 |
| DSE 机械提取诊断 | 现有 40 题正式 Docker 评分和原始结果 | 0 | 指定机械程序的能力边界；它获得入口映射，不能当第三个同输入 agent arm |
| 若坚持“150 题严格配对消融” | 可复用题目、契约、evaluator、分析代码；主榜成绩只作历史参照 | 同一新批次重跑 Luna Full Source 150 **及** Contract Only 150 | 才能报告新批次 150 对的配对效应及其统计检验 |

为何不能直接把 150 条主榜 Full Source 当成新消融的严格配对臂：主榜使用历史完整 harness mount；40 题消融采用仅挂载运行包的隔离模式，并屏蔽额外源码/包站点。即使 aggregate pass 恰好相同，已有 40 道题上主榜与消融 Full Source 的逐题结果也有 **4 道 Luna、2 道 Pro、10 道 Qwen** 不同。这是实测差异，不应把跨批次配对包装为单变量干预。150 题可以按 task ID 做对应表，但统计表和正文须写明不同批次、环境差异和结论边界。若审稿目标是消除这个限制，执行表中的严格方案，不能只补跑失败题。

## 2. 现有数据与版本先盘清楚

服务器先确认这些输入真实存在，并保存 SHA-256、Git commit、模型与镜像身份。以下本地位置只是索引，服务器应以自身保存的原始记录为准：

- 150 题身份：`docs/paper-workbench/writing/chapter2_python150_task_inventory.json`，上游冻结清单见其中 `release_manifest`；主榜逐题表：`reports/paper_analysis/python150_prime_v2_analysis_20260905/task_results.csv`。两者都必须恰好有同一组 150 个 Luna task ID。主榜 Luna 有 150 个保留运行，但只有 149 个 `eval/result.json`；未交付的那题仍保留在分母中，不可因缺评测 JSON 而丢行。
- 原 40 题固定清单：`docs/paper-workbench/experiments/source_ablation_40.json`；原始消融逐题与配对数据：`docs/paper-workbench/data/source_ablation_retained_20260921/`，原始完整服务器运行一般位于 `experiments/python/openhands/<model>/source-ablation-40-r1/<arm>/<task_id>/`。
- Pro 18 个 Contract Only 无提交/LLM 请求超时中，有 6 个恢复结果已纳入另一版、12 个仍保留原结果：`docs/paper-workbench/data/source_ablation_recovery_20260916/`。该版 Pro Contract 为 **7/40**；当前正文使用的原版为 **6/40**。不要无说明地拼接两版。若本轮不继续恢复 Pro，保持正文原版并报告该限制。
- DSE 正式结果：`experiments/dse/source_ablation40_v1_2_reviewed_20260926/`，重点保留 `freeze_manifest.json`、`formal_evaluation_identity_check.json`、`evaluation_receipt.json`、`functional_summary.json`、`evaluation_results.json` 与 40 个 `tasks/<id>/eval/result.json`。正文当前写 10/40、Build 首败 11、Primary 16、Extended 3；从原始结果复核后再沿用。
- 当前论文 RQ2：`docs/paper/main.tex` 的 `\subsection{RQ2: ...}`，表 `tab:paired-ablation` 和图 `fig:source-evidence`。150 题新数据不可直接覆盖原 40 题表或 DSE 图。

原 40 题分析脚本 `reports/paper_analysis/source_ablation_40_20260913/analyze.py` 内有旧目录断言；若运行于现有重组目录，需要先改成只读输入映射或另写副本，**不要**为了跑通而覆盖历史数据。当前 100 题选择文件只是一份未执行的备选设计，不把它当作已完成结果或本次 150 题任务清单。

## 3. 冻结本次 150 题协议

在调用模型之前写 `experiments/rq2_150_luna_contract_v1/protocol.json`，至少记录：本次目标、150 个 task ID/哈希、论文主榜 Full 150 的来源、选定模型与 provider 实际 ID、OpenHands/工具版本、配置文件哈希、prompt 风格、预算、镜像 ID、Git commit、evaluator capsule 与依赖版本、网络规则、重试规则、数据保留规则。不要从文档中的旧口径推断今天的预算。**当前本机的 `harness/config/agents.toml` 没有 Luna profile**；服务器必须找到原 Luna 实际 profile/保存配置或重建并留存配置差异，不能用 Flash profile 换名。若服务器也无法确认 Luna 端点/配置，暂停 agent 运行；届时新结果不能称为原 Luna 的延伸。

Contract Only 的 agent 工作区应有公开 `TASK.md`、删减后的 `metadata.json`、`requirements.lock` 和 `submission/`；没有 `repo/`、benchmark 公共/隐藏测试、参考答案、具体任务的 `evaluation/` 文件或源码定位提示。它可以写自己的测试。运行时须启用 supplementary isolation，使 agent 只挂载必要的 `featureliftbench` 运行包（其中仍有通用工具实现），并阻断从网络、预装包、cache、wheel 等路径重获目标项目。评测端仍用同一冻结、断网的 Docker evaluator，功能通过定义仍是 Build ∧ Primary ∧ Extended ∧ Isolation；`run.status` 和 agent 退出码**不是**功能分数。

预算必须从原 Luna 40 题和服务器现存配置核实：旧记录持久化 OpenHands `max_iterations=500`、逐题 wall timeout 3600 秒、context 131072、reserved output 8192；Luna 旧 40 题的 `agent_max_steps` 为空。**Pro 另有 harness 120-step limit，不要误套到 Luna。** 如模型端点、condenser、镜像或预算无法按旧组重现，记录差异并把新 150 题明确命名为新批次；不要补改旧数据。

预先固定重试政策：一个 task 的首次完整 agent attempt 作为保留结果；普通功能失败、步数用尽、有包未过门均不得重刷。只有原始事件能证明模型 API/运输层故障并导致无可评测 submission 时，才可新建独立 attempt 目录恢复；**默认每题最多 3 次 attempt（首轮 + 至多 2 次服务故障恢复）**，若原实验政策更严格则沿用原政策。保留每次 attempt 和原因，选**最早符合政策的 attempt**，不能择优。仍未解决的基础设施失败单列，分母仍是 150，提供可能结果的上下界/敏感性结果。

## 4. 服务器执行顺序

### 4.1 只读预检与题单

确认 Docker 可用，检查冻结清单、模型 profile、API 可达性以及镜像 digest。评测代码请使用服务器已验证的 Python 3.12 环境（本地默认 `python3` 是 3.9，不能运行该 harness）。生成这次的 150 题列表；不要用 `source_ablation_100.txt` 或临时按难度筛题。示例：

```bash
mkdir -p experiments/rq2_150_luna_contract_v1
python3.12 - <<'PY'
import json
from pathlib import Path
p = Path('docs/paper-workbench/writing/chapter2_python150_task_inventory.json')
data = json.loads(p.read_text())
ids = sorted(row['task_id'] for row in data['tasks'])
assert len(ids) == len(set(ids)) == 150
assert all((Path('benchmark/tasks') / tid / 'metadata.json').is_file() for tid in ids)
Path('experiments/rq2_150_luna_contract_v1/task_ids.txt').write_text('\n'.join(ids) + '\n')
PY
sha256sum experiments/rq2_150_luna_contract_v1/task_ids.txt
git rev-parse HEAD
python3.12 -B docs/paper-workbench/experiments/analyze_rq2_150.py --preflight
```

这里的镜像变量和下文 `FLB_PROFILE` 要由服务器管理员按已有 Luna 运行设置填写。不要把 `.env`、密钥或未脱敏的认证日志放入交付包。

### 4.2 三题 smoke：先验可见性，再看模型是否能交付

使用原固定清单中的 `smoke_task_ids`（已覆盖不同类型），放在独立的 `smoke/` 目录。先做**不调用模型**的工作区检查。例如从项目根目录生成三题的预览工作区，检查没有 `repo/`、评测测试和参考答案：

```bash
PYTHONPATH=harness python3.12 - <<'PY'
import json
from pathlib import Path
from featureliftbench.ablation import AblationOptions
from featureliftbench.agent_runner import prepare_agent_workspace
manifest = json.loads(Path('docs/paper-workbench/experiments/source_ablation_40.json').read_text())
for tid in manifest['smoke_task_ids']:
    task = Path('benchmark/tasks') / tid
    metadata = json.loads((task / 'metadata.json').read_text())
    workspace = Path('experiments/rq2_150_luna_contract_v1/smoke/workspace_preview') / tid
    prepare_agent_workspace(task, workspace, metadata, ablation=AblationOptions(
        source_context='contract_only', mount_public_tests=False,
        expose_source_hints=False, prompt_style='standard'))
    assert not any((workspace / x).exists() for x in (
        'repo', 'public_tests', 'hidden_tests', 'reference_solution', 'evaluation'))
    print(tid, sorted(p.name for p in workspace.iterdir()))
PY
```

再验证网络不能取回原项目，但模型 API 能工作；最后只跑三题实际 smoke。实际运行后检查 `agent/agent_visible_inventory.json` 中 `repo_present=false`、`agent_source_available=false`，`run.json` 中 `source_context=contract_only`、`agent_harness_mount=package`，source hints/public benchmark tests 均不可见。smoke 结果不作为正式 150 次 attempt，也不能拿来修改任务或提示以适配测试结果。若可见性或镜像检查失败，停在 smoke 修复环境并记录改动。

### 4.3 正式运行 150 题

先在服务器执行 `PYTHONPATH=harness python3.12 -B -m featureliftbench.cli run-agent --help` 对照当前 CLI。以下是**模板，不是未填变量即可执行的完整命令**；用与旧 Luna ablation 一致的 profile、模型 provider 和镜像固定值，且每次输出到新目录：

```bash
export FEATURELIFTBENCH_SOURCE_ABLATION_ISOLATION=1
export FLB_PROFILE='SERVER_VERIFIED_LUNA_PROFILE'
export FLB_AGENT_IMAGE='SERVER_VERIFIED_AGENT_IMAGE'
export FLB_EVAL_IMAGE='SERVER_VERIFIED_EVAL_IMAGE'
export FLB_AGENT_NETWORK='SERVER_VERIFIED_AGENT_NETWORK'
export FEATURELIFTBENCH_AGENT_DOCKER_NETWORK="$FLB_AGENT_NETWORK"
docker image inspect "$FLB_AGENT_IMAGE" --format '{{.Id}}'
docker image inspect "$FLB_EVAL_IMAGE" --format '{{.Id}}'
mkdir -p experiments/rq2_150_luna_contract_v1/driver_logs

while IFS= read -r task_id; do
  out="experiments/rq2_150_luna_contract_v1/runs/contract_only/$task_id"
  if test -e "$out"; then
    echo "Existing output; inspect against retention policy: $out" >&2
    exit 1
  fi
  PYTHONPATH=harness python3.12 -B -m featureliftbench.cli run-agent \
    "benchmark/tasks/$task_id" \
    --agent openhands --agent-profile "$FLB_PROFILE" \
    --agent-config harness/config/agents.toml --env-file .env \
    --source-context contract_only --prompt-style standard \
    --no-agent-source-hints --no-agent-public-tests \
    --agent-docker --agent-docker-image "$FLB_AGENT_IMAGE" \
    --eval-docker --eval-docker-image "$FLB_EVAL_IMAGE" \
    --timeout-seconds 3600 --num-workers 1 \
    --extra-agent-passes 0 --max-task-attempts 1 \
    --retry-rate-limit 1 --retry-transient-api 1 \
    --output "$out" \
    > "experiments/rq2_150_luna_contract_v1/driver_logs/$task_id.log" 2>&1
  rc=$?
  printf '%s,%s\n' "$task_id" "$rc" \
    >> experiments/rq2_150_luna_contract_v1/driver_exit_codes.csv
  # CLI 的退出码 1 也可能只是功能未通过；必须读取 run.json/eval/result.json 判定。
  if test "$rc" -gt 1; then
    echo "Runner/config error; inspect logs before continuing: $task_id" >&2
    exit "$rc"
  fi
  if ! test -f "$out/run.json"; then
    echo "No run.json; classify this attempt before continuing: $task_id" >&2
    exit 2
  fi
done < experiments/rq2_150_luna_contract_v1/task_ids.txt
```

实际服务器的配置路径、网络与可用 flag 若不同，以核实后的实际命令为准，保存完整脱敏命令行。逐题检查输出：`run.json`、`agent/agent_visible_inventory.json`、`workspace/TASK.md`、`agent/openhands_events.jsonl`、`agent/usage.json`、`submission/`；**有可评测提交时**还要有 `eval/result.json`。如果缺文件，不要把它当默认 Build failure；调查并标记真实原因。CLI 返回码 1 可能只是功能失败，不能直接当基础设施故障。脚本因中断停下时，按固定 `task_ids.txt` 核对哪些题已有完整 `run.json`、哪些题只有半成品目录；人工登记半成品并按预定恢复政策另建 attempt，再继续尚未启动的题。不得删除已有记录或使用会按 `failed`/`missing_submission` 扩大重试范围的默认 `--resume`。

### 4.4 严格 150 题配对升级（只有准备采用该论文表述时执行）

保留同一新批次 Contract Only 初态、任务、evaluator 和配置，再以 `--source-context full_repository` 跑 **全部 150 题**到新的 `runs/full_repository/`。两臂的 supplementary isolation、package-only harness mount、模型/profile、预算、依赖、镜像与重试政策必须一致；唯一设计差异是 agent 可见的上游 repo 及相应环境说明。保存两臂完整 prompt diff 和逐题配置比对。历史主榜 Full 仍单独存档，不并入这 150 对。

### 4.5 生成逐题表；身份审计通过后才写正文

本仓库提供只读分析入口；它对 150 题做唯一键连接、核对新运行的 Contract Only 可见性/评测方式，并生成逐题表和描述性计数：

```bash
python3.12 -B docs/paper-workbench/experiments/analyze_rq2_150.py \
  --runs experiments/rq2_150_luna_contract_v1/runs/contract_only \
  --output experiments/rq2_150_luna_contract_v1/analysis
```

阅读 `analysis/readiness.json`：有任何缺题、配置/可见性或评分不一致时，先修数据身份或记录 unresolved，不得抄 `descriptive_results.json` 进论文。脚本的 `paper_ready=false` 是有意设置：它无法从汇总 CSV 自动证明跨批次评测环境完全一致，也无法替人选择服务故障恢复 attempt。服务器还必须交 **150 行身份审计表**，逐题比较主榜与新运行的 `spec_hash`、目标 API/公开契约、依赖锁、评测文件或 capsule digest、镜像及 run identity；原主榜无 `eval/result.json` 的题通过冻结 evaluator 文件/manifest 比对。若关键契约或 evaluator 不同且不能重新评分到共同版本，这道题不能硬算作同一任务对照，应停止全量可比性声称或改做新批次两臂严格实验。审计记录所有差异及处理，不只给 `matches=true`。

只读脚本输出 `contract_task_outcomes.csv`、`main_full150_vs_new_contract150.csv`、`descriptive_results.json`（仅机器核对齐全时）和 `readiness.json`。只输入新 Contract Only 一臂时，它**不产生受控实验的 p 值**，也不会自动替换 40 题旧结果。人工按预定政策核实异常、150 行身份及 evaluator 以后，才能生成最终表格和英文文字。

若执行了 §4.4 的新批次 Full Source 150 题，在上面的分析命令追加 `--full-runs experiments/rq2_150_luna_contract_v1/runs/full_repository`。机器核对两臂题目、配置、可见性和可用评测 capsule 一致后，另生成 `paired_150.csv` 与 `paired_150_stats.json`（两臂通过数、2×2、百分点差、100,000 次成对 bootstrap 区间、仓库聚类敏感性区间和 exact McNemar）。仍需人工审查无提交/服务错误、prompt 功能义务和全部保留 attempt；脚本不替代论文证据复核。

## 5. 最终必须交付什么

建议在服务器形成 `experiments/rq2_150_luna_contract_v1/delivery/`。正式交付至少包含：

1. **协议和身份**：`protocol.json`、`task_ids.txt`、冻结清单/任务契约/依赖锁/evaluator capsule 的路径与哈希、Git commit、model/provider 实际 ID、OpenHands 及镜像 digest、脱敏配置和命令、日期、重试政策；另交上述 **150 行逐题跨批次身份审计表**；若升级严格配对，再加新两臂一致性检查。
2. **150 行 Contract Only 逐题表** `contract_task_outcomes.csv`：`task_id`、repo ID、cohort、lift type、run 路径与哈希、attempt/保留原因、是否生成可评测提交、`functional_pass`、Build/Primary/Extended/Isolation 各门布尔值、**first_failed_gate**、agent exit/status、API/工具/超时错误码、实际步数/时长、eval capsule digest、镜像与配置身份。空提交单独分类，不能算 Build failure。
3. **可见性审计** `workspace_audit.csv`：150 题逐行 `repo_present=false`、source hints/tests/reference/evaluation 不可见、package-only harness mount、阻断原项目获取途径、prompt/公开契约哈希与审计结果。失败样本留事件和说明。
4. **保留选择与异常**：`retained_manifest.csv` 列出每题所有 attempt、原始记录路径/哈希、被选中的 attempt 和理由；`infra_incidents.csv` 区分模型 API timeout、工具故障、Docker/依赖故障与普通功能失败。无提交但模型调用超时，不能写成 step-limit failure。
5. **原始私有证据**：每题 `run.json`、完整但脱敏的 events、实际 submission（含资源）、agent 可见 prompt/inventory、usage；对有可评测提交的题加 Docker `eval/result.json` 和各门日志；对每个成员文件计算 SHA-256。论文公开包只放合适的汇总/复现代码，私有评测材料另包保存。
6. **分析结果**：`main_full150_vs_new_contract150.csv` 按 task ID 一一连接、150 行无缺失；总通过率、交叉 2×2（both/full-only/contract-only/neither）、失败门分解、Direct/Adapted/Composite 及 earlier/later 分层、交付率和服务异常敏感性。标明此表为**跨批次描述性比较**。严格升级后另交 `paired_150.csv` 和 paired bootstrap CI、exact McNemar、repository-cluster sensitivity，并写清是否预先固定了分析规则。
7. **复用性证明**：指向主榜 Full 150、历史配对 40、DSE 40 的原始身份与摘要哈希；复核主榜 150 条及 DSE 40 条数量和评分来源。DSE 保留现有 `10/40`、首败门和 all-artifact source overlap 定义，不把高 Copy 直接等同于行为理解。
8. **论文更新候选**：一份可直接审阅的 RQ2 英文 Methods/Results/Threats 草稿、150 题新表 `.tex`/CSV、图源数据和可重生成脚本。原 40 题配对表与 DSE 诊断图不自动替换。数值必须从上述逐题表生成，不能手录猜测。

交付前检查计数：150 个唯一 task × 1 新 Contract 条件；若严格升级则 150×2。每题都必须有结论或明确的 unresolved infrastructure 状态，保留在分母内。压缩包应有 `SHA256SUMS`，验证可解压且所有成员哈希一致。**不要**把 `.env`、API key、上游源码归档或 hidden tests 混入公开论文材料。

## 6. 数据到手后怎样改 RQ2

推荐写法：40 题三模型**配对消融**继续作为“仓库证据是否有帮助”的主要受控证据；150 题 Luna 新结果另设一个 **full-benchmark coverage check**，清楚标注主榜 Full Source 与新 Contract Only 来自不同批次，列出配置差异和逐题敏感性；DSE 40 保持“机械搬迁的诊断性对照”。不能写“我们在 150 题上只改变了源码可见性”，也不能把 DSE/三模型 40 题与 Luna 150 题算作同一个 150 题三臂实验。

若完整跑出新批次两臂 150 题且核验一致，论文可以把 150 题 Luna 配对结果提升为 RQ2 的全量主分析；原 40 题多模型配对结果及 DSE40 留作跨配置/机制诊断。此时重算图、表、置信区间和所做检验族的多重比较；不得只改分母或把原 40 题结果拷贝进新 150 题组。

论文当前 Pro 结论仍受 18 个旧 Contract Only 超时无提交影响。已做的部分恢复只替换 6 个，另 12 个尚未解决；若要修改主文 Pro 数值，应先固定恢复政策、完成/透明报告剩余异常，再用同一 40 题配对数据整体重算统计，并保留原版作敏感性对照。本次 Luna150 扩展**不依赖**先完成该恢复。

## 7. 可以写入论文的验收门槛

- **省成本方案的最低门槛**：150 个固定 task 各有唯一保留结论；机器可见性和 Docker 评测检查通过；所有服务异常有原始证据、预定保留选择和敏感性界限；150 行跨批次身份审计确认公开契约、依赖与评分依据可比。满足后才把 `descriptive_results.json` 数字写成“跨批次覆盖性检查”，并把 `readiness.json` 的人工审核结论另行留档。主 RQ2 的因果主张仍来自原 40 题配对实验。
- **150 题受控主结果的最低门槛**：在上述基础上新增同一新批次 150 个 Full Source 初态运行；两臂逐题配置、prompt 的功能义务、任务和 evaluator 身份均核验；有 `paired_150.csv`、逐题 2×2、预定统计/置信区间及异常敏感性分析。满足后才写“150 题配对消融”。
- **任一方案未过门槛时**：保留全部记录，列出缺口；不把尚未核实的汇总数字或图表升格为论文正式结果。

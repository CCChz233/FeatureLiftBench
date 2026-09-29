# Claude Sonnet 5：第七配置服务器实验与论文数据交付

状态：待执行。本文档只规定新增实验和交付数据；**尚无 Claude 结果，不预填任何结果数字**。在项目根目录使用服务器上已验证的 Python、Docker、模型端点和冻结任务版本执行。

## 目标和运行量

在现有 150 道相同任务上增加一个完整的 **Claude Sonnet 5 + 固定 agent harness** 配置：

| 条件 | 正式 agent runs | 用途 |
| --- | ---: | --- |
| Main / Full Source | 150 | RQ1、RQ3、Fig. 5、Fig. 7、Fig. 8；同时作为 Claude 的 RQ2 Full Source 臂 |
| RQ2 Contract Only | 150 | 与 Claude Full Source 按 task ID 配对 |
| DSE | 0 | 复用现有模型无关的 150 题结果（31/150） |

因此新增 **300 个正式 agent-task cells**。Smoke、基础设施故障恢复、Fig. 7 的中间产物 Docker 复评不计入这 300 个正式 agent cells，但要单独记录。每格保留一个预先规定的结果，不按评测成绩择优。

本方案复用旧六配置的 Main 结果、旧三配置的 150 题 RQ2 结果及 DSE。**方法边界**：旧 RQ2 的 Full Source 来自历史 Main 批次；新 Contract Only 与历史 Main 可能有运行批次或 harness 隔离差异。按 task ID 配对可以算描述性差异和检验，但不能仅凭配对称所有四配置都是严格单因素控制实验。新 Claude 两臂应在同一冻结协议下执行，除了仓库证据的可见性外尽量一致；旧三配置差异须审计并在论文披露。若论文必须声称“四配置都严格控制”，需另行重跑旧配置的两个条件，300 次不足。

## A. 开跑前冻结（必须先于正式运行）

1. 固定论文所用的 **150 个 task ID**、任务包/契约/依赖锁/evaluator 版本。对照 `docs/paper-workbench/writing/chapter2_python150_task_inventory.json` 和当前论文 `docs/paper/main.tex`，不新增、删除或替换任务。保存清单、各输入 SHA-256、Git commit。
2. 保存模型的**实际 provider model ID**和版本、endpoint、OpenHands/harness 版本、agent profile（含 prompt、工具、上下文压缩设置）、步数/时间/token 上限、并发数、agent/evaluator 镜像 digest、网络与缓存规则。Claude 是新的 **model–harness configuration**，不能只填模型名称。密钥不得写入协议、日志或交付包。
3. 确认 Full Source 的工作区有公开 contract 与 pinned repository；Contract Only 保留同一公开 contract、允许的第三方依赖及锁定版本，但没有原仓库、source hints、benchmark tests、reference solution 或 evaluator 文件。检查网络、预装包、cache、wheel 路径不能在 Contract Only 取回目标项目。两臂评分均使用同一冻结、断网的 Docker evaluator。
4. 冻结保留规则：默认每格首次完整尝试；功能失败、步数耗尽不重刷。只有有原始日志证明的 API/运输/Docker 基础设施故障，才按预先写明的上限在**新 attempt 目录**恢复，保留全部 attempt、原因和选择记录。无法获得可评测提交也留在 150 分母中。
5. 先用少量覆盖不同 lift type 的任务做独立 smoke，验证 Claude 端点、工具调用、用量字段、两臂可见性及 Docker 评分；smoke 不并入正式 300 格。任何配置修正后重新冻结协议，再启动正式批次。

服务器先运行 `PYTHONPATH=harness python3.12 -B -m featureliftbench.cli run-agent --help` 核实当前 CLI。可参考 `docs/paper-workbench/experiments/RQ2_150_SERVER_RUNBOOK.md` 的工作区审计、运行和恢复方式，但那份文档的 **Luna profile、旧批次路径和旧运行数量不适用于 Claude**。正式两臂建议分别写入 `experiments/claude_sonnet5_150_v1/runs/full_source/` 与 `.../contract_only/`，smoke 和 attempts 分目录存放；不要覆盖任何既有运行。

## B. 每个正式运行必须保存

交付一个 **300 行**的 `run_manifest.csv`，唯一键为 `(condition, task_id)`；每行指向保留 attempt 和全部原始 attempts。至少含：`task_id`、repo ID、lift type、condition、配置/model ID、task/spec/evaluator/config/image hashes、run 路径、attempt ID、保留原因、agent 状态、可评测提交与否、`functional_pass`、Build/Primary/Extended/Isolation 四关状态、first failed gate、异常类别、steps、总 input/output/cache token、运行时间。

每格原始记录保留：`run.json`、agent 实际可见的 TASK/metadata/inventory、完整脱敏轨迹与工具 observation、逐请求 usage（含 request/response ID 与重试）、最终 `submission/` 全树、Docker `eval/result.json` 和日志（有提交时）。无提交、评测器错误、模型 API 错误分开记录，不能都算 Build failure。保存文件 SHA-256；私有 hidden tests 与密钥只在服务器保存，不放 GitHub。

为了让后续论文分析**确实能做**，额外保存：

- **RQ2**：两臂逐题结果和同任务身份审计；确认 contract、依赖、evaluator 相同，差异为 repo 可见性。交 `paired_claude_150.csv`，列出 both-pass、Full-only、Contract-only、neither 的逐题分类。
- **RQ3/source exposure**：Full Source 的 150 条完整轨迹，包括成功读取源码的 tool call、observation 内容和顺序；逐题入口映射使用当前冻结的私有分析映射，不给 agent。交 `source_exposure_claude.csv`、证据事件表、unknown/缺失日志表。源文件名提及或失败读取不能算 confirmed read。
- **Fig. 7**：Full Source 轨迹中每次可恢复的完整提交状态、事件顺序、逐请求 token 账本和最终 submission；对候选中间状态用同一冻结 Docker evaluator 离线复评，交最早通过 checkpoint、其后 token/response 数及不可判定原因。只有终态 submission 或汇总 token，**无法**补 Fig. 7。
- **Fig. 8**：Full Source 所有通过任务的完整最终 submission、参考包/源码快照身份、RRES/Copy 原始输入与逐题值。只报告成功产物；不能把失败格子的 footprint 填零。
- **定性案例**：推荐保留现有 40 个已审案例，另从 Claude 的 source-exposed behavioral failures 中按冻结的覆盖规则选 6 个，形成 **46 例**；逐例交选择依据、证据片段、人工审阅和主题标签。若坚持 42=7×6，须重新选取和复核旧样本，不能直接删 4 例而沿用旧叙述。

## C. 交付目录和验收

建议服务器交付目录（大轨迹可单独归档并提供校验和）：

```text
experiments/claude_sonnet5_150_v1/delivery/
  protocol.json                 # 冻结配置、任务/镜像/代码哈希、保留政策
  task_ids.txt                  # 与论文同一 150 题
  run_manifest.csv              # 300 行，每题两臂
  retained_attempts.csv         # 所有 attempt 和保留选择
  workspace_audit.csv           # 300 行，两臂可见性和身份
  infra_incidents.csv           # 异常与恢复
  paired_claude_150.csv         # RQ2 逐题配对
  source_exposure_claude.csv    # 150 行 Main 轨迹诊断
  exposure_events.csv           # confirmed read 证据
  fig07_checkpoints.csv         # eligible、首次通过、token/response、缺失原因
  fig08_artifacts.csv           # 成功产物的 RRES/Copy 输入和值
  qualitative_claude_6.csv     # 6 个审阅案例及证据
  sha256sums.txt                # 原始运行/分析文件校验和
  raw_runs/                     # 或指向服务器原始归档的 manifest
```

验收条件：同一冻结题集恰有 **150 个 Full Source + 150 个 Contract Only 保留格**，无重复键、无静默丢题；每格原始运行和评测身份可追溯；两臂 contract/evaluator 与可见性核对完成；四关/无提交/基础设施故障可区分；steps 和 token 能按论文口径复核；RQ3 轨迹、Fig. 7 中间状态、Fig. 8 成功产物的覆盖率和缺失原因明确。即使某项数据不可恢复，也交覆盖率与原因，不能补造数值。

## D. 数据到论文的更新映射（收到交付后执行）

| 论文位置 | 更新内容 |
| --- | --- |
| RQ1 Table 2 / Table 3 | Claude 的 150 题通过率、RRES/Copy、Steps/Tokens、按结构成功率；重排排名和成功率范围 |
| RQ2 Fig. 4(a,b,c) / Table 4 | Claude 两臂、逐题差异与 95% paired task bootstrap CI；四个配置的 exact McNemar **重新一起做 Holm 校正**；DSE 31/150 复用 |
| RQ3 Fig. 5 / Table 5 | Claude 的第一失败关分布；Main 总分母从 900 到 **1050**，四类结果和 source-exposure 全部重算。原 `241/303` 的分母是 behavioral failures，新分母是 `303 + Claude behavioral failures`，不是 1050 |
| RQ3 定性部分 | 保留旧 40 例并加入 6 个 Claude 案例；若主题或例证有变化，重写相应文字和 Fig. 6 |
| Fig. 7 | 添加 Claude 盒图和 eligible `n`；两面板样本可能不同，重算整体范围与图注 |
| Fig. 8 | 将 Claude 成功产物并入后，对**全部七配置**重新拟合 task fixed effects、bootstrap 和敏感性分析；重算入样任务/产物/仓库数，不只在旧图上加一点 |
| 全文 | six→seven 以及所有 aggregate counts、百分比、排序、图注、摘要、引言、结论和复现材料同步核对 |

现有绘图/分析代码有六模型、900 格及旧样本数的硬编码（例如 `docs/paper-workbench/figures/scripts/footprint_analysis.py`、`fig07_post_pass_execution.py`、`fig05_failure_stages.py`）。**服务器先交原始数据和上述逐题表，不要只交新图或摘要数字。**作者收到数据后扩展脚本、重新跑全部分析，逐项核对正文。当前 `docs/paper/main.tex` 尚未加入 Claude；不能在 300 格结果未核实前改写结果段落。

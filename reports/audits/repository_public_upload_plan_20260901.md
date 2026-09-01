# FeatureLiftBench 公开仓库整理与上传计划（2026-09-01）

> **Status: proposed**  
> 目标：在保持 GitHub 仓库公开的前提下，安全上传当前工作，保证服务器能够复现实验，同时不把凭据、尚未发布的隐藏评测资产和可再生成的大文件混入 Git 历史。

## 1. 当前基线

- 起始提交：`5f57fae21b928b06f6cfc7f46f77e2684c33823e`
- 分支：`main`
- GitHub：公开仓库；整理前本地 `main` 与 `origin/main` 同步
- 当前暂存区：5,397 个文件，其中 5,029 个新增、368 个修改
- 暂存文件工作区体积：约 119.1 MiB
- Benchmark 相关暂存文件：5,218 个
- 仓库中的本地大资产：
  - `experiments/`：约 6.5 GiB，原始实验与传输包，默认不进 Git
  - `benchmark/vendor-wheels/`：约 178 MiB，离线依赖，可外置
  - `benchmark/submissions/`：约 41 MiB，包含 Oracle/reference 输出
  - `reports/`：约 29 MiB，主要是小型派生分析
- 当前公开历史已经包含 Python-150 的部分 hidden tests；它们已经不能通过普通删除重新变为秘密。新增 Hard-50 隐藏评测仍可在首次推送前隔离。
- 已确认 `.env` 与 `harness/config/agents.toml` 不应进入 Git。
- 当前验证尚有一个待修复项：完整 harness 测试出现 10 个同源失败，原因是旧 Python-150 兼容 freeze 与新任务 spec hash 不一致。该问题修复并回归前不推送正式实验版本。

## 2. 目标仓库形态

### 2.1 GitHub 公开仓库保留

- `README.md`、`RUN.md`、`BUNDLE.md` 和 current 文档入口
- `harness/`、`docker/`、`integrations/`、正式 `scripts/`
- TASK、公开 metadata、requirements lock、public tests
- suite/freeze/source registry、内容哈希、版本和 provenance
- 论文正文、表格、可审查的聚合结果、审计报告
- 不含答案代码的服务器运行脚本与资产构建说明
- 小型、稳定、许可证允许分发且不能方便重建的运行依赖

### 2.2 本地/评测服务器专用 overlay

- 尚未公开的 Hard-50 hidden tests
- Hard-50 reference solutions 与 Oracle submissions
- API key、`.env`、`agents.toml` 和机器本地配置
- source archives、完整上游 checkout
- 原始模型轨迹、逐题 workspace、临时实验包
- 暂不适合进入 Git 历史的离线 wheels

这些资产不要求另建私有 GitHub 仓库。使用带 SHA256 的本地 server bundle 直接传到实验服务器；公开仓库只保存 manifest、校验和、构建脚本和恢复说明。

## 3. 今天可完成的快速路径

### 阶段 A：冻结并核对当前工作区

1. 记录当前 commit、freeze ID、candidate ID、文件数量和目录体积。
2. 导出暂存清单和大文件清单到本维护记录的配套 JSON。
3. 确认 `.env`、agent 配置、密钥、token、私钥和本地绝对路径未进入暂存区。
4. 不删除任何 Benchmark、freeze、reference 或原始实验。

**验收：** 当前工作有可核对的路径清单、哈希与恢复方式。

### 阶段 B：建立 public / evaluator 两层发布边界

1. 保留已经公开的 Python-150 测试资产，登记为 `released evaluation assets`，不再把它们描述为保密 holdout。
2. 将新增 Hard-50 的以下路径从公开提交中排除，但保留在本地：
   - `benchmark/hard50/**/hidden_tests/`
   - `benchmark/hard50/**/evaluation/oracle_manifest.json`
   - `benchmark/hard50_pilot/**/reference_solution/`
   - 新增的 `benchmark/submissions/**/oracle/`
3. 保留公开任务合同：TASK、public tests、metadata 的非泄漏字段、requirements lock、source/freeze digest。
4. 为 evaluator overlay 建立 manifest，逐项记录相对路径、大小、SHA256、对应 candidate/freeze ID。
5. 在 `.gitignore` 中使用精确路径规则，并对公开 README、manifest 和 checksum 设置显式例外。

**验收：** `git diff --cached --name-only` 不再出现新增 Hard-50 hidden/reference/oracle 内容；overlay manifest 能证明服务器拿到的是冻结版本。

### 阶段 C：外置可再生成的大资产

1. `experiments/` 继续执行“payload 不进 Git，registry/checksum 进 Git”。
2. source archives 不进 Git；服务器根据 `benchmark/sources/python200_hard_registry.json` 物化。
3. 将新增 vendor wheels 从普通 Git 提交中移出，生成 wheel manifest（文件名、平台、大小、SHA256、获取/重建命令）。
4. 若服务器必须离线运行，将 wheels 放入 server bundle；若网络可用，则按 lock/manifest 下载并校验。
5. 不使用 Git LFS 保存 hidden tests 或 reference solution。LFS 只解决体积，不解决公开泄漏问题。

**验收：** 所有外置资产都有固定输入、SHA256 和服务器恢复命令。

### 阶段 D：修复上传前阻塞项

1. 从 Python-200 candidate 与 600/600 Oracle 重验证结果生成 Python-150 v3 compatibility freeze。
2. 不修改已冻结的 evaluator/harness 内容，避免改变 Python-200 candidate ID。
3. 先运行 `test_contract_closure_gate.py`，再运行完整 harness 测试。
4. 重新检查 Python-200 candidate freeze 与 final freeze 身份保持不变。

**验收：** 定向测试通过；完整 harness 测试无失败；candidate/final freeze digest 未漂移。

### 阶段 E：拆分提交

按以下顺序提交，避免形成一个无法审查的百万行提交：

1. `benchmark: freeze Python-200 public task contracts`
2. `eval: add Python-200 runner and compatibility freeze`
3. `analysis: add reproducible reports and paper tables`
4. `docs: update paper, status, and server runbook`
5. `chore: define public release and server overlay policy`

每个提交只加入对应路径，并在提交后运行最低相关检查。纯仓库整理不与 evaluator 功能修复混在同一提交。

**验收：** 每个提交均可说明目的；没有凭据；没有新增隐藏答案；单文件均小于 GitHub 100 MiB 限制。

### 阶段 F：推送与服务器交付

1. 推送公开 `main`。
2. 在本地生成忽略的 `exports/python200-prime-server-<freeze-id>.tar.*`。
3. bundle 包含 evaluator overlay、wheels（若离线需要）、必要 source archives、manifest 和 SHA256；不包含 `.env`。
4. 使用 `scp`/`rsync` 将 bundle 单独传到服务器。
5. 服务器 clone 公开仓库，核对 commit；解包 overlay，核对 SHA256；再按 server runbook 构建镜像与运行实验。

**验收：** GitHub 可从全新 clone 完成公开检查；服务器以相同 commit + 相同 overlay manifest 启动 frozen experiment。

## 4. 上传后仓库整理

这部分不阻塞今天上传，但应使用单独整理提交完成：

1. 将根目录的 `run.sh`、`run_easy.sh`、`run_smoke.sh`、`start_run.sh`、`resume_run.sh`、`check_env.sh` 等逐项映射到正式入口。
2. 仍被文档引用的先改成带弃用说明的薄转发；无引用且已有替代的删除。
3. 删除可重建缓存：`.DS_Store`、`__pycache__`、`.pytest_cache`、`.ruff_cache`、未激活 venv。
4. 清理报告中的 `__pycache__`、临时 SQLite 和重复生成图；需要保留的分析产物必须能由 notebook/script 重建。
5. 更新 `docs/README.md`，确保 current 规范、论文、运行入口和维护手册两跳可达。
6. 每次正式实验后只提交 registry、checksum 和小型聚合报告，原始结果保持只追加并外置。

## 5. 公开 Benchmark 的发布口径

当前应区分两种“隐藏”：

- **已发布测试**：已经进入公开 Git 历史的 Python-150 测试。它们可用于 artifact reproduction，但不能再声称对未来模型完全保密。
- **未发布 holdout**：新增 Hard-50 evaluator overlay。在主实验冻结和跑完前不进入公开 Git；论文发布时再决定完全公开、延迟公开，或保留托管评测。

论文中应明确主实验的运行时间、commit、candidate/freeze ID，以及测试是否在运行时公开。这样即使之后开源 evaluator，也不会影响已完成实验的时间顺序和可审计性。

## 6. 需要维护者批准的高风险动作

以下动作执行前必须再次点名确认：

- 从公开提交中排除新增 Hard-50 hidden tests
- 从公开提交中排除 Hard-50 reference solutions 和新增 Oracle submissions
- 外置新增 vendor wheels
- 生成并传输服务器 evaluator overlay
- 后续删除根目录兼容脚本

这些动作只调整发布边界，不删除本地唯一资产，也不改变 Python-200 task/freeze 身份。

## 7. 最终验收清单

- [ ] 工作区资产有 Track / Ignore / Externalize / Keep 决策
- [ ] `.env`、agent 配置和凭据未被跟踪
- [ ] 新增 Hard-50 holdout 与 reference solution 未进入公开提交
- [ ] 原始实验 payload 和 source archives 未进入 Git
- [ ] 外置 wheels/overlay 有 manifest、SHA256 和恢复命令
- [ ] 兼容 freeze 问题已修复
- [ ] 定向测试与完整 harness 测试通过
- [ ] Python-200 candidate/final freeze 身份未漂移
- [ ] 提交按 benchmark/eval/analysis/docs/policy 拆分
- [ ] GitHub 全新 clone 可完成公开检查
- [ ] 服务器 bundle 可校验并启动 frozen experiment
- [ ] 上传后另开纯整理提交处理根目录和缓存

## 8. 建议执行顺序

```text
公开/私有资产分层
  → 修复 compatibility freeze
  → 定向与完整测试
  → 拆分提交
  → 推送公开仓库
  → 构建 server overlay bundle
  → 服务器校验并运行
  → 后续纯整理提交
```

这条路径不要求把仓库改为 private，也不要求把 6.5 GiB 实验目录或 178 MiB wheels 全塞进 Git。GitHub 负责保存可审查、可复现的公开源码与身份；服务器 bundle 负责交付尚未公开或体积较大的评测资产。

# TD-Cognition Pilot Runbook

**更新：** 2026-07-28 18:10（Asia/Shanghai）  
**模型：** `deepseek/deepseek-v4-flash`（API）  
**设计：** Baseline (`main`) vs `td_cognition`（Phase1 认知 → Phase2 注入实现）  
**故事：** [METHOD_TEST_DRIVEN_COGNITION.md](../../docs/METHOD_TEST_DRIVEN_COGNITION.md)  
**题集：** [`task_ids.txt`](task_ids.txt)（12 题）

## 当前状态（GPU176）

| 项 | 路径 / 值 |
| --- | --- |
| 主机 | `GPU176` → `/data1/FeatureLiftBench` |
| 协议 | **两阶段**（锁文件硬门闩已废弃） |
| Baseline（已完成） | `experiments/ablation/compare-20260728-155516/main` → **4/12 pass** |
| 旧 TD（作废） | 同 compare 下 `td_cognition/` → 12× `missing_submission`（runner 与锁文件冲突） |
| **当前 TD 重跑** | `experiments/ablation/td-cognition-twophase-20260728-180833` |
| Run ID | `td-cognition-twophase-20260728-180833`（见 `CURRENT_RUN_ID.txt`） |
| 日志 | `experiments/td_cognition_pilot/logs/td-cognition-twophase-20260728-180833.log` |
| tmux | session 名 `td_cognition_pilot` |

查看进度：

```bash
cd /data1/FeatureLiftBench
tmux attach -t td_cognition_pilot   # 或
tail -f experiments/td_cognition_pilot/logs/td-cognition-twophase-20260728-180833.log
```

## 协议（现行）

1. **Phase 1**：产出 `COGNITION.md` + `probes/`（可跑 pytest）；不实现 `submission/featurelifted/`。超时上限 1800s。轨迹：`agent_phase1/`。  
2. **Phase 2**：清空 `submission/`，把 Phase1 脚手架注入 TASK/OpenHands 提示，再实现。轨迹：`agent/`。  
3. 审计：`td_cognition_phase.json`。

## 服务器常用命令

```bash
cd /data1/FeatureLiftBench

# 仅 TD 臂（Baseline 已有时可跳过）
./run_experiment.sh --arm td_cognition \
  --task-file experiments/td_cognition_pilot/task_ids.txt \
  --run-id td-cognition-twophase-$(date +%Y%m%d-%H%M%S) \
  --workers 1 --timeout 3600

# 断点续跑（输出目录已存在时）
./run_experiment.sh --arm td_cognition \
  --task-file experiments/td_cognition_pilot/task_ids.txt \
  --resume experiments/ablation/td-cognition-twophase-20260728-180833

# 对照汇总时：Baseline 用旧 main，TD 用 twophase 目录，勿混报作废的锁文件那一臂
```

## 结果怎么比

- Baseline：`compare-20260728-155516/main/suite.json`（4 passed / 8 failed）  
- TD（有效）：`td-cognition-twophase-*/suite.json`（跑完后）  
- **不要**用 `compare-.../td_cognition` 当方法结果

## Go / No-Go

主指标：Functional Pass@1（12 题）。次要：Phase1 脚手架合格率、token/steps。

| 结果 | 动作 |
| --- | --- |
| TD 相对 Baseline 有稳定增益 | 扩题；可选 Oracle-Scaffold |
| 无增益 | 查 Phase1 质量 / Phase2 是否使用脚手架 → 修订或降级 |
| Phase1 大量空模板 | 加强 Phase1 提示后再复跑 |

# FeatureLiftBench TODO

当前目标：用 **OpenHands + `featureliftbench` CLI** 跑通 pilot5 与 main 全量，基础设施干净后再写论文级结果。

## P0：当前路径验证

- [ ] `featureliftbench setup` 通过（含本地 vLLM 或云端 API）
- [ ] `featureliftbench smoke` 通过 `check_openhands_smoke`
- [ ] `featureliftbench run --suite pilot5` → `docker_sandbox_failures==0`
- [ ] `featureliftbench run --suite main` 在 tmux 中可 resume

## P1：全量前

- [ ] `audit_task_dependencies.py` → 100 ok
- [ ] `infra-summary.json` → `infra_clean=true`（pilot 或 smoke 切片）
- [ ] 确认 `max_steps=180`、token/context audit 可验证

## P2：文档与债务

- [x] `flb.local.toml` + CLI（`setup` / `run` / `smoke` / `resume`）
- [x] smoke 与 main 分离
- [ ] 全量跑完后更新 `docs/EXPERIMENT_RESULTS.md`（若需要）

## 参考

- 命令：[RUN.md](RUN.md)
- 架构：[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- OpenHands 加固：[docs/OPENHANDS_BENCHMARK_TODO.md](docs/OPENHANDS_BENCHMARK_TODO.md)
- 出题：[BATCH1_PLAYBOOK.md](BATCH1_PLAYBOOK.md)

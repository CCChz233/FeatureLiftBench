# 私有服务器交接

这是覆盖到现有 FeatureLiftBench checkout 的维护者包，包含隐藏测试与参考解。
不得直接把包交给被测 agent；`run-agent` 会按既有协议构建无提示工作区。
包包含完整来源归档、三个任务、生成器、基线和最新本地验证日志；不包含
Python 环境、模型凭据、Docker 镜像或完整 wheel 缓存，不是完全自包含运行环境。

本地生成包：

```powershell
.venv/Scripts/python.exe benchmark/selection/workflow_hard_pilot_20260912/export_pilot.py --evidence experiments/validation/workflow_hard_pilot/20260912T101718Z/summary.json
```

输出到 `exports/server-overlays/workflow-hard-pilot-<timestamp>.tar.gz`，
同目录有 `.sha256` 和 `.inputs.json`。归档内部含 `INPUT_LOCK.json`。
INPUT_LOCK 是候选输入的校准锁，不是主榜通过的 freeze。

Linux 服务器使用与比较实验相同的 checkout/harness、Python 3.12 和镜像。
在干净的独立 checkout 解包，避免覆盖另一个版本的同名候选。
先核对 `.sha256`，再用 `tar -xzf <overlay> -C <checkout>` 解包。
设置下列便捷变量：

```bash
P=benchmark/selection/workflow_hard_pilot_20260912
python3 "$P/server_replay.py" verify
```

在可联网的依赖准备阶段补齐两个纯 Python wheel（运行测试时仍断网）：

```bash
python3 -m pip download --only-binary=:all: --no-deps \
  --dest benchmark/vendor-wheels packaging==25.0 networkx==3.4.2
```

已有 harness 的 pytest 等工具 wheel 也需按项目 setup 流程准备好。不可安装 pip、
dbt-core 或 SQLGlot 到被测 submission 的依赖环境以替代提取。

先跑参考解，默认三轮，覆盖两个候选和 SQLGlot 对照：

```bash
python3 "$P/server_replay.py" reference --repeats 3
```

该命令先验证锁，再从已验证归档恢复不存在的 staging repo；已存在但 hash 不符会失败。
随后调用现有 CLI 的 `eval --docker`，要求功能和 isolation 都通过。
输出目录为 `experiments/calibration/workflow_hard_pilot/reference-<timestamp>/`。
本地尚不能执行 Linux 分支；服务器第一次运行是集成验证，不能预先当作成功证据。

模型校准前，选择与旧 Hard-50 比较实验一致的 **OpenHands baseline profile**；
核对其 token/step/call/cost 上限、模型版本、工具配置和运行时限制，禁用方法增强或
额外预算。脚本保留 profile 文件 hash、命令、超时和全部独立运行；凭据内容不写入报告。
不要使用无限预算配置。下面的 `<profile>` 必须替换为服务器实际的已核对 profile：

```bash
python3 "$P/server_replay.py" calibrate \
  --agent-profile <profile> \
  --agent-config harness/config/agents.toml \
  --env-file .env \
  --reference-evidence experiments/calibration/workflow_hard_pilot/reference-<timestamp>/summary.json \
  --repeats 3 --timeout-seconds 3600
```

默认只校准 pip、dbt 两题；SQLGlot 已从难题候选清单剔除。
脚本要求与输入锁匹配的 Docker 参考通过报告才启动模型，使用 Full-Repository、
No-Hint、不暴露 evaluator 测试、无额外失败重跑。对第二个模型用相同预算再独立运行。
各任务的 run/eval 结果和日志都保留；`calibrate` 命令完成不代表模型功能通过。
不同预算或不同 harness 的运行只能单列，不能合并成同一难度结论。

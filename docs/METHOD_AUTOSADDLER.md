# AutoSaddler-FLB (prompt-pack method)

> **Status: current · Last verified: 2026-08-29**
> 这是 FeatureLiftBench 的一种 **screening method**，不是 Official Main。
> 尚无正式分数，**不得**并入 OpenHands 论文主表。

AutoSaddler 是微软的 harness 优化器（[arxiv:2608.23041](https://arxiv.org/abs/2608.23041)）。
在本仓库里它被收成 **prompt-pack 方法**：在 **与 Main 相同的信息边界** 上搜索四段
OpenHands 附录（repository inspection / implementation / self-verification /
completion），然后用冻结后的 pack 再跑 OpenHands。不改 agent runtime、不改
evaluator、不改题包、不把 Hidden 暴露给优化器。

## 仓库怎么放

| 路径 | 谁拥有 | 是否进 FeatureLiftBench git |
| --- | --- | --- |
| `integrations/autosaddler_featureliftbench/` | 本项目（对接） | 是 |
| `microsoft/AutoSaddler` @ `30e20ce` | 上游 | **否**。按 pin 从 GitHub 安装 |
| 本机 `AutoSaddler/` 目录 | 可选可编辑 checkout | gitignore |

Pin：[AUTOSADDLER_PIN.json](../integrations/autosaddler_featureliftbench/AUTOSADDLER_PIN.json)。
机器可读规范：[autosaddler.json](../harness/config/methods/autosaddler.json)。
`--method autosaddler` 的 `run-agent` 标志与 `main` 相同；学到的 pack 通过

`FEATURELIFTBENCH_OPENHANDS_PROMPT_APPEND_FILE`

注入。没有 pack 时行为应与 Main 的 inactive seed 一致。

## 安装

```bash
python3.12 -m venv integrations/autosaddler_featureliftbench/.venv
source integrations/autosaddler_featureliftbench/.venv/bin/activate
pip install -e ./harness
pip install -e "./integrations/autosaddler_featureliftbench"
```

`autosaddler` 从 pin 的 Git commit 拉取，不要把微软仓文件 commit 进本仓库。

## 两段入口（不要混）

1. **优化**（小 train/dev，产出 candidate pack）：

```bash
python -m autosaddler_featureliftbench.runner \
  --config integrations/autosaddler_featureliftbench/configs/causal_pilot_deepseek.yaml \
  --run-id <run-id>
```

2. **评测冻结 pack**（与 Main 同协议）：

```bash
export FEATURELIFTBENCH_OPENHANDS_PROMPT_APPEND_FILE=<frozen-pack>
./scripts/run_benchmark.sh \
  --benchmark python200_hard \
  --agent openhands \
  --method autosaddler \
  --docker --workers 1 --timeout 3600
```

优化用的 train 题必须与最终 readout 题 **仓级不相交**。不要在 Python-200' 上边搜边报。
数字进独立 screening 表，不进 OpenHands 主表。

细节与契约：[integrations/autosaddler_featureliftbench/README.md](../integrations/autosaddler_featureliftbench/README.md)。

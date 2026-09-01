# AutoSaddler-FLB (OpenHands 上的可行性试验)

> **Status: current · Last verified: 2026-08-29**
> 目的：看 AutoSaddler 在 **FeatureLiftBench + OpenHands** 上有没有用。
> 这不是 Official Main，也还没有正式分数。试出来的数不要写进 OpenHands 论文主表。

可以做。对接已经接好：优化器改四段 OpenHands 附录，每次候选仍用现有 OpenHands +
Docker evaluator 打 Functional Pass。Agent 就是你们的 OpenHands，题就是你们的
FeatureLift 题。

当前集成是 **prompt-only**（OpenHands 本体冻结）。tools / middleware 是 AutoSaddler
的更大搜索空间，要另开 Git harness，不是这一条试验。

## 怎么「试试好不好用」

先在 **两道、仓不相交** 的题上看 H0（空附录 = 现在的 Main）和 H1（AutoSaddler 改过的附录）。
这就是可行性试验，不是论文全量。

| 角色 | 题 | 题根 | 为何选它 |
| --- | --- | --- | --- |
| train | `apischema__serialization_core__001` | `benchmark/hard50_pilot/` | Flash 在 public+hidden 上功能性失败，空 lock，隔离通过 |
| development | `paste__dispatch_map_core__001` | 同上 | 另一个仓，Flash 同样是功能性失败，不是装依赖失败 |

不要用 `taskiq` / `oslo_config` 这类 **pip 在评测镜像里装不上** 的题当因果切片：优化器会学到错误信号。也不要用 Flash 已经能过的题当 Dev H0，否则没有 lift 空间。

最多 4 次 OpenHands：Dev H0 → Train H0 → Train H1 →（若 train 变好）Dev H1。

- Dev H1 比 H0 好：说明在这两道题上、对 OpenHands 有用，再考虑加题或开 tools。
- Train 变好、Dev 不动：过拟合，方法在这个 setting 里还没泛化。
- Train 也不动：prompt-only 这条线在这个 setting 里没碰到瓶颈。

先不要拿 200 题来试：一次 rollout 很贵，全量既看不出「有没有用」，也把测试集用掉了。
**不是永远不许跑更大集**，是先用这两道题回答「OpenHands 上有没有信号」。

## 跑

```bash
python3.12 -m venv integrations/autosaddler_featureliftbench/.venv
source integrations/autosaddler_featureliftbench/.venv/bin/activate
pip install -e ./harness
pip install -e "./integrations/autosaddler_featureliftbench"

set -a && source .env && set +a
cd integrations/autosaddler_featureliftbench
python -m autosaddler_featureliftbench.runner \
  --config configs/causal_pilot_deepseek.yaml \
  --run-id flb-openhands-trial-002
```

需要 `.env`、Docker 评测镜像、OpenHands 在 `PATH` 里。输出在
`experiments/methods/autosaddler_flb/causal_pilot_runs/`。

Pin 与对接说明：[AUTOSADDLER_PIN.json](../integrations/autosaddler_featureliftbench/AUTOSADDLER_PIN.json) ·
[integration README](../integrations/autosaddler_featureliftbench/README.md)。
微软仓不进本仓库 git；`autosaddler` 按 commit 安装。

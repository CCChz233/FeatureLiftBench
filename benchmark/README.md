# FeatureLiftBench 任务与身份资产

> **Status: reference · Last verified: 2026-09-14**

当前论文采用固定的 150 题集合，见
[python150_membership.json](../docs/paper/writing/python150_membership.json)。
任务身份与源快照来自已有 freeze，目录名称不定义论文难度或范围。

| 路径 | 内容 |
| --- | --- |
| `tasks/` | 论文任务实体包及一项 sanity；写作时按 150 题清单过滤 |
| `hard50/` | 历史额外 50 题，不纳入本文 |
| `python200_hard_tasks/` | 保留的 200 个符号链接：150 → tasks，50 → hard50 |
| `sources/` | 源仓库 registry 和固定快照信息 |
| [suites.toml](suites.toml) | 运行 catalog，保留历史 suite 标识与运行语义 |

历史题包、参考实现和依赖资产见
[归档说明](../archive/paper_unrelated_20260914/README.md)。
不要通过整理改写题包、源哈希、freeze 或把符号链接复制成另一套实体。
Catalog 的历史 `paper_main` 标记不取代当前论文显式的 150 题选择。

任务构建与准入仍遵循 [TASK_DESIGN_RULES.md](../docs/TASK_DESIGN_RULES.md)。
论文与运行目录对应见 [PAPER_FOLDERS.md](../docs/paper/PAPER_FOLDERS.md)。

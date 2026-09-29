# FeatureLiftBench 项目地图

> **Status: current · Last verified: 2026-09-29**

当前论文讨论行为保持的功能迁移：给定固定版本的完整 Python 源仓库和公开契约，agent 构建独立软件包，再用 Build、Primary、Extended、Isolation 四门评测。正文只报告选定的 150 题、126 个仓库、132 个快照；六配置共有 900 个逐题结果。

| 工作 | 唯一当前入口 |
| --- | --- |
| 写正文、参考文献、看正式图 | [docs/paper/](paper/README.md) |
| 查论文使用的数据 | [paper_sources.json](paper-workbench/paper_sources.json) |
| 逐图改外观 | [独立脚本](paper-workbench/figures/standalone/README.md) |
| 复算并重画论文图 | [绘图流程](paper-workbench/figures/scripts/README.md) |
| 看 150 题 RQ2 尚未入稿试画 | [草稿目录](paper-workbench/figures/drafts/rq2_150/README.md) |
| 跑论文检查、编译和打包 | [当前工作流](paper-workbench/WORKFLOW.md) |
| 找旧图、旧计划与搬迁记录 | [清理归档](archive/paper_cleanup_20260929/README.md) |
| 运行 benchmark | [RUN.md](../RUN.md)、[评测协议](EVALUATION.md) |

论文目前有 8 张图、5 张表；`docs/paper/main.tex` 引用 12 个图片文件，Fig. 2 是 LaTeX 排版图而非外部图片。RQ2 正文仍使用 40 题 Full Source/Contract Only 消融和 DSE 诊断。150 题版本的 Fig. 4 草稿被单独保存，不能凭草稿中的数字宣称已完成新的实验分析。

`benchmark/` 保存任务包，`harness/` 保存评测器，`experiments/` 保存运行记录，`reports/` 和 `artifacts/` 保存分析与固定身份。`docs/paper-workbench/` 保存论文复算代码和已选数据；`docs/paper/` 仅存正式正文与引用资产。历史 200 题目录名是存储背景，不改变论文 150 题范围。

# 当前论文工作流

> **Status: current · Last verified: 2026-09-29**

从仓库根目录执行以下命令：

```bash
python -B scripts/paper.py check
python -B docs/paper-workbench/figures/scripts/draw_all.py --list
python -B docs/paper-workbench/figures/scripts/draw_all.py --only 4 --output-dir /tmp/flb-figures-preview
python -B scripts/paper.py build
python -B scripts/paper.py package
```

`check` 只核对已保存证据，不启动 agent 或 Docker 实验；`draw_all.py` 默认只生成预览。只有显式 `--publish` 才会更新 `docs/paper/figures/` 中的正式 PDF。修改正式论文前，先核对 [输入清单](paper_sources.json) 与 [正文](../paper/main.tex)。

逐图外观修改可用 [独立脚本](figures/standalone/README.md)，但其中数值是冻结副本；新实验数据必须先进入可复算流程，并更新正文口径。未入稿的 RQ2 150 题草稿在 [drafts/rq2_150](figures/drafts/rq2_150/README.md)。旧版工作流保存在 [归档](../archive/paper_cleanup_20260929/workbench_plans/WORKFLOW_before_cleanup.md)。

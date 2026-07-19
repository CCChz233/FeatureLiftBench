# Python task design notes

按题 maintainer 设计笔记，共 **106** 篇 + [TEMPLATE.md](TEMPLATE.md)。**不是** agent 入口；落地 spec 以 `benchmark/tasks/<task_id>/TASK.md` 为准。

## 与 benchmark 的关系

| 层级 | 路径 | 读者 |
| --- | --- | --- |
| Design note | `docs/task_designs/<task_id>.md` | 出题 / audit / promote |
| Task package | `benchmark/tasks/<task_id>/` | Agent + evaluator |
| Authoritative spec | `benchmark/tasks/<task_id>/TASK.md` | Agent prompt |

Promote 前：design note → materialize → validate → `benchmark/staging` or `batch3_pilot` → promote 到 `benchmark/tasks/`。

## 命名

文件名与 `task_id` 一致，例如 `jinja2__lexer_parser_core__001.md`。Hard3 扩展题后缀 `__hard3_001`。

## 索引

- 完整 task 列表与 split：[../python/02_python_repo_task_inventory.md](../python/02_python_repo_task_inventory.md)
- Taxonomy / entanglement：`artifacts/research_analysis/python150_task_taxonomy.csv`
- Promote 规则：[../07_incremental_task_rules.md](../07_incremental_task_rules.md)
- Agent 工作流：[../../.agents/skills/featureliftbench-create-task/SKILL.md](../../.agents/skills/featureliftbench-create-task/SKILL.md)

## 模板

新题从 [TEMPLATE.md](TEMPLATE.md) 复制，填写 target API、included/excluded behaviors、oracle 预期、hidden 设计意图与 promote blockers。

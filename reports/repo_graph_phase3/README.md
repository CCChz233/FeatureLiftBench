# Phase 3 MVP 关系族落地（2026-07-23）

> 历史 RSG 原型证据；该方法不属于 v2 Main，下面命令和指标只用于追溯。

## 交付

Python adapter `python-adapter-v2` 补齐设计预注册 10 类关系：

| Kind | 提取方式 |
| --- | --- |
| `EXPORTS` | `__all__` 字符串列表 |
| `PROVIDES_MEMBER` | class → 公开方法/成员 |
| `RETURNS_TYPE` | 函数返回注解 |
| `RAISES` | `raise` 语句 |
| `LOADS_RESOURCE` | 既有 open/Path/resources/`__file__` |
| `PACKAGED_BY` | `pyproject.toml` package-data + `MANIFEST.in` |
| `READS_CONFIG` | 配置后缀路径的 open/load/read |
| `DEFAULT_DEFINED_BY` | 参数默认值表达式 |
| `REGISTERS` | `.register/.subscribe/.connect` + register/route decorator |
| `RESOLVES_VIA` | registry 下标 + getattr 动态分派（`unresolved_dynamic`） |

## 测试

```bash
PYTHONPATH=harness python -m unittest tests.test_repo_graph_relations tests.test_repo_graph
```

Fixture：`harness/tests/fixtures/repo_graph_phase3/`

## 离线比较脚手架

```bash
PYTHONPATH=harness python harness/scripts/compare_support_baselines.py \
  --repo benchmark/sanity/iniconfig__parse_config__001/repo \
  --seed IniConfig --budget-tokens 2000 \
  --output reports/repo_graph_phase3/iniconfig_support_compare.json
```

Phase 4 仍需人工标注集与约定指标门；本目录仅存放脚手架输出。

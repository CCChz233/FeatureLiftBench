# Qwen3.6-35B freeze v2 最终结果（关闭补跑）

生成时间：2026-09-05T00:23:21Z
冻结：`6c20ff0307762503a73cbb9ff32e9992c6446e4b17483a68373027be58cbf419`
候选镜像：`212930ea`
profile：`openhands_qwen3_6_35b_a3b_fp8_paper`
父目录：`/home/chaihongzheng/workspace/FeatureLiftBench/experiments/python/openhands/qwen3.6-35b-a3b-fp8/python200-prime-v2-main-r1`

## 主表（仅 24 题 freeze v2）

这是 Qwen 在 freeze v2 上**唯一可引用**的结果。另外 176 题不是 freeze v2，禁止合成 200 题主表。

| 指标 | 值 |
|---|---|
| n | **24** |
| Functional Pass | **6 / 24 = 25.0%** |
| 有包且评测 | 21 |
| 空卷 | **3**（计入 Functional Fail） |
| 有包中 Functional | 6 / 21 |

空卷 **不再补跑**。`attempt=2` 已经给过瞬时重试；三次都是 `tool_validation_error`（缺 `security_risk`），不是 Hidden 语义失败。

## 为什么还有 3 题空卷

| 题 | 原因 |
|---|---|
| `importlib_metadata__entry_points_core__001` | 连续 `file_editor`/`task_tracker` 缺 `security_risk`，未写出 submission |
| `intervaltree__interval_tree_core__001` | 连续 `terminal`/`file_editor` 缺 `security_risk`，未写出 submission |
| `virtualenv__interpreter_spec_core__hard3_001` | 同上（freeze24 收尾时新出现） |

这是 Qwen native tool calling 没填 OpenHands 必填字段。主表 profile 未开 `openhands_tool_alias_compat`。打开补丁可以减少空卷，但那是 harness 代填，不再是这轮设定。

## 有包失败的第一道闸（21 题里的 15 题）

build=2  public=10  hidden=3  isolation=0

## Functional 通过的 6 题

- `cachetools__cache_eviction_core__001`
- `diskcache__eviction_policy_core__hard3_001`
- `jsonpointer__resolve_core__001`
- `packaging__requirement_marker_specifier__001`
- `python_frontmatter__roundtrip_core__001`
- `stevedore__extension_manager_core__hard3_001`

## 不要引用

- 父套件 `suite.json` n=200、Functional 86/169：freeze 身份是 24×v2 + 126×旧 150 freeze + 50×Hard-50 无 freeze。
- 「真实能力 6/21」：空卷必须留在 24 题分母里。

## 产物

- 切片套件：`experiments/python/openhands/qwen3.6-35b-a3b-fp8/python200-prime-v2-main-r1/suite.freeze_v2_final.json`
- 本目录：`summary.json`、`task_results.csv`

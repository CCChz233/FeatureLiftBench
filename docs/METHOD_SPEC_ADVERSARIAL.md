# Spec-grounded adversarial self-test

> **Status: killed · Last verified: 2026-08-20**
> 本文件是 **Spec-grounded adversarial self-test** 的唯一规范。不是自反思，
> 不是 Public-feedback，数字不进 Python-200 主表。**Hidden-4 筛选已 Kill。**

## 定义

Harness 从 `metadata.public_spec` 生成可执行合同矩阵；Agent 填满每个
`Bxxx` 场景桩，并可选地对它在 `repo/` 里找到的上游符号做 dual-run。
Hidden 与 `public_tests/` **永不**挂载。同一 128k / 120-step / No-Hint /
无 2M Main 信封。

| 维度 | Main 对照 | Spec-adversarial |
| --- | --- | --- |
| Prompt | `standard` | 同左 + 短 appendix |
| Context / reserved | 131072 / 8192 | 同左 |
| Max steps | 120 | 同左 |
| Total token cap | **无** | 同左 |
| Condenser | `token` / LLM summary | 同左 |
| Source hints | 无 | 无（不写 `source_entrypoints`） |
| `public_tests/` | 不挂载 | 不挂载 |
| Hidden | evaluator-only | evaluator-only |
| Workspace extras | 无 | `contract_matrix.json` + stubs + `run_contract_check.py` |
| Runtime `ablation_arm` | `main` | `spec_adversarial_self_test` |

与已死臂的对比：

- **Audit：** 自然语言 Bxxx 走查；本臂无 `AUDIT_RESULT` 块。
- **TFL：** Agent 自造用例再 freeze；本臂行由 spec 预开槽，无 freeze 阶段。
- **Public-feedback：** 官方测试；本臂永不复制 `public_tests/` / `hidden_tests/`。
- **CCG：** 硬拦截 OpenHands `finish`；本臂只用过程指标。

不要叠 Entrypoint-Hint、Public-feedback、TFL、audit、CCG、verification-aware、
artifact-aware 或 recency。`run_python200_paper.sh --execute` 会拒绝本臂。

机器可读冻结：[`harness/config/methods/spec_adversarial_self_test.json`](../harness/config/methods/spec_adversarial_self_test.json)。

## 切片

Hidden-4：RQ6 上 Public-feedback 仍抬不动 Hidden 的四题。清单
[`spec_adversarial_hidden4_v1.txt`](../harness/config/experiments/spec_adversarial_hidden4_v1.txt)。

- `parse__format_parser_core__001`
- `pygments__lexer_core__001`
- `python_decouple__config_repository_core__001`
- `schema__nested_validate_core__hard3_001`

同日必须重跑这 4 题的 Main。

## 读出

主指标仍是 evaluator `functional_gate`，外加 Hidden 0→1：

| 结果 | 动作 |
| --- | --- |
| Hidden 0→1 = **0/4** | **Kill**。不 Distill-24，不 Python-200，不叠 Entrypoint-Hint / Public-feedback。 |
| Hidden 0→1 ≥ **2/4** 且 public 仍未挂载 | 继续调查；仍不是主表行。 |
| 中间地带 | 记过程指标后决定；默认不扩面。 |

功能分高于同日 Main **不**替代 Python-200 主表。

## 怎么跑

本地 vLLM 若未起来，脚本会改走 DeepSeek API；两者是同一 Flash，不是实验因子。

```bash
# 同日两臂。第一臂 CLI exit 1 也会继续第二臂。
ENDPOINT=api WORKERS=2 ./logs/run_spec_adversarial_hidden4_deepseek_flash.sh both
```

比较：

```bash
PYTHONPATH=harness python3 harness/scripts/compare_spec_adversarial_hidden4.py \
  experiments/methods/spec_adversarial/<pair>/main \
  experiments/methods/spec_adversarial/<pair>/spec_adversarial
```

## 证据（Hidden-4 已齐 · **Kill**）

套件：`experiments/methods/spec_adversarial/hidden4-deepseek-v4-flash-20260820-091254/`。
快照：[`spec_adversarial_hidden4_20260820.json`](../artifacts/research_analysis/current_results/spec_adversarial_hidden4_20260820.json)。

- 端点：DeepSeek API Flash；信封如上。挂载完整性：Main 4/4 未挂，treatment 4/4 未挂。
- 同日 Main：**0/4** `functional_gate`（四题均为 public=1 / hidden=0）。
- Spec-adversarial：**0/4**（Δ0）。Hidden 0→1 = **0/4** → **Kill**。
- 过程：4/4 `checker_ran` 且 `checker_ok`；4/4 stubs 填满；3/4 用了 `--oracle-import`。
  可执行 public_spec 清单关绿，仍抬不动 Hidden。

| 题 | Main P/H | Treatment P/H | Hidden flip |
| --- | --- | --- | --- |
| parse | 1/0 | 1/0 | unchanged |
| pygments | 1/0 | 1/0 | unchanged |
| python_decouple | 1/0 | 1/0 | unchanged |
| schema | 1/0 | 1/0 | unchanged |

不 Distill-24，不 Python-200，不叠 Entrypoint-Hint / Public-feedback。数字不进主表。

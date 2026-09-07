# Python-200′ freeze v2 实验结果（2026-09-05）

> **Canonical.** 这是 freeze v2 Official Main **唯一正确**的 200 题主表。24 题补跑已叠回同一目录。不要和 20260829、9 月 2 日 Qwen 另一套、或叠回前的 143/132/80 混用。

冻结：`6c20ff0307762503a73cbb9ff32e9992c6446e4b17483a68373027be58cbf419`  
候选镜像：`212930ea`  
协议：OpenHands Official Main，Full-Repository / No-Hint  
主指标：**Functional Pass** = Build ∧ Public ∧ Hidden ∧ Isolation。空卷计入失败。

完整 200 题目录（24 题 freeze-preflight 失败后又叠回去）：

- `experiments/python/openhands/deepseek-v4-flash/python200-prime-v2-main-r1`
- `experiments/python/openhands/gpt-5.6-luna/python200-prime-v2-main-r1`
- `experiments/python/openhands/glm-5.3-flash/python200-prime-v2-main-r1`
- `experiments/python/openhands/qwen3.6-35b-a3b-fp8/python200-prime-v2-main-r1`
- `experiments/python/openhands/gpt-oss-120b/python200-prime-v2-main-r1`

那 24 题只是补跑，不是这几家的全部结果。GLM-5.3-Flash 于 2026-09-06 收工（200/200），进本表。不要用 `run.status` 的 59/200。旗舰 GLM-5.3 错跑目录不进表。

## 主表：Functional Pass @ 200

| 模型 | Functional Pass | Python-150 | Hard-50 | 空卷 | Wilson 95% CI |
|---|---|---|---|---|---|
| DeepSeek V4 Flash | **157 / 200 (78.5%)** | 108 / 150 | 49 / 50 | 0 | 72.3–83.6% |
| GPT-5.6 Luna (OpenLux) | **144 / 200 (72.0%)** | 102 / 150 | 42 / 50 | 1 | 65.4–77.8% |
| GLM-5.3-Flash | **98 / 200 (49.0%)** | 68 / 150 | 30 / 50 | 45 | 42.2–55.9% |
| Qwen3.6-35B | **86 / 200 (43.0%)** | 63 / 150 | 23 / 50 | 31 | 36.3–49.9% |
| GPT-OSS 120B | **61 / 200 (30.5%)** | 36 / 150 | 25 / 50 | 1 | 24.5–37.2% |

首败（200 题）：

| 模型 | Pass | Public | Hidden | Build | Isolation | Empty |
|---|---|---|---|---|---|---|
| DeepSeek | 157 | 26 | 16 | 0 | 1 | 0 |
| Luna | 144 | 36 | 16 | 3 | 0 | 1 |
| GLM | 98 | 39 | 10 | 5 | 3 | 45 |
| Qwen | 86 | 50 | 26 | 7 | 0 | 31 |
| GPT-OSS | 61 | 91 | 28 | 18 | 1 | 1 |

不要用 `run.status=passed`（DeepSeek 只有 29；GLM 只有 59）。Qwen 31 题空卷是过程失败（TVE 为主），GLM 45 题空卷主要是未交包，计入 Functional Fail，不要改写成 86/169 或 98/155。

## 补跑的 24 题（freeze-preflight 子集）

叠进上面的 200，不必单独当主表。同一 24 题上：DeepSeek 14/24，Luna 12/24，Qwen 6/24，GPT-OSS 4/24。

## 不要和这张主表混的数字

- `python200-hard-main-20260829`：**132/200**（更早 freeze）
- `python200-prime-qwen36-35b-a3b-fp8-main-r1`：9 月 2 日 Qwen 另一套 200，早于 freeze v2
- 论文稿 9 月 4 日写的 143/200、132/200、80/200：补跑 24 题之前的口径
- 「Qwen 真实能力 86/169」或「6/21」

Hard-50 上 DeepSeek 49/50、Luna 42/50 是这张 200 主表的分层，但 Hard-50 无 `reference_solution/`，compactness 不进 Functional，不要当成难度已被打穿的证据。

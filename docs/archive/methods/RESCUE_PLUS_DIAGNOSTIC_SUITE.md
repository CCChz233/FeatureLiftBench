# Rescue+ 高区分度诊断集

> **Status: archived · Last verified: 2026-08-18**
> Rescue+ 诊断集已停止使用。Core-12 现仅作历史方法诊断，不能换算成 Python-200。

## 结论

后续 DeepSeek API 方法迭代默认不重复运行 Python-200 全量。固定使用 `rescue_plus_distill24_v1`，其中前 12 题组成更便宜的 `core12`。

- `core12`：实现或 checker 小改动后的快速诊断，只运行待测方法。
- `distill24`：方法版本比较，在完全相同条件下配对运行 Frozen Lite V1（45+10 信封）和 Rescue+。这不是 Python-200 主表里的 120 步旧 Lite V1 协议，也不是当前 [V1 = Main+2M](../../METHOD_V1.md)。
- Python-200：只在方法和 checker 冻结后运行一次，作为最终无偏结果；诊断集结果不能换算成全量通过率。

任务文件：

- `harness/config/experiments/rescue_plus_core12_v1.txt`
- `harness/config/experiments/rescue_plus_distill24_v1.txt`
- `harness/config/experiments/rescue_plus_distill24_v1.json`

## 选题依据

主要依据是同一 DeepSeek API 模型上的 Main 150 题运行与 Lite V1 200 题运行的 150 道公共任务。该配对中：

- Main 对、Lite V1 错：10 题，全部收入。
- Main、Lite V1 都错：52 题，按 API、签名、匹配、嵌套状态等失败类型选 5 题。
- Main 错、Lite V1 对：16 题，选 3 题作为 V1 优势回退保护。
- 两者都对：72 题，只保留 3 题作为正确性和 token 哨兵。

另外从 Python-200 本地 vLLM 配对结果的 External-50 中加入 3 道 Main 对、Lite V1 错的任务。最终 24 题中，21 题用于区分方法，3 题用于检测回退和无谓开销。

`tenacity` 和 `pluggy` 暂不进入诊断集，因为已经发现公开任务描述、可见上游行为和 evaluator 之间存在需要单独审计的不一致。它们不能作为方法迭代的干净反馈。

## 固定使用规则

1. 清单版本冻结后，不根据 Rescue+ 的新结果增删题。若任务本身审计失败，发布新版本清单并保留旧版本。
2. 比较方法时必须使用相同模型 endpoint、镜像、预算、并发和 evaluator。
3. 小改动只跑 `core12`；准备保留一个版本时跑配对 `distill24`。
4. 主要看净挽救数：`Rescue+ 新增通过 - Rescue+ 引入回退`，同时报告总 token、token/通过题和 repair 触发率。
5. `distill24` 是有意富集失败题的开发集，不能报告成 Python-200 的准确率，也不能作为论文最终测试集。

## 运行方式

把任务文件逐行转换成 CLI 的 `--task-id` 参数：

```bash
task_args=()
while IFS= read -r task_id; do
  task_args+=(--task-id "$task_id")
done < harness/config/experiments/rescue_plus_core12_v1.txt
```

需要完整 24 题时，将文件名替换为 `rescue_plus_distill24_v1.txt`。其余参数继续使用对应方法的冻结 profile 和固定 Docker 镜像。

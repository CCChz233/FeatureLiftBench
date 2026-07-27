# 当前结果能说明什么

**最后更新：** 2026-07-27

## 最重要的结论

Benchmark 的工程合格性已经由任务、source、Oracle、isolation、compactness
和 freeze 门禁证明，不需要靠某个模型跑 100 次来证明。

模型能力结论则相反：当前还没有 v3 Full-Repository / No-Hint baseline，
所以不能把历史通过率写成新版 benchmark 的最终性能。

## 已经可以支持的结论

### 1. Python-150 是可执行且稳定的 v3 benchmark

- 150/150 任务通过八原则审计；
- 132/132 canonical snapshots ready；
- 450/450 Docker Oracle runs 通过；
- 150/150 tasks 三次结果稳定；
- 0 active quarantine；
- source/spec/reference/evaluator/environment 已冻结。

### 2. 历史条件下有明显模型区分度

`mixed_snapshot_v1` 四模型 evaluator Functional Pass@1 从 24.7% 到
58.0%。这说明任务不是全过或全挂，并能区分模型能力。

但 source context、定位提示和 exact freeze provenance 与 v3 不同，因此
不能把这些数值外推成 v3 通过率。

### 3. Functional Pass 与 Agent completion 必须分开

五个历史任务在 Agent step-limit 后仍留下 evaluator 可通过的 submission。
按 benchmark correctness，它们 functional pass；按 agent process，它们未
正常完成。二者混成单一 `run.status` 会改变模型排名数字。

论文应把 evaluator Functional Pass@1 作为 headline，把 step-limit、
completion 和 token 作为过程指标。

### 4. Public-feedback 会改变结果

历史 hard-50 配对中，Public-feedback 11/50，test-blind 4/50。因此
public evaluator tests 是否对 Agent 可见是关键实验变量，不能用同一个
“Main”名称混报。

### 5. 失败不只是定位失败

已有轨迹反复出现：

- required API/export 缺失；
- public behavior 通过但 hidden 边界失败；
- helper、resource、registry 或 external dependency 漏带；
- framework/global-state 隔离失败；
- copy-heavy 解法功能通过但不紧凑；
- 重复探索、step/context budget 耗尽。

旧 RSG start-here A/B 没有在小规模 hard tasks 上提升 hidden pass，提示
“告诉模型先看哪里”不足以解决 API/behavior completion。

## 尚不能支持的结论

- 不能声称任一模型在 v3 Main 的通过率；
- 不能声称 Full-Repository 一定比旧 slice 更难或更容易；
- 不能声称 source entrypoint hint 的因果效应，除非在 v3 同源配对臂重跑；
- 不能把 AI-assisted 标注写成 independent human gold；
- 不能把 150 个 `hard` 标签解释为经验难度等级；
- 不能外推到任意语言、应用型服务、GUI、云原生或大型系统；
- 不能用旧 composite `final_score` 代替 Functional Pass@1；
- 不能从单次模型轨迹推断稳定性。

## v3 baseline 完成后优先回答

1. 不同模型的 Functional Pass@1 和置信区间；
2. full-repository 下 localization、closure 和 behavior failure 的占比；
3. 正确方案的 reference-relative compactness；
4. repository size、domain、archetype、entanglement 与 task footprint 的关系；
5. token、step、latency 和 context-limit 对通过率的关系；
6. Main、Entrypoint-Hint、Public-feedback 和 Pruned-Context 的配对差异。

## 证据

- [v3 readiness](../reports/audits/v3_main_readiness.md)
- [v3 Oracle](../reports/audits/v3_oracle_revalidation/summary.md)
- [历史四模型结果](../reports/python150_compliant_20260726/)
- [轨迹证据](research_analysis/TRAJECTORY_FINDINGS.md)
- [失败归因](../reports/failure_attribution_20260720/)
- [实验清单](EXPERIMENTS.md)

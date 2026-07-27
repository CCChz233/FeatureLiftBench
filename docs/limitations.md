# Known Limitations

## Dataset construction

- **Maintainer task selection.** 150 tasks were maintainer-selected. Current
  registry proves exact source/revision/content；replacement 7 有固定 21-repo
  candidate ledger，但原有 143 题的候选池与构建淘汰过程记录仍不完整。
- **Python library/tooling skew.** 102 library、29 developer-tooling、17
  framework/plugin、2 application/service tasks。结论主要适用于 Python
  libraries/tooling，不能自然外推到大型业务系统、GUI、cloud-native、GPU
  或分布式服务。
- **Domain and mechanism imbalance.** Parsing 41/150，parser-state 45/150，
  third-party-dependency primary 仅 3/150。领域多样不等于机制均衡。
- **Source popularity and contamination.** 题集包含 pytest、Jinja2、
  SQLAlchemy、Pydantic 等知名项目；尚未完成 popular-vs-long-tail 和潜在
  training contamination sensitivity analysis。
- **Task footprint coverage.** active compactness registry 有 150/150
  reference file/LOC records，但 symbol records 只有 49/150。完整仓库很大
  不自动证明每题作用域很大。
- **Application coverage.** 2 application/service tasks 不足以支持“任意真实
  软件仓库”主张。

## Task design and review

- **AI-assisted provenance.** 契约、taxonomy 和部分 closure 记录由
  AI-assisted/maintainer workflow 产生。独立人工审核不是准入门槛，这些
  记录不能写成 independently adjudicated human gold。
- **Hidden-test completeness.** Public/hidden 都受同一公开契约约束，但有限
  测试不能证明完整语义等价。未覆盖行为可能造成假阳性。
- **Evidence asymmetry.** 完整仓库保留 upstream tests/docs/examples，
  但项目之间证据丰富度差异很大；Agent 的任务难度同时受上游工程质量影响。
- **Difficulty labels.** 当前 150/150 metadata 为 `hard`，旧 Core-100 /
  Hard-50 是构造切片，不是 v3 empirical difficulty。必须用首轮 frozen v3
  baseline 重校准。
- **No extraction-authenticity proof.** Benchmark 允许复制、裁剪和适配，也
  允许行为等价重构；当前没有可靠判据证明 submission 一定“理解并提取”
  而不是基于契约重写。

## Evaluation

- **Binary functional gate.** Build + public + hidden + isolation 全过才 pass；
  不提供部分正确性的 headline credit。
- **Reference-relative proxy.** Frozen reference 是一个可行实现，不是唯一
  最小解。LOC/file/copy/dependency 指标只能描述紧凑性，不能证明最小闭包。
- **Copy detection.** Copied LOC 使用保守的 normalized line-sequence
  heuristic；重排、改名和语义复制可能漏检，常见模板也可能造成误报。
- **Isolation coverage.** Forbidden imports、paths、dependencies、symlinks、
  dynamic imports 和 resources 的检查仍可能存在绕过方式。
- **Public-feedback naming history.** 旧实验曾用 `Main` 表示 public tests
  可见、`No-public` 表示不可见。历史结果必须按实际可见性重标，不能只读
  run 名称。
- **Agent/evaluator status mismatch.** Agent step-limit 后可能留下 evaluator
  可通过的 submission。Functional Pass、Agent completion 和 process failure
  必须分别报告。

## Reproducibility and licensing

- **Large archives are not committed.** Canonical archives在本地
  `benchmark/sources/archives/`，Git 只记录 registry、digest 和
  materialization logic。复现依赖上游仍可获取或研究者保存已验证 archive。
- **Upstream licensing.** 126 external sources 有不同许可证；benchmark release
  需要继续核对源码再分发、reference code 和派生 submission 的许可证义务。
- **Environment coupling.** 结果依赖 Python、vendor wheels、Docker、
  OpenHands、模型 provider/router 和资源限制；freeze 能记录条件，但不能
  消除所有平台差异。

## Experimental evidence

- **No v3 model baseline yet.** 当前模型数字全部来自
  `mixed_snapshot_v1`；不能用于声明 v3 Full-Repository / No-Hint 的绝对
  性能。
- **One-attempt variance.** Pass@1 是主要比较口径，但单次轨迹不能回答模型
  随机性和稳定性。若研究 variance，需要预注册重复实验。
- **Historical failure attribution.** 550-run trajectory analysis 来自旧
  source/hint 条件，机制假设可复用，比例不可直接外推。
- **Go is calibration only.** Go tasks 尚未通过与 Python v3 同等级的
  source/spec/Oracle/freeze 门禁，不应进入混合 leaderboard。

当前 gate 状态见 [STATUS.md](STATUS.md)，设计前提见
[BENCHMARK_DESIGN.md](BENCHMARK_DESIGN.md)，实验口径见
[EXPERIMENTS.md](EXPERIMENTS.md)。

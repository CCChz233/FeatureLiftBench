# FeatureLiftBench 组会汇报：Benchmark 怎么设计的

> 用途：组会介绍设计思路与当前进展  
> 日期：2026-08-05  
> 旗舰例题三道（互补）：安全 token · CLI 框架 · 配置 round-trip  
> 详细规范见 `docs/BENCHMARK_DESIGN.md`；数字以 `docs/STATUS.md` / `docs/FINDINGS.md` 为准

---

## 1. 一句话

**FeatureLiftBench** 评测代码 Agent 能否在完整真实仓库与公开功能契约下，自主定位、理解、抽取并验证目标能力，最终交付一个**独立可安装、行为完整、尽量紧凑**的功能模块。

不是修 bug 榜，也不是从零写玩具——而是：**从真实仓抽功能，解耦成可单独用的包。**

---

## 2. 为什么做

| 常见评测 | 我们想测的 |
| --- | --- |
| 修 GitHub issue（如 SWE-bench） | 从完整仓库**抽取并解耦**目标功能 |
| 从零写代码 | **保真**上游可观察行为，再独立交付 |
| 能搜到文件就算成功 | 契约闭合 + 解耦 + 干净环境可跑 |

工程里更常见的难题是：既要行为对齐，又要解开依赖/配置/状态等**纠缠（entanglement）**，交出真正能单独安装使用的模块（减依赖、控供应链、内嵌最小能力）。  
（注：这里说的是 feature lifting 的主纠缠机制，不是 Constantine/PDG 那套经典 coupling taxonomy；详见 `docs/汇报_题集构成.md` §3。）

---

## 3. 测什么 / 不测什么

| 是 | 不是 |
| --- | --- |
| 从完整仓库恢复目标功能并解耦成新包 | 给原仓打补丁 |
| 对齐公开契约与上游行为 | 纯绿场自由发挥 |
| 交卷后私有测试验收 | 让 Agent 看见并拟合评分测试 |
| 紧凑性作次要指标 | 证明「唯一最小闭包」 |
| 方法无关（不规定 Agent 怎么想） | 强制某种推理工作流 |

---

## 4. 三道旗舰例题（推荐组会主讲）

选题原则：**工程场景硬、契约清楚、模型结果有区分度、故事互补。**

| # | 题 | 工程场景 | 禁运 | 故事角色 |
| --- | --- | --- | --- | --- |
| A | `itsdangerous__timed_serializer_core__001` | 签名 cookie / 过期验证链接 | `itsdangerous` | **安全契约**；Public✓ Hidden✗ 典型 |
| B | `click__option_parser__001` | 内部工具 CLI | `click` | **框架纠缠解耦**；主纠缠=framework，极难 |
| C | `configobj__roundtrip_config_core__001` | INI 配置读写与校验 | `configobj` | **配置保真**；多数模型卡在 Hidden |

### A. itsdangerous — 带过期的签名 Token

**路径：** `benchmark/tasks/itsdangerous__timed_serializer_core__001/`  
**上游：** [pallets/itsdangerous](https://github.com/pallets/itsdangerous) 2.2.0

**为什么最好讲：** 每个后端都懂——密码重置、邮箱验证、signed cookie。要求抽出：

```python
from featurelifted import BadSignature, SignatureExpired, URLSafeTimedSerializer
```

| 层 | 考什么 | 例子 |
| --- | --- | --- |
| Public（基础功能） | 能签能验、salt 隔离、防篡改 | `dumps({"name":"Ada"})` 再 `loads`；改 token 抛 `BadSignature` |
| Hidden（更严边界） | 过期边界、错钥、错误类型 | `max_age=5` 在边界秒抛 `SignatureExpired` 而非笼统错误 |
| Isolation | 真解耦 | 不能 `import itsdangerous`，不能读原仓路径 |

**冻结结果：** DeepSeek **过**；GPT-OSS **Public✓ Hidden✗**；两款 Qwen Build 过但 Public 不过。

**组会一句：** 基础签名过了，过期语义不过——说明我们测的是契约闭合，不是“写出个 HMAC”。

---

### B. click — 命令行 Option / Command / CliRunner

**路径：** `benchmark/tasks/click__option_parser__001/`  
**上游：** [pallets/click](https://github.com/pallets/click)

**为什么有工程价值：** 团队天天写内部 CLI；有时要最小命令框架，或控依赖不能整库引入 click。主纠缠机制是 **framework**（decorator、context、参数解析、测试 runner）。

Agent 要交付可装饰的 command/group，并用 `CliRunner` 调用：

```python
# Public：主路径 —— option / argument / Choice 错误
@click.command()
@click.option("--count", default=1, type=int)
@click.option("--mode", type=click.Choice(["fast", "slow"]), default="fast")
@click.argument("name")
def cli(count, mode, name):
    click.echo(f"{name}:{mode}:{count}")
```

```python
# Hidden：嵌套 group、IntRange、prompt、isolated_filesystem
@click.group()
@click.option("--debug/--no-debug", default=False)
@click.pass_context
def cli(ctx, debug): ...
```

**冻结结果：** 仅 DeepSeek **过**；GPT-OSS / Qwen 多停在 Build 级，主路径行为对不齐。

**组会一句：** 不是“找到 click 源码”，而是把 decorator 框架 + runner **解耦搬出来**——四个模型里几乎全军覆没。

---

### C. configobj — 配置 Round-trip + configspec 校验

**路径：** `benchmark/tasks/configobj__roundtrip_config_core__001/`  
**上游：** configobj（INI-like 配置）

**为什么有工程价值：** 读配置、写回、保留注释/顺序、按 schema 校验——运维与工具链刚需。禁止 `import configobj`。

| 层 | 考什么 | 例子 |
| --- | --- | --- |
| Public | 解析嵌套 section、write 后再读回 | `[owner] name = Ada`；keys round-trip |
| Hidden | **注释保留**、configspec 校验失败展平、extra values | `# banner` 写回仍在；`port=3` 不满足 `integer(min=10)` |

**冻结结果：** DeepSeek **过**；GPT-OSS / Qwen3.5 / Qwen3.6 全部 **Public✓ Hidden✗**。

**组会一句：** 三个模型都能“读改写配置”，但卡在注释保真与校验契约——**Public 过 ≠ 题过** 的最整齐证据。

---

### 三道题怎么一起讲（2 分钟版）

```text
itsdangerous  → 安全语义（过期/错误类型）
click         → 框架解耦（CLI decorator 栈）
configobj     → 配置保真（注释/校验细节）
         ↓
共同点：完整仓库 + 公开契约 + 禁运原包 + Public/Hidden/Isolation
```

---

## 5. 信息边界（设计核心）

### Agent 能看见

- 固定版本的**完整上游仓库**
- **完整公开功能契约**（API、行为、forbidden）
- 提交包布局与依赖锁

### Agent 看不见

- 实现位置提示（Main 下不对 Agent 暴露 entrypoints）
- Benchmark 自建 public / hidden 测试
- Reference / oracle、难度标签

### Agent 要交

- `submission/featurelifted/` 独立包

**条件名称：** Full-Repository / No-Hint Main

```text
Agent 可见          │ 完整 repo + 公开契约 + 依赖锁
Agent 不可见        │ 定位提示 + 评测测试 + reference
交卷后评测          │ Build ∧ Public ∧ Hidden ∧ Isolation
                    │ + 独立报告的 Compactness
```

---

## 6. 题目怎么出

1. **真实仓库**：固定 commit，完整 source tree  
2. **公开契约写清楚**：`required_api`、行为、forbidden  
3. **两级测试、同一契约**  
   - **Public** ≈ 基础功能 / 主路径  
   - **Hidden** ≈ 边界 / 保真细节 / 异常；不得偷偷加新 API  
4. **可带主纠缠机制**：framework / config / data_model 等（一题可多因，标注的是 dominant）  

三道旗舰题分别示范了：安全边界、框架纠缠、配置保真——不是同一类玩具题刷分。

---

## 7. 怎么打分

```text
Functional Pass = Build ∧ Public ∧ Hidden ∧ Isolation
```

| 门 | 含义 |
| --- | --- |
| **Build** | 能否安装 / 导入 |
| **Public** | 基础功能对齐公开契约 |
| **Hidden** | 更严边界仍对齐 |
| **Isolation** | 真解耦（禁运原包、不碰评测私货） |

主指标：**Functional Pass@1**（不以 Agent 是否跑完流程为准）。  
Compactness 单独报告。

### 三道旗舰题结果对照（冻结 Python-150）

| 题 | DeepSeek | GPT-OSS | Qwen3.5 | Qwen3.6 |
| --- | :---: | :---: | :---: | :---: |
| itsdangerous | **F** | Public✓ Hidden✗ | Build 级 | Build 级 |
| click | **F** | Build 级 | Build 级 | Build 级 |
| configobj | **F** | Public✓ Hidden✗ | Public✓ Hidden✗ | Public✓ Hidden✗ |

（F = Functional 全过。）

---

## 8. 当前规模与总体结果

### Benchmark 状态

- **Python-200** = 冻结 Python-150 + 平衡 External-50  
- 任务包已可跑；正式全量模型实验仍在推进  

### 冻结 Python-150（Functional Pass@1；DeepSeek 已补齐）

| 模型 | 覆盖 | Pass@1 | 备注 |
| --- | ---: | ---: | --- |
| DeepSeek V4 Flash | 150/150 | **99/150（66.0%）** | 显著领先 |
| Qwen3.5 122B | 150/150 | **59/150（39.3%）** | 与 3.6 打平 |
| Qwen3.6 35B | 150/150 | **59/150（39.3%）** | context 违规更多 |
| GPT-OSS 120B | 150/150 | **27/150（18.0%）** | 显著更弱 |

完整表：[`reports/paper_analysis/python150_with_deepseek150_20260805/`](../reports/paper_analysis/python150_with_deepseek150_20260805/README.md)

### 组会可说的结论

1. 任务偏难、有区分度（约 18%–66%）  
2. 同覆盖排名：**DeepSeek ≫ Qwen3.5 ≈ Qwen3.6 ≫ GPT-OSS**  
3. 旗舰题说明失败常在 **契约细节 / Hidden**，不只是找不到代码  
4. 必须以 Functional Pass 为准；尚无最终 Python-200 leaderboard  

---

## 9. 口头三句话（备用）

1. 我们评的是「从完整仓库抽独立模块」，不是修 issue。  
2. 三道硬题：签名 token、CLI 框架、配置 round-trip——都禁运原包，都要过 Public/Hidden/Isolation。  
3. 常见挂法是 Public 过了 Hidden 不过；说明瓶颈在契约闭合，不在“会不会搜仓库”。  

---

## 10. 例题速查（投屏）

| 题 | 路径 | 交付核心 | 禁运 |
| --- | --- | --- | --- |
| A 安全 | `.../itsdangerous__timed_serializer_core__001/` | `URLSafeTimedSerializer` | `itsdangerous` |
| B CLI | `.../click__option_parser__001/` | command/option + `CliRunner` | `click` |
| C 配置 | `.../configobj__roundtrip_config_core__001/` | `ConfigObj` + validate | `configobj` |

---

## 11. 相关文档

| 需要 | 文档 |
| --- | --- |
| 当前规模 / blocker | `docs/STATUS.md` |
| 实验结果能说明什么 | `docs/FINDINGS.md` |
| 设计全文 | `docs/BENCHMARK_DESIGN.md` |
| 评测规范 | `docs/EVALUATION.md` |
| 任务出题规则 | `docs/TASK_DESIGN_RULES.md` |

# Self-Authored Contract（自举合约）— 协议 v0 + focus 结果

> **Documentation status: archived · Indexed: 2026-08-04**

**状态：** 已实现首版；focus（alembic+click）**已跑完（2026-07-30）→ Functional 0/2，弱于 clean3**  
**动机：** clean3 证明「脚手架模板出题 + 模型答题」能抬 public，但模型只刷现成题单；用户要求 **由大模型自主出题**。  
**对照：** [METHOD_EXEC_CONTRACT.md](METHOD_EXEC_CONTRACT.md)（模板/AST 出题）· [METHOD_TEST_DRIVEN_COGNITION.md](METHOD_TEST_DRIVEN_COGNITION.md)（自编探针已失败）  
**试点目录：** `experiments/self_contract_pilot/` · **结果：** `FOCUS_RESULTS.md`（当前 checkout 均未保留）  
**臂名：** `--arm self_contract`（勿与 `exec_contract` 混报）

---

## 0. Focus 结论（先看这里）

| Arm | alembic | click | Functional |
|---|---|---|---|
| Main | p✗ h✗ | p✗ h✗ | 0/2 |
| **exec clean3** | **p✓ h✗** | **p✓ h✗** | 0/2（最佳 public） |
| self_contract `…-140322` | p✗ h✗ | p✗ h✗ | 0/2 |

- 闸门：两题 `author_ok` + `impl_ok`（合约绿），formal 仍挂 → **空包必红挡假绿，挡不住错故事**。  
- alembic：自出 B006 `get_revision("base") is None` → 实现把 `"base"` 当符号 → 同 clean4。  
- click：自出题漏 `invoke` → public `AttributeError`。  
- **H-SAC 在本 focus 未获支持**；干净模板上限仍看 clean3。勿扩 12 直至协议有新闸门/提示假设。

---

## 1. 人话

不要我们（程序模板）替模型出小测验。  
让模型自己根据 **题目说明 + 原仓库** 写出可执行的 `contracts/`，**先冻结题目**，再实现 `featurelifted`，最后用这些题验收。  
正式 public/hidden **始终不给模型看**。

---

## 2. 和现有两条路差在哪

| | TD-Cognition | Exec-Contract (clean3) | **Self-Authored Contract** |
| --- | --- | --- | --- |
| 谁出题 | 模型自编 probes | **Harness 模板**出 contracts | **模型**出 contracts |
| 题靠谱吗 | 常浅/错，锁死错误故事 | 靠谱但覆盖窄，模型「考啥做啥」 | **focus：题可绿但偏/漏**（base 泛化；漏 invoke） |
| 行为真值 | 无 | 可选上游 Phase0 事实 | **可选**注入事实，但**不替模型写断言** |
| 交卷门 | 探针（曾假绿） | 模板合约 pytest | **自出合约** pytest + 硬闸 |

**不是**回到 TD：TD 的失败是「错探针 + 弱门」。本臂要解决的是 **出题自主性**，同时用更狠的冻结与实质闸门，避免再锁死胡编。

---

## 3. 核心假说

**H-SAC：** 在 test-blind 下，由同一（或同系列）模型 **先写出打向 `featurelifted` 的实质合约并冻结**，再实现，相对 Main / 模板 Exec-Contract，能提高 Functional Pass，或至少在「模板没写到的 TASK 行为」上减少漏做。

**机制假设：** 模型出题时被迫把 TASK/源码读成可检查断言；答题阶段不能改题，只能改实现。

---

## 4. 协议（必须按阶段）

### 4.0 可见性（全程）

| 可见 | 不可见 |
| --- | --- |
| `TASK.md` / `public_spec`、`repo/`、（可选）`RUNTIME_FACTS` | benchmark `public_tests` / `hidden_tests` / eval 日志 |

研究者看 formal 失败后 **不得** 把同构断言塞进 prompt 或种子合约。

### 4.1 Phase A — 出题（只出题，不写 submission）

**输入：** TASK + repo +（可选）上游 Phase0 事实（只作参考，不是现成 pytest）。  

**输出（强制）：**

```
contracts/
  test_*.py          # 必须 import featurelifted，含真实 assert
  README.md          # 模型用一句话说明每条题在验 TASK 哪条行为
CONTRACT_MANIFEST.json  # 文件列表 + sha256，用于冻结
```

**硬禁止：**

- `assert True` / 空 `pass` / 无条件 `pytest.skip` 充当主断言  
- 删除或弱化稍后的合约  
- `import` 原包顶替 `featurelifted`  
- 猜测 / 编造 benchmark 隐藏用例字面量（报错大小写、hidden 专用图等）

**出题闸门 `gate_author.ok`（全过才进入 Phase B）：**

1. `contracts/` 可收集，且 **至少 N 条** 非 skip 用例（建议 N≥5，可配置）。  
2. **实质分：** 对「故意缺实现的空 `featurelifted`」跑合约 → **必须大面积失败**（证明题在验真东西，不是假绿）。  
3. **静态黑名单：** 源码中不得出现 `assert True`、以及已知泄漏串（可选表）。  
4. **覆盖清单：** README/manifest 须声明覆盖了哪些 `public_spec.behaviors` id；未覆盖的 id 记 `gaps`（不强制 100%，但写入 audit）。

出题轮次：默认 **1 次**；闸门失败可 **1 次重修出题**，仍失败则本臂记 `author_failed`（与实现失败分开统计）。

### 4.2 Freeze — 冻结

Harness 计算 `CONTRACT_MANIFEST` 哈希，写入 `contracts.lock`。  
Phase B **禁止**修改 `contracts/`（校验哈希；改了即 `tamper` 失败）。

### 4.3 Phase B — 答题（只实现）

**输入：** 冻结后的 contracts + TASK + repo +（可选）facts。  

**输出：** `submission/featurelifted/`。  

**动作：** `PYTHONPATH=submission pytest contracts/ -q` 必须过。  
失败可 **1 轮 repair**（只改 submission，不改 contracts）。

**实现闸门 `gate_impl.ok`：** verify 绿 + 未篡改 lock +（可选）禁止 contracts 目录 mtime/hash 变化。

### 4.4 Phase C — 正式 eval

与 Main 相同：private public/hidden。  
主指标：Functional Pass。  
辅指标：`gate_author` / `gate_impl`、自出题条数、repair 次数、与 Main/clean3 的翻盘表。

---

## 5. 防「自己出假题」的关键设计

TD 已证明模型会出浅题。本臂默认启用：

| 机制 | 作用 |
| --- | --- |
| **空实现必红** | 题打空包必须失败 → 堵住 `assert True` |
| **冻结** | 不能改题迎合烂实现 |
| **出题/答题分相** | Prompt 与工具权限上 Phase A 不鼓励写 submission；Phase B 不开放改 contracts |
| **行为对齐声明** | 强迫对照 `behaviors` id，减少纯 hasattr 堆砌 |
| **（可选）批评轮** | 同一模型或短提示：只审 contracts 是否过弱，输出 `critique.md`；不自动改题除非 author repair |

**不做：** 用 formal 失败当老师来改 contracts（= 泄题）。

---

## 6. 与 Exec-Contract 模板的关系

| 模式 | 用途 |
| --- | --- |
| `exec_contract` 模板合约 | 已有 clean3 基线；模板出题 |
| `self_contract` | 本草案；模型出题 |
| 消融 | 同题：Main / clean3 / self_contract；**禁止**把泄漏 v2c 当主结果 |

可选混合（**非默认**）：Phase0 只产 `RUNTIME_FACTS`（无模板 pytest），供出题模型参考——仍是「模型写断言」。

---

## 7. 最小实现清单（工程）

1. `harness/.../self_contract/`：`author` → `freeze` → `implement` → `verify` → `audit`  
2. `agents.example.toml` profile：`openhands_*_self_contract`  
3. `--arm self_contract`  
4. 闸门：空包必红、manifest lock、禁止弱化  
5. 先 **alembic+click** focus，再考虑 12 题  

**成功信号（focus）：** ~~相对 Main 有 Functional 增益，或相对 clean3…~~ → **未达成**。  
**失败信号（已出现）：** `gate_author`/`gate_impl` 高但 Pass≤Main；锁死错误符号故事；漏 required API（`invoke`）。

---

## 8. 风险（写进故事里）

1. **重蹈 TD：** 自出题仍然浅/偏 → 空包必红 + 冻结缓解假绿，**不保证**故事正确（focus 已证实）。  
2. **费用/时延：** 出题+实现两阶段，比 clean3 更贵。  
3. **与模板合约重叠：** 若自出题碰巧像 hidden，只要生成时不可见 formal，仍算干净；**研究者不得用失败日志调 prompt**。  

---

## 9. 一句话立项

> **Self-Authored Contract：test-blind 下，模型先出可执行合约并冻结，再实现；用空包必红与锁题防止假绿与改题作弊。**  
> Focus 注记：机制跑通，**未**带来 Pass 增益；错题锁定与漏 API 是主风险。

---

## 10. 下一步

1. ~~落 `self_contract` 臂骨架 + 空包闸门~~  
2. ~~focus 跑 alembic+click，对照 Main / clean3~~ → 历史结果路径：`experiments/self_contract_pilot/FOCUS_RESULTS.md`（当前 checkout 未保留）  
3. 协议未改前 **不扩 12**；若再试：出题提示「id 优先于符号」+ 强制覆盖 required methods；可选批评轮（仍禁 formal 回填）  

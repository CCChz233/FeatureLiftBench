# Agent 瓶颈：具体案例汇报

> **Status: archived · Last verified: 2026-09-02**
> 冻结 Python-150 · Full-Repository / No-Hint · 定性案例，不更新主表数字。
> 旧 150+E50 的 72% **不是** Python-200' 主表。Hard-50 校准见 [STATUS.md](../../STATUS.md)。
> 目的：把「契约闭合失败 / 过早停止」讲成能听懂的例子，不讲抽象词。

---

## 1. 先说结论（30 秒）

当前 agent **不是**主要败在「找不到文件」或「装不上包」。

Python-200 上：Flash 的功能失败主体是 Hidden；Qwen / GPT-OSS 更多卡在 Public。
方法侧的自测、结构门、上游双跑都补不了评测私有行为，见 [FINDINGS.md](../../FINDINGS.md)。

常见失败是：

1. **主路径做对了，契约里的边界没做完就交卷**（过早停止）
2. **看起来像原功能，但 Hidden 要求的行为/接口对不齐**（契约没闭合）

下面先解释「契约级行为闭合」是什么意思，再用三道真题说明。

---

## 2. 什么叫「契约级行为闭合」？

**一句话：** 题目先把「什么叫做对」写清楚；测试只验证这些；Agent 交付的行为要**完整满足**这套说明——不能少做，也不能靠猜 Hidden 会考什么。

### 拆词（不抽象版）

| 词 | 在这套 benchmark 里指什么 |
| --- | --- |
| **契约** | Agent 能看到的公开说明：要交什么 API、什么行为、什么禁止项（`TASK.md` + `public_spec`） |
| **行为** | 可观察结果：返回值、异常**类型**、边界秒数、注释是否保留——不是「代码长得像上游」 |
| **闭合** | 该写的都写了、该测的都测了、测的和写的是同一套；没有「TASK 没写但 Hidden 偷偷考」，也没有「TASK 写了但实现没做到」 |

### 什么叫闭合 / 什么叫没闭合

| 情况 | 闭合？ | 对应下面哪道题 |
| --- | :---: | --- |
| TASK 写了「过期必须抛 `SignatureExpired`」，Hidden 真测这个，实现也抛对类型 | ✓ | 案例 A（DeepSeek 过） |
| TASK 写了过期语义，Agent 只实现 roundtrip，过期也抛 `BadSignature` 或笼统错误 | ✗ | 案例 A（GPT-OSS 挂） |
| TASK 要求注释保留 + configspec 校验，Public 读写过了，Hidden 测注释/校验 | ✗ | 案例 B |
| 大段拷贝 cache-key 代码，Public 过，但契约要求的 `normalize_body` 导出缺失 | ✗ | 案例 C |
| TASK 只写「能签名解密」，测试却要求特定 HMAC 实现细节（契约没写） | ✗ | 出题侧要避免；不算 Agent 的锅 |

### 和评测怎么对上

```text
TASK 公开契约（写什么 API、什么行为）
        ↓ 对齐
Public 测试（主路径：能跑、基本行为对）
        ↓ 同一契约的延伸，不是另一套题
Hidden 测试（边界、异常类型、required 导出、保真细节）
        ↓
Functional Pass = 行为真正闭合
```

所以 **Public✓ Hidden✗** 不是「题变难了」，而是：**主路径像做完了，契约里更细的条款还没闭合**。

### 和两种瓶颈的关系

| 现象 | 本质 |
| --- | --- |
| **契约没闭合** | TASK 里写清楚的行为/接口，实现没做全或做偏了 |
| **过早停止** | Agent 自测只覆盖主路径（如 roundtrip、基本读写），以为做完就 `finish`，没去对齐 Hidden 会考的边界 |

两者常一起出现：自测太浅 → 早停 → Hidden 暴露契约没闭合。

---

## 3. 案例 A：签名过了，过期语义不过

**题：** `itsdangerous__timed_serializer_core__001`
**场景：** 密码重置链接 / signed cookie——要抽出带过期的 URL-safe 签名器。

要交的 API：

```python
from featurelifted import BadSignature, SignatureExpired, URLSafeTimedSerializer
```

| 层 | Agent 通常怎么做 | 评测考什么 |
| --- | --- | --- |
| Public | `dumps` → `loads` 能回来；改 token 报错 | 基本加签/解签、防篡改 |
| Hidden | 往往不再细抠 | `max_age` 边界秒必须抛 **`SignatureExpired`**，不是笼统错误 |

**冻结结果：**

| 模型 | Build | Public | Hidden | Functional |
| --- | :---: | :---: | :---: | :---: |
| DeepSeek | ✓ | ✓ | ✓ | ✓ |
| GPT-OSS | ✓ | ✓ | **✗** | ✗ |
| Qwen3.5 / 3.6 | ✓ | ✗ | ✗ | ✗ |

**怎么讲：**
GPT-OSS 已经能「写出个 HMAC、签进去解出来」，但过期边界不对就挂了。
→ 对照 §2：**行为边界未闭合**（`SignatureExpired` vs 笼统错误）；若 Agent 自测只跑了 roundtrip 就 finish，就是 **过早停止**。

**组会一句：** 测的是过期语义闭合，不是「会不会写签名」。

---

## 4. 案例 B：配置读写过了，注释和校验不过

**题：** `configobj__roundtrip_config_core__001`
**场景：** 读 INI 配置、写回、按 schema 校验。

| 层 | 主路径（易过） | Hidden（易挂） |
| --- | --- | --- |
| Public | 解析 section、写后再读回 | — |
| Hidden | — | **注释保留**；`configspec` 校验失败；非法值展平 |

**冻结结果：**

| 模型 | Public | Hidden | Functional |
| --- | :---: | :---: | :---: |
| DeepSeek | ✓ | ✓ | ✓ |
| GPT-OSS | ✓ | **✗** | ✗ |
| Qwen3.5 | ✓ | **✗** | ✗ |
| Qwen3.6 | ✓ | **✗** | ✗ |

**怎么讲：**
三个模型都能「读改写配置」，看起来功能齐了，却在注释保真、校验契约上挂掉。
→ 对照 §2：**Public✓ Hidden✗** —— TASK 里写了、Hidden 测了，但实现没闭合。

**组会一句：** 能改配置 ≠ 题过了。

---

## 5. 案例 C：代码拷到了，缺一个契约要求的导出

**题：** `requests_cache__cache_key_core__hard3_001`
**场景：** 抽出 cache-key / 策略相关能力。

轨迹审计里的典型行为：定位并拷贝了 cache-key 相关区域，public 能过，但 Hidden 失败——契约要求的 **`normalize_body` 导出缺失**。

**冻结结果：**

| 模型 | Public | Hidden | Functional |
| --- | :---: | :---: | :---: |
| DeepSeek | ✓ | **✗** | ✗ |
| GPT-OSS | ✓ | **✗** | ✗ |
| Qwen3.5 | ✓ | **✗** | ✗ |
| Qwen3.6 | ✗ | ✗ | ✗ |

**怎么讲：**
不是没找到相关代码，甚至可能大段拷贝；缺的是契约面上的一个接口。
→ 对照 §2：**定位成功 + 拷贝很多 ≠ 契约闭合**；自测若只覆盖主路径就会过早 finish。

**组会一句：** 拷贝量不是闭包证据。

---

## 6. 三道题对照（一张表讲完）

| 案例 | 表面上看 | 实际挂在哪 | 契约闭合？ | 对应瓶颈 |
| --- | --- | --- | :---: | --- |
| itsdangerous | 会签名 | 过期 / 错误类型 | ✗ | 行为边界未闭合 + 易早停 |
| configobj | 会读写配置 | 注释 / 校验保真 | ✗ | Public✓ Hidden✗ |
| requests_cache | 找到并拷了相关代码 | 缺 required 导出 | ✗ | 定位≠闭合 |

---

## 7. 和「失败分布」对上

四模型合计失败里，首败大约：

- **Public ~57%** — 主路径契约就没对齐（如弱模型在 click / itsdangerous）
- **Hidden ~33%** — 主路径过了，边界/接口没闭合（如 configobj、requests_cache、GPT-OSS 的 itsdangerous）

Build / Isolation 都不是主故事。

---

## 8. 汇报收口（可直接念）

> Agent 现在不缺「去仓库里找实现」的能力。
> 缺的是：按题目公开契约，把主路径 **和** 边界行为都做完，再交卷——也就是 §2 说的 **契约级行为闭合**。
>
> itsdangerous：签名过了、过期语义不过。
> configobj：读写过了、注释校验不过。
> requests_cache：代码在、导出不齐。
>
> 这就是我们说的 **契约没闭合** 和 **过早停止**——§2 有定义，§3–§5 是三道真题。

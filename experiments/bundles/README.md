# Experiment bundles

实验传输包的落地区。原始压缩包通常很大，默认不进 Git；校验和与说明文件进 Git。

## 布局

| 目录 | 用途 |
| --- | --- |
| `incoming/` | 新收到、尚未确认的结果包 |
| `outgoing/` | 本机打出的可传包（含 runnable / oracle-only） |

## 可跑整包（推荐服务器部署）

在开发机（已有 oracle + archives）打一份「解压即可过 paper preflight」的包：

```bash
./scripts/build_runnable_bundle.sh
# -> experiments/bundles/outgoing/FeatureLiftBench-runnable-<stamp>.tar.gz
```

包内含：代码、`benchmark/tasks`、`benchmark/submissions/*/oracle`、`benchmark/sources/archives`。  
不含：`.env`、Docker 镜像、`.venv`、本机 `agents.toml`。

服务器：

```bash
tar -xzf FeatureLiftBench-runnable-*.tar.gz
cd FeatureLiftBench-runnable-*
# 按包内 BUNDLE.md 做 setup / 镜像 / plan
```

只传 oracle 时仍可用更小的 `flb_python150_oracles_*.tar.gz`。

## 结果包导入

- 导入前检查压缩包成员，拒绝绝对路径和 `..` 路径穿越。
- 导入后保留原包与 SHA-256，原始 run 放回其规范的 track/model/run 目录。
- bundle 只是传输副本，不参与指标扫描。

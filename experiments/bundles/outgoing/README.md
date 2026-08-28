# Outgoing Bundles

> **Documentation status: reference · Last verified: 2026-08-28**

当前**题包压缩包**（完整 `benchmark/`，含 150、Hard-50、archives、wheels；不含代码）：

- 文件：`FeatureLiftBench-benchmark-20260828.tar.gz`（约 690 MB，与本 README 同目录）
- 校验：[`current/FeatureLiftBench-benchmark-20260828.tar.gz.sha256`](current/FeatureLiftBench-benchmark-20260828.tar.gz.sha256)

该 tar 不进 Git。GitHub 上只有 checksum。服务器上放到仓库根旁解压：

```bash
shasum -a 256 -c experiments/bundles/outgoing/current/FeatureLiftBench-benchmark-20260828.tar.gz.sha256
tar -xzf FeatureLiftBench-benchmark-20260828.tar.gz
# 得到 ./benchmark/ ，覆盖或放到仓库根下
```

旧的 `scripts/build_runnable_bundle.sh` 仍从**已提交** revision 打「代码+旧 Python-200」包，不含未提交的 Hard-50。新主套件请用上面这个 20260828 题包 + `git clone` 代码。

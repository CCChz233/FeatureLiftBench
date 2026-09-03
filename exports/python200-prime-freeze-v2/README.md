# 上传这个文件夹

这是 **Python-200′ freeze v2** 的唯一上传包。旧 overlay、旧结果校验和已挪到 `../archive/`。

传这三个文件（约 2.0 GiB）：

1. `worktree.tar.gz` — freeze v2 题包和工作树
2. `overlay-offline.tar.gz` — Hidden / Oracle / wheels / 源码包
3. `images.tar.gz` — 已钉的 eval + agent 镜像

先校验：

```bash
shasum -a 256 -c SHA256SUMS
```

## 服务器上

不要 `git clone`。按顺序：

```bash
mkdir -p FeatureLiftBench
tar -xzf worktree.tar.gz -C FeatureLiftBench
python3.12 FeatureLiftBench/scripts/build_python200_server_overlay.py --verify overlay-offline.tar.gz
tar -xzf overlay-offline.tar.gz -C FeatureLiftBench
docker load < images.tar.gz
```

到 `FeatureLiftBench` 里自己配 `.env`（包里没有密钥）。

```bash
cd FeatureLiftBench
python3.12 scripts/build_python200_prime_final_freeze.py --check \
  --agent-image featureliftbench-agent:python200-prime-212930ea \
  --evaluator-image featureliftbench-eval:python200-prime-212930ea

./scripts/run_benchmark.sh --benchmark python200_hard --agent openhands --method main \
  --output experiments/python/openhands/<model>/python200-prime-main-r1 \
  --docker --workers 1 --timeout 3600
```

身份：freeze `6c20ff03…` / candidate `212930ea…`。不要跑 `run_python200_paper.sh`（那是旧 150+E50）。

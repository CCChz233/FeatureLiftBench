# Experiment Bundles

> **Documentation status: reference · Last verified: 2026-08-04**

| Directory | Purpose |
| --- | --- |
| `incoming/frozen-results/` | canonical received result archives |
| `outgoing/current/` | current runnable server package |
| `archive/releases/` | frozen historical deployment package |
| `archive/methods/` | unique method evidence package |
| `retired/` | temporary quarantine before verified deletion |

Tar 文件默认不进 Git；SHA256、状态和删除依据记录在
[`registry/bundle_ledger.json`](../registry/bundle_ledger.json)。导入前必须检查绝对
路径、`..` 逃逸和 symlink target。

# FeatureLiftBench methods

> **Status: current · Last verified: 2026-08-28**

`method/` is the public catalog of protocols that can be crossed with any
registered agent and benchmark suite. Implementation (prompt flags, checkers,
condensers) stays in `harness/`. Frozen method JSON specs stay in
`harness/config/methods/`. This directory only names the protocol and maps it
to `--agent-profile` plus `run-agent` flags.

Official paper Main is **No-Hint Full-Repository**. Benchmark design does not
force a particular agent workflow; methods here are optional protocols and
ablations. Scaffolding methods that failed screening stay registered as
`retired` or `screening` so old runs remain reproducible. Do not expand them
onto Python-200'.

## Registry (selected)

| Id | Role | Paper table |
| --- | --- | --- |
| `main` | Official No-Hint Full-Repository | yes (with OpenHands) |
| `v1` | Main + 2M token cap | cost arm; not the unreleased 200' main table |
| `entrypoint_hint` | Information ablation | no |
| `public_feedback` | RQ6 public-tests mount | no |
| `short_prompt` | Information ablation | no |
| `pruned_context` | Information ablation | no |
| `autosaddler` | Prompt-only AutoSaddler pack (screening) | no |

`--arm` is an alias of `--method`. Source of truth: [registry.toml](registry.toml).

```bash
PYTHONPATH=harness python3.12 -B -m featureliftbench.cli catalog list --kind methods
```

## Add a method

1. If the protocol needs new harness flags, add them to `run-agent` first.
2. Register id, aliases, `run_agent_flags`, and per-agent profiles in
   `registry.toml`.
3. Point `spec` at `harness/config/methods/*.json` when a frozen spec exists.
4. Mark `paper_table = false` unless the method is Official Main.
5. Run `catalog check`. Do not treat a new method as a paper contribution
   without a pre-registered comparison and a screening stop rule.

AutoSaddler-FLB (`--method autosaddler`) is a prompt-pack optimizer with a
separate train loop. See [METHOD_AUTOSADDLER.md](../docs/METHOD_AUTOSADDLER.md).

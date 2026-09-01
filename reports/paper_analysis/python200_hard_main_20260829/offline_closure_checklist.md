# Python-200′ offline evidence-closure checklist

> **Status: wheels closed 2026-08-30 · 84-task replacement running on local `latest` images**

## Completed in this pass

- [x] Verify and fingerprint the received archive, suite, selection, source registry, and taxonomy.
- [x] Produce a non-retroactive provenance attestation and per-task identity map.
- [x] Identify 17 freeze-preflight blocks that never launched an agent.
- [x] Audit all 59 context-window violations, their overage severity, and current outcomes.
- [x] Identify all 16 build-stage outcomes as unavailable offline dependencies.
- [x] Separate infrastructure outcomes from model/output failures across all 68 nominal non-passes.
- [x] Freeze an outcome-independent strict replacement union of 84 task IDs.
- [x] Produce candidate paper tables and a Results draft with eligibility-safe language.
- [x] Produce a checksum manifest for the offline evidence package.

## Follow-up 2026-08-30 (wheels only)

- [x] CPython 3.11 Linux wheel coverage **200/200** (`audit_python200_wheels.py`).
- [x] Freeze input `--check` still matches tree
  `98463b9d37757bb0ab4db4d4ff1389a3f3b6d50767eba43f89ea5eb273de1138`.
- [x] Independent replacement directory prepared (no `run.json`):
  `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260830-strict84-replacement/`.
- Record: `experiments/registry/python200_hard_wheel_closure_and_strict84_20260830.md`.

## Still requires experiment execution

- [x] Repair and preflight the offline wheel set for all 16 dependency failures (audit 200/200; Docker eval of those 16 still needs the paper-pinned eval image).
- [ ] Resolve the 17 task-spec/freeze mismatches against the intended immutable task packages (frozen input exists; replacement in progress on freeze input).
- [ ] Execute the frozen 84-task strict replacement set with hard context enforcement (started 2026-08-30T09:51:23Z on local `latest`; not paper-pinned).
- [ ] Merge replacement outcomes by the preregistered task-ID rule and regenerate the final table.
- [ ] Run the planned stratified stability repeats, or keep the limitation explicit.
- [ ] Run at least one additional model on the eligible Python-200′ suite, or narrow cross-model claims.

**Image deviation (declared):** received-suite Docker digests
`sha256:0843b6633d48da91832ce16c0e6ac42baf2f04d7b08cb66061720f176a8f2eea` (agent) and
`sha256:d1ea357c125a6f4957e1246f770bd1deb4717448e46e779f62b0351213cad191` (eval)
are still absent. The running replacement uses local `latest` (`cc622920…` /
`cccf858c…`). Outcomes are not paper-mergeable until those digests match or the
mismatch is kept as an explicit limitation.

## Promotion rule

Do not promote `132/200` into the abstract or final leaderboard. Promotion requires a direct freeze
binding, zero unresolved dependency/preflight failures, hard context compliance, and a reproducible
paper bundle built from the merged eligible result.

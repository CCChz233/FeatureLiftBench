# Python-200′ candidate provenance attestation

> **Status: candidate blocked · Verified from received files: 2026-08-29**

This document attests the received bytes and reconstructable identity. It does not promote the run into the paper leaderboard and does not alter the original suite.

## What is positively attested

- Task identity: 200/200 selected IDs match; no missing or extra IDs.
- Source identity: 183 emitted snapshot IDs match and 0 mismatch; 17 are unavailable.
- Runtime identity: agent `sha256:0843b6633d48da91832ce16c0e6ac42baf2f04d7b08cb66061720f176a8f2eea`; evaluator `sha256:d1ea357c125a6f4957e1246f770bd1deb4717448e46e779f62b0351213cad191`.
- Received archive SHA256: `15d82d53adcf7488d3684d5153cc4c2221563191672a90e431ed504ae6ff81cc`.
- Selection task-set SHA256: `a28c301e83bf62b831c007b7c5ebc4fd0f6e4c012496d812fa90d233dfe81ad3`.

## What is not attested

- The original suite has no direct `benchmark_freeze_id` field.
- 17 tasks never launched because the active spec hash disagreed with the freeze.
- 16 evaluations stopped at offline dependency installation.
- 59 attempted runs violated the prompt allowance.
- The strict replacement union is therefore **84 tasks**.

## Interpretation

The package is authentic and task-set reconstruction is strong, but the execution is not a complete eligible Python-200′ Main result. `132/200` is retained only as the received-suite audit headline. Final paper scoring requires replacement runs for the frozen union in `strict_replacement_task_ids.txt`.

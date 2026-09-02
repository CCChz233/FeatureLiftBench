# Archived one-shot scripts

> **Status: current · Last verified: 2026-09-02**

These were used to build historical freezes, External-150 replacements, and
contract-closure dossiers. They are not daily entrypoints. Keep them so a freeze
or overlay can be rebuilt; do not call them for new Python-200′ Main runs.

The live entry is `./scripts/run_benchmark.sh`. Inventory:
[../README.md](../README.md).

| Script | Why it is here |
| --- | --- |
| `audit_new_protocol_readiness.py` | Pre-v3 protocol gate |
| `audit_v2_main_readiness.py` | v2 Main readiness |
| `build_v2_benchmark_freeze.py` | v2 freeze builder |
| `build_compactness_registry.py` | Historical compactness registry |
| `build_spec_freeze.py` | Spec freeze |
| `revalidate_v2_oracles.py` / `revalidate_v3_oracles.py` | Dated oracle revalidation |
| `run_v3_adversarial_canaries.py` | v3 canaries |
| `build_v3_846_release_bundle.sh` | Dated release bundle |
| `build_external150_selection_ledger.py` and External-150 populate/promote/scaffold/split/pruned | External-150 replacement wave |
| `materialize_contract_closure_reviews.py` / `render_contract_review_dossiers.py` | One-shot closure dossiers |
| `harden_experiment_contracts.py` / `report_spec_compliance.py` | Historical contract hardening |

`scratch/` is local batch3/TFL drafts and stays gitignored.

Current freeze `--check` / overlay commands remain at `scripts/` root
(`build_python200_prime_*`, `build_v3_benchmark_freeze.py`,
`audit_v3_main_readiness.py`).

# Design card: pyotp__totp_hotp_core__001

**status:** `design_card_ready`  
**wave:** W5  
**package:** `pyotp`  
**repository_url:** https://github.com/pyotp/pyotp  
**planned_lift_type:** Direct  
**final_lift_type:** Direct  
**reclassification_reason:** None  
**feature_family:** protocol_state_transition  
**entanglement:** data_model_coupling  
**feature_one_liner:** TOTP/HOTP generate/verify  
**lift_review_flag:** none

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/archive/plans/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.TOTP(secret: str | bytes)"
  - "featurelifted.TOTP.at(for_time) / now / verify"
  - "featurelifted.HOTP(secret).at(count) / verify"
  - "featurelifted.random_base32()"
returns:
  - "otp strings; verify bool"
exceptions:
  - "declare"
defaults:
  - "interval 30 for TOTP"
state_effects:
  - "none"
```

## upstream_mapping

```yaml
primary_symbols:
  - "pyotp.TOTP"
  - "pyotp.HOTP"
supporting_components:
semantic_delta:
  - "Direct"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Fix time with freezegun only if needed; prefer at(timestamp).
```

## scope

```yaml
included:
  - "TOTP/HOTP generate/verify, random_base32"
excluded:
  - "QR provisioning network"
```

## feasibility

```yaml
commit: null  # resolve at pin/materialize
license: "MIT"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "local"
```

## acceptance

```yaml
closure_review: pending
reference_pass: pending
isolation_pass: pending
no_original_import: pending
overlap_check: pending
```

## agent_notes

- Staging path: `benchmark/staging/pyotp__totp_hotp_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.

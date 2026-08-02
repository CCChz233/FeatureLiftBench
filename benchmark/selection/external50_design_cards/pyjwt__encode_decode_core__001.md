# Design card: pyjwt__encode_decode_core__001

**status:** `design_card_ready`  
**wave:** W4  
**package:** `PyJWT`  
**repository_url:** https://github.com/jpadilla/pyjwt  
**planned_lift_type:** Adapted  
**final_lift_type:** Adapted  
**reclassification_reason:** None  
**feature_family:** serialize_format_render  
**entanglement:** data_model_coupling  
**feature_one_liner:** JWT encode/decode with algorithm options  
**lift_review_flag:** none

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.encode(payload: dict, key: str, algorithm: str = 'HS256', headers: dict | None = None) -> str"
  - "featurelifted.decode(jwt: str, key: str, algorithms: list[str], options: dict | None = None) -> dict"
  - "exceptions: InvalidTokenError, ExpiredSignatureError, InvalidSignatureError"
returns:
  - "JWT str; payload dict"
exceptions:
  - "PyJWT error types above"
defaults:
  - "algorithm HS256"
state_effects:
  - "none"
```

## upstream_mapping

```yaml
primary_symbols:
  - "jwt.encode"
  - "jwt.decode"
supporting_components:
  - "jwt.exceptions"
semantic_delta:
  - "Adapted JWT encode/decode"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  HS256 only.
```

## scope

```yaml
included:
  - "encode/decode, exp validation option"
excluded:
  - "JWKS fetch"
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
offline_resources: "local secrets"
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

- Staging path: `benchmark/staging/pyjwt__encode_decode_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.

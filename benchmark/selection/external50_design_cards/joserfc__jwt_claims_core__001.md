# Design card: joserfc__jwt_claims_core__001

**status:** `design_card_ready`  
**wave:** W3  
**package:** `joserfc`  
**repository_url:** https://github.com/authlib/joserfc  
**planned_lift_type:** Composite  
**final_lift_type:** Composite  
**reclassification_reason:** None  
**feature_family:** validate_normalize_construct  
**entanglement:** data_model_coupling  
**feature_one_liner:** JWS/JWT encode + claims validate pipeline  
**lift_review_flag:** none

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.jwt.encode(header: dict, claims: dict, key) -> str"
  - "featurelifted.jwt.decode(token: str, key, algorithms: list[str]) -> token object with claims"
  - "featurelifted.JWTClaimsRegistry / claims validate helpers used"
  - "featurelifted.OctKey.import_key / generate_key for tests"
  - "exceptions: JoseError, ExpiredTokenError, InvalidClaimError \u2014 declare"
returns:
  - "compact JWT string; claims dict"
exceptions:
  - "JoseError hierarchy"
defaults:
  - "alg HS256 in tests"
state_effects:
  - "none"
```

## upstream_mapping

```yaml
primary_symbols:
  - "joserfc.jwt"
  - "joserfc.jwk.OctKey"
supporting_components:
  - "joserfc.errors"
  - "joserfc.jws"
semantic_delta:
  - "encode/decode + claims validation pipeline"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  HS256 only for offline tests.
```

## scope

```yaml
included:
  - "HS256 JWT encode/decode, exp/nbf/iss claim checks"
excluded:
  - "JWKS URL fetch, asymmetric clouds KMS"
```

## feasibility

```yaml
commit: null  # resolve at pin/materialize
license: "BSD-3-Clause"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "local oct keys"
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

- Staging path: `benchmark/staging/joserfc__jwt_claims_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.

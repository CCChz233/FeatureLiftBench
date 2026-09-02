# Design card: cachecontrol__heuristic_store_core__001

**status:** `validated_staging`  
**wave:** W1  
**package:** `cachecontrol`  
**repository_url:** https://github.com/psf/cachecontrol  
**planned_lift_type:** Composite  
**final_lift_type:** Composite  
**reclassification_reason:** None  
**feature_family:** cache_retry_policy  
**entanglement:** data_model_coupling  
**feature_one_liner:** Heuristic expiration + DictCache store + serialize cached response  
**lift_review_flag:** none

**skim_status:** `pass-with-care` (2026-08-01)
**skim_notes:** Composite OK offline. Freeze: DictCache, ExpiresAfter, Serializer, CacheController cached_request/update_cached_response with fake responses. No requests Session/network.

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/archive/plans/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.DictCache()"
  - "featurelifted.BaseCache.get/set/delete(key)"
  - "featurelifted.Heuristic / ExpiresAfter(days=..., hours=...) apply(response) API (declare exact class)"
  - "featurelifted.serialize/deserialize cached response body+headers helpers used by CacheController subset"
  - "featurelifted.CacheController(cache, cacheable_methods=...) cached_request/update_cached_response subset"
returns:
  - "cache hit returns stored response parts; miss None"
exceptions:
  - "KeyError/ValueError on bad cache keys if any"
defaults:
  - "ExpiresAfter duration fields"
state_effects:
  - "DictCache mutable"
```

## upstream_mapping

```yaml
primary_symbols:
  - "cachecontrol.caches.DictCache"
  - "cachecontrol.heuristics"
  - "cachecontrol.controller.CacheController"
supporting_components:
  - "cachecontrol.serialize"
semantic_delta:
  - "Offline: do not wrap real urllib3; test heuristic+cache+serialize composition with fake response objects"
```

## oracle_basis

```yaml
basis: mixed
notes: |
  Avoid live HTTP; construct response-like objects.
```

## scope

```yaml
included:
  - "DictCache, expiration heuristic, serialize roundtrip, controller cache lookup/update"
excluded:
  - "requests Session integration, FileCache, RedisCache, network"
```

## feasibility

```yaml
commit: "aba0315599d7d4200074ab3606384732be7bbc25"  # tag v0.14.4
license: "Apache-2.0"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "fake response objects + DictCache only"
```

## acceptance

```yaml
closure_review: pass
reference_pass: pass
isolation_pass: pass
no_original_import: pass
overlap_check: pass
```

## agent_notes

- Staging path: `benchmark/staging/cachecontrol__heuristic_store_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.

# Design card: watchdog__observer_dispatch_core__001

**status:** `validated_staging`  
**wave:** W1  
**package:** `watchdog`  
**repository_url:** https://github.com/gorakhargosh/watchdog  
**planned_lift_type:** Composite  
**final_lift_type:** Composite  
**reclassification_reason:** None  
**feature_family:** protocol_state_transition  
**entanglement:** resource_coupling  
**feature_one_liner:** Observer + event handler registry + recursive scheduling  
**lift_review_flag:** none

**skim_status:** `pass-with-care` (2026-08-01)
**skim_notes:** Composite OK but platform-coupled. Prefer PollingObserver in tests for determinism. Freeze schedule/start/stop + FileSystemEventHandler create/modify/delete. Short timeouts + temp dir.

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.Observer()"
  - "featurelifted.Observer.schedule(handler, path: str, recursive: bool = False) -> Watch"
  - "featurelifted.Observer.start/stop/join"
  - "featurelifted.FileSystemEventHandler with on_created/modified/deleted/moved hooks"
  - "featurelifted.events: FileCreatedEvent, FileModifiedEvent, ... (declared subset)"
returns:
  - "schedule returns watch object; events delivered to handler methods"
exceptions:
  - "ValueError on invalid paths; OSError from FS"
defaults:
  - "recursive=False"
state_effects:
  - "background observer thread; tests must start/stop deterministically"
```

## upstream_mapping

```yaml
primary_symbols:
  - "watchdog.observers.Observer"
  - "watchdog.events.FileSystemEventHandler"
supporting_components:
  - "watchdog.events event classes"
  - "platform emitter"
semantic_delta:
  - "Compose observer + handler + event types; tests use temp dir + short polling"
```

## oracle_basis

```yaml
basis: mixed
notes: |
  Emitter behavior is platform-specific; freeze test strategy with temp files and timeouts.
```

## scope

```yaml
included:
  - "schedule recursive/non-recursive, handler callbacks for create/modify/delete"
excluded:
  - "inotify-specific flags, watchdog.watchmedo CLI, remote FS"
```

## feasibility

```yaml
commit: "a8829e350d76a9b6c9f716d242b42a34fbbd62fd"  # tag v6.0.0
license: "Apache-2.0"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "may use platform backends; pure polling fallback preferred in tests"
offline_resources: "local temp directory only; no network"
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

- Staging path: `benchmark/staging/watchdog__observer_dispatch_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.

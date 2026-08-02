# Design card: flask_login__session_guard_core__001

**status:** `validated_staging`  
**wave:** W1  
**package:** `flask-login`  
**repository_url:** https://github.com/maxcountryman/flask-login  
**planned_lift_type:** Composite  
**final_lift_type:** Composite  
**reclassification_reason:** None  
**feature_family:** registry_plugin_dispatch  
**entanglement:** framework_coupling  
**feature_one_liner:** LoginManager + user_loader + request/session guard helpers  
**lift_review_flag:** none

**skim_status:** `pass-with-care` (2026-08-01)
**skim_notes:** Composite OK with Flask allowed dependency. Freeze LoginManager/user_loader/login_user/logout_user/current_user/login_required/UserMixin. Tests use Flask test_request_context only.

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.LoginManager()"
  - "featurelifted.LoginManager.init_app(app)"
  - "featurelifted.LoginManager.user_loader(callback)"
  - "featurelifted.login_user(user, remember: bool = False)"
  - "featurelifted.logout_user()"
  - "featurelifted.current_user proxy attributes is_authenticated/is_anonymous/get_id"
  - "featurelifted.login_required decorator"
  - "featurelifted.UserMixin"
returns:
  - "login_user returns bool; current_user is proxy"
exceptions:
  - "Flask LoginException subset if any \u2014 prefer undocumented none; unauthorized handler"
defaults:
  - "remember=False"
state_effects:
  - "session keys _user_id/_fresh; requires Flask app/request/session context"
```

## upstream_mapping

```yaml
primary_symbols:
  - "flask_login.LoginManager"
  - "flask_login.login_user"
  - "flask_login.current_user"
supporting_components:
  - "flask_login.mixins.UserMixin"
  - "flask_login.utils"
semantic_delta:
  - "Compose manager+loader+session user + login_required; tests use Flask test_request_context"
```

## oracle_basis

```yaml
basis: mixed
notes: |
  Needs Flask as test dependency; no network. Declare Flask version bound in lockfile.
```

## scope

```yaml
included:
  - "user_loader, login/logout, login_required, UserMixin, remember flag basic"
excluded:
  - "LDAP, real HTTP servers, cookie encryption beyond Flask session"
```

## feasibility

```yaml
commit: "793e240e408802bb1b1fbdf57d36403ea204f0bc"  # tag 0.6.3
license: "MIT"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "Flask test client / request context only"
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

- Staging path: `benchmark/staging/flask_login__session_guard_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.

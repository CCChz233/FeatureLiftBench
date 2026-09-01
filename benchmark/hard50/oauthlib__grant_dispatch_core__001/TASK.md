# FeatureLift Task: Authorization-code grant dispatch

Build a standalone `featurelifted` package providing OAuth2 authorization-code issue and token exchange through `WebApplicationServer`.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    RequestValidator,
    WebApplicationServer,
)
```

## Required API Details

- `WebApplicationServer(request_validator, token_generator=None, token_expires_in=None, refresh_token_generator=None, **kwargs)` class constructor
  - `WebApplicationServer.__init__(self, request_validator, token_generator=None, token_expires_in=None, refresh_token_generator=None, **kwargs)`
  - `WebApplicationServer.create_authorization_response(self, uri, http_method='GET', body=None, headers=None, scopes=None, credentials=None)`
  - `WebApplicationServer.create_token_response(self, uri, http_method='POST', body=None, headers=None, credentials=None, grant_type_for_scope=None, claims=None)`
- `RequestValidator()` class constructor

## Required Behavior

- Given a validator that accepts client `cid` and redirect `https://example.com/cb`, `create_authorization_response` for `response_type=code` returns HTTP 302 with a `code` query parameter on `Location`.
- Exchanging that authorization code with `grant_type=authorization_code` via `create_token_response` returns HTTP 200 and a body containing `access_token`.
- A token request whose `grant_type` is not `authorization_code` is rejected with HTTP 400 and `unsupported_grant_type` in the body.
- A token request with an unknown or already-exchanged authorization code is rejected with HTTP 400.
- The package exposes `WebApplicationServer` and `RequestValidator` with authorization and token response methods listed in this contract.
- The submitted package source does not import the forbidden upstream package `oauthlib`.

## Constraints

- Forbidden imports: `oauthlib`.
- Do not implement JWT/OIDC extras.
- Do not implement live HTTP clients.
- Do not implement runtime import of oauthlib.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — Given a validator that accepts client `cid` and redirect `https://example.com/cb`, `create_authorization_response` for `response_type=code` returns HTTP 302 with a `code` query parameter on `Location`.
- **B002** — Exchanging that authorization code with `grant_type=authorization_code` via `create_token_response` returns HTTP 200 and a body containing `access_token`.
- **B003** — A token request whose `grant_type` is not `authorization_code` is rejected with HTTP 400 and `unsupported_grant_type` in the body.
- **B004** — A token request with an unknown or already-exchanged authorization code is rejected with HTTP 400.
- **B005** — The package exposes `WebApplicationServer` and `RequestValidator` with authorization and token response methods listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `oauthlib`.
<!-- featureliftbench:behavior-clauses:end -->

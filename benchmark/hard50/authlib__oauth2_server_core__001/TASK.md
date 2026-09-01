# FeatureLift Task: OAuth2 authorization-code grants

Build a standalone `featurelifted` package providing an in-memory OAuth2 authorization-code server: authorize, exchange a code for a token, and reject unknown clients, without live HTTP.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    AuthorizationCodeGrant,
    AuthorizationServer,
    ClientMixin,
    InvalidClientError,
    OAuth2Request,
)
```

## Required API Details

- `AuthorizationServer(scopes_supported=None)` class constructor
  - `AuthorizationServer.register_grant(self, grant_cls, extensions=None)`
  - `AuthorizationServer.create_authorization_response(self, request=None, grant_user=None)`
  - `AuthorizationServer.create_token_response(self, request=None)`
- `AuthorizationCodeGrant(request, server)` class constructor
- `ClientMixin()` class constructor
- `InvalidClientError` must be importable and raisable
- `OAuth2Request(method, uri, body=None, headers=None)` class constructor
  - `OAuth2Request.__init__(self, method, uri, body=None, headers=None)`

## Required Behavior

- `create_authorization_response` for a registered client's `response_type=code` request returns HTTP 302 whose Location keeps `state` and includes an authorization `code` query parameter.
- `create_token_response` for that code with `grant_type=authorization_code` and `client_secret_post` credentials returns HTTP 200 with an `access_token`, and the server `save_token` hook records the issued token.
- An authorization request whose `client_id` is unknown yields HTTP 400 whose body reports `error` equal to `invalid_client`.
- All grant traffic uses in-memory request tuples and `https://` URIs; the tests never open a listening HTTP server.
- The package exposes `AuthorizationServer`, `AuthorizationCodeGrant`, `ClientMixin`, `InvalidClientError`, and `OAuth2Request` as listed in this contract.
- The submitted package source does not import the forbidden upstream package `authlib`.

## Constraints

- Forbidden imports: `authlib`.
- Do not implement Flask or Django application integrations.
- Do not implement JWK cloud KMS.
- Do not implement listening HTTP servers.
- Do not implement runtime import of authlib.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — `create_authorization_response` for a registered client's `response_type=code` request returns HTTP 302 whose Location keeps `state` and includes an authorization `code` query parameter.
- **B002** — `create_token_response` for that code with `grant_type=authorization_code` and `client_secret_post` credentials returns HTTP 200 with an `access_token`, and the server `save_token` hook records the issued token.
- **B003** — An authorization request whose `client_id` is unknown yields HTTP 400 whose body reports `error` equal to `invalid_client`.
- **B004** — All grant traffic uses in-memory request tuples and `https://` URIs; the tests never open a listening HTTP server.
- **B005** — The package exposes `AuthorizationServer`, `AuthorizationCodeGrant`, `ClientMixin`, `InvalidClientError`, and `OAuth2Request` as listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `authlib`.
<!-- featureliftbench:behavior-clauses:end -->

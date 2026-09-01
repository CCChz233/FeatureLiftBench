# FeatureLift Task: WSGI Request and Response

Build a standalone `featurelifted` package providing WebOb-style `Request` and `Response` over an in-memory WSGI environ, including `Request.blank`, case-insensitive headers, form POST, and JSON response bodies. Do not open network sockets or use an HTTP client.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    Request,
    Response,
)
```

## Required API Details

- `Request(environ, charset=None, unicode_errors=None, decode_param_names=None, **kw)` class constructor
  - `Request.blank(cls, path, environ=None, base_url=None, headers=None, POST=None, **kw)`
- `Response(body=None, status=None, headerlist=None, app_iter=None, content_type=None, conditional_response=None, charset=..., **kw)` class constructor

## Required Behavior

- After `Request.blank("/search?q=lift")`, `method` is GET, `path_info` is `/search`, and `GET["q"]` is `lift`.
- Headers passed to `Request.blank` are readable case-insensitively (`headers["X-Trace"]` and `headers["x-trace"]` return the same value) and appear as `HTTP_X_TRACE` on `environ`.
- `Request.blank("/", POST={"name": "ada"})` yields method POST and `POST["name"] == "ada"`; the body contains the urlencoded field.
- `Response(json={"ok": True})` has status 200, content type `application/json`, `json_body == {"ok": True}`, and compact UTF-8 body. A `status=404` JSON response reports `status_code == 404`.
- The package exposes `Request`, classmethod `Request.blank`, and `Response` as listed in this contract.
- The submitted package source does not import the forbidden upstream package `webob`.

## Constraints

- Forbidden imports: `webob`.
- Do not implement webob.client SendRequest.
- Do not implement live sockets.
- Do not implement Pyramid.
- Do not implement runtime import of webob.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — After `Request.blank("/search?q=lift")`, `method` is GET, `path_info` is `/search`, and `GET["q"]` is `lift`.
- **B002** — Headers passed to `Request.blank` are readable case-insensitively (`headers["X-Trace"]` and `headers["x-trace"]` return the same value) and appear as `HTTP_X_TRACE` on `environ`.
- **B003** — `Request.blank("/", POST={"name": "ada"})` yields method POST and `POST["name"] == "ada"`; the body contains the urlencoded field.
- **B004** — `Response(json={"ok": True})` has status 200, content type `application/json`, `json_body == {"ok": True}`, and compact UTF-8 body. A `status=404` JSON response reports `status_code == 404`.
- **B005** — The package exposes `Request`, classmethod `Request.blank`, and `Response` as listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `webob`.
<!-- featureliftbench:behavior-clauses:end -->

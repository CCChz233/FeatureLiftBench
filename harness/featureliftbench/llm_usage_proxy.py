"""Local OpenAI-compatible usage audit proxy for OpenHands runs."""

from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit
from urllib.parse import urlunsplit

from .openhands_usage import CONTEXT_WINDOW_TOKENS
from .openhands_usage import MAX_ALLOWED_PROMPT_TOKENS
from .openhands_usage import RESERVED_OUTPUT_TOKENS


PROXY_DISABLE_ENV = "FEATURELIFTBENCH_OPENHANDS_USAGE_PROXY"


@dataclass(frozen=True)
class LLMUsageProxyConfig:
    target_base_url: str
    api_key: str
    audit_path: Path
    usage_path: Path
    model: str = ""


class LLMUsageProxy:
    """Forward OpenAI-compatible requests while auditing provider usage fields."""

    def __init__(self, config: LLMUsageProxyConfig) -> None:
        self.config = config
        self._server: _ProxyServer | None = None
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._api_calls = 0
        self._prompt_tokens = 0
        self._completion_tokens = 0
        self._max_prompt_tokens_per_call = 0
        self._max_total_tokens_per_call = 0
        self._saw_verified_usage = False
        self._context_violation = False

    @property
    def base_url(self) -> str:
        if self._server is None:
            raise RuntimeError("proxy has not been started")
        host, port = self._server.server_address
        return f"http://{host}:{port}/v1"

    def start(self) -> "LLMUsageProxy":
        self.config.audit_path.parent.mkdir(parents=True, exist_ok=True)
        self.config.usage_path.parent.mkdir(parents=True, exist_ok=True)
        self._server = _ProxyServer(("127.0.0.1", 0), _ProxyHandler, self)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        return self

    def close(self) -> None:
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
        if self._thread is not None:
            self._thread.join(timeout=2)
            self._thread = None
        self.write_usage_summary()

    def __enter__(self) -> "LLMUsageProxy":
        return self.start()

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def forward(self, handler: BaseHTTPRequestHandler) -> None:
        content_length = _safe_int(handler.headers.get("Content-Length"))
        body = handler.rfile.read(content_length if content_length is not None else 0)
        request_payload = _json_object(body)
        target_url = self._target_url(handler.path)
        request = urllib.request.Request(
            target_url,
            data=body,
            headers=self._forward_headers(handler),
            method=handler.command,
        )
        status = 502
        response_headers: dict[str, str] = {"Content-Type": "application/json"}
        response_body = json.dumps(
            {"error": {"message": "proxy forwarding failed"}},
            sort_keys=True,
        ).encode("utf-8")
        try:
            with urllib.request.urlopen(request, timeout=600) as response:
                status = int(response.status)
                response_body = response.read()
                response_headers = _response_headers(response.headers)
        except urllib.error.HTTPError as exc:
            status = int(exc.code)
            response_body = exc.read()
            response_headers = _response_headers(exc.headers)
        except urllib.error.URLError as exc:
            response_body = json.dumps(
                {"error": {"message": str(exc.reason)}},
                sort_keys=True,
            ).encode("utf-8")

        self._record_call(
            path=handler.path,
            target_url=target_url,
            status=status,
            request_payload=request_payload,
            response_body=response_body,
        )
        handler.send_response(status)
        for key, value in response_headers.items():
            if key.lower() in {"connection", "content-length", "transfer-encoding"}:
                continue
            handler.send_header(key, value)
        handler.send_header("Content-Length", str(len(response_body)))
        handler.end_headers()
        handler.wfile.write(response_body)

    def write_usage_summary(self) -> None:
        with self._lock:
            api_calls = self._api_calls
            if api_calls <= 0:
                return
            prompt_tokens = self._prompt_tokens
            completion_tokens = self._completion_tokens
            max_prompt = self._max_prompt_tokens_per_call
            max_total = self._max_total_tokens_per_call
            saw_verified = self._saw_verified_usage
            context_violation = self._context_violation

        token_source = "openhands_proxy" if saw_verified else "openhands_proxy_no_provider_usage"
        usage = {
            "assistant_steps": 0,
            "api_calls": api_calls,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "context_audit": {
                "available": saw_verified,
                "runtime": "openhands",
                "history_policy": "external_openhands",
                "token_source": token_source,
                "usage_unverified": not saw_verified,
                "context_window_tokens": CONTEXT_WINDOW_TOKENS,
                "reserved_output_tokens": RESERVED_OUTPUT_TOKENS,
                "max_allowed_prompt_tokens": MAX_ALLOWED_PROMPT_TOKENS,
                "max_prompt_tokens_per_call": max_prompt,
                "max_total_tokens_per_call": max_total,
                "context_violation": context_violation,
                "over_context_behavior": "audited_by_featureliftbench_proxy",
            },
        }
        self.config.usage_path.write_text(
            json.dumps(usage, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def _target_url(self, request_path: str) -> str:
        base = self.config.target_base_url.rstrip("/")
        parsed = urlsplit(base)
        base_path = parsed.path.rstrip("/")
        path = request_path
        if base_path.endswith("/v1") and path.startswith("/v1/"):
            path = path[len("/v1") :]
        if not path.startswith("/"):
            path = "/" + path
        return urlunsplit((parsed.scheme, parsed.netloc, base_path + path, "", ""))

    def _forward_headers(self, handler: BaseHTTPRequestHandler) -> dict[str, str]:
        headers: dict[str, str] = {}
        for key, value in handler.headers.items():
            if key.lower() in {"host", "content-length", "connection", "authorization"}:
                continue
            headers[key] = value
        headers.setdefault("Content-Type", "application/json")
        headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers

    def _record_call(
        self,
        *,
        path: str,
        target_url: str,
        status: int,
        request_payload: dict[str, Any] | None,
        response_body: bytes,
    ) -> None:
        response_payload = _json_object(response_body)
        usage = response_payload.get("usage") if isinstance(response_payload, dict) else None
        usage = usage if isinstance(usage, dict) else {}
        prompt = _int_metric(usage.get("prompt_tokens"))
        completion = _int_metric(usage.get("completion_tokens"))
        total = _int_metric(usage.get("total_tokens"))
        if total is None and (prompt is not None or completion is not None):
            total = (prompt or 0) + (completion or 0)
        model = ""
        if isinstance(request_payload, dict) and isinstance(request_payload.get("model"), str):
            model = request_payload["model"]
        elif self.config.model:
            model = self.config.model

        verified = prompt is not None
        prompt_value = prompt or 0
        completion_value = completion or 0
        total_value = total or (prompt_value + completion_value)
        context_violation = verified and prompt_value > MAX_ALLOWED_PROMPT_TOKENS
        record = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "runtime": "openhands",
            "phase": "openhands_proxy",
            "path": path,
            "target_url": _redact_url(target_url),
            "status": status,
            "model": model,
            "usage_verified": verified,
            "prompt_tokens": prompt,
            "completion_tokens": completion,
            "total_tokens": total,
            "context_window_tokens": CONTEXT_WINDOW_TOKENS,
            "max_allowed_prompt_tokens": MAX_ALLOWED_PROMPT_TOKENS,
            "context_violation": context_violation,
        }
        with self._lock:
            self._api_calls += 1
            self._prompt_tokens += prompt_value
            self._completion_tokens += completion_value
            self._max_prompt_tokens_per_call = max(
                self._max_prompt_tokens_per_call,
                prompt_value,
            )
            self._max_total_tokens_per_call = max(
                self._max_total_tokens_per_call,
                total_value,
            )
            self._saw_verified_usage = self._saw_verified_usage or verified
            self._context_violation = self._context_violation or bool(context_violation)
            with self.config.audit_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, sort_keys=True) + "\n")


class _ProxyServer(ThreadingHTTPServer):
    def __init__(
        self,
        server_address: tuple[str, int],
        handler_class: type[BaseHTTPRequestHandler],
        proxy: LLMUsageProxy,
    ) -> None:
        super().__init__(server_address, handler_class)
        self.proxy = proxy


class _ProxyHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_POST(self) -> None:
        server = self.server
        if not isinstance(server, _ProxyServer):
            self.send_error(500)
            return
        server.proxy.forward(self)

    def log_message(self, format: str, *args: object) -> None:
        return


def maybe_start_openhands_usage_proxy(
    env: dict[str, str],
    agent_output_dir: Path,
) -> LLMUsageProxy | None:
    if env.get(PROXY_DISABLE_ENV, "").strip().lower() in {"0", "false", "no", "off"}:
        return None
    target_base_url = _first_non_empty(
        env.get("FEATURELIFTBENCH_API_BASE"),
        env.get("OPENAI_BASE_URL"),
        env.get("OPENAI_API_BASE"),
        env.get("LLM_BASE_URL"),
        env.get("DEEPSEEK_API_BASE"),
    )
    api_key = _first_non_empty(
        env.get("FEATURELIFTBENCH_API_KEY"),
        env.get("OPENAI_API_KEY"),
        env.get("LLM_API_KEY"),
        env.get("DEEPSEEK_API_KEY"),
    )
    if not target_base_url or not api_key:
        return None
    return LLMUsageProxy(
        LLMUsageProxyConfig(
            target_base_url=target_base_url,
            api_key=api_key,
            audit_path=agent_output_dir / "context_audit.jsonl",
            usage_path=agent_output_dir / "openhands_usage.json",
            model=env.get("LLM_MODEL") or env.get("FEATURELIFTBENCH_MODEL", ""),
        )
    )


def _response_headers(headers: Any) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, value in headers.items():
        if isinstance(key, str) and isinstance(value, str):
            result[key] = value
    return result


def _json_object(data: bytes) -> dict[str, Any] | None:
    try:
        payload = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _safe_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        parsed = int(value)
    except ValueError:
        return None
    return parsed if parsed >= 0 else None


def _int_metric(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value >= 0 else None
    if isinstance(value, float) and value >= 0 and value.is_integer():
        return int(value)
    if isinstance(value, str):
        try:
            parsed = int(value.strip())
        except ValueError:
            return None
        return parsed if parsed >= 0 else None
    return None


def _first_non_empty(*values: str | None) -> str:
    for value in values:
        if value:
            return value
    return ""


def _redact_url(url: str) -> str:
    parsed = urlsplit(url)
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))

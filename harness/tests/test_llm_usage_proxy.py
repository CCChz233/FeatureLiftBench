from __future__ import annotations

import json
import tempfile
import threading
import unittest
import urllib.request
from http.server import BaseHTTPRequestHandler
from http.server import ThreadingHTTPServer
from pathlib import Path

from featureliftbench.llm_usage_proxy import LLMUsageProxy
from featureliftbench.llm_usage_proxy import LLMUsageProxyConfig


class LLMUsageProxyTests(unittest.TestCase):
    def test_proxy_forwards_request_and_records_provider_usage(self) -> None:
        try:
            upstream = _FakeUpstreamServer()
        except PermissionError as exc:
            self.skipTest(f"local loopback sockets are unavailable: {exc}")
        upstream.start()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                proxy = LLMUsageProxy(
                    LLMUsageProxyConfig(
                        target_base_url=upstream.base_url + "/v1",
                        api_key="sk-real",
                        audit_path=root / "context_audit.jsonl",
                        usage_path=root / "openhands_usage.json",
                        model="deepseek-v4-flash",
                    )
                ).start()
                try:
                    body = json.dumps(
                        {
                            "model": "deepseek-v4-flash",
                            "messages": [{"role": "user", "content": "hello"}],
                        }
                    ).encode("utf-8")
                    request = urllib.request.Request(
                        proxy.base_url + "/chat/completions",
                        data=body,
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": "Bearer proxy-key",
                        },
                        method="POST",
                    )
                    with urllib.request.urlopen(request, timeout=10) as response:
                        payload = json.loads(response.read().decode("utf-8"))
                finally:
                    proxy.close()

                audit_records = [
                    json.loads(line)
                    for line in (root / "context_audit.jsonl").read_text(encoding="utf-8").splitlines()
                ]
                usage = json.loads((root / "openhands_usage.json").read_text(encoding="utf-8"))

            self.assertEqual(payload["usage"]["prompt_tokens"], 123)
            self.assertEqual(upstream.last_path, "/v1/chat/completions")
            self.assertEqual(upstream.last_authorization, "Bearer sk-real")
            self.assertEqual(len(audit_records), 1)
            self.assertTrue(audit_records[0]["usage_verified"])
            self.assertEqual(usage["api_calls"], 1)
            self.assertEqual(usage["prompt_tokens"], 123)
            self.assertEqual(usage["completion_tokens"], 45)
            self.assertFalse(usage["context_audit"]["usage_unverified"])
            self.assertEqual(usage["context_audit"]["token_source"], "openhands_proxy")
        finally:
            upstream.close()


class _FakeUpstreamServer:
    def __init__(self) -> None:
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), _FakeUpstreamHandler)
        self.server.owner = self  # type: ignore[attr-defined]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.last_path = ""
        self.last_authorization = ""

    @property
    def base_url(self) -> str:
        host, port = self.server.server_address
        return f"http://{host}:{port}"

    def start(self) -> None:
        self.thread.start()

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)


class _FakeUpstreamHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_POST(self) -> None:
        owner = self.server.owner  # type: ignore[attr-defined]
        owner.last_path = self.path
        owner.last_authorization = self.headers.get("Authorization", "")
        length = int(self.headers.get("Content-Length", "0"))
        self.rfile.read(length)
        body = json.dumps(
            {
                "id": "chatcmpl-test",
                "choices": [{"message": {"content": "ok"}}],
                "usage": {
                    "prompt_tokens": 123,
                    "completion_tokens": 45,
                    "total_tokens": 168,
                },
            }
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


if __name__ == "__main__":
    unittest.main()

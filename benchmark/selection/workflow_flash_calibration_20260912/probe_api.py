"""Probe only the user-authorized DeepSeek endpoint; never log credentials."""
from datetime import datetime, timezone
import json
from pathlib import Path
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[3]


def main():
    values = dict(line.split("=", 1) for line in (ROOT / ".env.workflow-hard-flash.local").read_text().splitlines() if line and not line.startswith("#"))
    key = values["FEATURELIFTBENCH_API_KEY"].strip()
    base = values["FEATURELIFTBENCH_API_BASE"].rstrip("/")
    if base != "https://api.deepseek.com":
        raise ValueError("Unexpected API destination")
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    client = urllib.request.build_opener(NoRedirect)
    report = dict(endpoint=base, requested_model="deepseek-flash", checks=[], benchmark_started=False)
    def request(path, payload=None):
        data = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(base + path, data=data, headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
        try:
            with client.open(req, timeout=30) as response:
                body = json.load(response)
                status = response.status
        except urllib.error.HTTPError as exc:
            body = json.loads(exc.read().decode("utf-8", errors="replace").replace(key, "[REDACTED]"))
            status = exc.code
        except (urllib.error.URLError, OSError) as exc:
            report["checks"].append(dict(path=path, status="connection_error", error=str(exc).replace(key, "[REDACTED]")))
            return None
        if status != 200:
            report["checks"].append(dict(path=path, status=status, error=body.get("error", {})))
            return None
        report["checks"].append(dict(path=path, status=status))
        return body
    models = request("/models")
    if models is not None:
        report["models"] = [m["id"] for m in models.get("data", [])]
        completion = request("/chat/completions", dict(model="deepseek-flash", messages=[dict(role="user", content="Reply with OK only.")], max_tokens=16, thinking=dict(type="disabled")))
        if completion is not None:
            report.update(returned_model=completion.get("model"), usage=completion.get("usage"), completion_received=bool(completion.get("choices")))
    output = ROOT / "experiments/calibration/workflow_flash_api" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output.mkdir(parents=True, exist_ok=False)
    path = output / "preflight.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))
    print(path)
    return 0 if report.get("completion_received") else 1


if __name__ == "__main__":
    raise SystemExit(main())

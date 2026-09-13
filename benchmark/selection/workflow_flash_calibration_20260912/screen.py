"""Exploratory Flash source-reading agent. NOT the OpenHands Main runtime.

This process performs API calls and brokered file I/O only. It never executes
model code. Evaluation is a separate invocation without API credentials.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import argparse
import fnmatch
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
IDS = ["pip__offline_distribution_selection__workflow_001", "dbt_core__offline_graph_selection__workflow_001"]


def tool(name, description, properties, required):
    return dict(type="function", function=dict(name=name, description=description, parameters=dict(type="object", properties=properties, required=required)))


S = {"type": "string"}
I = {"type": "integer"}
TOOLS = [
    tool("list_files", "List complete upstream repository files matching a glob; use offset to paginate. Source paths begin repo/.", dict(glob=S, offset=I), []),
    tool("read_file", "Read UTF-8 source or submitted text, numbered from 1, up to 400 lines per call.", dict(path=S, start=I, count=I), ["path"]),
    tool("search", "Literal text search over full upstream repository files matching a glob. Up to 50 matching lines; use offset to paginate.", dict(query=S, glob=S, offset=I), ["query"]),
    tool("write_file", "Create or replace a UTF-8 submission file. Paths must begin featurelifted/. Code is not executed by this tool.", dict(path=S, content=S), ["path", "content"]),
    tool("copy_source", "Copy an upstream text file into featurelifted/, optionally applying literal replacements in order. Source remains unchanged.", dict(source=S, destination=S, replacements={"type": "array", "items": {"type": "object", "properties": {"old": S, "new": S}, "required": ["old", "new"]}}), ["source", "destination"]),
]


class Broker:
    def __init__(self, snapshot, submission):
        archive = ROOT / snapshot["archive_path"]
        if hashlib.sha256(archive.read_bytes()).hexdigest() != snapshot["archive_sha256"]:
            raise ValueError("Source archive digest mismatch")
        self.source = {}
        with tarfile.open(archive, "r:gz") as tf:
            for member in tf.getmembers():
                if member.isfile():
                    self.source["repo/" + member.name] = tf.extractfile(member).read()
                elif member.issym():
                    self.source["repo/" + member.name] = ("SYMLINK -> " + member.linkname).encode()
        self.submission = submission
        submission.mkdir(parents=True)

    def destination(self, path):
        name = PurePosixPath(path)
        if name.is_absolute() or not name.parts or name.parts[0] != "featurelifted" or len(name.parts) < 2 or ".." in name.parts or "\\" in path or ":" in path:
            raise ValueError("Only relative featurelifted/ paths are writable")
        target = self.submission.joinpath(*name.parts)
        if not target.resolve().is_relative_to(self.submission.resolve()):
            raise ValueError("Path escaped submission")
        return target

    def read(self, path):
        if path.startswith("repo/"):
            return self.source[path].decode("utf-8", errors="replace")
        return self.destination(path).read_text(encoding="utf-8")

    def invoke(self, name, args):
        if name == "list_files":
            paths = sorted(p for p in self.source if fnmatch.fnmatchcase(p, args.get("glob", "repo/*")))
            offset = max(0, int(args.get("offset", 0)))
            return dict(total=len(paths), paths=paths[offset:offset + 200], next_offset=offset + 200 if offset + 200 < len(paths) else None)
        if name == "read_file":
            lines = self.read(args["path"]).splitlines()
            start = max(1, int(args.get("start", 1)))
            count = min(400, max(1, int(args.get("count", 250))))
            return dict(total_lines=len(lines), lines="\n".join(f"{i + 1}: {lines[i]}" for i in range(start - 1, min(len(lines), start - 1 + count))))
        if name == "search":
            found = []
            query = args["query"]
            if not query:
                raise ValueError("Search query cannot be empty")
            for path in sorted(self.source):
                if fnmatch.fnmatchcase(path, args.get("glob", "repo/*.py")):
                    for i, line in enumerate(self.read(path).splitlines(), 1):
                        if query in line:
                            found.append(dict(path=path, line=i, text=line[:1200]))
            offset = max(0, int(args.get("offset", 0)))
            return dict(total=len(found), matches=found[offset:offset + 50], next_offset=offset + 50 if offset + 50 < len(found) else None)
        if name in {"write_file", "copy_source"}:
            path = args["path"] if name == "write_file" else args["destination"]
            text = args["content"] if name == "write_file" else self.read(args["source"])
            if name == "copy_source":
                for replacement in args.get("replacements", []):
                    if not replacement["old"]:
                        raise ValueError("Empty replacement is not supported")
                    text = text.replace(replacement["old"], replacement["new"])
            if len(text.encode()) > 2_000_000:
                raise ValueError("Submission file exceeds 2MB")
            target = self.destination(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
            return dict(written=path, chars=len(text))
        raise ValueError("Unknown tool")


def run(task_id, snapshot, output, key, args):
    folder = output / task_id
    folder.mkdir()
    broker = Broker(snapshot, folder / "submission")
    task = ROOT / "benchmark/staging" / task_id
    public = (task / "TASK.md").read_text(encoding="utf-8")
    messages = [dict(role="system", content="You are implementing an offline feature extraction task from a complete pinned upstream repository. The user contract is authoritative. Inspect the source using tools, preserve its relevant behavior, and write a standalone featurelifted package. The repository is read-only. Only declared support dependencies may be imported. No benchmark tests, reference solution, source entrypoint hints, or credentials are available. Tools provide source listing, literal search, reading, copying and writing; no shell, interpreter, or execution feedback is available in this exploratory runtime. Use static reasoning to verify imports and behavior. Do not merely describe a solution: write all required files. Finish with a short final message after writing the package."), dict(role="user", content=public)]
    messages[0]["content"] += f" Budget: at most {args.max_steps} API rounds and {args.token_budget} cumulative API tokens, including repeated cached input. Tool results report usage and remaining budget. Prioritize writing a complete working submission before spending the budget on exhaustive source reading. Single-response allowance is {args.max_output_tokens} tokens, including reasoning."
    report = dict(task_id=task_id, protocol="exploratory-source-tools-no-execution-v2", model="deepseek-flash", thinking="enabled", official_main=False, source_context="full_repository", source_archive_sha256=snapshot["archive_sha256"], task_sha256=hashlib.sha256(public.encode()).hexdigest(), source_hints=False, evaluator_tests_visible=False, max_steps=args.max_steps, cumulative_token_budget=args.token_budget, per_response_max_tokens=args.max_output_tokens, timeout_seconds=1800, usage=dict(prompt_tokens=0, completion_tokens=0, total_tokens=0), steps=[], status="running")
    start = time.monotonic()
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    client = urllib.request.build_opener(NoRedirect)
    def save():
        report["elapsed_seconds"] = round(time.monotonic() - start, 2)
        (folder / "run.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        (folder / "trajectory.json").write_text(json.dumps(messages, ensure_ascii=False), encoding="utf-8")
    save()
    try:
        for step in range(1, args.max_steps + 1):
            if time.monotonic() - start > 1800:
                report["status"] = "time_budget_exhausted"
                break
            # Conservative bound uses UTF-8 byte count as an input token ceiling.
            envelope = len(json.dumps(messages, ensure_ascii=False).encode()) + len(json.dumps(TOOLS).encode())
            if report["usage"]["total_tokens"] + envelope + args.max_output_tokens > args.token_budget:
                report["status"] = "token_budget_exhausted"
                break
            payload = dict(model="deepseek-flash", messages=messages, tools=TOOLS, max_tokens=args.max_output_tokens, thinking=dict(type="enabled"))
            request = urllib.request.Request("https://api.deepseek.com/chat/completions", data=json.dumps(payload).encode(), headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
            with client.open(request, timeout=180) as response:
                body = json.load(response)
            for field in report["usage"]:
                report["usage"][field] += body.get("usage", {}).get(field, 0)
            report["returned_model"] = body.get("model")
            report["system_fingerprint"] = body.get("system_fingerprint")
            choice = body["choices"][0]
            raw = choice["message"]
            message = {k: raw[k] for k in ("role", "content", "reasoning_content", "tool_calls") if k in raw and raw[k] is not None}
            messages.append(message)
            calls = raw.get("tool_calls") or []
            record = dict(step=step, finish_reason=choice.get("finish_reason"), tool_names=[c["function"]["name"] for c in calls], usage=body.get("usage", {}))
            report["steps"].append(record)
            for call in calls:
                try:
                    result = broker.invoke(call["function"]["name"], json.loads(call["function"]["arguments"]))
                except Exception as exc:
                    result = dict(tool_error=str(exc))
                result["_runtime_budget"] = dict(cumulative_tokens_used=report["usage"]["total_tokens"], tokens_remaining=args.token_budget - report["usage"]["total_tokens"], rounds_remaining=args.max_steps - step, note="Repeated context input consumes this budget; write a complete submission before it is exhausted.")
                messages.append(dict(role="tool", tool_call_id=call["id"], content=json.dumps(result, ensure_ascii=False)))
            save()
            print(json.dumps(dict(task_id=task_id, step=step, tools=record["tool_names"], total_tokens=report["usage"]["total_tokens"])), flush=True)
            if not calls:
                if choice.get("finish_reason") == "length":
                    messages.append(dict(role="user", content="Your last response reached the per-response token limit. Continue and use write_file/copy_source to complete the submission within the remaining overall budget."))
                    continue
                report["status"] = "submitted" if choice.get("finish_reason") == "stop" else "output_truncated"
                break
        else:
            report["status"] = "step_budget_exhausted"
    except Exception as exc:
        report["status"] = "infrastructure_error"
        report["error"] = str(exc).replace(key, "[REDACTED]")
        if isinstance(exc, urllib.error.HTTPError):
            report["api_error"] = exc.read().decode(errors="replace").replace(key, "[REDACTED]")[:2000]
    report["submission_files"] = [p.relative_to(folder / "submission").as_posix() for p in (folder / "submission").rglob("*") if p.is_file()]
    save()
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-steps", type=int, default=120)
    parser.add_argument("--token-budget", type=int, default=2_000_000)
    parser.add_argument("--max-output-tokens", type=int, default=32768)
    args = parser.parse_args()
    values = dict(line.split("=", 1) for line in (ROOT / ".env.workflow-hard-flash.local").read_text().splitlines() if line and not line.startswith("#"))
    if values["FEATURELIFTBENCH_API_BASE"].strip().rstrip("/") != "https://api.deepseek.com":
        raise ValueError("Unexpected API destination")
    registry = json.loads((ROOT / "benchmark/sources/workflow_hard_pilot_registry.json").read_text(encoding="utf-8"))
    snapshots = {task: snapshot for snapshot in registry["snapshots"] for task in snapshot["task_ids"]}
    output = ROOT / "experiments/calibration/workflow_flash_screen" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output.mkdir(parents=True)
    (output / "runtime_source.py").write_bytes(Path(__file__).read_bytes())
    print(output, flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(run, task, snapshots[task], output, values["FEATURELIFTBENCH_API_KEY"].strip(), args) for task in IDS]
        results = [f.result() for f in futures]
    (output / "generation_summary.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps([dict(task_id=r["task_id"], status=r["status"], usage=r["usage"], files=len(r["submission_files"])) for r in results]), flush=True)


if __name__ == "__main__":
    main()

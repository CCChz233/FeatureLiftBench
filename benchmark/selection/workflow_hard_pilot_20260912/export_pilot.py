"""Create a maintainer-only, checksummed server overlay without reading repo trees."""
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import tarfile
from definitions import TASKS

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TASK_PARTS = ("TASK.md", "metadata.json", "requirements.lock", "public_tests", "hidden_tests", "evaluation", "reference_solution")


def files_under(path):
    paths = [path] if path.is_file() else sorted(path.rglob("*"))
    return [p for p in paths if p.is_file() and not any(x in {"__pycache__", ".pytest_cache"} for x in p.parts) and p.suffix not in {".pyc", ".pyo"}]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", required=True, type=Path)
    args = parser.parse_args()
    evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    if not evidence["development_reference_pass"]:
        raise ValueError("All development reference gates must pass before export")
    files = [p for p in files_under(HERE) if p.name != "INPUT_LOCK.json"]
    for definition in TASKS:
        task = ROOT / "benchmark/staging" / definition["task_id"]
        for part in TASK_PARTS:
            files += files_under(task / part)
    registry_path = ROOT / "benchmark/sources/workflow_hard_pilot_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    files.append(registry_path)
    files += [ROOT / s["archive_path"] for s in registry["snapshots"]]
    evidence_root = args.evidence.resolve().parent
    files.append(args.evidence.resolve())
    files += sorted(evidence_root.rglob("*.log"))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = ROOT / "exports/server-overlays" / ("workflow-hard-pilot-" + stamp + ".tar.gz")
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest = dict(schema="workflow_hard_pilot.input_lock.v1", created_at=stamp, phase="pre-calibration", main_freeze=False, task_ids=[d["task_id"] for d in TASKS], hard_candidates=[d["task_id"] for d in TASKS if d["source"] != "sqlglot"], controls=[d["task_id"] for d in TASKS if d["source"] == "sqlglot"], local_evidence=args.evidence.resolve().relative_to(ROOT).as_posix(), files={})
    with tarfile.open(output, "x:gz") as tf:
        for path in sorted(set(files)):
            relative = path.relative_to(ROOT).as_posix()
            content = path.read_bytes()
            manifest["files"][relative] = hashlib.sha256(content).hexdigest()
            info = tarfile.TarInfo(relative)
            info.size, info.mode, info.mtime = len(content), 0o644, 0
            tf.addfile(info, io.BytesIO(content))
        payload = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
        lock_name = HERE.relative_to(ROOT).as_posix() + "/INPUT_LOCK.json"
        info = tarfile.TarInfo(lock_name)
        info.size, info.mode, info.mtime = len(payload), 0o644, 0
        tf.addfile(info, io.BytesIO(payload))
    # The lock is a release-specific sidecar, never self-hashed or overwritten.
    lock_path = output.with_suffix("").with_suffix(".inputs.json")
    lock_path.write_bytes(payload)
    sha = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(output.suffix + ".sha256").write_text(sha + "  " + output.name + "\n", encoding="utf-8")
    print(json.dumps(dict(overlay=str(output), input_lock=str(lock_path), sha256=sha, file_count=len(manifest["files"]), bytes=output.stat().st_size)))


if __name__ == "__main__":
    main()

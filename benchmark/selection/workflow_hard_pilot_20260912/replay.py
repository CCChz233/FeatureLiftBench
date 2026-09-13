"""Windows-compatible development checks; does not substitute for Docker Main."""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "harness"))
from featureliftbench.validate import validate_task
from definitions import TASKS

BOOTSTRAP = '''import builtins, importlib.abc, io, json, os, pathlib, socket, sys
submission, tests, forbidden_json, project = sys.argv[1:]
forbidden = set(json.loads(forbidden_json))
class DenyUpstream(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in forbidden:
            raise ImportError("Forbidden upstream import: " + fullname)
sys.meta_path.insert(0, DenyUpstream())
def deny_network(*args, **kwargs): raise RuntimeError("network disabled in development replay")
socket.socket.connect = deny_network
socket.socket.connect_ex = deny_network
socket.create_connection = deny_network
original_open = builtins.open
original_io_open = io.open
def checked(function, file, *args, **kwargs):
    if isinstance(file, (str, bytes, os.PathLike)):
        path = pathlib.Path(os.fsdecode(file)).resolve()
        source = pathlib.Path(project) / "benchmark" / "sources"
        staging = pathlib.Path(project) / "benchmark" / "staging"
        if path.is_relative_to(source) or path.is_relative_to(staging):
            raise PermissionError("Source/reference access forbidden: " + str(path))
    return function(file, *args, **kwargs)
builtins.open = lambda file, *a, **kw: checked(original_open, file, *a, **kw)
io.open = lambda file, *a, **kw: checked(original_io_open, file, *a, **kw)
sys.path.insert(0, submission)
import featurelifted
assert pathlib.Path(featurelifted.__file__).resolve().is_relative_to(pathlib.Path(submission).resolve())
import pytest
raise SystemExit(pytest.main([tests, "-q", "--import-mode=importlib", "-p", "no:cacheprovider"]))
'''


def verify_archive(snapshot):
    path = ROOT / snapshot["archive_path"]
    if hashlib.sha256(path.read_bytes()).hexdigest() != snapshot["archive_sha256"]:
        return False
    digest = hashlib.sha256()
    with tarfile.open(path, "r:gz") as tf:
        for member in sorted((m for m in tf.getmembers() if not m.isdir()), key=lambda m: m.name.encode()):
            kind = "symlink" if member.issym() else "file"
            mode = "120000" if member.issym() else "100755" if member.mode & 0o100 else "100644"
            content = member.linkname.encode() if member.issym() else tf.extractfile(member).read()
            record = "\0".join([kind, mode, member.name, str(len(content)), hashlib.sha256(content).hexdigest()]) + "\n"
            digest.update(record.encode())
    return digest.hexdigest() == snapshot["source_tree_sha256"]


def run_submission(task, submission, output, repeats):
    # Only copied submission and tests enter the process working directory.
    destination = output / "submission"
    shutil.copytree(submission, destination, dirs_exist_ok=True)
    metadata = json.loads((task / "metadata.json").read_text())
    forbidden = metadata["environment"]["forbidden_imports"]
    imports = []
    for path in destination.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports += [n.name for n in node.names if n.name.split(".")[0] in forbidden]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module and node.module.split(".")[0] in forbidden:
                imports.append(node.module)
    result = dict(forbidden_static_imports=imports, runs=[])
    env = {**os.environ, "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1", "PYTHONDONTWRITEBYTECODE": "1"}
    for iteration in range(repeats):
        for tier in ["public", "hidden"]:
            tests = output / (tier + "_tests")
            shutil.copytree(task / (tier + "_tests"), tests, dirs_exist_ok=True)
            proc = subprocess.run([sys.executable, "-I", "-B", "-c", BOOTSTRAP, str(destination), str(tests), json.dumps(forbidden), str(ROOT)], cwd=output, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
            log = output / f"{tier}_r{iteration + 1}.log"
            log.write_text(proc.stdout + proc.stderr, encoding="utf-8")
            result["runs"].append(dict(tier=tier, repeat=iteration + 1, returncode=proc.returncode, log=str(log.relative_to(ROOT)), summary=proc.stdout.splitlines()[-1:]))
    result["passed"] = not imports and all(r["returncode"] == 0 for r in result["runs"])
    result["python_loc"] = sum(bool(line.strip()) and not line.strip().startswith("#") for p in destination.rglob("*.py") for line in p.read_text(encoding="utf-8").splitlines())
    result["python_files"] = len(list(destination.rglob("*.py")))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = (args.output or ROOT / "experiments/validation/workflow_hard_pilot" / stamp).resolve()
    if output.exists():
        raise ValueError("Use a fresh output directory; historical runs are never overwritten")
    output.mkdir(parents=True)
    registry = json.loads((ROOT / "benchmark/sources/workflow_hard_pilot_registry.json").read_text())
    import jsonschema
    schema = json.loads((ROOT / "benchmark/sources/registry.schema.json").read_text())
    schema_errors = [error.message for error in jsonschema.Draft202012Validator(schema).iter_errors(registry)]
    report = dict(protocol="local-development-only", docker=False, registry_schema_errors=schema_errors, cli_blocker="Windows CLI imports Unix-only fcntl; direct harness validate_task is used", python=sys.version, source_checks={s["source_snapshot_id"]: verify_archive(s) for s in registry["snapshots"]}, tasks=[])
    for definition in TASKS:
        task = ROOT / "benchmark/staging" / definition["task_id"]
        validation = validate_task(task)
        entry = dict(task_id=task.name, validate_task=dict(valid=validation.valid, errors=validation.errors, warnings=validation.warnings))
        task_out = output / task.name
        task_out.mkdir()
        entry["reference"] = run_submission(task, task / "reference_solution", task_out / "reference", args.repeats)
        entry["baselines"] = {}
        for baseline in sorted((task / "evaluation/baselines").glob("*")):
            if baseline.is_dir():
                entry["baselines"][baseline.name] = run_submission(task, baseline, task_out / baseline.name, 1)
        report["tasks"].append(entry)
        print(json.dumps(entry, ensure_ascii=False))
    report["development_reference_pass"] = not schema_errors and all(report["source_checks"].values()) and all(t["validate_task"]["valid"] and t["reference"]["passed"] for t in report["tasks"])
    report["remaining_gates"] = ["Linux Docker functional/isolation replay", "allowlist-only installation", "fixed-budget strong-agent calibration", "source/closure overlap review", "freeze and promotion"]
    path = output / "summary.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(path)
    return 0 if report["development_reference_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

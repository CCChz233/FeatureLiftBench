"""Evaluate saved submissions separately from the credential-bearing API process."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
PILOT = ROOT / "benchmark/selection/workflow_hard_pilot_20260912"
sys.path.insert(0, str(PILOT))
spec = importlib.util.spec_from_file_location("pilot_replay", PILOT / "replay.py")
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)

AUDIT = '''
pytest_ini = pathlib.Path(tests).parent / 'pytest.ini'
pytest_ini.write_text('[pytest]\\n', encoding='utf-8')
allowed_roots = [pathlib.Path(submission).resolve().parent, pathlib.Path(sys.prefix).resolve(), pathlib.Path(sys.base_prefix).resolve()]
def audit_boundary(event, args):
    if event in {'subprocess.Popen', 'os.system', 'os.posix_spawn', 'socket.connect', 'socket.getaddrinfo', 'ctypes.dlopen'}:
        raise PermissionError('Blocked process/network/native-code operation in development evaluation')
    if event == 'open' and args and isinstance(args[0], (str, bytes, os.PathLike)):
        path = pathlib.Path(os.fsdecode(args[0])).resolve()
        if not any(path.is_relative_to(root) for root in allowed_roots):
            raise PermissionError('File read outside submission/test/runtime allowlist')
sys.addaudithook(audit_boundary)
'''
replay.BOOTSTRAP = replay.BOOTSTRAP.replace("sys.path.insert(0, submission)\nimport featurelifted", AUDIT + "\nsys.path.insert(0, submission)\nimport featurelifted")
replay.BOOTSTRAP = replay.BOOTSTRAP.replace('pytest.main([tests, "-q",', 'pytest.main([tests, "-c", str(pytest_ini), "--rootdir", str(pathlib.Path(tests).parent), "--confcutdir", str(pathlib.Path(tests).parent), "-q",')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("--label", default="evaluation")
    args = parser.parse_args()
    output = args.run.resolve()
    results = []
    for path in sorted(output.glob("*/run.json")):
        run = json.loads(path.read_text(encoding="utf-8"))
        entry = dict(task_id=run["task_id"], generation_status=run["status"], usage=run["usage"], submitted_files=run["submission_files"])
        if not args.label.replace("_", "").isalnum():
            raise ValueError("Use an alphanumeric output label")
        evaluation = path.parent / args.label
        if evaluation.exists():
            raise ValueError("Evaluation already exists; preserve historical output")
        task = ROOT / "benchmark/staging" / run["task_id"]
        # Verify this stricter local boundary with the known correct reference first.
        reference = replay.run_submission(task, task / "reference_solution", evaluation / "reference", 1)
        entry["reference_check"] = reference
        if not reference["passed"]:
            entry["status"] = "evaluation_environment_error"
        elif not run["submission_files"]:
            entry["status"] = "missing_submission"
        else:
            entry["functional"] = replay.run_submission(task, path.parent / "submission", evaluation / "model", 1)
            entry["status"] = "passed" if entry["functional"]["passed"] else "failed"
        results.append(entry)
    report = dict(protocol="exploratory-source-tools-no-execution", official_main=False, docker=False, limitations=["Custom source-reading/file-writing runtime instead of OpenHands", "No interpreter or self-test execution during generation", "Local Python audit boundary is not OS isolation", "Single exploratory attempt per task per runtime revision; not empirical hard certification"], tasks=results)
    (output / (args.label + "_summary.json")).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

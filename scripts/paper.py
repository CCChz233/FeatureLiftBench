"""Paper entrypoint: check saved evidence, update tables, draw figures, or package LaTeX.

No command launches an agent, evaluates a benchmark task, or compiles LaTeX.
Paths are resolved from this file, so commands also work outside the repo root.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "docs/paper"
sys.path.insert(0, str(PAPER))
from paper_inputs import MANIFEST, validate_scope


def run(relative: str, *args: str) -> None:
    subprocess.run([sys.executable, "-B", str(ROOT / relative), *args], cwd=ROOT, check=True)


def check() -> None:
    print(json.dumps(validate_scope(), ensure_ascii=False), flush=True)
    run("docs/paper/writing/update_tables.py", "--check")
    run("docs/paper/writing/update_structure_results.py", "--check")
    print("Paper inputs and generated tables agree; no files changed.", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "tables", "figures", "package"))
    args = parser.parse_args()
    if args.command == "check":
        check()
    elif args.command == "tables":
        validate_scope()
        run("docs/paper/writing/update_tables.py")
        run("docs/paper/writing/update_structure_results.py")
    elif args.command == "figures":
        validate_scope()
        run("docs/paper/figures/scripts/redraw_figures.py")
    else:
        check()
        output = PAPER / "featureliftbench_overleaf.zip"
        # Read all files before replacing the existing upload snapshot.
        payloads = [(name, (PAPER / name).read_bytes()) for name in MANIFEST["paper_files"]]
        with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
            for name, data in payloads:
                archive.writestr(name, data)
        print(f"Packaged {len(payloads)} files: {output}")


if __name__ == "__main__":
    main()

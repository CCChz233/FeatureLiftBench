"""Paper entrypoint: check saved evidence, update tables, draw figures, or package LaTeX.

No command launches an agent or evaluates a benchmark task. Only build compiles LaTeX.
Paths are resolved from this file, so commands also work outside the repo root.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import shutil
import sys
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "docs/paper-workbench"
MANUSCRIPT = ROOT / "docs/paper"
sys.path.insert(0, str(PAPER))
from paper_inputs import MANIFEST, validate_scope, validate_manuscript


def run(relative: str, *args: str) -> None:
    subprocess.run([sys.executable, "-B", str(ROOT / relative), *args], cwd=ROOT, check=True)


def check() -> None:
    print(json.dumps(validate_scope(), ensure_ascii=False), flush=True)
    print(json.dumps(validate_manuscript(), ensure_ascii=False), flush=True)
    if has_generated_main_table():
        run("docs/paper-workbench/writing/update_tables.py", "--check")
    else:
        print("Imported manuscript has no generated main-table region; legacy table comparison skipped.", flush=True)
    run("docs/paper-workbench/writing/update_structure_results.py", "--check")
    run("docs/paper-workbench/execution_effort.py", "--check")
    run("docs/paper-workbench/writing/execution_effort_tables.py", "--check")
    print("Available paper input checks passed; no files changed.", flush=True)


def has_generated_main_table() -> bool:
    return "% BEGIN GENERATED TABLE: main" in (MANUSCRIPT / "main.tex").read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "audit", "tables", "figures", "build", "package"))
    args = parser.parse_args()
    if args.command == "check":
        check()
    elif args.command == "audit":
        check()
        if not has_generated_main_table():
            raise RuntimeError("Legacy table audit requires a generated main-table region; the imported manuscript has none.")
        run("docs/paper-workbench/writing/update_tables.py", "--check", "--require-raw-profiles")
    elif args.command == "tables":
        validate_scope()
        if not has_generated_main_table():
            raise RuntimeError("Legacy table updater requires a generated main-table region; edit the imported manuscript directly.")
        run("docs/paper-workbench/writing/update_tables.py")
        run("docs/paper-workbench/writing/update_structure_results.py")
        run("docs/paper-workbench/writing/execution_effort_tables.py")
    elif args.command == "figures":
        validate_scope()
        run("docs/paper-workbench/figures/scripts/draw_all.py")
    elif args.command == "build":
        validate_manuscript()
        build_dir = PAPER / "build/current"
        build_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run([
            "latexmk", "-pdf", "-pdflatex=pdflatex -no-shell-escape %O %S",
            "-interaction=nonstopmode", "-halt-on-error",
            f"-outdir={build_dir}", "main.tex",
        ], cwd=MANUSCRIPT, check=True)
        shutil.copy2(build_dir / "main.pdf", MANUSCRIPT / "main.pdf")
        print(f"Built: {MANUSCRIPT / 'main.pdf'}")
    else:
        check()
        output = MANUSCRIPT / "featureliftbench_overleaf.zip"
        # Read all files before replacing the existing upload snapshot.
        payloads = [(name, (MANUSCRIPT / name).read_bytes()) for name in MANIFEST["paper_files"]]
        with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
            for name, data in payloads:
                archive.writestr(name, data)
        print(f"Packaged {len(payloads)} files: {output}")


if __name__ == "__main__":
    main()

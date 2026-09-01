#!/usr/bin/env python3.12
"""Build oracle/naive/copy-all submissions for Hard-50 pilot tasks."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PILOT = ROOT / "benchmark" / "hard50_pilot"
OUT = (
    ROOT
    / "experiments"
    / "validation"
    / "hard50"
    / "hard50_pilot_gates_20260827"
    / "submissions"
)

NAIVE = '''\
"""Intentionally incomplete naive extraction."""

class _Missing:
    def __getattr__(self, name):
        raise NotImplementedError(name)

    def __call__(self, *args, **kwargs):
        raise NotImplementedError

def __getattr__(name):
    return _Missing()
'''


def copytree(src: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def build() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for task_dir in sorted(p for p in PILOT.iterdir() if (p / "metadata.json").is_file()):
        oracle_src = task_dir / "reference_solution" / "featurelifted"
        if not oracle_src.is_dir():
            raise SystemExit(f"missing oracle: {oracle_src}")
        oracle = OUT / task_dir.name / "oracle" / "featurelifted"
        naive = OUT / task_dir.name / "naive" / "featurelifted"
        copy_all = OUT / task_dir.name / "copy_all" / "featurelifted"
        copytree(oracle_src, oracle)
        if naive.exists():
            shutil.rmtree(naive)
        naive.mkdir(parents=True)
        (naive / "__init__.py").write_text(NAIVE, encoding="utf-8")
        copytree(oracle_src, copy_all)
        decoy = copy_all / "_copyall_decoy"
        decoy.mkdir(exist_ok=True)
        oracle_loc = sum(
            1
            for path in oracle_src.rglob("*.py")
            if path.is_file()
            for _ in path.read_text(encoding="utf-8", errors="replace").splitlines()
            if _.strip()
        )
        pad_n = max(800, oracle_loc)
        pad = "\n".join(f"DECOY_VALUE_{i} = {i}  # unused copy-all padding" for i in range(pad_n))
        (decoy / "padding.py").write_text(pad + "\n", encoding="utf-8")
        print(f"{task_dir.name}: oracle/naive/copy_all pad={pad_n}")


if __name__ == "__main__":
    build()

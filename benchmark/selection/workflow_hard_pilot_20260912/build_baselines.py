"""Build honest shallow implementations and an explicit mechanical-copy control."""
import json
from pathlib import Path
import shutil
from definitions import TASKS

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main():
    for definition in TASKS:
        task = ROOT / "benchmark/staging" / definition["task_id"]
        base = task / "evaluation/baselines"
        if definition["source"] in {"pip", "dbt-core"}:
            name = "dbt" if definition["source"] == "dbt-core" else "pip"
            destination = base / "shallow_policy/featurelifted"
            destination.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HERE / "baselines" / (name + ".py"), destination / "__init__.py")
        else:
            # The current SQLGlot reference IS a mechanically renamed full
            # package. This control deliberately exposes that shortcut.
            shutil.copytree(task / "reference_solution", base / "mechanical_full_copy", dirs_exist_ok=True)
        description = dict(source=definition["source"], reference_is_minimal=False, artificial_padding=False, note="Shallow policy is independently implemented; mechanical_full_copy is the renamed full SQLGlot package with the public record adapter. Neither outcome is a strong-agent calibration.")
        (task / "evaluation/baseline_design.json").write_text(json.dumps(description, indent=2) + "\n")


if __name__ == "__main__":
    main()

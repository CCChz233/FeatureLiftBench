from __future__ import annotations

import pytest
from featurelifted import Session, false, true

pytestmark = pytest.mark.filterwarnings("ignore::UserWarning")


def test_true_false_and_or() -> None:
    assert bool(true) is True
    assert bool(false) is False
    assert bool(true & false) is False
    assert bool(true | false) is True


def test_run_obeys_true_condition() -> None:
    seen: list[str] = []

    def job() -> None:
        seen.append("ok")

    session = Session(
        config={
            "execution": "main",
            "cycle_sleep": 0,
            "silence_task_prerun": True,
            "silence_cond_check": True,
        }
    )
    session.create_task(start_cond=true, name="job", execution="main")(job)
    session.run("job", obey_cond=True, execution="main")
    assert seen == ["ok"]

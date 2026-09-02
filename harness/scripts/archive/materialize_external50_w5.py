#!/usr/bin/env python3
"""Materialize External-50 W5 tasks into benchmark/staging/."""

from __future__ import annotations

import importlib.util
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
PILOT = ROOT / "harness" / "scripts" / "materialize_external50_pilot.py"
W1 = ROOT / "harness" / "scripts" / "materialize_external50_w1.py"
PIN_ROOT = Path("/tmp/flb_w345_pins")
STAGING = ROOT / "benchmark" / "staging"

spec = importlib.util.spec_from_file_location("pilot_mat", PILOT)
pilot = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(pilot)

w1_spec = importlib.util.spec_from_file_location("w1_mat", W1)
w1 = importlib.util.module_from_spec(w1_spec)
assert w1_spec.loader is not None
w1_spec.loader.exec_module(w1)

copy_package_tree = w1.copy_package_tree
write_json = pilot.write_json
finalize_metadata = pilot.finalize_metadata
base_metadata = pilot.base_metadata
make_archive_and_register = pilot.make_archive_and_register


def w5_metadata(task_id: str, meta: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    metadata = base_metadata(task_id, meta, **kwargs)
    metadata["tags"] = ["external50", "w5", meta["lift"].lower(), meta["forbidden"]]
    return metadata


def _prepare(task_id: str, meta: dict[str, Any]) -> Path:
    task_dir = STAGING / task_id
    if task_dir.exists():
        shutil.rmtree(task_dir)
    task_dir.mkdir(parents=True)
    shutil.copytree(
        meta["src"],
        task_dir / "repo",
        ignore=shutil.ignore_patterns(
            "__pycache__", "*.pyc", ".flb_pin", "*.tar.gz", "wheels", ".git"
        ),
    )
    (task_dir / "evaluation").mkdir(parents=True)
    (task_dir / "public_tests").mkdir()
    (task_dir / "hidden_tests").mkdir()
    return task_dir


PINS: dict[str, dict[str, Any]] = {
    "more_itertools__recipes_core__001": {
        "package": "more-itertools",
        "url": "https://github.com/more-itertools/more-itertools",
        "commit": "64be96ceb2a6e836f76f069f4a96d2394d59fd0c",
        "tag": "v11.1.0",
        "license": "MIT",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "more_itertools",
        "forbidden": "more_itertools",
        "lift": "Direct",
        "pkg_dir": lambda: PIN_ROOT / "more_itertools" / "more_itertools",
    },
    "fasteners__process_lock_core__001": {
        "package": "fasteners",
        "url": "https://github.com/harlowja/fasteners",
        "commit": "87839f4acc6660856c67963b128dedd84e94907d",
        "tag": "0.20",
        "license": "Apache-2.0",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "fasteners",
        "forbidden": "fasteners",
        "lift": "Direct",
        "pkg_dir": lambda: PIN_ROOT / "fasteners" / "fasteners",
    },
    "portalocker__file_lock_core__001": {
        "package": "portalocker",
        "url": "https://github.com/WoLpH/portalocker",
        "commit": "cf1e80dd715a9df02e20b0eb38a03cb8b41bac31",
        "tag": "v4.0.0",
        "license": "BSD-3-Clause",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "portalocker",
        "forbidden": "portalocker",
        "lift": "Direct",
        "pkg_dir": lambda: PIN_ROOT / "portalocker" / "portalocker",
    },
    "pyotp__totp_hotp_core__001": {
        "package": "pyotp",
        "url": "https://github.com/pyotp/pyotp",
        "commit": "81ed54ac7347fbac522ce9c6bd1bca8e18ad4603",
        "tag": "v2.10.0",
        "license": "MIT",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "pyotp",
        "forbidden": "pyotp",
        "lift": "Direct",
        "pkg_dir": lambda: PIN_ROOT / "pyotp" / "src" / "pyotp",
    },
    "chardet__detect_core__001": {
        "package": "chardet",
        "url": "https://github.com/chardet/chardet",
        "commit": "376c381114c7d4b014fddc6b2eea784f0207d723",
        "tag": "unreleased-2.0.1",
        "license": "LGPL-2.1",
        "license_path": "COPYING",
        "src": PIN_ROOT / "chardet",
        "forbidden": "chardet",
        "lift": "Direct",
        "pkg_dir": lambda: PIN_ROOT / "chardet" / "src-python3" / "chardet",
    },
    "ftfy__fix_text_core__001": {
        "package": "ftfy",
        "url": "https://github.com/rspeer/python-ftfy",
        "commit": "5340af6746ff655a9cd7cb2b50c2fd0b35bb91d3",
        "tag": "v6.3.1",
        "license": "Apache-2.0",
        "license_path": "LICENSE.txt",
        "src": PIN_ROOT / "ftfy",
        "forbidden": "ftfy",
        "lift": "Direct",
        "pkg_dir": lambda: PIN_ROOT / "ftfy" / "ftfy",
    },
    "pyrsistent__pmap_pvector_core__001": {
        "package": "pyrsistent",
        "url": "https://github.com/tobgu/pyrsistent",
        "commit": "a6c9c18981168820fd8acaafc783946ce638b7dc",
        "tag": "v0.21.0",
        "license": "MIT",
        "license_path": "LICENSE.mit",
        "src": PIN_ROOT / "pyrsistent",
        "forbidden": "pyrsistent",
        "lift": "Direct",
        "pkg_dir": lambda: PIN_ROOT / "pyrsistent" / "pyrsistent",
    },
}


def materialize_more_itertools() -> Path:
    task_id = "more_itertools__recipes_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "more_itertools")
    (task_dir / "requirements.lock").write_text("# no third-party dependencies\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text(
        "more_itertools\n", encoding="utf-8"
    )
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "more_itertools",
            "required_source_files": [
                "more_itertools/recipes.py",
                "more_itertools/more.py",
                "more_itertools/__init__.py",
            ],
            "runtime_dependencies": [],
            "notes": "Direct extract of chunked/first/unique_everseen/consume/windowed helpers.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import chunked, consume, first, unique_everseen, windowed


def test_chunked_and_first() -> None:
    assert list(chunked(range(5), 2)) == [[0, 1], [2, 3], [4]]
    assert first(x for x in [0, 1, 2]) == 0


def test_unique_everseen() -> None:
    assert list(unique_everseen([1, 2, 1, 3, 2])) == [1, 2, 3]


def test_consume_and_windowed() -> None:
    it = iter(range(5))
    consume(it, 2)
    assert next(it) == 2
    assert list(windowed([1, 2, 3, 4], 3)) == [(1, 2, 3), (2, 3, 4)]
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
from pathlib import Path

from featurelifted import chunked, consume, first, unique_everseen, windowed


def test_chunked_strict() -> None:
    try:
        list(chunked([1, 2, 3], 2, strict=True))
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_unique_everseen_key() -> None:
    data = ["A", "a", "B", "b"]
    assert list(unique_everseen(data, key=str.lower)) == ["A", "B"]


def test_windowed_fillvalue() -> None:
    assert list(windowed([1, 2], 3, fillvalue=0)) == [(1, 2, 0)]


def test_consume_all() -> None:
    it = iter(range(3))
    consume(it)
    assert list(it) == []


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from more_itertools\\b|import more_itertools\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import chunked, consume, first, unique_everseen, windowed


def test_required_api_surface() -> None:
    assert all(callable(x) for x in (chunked, consume, first, unique_everseen, windowed))
''',
        encoding="utf-8",
    )
    metadata = w5_metadata(
        task_id,
        meta,
        feature={
            "name": "more_itertools recipes",
            "description": "Direct extract of more_itertools chunked/first/unique_everseen/consume/windowed.",
            "source_entrypoints": [
                "more_itertools.chunked",
                "more_itertools.recipes.unique_everseen",
                "more_itertools.recipes.consume",
            ],
            "included_behaviors": [
                "chunked splits iterables into fixed-size tuples",
                "first returns first item",
                "unique_everseen deduplicates preserving order",
                "consume advances iterators",
                "windowed sliding windows",
            ],
            "excluded_behaviors": ["full more_itertools surface beyond listed helpers"],
        },
        entanglement={
            "level": "low",
            "types": ["data_model_coupling"],
            "primary": "data_model_coupling",
            "description": "Pure iterator helper toolkit.",
            "signals": ["chunked", "windowed", "unique_everseen"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import chunked, first, unique_everseen, consume, windowed",
            "callable": "chunked",
            "signature": "chunked(iterable, n, strict=False)",
        },
        public_spec={
            "title": "more_itertools recipes",
            "summary": "Extract a task-scoped subset of `more_itertools` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.chunked", "kind": "function", "signature": "(iterable, n, strict=False)"},
                {"path": "featurelifted.first", "kind": "function", "signature": "(iterable, default=...)"},
                {"path": "featurelifted.unique_everseen", "kind": "function", "signature": "(iterable, key=None)"},
                {"path": "featurelifted.consume", "kind": "function", "signature": "(iterator, n=None)"},
                {"path": "featurelifted.windowed", "kind": "function", "signature": "(seq, n, fillvalue=None, step=1)"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: chunked splits iterables and first returns the first element. Required observable cases include chunked and first."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: unique_everseen deduplicates preserving order. Required observable cases include unique everseen; unique everseen key."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: consume advances iterators and windowed yields sliding tuples. Required observable cases include consume and windowed; windowed fillvalue; consume all."},
                {"id": "B004", "text": "chunked strict=True raises ValueError when the iterable length is not divisible by n."},
                {"id": "B005", "text": "The package exposes chunked/first/unique_everseen/consume/windowed with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: more_itertools."},
            ],
            "exclusions": ["full more_itertools catalog", "original more_itertools import at runtime"],
            "forbidden": {"imports": ["more_itertools"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_fasteners() -> Path:
    task_id = "fasteners__process_lock_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "fasteners")
    (task_dir / "requirements.lock").write_text("# no third-party dependencies\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("fasteners\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "fasteners",
            "required_source_files": [
                "fasteners/process_lock.py",
                "fasteners/process_mechanism.py",
            ],
            "runtime_dependencies": [],
            "notes": "Direct InterProcessLock acquire/release/context manager.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import InterProcessLock


def test_acquire_release(tmp_path) -> None:
    lock_path = str(tmp_path / "lock")
    lock = InterProcessLock(lock_path)
    assert lock.acquire() is True
    lock.release()


def test_context_manager(tmp_path) -> None:
    lock_path = str(tmp_path / "lock2")
    with InterProcessLock(lock_path):
        pass
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
from pathlib import Path

from featurelifted import InterProcessLock


def test_reacquire_after_release(tmp_path) -> None:
    lock_path = str(tmp_path / "reuse")
    lock = InterProcessLock(lock_path)
    assert lock.acquire() is True
    lock.release()
    assert lock.acquire() is True
    lock.release()


def test_nonblocking_acquire_free_lock(tmp_path) -> None:
    lock_path = str(tmp_path / "nb")
    lock = InterProcessLock(lock_path)
    assert lock.acquire(blocking=False) is True
    lock.release()


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from fasteners\\b|import fasteners\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import InterProcessLock


def test_required_api_surface() -> None:
    assert InterProcessLock is not None
''',
        encoding="utf-8",
    )
    metadata = w5_metadata(
        task_id,
        meta,
        feature={
            "name": "fasteners process lock",
            "description": "Direct fasteners InterProcessLock acquire/release/context manager.",
            "source_entrypoints": ["fasteners.InterProcessLock"],
            "included_behaviors": [
                "acquire returns bool and release unlocks",
                "context manager acquire/release",
                "non-blocking acquire option",
            ],
            "excluded_behaviors": ["redis locks", "ReaderWriterLock unless listed"],
        },
        entanglement={
            "level": "medium",
            "types": ["resource_coupling"],
            "primary": "resource_coupling",
            "description": "Filesystem advisory lock file coordination.",
            "signals": ["InterProcessLock", "acquire/release"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import InterProcessLock",
            "callable": "InterProcessLock.acquire",
            "signature": "acquire(blocking: bool = True) -> bool",
        },
        public_spec={
            "title": "fasteners process lock",
            "summary": "Extract a task-scoped subset of `fasteners` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.InterProcessLock", "kind": "class"},
                {"path": "featurelifted.InterProcessLock.acquire", "kind": "method", "signature": "(blocking: bool = True) -> bool"},
                {"path": "featurelifted.InterProcessLock.release", "kind": "method"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: InterProcessLock acquire/release. Required observable cases include acquire release; reacquire after release."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: context manager acquires and releases. Required observable cases include context manager."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: non-blocking acquire succeeds on a free lock. Required observable cases include nonblocking acquire free lock."},
                {"id": "B004", "text": "Lock files are created under the provided path in temp directories during tests."},
                {"id": "B005", "text": "The package exposes InterProcessLock with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: fasteners."},
            ],
            "exclusions": ["redis locks", "original fasteners import at runtime"],
            "forbidden": {"imports": ["fasteners"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_portalocker() -> Path:
    task_id = "portalocker__file_lock_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "portalocker")
    # Intra-package submodule refs must stay relative (not top-level featurelifted.*).
    for path in ref.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        updated = (
            text.replace("lock = featurelifted.lock\n", "lock = portalocker.lock\n")
            .replace("unlock = featurelifted.unlock\n", "unlock = portalocker.unlock\n")
            .replace("featurelifted.lock(", "portalocker.lock(")
            .replace("featurelifted.unlock(", "portalocker.unlock(")
        )
        if updated != text:
            path.write_text(updated, encoding="utf-8")
    (task_dir / "requirements.lock").write_text("# no third-party dependencies\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("portalocker\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "portalocker",
            "required_source_files": [
                "portalocker/portalocker.py",
                "portalocker/utils.py",
                "portalocker/constants.py",
            ],
            "runtime_dependencies": [],
            "notes": "Direct lock/unlock + Lock context manager + LOCK_EX.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import LOCK_EX, Lock, lock, unlock


def test_lock_context_manager(tmp_path) -> None:
    path = tmp_path / "data.txt"
    path.write_text("x", encoding="utf-8")
    with Lock(str(path), mode="a") as fh:
        fh.write("y")
    assert "xy" in path.read_text(encoding="utf-8")


def test_lock_unlock_functions(tmp_path) -> None:
    path = tmp_path / "raw.txt"
    path.write_text("a", encoding="utf-8")
    fh = open(path, "a")
    try:
        lock(fh, LOCK_EX)
        fh.write("b")
        unlock(fh)
    finally:
        fh.close()
    assert path.read_text(encoding="utf-8") == "ab"
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
from pathlib import Path

from featurelifted import LOCK_EX, LOCK_NB, LOCK_SH, Lock, LockException


def test_lock_constants() -> None:
    assert LOCK_EX is not None and LOCK_SH is not None and LOCK_NB is not None


def test_lock_exception_type() -> None:
    assert issubclass(LockException, Exception)


def test_lock_timeout(tmp_path) -> None:
    path = tmp_path / "t.txt"
    path.write_text("z", encoding="utf-8")
    with Lock(str(path), timeout=1):
        assert path.exists()


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from portalocker\\b|import portalocker\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import LOCK_EX, Lock, lock, unlock


def test_required_api_surface() -> None:
    assert Lock is not None and callable(lock) and callable(unlock)
    assert LOCK_EX is not None
''',
        encoding="utf-8",
    )
    metadata = w5_metadata(
        task_id,
        meta,
        feature={
            "name": "portalocker file lock",
            "description": "Direct portalocker lock/unlock + Lock context manager.",
            "source_entrypoints": ["portalocker.lock", "portalocker.Lock", "portalocker.LOCK_EX"],
            "included_behaviors": [
                "Lock context manager yields file handle",
                "lock/unlock advisory file locks",
                "LOCK_EX/LOCK_SH/LOCK_NB constants",
            ],
            "excluded_behaviors": ["redis lock", "network locks"],
        },
        entanglement={
            "level": "medium",
            "types": ["resource_coupling"],
            "primary": "resource_coupling",
            "description": "OS file descriptor locking.",
            "signals": ["Lock", "LOCK_EX", "lock/unlock"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import Lock, lock, unlock, LOCK_EX",
            "callable": "Lock",
            "signature": "Lock(filename, mode='a', timeout=None)",
        },
        public_spec={
            "title": "portalocker file lock",
            "summary": "Extract a task-scoped subset of `portalocker` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.lock", "kind": "function", "signature": "(file, flags=LOCK_EX)"},
                {"path": "featurelifted.unlock", "kind": "function", "signature": "(file)"},
                {"path": "featurelifted.Lock", "kind": "class"},
                {"path": "featurelifted.LOCK_EX", "kind": "constant"},
                {"path": "featurelifted.LOCK_SH", "kind": "constant"},
                {"path": "featurelifted.LOCK_NB", "kind": "constant"},
                {"path": "featurelifted.LockException", "kind": "class"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: Lock context manager and lock/unlock on file handles. Required observable cases include lock context manager; lock unlock functions."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: LOCK_EX and related constants are exposed. Required observable cases include lock constants."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: Lock accepts timeout and LockException exists. Required observable cases include lock timeout; lock exception type."},
                {"id": "B004", "text": "Tests use local temp files only; no network resources."},
                {"id": "B005", "text": "The package exposes Lock/lock/unlock/LOCK_EX/LockException with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: portalocker."},
            ],
            "exclusions": ["redis lock", "original portalocker import at runtime"],
            "forbidden": {"imports": ["portalocker"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_pyotp() -> Path:
    task_id = "pyotp__totp_hotp_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "pyotp")
    (task_dir / "requirements.lock").write_text("# no third-party dependencies\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("pyotp\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "pyotp",
            "required_source_files": ["pyotp/totp.py", "pyotp/hotp.py", "pyotp/__init__.py"],
            "runtime_dependencies": [],
            "notes": "Direct TOTP/HOTP at/verify + random_base32.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

import datetime

from featurelifted import HOTP, TOTP, random_base32


SECRET = "JBSWY3DPEHPK3PXP"


def test_totp_at_verify() -> None:
    totp = TOTP(SECRET)
    when = datetime.datetime.fromtimestamp(1234567890)
    code = totp.at(when)
    assert code == "742275"
    assert totp.verify(code, when) is True


def test_hotp_at_verify() -> None:
    hotp = HOTP(SECRET)
    code = hotp.at(0)
    assert code == "282760"
    assert hotp.verify(code, 0) is True


def test_random_base32() -> None:
    secret = random_base32()
    assert len(secret) == 32
    assert set(secret) <= set("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567")
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import datetime
import re
from pathlib import Path

from featurelifted import HOTP, TOTP, random_base32


SECRET = "JBSWY3DPEHPK3PXP"


def test_totp_verify_rejects_wrong() -> None:
    totp = TOTP(SECRET)
    when = datetime.datetime.fromtimestamp(1234567890)
    assert totp.verify("000000", when) is False


def test_hotp_counter_increments() -> None:
    hotp = HOTP(SECRET)
    assert hotp.at(0) != hotp.at(1)


def test_random_base32_length_guard() -> None:
    try:
        random_base32(length=16)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from pyotp\\b|import pyotp\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import HOTP, TOTP, random_base32


def test_required_api_surface() -> None:
    assert TOTP is not None and HOTP is not None
    assert callable(random_base32)
''',
        encoding="utf-8",
    )
    metadata = w5_metadata(
        task_id,
        meta,
        feature={
            "name": "pyotp totp hotp",
            "description": "Direct pyotp TOTP/HOTP at/verify + random_base32.",
            "source_entrypoints": ["pyotp.TOTP", "pyotp.HOTP", "pyotp.random_base32"],
            "included_behaviors": [
                "TOTP.at/verify for timestamps",
                "HOTP.at/verify for counters",
                "random_base32 secret generation",
            ],
            "excluded_behaviors": ["QR provisioning network", "parse_uri unless listed"],
        },
        entanglement={
            "level": "low",
            "types": ["data_model_coupling"],
            "primary": "data_model_coupling",
            "description": "OTP generation and verification helpers.",
            "signals": ["TOTP.at", "HOTP.verify", "random_base32"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import TOTP, HOTP, random_base32",
            "callable": "TOTP.at",
            "signature": "at(for_time) -> str",
        },
        public_spec={
            "title": "pyotp totp hotp",
            "summary": "Extract a task-scoped subset of `pyotp` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.TOTP", "kind": "class"},
                {"path": "featurelifted.TOTP.at", "kind": "method"},
                {"path": "featurelifted.TOTP.verify", "kind": "method"},
                {"path": "featurelifted.HOTP", "kind": "class"},
                {"path": "featurelifted.HOTP.at", "kind": "method"},
                {"path": "featurelifted.HOTP.verify", "kind": "method"},
                {"path": "featurelifted.random_base32", "kind": "function", "signature": "(length=32)"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: TOTP.at/verify for fixed timestamps. Required observable cases include totp at verify; totp verify rejects wrong."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: HOTP.at/verify for counters. Required observable cases include hotp at verify; hotp counter increments."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: random_base32 generates base32 secrets with minimum length guard. Required observable cases include random base32; random base32 length guard."},
                {"id": "B004", "text": "Tests use at(timestamp) rather than now() to avoid time dependence."},
                {"id": "B005", "text": "The package exposes TOTP/HOTP/random_base32 with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: pyotp."},
            ],
            "exclusions": ["QR provisioning network", "original pyotp import at runtime"],
            "forbidden": {"imports": ["pyotp"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_chardet() -> Path:
    task_id = "chardet__detect_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "chardet")
    (task_dir / "requirements.lock").write_text("# no third-party dependencies\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("chardet\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "chardet",
            "required_source_files": ["chardet/__init__.py", "chardet/universaldetector.py"],
            "runtime_dependencies": [],
            "notes": "Direct chardet.detect(bytes) -> encoding/confidence dict.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import detect


def test_detect_ascii() -> None:
    result = detect(b"hello")
    assert result["encoding"] == "ascii"
    assert result["confidence"] >= 0.9


def test_detect_utf8() -> None:
    result = detect("café".encode("utf-8"))
    assert result["encoding"] == "utf-8"
    assert "confidence" in result


def test_detect_cyrillic_utf8() -> None:
    result = detect("Привет".encode("utf-8"))
    assert result["encoding"] == "utf-8"
    assert result["confidence"] >= 0.5
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
from pathlib import Path

from featurelifted import detect


def test_detect_empty_bytes() -> None:
    result = detect(b"")
    assert "encoding" in result and "confidence" in result


def test_detect_latin1() -> None:
    raw = bytes(range(128, 160))
    result = detect(raw)
    assert isinstance(result, dict)
    assert result.get("encoding") is not None or result.get("confidence") is not None


def test_result_keys() -> None:
    result = detect(b"abc")
    assert set(result.keys()) >= {"encoding", "confidence"}


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from chardet\\b|import chardet\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import detect


def test_required_api_surface() -> None:
    assert callable(detect)
''',
        encoding="utf-8",
    )
    metadata = w5_metadata(
        task_id,
        meta,
        feature={
            "name": "chardet detect",
            "description": "Direct chardet.detect encoding detection on byte samples.",
            "source_entrypoints": ["chardet.detect"],
            "included_behaviors": [
                "detect returns encoding/confidence dict",
                "ascii and utf-8 fixtures",
                "empty input behavior",
            ],
            "excluded_behaviors": ["chardetect CLI", "UniversalDetector direct use"],
        },
        entanglement={
            "level": "medium",
            "types": ["parser_state_coupling"],
            "primary": "parser_state_coupling",
            "description": "Charset prober pipeline over byte buffers.",
            "signals": ["detect", "encoding", "confidence"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import detect",
            "callable": "detect",
            "signature": "detect(byte_str: bytes) -> dict",
        },
        public_spec={
            "title": "chardet detect",
            "summary": "Extract a task-scoped subset of `chardet` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.detect", "kind": "function", "signature": "(byte_str: bytes) -> dict"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: detect returns encoding/confidence for ascii and utf-8 bytes. Required observable cases include detect ascii; detect utf8; detect cyrillic utf8."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: detect handles empty buffers and returns dict keys. Required observable cases include detect empty bytes; result keys."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: detect returns a dict for latin1 byte ranges. Required observable cases include detect latin1."},
                {"id": "B004", "text": "detect operates on bytes fixtures only; no filesystem or network."},
                {"id": "B005", "text": "The package exposes detect with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: chardet."},
            ],
            "exclusions": ["chardetect CLI", "original chardet import at runtime"],
            "forbidden": {"imports": ["chardet"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_ftfy() -> Path:
    task_id = "ftfy__fix_text_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "ftfy")
    (task_dir / "requirements.lock").write_text("wcwidth==0.2.13\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("ftfy\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "ftfy",
            "required_source_files": ["ftfy/__init__.py", "ftfy/fixes.py"],
            "runtime_dependencies": ["wcwidth"],
            "notes": "Direct ftfy.fix_text mojibake repair.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import fix_text


def test_fix_latin1_mojibake() -> None:
    assert fix_text("cafÃ©") == "café"


def test_fix_em_dash_mojibake() -> None:
    assert fix_text("â€”") == "—"


def test_fix_identity_ascii() -> None:
    assert fix_text("plain text") == "plain text"
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
from pathlib import Path

from featurelifted import fix_text


def test_fix_double_encoded_utf8() -> None:
    broken = "Ã©".encode("latin-1").decode("utf-8", errors="replace")
    assert "é" in fix_text(broken) or fix_text(broken) != broken


def test_fix_preserves_newlines() -> None:
    text = "line1\\nline2"
    assert fix_text(text) == text


def test_fix_empty() -> None:
    assert fix_text("") == ""


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from ftfy\\b|import ftfy\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import fix_text


def test_required_api_surface() -> None:
    assert callable(fix_text)
''',
        encoding="utf-8",
    )
    metadata = w5_metadata(
        task_id,
        meta,
        allowed_dependencies=["wcwidth"],
        feature={
            "name": "ftfy fix text",
            "description": "Direct ftfy.fix_text mojibake repair.",
            "source_entrypoints": ["ftfy.fix_text"],
            "included_behaviors": [
                "fix_text repairs common mojibake",
                "preserves plain ascii",
                "handles empty strings",
            ],
            "excluded_behaviors": ["ftfy CLI", "guess_bytes unless listed"],
        },
        entanglement={
            "level": "medium",
            "types": ["parser_state_coupling"],
            "primary": "parser_state_coupling",
            "description": "Unicode normalization and encoding-fix heuristics.",
            "signals": ["fix_text", "mojibake"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import fix_text",
            "callable": "fix_text",
            "signature": "fix_text(text: str, ...) -> str",
        },
        public_spec={
            "title": "ftfy fix text",
            "summary": "Extract a task-scoped subset of `ftfy` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.fix_text", "kind": "function", "signature": "(text: str, ...) -> str"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: fix_text repairs latin-1 mojibake and em-dash sequences. Required observable cases include fix latin1 mojibake; fix em dash mojibake."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: fix_text leaves plain ascii unchanged. Required observable cases include fix identity ascii; fix preserves newlines."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: fix_text handles empty and partially broken utf-8. Required observable cases include fix empty; fix double encoded utf8."},
                {"id": "B004", "text": "wcwidth is the only allowed third-party dependency for formatting helpers."},
                {"id": "B005", "text": "The package exposes fix_text with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: ftfy."},
            ],
            "exclusions": ["ftfy CLI", "original ftfy import at runtime"],
            "forbidden": {"imports": ["ftfy"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_pyrsistent() -> Path:
    task_id = "pyrsistent__pmap_pvector_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "pyrsistent")
    (task_dir / "requirements.lock").write_text("# no third-party dependencies\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("pyrsistent\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "pyrsistent",
            "required_source_files": [
                "pyrsistent/_pmap.py",
                "pyrsistent/_pvector.py",
                "pyrsistent/__init__.py",
            ],
            "runtime_dependencies": [],
            "notes": "Direct pmap/pvector + PMap.set/get + PVector.append.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import PMap, PVector, pmap, pvector


def test_pmap_set_get() -> None:
    m = pmap({"a": 1})
    m2 = m.set("b", 2)
    assert m2["a"] == 1 and m2.get("b") == 2
    assert m is not m2


def test_pvector_append() -> None:
    v = pvector([1, 2])
    v2 = v.append(3)
    assert list(v) == [1, 2] and list(v2) == [1, 2, 3]
    assert v is not v2


def test_factory_types() -> None:
    assert isinstance(pmap(), PMap)
    assert isinstance(pvector(), PVector)
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
from pathlib import Path

from featurelifted import pmap, pvector


def test_pmap_immutability() -> None:
    m = pmap({"x": 1})
    m2 = m.set("y", 2)
    assert "y" not in m and m2["y"] == 2


def test_pvector_set() -> None:
    v = pvector([10, 20, 30])
    v2 = v.set(1, 99)
    assert list(v) == [10, 20, 30] and list(v2) == [10, 99, 30]


def test_pvector_extend() -> None:
    base = pvector([1])
    extended = base.extend([2, 3])
    assert list(extended) == [1, 2, 3]


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from pyrsistent\\b|import pyrsistent\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import PMap, PVector, pmap, pvector


def test_required_api_surface() -> None:
    assert callable(pmap) and callable(pvector)
    assert PMap is not None and PVector is not None
''',
        encoding="utf-8",
    )
    metadata = w5_metadata(
        task_id,
        meta,
        feature={
            "name": "pyrsistent pmap pvector",
            "description": "Direct pyrsistent pmap/pvector persistent collections.",
            "source_entrypoints": ["pyrsistent.pmap", "pyrsistent.pvector", "pyrsistent.PMap", "pyrsistent.PVector"],
            "included_behaviors": [
                "pmap/PMap.set/get immutable maps",
                "pvector/PVector.append/set/extend",
                "updates return new objects leaving originals unchanged",
            ],
            "excluded_behaviors": ["pset/pdeque/pclass unless listed", "C extension requirement"],
        },
        entanglement={
            "level": "medium",
            "types": ["data_model_coupling"],
            "primary": "data_model_coupling",
            "description": "Persistent data structures with structural sharing.",
            "signals": ["pmap", "pvector", "immutability"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import pmap, pvector, PMap, PVector",
            "callable": "pmap",
            "signature": "pmap(initial=None) -> PMap",
        },
        public_spec={
            "title": "pyrsistent pmap pvector",
            "summary": "Extract a task-scoped subset of `pyrsistent` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.pmap", "kind": "function", "signature": "(initial=None) -> PMap"},
                {"path": "featurelifted.pvector", "kind": "function", "signature": "(initial=()) -> PVector"},
                {"path": "featurelifted.PMap", "kind": "class"},
                {"path": "featurelifted.PMap.set", "kind": "method"},
                {"path": "featurelifted.PMap.get", "kind": "method"},
                {"path": "featurelifted.PVector", "kind": "class"},
                {"path": "featurelifted.PVector.append", "kind": "method"},
                {"path": "featurelifted.PVector.extend", "kind": "method"},
                {"path": "featurelifted.PVector.set", "kind": "method"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: pmap/PMap.set/get returns new maps without mutating originals. Required observable cases include pmap set get; pmap immutability."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: pvector/PVector.append returns new vectors. Required observable cases include pvector append; factory types."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: PVector.set/extend produce new vectors. Required observable cases include pvector set; pvector extend."},
                {"id": "B004", "text": "Original pmap/pvector instances remain unchanged after updates."},
                {"id": "B005", "text": "The package exposes pmap/pvector/PMap/PVector with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: pyrsistent."},
            ],
            "exclusions": ["pset/pdeque/pclass", "original pyrsistent import at runtime"],
            "forbidden": {"imports": ["pyrsistent"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


BUILDERS: dict[str, Callable[[], Path]] = {
    "more_itertools__recipes_core__001": materialize_more_itertools,
    "fasteners__process_lock_core__001": materialize_fasteners,
    "portalocker__file_lock_core__001": materialize_portalocker,
    "pyotp__totp_hotp_core__001": materialize_pyotp,
    "chardet__detect_core__001": materialize_chardet,
    "ftfy__fix_text_core__001": materialize_ftfy,
    "pyrsistent__pmap_pvector_core__001": materialize_pyrsistent,
}


def main(argv: list[str]) -> int:
    targets = argv[1:] or list(BUILDERS)
    for task_id in targets:
        if task_id not in BUILDERS:
            print(f"unknown/not-yet-supported: {task_id}", file=sys.stderr)
            return 1
        path = BUILDERS[task_id]()
        print(f"materialized {task_id} -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

"""Archive exact Git blobs and modes, independently of Windows checkout conversion."""
from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "harness"))
from featureliftbench.source_archive import safe_extract_archive


def run_git(checkout, *args):
    return subprocess.check_output(["git", "-C", str(checkout), *args])


def prepare(source):
    base = ROOT / "benchmark/sources/workflow_hard_pilot"
    checkout = base / "checkouts" / source["name"]
    commit = run_git(checkout, "rev-parse", "HEAD").decode().strip()
    if commit != source["commit"]:
        raise ValueError(f"Unexpected revision: {source['name']} {commit}")
    entries = []
    for record in run_git(checkout, "ls-tree", "-rz", "HEAD").split(b"\0"):
        if not record:
            continue
        info, path = record.split(b"\t", 1)
        mode, kind, oid = info.decode().split()
        if kind != "blob" or mode not in {"100644", "100755", "120000"}:
            raise ValueError(f"Unmaterialized submodule/unsupported entry: {path!r}")
        entries.append((path.decode("utf-8"), mode, oid))
    entries.sort(key=lambda item: item[0].encode("utf-8"))
    archive = ROOT / "benchmark/sources/archives" / f"workflow-pilot-{source['name']}-{commit[:12]}.tar.gz"
    archive.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    stats = dict(tracked_file_count=0, python_file_count=0, python_loc=0, total_bytes=0, max_path_depth=0)
    git = subprocess.Popen(["git", "-C", str(checkout), "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        with archive.open("wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed, tarfile.open(fileobj=compressed, mode="w|") as tf:
            for path, mode, oid in entries:
                git.stdin.write((oid + "\n").encode())
                git.stdin.flush()
                blob_oid, kind, size = git.stdout.readline().decode().split()
                content = git.stdout.read(int(size))
                if blob_oid != oid or kind != "blob" or git.stdout.read(1) != b"\n":
                    raise ValueError("Invalid Git batch response")
                name = Path(path)
                if name.is_absolute() or ".." in name.parts:
                    raise ValueError(path)
                item = tarfile.TarInfo(path)
                item.mode = int(mode[-3:], 8)
                item.mtime = item.uid = item.gid = 0
                item.uname = item.gname = ""
                if mode == "120000":
                    item.type = tarfile.SYMTYPE
                    item.linkname = content.decode("utf-8")
                    tf.addfile(item)
                else:
                    item.size = len(content)
                    tf.addfile(item, io.BytesIO(content))
                record = "\0".join(["symlink" if mode == "120000" else "file", mode, path, str(len(content)), hashlib.sha256(content).hexdigest()]) + "\n"
                digest.update(record.encode())
                stats["tracked_file_count"] += 1
                stats["total_bytes"] += len(content)
                stats["max_path_depth"] = max(stats["max_path_depth"], len(name.parts))
                if path.endswith(".py") and mode != "120000":
                    stats["python_file_count"] += 1
                    stats["python_loc"] += sum(bool(line.strip()) and not line.strip().startswith("#") for line in content.decode("utf-8", errors="ignore").splitlines())
    finally:
        git.stdin.close()
        git.stdout.close()
        if git.wait() != 0:
            raise RuntimeError("git cat-file failed")
    tree = base / "trees" / source["name"]
    tree.mkdir(parents=True, exist_ok=True)
    safe_extract_archive(archive, tree)
    if not (tree / source["license_path"]).is_file():
        raise ValueError("Missing upstream license")
    return {**source, **stats, "archive_path": archive.relative_to(ROOT).as_posix(), "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(), "source_tree_sha256": digest.hexdigest(), "tree_path": tree.relative_to(ROOT).as_posix()}


if __name__ == "__main__":
    sources = json.loads((HERE / "sources.json").read_text())["sources"]
    result = [prepare(source) for source in sources]
    (HERE / "source_evidence.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps([{k: s[k] for k in ("name", "commit", "tracked_file_count", "python_loc", "archive_sha256")} for s in result], indent=2))

"""Locate recorded sources without rewriting historical hashes or run records."""
import hashlib
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paper_inputs import ROOT


def verify_source(record):
    relative = record['path']
    candidates = [ROOT / relative, ROOT / 'archive/paper_unrelated_20260914' / relative]
    for path in candidates:
        if not path.is_file():
            continue
        raw = path.read_bytes()
        variants = {'exact': raw}
        # Only line endings may differ. The transformed bytes must reproduce
        # the recorded SHA-256 exactly; arbitrary semantic changes still fail.
        lf = raw.replace(b'\r\n', b'\n')
        variants['LF-equivalent'] = lf
        variants['CRLF-equivalent'] = lf.replace(b'\n', b'\r\n')
        for mode, content in variants.items():
            if hashlib.sha256(content).hexdigest() == record['sha256']:
                return {'recorded_path': relative,
                        'resolved_path': path.relative_to(ROOT).as_posix(),
                        'verification': mode}
    raise AssertionError(f'Recorded evidence missing or changed: {relative}')

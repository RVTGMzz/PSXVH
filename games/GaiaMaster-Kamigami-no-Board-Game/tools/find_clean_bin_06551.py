#!/usr/bin/env python3
# -*- coding: ascii -*-
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

CLEAN_SHA1 = "f4d5298583c90d89c4b7e51d2dde160ee07f2aec"


def sha1_file(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().lower()


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: find_clean_bin_06551.py ROOT OUTPUT_PATH_FILE", file=sys.stderr)
        return 2

    root = Path(sys.argv[1]).expanduser().resolve()
    out = Path(sys.argv[2]).expanduser().resolve()
    if not root.is_dir():
        print("[ERROR] Package root not found: %s" % root, file=sys.stderr)
        return 2

    # Package workflow removes ROM-like files from Core, so recursive scan is
    # safe and also supports a user placing the clean BIN in a small subfolder.
    candidates = sorted(
        (p for p in root.rglob("*.bin") if p.is_file()),
        key=lambda p: (len(p.parts), str(p).lower()),
    )

    for p in candidates:
        try:
            got = sha1_file(p)
        except OSError:
            continue
        if got == CLEAN_SHA1:
            out.write_text(str(p), encoding="utf-8")
            print("[OK] CLEAN Japan BIN found: %s" % p)
            return 0

    try:
        if out.exists():
            out.unlink()
    except OSError:
        pass
    print("[ERROR] CLEAN Japan BIN with expected SHA1 was not found.", file=sys.stderr)
    print("Expected SHA1: %s" % CLEAN_SHA1, file=sys.stderr)
    print("Scanned BIN files: %d" % len(candidates), file=sys.stderr)
    return 3


if __name__ == "__main__":
    raise SystemExit(main())

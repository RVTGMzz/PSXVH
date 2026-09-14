#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract the readable source embedded in build_gaia_06100_hybrid_accent_b1.py.

The wrapper stores the exact development source as zlib-compressed Base85 and
records the expected SHA1 in its module docstring. This extractor parses the
wrapper AST without executing the embedded builder, verifies the known SHA1,
and writes an auditable readable snapshot.
"""
from __future__ import annotations

import ast
import base64
import hashlib
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "build_gaia_06100_hybrid_accent_b1.py"
OUT = HERE / "build_gaia_06100_hybrid_accent_b1_READABLE.py"
EXPECTED_SHA1 = "faea2fbf90d3b4038ad64d3872934c043115878a"


def main() -> int:
    tree = ast.parse(SRC.read_text(encoding="utf-8"), filename=str(SRC))
    payload = None
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(t, ast.Name) and t.id == "_PAYLOAD" for t in node.targets):
            continue
        payload = ast.literal_eval(node.value)
        break
    if not isinstance(payload, (bytes, bytearray)):
        raise SystemExit("[BLOCKED] _PAYLOAD bytes literal not found")

    raw = zlib.decompress(base64.b85decode(payload))
    got = hashlib.sha1(raw).hexdigest()
    if got != EXPECTED_SHA1:
        raise SystemExit(f"[BLOCKED] readable source SHA1 mismatch: {got}")

    # Ensure the embedded source is valid UTF-8 Python before persisting it.
    text = raw.decode("utf-8")
    compile(text, OUT.name, "exec")
    OUT.write_text(text, encoding="utf-8", newline="\n")

    print(f"[OK] extracted {OUT.name}")
    print(f"bytes={len(raw)} sha1={got}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import base64
import gzip
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PARTS = ROOT / "parts"
OUT = ROOT / "GaiaMaster_RUNTIME_CANDIDATE_EXACT_OVERLAY_B50.csv"
EXPECTED_RAW_SHA256 = "448bc34afa675299b0de20c54d804d5765e7f9954f67c39058884b318de504b7"
EXPECTED_GZIP_SHA256 = "4b8373f53ea04b3b89420c874870b07016fd817c51e603b5644643e6cc122b60"
EXPECTED_RAW_SIZE = 162851


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    part_paths = sorted(PARTS.glob("GaiaMaster_RUNTIME_CANDIDATE_EXACT_OVERLAY_B50.csv.gz.b64.part*"))
    if len(part_paths) != 4:
        raise SystemExit(f"Expected 4 parts, found {len(part_paths)}")

    b64 = "".join(path.read_text(encoding="ascii").strip() for path in part_paths)
    gz = base64.b64decode(b64, validate=True)
    if sha256(gz) != EXPECTED_GZIP_SHA256:
        raise SystemExit("Compressed SHA256 mismatch")

    raw = gzip.decompress(gz)
    if len(raw) != EXPECTED_RAW_SIZE:
        raise SystemExit(f"Raw size mismatch: {len(raw)} != {EXPECTED_RAW_SIZE}")
    if sha256(raw) != EXPECTED_RAW_SHA256:
        raise SystemExit("Raw SHA256 mismatch")

    OUT.write_bytes(raw)
    print(f"Restored: {OUT}")
    print(f"Rows/checkpoint: B50 exact-offset runtime candidate overlay")
    print(f"SHA256: {EXPECTED_RAW_SHA256}")


if __name__ == "__main__":
    main()

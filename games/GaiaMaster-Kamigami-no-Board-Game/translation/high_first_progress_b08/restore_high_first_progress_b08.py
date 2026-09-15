#!/usr/bin/env python3
from pathlib import Path
import gzip
import hashlib

HERE = Path(__file__).resolve().parent
PARTS = [HERE / f"HIGH_FIRST_PROGRESS_B08.csv.gz.part{i:02d}" for i in range(1, 6)]
OUT = HERE / "HIGH_FIRST_PROGRESS_B08.csv"
EXPECTED_GZ_SHA256 = "23d5989bae4101a48fea8d0e3b82d8eb5475cdb0b3f4ae203e2ff4598286a905"
EXPECTED_RAW_SHA256 = "ca8cd8eee361b37bf9f91ff5744ad95c691249be28a636bf7fbffa58946eebaf"

missing = [str(p) for p in PARTS if not p.is_file()]
if missing:
    raise SystemExit("Missing progress chunk(s): " + ", ".join(missing))

gz = b"".join(p.read_bytes() for p in PARTS)
if hashlib.sha256(gz).hexdigest() != EXPECTED_GZ_SHA256:
    raise SystemExit("Compressed progress SHA256 mismatch")
raw = gzip.decompress(gz)
if hashlib.sha256(raw).hexdigest() != EXPECTED_RAW_SHA256:
    raise SystemExit("Restored CSV SHA256 mismatch")
OUT.write_bytes(raw)
print(f"Restored: {OUT}")
print(f"Rows: {sum(1 for _ in raw.splitlines()) - 1}")
print(f"SHA256: {EXPECTED_RAW_SHA256}")

#!/usr/bin/env python3
from pathlib import Path
import gzip
import hashlib

HERE = Path(__file__).resolve().parent
PARTS = [HERE / f"HIGH_FIRST_PROGRESS_B09.csv.gz.part{i:02d}" for i in range(1, 6)]
OUT = HERE / "HIGH_FIRST_PROGRESS_B09.csv"
EXPECTED_GZ_SHA256 = "718abe888377b7bc8339549a0d06d4e95f2fbecf4541bdef308f4dbf8c42a615"
EXPECTED_RAW_SHA256 = "cba3cf98a44d1fd97ba610d66e4b57cb9ca1af47bdc9fc3a09eae6ae79c01c23"

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

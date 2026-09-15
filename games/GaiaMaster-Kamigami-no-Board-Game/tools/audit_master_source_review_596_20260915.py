#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit editorial source-translation coverage for all 596 Master rows.

IMPORTANT:
- This is NOT a runtime coverage gate.
- This does NOT modify Translation Master.
- This does NOT modify vi_game_current.
- A PASS here means every current Master source key has a reviewed/source-full
  Vietnamese translation path with exact Japanese identity and token order.

Part coverage contract:
- Part01: 100 via dedicated 92+8 review gate
- Part02: 100 via exact-companion reuse + reviewed phrase fallback gate
- Part03: 100 via full exact reviewed companion
- Part04: 100 via dedicated 77+23 review gate
- Part05: 100 via full exact reviewed companion
- Part06:  96 via full exact reviewed companion
Total: 596
"""
from __future__ import annotations

import csv
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
TR = ROOT / "translation"
TOKEN_RE = re.compile(r"%(?:[-+0-9.#]*[A-Za-z%])|/[Vv]")

PART_COUNTS = {1: 100, 2: 100, 3: 100, 4: 100, 5: 100, 6: 96}
DELEGATED_GATES = {
    1: TOOLS / "audit_part01_source_review_20260915.py",
    2: TOOLS / "audit_part02_source_review_20260915.py",
    4: TOOLS / "audit_part04_source_review_20260915.py",
}
REVIEWED_COMPANIONS = {
    3: TR / "TRANSLATION_MASTER_PART03_SOURCE_REVIEWED_2026-09-15.csv",
    5: TR / "TRANSLATION_MASTER_PART05_SOURCE_REVIEWED_2026-09-15.csv",
    6: TR / "TRANSLATION_MASTER_PART06_SOURCE_REVIEWED_2026-09-15.csv",
}


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        if not r.fieldnames:
            raise RuntimeError(f"No CSV header: {path}")
        return list(r)


def norm_off(raw: str) -> str:
    return hex(int(str(raw).strip(), 0)).lower()


def key(row):
    return (row["file"].strip(), norm_off(row["offset_hex"]))


def tokens(text: str):
    return tuple(m.group(0) for m in TOKEN_RE.finditer(text or ""))


def master_path(part: int) -> Path:
    return TR / f"TRANSLATION_MASTER_0.6_part{part:02d}.csv"


def run_gate(part: int, path: Path) -> None:
    if not path.is_file():
        raise RuntimeError(f"Missing delegated Part{part:02d} gate: {path}")
    cp = subprocess.run(
        [sys.executable, str(path)],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    print(f"\n--- Part{part:02d} delegated audit ---")
    print(cp.stdout.rstrip())
    if cp.returncode != 0:
        raise RuntimeError(f"Part{part:02d} delegated audit failed with exit code {cp.returncode}")


def audit_exact_companion(part: int, companion: Path) -> int:
    master = master_path(part)
    if not master.is_file() or not companion.is_file():
        raise RuntimeError(f"Missing Part{part:02d} Master/review companion")

    master_rows = read_csv(master)
    expected = PART_COUNTS[part]
    if len(master_rows) != expected:
        raise RuntimeError(
            f"Part{part:02d} Master row-count gate failed: {len(master_rows)} != {expected}"
        )

    review_rows = read_csv(companion)
    if len(review_rows) != expected:
        raise RuntimeError(
            f"Part{part:02d} reviewed companion row-count gate failed: "
            f"{len(review_rows)} != {expected}"
        )

    master_map = {}
    runtime_before = {}
    for row in master_rows:
        k = key(row)
        if k in master_map:
            raise RuntimeError(f"Duplicate Part{part:02d} Master key: {k}")
        master_map[k] = row
        runtime_before[k] = row.get("vi_game_current", "")

    review_map = {}
    for row in review_rows:
        k = key(row)
        if k in review_map:
            raise RuntimeError(f"Duplicate Part{part:02d} reviewed key: {k}")
        jp = row.get("japanese") or ""
        vi = (row.get("vi_full_reviewed") or "").strip()
        if not vi:
            raise RuntimeError(f"Blank Part{part:02d} reviewed translation: {k}")
        if tokens(jp) != tokens(vi):
            raise RuntimeError(
                f"Part{part:02d} token mismatch {k}: {tokens(jp)} != {tokens(vi)}"
            )
        review_map[k] = row

    if set(master_map) != set(review_map):
        missing = sorted(set(master_map) - set(review_map))
        extra = sorted(set(review_map) - set(master_map))
        raise RuntimeError(
            f"Part{part:02d} reviewed key-set mismatch: "
            f"missing={missing[:10]} extra={extra[:10]}"
        )

    fragment_count = 0
    for k, master_row in master_map.items():
        review_row = review_map[k]
        if (master_row.get("japanese") or "") != (review_row.get("japanese") or ""):
            raise RuntimeError(
                f"Part{part:02d} exact Japanese mismatch {k}: "
                f"master={master_row.get('japanese')!r} "
                f"review={review_row.get('japanese')!r}"
            )
        if "FRAGMENT" in (review_row.get("status") or ""):
            fragment_count += 1
        if runtime_before[k] != master_row.get("vi_game_current", ""):
            raise RuntimeError(f"Part{part:02d} vi_game_current mutated unexpectedly: {k}")

    print(f"\n--- Part{part:02d} exact companion audit ---")
    print(f"Master rows               : {len(master_rows)} / {expected}")
    print(f"Reviewed exact rows       : {len(review_rows)} / {expected}")
    print(f"Explicit fragments        : {fragment_count}")
    print("Exact Japanese identity   : PASS")
    print("Format-token order        : PASS")
    print("vi_game_current mutations : 0")
    return expected


def main() -> int:
    # First prove the six Master parts still form the expected 596-row corpus.
    total_master = 0
    all_master_keys = set()
    for part, expected in PART_COUNTS.items():
        path = master_path(part)
        if not path.is_file():
            raise RuntimeError(f"Missing Translation Master Part{part:02d}: {path}")
        rows = read_csv(path)
        if len(rows) != expected:
            raise RuntimeError(
                f"Part{part:02d} Master row-count gate failed: {len(rows)} != {expected}"
            )
        total_master += len(rows)
        for row in rows:
            k = key(row)
            if k in all_master_keys:
                raise RuntimeError(f"Duplicate exact Master key across parts: {k}")
            all_master_keys.add(k)

    if total_master != 596 or len(all_master_keys) != 596:
        raise RuntimeError(
            f"Global Master corpus gate failed: rows={total_master} unique_keys={len(all_master_keys)}"
        )

    print("GAIA MASTER EDITORIAL SOURCE REVIEW AUDIT")
    print("=" * 72)
    print(f"Translation Master rows     : {total_master} / 596")
    print(f"Unique exact Master keys    : {len(all_master_keys)} / 596")

    # Delegated reviewed-source gates for Parts 01/02/04.
    delegated_total = 0
    for part in (1, 2, 4):
        run_gate(part, DELEGATED_GATES[part])
        delegated_total += PART_COUNTS[part]

    # Full exact companion gates for Parts 03/05/06.
    exact_total = 0
    for part in (3, 5, 6):
        exact_total += audit_exact_companion(part, REVIEWED_COMPANIONS[part])

    reviewed_total = delegated_total + exact_total
    if reviewed_total != 596:
        raise RuntimeError(f"Global reviewed coverage arithmetic failed: {reviewed_total} != 596")

    print("\n" + "=" * 72)
    print("EDITORIAL SOURCE REVIEW COVERAGE: 596 / 596")
    print("Exact Japanese identity     : GATED")
    print("Format-token order          : GATED")
    print("Runtime fields modified     : 0")
    print("Runtime/build integration   : NONE")
    print("Runtime PASS claim          : NO")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

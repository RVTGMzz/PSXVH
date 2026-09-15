#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit full source-level editorial coverage for Translation Master Part04.

This is a translation-source audit only. It never writes Master and never
changes vi_game_current.

Coverage is intentionally split:
- 77 rows that were blank vi_full and were reviewed in the completion overlay;
- 23 rows that already had old vi_full and are reviewed in a separate overlay.

The union must exactly equal all 100 Part04 source keys.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TR = ROOT / "translation"
MASTER = TR / "TRANSLATION_MASTER_0.6_part04.csv"
COMPLETION_REVIEW = TR / "TRANSLATION_COMPLETION_REVIEWED_COMBAT_ITEMS_2026-09-15.csv"
EXISTING_REVIEW = TR / "PART04_EXISTING_SOURCE_REVIEW_2026-09-15.csv"
TOKEN_RE = re.compile(r"%(?:[-+0-9.#]*[A-Za-z%])|/[Vv]")


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


def add_review(dst, row, vi_field: str, origin: str) -> None:
    k = key(row)
    jp = row.get("japanese") or ""
    vi = (row.get(vi_field) or "").strip()
    if not vi:
        raise RuntimeError(f"Blank reviewed translation: {origin} {k}")
    if tokens(jp) != tokens(vi):
        raise RuntimeError(
            f"Token mismatch {origin} {k}: {tokens(jp)} != {tokens(vi)}"
        )
    if k in dst:
        raise RuntimeError(f"Duplicate reviewed Part04 key: {k}")
    dst[k] = (jp, vi, origin)


def main() -> int:
    missing = [p for p in (MASTER, COMPLETION_REVIEW, EXISTING_REVIEW) if not p.is_file()]
    if missing:
        raise RuntimeError("Missing files:\n" + "\n".join(str(p) for p in missing))

    master_rows = read_csv(MASTER)
    if len(master_rows) != 100:
        raise RuntimeError(f"Part04 row-count gate failed: {len(master_rows)} != 100")

    master = {}
    runtime_before = {}
    for row in master_rows:
        k = key(row)
        if k in master:
            raise RuntimeError(f"Duplicate Master Part04 key: {k}")
        master[k] = row
        runtime_before[k] = row.get("vi_game_current", "")

    reviewed = {}
    completion_count = 0
    for row in read_csv(COMPLETION_REVIEW):
        if (row.get("source_queue") or "").strip() != "PART04":
            continue
        add_review(reviewed, row, "vi_full", COMPLETION_REVIEW.name)
        completion_count += 1

    existing_count = 0
    for row in read_csv(EXISTING_REVIEW):
        add_review(reviewed, row, "vi_full_reviewed", EXISTING_REVIEW.name)
        existing_count += 1

    if completion_count != 77:
        raise RuntimeError(f"Part04 completion-review gate failed: {completion_count} != 77")
    if existing_count != 23:
        raise RuntimeError(f"Part04 existing-review gate failed: {existing_count} != 23")
    if len(reviewed) != 100:
        raise RuntimeError(f"Part04 reviewed-union gate failed: {len(reviewed)} != 100")

    missing_keys = sorted(set(master) - set(reviewed))
    extra_keys = sorted(set(reviewed) - set(master))
    if missing_keys or extra_keys:
        raise RuntimeError(
            f"Part04 key-set mismatch: missing={missing_keys[:10]} extra={extra_keys[:10]}"
        )

    fragments = 0
    for k, (jp, _vi, _origin) in reviewed.items():
        row = master[k]
        if (row.get("japanese") or "") != jp:
            raise RuntimeError(
                f"Exact Japanese mismatch {k}: master={row.get('japanese')!r} review={jp!r}"
            )
        if runtime_before[k] != row.get("vi_game_current", ""):
            raise RuntimeError(f"Runtime field mutated unexpectedly: {k}")

    for row in read_csv(EXISTING_REVIEW):
        if "FRAGMENT" in (row.get("status") or ""):
            fragments += 1

    print("GAIA MASTER PART04 SOURCE REVIEW AUDIT")
    print("=" * 64)
    print(f"Master rows                  : {len(master_rows)} / 100")
    print(f"Reviewed completion rows     : {completion_count} / 77")
    print(f"Reviewed pre-existing rows   : {existing_count} / 23")
    print(f"Reviewed exact-key union     : {len(reviewed)} / 100")
    print(f"Explicit existing fragments  : {fragments}")
    print("Exact Japanese identity      : PASS")
    print("Format-token order           : PASS")
    print("vi_game_current mutations    : 0")
    print("Runtime/build integration    : NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

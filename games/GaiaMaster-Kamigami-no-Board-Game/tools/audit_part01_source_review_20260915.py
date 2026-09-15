#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit full source-level editorial coverage for Translation Master Part01.

Read-only translation-source audit. No Master/runtime writes.

Coverage:
- 92 rows that originally had blank vi_full, resolved through the reviewed
  repeat lexicon using exact Japanese identity;
- 8 rows that already had old vi_full, reviewed by exact file+offset.

The union must exactly equal all 100 Part01 source keys.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TR = ROOT / "translation"
MASTER = TR / "TRANSLATION_MASTER_0.6_part01.csv"
QUEUE = TR / "TRANSLATION_COMPLETION_QUEUE_01_PART01.csv"
LEXICON = TR / "TRANSLATION_COMPLETION_REVIEWED_REPEAT_LEXICON_2026-09-15.csv"
EXISTING = TR / "PART01_EXISTING_SOURCE_REVIEW_2026-09-15.csv"
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


def main() -> int:
    required = (MASTER, QUEUE, LEXICON, EXISTING)
    missing_files = [p for p in required if not p.is_file()]
    if missing_files:
        raise RuntimeError("Missing files:\n" + "\n".join(str(p) for p in missing_files))

    master_rows = read_csv(MASTER)
    if len(master_rows) != 100:
        raise RuntimeError(f"Part01 row-count gate failed: {len(master_rows)} != 100")
    master = {}
    runtime_before = {}
    for row in master_rows:
        k = key(row)
        if k in master:
            raise RuntimeError(f"Duplicate Part01 Master key: {k}")
        master[k] = row
        runtime_before[k] = row.get("vi_game_current", "")

    queue_rows = read_csv(QUEUE)
    if len(queue_rows) != 92:
        raise RuntimeError(f"Part01 completion queue gate failed: {len(queue_rows)} != 92")

    lex = {}
    for row in read_csv(LEXICON):
        jp = row.get("japanese") or ""
        vi = (row.get("vi_full") or "").strip()
        if not jp or not vi:
            raise RuntimeError(f"Blank reviewed lexicon row: {row}")
        if jp in lex and lex[jp] != vi:
            raise RuntimeError(f"Conflicting reviewed lexicon translation for {jp!r}")
        lex[jp] = vi

    reviewed = {}
    for row in queue_rows:
        k = key(row)
        jp = row.get("japanese") or ""
        vi = lex.get(jp)
        if vi is None:
            raise RuntimeError(f"Part01 queue phrase missing reviewed lexicon entry: {k} {jp!r}")
        if tokens(jp) != tokens(vi):
            raise RuntimeError(f"Part01 lexicon token mismatch {k}: {tokens(jp)} != {tokens(vi)}")
        reviewed[k] = (jp, vi, LEXICON.name)

    existing_rows = read_csv(EXISTING)
    if len(existing_rows) != 8:
        raise RuntimeError(f"Part01 existing-review gate failed: {len(existing_rows)} != 8")
    for row in existing_rows:
        k = key(row)
        jp = row.get("japanese") or ""
        vi = (row.get("vi_full_reviewed") or "").strip()
        if not vi:
            raise RuntimeError(f"Blank Part01 exact review: {k}")
        if tokens(jp) != tokens(vi):
            raise RuntimeError(f"Part01 exact-review token mismatch {k}: {tokens(jp)} != {tokens(vi)}")
        if k in reviewed:
            raise RuntimeError(f"Part01 queue/existing overlap: {k}")
        reviewed[k] = (jp, vi, EXISTING.name)

    if len(reviewed) != 100:
        raise RuntimeError(f"Part01 reviewed-union gate failed: {len(reviewed)} != 100")
    missing = sorted(set(master) - set(reviewed))
    extra = sorted(set(reviewed) - set(master))
    if missing or extra:
        raise RuntimeError(f"Part01 key-set mismatch: missing={missing[:10]} extra={extra[:10]}")

    for k, (jp, _vi, _origin) in reviewed.items():
        row = master[k]
        if (row.get("japanese") or "") != jp:
            raise RuntimeError(
                f"Part01 exact Japanese mismatch {k}: master={row.get('japanese')!r} review={jp!r}"
            )
        if runtime_before[k] != row.get("vi_game_current", ""):
            raise RuntimeError(f"Part01 vi_game_current mutated unexpectedly: {k}")

    print("GAIA MASTER PART01 SOURCE REVIEW AUDIT")
    print("=" * 64)
    print(f"Master rows                 : {len(master_rows)} / 100")
    print(f"Reviewed queue rows         : {len(queue_rows)} / 92")
    print(f"Reviewed existing rows      : {len(existing_rows)} / 8")
    print(f"Reviewed exact-key union    : {len(reviewed)} / 100")
    print("Exact Japanese identity     : PASS")
    print("Format-token order          : PASS")
    print("vi_game_current mutations   : 0")
    print("Runtime/build integration   : NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

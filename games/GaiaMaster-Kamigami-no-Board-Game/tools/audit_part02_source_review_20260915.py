#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit Translation Master Part02 against reviewed source companions.

Read-only translation-source audit. No Master/runtime writes.

Priority:
1. exact Batch40 source-full companion by file + offset + exact Japanese;
2. reviewed repeat lexicon by exact Japanese, only if no exact companion exists.

The intent is to reuse already-reviewed source translations instead of
creating another 100-row duplicate companion.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TR = ROOT / "translation"
MASTER = TR / "TRANSLATION_MASTER_0.6_part02.csv"
LEXICON = TR / "TRANSLATION_COMPLETION_REVIEWED_REPEAT_LEXICON_2026-09-15.csv"
BATCH40_GLOB = "BATCH40_SOURCE_FULL_*_2026-09-15.csv"
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
    if not MASTER.is_file() or not LEXICON.is_file():
        raise RuntimeError("Missing Part02 Master or reviewed repeat lexicon")

    source_files = sorted(TR.glob(BATCH40_GLOB))
    if not source_files:
        raise RuntimeError("No Batch40 source-full companions found")

    master_rows = read_csv(MASTER)
    if len(master_rows) != 100:
        raise RuntimeError(f"Part02 row-count gate failed: {len(master_rows)} != 100")

    exact = {}
    exact_conflicts = []
    for path in source_files:
        for row in read_csv(path):
            if not {"file", "offset_hex", "japanese", "vi_full"}.issubset(row):
                continue
            k = key(row)
            jp = row.get("japanese") or ""
            vi = (row.get("vi_full") or "").strip()
            if not vi:
                continue
            item = (jp, vi, path.name)
            old = exact.get(k)
            if old is not None and old[:2] != item[:2]:
                exact_conflicts.append((k, old, item))
                continue
            exact[k] = item
    if exact_conflicts:
        raise RuntimeError(f"Batch40 exact companion conflicts: {exact_conflicts[:5]}")

    lex = {}
    for row in read_csv(LEXICON):
        jp = row.get("japanese") or ""
        vi = (row.get("vi_full") or "").strip()
        if not jp or not vi:
            raise RuntimeError(f"Blank repeat lexicon row: {row}")
        if jp in lex and lex[jp] != vi:
            raise RuntimeError(f"Conflicting repeat lexicon translation: {jp!r}")
        lex[jp] = vi

    exact_used = []
    lex_used = []
    missing = []
    token_fail = []
    runtime_snapshot = []

    for row in master_rows:
        k = key(row)
        jp = row.get("japanese") or ""
        runtime_snapshot.append((k, row.get("vi_game_current", "")))

        chosen = None
        item = exact.get(k)
        if item is not None:
            src_jp, vi, origin = item
            if src_jp != jp:
                raise RuntimeError(
                    f"Exact source mismatch {k}: master={jp!r} companion={src_jp!r}"
                )
            chosen = (vi, origin)
            exact_used.append((k, origin))
        elif jp in lex:
            chosen = (lex[jp], LEXICON.name)
            lex_used.append(k)
        else:
            missing.append((k, jp))
            continue

        vi, origin = chosen
        if tokens(jp) != tokens(vi):
            token_fail.append((k, jp, vi, origin, tokens(jp), tokens(vi)))

    if token_fail:
        raise RuntimeError(f"Part02 token mismatch: {token_fail[:5]}")
    if missing:
        raise RuntimeError(f"Part02 reviewed-source gaps: {missing[:20]}")

    # Read-only script: this should remain tautologically unchanged, but retain
    # the snapshot as an explicit contract statement for future refactors.
    runtime_after = [(key(r), r.get("vi_game_current", "")) for r in master_rows]
    if runtime_snapshot != runtime_after:
        raise RuntimeError("Part02 vi_game_current mutated unexpectedly")

    print("GAIA MASTER PART02 SOURCE REVIEW REUSE AUDIT")
    print("=" * 68)
    print(f"Master rows                : {len(master_rows)} / 100")
    print(f"Batch40 exact companions   : {len(exact_used)}")
    print(f"Repeat-lexicon fallbacks   : {len(lex_used)}")
    print(f"Missing reviewed source    : {len(missing)}")
    print("Exact Japanese identity    : PASS")
    print("Format-token order         : PASS")
    print("vi_game_current mutations  : 0")
    print("Runtime/build integration  : NONE")
    print("Reviewed source coverage   : 100 / 100")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit Translation Master Part02 against reviewed source companions.

Read-only translation-source audit. No Master/runtime writes.

Exact-source priority, highest first:
1. dedicated Part02 reviewed gap patch;
2. exact completion-review companion;
3. Master-only exact source companion;
4. Batch43 source-full companions;
5. Batch40 source-full companions;
6. reviewed repeat lexicon by Japanese phrase, only if no exact companion exists.

Multiple exact companions may intentionally contain different editorial wording.
That is not a source conflict when file + offset + Japanese identity agree: the
higher-priority reviewed source wins. A different Japanese source at the same
exact key remains a hard error.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TR = ROOT / "translation"
MASTER = TR / "TRANSLATION_MASTER_0.6_part02.csv"
LEXICON = TR / "TRANSLATION_COMPLETION_REVIEWED_REPEAT_LEXICON_2026-09-15.csv"
PART02_GAPS = TR / "PART02_SOURCE_REVIEW_GAPS_2026-09-15.csv"
COMPLETION_EXACT = TR / "TRANSLATION_COMPLETION_REVIEWED_COMBAT_ITEMS_2026-09-15.csv"
MASTER_ONLY = TR / "MASTER_ONLY_EXACT_GAMEPLAY_SOURCE_FULL_2026-09-15.csv"
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


def exact_source_files():
    files = []
    if PART02_GAPS.is_file():
        files.append((PART02_GAPS, "part02-gap-review", "vi_full_reviewed"))
    if COMPLETION_EXACT.is_file():
        files.append((COMPLETION_EXACT, "completion-reviewed", "vi_full"))
    if MASTER_ONLY.is_file():
        files.append((MASTER_ONLY, "master-only", "vi_full"))
    files.extend(
        (p, "batch43", "vi_full")
        for p in sorted(TR.glob("BATCH43_SOURCE_FULL_*_2026-09-15.csv"))
    )
    files.extend(
        (p, "batch40", "vi_full")
        for p in sorted(TR.glob("BATCH40_SOURCE_FULL_*_2026-09-15.csv"))
    )
    return files


def main() -> int:
    if not MASTER.is_file() or not LEXICON.is_file():
        raise RuntimeError("Missing Part02 Master or reviewed repeat lexicon")

    source_files = exact_source_files()
    if not source_files:
        raise RuntimeError("No reviewed exact source companions found")

    master_rows = read_csv(MASTER)
    if len(master_rows) != 100:
        raise RuntimeError(f"Part02 row-count gate failed: {len(master_rows)} != 100")

    exact = {}
    for path, source_class, vi_field in source_files:
        for row in read_csv(path):
            if not {"file", "offset_hex", "japanese", vi_field}.issubset(row):
                continue
            k = key(row)
            jp = row.get("japanese") or ""
            vi = (row.get(vi_field) or "").strip()
            if not vi:
                continue
            old = exact.get(k)
            if old is not None:
                if old[0] != jp:
                    raise RuntimeError(
                        f"Exact companion Japanese conflict {k}: "
                        f"{old[0]!r} from {old[2]} != {jp!r} from {path.name}"
                    )
                continue
            exact[k] = (jp, vi, path.name, source_class)

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
    source_class_counts = {}
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
            src_jp, vi, origin, source_class = item
            if src_jp != jp:
                raise RuntimeError(
                    f"Exact source mismatch {k}: master={jp!r} companion={src_jp!r}"
                )
            chosen = (vi, origin)
            exact_used.append((k, origin))
            source_class_counts[source_class] = source_class_counts.get(source_class, 0) + 1
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

    runtime_after = [(key(r), r.get("vi_game_current", "")) for r in master_rows]
    if runtime_snapshot != runtime_after:
        raise RuntimeError("Part02 vi_game_current mutated unexpectedly")

    print("GAIA MASTER PART02 SOURCE REVIEW REUSE AUDIT")
    print("=" * 68)
    print(f"Master rows                : {len(master_rows)} / 100")
    print(f"Exact-source companions    : {len(exact_used)}")
    for source_class in (
        "part02-gap-review",
        "completion-reviewed",
        "master-only",
        "batch43",
        "batch40",
    ):
        print(f"  {source_class:20s}: {source_class_counts.get(source_class, 0)}")
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

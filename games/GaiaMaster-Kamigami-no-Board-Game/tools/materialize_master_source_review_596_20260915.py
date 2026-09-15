#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Materialize the proven 596-row editorial source review into Master vi_full.

Default mode is DRY-RUN. Use --write to update only the `vi_full` column of the
six Translation Master parts.

Hard safety contract:
- exact file + offset + Japanese identity for every row;
- format-token count/order preserved;
- exactly 596 reviewed source keys required;
- `vi_game_current` is NEVER changed;
- every field except `vi_full` must remain byte-for-byte equivalent as parsed
  CSV data before/after materialization;
- this is source translation integration only, NOT runtime integration.
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TR = ROOT / "translation"
TOKEN_RE = re.compile(r"%(?:[-+0-9.#]*[A-Za-z%])|/[Vv]")
PART_COUNTS = {1: 100, 2: 100, 3: 100, 4: 100, 5: 100, 6: 96}
MASTER_PARTS = {
    part: TR / f"TRANSLATION_MASTER_0.6_part{part:02d}.csv"
    for part in PART_COUNTS
}

LEXICON = TR / "TRANSLATION_COMPLETION_REVIEWED_REPEAT_LEXICON_2026-09-15.csv"
PART01_QUEUE = TR / "TRANSLATION_COMPLETION_QUEUE_01_PART01.csv"
PART01_EXISTING = TR / "PART01_EXISTING_SOURCE_REVIEW_2026-09-15.csv"
PART02_GAPS = TR / "PART02_SOURCE_REVIEW_GAPS_2026-09-15.csv"
COMPLETION_EXACT = TR / "TRANSLATION_COMPLETION_REVIEWED_COMBAT_ITEMS_2026-09-15.csv"
MASTER_ONLY = TR / "MASTER_ONLY_EXACT_GAMEPLAY_SOURCE_FULL_2026-09-15.csv"
PART04_EXISTING = TR / "PART04_EXISTING_SOURCE_REVIEW_2026-09-15.csv"
DIRECT_REVIEW = {
    3: TR / "TRANSLATION_MASTER_PART03_SOURCE_REVIEWED_2026-09-15.csv",
    5: TR / "TRANSLATION_MASTER_PART05_SOURCE_REVIEWED_2026-09-15.csv",
    6: TR / "TRANSLATION_MASTER_PART06_SOURCE_REVIEWED_2026-09-15.csv",
}


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        if not r.fieldnames:
            raise RuntimeError(f"No CSV header: {path}")
        return list(r.fieldnames), list(r)


def write_csv(path: Path, fields, rows) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def norm_off(raw: str) -> str:
    return hex(int(str(raw).strip(), 0)).lower()


def key(row):
    return (row["file"].strip(), norm_off(row["offset_hex"]))


def tokens(text: str):
    return tuple(m.group(0) for m in TOKEN_RE.finditer(text or ""))


def add_review(dst, row, vi_field: str, origin: str, *, overwrite=False) -> None:
    k = key(row)
    jp = row.get("japanese") or ""
    vi = (row.get(vi_field) or "").strip()
    if not vi:
        raise RuntimeError(f"Blank reviewed source: {origin} {k}")
    if tokens(jp) != tokens(vi):
        raise RuntimeError(
            f"Token mismatch {origin} {k}: {tokens(jp)} != {tokens(vi)}"
        )
    old = dst.get(k)
    if old is not None and not overwrite:
        if old[0] != jp:
            raise RuntimeError(
                f"Japanese conflict {k}: {old[0]!r} from {old[2]} != {jp!r} from {origin}"
            )
        return
    if old is not None and old[0] != jp:
        raise RuntimeError(
            f"Japanese conflict {k}: {old[0]!r} from {old[2]} != {jp!r} from {origin}"
        )
    dst[k] = (jp, vi, origin)


def load_lexicon():
    _fields, rows = read_csv(LEXICON)
    out = {}
    for row in rows:
        jp = row.get("japanese") or ""
        vi = (row.get("vi_full") or "").strip()
        if not jp or not vi:
            raise RuntimeError(f"Blank reviewed repeat lexicon row: {row}")
        if tokens(jp) != tokens(vi):
            raise RuntimeError(f"Repeat lexicon token mismatch: {jp!r}")
        if jp in out and out[jp] != vi:
            raise RuntimeError(f"Conflicting repeat lexicon entry: {jp!r}")
        out[jp] = vi
    return out


def build_part01_review(lex):
    out = {}
    _fields, queue = read_csv(PART01_QUEUE)
    if len(queue) != 92:
        raise RuntimeError(f"Part01 queue gate failed: {len(queue)} != 92")
    for row in queue:
        jp = row.get("japanese") or ""
        vi = lex.get(jp)
        if vi is None:
            raise RuntimeError(f"Part01 queue phrase missing reviewed lexicon: {key(row)} {jp!r}")
        temp = dict(row)
        temp["vi_full_materialized"] = vi
        add_review(out, temp, "vi_full_materialized", LEXICON.name)

    _fields, existing = read_csv(PART01_EXISTING)
    if len(existing) != 8:
        raise RuntimeError(f"Part01 existing-review gate failed: {len(existing)} != 8")
    for row in existing:
        add_review(out, row, "vi_full_reviewed", PART01_EXISTING.name)
    if len(out) != 100:
        raise RuntimeError(f"Part01 reviewed union failed: {len(out)} != 100")
    return out


def part02_exact_sources():
    sources = []
    if PART02_GAPS.is_file():
        sources.append((PART02_GAPS, "vi_full_reviewed"))
    if COMPLETION_EXACT.is_file():
        sources.append((COMPLETION_EXACT, "vi_full"))
    if MASTER_ONLY.is_file():
        sources.append((MASTER_ONLY, "vi_full"))
    sources.extend((p, "vi_full") for p in sorted(TR.glob("BATCH43_SOURCE_FULL_*_2026-09-15.csv")))
    sources.extend((p, "vi_full") for p in sorted(TR.glob("BATCH40_SOURCE_FULL_*_2026-09-15.csv")))
    return sources


def build_part02_review(master_rows, lex):
    # Highest-priority exact source wins. Lower-priority wording for the same
    # exact Japanese source is intentionally ignored.
    exact = {}
    for path, vi_field in part02_exact_sources():
        _fields, rows = read_csv(path)
        for row in rows:
            if not {"file", "offset_hex", "japanese", vi_field}.issubset(row):
                continue
            add_review(exact, row, vi_field, path.name)

    out = {}
    for row in master_rows:
        k = key(row)
        jp = row.get("japanese") or ""
        item = exact.get(k)
        if item is not None:
            src_jp, vi, origin = item
            if src_jp != jp:
                raise RuntimeError(
                    f"Part02 exact source mismatch {k}: master={jp!r} review={src_jp!r}"
                )
            out[k] = item
        elif jp in lex:
            vi = lex[jp]
            if tokens(jp) != tokens(vi):
                raise RuntimeError(f"Part02 lexicon token mismatch: {k}")
            out[k] = (jp, vi, LEXICON.name)
        else:
            raise RuntimeError(f"Part02 missing reviewed source: {k} {jp!r}")
    if len(out) != 100:
        raise RuntimeError(f"Part02 reviewed union failed: {len(out)} != 100")
    return out


def build_part04_review():
    out = {}
    _fields, completion = read_csv(COMPLETION_EXACT)
    for row in completion:
        if (row.get("source_queue") or "").strip() != "PART04":
            continue
        add_review(out, row, "vi_full", COMPLETION_EXACT.name)
    if len(out) != 77:
        raise RuntimeError(f"Part04 completion-review gate failed: {len(out)} != 77")

    _fields, existing = read_csv(PART04_EXISTING)
    if len(existing) != 23:
        raise RuntimeError(f"Part04 existing-review gate failed: {len(existing)} != 23")
    for row in existing:
        add_review(out, row, "vi_full_reviewed", PART04_EXISTING.name)
    if len(out) != 100:
        raise RuntimeError(f"Part04 reviewed union failed: {len(out)} != 100")
    return out


def build_direct_review(part: int):
    path = DIRECT_REVIEW[part]
    _fields, rows = read_csv(path)
    expected = PART_COUNTS[part]
    if len(rows) != expected:
        raise RuntimeError(f"Part{part:02d} direct-review gate failed: {len(rows)} != {expected}")
    out = {}
    for row in rows:
        add_review(out, row, "vi_full_reviewed", path.name)
    if len(out) != expected:
        raise RuntimeError(f"Part{part:02d} reviewed key union failed: {len(out)} != {expected}")
    return out


def non_vi_full_projection(fields, rows):
    keep = [f for f in fields if f != "vi_full"]
    return [tuple(row.get(f, "") for f in keep) for row in rows]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="replace Master vi_full with reviewed source text")
    args = ap.parse_args()

    required = [LEXICON, PART01_QUEUE, PART01_EXISTING, PART02_GAPS, COMPLETION_EXACT,
                MASTER_ONLY, PART04_EXISTING, *MASTER_PARTS.values(), *DIRECT_REVIEW.values()]
    missing = [p for p in required if not p.is_file()]
    if missing:
        raise RuntimeError("Missing required files:\n" + "\n".join(str(p) for p in missing))

    lex = load_lexicon()
    masters = {}
    total_rows = 0
    all_keys = set()
    for part, path in MASTER_PARTS.items():
        fields, rows = read_csv(path)
        expected = PART_COUNTS[part]
        if len(rows) != expected:
            raise RuntimeError(f"Part{part:02d} row-count gate failed: {len(rows)} != {expected}")
        if "vi_full" not in fields or "vi_game_current" not in fields:
            raise RuntimeError(f"Unexpected Master schema: {path.name}")
        for row in rows:
            k = key(row)
            if k in all_keys:
                raise RuntimeError(f"Duplicate Master exact key across parts: {k}")
            all_keys.add(k)
        total_rows += len(rows)
        masters[part] = (path, fields, rows)

    if total_rows != 596 or len(all_keys) != 596:
        raise RuntimeError(f"Master corpus gate failed: rows={total_rows} keys={len(all_keys)}")

    reviews = {
        1: build_part01_review(lex),
        2: build_part02_review(masters[2][2], lex),
        3: build_direct_review(3),
        4: build_part04_review(),
        5: build_direct_review(5),
        6: build_direct_review(6),
    }

    reviewed_union = set()
    for part, review in reviews.items():
        expected = PART_COUNTS[part]
        if len(review) != expected:
            raise RuntimeError(f"Part{part:02d} review count failed: {len(review)} != {expected}")
        overlap = reviewed_union & set(review)
        if overlap:
            raise RuntimeError(f"Duplicate reviewed key across parts: {sorted(overlap)[:10]}")
        reviewed_union.update(review)
    if reviewed_union != all_keys:
        missing_review = sorted(all_keys - reviewed_union)
        extra_review = sorted(reviewed_union - all_keys)
        raise RuntimeError(
            f"Reviewed 596 key-set mismatch: missing={missing_review[:10]} extra={extra_review[:10]}"
        )

    blank_before = 0
    identical_before = 0
    editorial_change = 0
    changed_by_part = {}
    original_non_full = {}
    runtime_before = {}

    for part, (path, fields, rows) in masters.items():
        original_non_full[part] = non_vi_full_projection(fields, rows)
        runtime_before[part] = [r.get("vi_game_current", "") for r in rows]
        changed = 0
        for row in rows:
            k = key(row)
            jp = row.get("japanese") or ""
            src_jp, reviewed_vi, origin = reviews[part][k]
            if src_jp != jp:
                raise RuntimeError(
                    f"Exact Japanese mismatch Part{part:02d} {k}: master={jp!r} review={src_jp!r}"
                )
            if tokens(jp) != tokens(reviewed_vi):
                raise RuntimeError(
                    f"Token mismatch Part{part:02d} {k}: {tokens(jp)} != {tokens(reviewed_vi)}"
                )
            old = (row.get("vi_full") or "").strip()
            if not old:
                blank_before += 1
            elif old == reviewed_vi:
                identical_before += 1
            else:
                editorial_change += 1
            if old != reviewed_vi:
                changed += 1
            row["vi_full"] = reviewed_vi
        changed_by_part[part] = changed

        if non_vi_full_projection(fields, rows) != original_non_full[part]:
            raise RuntimeError(f"Non-vi_full field mutation detected in Part{part:02d}")
        if [r.get("vi_game_current", "") for r in rows] != runtime_before[part]:
            raise RuntimeError(f"vi_game_current mutation detected in Part{part:02d}")

    changed_total = sum(changed_by_part.values())

    print("GAIA MASTER MATERIALIZE EDITORIAL SOURCE REVIEW 596")
    print("=" * 72)
    print(f"Master exact rows           : {total_rows} / 596")
    print(f"Reviewed exact keys         : {len(reviewed_union)} / 596")
    print(f"Blank vi_full before        : {blank_before}")
    print(f"Already identical           : {identical_before}")
    print(f"Editorial replacements      : {editorial_change}")
    print(f"Rows changed in vi_full     : {changed_total}")
    for part in range(1, 7):
        print(f"  Part{part:02d} changes            : {changed_by_part[part]}")
    print("Non-vi_full field changes   : 0")
    print("vi_game_current changes     : 0")
    print("Runtime/build integration   : NONE")
    print(f"Mode                        : {'WRITE' if args.write else 'DRY-RUN'}")

    if args.write:
        for part, (path, fields, rows) in masters.items():
            write_csv(path, fields, rows)

        # Re-read from disk and prove the only parsed-field differences are vi_full.
        for part, (path, fields, _rows) in masters.items():
            new_fields, new_rows = read_csv(path)
            if new_fields != fields:
                raise RuntimeError(f"Master schema changed after write: Part{part:02d}")
            if non_vi_full_projection(new_fields, new_rows) != original_non_full[part]:
                raise RuntimeError(f"Post-write non-vi_full mutation: Part{part:02d}")
            if [r.get("vi_game_current", "") for r in new_rows] != runtime_before[part]:
                raise RuntimeError(f"Post-write vi_game_current mutation: Part{part:02d}")
            if any(not (r.get("vi_full") or "").strip() for r in new_rows):
                raise RuntimeError(f"Post-write blank vi_full remains: Part{part:02d}")
        print("WRITE VERIFY                : PASS")
    else:
        print("WRITE VERIFY                : not executed")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

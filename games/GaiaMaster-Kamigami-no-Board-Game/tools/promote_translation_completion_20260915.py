#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Promote the 2026-09-15 source-translation completion queues into Master.

Safety contract:
- source text only: NEVER changes vi_game_current;
- exact identity required: file + offset + Japanese source;
- format token count/order must remain identical;
- existing non-empty vi_full is never overwritten;
- dry-run by default; --write is explicit.

Editorial priority:
1. prepared exact completion queues establish the 203 target keys;
2. reviewed repeat lexicon normalizes repeated tavern/settings source text;
3. reviewed exact combat/item/prompt overlay wins for its exact keys.
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TR = ROOT / "translation"
MASTER_PARTS = [TR / f"TRANSLATION_MASTER_0.6_part{i:02d}.csv" for i in range(1, 7)]
QUEUE_FILES = [
    TR / "TRANSLATION_COMPLETION_QUEUE_01_PART01.csv",
    TR / "TRANSLATION_COMPLETION_QUEUE_02_PART02.csv",
    TR / "TRANSLATION_COMPLETION_QUEUE_03_PART03.csv",
    TR / "TRANSLATION_COMPLETION_QUEUE_04_PART04.csv",
    TR / "TRANSLATION_COMPLETION_QUEUE_05_PART06.csv",
]
REPEAT_LEXICON = TR / "TRANSLATION_COMPLETION_REVIEWED_REPEAT_LEXICON_2026-09-15.csv"
REVIEWED_EXACT = TR / "TRANSLATION_COMPLETION_REVIEWED_COMBAT_ITEMS_2026-09-15.csv"
TOKEN_RE = re.compile(r"%(?:[-+0-9.#]*[A-Za-z%])|/[Vv]")


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


def load_repeat_lexicon():
    _fields, rows = read_csv(REPEAT_LEXICON)
    out = {}
    for r in rows:
        jp = r.get("japanese") or ""
        vi = (r.get("vi_full") or "").strip()
        if not jp or not vi:
            raise RuntimeError(f"Blank repeat lexicon row in {REPEAT_LEXICON.name}: {r}")
        if jp in out and out[jp] != vi:
            raise RuntimeError(f"Conflicting repeat lexicon translation for {jp!r}")
        if tokens(jp) != tokens(vi):
            raise RuntimeError(
                f"Token mismatch in {REPEAT_LEXICON.name} {jp!r}: "
                f"{tokens(jp)} != {tokens(vi)}"
            )
        out[jp] = vi
    return out


def load_overlay():
    overlay = {}
    origin = {}

    # Base exact-key target set. These five files must stay at 203 unique keys.
    for path in QUEUE_FILES:
        _fields, rows = read_csv(path)
        for r in rows:
            k = key(r)
            jp = r.get("japanese") or ""
            vi = (r.get("vi_full") or "").strip()
            if not vi:
                raise RuntimeError(f"Blank prepared translation: {path.name} {k}")
            if tokens(jp) != tokens(vi):
                raise RuntimeError(
                    f"Token mismatch in {path.name} {k}: {tokens(jp)} != {tokens(vi)}"
                )
            if k in overlay and overlay[k][0] != jp:
                raise RuntimeError(f"Conflicting Japanese source for {k}")
            overlay[k] = (jp, vi)
            origin[k] = path.name

    if len(overlay) != 203:
        raise RuntimeError(f"Prepared completion key gate failed: {len(overlay)} != 203")

    # Normalize every repeated source phrase through one reviewed translation.
    lexicon = load_repeat_lexicon()
    lexicon_used = set()
    repeat_replaced = 0
    for k, (jp, old_vi) in list(overlay.items()):
        new_vi = lexicon.get(jp)
        if new_vi is None:
            continue
        overlay[k] = (jp, new_vi)
        origin[k] = REPEAT_LEXICON.name
        lexicon_used.add(jp)
        repeat_replaced += 1

    unused_lexicon = sorted(set(lexicon) - lexicon_used)
    if unused_lexicon:
        raise RuntimeError(
            "Reviewed repeat lexicon contains unused Japanese source rows: "
            + repr(unused_lexicon[:10])
        )

    # Explicitly reviewed exact wording wins last for its 80 selected keys.
    _fields, rows = read_csv(REVIEWED_EXACT)
    reviewed_exact_keys = set()
    for r in rows:
        k = key(r)
        jp = r.get("japanese") or ""
        vi = (r.get("vi_full") or "").strip()
        if not vi:
            raise RuntimeError(f"Blank reviewed translation: {REVIEWED_EXACT.name} {k}")
        if tokens(jp) != tokens(vi):
            raise RuntimeError(
                f"Token mismatch in {REVIEWED_EXACT.name} {k}: {tokens(jp)} != {tokens(vi)}"
            )
        if k not in overlay:
            raise RuntimeError(f"Reviewed key not present in completion queues: {k}")
        if overlay[k][0] != jp:
            raise RuntimeError(f"Reviewed Japanese mismatch for {k}")
        overlay[k] = (jp, vi)
        origin[k] = REVIEWED_EXACT.name
        reviewed_exact_keys.add(k)

    if len(reviewed_exact_keys) != 80:
        raise RuntimeError(f"Reviewed exact key gate failed: {len(reviewed_exact_keys)} != 80")
    if len(overlay) != 203:
        raise RuntimeError(f"Completion overlay gate failed: {len(overlay)} != 203")

    return overlay, origin, len(lexicon), repeat_replaced, len(reviewed_exact_keys)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="write promoted vi_full values into Master")
    args = ap.parse_args()

    required = [*MASTER_PARTS, *QUEUE_FILES, REPEAT_LEXICON, REVIEWED_EXACT]
    missing = [p for p in required if not p.is_file()]
    if missing:
        raise RuntimeError("Missing files:\n" + "\n".join(str(p) for p in missing))

    overlay, origin, lexicon_count, repeat_replaced, reviewed_exact_count = load_overlay()
    matched = set()
    promoted = []
    already_same = []
    existing_different = []
    masters = {}

    for path in MASTER_PARTS:
        fields, rows = read_csv(path)
        if "vi_full" not in fields or "vi_game_current" not in fields:
            raise RuntimeError(f"Unexpected Master schema: {path.name}")
        before_runtime = [r.get("vi_game_current", "") for r in rows]

        for r in rows:
            k = key(r)
            item = overlay.get(k)
            if item is None:
                continue
            source_jp, new_vi = item
            if (r.get("japanese") or "") != source_jp:
                raise RuntimeError(
                    f"Exact source mismatch {path.name} {k}: "
                    f"master={r.get('japanese')!r} overlay={source_jp!r}"
                )
            matched.add(k)
            old = (r.get("vi_full") or "").strip()
            if not old:
                r["vi_full"] = new_vi
                promoted.append((path.name, k, origin[k]))
            elif old == new_vi:
                already_same.append((path.name, k))
            else:
                # Source pass is non-destructive. Never silently replace prior editorial work.
                existing_different.append((path.name, k, old, new_vi, origin[k]))

        after_runtime = [r.get("vi_game_current", "") for r in rows]
        if before_runtime != after_runtime:
            raise RuntimeError(f"vi_game_current mutated unexpectedly in {path.name}")
        masters[path] = (fields, rows)

    not_found = sorted(set(overlay) - matched)
    if not_found:
        raise RuntimeError(f"Overlay keys missing from Master: {not_found[:10]}")

    print("GAIA MASTER SOURCE TRANSLATION COMPLETION PROMOTION")
    print("=" * 72)
    print(f"Overlay exact keys       : {len(overlay)} / 203")
    print(f"Reviewed repeat phrases : {lexicon_count}")
    print(f"Exact keys normalized    : {repeat_replaced}")
    print(f"Reviewed exact keys      : {reviewed_exact_count} / 80")
    print(f"Matched in Master        : {len(matched)} / 203")
    print(f"Blank vi_full promoted   : {len(promoted)}")
    print(f"Already identical        : {len(already_same)}")
    print(f"Existing different kept  : {len(existing_different)}")
    print("Runtime fields changed   : 0")
    print(f"Mode                     : {'WRITE' if args.write else 'DRY-RUN'}")

    if existing_different:
        print("\nExisting editorial translations preserved:")
        for part, k, old, new, src in existing_different[:40]:
            print(f"- {part} {k}: keep={old!r} candidate={new!r} source={src}")

    if args.write:
        for path, (fields, rows) in masters.items():
            write_csv(path, fields, rows)
        print("\nWRITE COMPLETE: only previously blank vi_full cells were filled.")
    else:
        print("\nDry-run only. Re-run with --write after reviewing this report.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Promote the 2026-09-15 source-translation completion queues into Master.

Safety contract:
- source text only: NEVER changes vi_game_current;
- exact identity required: file + offset + Japanese source;
- format token count/order must remain identical;
- existing non-empty vi_full is never overwritten;
- dry-run by default; --write is explicit.

The reviewed combat/item overlay has priority over the earlier prepared queue
for the same exact source key.
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
REVIEWED = TR / "TRANSLATION_COMPLETION_REVIEWED_COMBAT_ITEMS_2026-09-15.csv"
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


def load_overlay():
    overlay = {}
    origin = {}

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

    # Explicitly reviewed wording wins for the same exact key.
    _fields, rows = read_csv(REVIEWED)
    for r in rows:
        k = key(r)
        jp = r.get("japanese") or ""
        vi = (r.get("vi_full") or "").strip()
        if not vi:
            raise RuntimeError(f"Blank reviewed translation: {REVIEWED.name} {k}")
        if tokens(jp) != tokens(vi):
            raise RuntimeError(
                f"Token mismatch in {REVIEWED.name} {k}: {tokens(jp)} != {tokens(vi)}"
            )
        if k not in overlay:
            raise RuntimeError(f"Reviewed key not present in completion queues: {k}")
        if overlay[k][0] != jp:
            raise RuntimeError(f"Reviewed Japanese mismatch for {k}")
        overlay[k] = (jp, vi)
        origin[k] = REVIEWED.name

    if len(overlay) != 203:
        raise RuntimeError(f"Completion overlay gate failed: {len(overlay)} != 203")
    return overlay, origin


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="write promoted vi_full values into Master")
    args = ap.parse_args()

    missing = [p for p in [*MASTER_PARTS, *QUEUE_FILES, REVIEWED] if not p.is_file()]
    if missing:
        raise RuntimeError("Missing files:\n" + "\n".join(str(p) for p in missing))

    overlay, origin = load_overlay()
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
    print(f"Matched in Master        : {len(matched)} / 203")
    print(f"Blank vi_full promoted   : {len(promoted)}")
    print(f"Already identical        : {len(already_same)}")
    print(f"Existing different kept  : {len(existing_different)}")
    print(f"Runtime fields changed   : 0")
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

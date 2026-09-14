#!/usr/bin/env python3
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TR = ROOT / "translation"
OUT = ROOT / "checkpoints" / "0.6.29.0" / "BATCH20_PRECEDENCE_SIMULATION.txt"
PARTS = [TR / f"TRANSLATION_MASTER_0.6_part{i:02d}.csv" for i in range(1, 7)]
B20 = TR / "BATCH20_EXACT_OFFSET_0.6.29.0.csv"
GAMEPLAY = TR / "GAMEPLAY_ACCENT_OVERRIDES_0.6.11.0.csv"
EXTRA_MAP = TR / "BATCH3_FALLBACK_ACCENT_MAP_0.6.12.0.csv"
COMPACT13 = TR / "COMPACT_TRANSLATION_OVERRIDES_0.6.13.0.csv"
COMPACT14 = TR / "COMPACT_TRANSLATION_OVERRIDES_0.6.14.1.csv"
DYNAMIC12 = TR / "DYNAMIC_LITERAL_OVERRIDES_0.6.12.0.csv"
TOKEN = re.compile(r"%(?:[-+0-9.#]*[A-Za-z])|/[Vv]")


def rows(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def key(r):
    return r["file"].strip(), hex(int(r["offset_hex"], 0)).lower()


def rlen(text):
    n = 0
    pos = 0
    for m in TOKEN.finditer(text or ""):
        n += (m.start() - pos) * 2
        n += len(m.group(0).encode("ascii"))
        pos = m.end()
    return n + (len(text or "") - pos) * 2


def main():
    master = []
    for p in PARTS:
        master.extend(rows(p))
    by_key = {key(r): r for r in master}
    batch = {key(r): r["vi_accented"].strip() for r in rows(B20)}

    for k, text in batch.items():
        by_key[k]["vi_full"] = text

    # Planned wrapper rule: exact-key override files lose only Batch20 collisions.
    gameplay = [r for r in rows(GAMEPLAY) if key(r) not in batch]
    compact13 = [r for r in rows(COMPACT13) if key(r) not in batch]
    compact14 = [r for r in rows(COMPACT14) if key(r) not in batch]

    # Reproduce 0.6.12 global fallback promotion.
    fallback_map = {}
    source = {}
    for r in gameplay:
        src = by_key.get(key(r))
        if not src:
            continue
        old = (src.get("vi_game_current") or "").strip()
        target = (r.get("vi_accented") or "").strip()
        if old and target and (old not in fallback_map or rlen(target) < rlen(fallback_map[old])):
            fallback_map[old] = target
            source[old] = "gameplay exemplar"
    for r in rows(EXTRA_MAP):
        old = (r.get("vi_game_current") or "").strip()
        target = (r.get("vi_accented") or "").strip()
        if old and target:
            fallback_map[old] = target
            source[old] = "Batch3 curated"

    global_overwrites = []
    for r in master:
        old = (r.get("vi_game_current") or "").strip()
        if not old or old not in fallback_map:
            continue
        target = fallback_map[old]
        try:
            field = len((r.get("japanese") or "").encode("cp932"))
        except UnicodeEncodeError:
            continue
        if rlen(target) <= field:
            current = (r.get("vi_full") or "").strip()
            if not current or rlen(target) <= rlen(current):
                k = key(r)
                if k in batch and target != batch[k]:
                    global_overwrites.append((k, batch[k], target, old, source[old]))
                r["vi_full"] = target

    # Reproduce later compact exact precedence after planned collision filtering.
    for r in compact13 + compact14:
        if key(r) in by_key:
            by_key[key(r)]["vi_full"] = (r.get("vi_accented") or "").strip()

    compact_overwrites = []
    for k, expected in batch.items():
        got = (by_key[k].get("vi_full") or "").strip()
        if got != expected:
            compact_overwrites.append((k, expected, got))

    # 0.6.12 copies DYNAMIC12 over the 0.6.11 live dynamic file. Any matching
    # existing Japanese row is a potential final overwrite inside 0.6.11.
    dynamic = rows(DYNAMIC12)
    dynamic_hits = []
    for k, expected in batch.items():
        src = by_key[k]
        jp = src.get("japanese") or ""
        for d in dynamic:
            scope = (d.get("file_scope") or "AUTO").strip()
            if d.get("japanese") == jp and (scope.upper() == "AUTO" or scope == k[0]):
                dynamic_hits.append((k, expected, d.get("vi_accented", ""), jp))

    lines = [
        "GAIA MASTER 0.6.29.0 BATCH20 PRECEDENCE SIMULATION",
        "=" * 72,
        f"Batch20 exact rows                 : {len(batch)}",
        f"Filtered gameplay exact collisions: {len(rows(GAMEPLAY)) - len(gameplay)}",
        f"Filtered compact13 collisions      : {len(rows(COMPACT13)) - len(compact13)}",
        f"Filtered compact14 collisions      : {len(rows(COMPACT14)) - len(compact14)}",
        f"Global fallback overwrites         : {len(global_overwrites)}",
        f"Later compact overwrites           : {len(compact_overwrites)}",
        f"Dynamic Japanese collision risks   : {len(dynamic_hits)}",
        "",
    ]
    if global_overwrites:
        lines.append("GLOBAL FALLBACK OVERWRITES:")
        for k, want, got, old, why in global_overwrites:
            lines.append(f"  {k[0]} {k[1]}: {want} -> {got} via {old!r} ({why})")
    if compact_overwrites:
        lines.append("LATER COMPACT OVERWRITES:")
        for k, want, got in compact_overwrites:
            lines.append(f"  {k[0]} {k[1]}: {want} -> {got}")
    if dynamic_hits:
        lines.append("DYNAMIC COLLISION RISKS:")
        for k, want, got, jp in dynamic_hits:
            lines.append(f"  {k[0]} {k[1]}: {want} -> {got} JP={jp}")
    lines.append("")
    lines.append("RESULT: " + ("PASS" if not global_overwrites and not compact_overwrites and not dynamic_hits else "NEEDS GUARDS"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TR = ROOT / "translation"
B20 = TR / "BATCH20_EXACT_OFFSET_0.6.29.0.csv"
EXACT_FILES = [
    TR / "GAMEPLAY_ACCENT_OVERRIDES_0.6.11.0.csv",
    TR / "COMPACT_TRANSLATION_OVERRIDES_0.6.13.0.csv",
    TR / "COMPACT_TRANSLATION_OVERRIDES_0.6.14.0.csv",
    TR / "COMPACT_TRANSLATION_OVERRIDES_0.6.14.1.csv",
]
OUT = ROOT / "checkpoints" / "0.6.29.0" / "BATCH20_PRODUCTION_COLLISIONS.txt"


def rows(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def key(r):
    return r["file"].strip(), hex(int(r["offset_hex"], 0)).lower()


def main():
    batch = {key(r): r for r in rows(B20)}
    lines = ["GAIA MASTER 0.6.29.0 BATCH20 PRODUCTION COLLISION AUDIT", "=" * 72]
    total = 0
    for path in EXACT_FILES:
        if not path.is_file():
            lines.append(f"MISSING: {path.name}")
            continue
        hits = [(key(r), r.get("vi_accented", "")) for r in rows(path) if key(r) in batch]
        total += len(hits)
        lines.append(f"{path.name}: {len(hits)} collision(s)")
        for k, text in hits:
            lines.append(f"  {k[0]} {k[1]} -> {text}")
    lines.append("")
    lines.append(f"TOTAL COLLISIONS: {total}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import re
from pathlib import Path

VERSION = "0.6.30.0"
ROOT = Path(__file__).resolve().parent.parent
TR = ROOT / "translation"
SEM = TR / "BATCH21_SEMANTIC_0.6.30.0.csv"
RESIDUAL = ROOT / "checkpoints" / "0.6.28.0" / "reports" / "GaiaMaster_0.6.28.0_RESIDUAL_ALPHA.csv"
OUT_DIR = ROOT / "checkpoints" / VERSION
OUT_CSV = OUT_DIR / "BATCH21_FIT_ANALYSIS.csv"
OUT_SUM = OUT_DIR / "BATCH21_FIT_SUMMARY.txt"
TOKEN = re.compile(r"%(?:[-+0-9.#]*[A-Za-z%])|/[Vv]")


def read_rows(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def norm(text):
    return re.sub(r"\s+", " ", (text or "").replace("\u3000", " ")).strip()


def runtime_len(text):
    text = text or ""
    total = 0
    pos = 0
    for m in TOKEN.finditer(text):
        total += (m.start() - pos) * 2
        total += len(m.group(0).encode("ascii"))
        pos = m.end()
    return total + (len(text) - pos) * 2


def main():
    sem = {norm(r["japanese"]): r["vi_fantasy"].strip() for r in read_rows(SEM)}
    residual = read_rows(RESIDUAL)
    out = []
    fit = 0
    pressure = 0
    max_over = 0

    for row in residual:
        jp = row["japanese"]
        vi = sem[norm(jp)]
        field = len(jp.encode("cp932"))
        used = runtime_len(vi)
        over = max(0, used - field)
        if over == 0:
            fit += 1
        else:
            pressure += 1
            max_over = max(max_over, over)
        out.append({
            "master_part": row["master_part"],
            "file": row["file"],
            "offset_hex": row["offset_hex"],
            "japanese": jp,
            "field_bytes": field,
            "semantic_vi": vi,
            "candidate_bytes": used,
            "over_bytes": over,
            "fit": "YES" if over == 0 else "NO",
            "vi_game_current": row["vi_game_current"],
        })

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fields = ["master_part", "file", "offset_hex", "japanese", "field_bytes",
              "semantic_vi", "candidate_bytes", "over_bytes", "fit", "vi_game_current"]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(sorted(out, key=lambda r: (-int(r["over_bytes"]), r["file"], int(r["offset_hex"], 16))))

    unique_fit = set()
    unique_pressure = set()
    for r in out:
        target = unique_fit if r["fit"] == "YES" else unique_pressure
        target.add(norm(r["japanese"]))

    lines = [
        f"GAIA MASTER {VERSION} BATCH 21 FIT ANALYSIS",
        "=" * 72,
        f"Residual rows analyzed : {len(out)}",
        f"Semantic keys          : {len(sem)}",
        f"Rows fitting now       : {fit}",
        f"Rows needing compact   : {pressure}",
        f"Unique JP fitting      : {len(unique_fit)}",
        f"Unique JP pressure     : {len(unique_pressure)}",
        f"Maximum over-bytes     : {max_over}",
        "",
        "NOTE: semantic wording is meaning-first; pressure rows are Batch 22 compact targets.",
        "No ROM/font/pointer data is modified.",
    ]
    OUT_SUM.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

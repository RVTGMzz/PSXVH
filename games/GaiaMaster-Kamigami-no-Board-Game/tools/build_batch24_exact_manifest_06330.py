#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path

VERSION = "0.6.33.0"
EXPECTED_ROWS = 147
ROOT = Path(__file__).resolve().parent.parent
TR = ROOT / "translation"
RESIDUAL = ROOT / "checkpoints" / "0.6.28.0" / "reports" / "GaiaMaster_0.6.28.0_RESIDUAL_ALPHA.csv"
SEM = TR / "BATCH21_SEMANTIC_0.6.30.0.csv"
B22 = TR / "BATCH22_COMPACT_0.6.31.0.csv"
B23 = TR / "BATCH23_COMPACT_0.6.32.0.csv"
OUT_CSV = TR / "BATCH24_EXACT_OFFSET_0.6.33.0.csv"
OUT_SUM = ROOT / "checkpoints" / VERSION / "BATCH24_MANIFEST_VALIDATION.txt"
TOKEN = re.compile(r"%(?:[-+0-9.#]*[A-Za-z%])|/[Vv]")
FROZEN = set("àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ")


def rows(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def norm(text):
    return re.sub(r"\s+", " ", (text or "").replace("\u3000", " ")).strip()


def tokens(text):
    return tuple(m.group(0) for m in TOKEN.finditer(text or ""))


def rlen(text):
    total = 0
    pos = 0
    for m in TOKEN.finditer(text or ""):
        total += (m.start() - pos) * 2 + len(m.group(0).encode("ascii"))
        pos = m.end()
    return total + (len(text or "") - pos) * 2


def bad_chars(text):
    out = []
    for ch in text:
        if ord(ch) < 128:
            continue
        try:
            ch.encode("cp932")
            continue
        except UnicodeEncodeError:
            pass
        if ch not in FROZEN:
            out.append(ch)
    return sorted(set(out))


def map_file(path, value_column):
    return {norm(r["japanese"]): (r[value_column].strip(), path.name) for r in rows(path)}


def main():
    residual = rows(RESIDUAL)
    semantic = map_file(SEM, "vi_fantasy")
    compact22 = map_file(B22, "vi_compact")
    compact23 = map_file(B23, "vi_compact")
    errors = []
    out = []
    seen_exact = set()
    source_counts = Counter()
    unique_choice = {}

    for i, row in enumerate(residual, 2):
        jp = row["japanese"]
        jk = norm(jp)
        choice = compact22.get(jk) or compact23.get(jk) or semantic.get(jk)
        if choice is None:
            errors.append(f"line {i}: no resolved candidate for {jp}")
            continue
        vi, source = choice
        ek = (row["file"].strip(), hex(int(row["offset_hex"], 0)).lower())
        if ek in seen_exact:
            errors.append(f"line {i}: duplicate exact key {ek}")
            continue
        seen_exact.add(ek)
        try:
            field = len(jp.encode("cp932"))
        except UnicodeEncodeError:
            errors.append(f"line {i}: Japanese not CP932 encodable: {jp}")
            continue
        used = rlen(vi)
        if used > field:
            errors.append(f"line {i}: resolved text too long {used}>{field}: {ek} {vi}")
        if tokens(jp) != tokens(vi):
            errors.append(f"line {i}: token mismatch: {ek} {jp} -> {vi}")
        bad = bad_chars(vi)
        if bad:
            errors.append(f"line {i}: unsupported chars {bad!r}: {ek} {vi}")
        old = unique_choice.get(jk)
        if old is not None and old != vi:
            errors.append(f"line {i}: same Japanese resolves inconsistently: {jp}: {old} != {vi}")
        unique_choice[jk] = vi
        source_counts[source] += 1
        out.append({
            "file": ek[0],
            "offset_hex": ek[1],
            "japanese": jp,
            "vi_accented": vi,
            "field_bytes": field,
            "vi_bytes": used,
            "free_bytes": field - used,
            "source": source,
            "category": "batch24-residual-exact",
        })

    if len(residual) != EXPECTED_ROWS:
        errors.append(f"residual source row count changed: {len(residual)} != {EXPECTED_ROWS}")
    if len(out) != EXPECTED_ROWS:
        errors.append(f"compiled exact row count {len(out)} != {EXPECTED_ROWS}")
    if len(unique_choice) != 62:
        errors.append(f"resolved unique Japanese count {len(unique_choice)} != 62")

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = ["file", "offset_hex", "japanese", "vi_accented", "field_bytes", "vi_bytes", "free_bytes", "source", "category"]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(sorted(out, key=lambda r: (r["file"], int(r["offset_hex"], 16))))

    OUT_SUM.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"GAIA MASTER {VERSION} BATCH 24 RESIDUAL EXACT MANIFEST",
        "=" * 72,
        f"Source residual rows    : {len(residual)}",
        f"Compiled exact rows     : {len(out)}",
        f"Resolved unique JP      : {len(unique_choice)}",
        f"Semantic-fit rows       : {source_counts.get(SEM.name, 0)}",
        f"Batch22 compact rows    : {source_counts.get(B22.name, 0)}",
        f"Batch23 compact rows    : {source_counts.get(B23.name, 0)}",
        f"Errors                  : {len(errors)}",
        "",
        "Guards:",
        "- every persisted 0.6.28.0 residual exact file+offset must resolve exactly once",
        "- Batch22/23 compact wording overrides Batch21 semantic wording only for pressure keys",
        "- every final exact string must fit its original Japanese field",
        "- runtime token identity/order preserved",
        "- CP932/frozen 60-glyph codepage only",
        "- data compiler only; no ROM/font/pointer modification",
    ]
    if errors:
        lines += ["", "ERRORS:"] + [f"- {e}" for e in errors]
    else:
        lines += ["", "RESULT                : STATIC PASS"]
    OUT_SUM.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

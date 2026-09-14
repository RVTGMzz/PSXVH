#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import re
from pathlib import Path

VERSION = "0.6.31.0"
EXPECTED_KEYS = 12
ROOT = Path(__file__).resolve().parent.parent
TR = ROOT / "translation"
COMPACT = TR / "BATCH22_COMPACT_0.6.31.0.csv"
FIT = ROOT / "checkpoints" / "0.6.30.0" / "BATCH21_FIT_ANALYSIS.csv"
OUT = ROOT / "checkpoints" / VERSION / "BATCH22_VALIDATION.txt"
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
    text = text or ""
    total = 0
    pos = 0
    for m in TOKEN.finditer(text):
        total += (m.start() - pos) * 2 + len(m.group(0).encode("ascii"))
        pos = m.end()
    return total + (len(text) - pos) * 2


def bad_chars(text):
    bad = []
    for ch in text:
        if ord(ch) < 128:
            continue
        try:
            ch.encode("cp932")
            continue
        except UnicodeEncodeError:
            pass
        if ch not in FROZEN:
            bad.append(ch)
    return sorted(set(bad))


def main():
    source = rows(FIT)
    pressure = {}
    for row in source:
        if row["fit"] == "NO":
            pressure.setdefault(norm(row["japanese"]), []).append(row)

    compact_rows = rows(COMPACT)
    errors = []
    mapping = {}
    covered_rows = 0
    exact_fit_rows = 0
    spare_bytes = 0

    if len(compact_rows) != EXPECTED_KEYS:
        errors.append(f"expected {EXPECTED_KEYS} compact keys, got {len(compact_rows)}")

    for i, row in enumerate(compact_rows, 2):
        jp = row["japanese"]
        vi = (row.get("vi_compact") or "").strip()
        k = norm(jp)
        if k in mapping:
            errors.append(f"line {i}: duplicate Japanese key: {jp}")
            continue
        mapping[k] = vi
        matches = pressure.get(k, [])
        if not matches:
            errors.append(f"line {i}: Japanese key not in Batch21 pressure set: {jp}")
            continue
        if any(int(r["over_bytes"]) > 6 for r in matches):
            errors.append(f"line {i}: outside easy pressure band: {jp}")
        if tokens(jp) != tokens(vi):
            errors.append(f"line {i}: token mismatch: {jp} -> {vi}")
        bad = bad_chars(vi)
        if bad:
            errors.append(f"line {i}: unsupported chars {bad!r}: {vi}")
        used = rlen(vi)
        for src in matches:
            field = int(src["field_bytes"])
            if used > field:
                errors.append(f"line {i}: still too long {used}>{field}: {jp} -> {vi}")
            else:
                covered_rows += 1
                spare_bytes += field - used
                if used == field:
                    exact_fit_rows += 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"GAIA MASTER {VERSION} BATCH 22 EASY COMPACT VALIDATION",
        "=" * 72,
        f"Compact Japanese keys : {len(mapping)}",
        f"Pressure rows covered : {covered_rows}",
        f"Exact-full-field rows : {exact_fit_rows}",
        f"Total spare bytes     : {spare_bytes}",
        f"Errors                : {len(errors)}",
        "",
        "Guards:",
        "- source must be Batch21 pressure rows with original overage <= 6 bytes",
        "- runtime token identity/order preserved",
        "- every compact candidate must fit every matching field",
        "- CP932/frozen 60-glyph codepage only",
        "- translation-data only; no ROM/font/pointer modification",
    ]
    if errors:
        lines += ["", "ERRORS:"] + [f"- {e}" for e in errors]
    else:
        lines += ["", "RESULT                : STATIC PASS"]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import re
from pathlib import Path

VERSION = "0.6.32.0"
EXPECTED_KEYS = 36
ROOT = Path(__file__).resolve().parent.parent
TR = ROOT / "translation"
B22 = TR / "BATCH22_COMPACT_0.6.31.0.csv"
B23 = TR / "BATCH23_COMPACT_0.6.32.0.csv"
FIT = ROOT / "checkpoints" / "0.6.30.0" / "BATCH21_FIT_ANALYSIS.csv"
OUT = ROOT / "checkpoints" / VERSION / "BATCH23_VALIDATION.txt"
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
    fit_rows = rows(FIT)
    pressure = {}
    for row in fit_rows:
        if row["fit"] == "NO":
            pressure.setdefault(norm(row["japanese"]), []).append(row)

    b22 = {norm(r["japanese"]) for r in rows(B22)}
    remaining = set(pressure) - b22
    b23_rows = rows(B23)
    mapping = {}
    errors = []
    covered = 0
    exact = 0
    spare = 0

    if len(b23_rows) != EXPECTED_KEYS:
        errors.append(f"expected {EXPECTED_KEYS} compact keys, got {len(b23_rows)}")

    for i, row in enumerate(b23_rows, 2):
        jp = row["japanese"]
        vi = (row.get("vi_compact") or "").strip()
        k = norm(jp)
        if k in mapping:
            errors.append(f"line {i}: duplicate Japanese key: {jp}")
            continue
        mapping[k] = vi
        matches = pressure.get(k, [])
        if not matches:
            errors.append(f"line {i}: key not in Batch21 pressure set: {jp}")
            continue
        if k in b22:
            errors.append(f"line {i}: overlaps Batch22 easy compact key: {jp}")
        if tokens(jp) != tokens(vi):
            errors.append(f"line {i}: token mismatch: {jp} -> {vi}")
        bad = bad_chars(vi)
        if bad:
            errors.append(f"line {i}: unsupported chars {bad!r}: {vi}")
        used = rlen(vi)
        for src in matches:
            field = int(src["field_bytes"])
            if used > field:
                errors.append(f"line {i}: too long {used}>{field}: {jp} -> {vi}")
            else:
                covered += 1
                spare += field - used
                if used == field:
                    exact += 1

    missing = sorted(remaining - set(mapping))
    extra = sorted(set(mapping) - remaining)
    if missing:
        errors.append(f"missing remaining pressure keys: {len(missing)}")
        errors.extend(f"  missing: {x}" for x in missing)
    if extra:
        errors.append(f"unexpected non-remaining keys: {len(extra)}")
        errors.extend(f"  extra: {x}" for x in extra)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"GAIA MASTER {VERSION} BATCH 23 REMAINING COMPACT VALIDATION",
        "=" * 72,
        f"Batch21 pressure keys : {len(pressure)}",
        f"Batch22 resolved keys : {len(b22)}",
        f"Remaining target keys : {len(remaining)}",
        f"Batch23 compact keys  : {len(mapping)}",
        f"Pressure rows covered : {covered}",
        f"Exact-full-field rows : {exact}",
        f"Total spare bytes     : {spare}",
        f"Errors                : {len(errors)}",
        "",
        "Guards:",
        "- Batch23 must equal the complete Batch21 pressure-key remainder after Batch22",
        "- runtime token identity/order preserved",
        "- every compact candidate must fit every matching source field",
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

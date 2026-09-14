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
OUT = ROOT / "checkpoints" / VERSION / "BATCH21_SEMANTIC_VALIDATION.txt"
RAW_TOKEN_RE = re.compile(r"%(?:[-+0-9.#]*[A-Za-z%])|/[Vv]")
FROZEN_CUSTOM = set("àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ")


def rows(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def norm(text):
    return re.sub(r"\s+", " ", (text or "").replace("\u3000", " ")).strip()


def tokens(text):
    return tuple(m.group(0) for m in RAW_TOKEN_RE.finditer(text or ""))


def unsupported(text):
    bad = []
    for ch in text:
        if ord(ch) < 128:
            continue
        try:
            ch.encode("cp932")
            continue
        except UnicodeEncodeError:
            pass
        if ch not in FROZEN_CUSTOM:
            bad.append(ch)
    return sorted(set(bad))


def main():
    sem_rows = rows(SEM)
    residual = rows(RESIDUAL)
    errors = []
    mapping = {}

    for i, row in enumerate(sem_rows, 2):
        jp = row.get("japanese", "")
        vi = (row.get("vi_fantasy") or "").strip()
        k = norm(jp)
        if not k or not vi:
            errors.append(f"line {i}: empty key/value")
            continue
        if k in mapping:
            errors.append(f"line {i}: duplicate Japanese key: {jp}")
        mapping[k] = vi
        if tokens(jp) != tokens(vi):
            errors.append(f"line {i}: token mismatch {tokens(jp)!r} != {tokens(vi)!r}: {jp} -> {vi}")
        bad = unsupported(vi)
        if bad:
            errors.append(f"line {i}: unsupported frozen-codepage chars {bad!r}: {vi}")

    residual_keys = [norm(r.get("japanese", "")) for r in residual]
    residual_unique = set(residual_keys)
    outside = sorted(set(mapping) - residual_unique)
    if outside:
        errors.append(f"semantic keys outside current residual set: {len(outside)}")
        errors.extend(f"  outside: {x}" for x in outside)

    covered_rows = sum(1 for k in residual_keys if k in mapping)
    covered_unique = len(residual_unique & set(mapping))
    remaining_rows = len(residual) - covered_rows
    remaining_unique = len(residual_unique - set(mapping))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"GAIA MASTER {VERSION} BATCH 21 SEMANTIC VALIDATION",
        "=" * 72,
        f"Semantic keys         : {len(mapping)}",
        f"Residual source rows  : {len(residual)}",
        f"Residual unique JP    : {len(residual_unique)}",
        f"Covered residual rows : {covered_rows}",
        f"Covered unique JP     : {covered_unique}",
        f"Remaining rows        : {remaining_rows}",
        f"Remaining unique JP   : {remaining_unique}",
        f"Errors                : {len(errors)}",
        "",
        "Guards:",
        "- semantic key must originate from persisted 0.6.28.0 residual report",
        "- runtime token identity/order must be preserved",
        "- Vietnamese text must stay inside CP932 or frozen 60-glyph codepage",
        "- semantic-only: no ROM/font/pointer modification",
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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static validator for Gaia Master 0.6.29.0 Batch 20 exact-offset sweep."""
from __future__ import annotations

import csv
import re
from pathlib import Path

VERSION = "0.6.29.0"
EXPECTED_ROWS = 75
ROOT = Path(__file__).resolve().parent.parent
TR = ROOT / "translation"
PRESSURE = ROOT / "checkpoints" / "0.6.28.0" / "reports" / "GaiaMaster_0.6.28.0_FIT_PRESSURE.csv"
BATCH20 = TR / "BATCH20_EXACT_OFFSET_0.6.29.0.csv"
B19_EXACT = ROOT / "checkpoints" / "0.6.28.0" / "reports" / "GaiaMaster_0.6.28.0_EXACT_OFFSET_LOCKS.csv"
HIST_EXACT = TR / "COMPACT_TRANSLATION_OVERRIDES_0.6.14.1.csv"
OUT = ROOT / "checkpoints" / VERSION / "BATCH20_VALIDATION.txt"

RAW_TOKEN_RE = re.compile(r"%(?:[-+0-9.#]*[A-Za-z%])|/[Vv]")
FROZEN_CUSTOM_ORDER = "àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ"
FROZEN_CUSTOM = set(FROZEN_CUSTOM_ORDER)


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return list(r)


def norm_off(v: str) -> str:
    return hex(int(str(v).strip(), 0)).lower()


def key(row):
    return row["file"].strip(), norm_off(row["offset_hex"])


def tokens(text: str):
    return tuple(m.group(0) for m in RAW_TOKEN_RE.finditer(text or ""))


def runtime_len(text: str) -> int:
    n = 0
    pos = 0
    for m in RAW_TOKEN_RE.finditer(text or ""):
        n += (m.start() - pos) * 2
        n += len(m.group(0).encode("ascii"))
        pos = m.end()
    n += (len(text or "") - pos) * 2
    return n


def unsupported(text: str):
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
    return bad


def main() -> int:
    required = [PRESSURE, BATCH20, B19_EXACT, HIST_EXACT]
    missing = [str(p) for p in required if not p.is_file()]
    if missing:
        raise SystemExit("[BLOCKED] missing files:\n  " + "\n  ".join(missing))

    pressure_rows = read_csv(PRESSURE)
    pressure = {key(r): r for r in pressure_rows}
    locks = {key(r) for r in read_csv(B19_EXACT)} | {key(r) for r in read_csv(HIST_EXACT)}
    rows = read_csv(BATCH20)

    errors = []
    seen = set()
    validated = []

    if len(rows) != EXPECTED_ROWS:
        errors.append(f"row-count expected {EXPECTED_ROWS}, got {len(rows)}")

    for i, row in enumerate(rows, 2):
        k = key(row)
        text = (row.get("vi_accented") or "").strip()
        if k in seen:
            errors.append(f"line {i}: duplicate exact key {k}")
            continue
        seen.add(k)

        p = pressure.get(k)
        if p is None:
            errors.append(f"line {i}: key not present in V2 FIT_PRESSURE: {k}")
            continue
        if k in locks:
            errors.append(f"line {i}: collides with protected exact lock: {k}")
            continue
        if not text:
            errors.append(f"line {i}: empty Vietnamese text: {k}")
            continue

        field = int(p["field_bytes"])
        old_over = int(p["over_bytes"])
        new_len = runtime_len(text)
        bad = unsupported(text)
        jp_tokens = tokens(p["japanese"])
        vi_tokens = tokens(text)

        if old_over > 6:
            errors.append(f"line {i}: outside Batch20 easy-pressure band (>6B): {k} over={old_over}")
        if new_len > field:
            errors.append(f"line {i}: still too long {new_len}>{field}: {k} {text!r}")
        if jp_tokens != vi_tokens:
            errors.append(f"line {i}: token mismatch {jp_tokens!r}!={vi_tokens!r}: {k}")
        if bad:
            errors.append(f"line {i}: unsupported frozen-codepage chars {bad!r}: {k}")

        validated.append((k, field, new_len, old_over, text))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"GAIA MASTER {VERSION} BATCH 20 STATIC VALIDATION",
        "=" * 72,
        f"Batch20 rows          : {len(rows)}",
        f"Pressure source rows  : {len(pressure_rows)}",
        f"Protected exact keys  : {len(locks)}",
        f"Validated rows        : {len(validated)}",
        f"Errors                : {len(errors)}",
        "",
        "Guards:",
        "- every key must come from 0.6.28.0 V2 FIT_PRESSURE",
        "- Batch20 only targets <=6-byte pressure rows",
        "- exact keys may not collide with Batch19/historical locks",
        "- runtime tokens must match identity and order",
        "- candidate length must fit Japanese field bytes",
        "- non-CP932 glyphs must belong to frozen Vietnamese codepage",
        "- no ROM/font/renderer/pointer work is performed",
    ]
    if errors:
        lines += ["", "ERRORS:"] + [f"- {e}" for e in errors]
    else:
        exact_fit = sum(1 for _, field, new_len, _, _ in validated if field == new_len)
        saved = sum(field - new_len for _, field, new_len, _, _ in validated)
        lines += [
            "",
            f"Exact-full-field rows : {exact_fit}",
            f"Total spare bytes     : {saved}",
            "RESULT                : STATIC PASS",
        ]

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

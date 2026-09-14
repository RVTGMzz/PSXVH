#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import re
from pathlib import Path

VERSION = "0.6.34.0"
EXPECTED_INPUT = 222
ROOT = Path(__file__).resolve().parent.parent
TR = ROOT / "translation"
PARTS = [TR / f"TRANSLATION_MASTER_0.6_part{i:02d}.csv" for i in range(1, 7)]
B20 = TR / "BATCH20_EXACT_OFFSET_0.6.29.0.csv"
B24 = TR / "BATCH24_EXACT_OFFSET_0.6.33.0.csv"
HIST = TR / "COMPACT_TRANSLATION_OVERRIDES_0.6.14.1.csv"
B19 = ROOT / "checkpoints" / "0.6.28.0" / "reports" / "GaiaMaster_0.6.28.0_EXACT_OFFSET_LOCKS.csv"
OUT = TR / "BATCH25_NEW_EXACT_OFFSET_0.6.34.0.csv"
REPORT = ROOT / "checkpoints" / VERSION / "BATCH25_MERGE_VALIDATION.txt"
TOKEN = re.compile(r"%(?:[-+0-9.#]*[A-Za-z%])|/[Vv]")
FROZEN = set("àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ")


def rows(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def key(r):
    return r["file"].strip(), hex(int(r["offset_hex"], 0)).lower()


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


def master_index():
    out = {}
    for p in PARTS:
        for r in rows(p):
            k = key(r)
            if k in out:
                raise RuntimeError(f"duplicate Translation Master key: {k}")
            out[k] = r
    return out


def protected_map(master):
    """Return only locks that the production path can actually encode in-place.

    0.6.14.1 is a candidate override table; its wrapper skips rows whose runtime
    encoding exceeds the original Japanese field. Treating every CSV row as an
    applied production lock would therefore over-protect historical no-op rows.
    Batch19 exact locks are already compiler-proven fitting and stay unconditional.
    """
    out = {}
    skipped_hist = []
    for r in rows(HIST):
        k = key(r)
        src = master.get(k)
        text = (r.get("vi_accented") or "").strip()
        if src is None:
            skipped_hist.append((k, text, "missing-master"))
            continue
        jp = src.get("japanese") or ""
        try:
            field = len(jp.encode("cp932"))
        except UnicodeEncodeError:
            skipped_hist.append((k, text, "jp-encode"))
            continue
        reason = None
        if rlen(text) > field:
            reason = f"too-long:{rlen(text)}>{field}"
        elif tokens(jp) != tokens(text):
            reason = "token-mismatch"
        elif bad_chars(text):
            reason = f"unsupported:{bad_chars(text)!r}"
        if reason:
            skipped_hist.append((k, text, reason))
            continue
        out[k] = (text, HIST.name)

    for r in rows(B19):
        k = key(r)
        value = (r.get("vi_full") or "").strip()
        if k in out and out[k][0] != value:
            raise RuntimeError(f"protected lock conflict before Batch25: {k}: {out[k]} vs {value}")
        out[k] = (value, B19.name)
    return out, skipped_hist


def main():
    master = master_index()
    protected, skipped_hist = protected_map(master)
    errors = []
    candidates = {}

    source_specs = [
        (B20, "vi_accented", B20.name),
        (B24, "vi_accented", B24.name),
    ]
    input_count = 0
    for path, value_col, source in source_specs:
        for r in rows(path):
            input_count += 1
            k = key(r)
            text = (r.get(value_col) or "").strip()
            old = candidates.get(k)
            if old and old[0] != text:
                errors.append(f"candidate conflict {k}: {old[0]!r} vs {text!r}")
                continue
            candidates[k] = (text, source)

    if input_count != EXPECTED_INPUT:
        errors.append(f"input exact row count {input_count} != {EXPECTED_INPUT}")

    output = []
    already_locked = []
    conflict_locked = []
    for k, (text, source) in sorted(candidates.items(), key=lambda x: (x[0][0], int(x[0][1], 16))):
        src = master.get(k)
        if src is None:
            errors.append(f"candidate key missing Translation Master: {k}")
            continue
        jp = src.get("japanese") or ""
        try:
            field = len(jp.encode("cp932"))
        except UnicodeEncodeError:
            errors.append(f"Japanese not CP932 encodable: {k}")
            continue
        used = rlen(text)
        if used > field:
            errors.append(f"candidate too long {used}>{field}: {k} {text}")
        if tokens(jp) != tokens(text):
            errors.append(f"token mismatch: {k} {jp} -> {text}")
        bad = bad_chars(text)
        if bad:
            errors.append(f"unsupported chars {bad!r}: {k} {text}")

        if k in protected:
            locked_text, locked_source = protected[k]
            if locked_text == text:
                already_locked.append((k, text, locked_source, source))
            else:
                conflict_locked.append((k, text, source, locked_text, locked_source))
                errors.append(
                    f"protected wording conflict {k}: new={text!r} ({source}) locked={locked_text!r} ({locked_source})"
                )
            continue

        output.append({
            "file": k[0],
            "offset_hex": k[1],
            "japanese": jp,
            "vi_accented": text,
            "field_bytes": field,
            "vi_bytes": used,
            "free_bytes": field - used,
            "source": source,
            "category": "batch25-new-exact",
        })

    fields = ["file", "offset_hex", "japanese", "vi_accented", "field_bytes", "vi_bytes", "free_bytes", "source", "category"]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(output)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"GAIA MASTER {VERSION} BATCH 25 MERGED EXACT VALIDATION",
        "=" * 72,
        f"Batch20 + Batch24 input rows : {input_count}",
        f"Unique candidate exact keys  : {len(candidates)}",
        f"Runtime-fit protected keys   : {len(protected)}",
        f"Historical rows skipped as no-op/unfit: {len(skipped_hist)}",
        f"Already-locked identical     : {len(already_locked)}",
        f"Protected wording conflicts  : {len(conflict_locked)}",
        f"New exact rows exported      : {len(output)}",
        f"Errors                       : {len(errors)}",
        "",
        "Guards:",
        "- Batch20 and Batch24 exact work is merged by file+offset",
        "- 0.6.14.1 rows count as protected only when they truly fit and encode under the frozen runtime contract",
        "- Batch19 exact locks remain unconditionally protected",
        "- identical protected wording is recognized and not exported twice",
        "- different runtime-fit protected wording is a hard error",
        "- every candidate is rechecked for field bytes, runtime tokens and frozen codepage",
        "- data compiler only; no ROM/font/pointer modification",
    ]
    if already_locked:
        lines += ["", "ALREADY LOCKED IDENTICAL:"]
        for k, text, lock_src, new_src in already_locked:
            lines.append(f"- {k[0]} {k[1]}: {text} [{lock_src}; candidate {new_src}]")
    if errors:
        lines += ["", "ERRORS:"] + [f"- {e}" for e in errors]
    else:
        lines += ["", "RESULT                : STATIC PASS"]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

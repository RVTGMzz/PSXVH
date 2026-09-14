#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import re
from pathlib import Path

VERSION = "0.6.39.0"
EXPECTED_INPUT = 295
ROOT = Path(__file__).resolve().parent.parent
TR = ROOT / "translation"
PARTS = [TR / f"TRANSLATION_MASTER_0.6_part{i:02d}.csv" for i in range(1, 7)]
SOURCES = [
    TR / "BATCH20_EXACT_OFFSET_0.6.29.0.csv",
    TR / "BATCH24_EXACT_OFFSET_0.6.33.0.csv",
    TR / "BATCH27_ACCENT_PROMOTION_0.6.36.0.csv",
    TR / "BATCH28_SAME_ROW_ACCENT_0.6.37.0.csv",
]
HIST = TR / "COMPACT_TRANSLATION_OVERRIDES_0.6.14.1.csv"
B19 = ROOT / "checkpoints" / "0.6.28.0" / "reports" / "GaiaMaster_0.6.28.0_EXACT_OFFSET_LOCKS.csv"
OUT = TR / "BATCH29_NEW_EXACT_OFFSET_0.6.39.0.csv"
FINAL = TR / "BATCH29_FINAL_EXACT_SET_0.6.39.0.csv"
REPORT = ROOT / "checkpoints" / VERSION / "BATCH29_MERGE_VALIDATION.txt"
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
    total = 0; pos = 0
    for m in TOKEN.finditer(text or ""):
        total += (m.start() - pos) * 2 + len(m.group(0).encode("ascii")); pos = m.end()
    return total + (len(text or "") - pos) * 2


def bad_chars(text):
    out = []
    for ch in text:
        if ord(ch) < 128: continue
        try:
            ch.encode("cp932"); continue
        except UnicodeEncodeError:
            pass
        if ch not in FROZEN: out.append(ch)
    return sorted(set(out))


def master_index():
    out = {}
    for p in PARTS:
        for r in rows(p):
            k = key(r)
            if k in out: raise RuntimeError(f"duplicate Translation Master key: {k}")
            out[k] = r
    return out


def protected_map(master):
    out = {}; skipped = []
    for r in rows(HIST):
        k = key(r); src = master.get(k); text = (r.get("vi_accented") or "").strip()
        if src is None:
            skipped.append((k, text, "missing-master")); continue
        jp = src.get("japanese") or ""
        try: field = len(jp.encode("cp932"))
        except UnicodeEncodeError:
            skipped.append((k, text, "jp-encode")); continue
        reason = None
        if rlen(text) > field: reason = f"too-long:{rlen(text)}>{field}"
        elif tokens(jp) != tokens(text): reason = "token-mismatch"
        elif bad_chars(text): reason = f"unsupported:{bad_chars(text)!r}"
        if reason:
            skipped.append((k, text, reason)); continue
        out[k] = (text, HIST.name)
    for r in rows(B19):
        k = key(r); value = (r.get("vi_full") or "").strip()
        if k in out and out[k][0] != value:
            raise RuntimeError(f"protected lock conflict before Batch29: {k}: {out[k]} vs {value}")
        out[k] = (value, B19.name)
    return out, skipped


def main():
    master = master_index(); protected, skipped_hist = protected_map(master)
    errors = []; candidates = {}; input_count = 0
    for path in SOURCES:
        for r in rows(path):
            input_count += 1
            k = key(r); text = (r.get("vi_accented") or "").strip()
            old = candidates.get(k)
            if old and old[0] != text:
                errors.append(f"candidate conflict {k}: {old[0]!r} vs {text!r}")
                continue
            candidates[k] = (text, path.name)
    if input_count != EXPECTED_INPUT:
        errors.append(f"input exact row count {input_count} != {EXPECTED_INPUT}")

    output = []; final_rows = []; already = []; conflicts = []
    for k, (text, source) in sorted(candidates.items(), key=lambda x:(x[0][0], int(x[0][1],16))):
        src = master.get(k)
        if src is None:
            errors.append(f"candidate key missing Translation Master: {k}"); continue
        jp = src.get("japanese") or ""
        try: field = len(jp.encode("cp932"))
        except UnicodeEncodeError:
            errors.append(f"Japanese not CP932 encodable: {k}"); continue
        used = rlen(text)
        if used > field: errors.append(f"candidate too long {used}>{field}: {k} {text}")
        if tokens(jp) != tokens(text): errors.append(f"token mismatch: {k} {jp} -> {text}")
        bad = bad_chars(text)
        if bad: errors.append(f"unsupported chars {bad!r}: {k} {text}")
        rec = {"file":k[0],"offset_hex":k[1],"japanese":jp,"vi_accented":text,
               "field_bytes":field,"vi_bytes":used,"free_bytes":field-used,
               "source":source,"category":"batch29-final-exact"}
        final_rows.append(rec)
        if k in protected:
            locked_text, locked_source = protected[k]
            if locked_text == text:
                already.append((k,text,locked_source,source))
            else:
                conflicts.append((k,text,source,locked_text,locked_source))
                errors.append(f"protected wording conflict {k}: new={text!r} ({source}) locked={locked_text!r} ({locked_source})")
            continue
        output.append(dict(rec, category="batch29-new-exact"))

    fields = ["file","offset_hex","japanese","vi_accented","field_bytes","vi_bytes","free_bytes","source","category"]
    for path, data in ((OUT, output),(FINAL, final_rows)):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w",encoding="utf-8",newline="") as f:
            w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n"); w.writeheader(); w.writerows(data)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines=[
        f"GAIA MASTER {VERSION} BATCH 29 MERGED EXACT VALIDATION","="*76,
        f"Input rows across B20/B24/B27/B28 : {input_count}",
        f"Unique final candidate keys        : {len(candidates)}",
        f"Runtime-fit protected keys         : {len(protected)}",
        f"Historical rows skipped no-op/unfit: {len(skipped_hist)}",
        f"Already-locked identical           : {len(already)}",
        f"Protected wording conflicts         : {len(conflicts)}",
        f"New exact rows exported            : {len(output)}",
        f"Final exact verification set       : {len(final_rows)}",
        f"Errors                             : {len(errors)}","",
        "Guards:",
        "- merge by exact file+offset",
        "- preserve runtime-fit historical locks and Batch19 exact locks",
        "- recheck byte fit, runtime tokens and frozen codepage",
        "- data compiler only; no ROM/font/pointer modification",
    ]
    if conflicts:
        lines += ["","PROTECTED CONFLICTS:"]
        for k,text,source,locked,locksrc in conflicts:
            lines.append(f"- {k[0]} {k[1]}: new={text!r} [{source}] locked={locked!r} [{locksrc}]")
    if errors:
        lines += ["","ERRORS:"]+[f"- {e}" for e in errors]
    else:
        lines += ["","RESULT: STATIC PASS"]
    REPORT.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("\n".join(lines))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())

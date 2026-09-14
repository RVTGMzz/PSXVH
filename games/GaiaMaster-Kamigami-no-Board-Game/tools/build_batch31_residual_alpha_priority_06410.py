#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

VERSION = "0.6.41.0"
ROOT = Path(__file__).resolve().parent.parent
TR = ROOT / "translation"
PARTS = [TR / f"TRANSLATION_MASTER_0.6_part{i:02d}.csv" for i in range(1, 7)]
B29 = TR / "BATCH29_FINAL_EXACT_SET_0.6.39.0.csv"
HIST = TR / "COMPACT_TRANSLATION_OVERRIDES_0.6.14.1.csv"
B19 = ROOT / "checkpoints" / "0.6.28.0" / "reports" / "GaiaMaster_0.6.28.0_EXACT_OFFSET_LOCKS.csv"
OUT = TR / "BATCH31_RESIDUAL_ALPHA_PRIORITY_0.6.41.0.csv"
REPORT = ROOT / "checkpoints" / VERSION / "BATCH31_RESIDUAL_ALPHA_PRIORITY_REPORT.txt"
TOKEN = re.compile(r"%(?:[-+0-9.#]*[A-Za-z%])|/[Vv]")
FROZEN = set("àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ")


def rows(path: Path):
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def key(r):
    return r["file"].strip(), hex(int(r["offset_hex"], 0)).lower()


def tokens(text):
    return tuple(m.group(0) for m in TOKEN.finditer(text or ""))


def rlen(text: str) -> int:
    total = 0
    pos = 0
    for m in TOKEN.finditer(text or ""):
        total += (m.start() - pos) * 2 + len(m.group(0).encode("ascii"))
        pos = m.end()
    return total + (len(text or "") - pos) * 2


def bad_chars(text: str):
    out = []
    for ch in text or "":
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


def master_rows():
    out = []
    seen = set()
    for p in PARTS:
        for r in rows(p):
            k = key(r)
            if k in seen:
                raise RuntimeError(f"duplicate Translation Master key: {k}")
            seen.add(k)
            out.append(r)
    if len(out) != 596:
        raise RuntimeError(f"Translation Master row gate {len(out)} != 596")
    return out


def historical_runtime_fit(master_by_key):
    out = set()
    skipped = 0
    for r in rows(HIST):
        k = key(r)
        src = master_by_key.get(k)
        text = (r.get("vi_accented") or "").strip()
        if not src or not text:
            skipped += 1
            continue
        jp = src.get("japanese") or ""
        try:
            field = len(jp.encode("cp932"))
        except UnicodeEncodeError:
            skipped += 1
            continue
        if rlen(text) > field or tokens(jp) != tokens(text) or bad_chars(text):
            skipped += 1
            continue
        out.add(k)
    return out, skipped


def main():
    master = master_rows()
    by_key = {key(r): r for r in master}

    protected_b29 = {key(r) for r in rows(B29)}
    protected_b19 = {key(r) for r in rows(B19)}
    protected_hist, hist_skipped = historical_runtime_fit(by_key)
    protected = protected_b29 | protected_b19 | protected_hist

    groups = defaultdict(list)
    residual_rows = []
    for r in master:
        k = key(r)
        fallback = (r.get("vi_game_current") or "").strip()
        if not fallback or k in protected:
            continue
        jp = (r.get("japanese") or "").strip()
        full = (r.get("vi_full") or "").strip()
        try:
            field = len(jp.encode("cp932"))
        except UnicodeEncodeError:
            field = -1
        rec = {
            "file": k[0],
            "offset_hex": k[1],
            "japanese": jp,
            "fallback": fallback,
            "vi_full": full,
            "field_bytes": field,
            "fallback_bytes": rlen(fallback),
            "full_bytes": rlen(full) if full else -1,
            "token_signature": " ".join(tokens(jp)),
        }
        residual_rows.append(rec)
        groups[(jp, fallback, full)].append(rec)

    out_rows = []
    for (jp, fallback, full), rr in groups.items():
        field = rr[0]["field_bytes"]
        fb = rr[0]["fallback_bytes"]
        fullb = rr[0]["full_bytes"]
        if not full:
            reason = "NO_VI_FULL"
        elif fullb <= field and tokens(jp) == tokens(full) and not bad_chars(full):
            reason = "FULL_FITS_BUT_NOT_PROMOTED"
        elif fullb > field:
            reason = "VI_FULL_TOO_LONG"
        elif tokens(jp) != tokens(full):
            reason = "VI_FULL_TOKEN_MISMATCH"
        elif bad_chars(full):
            reason = "VI_FULL_CODEPAGE_UNSAFE"
        else:
            reason = "MANUAL_REVIEW"
        out_rows.append({
            "count": len(rr),
            "japanese": jp,
            "fallback": fallback,
            "vi_full": full,
            "field_bytes": field,
            "fallback_bytes": fb,
            "vi_full_bytes": fullb,
            "free_vs_fallback": field - fb if field >= 0 else -999,
            "reason": reason,
            "files": ";".join(sorted({x["file"] for x in rr})),
            "offsets": ";".join(x["offset_hex"] for x in sorted(rr, key=lambda x:(x["file"], int(x["offset_hex"],16)))),
        })

    reason_rank = {
        "FULL_FITS_BUT_NOT_PROMOTED": 0,
        "NO_VI_FULL": 1,
        "VI_FULL_TOO_LONG": 2,
        "MANUAL_REVIEW": 3,
        "VI_FULL_TOKEN_MISMATCH": 4,
        "VI_FULL_CODEPAGE_UNSAFE": 5,
    }
    out_rows.sort(key=lambda r: (-r["count"], reason_rank.get(r["reason"], 9), r["fallback"], r["japanese"]))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = ["count","japanese","fallback","vi_full","field_bytes","fallback_bytes","vi_full_bytes","free_vs_fallback","reason","files","offsets"]
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader(); w.writerows(out_rows)

    reason_counts = defaultdict(int)
    reason_rows = defaultdict(int)
    for r in out_rows:
        reason_counts[r["reason"]] += 1
        reason_rows[r["reason"]] += int(r["count"])

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"GAIA MASTER {VERSION} BATCH 31 RESIDUAL ALPHA PRIORITY",
        "=" * 80,
        f"Translation Master rows      : {len(master)}",
        f"Protected B29 exact keys     : {len(protected_b29)}",
        f"Protected Batch19 locks      : {len(protected_b19)}",
        f"Runtime-fit historical locks : {len(protected_hist)}",
        f"Historical no-op/unfit rows  : {hist_skipped}",
        f"Residual fallback rows       : {len(residual_rows)}",
        f"Unique JP+fallback clusters  : {len(out_rows)}",
        "",
        "REASON BREAKDOWN (clusters / rows):",
    ]
    for name in sorted(reason_counts, key=lambda x:(reason_rank.get(x,9),x)):
        lines.append(f"- {name:28s}: {reason_counts[name]:3d} / {reason_rows[name]:3d}")
    lines += ["", "TOP 30 PRIORITY CLUSTERS:"]
    for i, r in enumerate(out_rows[:30], 1):
        lines.append(
            f"{i:02d}. x{r['count']:02d} [{r['reason']}] field={r['field_bytes']} fallback={r['fallback']!r} jp={r['japanese']!r} full={r['vi_full']!r}"
        )
    lines += [
        "",
        "NOTE:",
        "- inventory only; no ROM or source master mutation",
        "- protection is exact file+offset, never global fallback guessing",
        "- next batch should curate the highest-frequency safe clusters first",
        "",
        "RESULT: STATIC INVENTORY PASS",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

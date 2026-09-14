#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

VERSION = "0.6.36.0"
ROOT = Path(__file__).resolve().parent.parent
TR = ROOT / "translation"
OUT = TR / "BATCH27_ACCENT_PROMOTION_0.6.36.0.csv"
REPORT = ROOT / "checkpoints" / VERSION / "BATCH27_ACCENT_PROMOTION_REPORT.txt"
PARTS = [TR / f"TRANSLATION_MASTER_0.6_part{i:02d}.csv" for i in range(1, 7)]
EXACTS = [
    TR / "BATCH20_EXACT_OFFSET_0.6.29.0.csv",
    TR / "BATCH24_EXACT_OFFSET_0.6.33.0.csv",
]
TOKEN = re.compile(r"%(?:[-+0-9.#]*[A-Za-z])|/[Vv]")
FROZEN = set("àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ")


def rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def key(r):
    return r["file"].strip(), hex(int(r["offset_hex"], 0)).lower()


def tokens(text: str):
    return TOKEN.findall(text or "")


def safe_chars(text: str) -> bool:
    for ch in text or "":
        if ch in FROZEN:
            continue
        if ch == " " or 0x21 <= ord(ch) <= 0x7E:
            continue
        try:
            ch.encode("cp932")
        except Exception:
            return False
    return True


def rlen(text: str) -> int:
    n = 0
    pos = 0
    for m in TOKEN.finditer(text or ""):
        prefix = text[pos:m.start()]
        for ch in prefix:
            if ch in FROZEN or ch == " " or 0x21 <= ord(ch) <= 0x7E:
                n += 2
            else:
                n += len(ch.encode("cp932"))
        n += len(m.group(0).encode("ascii"))
        pos = m.end()
    for ch in (text or "")[pos:]:
        if ch in FROZEN or ch == " " or 0x21 <= ord(ch) <= 0x7E:
            n += 2
        else:
            n += len(ch.encode("cp932"))
    return n


def has_accent(text: str) -> bool:
    # We care about replacing legacy all-caps ASCII fallback with visibly Vietnamese text.
    return any(ord(ch) > 127 for ch in (text or "")) or any(ch.islower() for ch in (text or ""))


def main():
    master = []
    for p in PARTS:
        master.extend(rows(p))
    by_key = {key(r): r for r in master}

    exact_by_key = {}
    for p in EXACTS:
        for r in rows(p):
            exact_by_key[key(r)] = (r.get("vi_accented") or "").strip()

    # Japanese-keyed consensus only. Never infer semantics from accentless fallback.
    jp_candidates = defaultdict(set)
    jp_sources = defaultdict(list)
    for r in master:
        jp = (r.get("japanese") or "").strip()
        vi = (r.get("vi_full") or "").strip()
        if not jp or not vi or not safe_chars(vi) or tokens(jp) != tokens(vi):
            continue
        try:
            field = len(jp.encode("cp932"))
            if rlen(vi) <= field:
                jp_candidates[jp].add(vi)
                jp_sources[(jp, vi)].append("master-fit")
        except Exception:
            pass
    for k, vi in exact_by_key.items():
        src = by_key.get(k)
        if not src:
            continue
        jp = (src.get("japanese") or "").strip()
        if jp and vi and safe_chars(vi) and tokens(jp) == tokens(vi):
            jp_candidates[jp].add(vi)
            jp_sources[(jp, vi)].append(f"exact:{k[0]}:{k[1]}")

    consensus = {}
    ambiguous = {}
    for jp, vals in jp_candidates.items():
        if len(vals) == 1:
            consensus[jp] = next(iter(vals))
        elif vals:
            # If several proven translations exist, choose only when one is strictly shortest
            # and all keep identical runtime tokens. Otherwise leave ambiguous.
            ranked = sorted((rlen(v), v) for v in vals)
            if len(ranked) == 1 or ranked[0][0] < ranked[1][0]:
                consensus[jp] = ranked[0][1]
            else:
                ambiguous[jp] = sorted(vals)

    promotions = []
    fallback_runtime = 0
    exact_already = 0
    no_consensus = 0
    too_long = 0
    unsafe = 0

    for r in master:
        k = key(r)
        jp = (r.get("japanese") or "").strip()
        fallback = (r.get("vi_game_current") or "").strip()
        full = (r.get("vi_full") or "").strip()
        if not jp or not fallback:
            continue
        try:
            field = len(jp.encode("cp932"))
        except Exception:
            continue

        # Determine whether the current production row can still fall back to Alpha text.
        full_fits = bool(full and safe_chars(full) and tokens(jp) == tokens(full) and rlen(full) <= field)
        if full_fits:
            continue
        fallback_runtime += 1

        if k in exact_by_key:
            exact_already += 1
            continue
        cand = consensus.get(jp)
        if not cand:
            no_consensus += 1
            continue
        if not safe_chars(cand) or tokens(jp) != tokens(cand):
            unsafe += 1
            continue
        if rlen(cand) > field:
            too_long += 1
            continue
        if cand == fallback:
            continue
        promotions.append({
            "file": k[0],
            "offset_hex": k[1],
            "japanese": jp,
            "vi_accented": cand,
            "field_bytes": field,
            "vi_bytes": rlen(cand),
            "old_fallback": fallback,
            "source": "japanese-key-consensus",
        })

    promotions.sort(key=lambda r: (r["file"], int(r["offset_hex"], 16)))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        fields = ["file","offset_hex","japanese","vi_accented","field_bytes","vi_bytes","old_fallback","source"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(promotions)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"GAIA MASTER {VERSION} BATCH 27 ACCENT PROMOTION",
        "=" * 76,
        f"Translation Master rows             : {len(master)}",
        f"Japanese consensus keys             : {len(consensus)}",
        f"Ambiguous Japanese keys             : {len(ambiguous)}",
        f"Rows still capable of Alpha fallback: {fallback_runtime}",
        f"Already covered by B20/B24 exact    : {exact_already}",
        f"New safe accented promotions        : {len(promotions)}",
        f"No Japanese consensus               : {no_consensus}",
        f"Consensus too long                   : {too_long}",
        f"Unsafe/token rejected                : {unsafe}",
        "",
        "RULES:",
        "- Japanese-key consensus only; never infer meaning from accentless fallback.",
        "- Runtime tokens must preserve identity and order.",
        "- Candidate must fit original Japanese byte field.",
        "- Candidate must be CP932/frozen-60-codepage safe.",
        "- This batch only promotes rows that would otherwise fall back to Alpha text.",
        "",
        "RESULT: STATIC PROMOTION PASS",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

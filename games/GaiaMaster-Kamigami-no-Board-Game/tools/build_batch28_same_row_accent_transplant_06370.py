#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path

VERSION = "0.6.37.0"
ROOT = Path(__file__).resolve().parent.parent
TR = ROOT / "translation"
OUT = TR / "BATCH28_SAME_ROW_ACCENT_0.6.37.0.csv"
REPORT = ROOT / "checkpoints" / VERSION / "BATCH28_SAME_ROW_ACCENT_REPORT.txt"
PARTS = [TR / f"TRANSLATION_MASTER_0.6_part{i:02d}.csv" for i in range(1, 7)]
EXACTS = [
    TR / "BATCH20_EXACT_OFFSET_0.6.29.0.csv",
    TR / "BATCH24_EXACT_OFFSET_0.6.33.0.csv",
    TR / "BATCH27_ACCENT_PROMOTION_0.6.36.0.csv",
]
HIST = TR / "COMPACT_TRANSLATION_OVERRIDES_0.6.14.1.csv"
B19 = ROOT / "checkpoints" / "0.6.28.0" / "reports" / "GaiaMaster_0.6.28.0_EXACT_OFFSET_LOCKS.csv"
TOKEN = re.compile(r"%(?:[-+0-9.#]*[A-Za-z])|/[Vv]")
WORD = re.compile(r"[A-Za-z0-9]+")
FROZEN = set("àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ")


def rows(path: Path):
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def key(r):
    return r["file"].strip(), hex(int(r["offset_hex"], 0)).lower()


def fold(s: str) -> str:
    s = s.replace("Đ", "D").replace("đ", "d")
    return "".join(ch for ch in unicodedata.normalize("NFD", s) if unicodedata.category(ch) != "Mn").upper()


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
        for ch in text[pos:m.start()]:
            n += 2 if (ch in FROZEN or ch == " " or 0x21 <= ord(ch) <= 0x7E) else len(ch.encode("cp932"))
        n += len(m.group(0).encode("ascii"))
        pos = m.end()
    for ch in (text or "")[pos:]:
        n += 2 if (ch in FROZEN or ch == " " or 0x21 <= ord(ch) <= 0x7E) else len(ch.encode("cp932"))
    return n


def full_words(text: str):
    return [x for x in re.split(r"[^A-Za-zÀ-ỹĐđ]+", text or "") if x]


def transplant(fallback: str, full: str):
    """Return a same-word accented rewrite or None.

    No synonym translation happens here. A fallback token may match one full
    word or 2..4 consecutive full words after accent folding. Initialisms such
    as VK/SK are semantically matched but intentionally remain abbreviations.
    """
    fwords = full_words(full)
    if not fwords:
        return None
    folded = [fold(w) for w in fwords]
    out = []
    last = 0
    cursor = 0
    changed = False
    for m in WORD.finditer(fallback):
        out.append(fallback[last:m.start()])
        tok = m.group(0)
        ftok = fold(tok)
        replacement = tok
        found_end = None
        for i in range(cursor, len(fwords)):
            if folded[i] == ftok:
                replacement = fwords[i]
                found_end = i + 1
                break
            for width in range(2, 5):
                if i + width > len(fwords):
                    break
                joined = "".join(folded[i:i+width])
                if joined == ftok:
                    replacement = " ".join(fwords[i:i+width])
                    found_end = i + width
                    break
                initials = "".join(x[0] for x in folded[i:i+width] if x)
                if initials == ftok and len(ftok) >= 2:
                    replacement = tok
                    found_end = i + width
                    break
            if found_end is not None:
                break
        if found_end is None:
            return None
        cursor = found_end
        if replacement != tok:
            changed = True
        out.append(replacement)
        last = m.end()
    out.append(fallback[last:])
    candidate = "".join(out)
    return candidate if changed else None


def historical_protected(master_by_key):
    """Mirror Batch25 protection semantics.

    Only 0.6.14.1 rows that truly fit the original field, preserve runtime
    tokens and encode under the frozen runtime contract are locks. Batch19
    exact locks are compiler-proven and therefore unconditional.
    """
    protected = set()
    hist_fit = 0
    hist_skipped = 0
    for r in rows(HIST):
        k = key(r)
        src = master_by_key.get(k)
        text = (r.get("vi_accented") or "").strip()
        if src is None:
            hist_skipped += 1
            continue
        jp = src.get("japanese") or ""
        try:
            field = len(jp.encode("cp932"))
        except Exception:
            hist_skipped += 1
            continue
        if rlen(text) > field or tokens(jp) != tokens(text) or not safe_chars(text):
            hist_skipped += 1
            continue
        protected.add(k)
        hist_fit += 1
    b19_count = 0
    for r in rows(B19):
        protected.add(key(r))
        b19_count += 1
    return protected, hist_fit, hist_skipped, b19_count


def main():
    master = []
    for p in PARTS:
        master.extend(rows(p))
    master_by_key = {key(r): r for r in master}

    protected = set()
    for p in EXACTS:
        for r in rows(p):
            protected.add(key(r))
    hist_keys, hist_fit, hist_skipped, b19_count = historical_protected(master_by_key)
    protected.update(hist_keys)

    proposals = []
    examined = 0
    no_full = 0
    no_lexical_match = 0
    unsafe = 0
    too_long = 0
    token_bad = 0

    for r in master:
        k = key(r)
        fallback = (r.get("vi_game_current") or "").strip()
        full = (r.get("vi_full") or "").strip()
        jp = (r.get("japanese") or "").strip()
        if not fallback or k in protected:
            continue
        examined += 1
        if not full:
            no_full += 1
            continue
        cand = transplant(fallback, full)
        if not cand:
            no_lexical_match += 1
            continue
        if tokens(jp) != tokens(cand):
            token_bad += 1
            continue
        if not safe_chars(cand):
            unsafe += 1
            continue
        try:
            field = len(jp.encode("cp932"))
        except Exception:
            continue
        clen = rlen(cand)
        if clen > field:
            too_long += 1
            continue
        proposals.append({
            "file": k[0],
            "offset_hex": k[1],
            "japanese": jp,
            "vi_accented": cand,
            "field_bytes": field,
            "vi_bytes": clen,
            "old_fallback": fallback,
            "vi_full_reference": full,
            "source": "same-row-lexical-accent-transplant",
        })

    proposals.sort(key=lambda r: (r["file"], int(r["offset_hex"], 16)))
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        fields = ["file","offset_hex","japanese","vi_accented","field_bytes","vi_bytes","old_fallback","vi_full_reference","source"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(proposals)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"GAIA MASTER {VERSION} BATCH 28 SAME-ROW ACCENT TRANSPLANT",
        "=" * 78,
        f"Translation Master rows      : {len(master)}",
        f"Total protected exact keys   : {len(protected)}",
        f"Runtime-fit historical locks : {hist_fit}",
        f"Historical no-op/unfit rows  : {hist_skipped}",
        f"Batch19 exact lock rows       : {b19_count}",
        f"Fallback rows examined       : {examined}",
        f"New safe accent rewrites     : {len(proposals)}",
        f"No vi_full reference         : {no_full}",
        f"No lexical proof             : {no_lexical_match}",
        f"Too long                     : {too_long}",
        f"Unsafe codepage              : {unsafe}",
        f"Runtime token rejected       : {token_bad}",
        "",
        "SAFETY CONTRACT:",
        "- same row only: vi_game_current is compared to that row's vi_full",
        "- only accent/case/word-boundary transfer with accent-fold lexical proof",
        "- no synonym translation and no fallback-semantic inference",
        "- abbreviations such as VK/SK remain abbreviations",
        "- runtime-fit historical locks and Batch19 exact locks are never proposed again",
        "- runtime tokens must match identity/order",
        "- result must fit the original Japanese field",
        "- result must be frozen-codepage/CP932 safe",
        "",
        "RESULT: STATIC TRANSPLANT PASS",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

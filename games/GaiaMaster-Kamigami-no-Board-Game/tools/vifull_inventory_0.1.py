#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gaia Master vi_full Inventory 0.1
READ ONLY. No ROM patch. No emulator boot.

Fetches the six Translation Master 0.6 CSV files from the current Gaia branch,
then inventories the exact characters currently used by `vi_full`.

If internet fetch fails, place the six CSV files beside this script and rerun.
"""

from __future__ import print_function
import csv
import io
import os
import sys
import unicodedata
import urllib.request
from collections import Counter

BRANCH = "gaia-character-select-font-atlas-reverse-01"
REPO = "ronvotri/Viet-Hoa-PS1"
BASE = (
    "https://raw.githubusercontent.com/%s/%s/"
    "games/GaiaMaster-Kamigami-no-Board-Game/translation/"
    % (REPO, BRANCH)
)

FILES = [
    "TRANSLATION_MASTER_0.6_part01.csv",
    "TRANSLATION_MASTER_0.6_part02.csv",
    "TRANSLATION_MASTER_0.6_part03.csv",
    "TRANSLATION_MASTER_0.6_part04.csv",
    "TRANSLATION_MASTER_0.6_part05.csv",
    "TRANSLATION_MASTER_0.6_part06.csv",
]

# From Production Capacity Scanner 0.1 on the verified clean BIN.
ZERO_HIT_SLOT_CAPACITY = 64
UNMAPPED_ZERO_SLOT_CAPACITY = 34

ASCII_NATIVE = set(chr(i) for i in range(0x20, 0x7F))

# Punctuation which should be normalized at encode time instead of consuming
# a custom 12x12 Vietnamese slot.
NORMALIZE = {
    "\u2018": "'", "\u2019": "'",
    "\u201C": '"', "\u201D": '"',
    "\u2013": "-", "\u2014": "-",
    "\u2026": "...",
    "\u00A0": " ",
}

def is_vietnamese_precomposed(ch):
    if len(ch) != 1:
        return False
    if ch in ("đ", "Đ"):
        return True
    nfd = unicodedata.normalize("NFD", ch)
    if not nfd:
        return False
    base = nfd[0]
    marks = nfd[1:]
    if base not in "AaEeIiOoUuYy":
        return False
    allowed = {
        "\u0300", "\u0301", "\u0303", "\u0309", "\u0323",
        "\u0302", "\u0306", "\u031B",
    }
    return bool(marks) and all(m in allowed for m in marks)

def fetch_or_local(here, name):
    local = os.path.join(here, name)
    if os.path.isfile(local):
        with open(local, "rb") as f:
            return f.read(), "local"

    url = BASE + name
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "GaiaMaster-ViFullInventory/0.1"},
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read()
        try:
            with open(local, "wb") as f:
                f.write(data)
        except Exception:
            pass
        return data, url
    except Exception as e:
        raise RuntimeError(
            "Could not fetch %s (%s). Put all six Translation Master CSVs beside this script."
            % (name, e)
        )

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    rows = []
    sources = []

    for name in FILES:
        data, src = fetch_or_local(here, name)
        text = data.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        part_rows = list(reader)
        rows.extend(part_rows)
        sources.append((name, src, len(part_rows)))

    vi_rows = [r for r in rows if (r.get("vi_full") or "").strip()]
    texts = [(r.get("vi_full") or "").strip() for r in vi_rows]

    all_counter = Counter("".join(texts))
    unique = sorted(all_counter)

    custom_vi = [ch for ch in unique if is_vietnamese_precomposed(ch)]
    custom_vi.sort(key=lambda c: (c.lower(), c.islower(), ord(c)))

    lowercase = sorted(ch for ch in custom_vi if ch.islower())
    uppercase = sorted(ch for ch in custom_vi if ch.isupper())

    normalized_only = sorted(ch for ch in unique if ch in NORMALIZE)
    ascii_native = sorted(ch for ch in unique if ch in ASCII_NATIVE)

    other_unicode = []
    for ch in unique:
        if ch in ASCII_NATIVE:
            continue
        if ch in NORMALIZE:
            continue
        if is_vietnamese_precomposed(ch):
            continue
        other_unicode.append(ch)

    custom_freq = sorted(
        ((all_counter[ch], ch) for ch in custom_vi),
        key=lambda x: (-x[0], ord(x[1]))
    )

    report = []
    ap = report.append
    ap("GAIA MASTER vi_full INVENTORY 0.1")
    ap("=" * 88)
    ap("READ ONLY - KHONG SUA ROM - KHONG BOOT GAME")
    ap("")
    ap("Repository : %s" % REPO)
    ap("Branch     : %s" % BRANCH)
    ap("")
    ap("CSV SOURCES")
    ap("-" * 88)
    for name, src, n in sources:
        ap("%s rows=%d source=%s" % (name, n, src))
    ap("")
    ap("CORPUS")
    ap("-" * 88)
    ap("total Translation Master rows : %d" % len(rows))
    ap("rows with non-empty vi_full   : %d" % len(vi_rows))
    ap("unique characters in vi_full  : %d" % len(unique))
    ap("")
    ap("PRODUCTION 12x12 CUSTOM VIETNAMESE")
    ap("-" * 88)
    ap("unique Vietnamese precomposed custom chars : %d" % len(custom_vi))
    ap("lowercase custom chars                     : %d" % len(lowercase))
    ap("uppercase custom chars                     : %d" % len(uppercase))
    ap("known clean-atlas zero-hit capacity         : %d" % ZERO_HIT_SLOT_CAPACITY)
    ap("completely-unmapped zero-hit capacity       : %d" % UNMAPPED_ZERO_SLOT_CAPACITY)
    ap("")
    ap("custom set:")
    ap("".join(custom_vi) if custom_vi else "<none>")
    ap("")
    ap("lowercase:")
    ap("".join(lowercase) if lowercase else "<none>")
    ap("")
    ap("uppercase:")
    ap("".join(uppercase) if uppercase else "<none>")
    ap("")

    fits = len(custom_vi) <= ZERO_HIT_SLOT_CAPACITY
    strong_fits = len(custom_vi) <= UNMAPPED_ZERO_SLOT_CAPACITY

    ap("CAPACITY VERDICT")
    ap("-" * 88)
    ap("actual vi_full custom glyph need : %d" % len(custom_vi))
    ap("available zero-hit slots         : %d" % ZERO_HIT_SLOT_CAPACITY)
    ap("verdict                          : %s" % ("PASS" if fits else "FAIL"))
    ap("unmapped-only strong verdict     : %s" % ("PASS" if strong_fits else "NO"))
    ap("")

    if fits:
        ap("[PASS] Current vi_full corpus fits the proven 12x12 mapping-only architecture.")
        ap("Next: freeze a deterministic codepage for exactly this corpus,")
        ap("then build a multi-string production proof.")
    else:
        ap("[FAIL] Current vi_full corpus itself exceeds 64 clean slots.")
        ap("Next: reclaim translated Japanese slots or redesign allocation.")
    ap("")

    ap("CUSTOM CHAR FREQUENCY")
    ap("-" * 88)
    for count, ch in custom_freq:
        ap("U+%04X %-2s count=%d name=%s" %
           (ord(ch), ch, count, unicodedata.name(ch, "?")))
    ap("")

    ap("NORMALIZABLE UNICODE PUNCTUATION")
    ap("-" * 88)
    if normalized_only:
        for ch in normalized_only:
            ap("U+%04X %r -> %r count=%d" %
               (ord(ch), ch, NORMALIZE[ch], all_counter[ch]))
    else:
        ap("<none>")
    ap("")

    ap("OTHER NON-ASCII / NON-VIETNAMESE CHARACTERS NEEDING POLICY")
    ap("-" * 88)
    if other_unicode:
        for ch in other_unicode:
            ap("U+%04X %r count=%d name=%s" %
               (ord(ch), ch, all_counter[ch], unicodedata.name(ch, "?")))
    else:
        ap("<none>")
    ap("")

    ap("ASCII/NATIVE CHARACTERS PRESENT")
    ap("-" * 88)
    ap("".join(ascii_native))

    out = os.path.join(here, "GaiaMaster_ViFullInventory_01.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(report) + "\n")

    print("[OK] vi_full inventory complete.")
    print("Translation rows total :", len(rows))
    print("Rows with vi_full      :", len(vi_rows))
    print("Custom VI glyphs       :", len(custom_vi))
    print("Zero-hit slot capacity :", ZERO_HIT_SLOT_CAPACITY)
    print("Verdict                :", "PASS" if fits else "FAIL")
    print("Report:", out)
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("[ERROR]", repr(e))
        sys.exit(9)

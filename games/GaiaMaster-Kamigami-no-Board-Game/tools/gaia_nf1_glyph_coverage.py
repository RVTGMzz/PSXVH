#!/usr/bin/env python3
from __future__ import annotations
import csv,unicodedata
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TR=ROOT/"translation"
MASTERS=[TR/f"TRANSLATION_MASTER_0.6_part{i:02d}.csv" for i in range(1,7)]
OUT=ROOT/"font_experiment"
VI_BASE=set("ĂÂĐÊÔƠƯăâđêôơư")
ASCII_LATIN=set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
DIGITS=set("0123456789")

def is_vi(ch):
    if ch in VI_BASE:return True
    name=unicodedata.name(ch,"")
    return any(x in name for x in ("WITH ACUTE","WITH GRAVE","WITH HOOK ABOVE","WITH TILDE","WITH DOT BELOW","WITH BREVE","WITH CIRCUMFLEX","WITH HORN","WITH STROKE")) and ("LATIN" in name)

def main():
    texts=[]
    for p in MASTERS:
        if not p.is_file():raise RuntimeError(f"Missing translation master: {p}")
        with p.open("r",encoding="utf-8-sig",newline="") as f:
            for r in csv.DictReader(f):
                s=(r.get("vi_full") or "").strip()
                if s:texts.append(s)
    c=Counter("".join(texts))
    chars=sorted(c,key=lambda x:(ord(x),x))
    OUT.mkdir(exist_ok=True)
    csvp=OUT/"NF1_GLYPH_COVERAGE.csv"
    with csvp.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.writer(f);w.writerow(["char","codepoint","count","category","unicode_name"])
        for ch in chars:
            if ch.isspace():cat="space"
            elif ch in ASCII_LATIN:cat="latin"
            elif ch in DIGITS:cat="digit"
            elif is_vi(ch):cat="vietnamese"
            elif unicodedata.category(ch).startswith("P"):cat="punctuation"
            else:cat="other"
            w.writerow([ch,f"U+{ord(ch):04X}",c[ch],cat,unicodedata.name(ch,"")])
    cats=Counter()
    for ch in chars:
        if ch.isspace():cats["space"]+=1
        elif ch in ASCII_LATIN:cats["latin"]+=1
        elif ch in DIGITS:cats["digit"]+=1
        elif is_vi(ch):cats["vietnamese"]+=1
        elif unicodedata.category(ch).startswith("P"):cats["punctuation"]+=1
        else:cats["other"]+=1
    rp=OUT/"NF1_GLYPH_COVERAGE_REPORT.txt"
    lines=["GAIA MASTER NF1 GLYPH COVERAGE","="*60,
           f"translation rows with vi_full: {len(texts)}",
           f"unique Unicode characters: {len(chars)}",
           f"latin ASCII: {cats['latin']}",
           f"Vietnamese-specific/precomposed: {cats['vietnamese']}",
           f"digits: {cats['digit']}",
           f"punctuation: {cats['punctuation']}",
           f"other: {cats['other']}","",
           "This is source-text coverage only. It does not imply all glyphs can be mapped into the current atlas.",
           "NF1 must reconcile this inventory with Gaia's proven mapping/slot capacity before any ROM build.",
           "Runtime PASS remains NO."]
    rp.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("\n".join(lines));print("CSV:",csvp);print("Report:",rp)

if __name__=="__main__":
    main()

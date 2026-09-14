#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import csv,re
from pathlib import Path
VERSION="0.6.51.0"
ROOT=Path(__file__).resolve().parent.parent;TR=ROOT/"translation"
PARTS=[TR/f"TRANSLATION_MASTER_0.6_part{i:02d}.csv" for i in range(1,7)]
FINAL=TR/"BATCH40_FINAL_EXACT_SET_0.6.50.0.csv"
B19=ROOT/"checkpoints"/"0.6.28.0"/"reports"/"GaiaMaster_0.6.28.0_EXACT_OFFSET_LOCKS.csv"
HIST=TR/"COMPACT_TRANSLATION_OVERRIDES_0.6.14.1.csv"
REPORT=ROOT/"checkpoints"/VERSION/"BATCH41_MASTER_COVERAGE_AUDIT.txt"
TOKEN=re.compile(r"%(?:[-+0-9.#]*[A-Za-z%])|/[Vv]")
FROZEN=set("àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ")
def rows(p):
    if not p.is_file():return []
    with p.open("r",encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def key(r):return r["file"].strip(),hex(int(r["offset_hex"],0)).lower()
def toks(t):return tuple(m.group(0) for m in TOKEN.finditer(t or ""))
def rlen(t):
    n=0;pos=0
    for m in TOKEN.finditer(t or ""):
        n+=(m.start()-pos)*2+len(m.group(0).encode("ascii"));pos=m.end()
    return n+(len(t or "")-pos)*2
def bad(t):
    out=[]
    for ch in t or "":
        if ord(ch)<128:continue
        try:ch.encode("cp932");continue
        except UnicodeEncodeError:pass
        if ch not in FROZEN:out.append(ch)
    return sorted(set(out))
def master():
    out=[];seen=set()
    for p in PARTS:
        for r in rows(p):
            k=key(r)
            if k in seen:raise RuntimeError(f"duplicate master key {k}")
            seen.add(k);out.append(r)
    if len(out)!=596:raise RuntimeError(f"master gate {len(out)} != 596")
    return out
def hist_fit(m):
    by={key(r):r for r in m};out=set()
    for r in rows(HIST):
        k=key(r);src=by.get(k);txt=(r.get("vi_accented") or "").strip()
        if not src or not txt:continue
        jp=src.get("japanese") or ""
        try:f=len(jp.encode("cp932"))
        except UnicodeEncodeError:continue
        if rlen(txt)<=f and toks(jp)==toks(txt) and not bad(txt):out.add(k)
    return out
def main():
    m=master();all_keys={key(r) for r in m};exact={key(r) for r in rows(FINAL)};b19={key(r) for r in rows(B19)};hist=hist_fit(m)
    covered=exact|b19|hist;uncovered=sorted(all_keys-covered,key=lambda k:(k[0],int(k[1],16)))
    by={key(r):r for r in m};uncovered_fb=[k for k in uncovered if (by[k].get("vi_game_current") or "").strip()]
    uncovered_full=[k for k in uncovered if (by[k].get("vi_full") or "").strip()]
    lines=[f"GAIA MASTER {VERSION} BATCH 41 FULL MASTER COVERAGE AUDIT","="*84,
           f"Translation Master rows       : {len(m)}",f"Batch40 final exact keys      : {len(exact)}",
           f"Batch19 exact locks           : {len(b19)}",f"Runtime-fit historical locks  : {len(hist)}",
           f"Union covered master keys     : {len(covered & all_keys)} / {len(all_keys)}",
           f"Uncovered master keys         : {len(uncovered)}",f"Uncovered with Alpha fallback : {len(uncovered_fb)}",
           f"Uncovered with vi_full        : {len(uncovered_full)}","",
           "NOTE:","- Coverage means key is protected by Batch40 exact, Batch19 exact, or a runtime-fit historical lock.",
           "- This audit covers only the current 596-row Translation Master; it does NOT claim whole-game text coverage.",
           "- Story/tutorial/help strings discovered outside this master still require whole-game scanner expansion."]
    if uncovered:
        lines += ["","UNCOVERED:"]
        for k in uncovered:
            r=by[k];lines.append(f"- {k[0]} {k[1]} jp={r.get('japanese','')!r} fallback={(r.get('vi_game_current') or '').strip()!r} full={(r.get('vi_full') or '').strip()!r}")
    result="PASS" if not uncovered_fb else "REVIEW"
    lines += ["",f"RESULT: MASTER FALLBACK COVERAGE {result}"]
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text("\n".join(lines)+"\n",encoding="utf-8");print("\n".join(lines))
    return 0 if not uncovered_fb else 1
if __name__=="__main__":raise SystemExit(main())

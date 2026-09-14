#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import re
from pathlib import Path

VERSION="0.6.47.0"
ROOT=Path(__file__).resolve().parent.parent
TR=ROOT/"translation"
PARTS=[TR/f"TRANSLATION_MASTER_0.6_part{i:02d}.csv" for i in range(1,7)]
B33_NEW=TR/"BATCH33_NEW_EXACT_OFFSET_0.6.43.0.csv"
B33_FINAL=TR/"BATCH33_FINAL_EXACT_SET_0.6.43.0.csv"
B36=TR/"BATCH36_CURATED_COMPACT_0.6.46.0.csv"
OUT_NEW=TR/"BATCH37_NEW_EXACT_OFFSET_0.6.47.0.csv"
OUT_FINAL=TR/"BATCH37_FINAL_EXACT_SET_0.6.47.0.csv"
REPORT=ROOT/"checkpoints"/VERSION/"BATCH37_MERGE_REPORT.txt"
TOKEN=re.compile(r"%(?:[-+0-9.#]*[A-Za-z%])|/[Vv]")
FROZEN=set("àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ")
EXPECTED_NEW=514
EXPECTED_FINAL=527

def rows(path):
    with path.open("r",encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def key(r):return r["file"].strip(),hex(int(r["offset_hex"],0)).lower()
def tokens(t):return tuple(m.group(0) for m in TOKEN.finditer(t or ""))
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
def master_index():
    out={}
    for p in PARTS:
        for r in rows(p):
            k=key(r)
            if k in out:raise RuntimeError(f"duplicate master key {k}")
            out[k]=r
    if len(out)!=596:raise RuntimeError(f"master gate {len(out)} != 596")
    return out
def norm(r,source,category,master):
    k=key(r);src=master.get(k)
    if not src:raise RuntimeError(f"missing master source {k}")
    jp=src.get("japanese") or "";text=(r.get("vi_accented") or "").strip();field=len(jp.encode("cp932"));used=rlen(text)
    if used>field:raise RuntimeError(f"too long {used}>{field}: {k} {text!r}")
    if tokens(jp)!=tokens(text):raise RuntimeError(f"token mismatch {k}")
    b=bad(text)
    if b:raise RuntimeError(f"unsupported chars {b!r}: {k} {text!r}")
    return {"file":k[0],"offset_hex":k[1],"japanese":jp,"vi_accented":text,"field_bytes":field,"vi_bytes":used,"free_bytes":field-used,"source":source,"category":category}
def merge(dest,rec):
    k=(rec["file"],rec["offset_hex"]);old=dest.get(k)
    if old and old["vi_accented"]!=rec["vi_accented"]:raise RuntimeError(f"wording conflict {k}: {old['vi_accented']!r} vs {rec['vi_accented']!r}")
    dest[k]=rec
def write(path,data):
    fields=["file","offset_hex","japanese","vi_accented","field_bytes","vi_bytes","free_bytes","source","category"]
    with path.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(sorted(data.values(),key=lambda r:(r["file"],int(r["offset_hex"],16))))
def main():
    master=master_index();new={};final={};errors=[]
    for r in rows(B33_NEW):merge(new,norm(r,B33_NEW.name,"batch37-new-exact",master))
    for r in rows(B33_FINAL):merge(final,norm(r,B33_FINAL.name,"batch37-final-exact",master))
    for r in rows(B36):
        nr=norm(r,B36.name,"batch37-new-exact",master);fr=dict(nr);fr["category"]="batch37-final-exact";merge(new,nr);merge(final,fr)
    if len(new)!=EXPECTED_NEW:errors.append(f"new exact count {len(new)} != {EXPECTED_NEW}")
    if len(final)!=EXPECTED_FINAL:errors.append(f"final exact count {len(final)} != {EXPECTED_FINAL}")
    if not set(new).issubset(final):errors.append("new set not subset of final set")
    OUT_NEW.parent.mkdir(parents=True,exist_ok=True);write(OUT_NEW,new);write(OUT_FINAL,final)
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    lines=[f"GAIA MASTER {VERSION} BATCH 37 LARGE MERGE","="*76,
           f"B33 new rows               : {len(rows(B33_NEW))}",f"B33 final rows             : {len(rows(B33_FINAL))}",
           f"B36 curated rows           : {len(rows(B36))}",f"Merged new exact targets   : {len(new)}",
           f"Merged final verify set    : {len(final)}",f"Errors                     : {len(errors)}","",
           "Guards:","- merge by exact file+offset","- revalidate byte fit, runtime tokens and frozen codepage","- wording conflicts hard-fail","- no ROM/font/pointer modification"]
    if errors:lines += ["","ERRORS:"]+[f"- {e}" for e in errors]
    else:lines += ["","RESULT: STATIC MERGE PASS"]
    REPORT.write_text("\n".join(lines)+"\n",encoding="utf-8");print("\n".join(lines));return 1 if errors else 0
if __name__=="__main__":raise SystemExit(main())

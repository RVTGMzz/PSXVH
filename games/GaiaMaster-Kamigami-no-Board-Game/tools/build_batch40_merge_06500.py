#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import csv,re
from pathlib import Path
VERSION="0.6.50.0"
ROOT=Path(__file__).resolve().parent.parent;TR=ROOT/"translation"
PARTS=[TR/f"TRANSLATION_MASTER_0.6_part{i:02d}.csv" for i in range(1,7)]
B37_NEW=TR/"BATCH37_NEW_EXACT_OFFSET_0.6.47.0.csv";B37_FINAL=TR/"BATCH37_FINAL_EXACT_SET_0.6.47.0.csv";B39=TR/"BATCH39_MASTER_CLOSURE_0.6.49.0.csv"
OUT_NEW=TR/"BATCH40_NEW_EXACT_OFFSET_0.6.50.0.csv";OUT_FINAL=TR/"BATCH40_FINAL_EXACT_SET_0.6.50.0.csv";REPORT=ROOT/"checkpoints"/VERSION/"BATCH40_MERGE_REPORT.txt"
TOKEN=re.compile(r"%(?:[-+0-9.#]*[A-Za-z%])|/[Vv]");FROZEN=set("àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ")
EXPECTED_NEW=547;EXPECTED_FINAL=560

def rows(p):
    with p.open("r",encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
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
            if k in out:raise RuntimeError(f"duplicate master {k}")
            out[k]=r
    if len(out)!=596:raise RuntimeError(f"master gate {len(out)} != 596")
    return out
def norm(r,source,category,master):
    k=key(r);src=master.get(k)
    if not src:raise RuntimeError(f"missing master {k}")
    jp=src.get("japanese") or "";txt=(r.get("vi_accented") or "").strip();field=len(jp.encode("cp932"));used=rlen(txt)
    if used>field:raise RuntimeError(f"too long {used}>{field}: {k}")
    if tokens(jp)!=tokens(txt):raise RuntimeError(f"token mismatch {k}")
    b=bad(txt)
    if b:raise RuntimeError(f"unsupported {b!r}: {k}")
    return {"file":k[0],"offset_hex":k[1],"japanese":jp,"vi_accented":txt,"field_bytes":field,"vi_bytes":used,"free_bytes":field-used,"source":source,"category":category}
def merge(d,r):
    k=(r["file"],r["offset_hex"]);old=d.get(k)
    if old and old["vi_accented"]!=r["vi_accented"]:raise RuntimeError(f"wording conflict {k}: {old['vi_accented']!r} vs {r['vi_accented']!r}")
    d[k]=r
def write(p,d):
    fs=["file","offset_hex","japanese","vi_accented","field_bytes","vi_bytes","free_bytes","source","category"]
    with p.open("w",encoding="utf-8-sig",newline="") as f:w=csv.DictWriter(f,fieldnames=fs,lineterminator="\n");w.writeheader();w.writerows(sorted(d.values(),key=lambda r:(r["file"],int(r["offset_hex"],16))))
def main():
    master=master_index();new={};final={};errors=[]
    for r in rows(B37_NEW):merge(new,norm(r,B37_NEW.name,"batch40-new-exact",master))
    for r in rows(B37_FINAL):merge(final,norm(r,B37_FINAL.name,"batch40-final-exact",master))
    for r in rows(B39):
        nr=norm(r,B39.name,"batch40-new-exact",master);fr=dict(nr);fr["category"]="batch40-final-exact";merge(new,nr);merge(final,fr)
    if len(new)!=EXPECTED_NEW:errors.append(f"new count {len(new)} != {EXPECTED_NEW}")
    if len(final)!=EXPECTED_FINAL:errors.append(f"final count {len(final)} != {EXPECTED_FINAL}")
    if not set(new).issubset(final):errors.append("new set not subset final")
    OUT_NEW.parent.mkdir(parents=True,exist_ok=True);write(OUT_NEW,new);write(OUT_FINAL,final);REPORT.parent.mkdir(parents=True,exist_ok=True)
    lines=[f"GAIA MASTER {VERSION} BATCH 40 MASTER-CLOSURE MERGE","="*80,f"B37 new rows               : {len(rows(B37_NEW))}",f"B37 final rows             : {len(rows(B37_FINAL))}",f"B39 closure rows           : {len(rows(B39))}",f"Merged new exact targets   : {len(new)}",f"Merged final verify set    : {len(final)}",f"Errors                     : {len(errors)}","","Guards:","- merge by exact file+offset","- byte fit/token/codepage revalidated","- conflicts hard-fail","- no ROM/font/pointer modification"]
    if errors:lines += ["","ERRORS:"]+[f"- {e}" for e in errors]
    else:lines += ["","RESULT: STATIC MERGE PASS"]
    REPORT.write_text("\n".join(lines)+"\n",encoding="utf-8");print("\n".join(lines));return 1 if errors else 0
if __name__=="__main__":raise SystemExit(main())

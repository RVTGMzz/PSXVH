#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import csv,re
from pathlib import Path
VERSION="0.6.49.0"
ROOT=Path(__file__).resolve().parent.parent;TR=ROOT/"translation"
PARTS=[TR/f"TRANSLATION_MASTER_0.6_part{i:02d}.csv" for i in range(1,7)]
PROTECTED_FINAL=TR/"BATCH37_FINAL_EXACT_SET_0.6.47.0.csv"
HIST=TR/"COMPACT_TRANSLATION_OVERRIDES_0.6.14.1.csv"
B19=ROOT/"checkpoints"/"0.6.28.0"/"reports"/"GaiaMaster_0.6.28.0_EXACT_OFFSET_LOCKS.csv"
OUT=TR/"BATCH39_MASTER_CLOSURE_0.6.49.0.csv"
REPORT=ROOT/"checkpoints"/VERSION/"BATCH39_MASTER_CLOSURE_REPORT.txt"
TOKEN=re.compile(r"%(?:[-+0-9.#]*[A-Za-z%])|/[Vv]")
FROZEN=set("àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ")
CURATED={
"売却":"B.","ームができ、勝":"Thắng","クレイモア":"Claym","ダンテ":"Dte","じしん":"ĐĐ","地震":"ĐĐ",
"ガラハッド":"Galhd","価格":"G.","価値":"GT","ゴライアス":"Golia","ハヤテ":"Hyt","ジガー":"Jig","クナイ":"Kun",
"Ｌ/V%d（あと/V%d）":"L/V%d C/V%d","幸運":"M.","メグメグ":"Megu","バンク":"NH","浴場":"T.","レイピア":"Rapi",
"落雷":"S.","お店":"CH","シンバッド":"Sinba","温泉":"SN","勝利者":"VĐ","丸薬":"T.","基本武器":"VKCB",
"資金":"V.","庭園":"V.","ワープ":"DC","不幸":"X.","ヤスツナ":"Yasu","「地震」":"「ĐĐ」","/V%sさん/v":"/V%s/v",
}
def rows(p):
    if not p.is_file():return []
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
def master_rows():
    out=[];seen=set()
    for p in PARTS:
        for r in rows(p):
            k=key(r)
            if k in seen:raise RuntimeError(f"duplicate master {k}")
            seen.add(k);out.append(r)
    if len(out)!=596:raise RuntimeError(f"master gate {len(out)} != 596")
    return out
def historical_fit(master):
    by={key(r):r for r in master};out=set()
    for r in rows(HIST):
        k=key(r);src=by.get(k);txt=(r.get("vi_accented") or "").strip()
        if not src or not txt:continue
        jp=src.get("japanese") or ""
        try:field=len(jp.encode("cp932"))
        except UnicodeEncodeError:continue
        if rlen(txt)<=field and tokens(jp)==tokens(txt) and not bad(txt):out.add(k)
    return out
def main():
    master=master_rows();protected={key(r) for r in rows(PROTECTED_FINAL)}|{key(r) for r in rows(B19)}|historical_fit(master)
    out=[];errors=[];hits={jp:0 for jp in CURATED};skipped=0
    for r in master:
        k=key(r);jp=(r.get("japanese") or "").strip();fb=(r.get("vi_game_current") or "").strip()
        if jp not in CURATED or not fb:continue
        hits[jp]+=1
        if k in protected:skipped+=1;continue
        txt=CURATED[jp];field=len(jp.encode("cp932"));used=rlen(txt)
        if used>field:errors.append(f"too long {used}>{field}: {k} {txt!r}");continue
        if tokens(jp)!=tokens(txt):errors.append(f"token mismatch {k}: {tokens(jp)} != {tokens(txt)}");continue
        b=bad(txt)
        if b:errors.append(f"unsupported chars {b!r}: {k} {txt!r}");continue
        out.append({"file":k[0],"offset_hex":k[1],"japanese":jp,"vi_accented":txt,"field_bytes":field,"vi_bytes":used,"free_bytes":field-used,"source":"BATCH39_MASTER_CLOSURE_0.6.49.0","category":"batch39-master-closure"})
    miss=[jp for jp,n in hits.items() if not n]
    if miss:errors.append(f"missing curated keys: {miss!r}")
    if len(out)!=33:errors.append(f"closure row count {len(out)} != 33")
    OUT.parent.mkdir(parents=True,exist_ok=True);fields=["file","offset_hex","japanese","vi_accented","field_bytes","vi_bytes","free_bytes","source","category"]
    with OUT.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(sorted(out,key=lambda r:(r["file"],int(r["offset_hex"],16))))
    REPORT.parent.mkdir(parents=True,exist_ok=True);full=sum(1 for r in out if int(r["free_bytes"])==0)
    lines=[f"GAIA MASTER {VERSION} BATCH 39 MASTER RESIDUAL CLOSURE","="*80,f"Curated Japanese keys       : {len(CURATED)}",f"Closure rows exported       : {len(out)}",f"Protected hits skipped      : {skipped}",f"Exact-full-field rows       : {full}",f"Errors                      : {len(errors)}","","Guards:","- exact Japanese-keyed manual closure","- B37/Batch19/runtime-fit historical keys protected","- runtime token identity/order preserved","- CP932 field byte-fit required","- frozen Vietnamese codepage required","- no ROM/font/pointer modification"]
    if errors:lines += ["","ERRORS:"]+[f"- {e}" for e in errors]
    else:lines += ["","RESULT: STATIC MASTER-CLOSURE PASS"]
    REPORT.write_text("\n".join(lines)+"\n",encoding="utf-8");print("\n".join(lines));return 1 if errors else 0
if __name__=="__main__":raise SystemExit(main())

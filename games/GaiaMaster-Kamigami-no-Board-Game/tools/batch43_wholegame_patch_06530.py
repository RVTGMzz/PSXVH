#!/usr/bin/env python3
from __future__ import annotations
import csv,re,struct
from pathlib import Path
import build_gaia_06100_hybrid_accent_b1_READABLE as base

ROOT=Path(__file__).resolve().parent.parent
MANIFEST=ROOT/"translation"/"BATCH43_WHOLEGAME_VISIBLE_0.6.53.0.csv"
B40=ROOT/"translation"/"BATCH40_FINAL_EXACT_SET_0.6.50.0.csv"
EXPECTED=102
TOKEN=re.compile(r"%(?:[-+0-9.#]*[A-Za-z])|/[Vv]")

def rows(path):
    with path.open("r",encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))

def runtime_len(text):
    fake={ch:0x889F+i for i,ch in enumerate(base.CUSTOM_CHARS)}
    return len(base.encode_runtime_text(text,fake)[0])

def load_manifest():
    rr=rows(MANIFEST)
    if len(rr)!=EXPECTED:raise RuntimeError(f"Batch43 row gate {len(rr)} != {EXPECTED}")
    old={(r["file"].strip(),int(r["offset_hex"],0)) for r in rows(B40)}
    out=[];seen=set()
    for r in rr:
        key=(r["file"].strip(),int(r["offset_hex"],0))
        if key in seen:raise RuntimeError(f"duplicate {key}")
        if key in old:raise RuntimeError(f"Batch40 overlap {key}")
        seen.add(key)
        if key[0]!="PRGPACK.BDP" or r["confidence"]!="HIGH":raise RuntimeError(f"bad source gate {key}")
        jp=r["japanese"];vi=r["vi_accented"];field=int(r["field_bytes"])
        if TOKEN.findall(jp)!=TOKEN.findall(vi):raise RuntimeError(f"token mismatch {key}")
        n=runtime_len(vi)
        if n>field:raise RuntimeError(f"overflow {key}: {n}>{field}")
        out.append((key[1],jp,vi,field))
    spans=sorted((o,o+f) for o,_,_,f in out)
    if any(spans[i][0]<spans[i-1][1] for i in range(1,len(spans))):raise RuntimeError("Batch43 field overlap")
    return out

def patch(clean:Path,built:Path):
    rr=load_manifest()
    with clean.open("rb") as f:
        slps=base.read_iso_file(f,base.SLPS_EXTENT,base.SLPS_SIZE);clean_prg=base.read_iso_file(f,base.PRG_EXTENT,base.PRG_SIZE)
    cmap=dict(zip(base.CUSTOM_CHARS,base.safe_custom_codes(slps,clean_prg,len(base.CUSTOM_CHARS))))
    with built.open("rb") as f:prg=base.read_iso_file(f,base.PRG_EXTENT,base.PRG_SIZE)
    entries=base.parse_bdp_entries(prg);new=bytearray(prg);touched=set()
    for off,jp,vi,field in rr:
        enc,_=base.encode_runtime_text(vi,cmap);cur=bytes(new[off:off+field])
        try:norm=cur.decode("cp932").strip(" \u3000")
        except Exception:norm=None
        if norm!=jp:raise RuntimeError(f"source mismatch 0x{off:X}: {norm!r} != {jp!r}")
        owner,s,e=base.owner_for_offset(entries,off)
        if off+field+1>e or new[off+field]!=0:raise RuntimeError(f"field boundary gate 0x{off:X}")
        new[off:off+field]=enc+b"\0"*(field-len(enc));touched.add(owner)
    by={i:(s,e) for i,s,e in entries}
    for i in touched:
        s,e=by[i];struct.pack_into("<I",new,s+4,base.bdp_checksum(bytearray(new[s:e])))
    struct.pack_into("<I",new,4,base.bdp_checksum(new));base.parse_bdp_entries(bytes(new))
    changed=set()
    with built.open("r+b") as f:
        base.write_changed_iso_file(f,base.PRG_EXTENT,prg,bytes(new),changed)
        for sec in sorted(changed):
            f.seek(sec*2352);raw=f.read(2352);f.seek(sec*2352);f.write(base.regen_sector(raw))
    with built.open("rb") as f:chk=base.read_iso_file(f,base.PRG_EXTENT,base.PRG_SIZE)
    base.parse_bdp_entries(chk)
    for off,jp,vi,field in rr:
        enc,_=base.encode_runtime_text(vi,cmap);cur=bytes(chk[off:off+field])
        if cur[:len(enc)]!=enc or any(cur[len(enc):]):raise RuntimeError(f"verify fail 0x{off:X}")
    return len(rr),len(changed),len(touched)

if __name__=="__main__":
    rr=load_manifest();print("BATCH43 STATIC PASS");print("rows=",len(rr))

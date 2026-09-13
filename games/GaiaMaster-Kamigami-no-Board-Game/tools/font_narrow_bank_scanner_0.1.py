#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gaia Master Font Narrow Bank Scanner 0.1
READ ONLY. Does not modify the ROM and does not boot the game.

Purpose
-------
Test whether Gaia Master's EXISTING native 1-byte narrow glyph bank can provide
>=9 isolated 8px-advance glyph sources for the real Vietnamese proof "Chọn tướng".

Reverse facts used:
- Character Select/native 12px class uses state dimension 11.
- metric setter gives state+0x3E = 8 for dimension 11.
- 1-byte codes avoid the Japanese multibyte full-width classifier.
- halfwidth table RAM = 0x8007E01C.
- native narrow source base RAM = 0x8006BAAC.
- for dimension 11, narrow source rows are 12 rows, 3 bytes per glyph per row,
  with two glyph halves interleaved in a 6-byte row.
- narrow copy returns 8, so cache-miss advance uses native state+0x3E = 8.

IMPORTANT: static scanner only. No runtime build from this alone.
"""
from __future__ import print_function
import hashlib, os, struct, sys

EXPECTED_BIN_SHA1="f4d5298583c90d89c4b7e51d2dde160ee07f2aec"
EXPECTED_SLPS_SHA1="1dfeb6b7cfda59c108dde2dc0b8abda9a40e6ae5"
EXPECTED_PRG_SHA1="a9b195b8ae5d8cad7f4f755daa08337d4671632c"
SLPS_EXTENT=24; SLPS_SIZE=487424; PRG_EXTENT=2679; PRG_SIZE=1534236
LOAD_BASE=0x8000F800
HALF_TABLE_RAM=0x8007E01C; NARROW_BASE_RAM=0x8006BAAC; ATLAS_RAM=0x8006BCEC
HALF_TABLE_OFF=HALF_TABLE_RAM-LOAD_BASE; NARROW_BASE_OFF=NARROW_BASE_RAM-LOAD_BASE; ATLAS_OFF=ATLAS_RAM-LOAD_BASE
CHARSEL_DIMENSION=11; ROWS=12; NARROW_ADVANCE=8; PAIR_ROW_BYTES=6; GLYPH_ROW_BYTES=3; PAIR_BYTES=72; NARROW_INDEX_COUNT=15
OLD_ZERO_RUN_START=0x05C0E0; OLD_ZERO_RUN_END=0x05C2B8
PROOF_UNITS=["C","h","ọ","n","SPACE","t","ư","ớ","g"]

def sha1_bytes(d): h=hashlib.sha1(); h.update(d); return h.hexdigest()
def sha1_file(p):
    h=hashlib.sha1()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(8*1024*1024),b""): h.update(b)
    return h.hexdigest()
def read_iso_file(f,extent,size):
    out=bytearray(); rem=size; sec=extent
    while rem:
        n=min(2048,rem); f.seek(sec*2352+24); b=f.read(n)
        if len(b)!=n: raise RuntimeError("Short read at raw sector %d"%sec)
        out.extend(b); rem-=n; sec+=1
    return bytes(out)
def cp932_char(code):
    try: return bytes([code]).decode("cp932")
    except Exception: return None
def valid_sjis_trail(b): return (0x40<=b<=0x7E) or (0x80<=b<=0xFC)
def decode_gaia_text_segment(seg):
    toks=[]; i=0
    while i<len(seg):
        b=seg[i]
        if 0x20<=b<=0x7E or 0xA0<=b<=0xDF: toks.append(("one",b)); i+=1; continue
        if (0x81<=b<=0x9F) or (0xE0<=b<=0xFC):
            if i+1>=len(seg) or not valid_sjis_trail(seg[i+1]) or seg[i+1]==0x7F: return None
            toks.append(("two",(b<<8)|seg[i+1])); i+=2; continue
        return None
    return toks
def strict_nul_text_hits(blob,wanted):
    hits={c:0 for c in wanted}; examples={c:[] for c in wanted}; start=0
    while start<len(blob):
        end=blob.find(b"\x00",start)
        if end<0: break
        seg=blob[start:end]
        if 2<=len(seg)<=512:
            toks=decode_gaia_text_segment(seg)
            if toks is not None and len(toks)>=2 and (any(k=="two" for k,v in toks) or len(toks)>=4):
                for k,v in toks:
                    if k=="one" and v in hits:
                        hits[v]+=1
                        if len(examples[v])<3: examples[v].append((start,blob[start:min(end,start+80)]))
        start=end+1
    return hits,examples
def remap_dim11(a1):
    if a1==10:return 10
    if a1==12:return 11
    if a1==57:return 12
    if a1 in (87,55):return 13
    if a1==13:return 14
    return a1
def source_for_index(idx):
    if not 0<=idx<15:return None
    off=NARROW_BASE_OFF+3*((idx&~1)*ROWS)+3*(idx&1)
    return LOAD_BASE+off,off
def effective_glyph_bytes(slps,idx):
    ram,off=source_for_index(idx); out=bytearray()
    for r in range(ROWS): out.extend(slps[off+r*6:off+r*6+3])
    return bytes(out)
def full_source_span(idx):
    ram,off=source_for_index(idx); return off,off+(ROWS-1)*6+3
def table_entry(slps,code):
    off=HALF_TABLE_OFF+(code-0xA0)*2
    return struct.unpack_from("<H",slps,off)[0]
def resolve_aliases(slps):
    rec=[]
    for c in range(0x21,0x80):
        raw=c-33; fin=remap_dim11(raw)
        rec.append(dict(code=c,kind="ASCII",char=cp932_char(c),table=None,flags=0,raw_index=raw,final_index=fin,source=source_for_index(fin) if fin<15 else None,eligible_halfwidth=False))
    for c in range(0xA0,0xDE):
        ent=table_entry(slps,c); raw=ent&0x1FF; flags=ent&~0x1FF; fin=remap_dim11(raw)
        rec.append(dict(code=c,kind="HALF",char=cp932_char(c),table=ent,flags=flags,raw_index=raw,final_index=fin,source=source_for_index(fin) if fin<15 else None,eligible_halfwidth=(0xA1<=c<=0xDD and cp932_char(c) is not None and not(ent&0x2000) and fin<15)))
    return rec
def fmt_char(ch): return "<invalid>" if ch is None else repr(ch)

def main():
    here=os.path.dirname(os.path.abspath(__file__)); src=os.path.abspath(sys.argv[1]) if len(sys.argv)>=2 else os.path.join(here,"GaiaMaster - Kamigami no Board Game (Japan).bin")
    if not os.path.isfile(src): print("[ERROR] CLEAN Gaia Master BIN not found."); return 2
    bsha=sha1_file(src).lower()
    if bsha!=EXPECTED_BIN_SHA1: print("[ERROR] CLEAN BIN required. Got",bsha); return 3
    with open(src,"rb") as f: slps=read_iso_file(f,SLPS_EXTENT,SLPS_SIZE); prg=read_iso_file(f,PRG_EXTENT,PRG_SIZE)
    if sha1_bytes(slps)!=EXPECTED_SLPS_SHA1: raise RuntimeError("SLPS SHA1 mismatch")
    if sha1_bytes(prg)!=EXPECTED_PRG_SHA1: raise RuntimeError("PRGPACK SHA1 mismatch")
    aliases=resolve_aliases(slps); codes=sorted(set(r["code"] for r in aliases)); ph,pe=strict_nul_text_hits(prg,codes); sh,se=strict_nul_text_hits(slps,codes)
    by={i:[] for i in range(15)}
    for r in aliases:
        if r["source"] is not None and 0<=r["final_index"]<15:
            r["prg_hits"]=ph.get(r["code"],0); r["slps_hits"]=sh.get(r["code"],0); r["text_hits"]=r["prg_hits"]+r["slps_hits"]; by[r["final_index"]].append(r)
    summ=[]
    for i in range(15):
        ars=by[i]; total=sum(r.get("text_hits",0) for r in ars); hc=[r for r in ars if r["eligible_halfwidth"] and r.get("text_hits",0)==0]; hc.sort(key=lambda r:(r["flags"]!=0,r["flags"],r["code"])); eff=effective_glyph_bytes(slps,i)
        summ.append(dict(idx=i,aliases=ars,total_hits=total,half_candidates=hc,source=source_for_index(i),span=full_source_span(i),sha1=sha1_bytes(eff)[:12],effective=eff))
    clean=[s for s in summ if s["total_hits"]==0 and s["half_candidates"]]; selected=[(s,s["half_candidates"][0]) for s in clean]; selected.sort(key=lambda x:(x[1]["flags"]!=0,x[1]["code"],x[0]["idx"]))
    bank_bytes=ATLAS_OFF-NARROW_BASE_OFF; expected=((15+1)//2)*72; ov=max(0,min(OLD_ZERO_RUN_END,ATLAS_OFF)-max(OLD_ZERO_RUN_START,NARROW_BASE_OFF))
    L=[]; ap=L.append
    ap("GAIA MASTER FONT NARROW BANK SCANNER 0.1"); ap("="*100); ap("READ ONLY - KHONG SUA ROM - KHONG BOOT GAME"); ap("")
    ap("Input BIN : %s"%os.path.basename(src)); ap("BIN SHA1  : %s"%bsha); ap("SLPS SHA1 : %s"%sha1_bytes(slps)); ap("PRG SHA1  : %s"%sha1_bytes(prg)); ap("Load base : 0x%08X"%LOAD_BASE); ap("")
    ap("PROVEN / RECONSTRUCTED NATIVE NARROW PATH"); ap("-"*100); ap("Character Select dimension class : 11 (12-pixel native cell)"); ap("Native narrow advance            : 8 px"); ap("Halfwidth remap table             : RAM 0x%08X SLPS+0x%06X"%(HALF_TABLE_RAM,HALF_TABLE_OFF)); ap("Native narrow source              : RAM 0x%08X SLPS+0x%06X"%(NARROW_BASE_RAM,NARROW_BASE_OFF)); ap("Main atlas                        : RAM 0x%08X SLPS+0x%06X"%(ATLAS_RAM,ATLAS_OFF)); ap("Narrow physical bytes             : %d expected=%d [%s]"%(bank_bytes,expected,"MATCH" if bank_bytes==expected else "MISMATCH")); ap("Old zero-run overlap              : %d byte(s) %s"%(ov,"[REJECT AS CODE CAVE]" if ov else "")); ap("")
    ap("="*100); ap("NATIVE NARROW SOURCE INDEX MAP 0..14"); ap("="*100)
    for s in summ:
        ram,off=s["source"]; a=[]
        for r in s["aliases"]:
            ent="" if r["table"] is None else " tbl=%04X"%r["table"]
            a.append("%02X/%s%s hits=%d"%(r["code"],fmt_char(r["char"]),ent,r.get("text_hits",0)))
        hc=", ".join("%02X%s"%(r["code"],fmt_char(r["char"])) for r in s["half_candidates"]) or "-"; ap(""); ap("index %02d source=0x%08X SLPS+0x%06X cache_key=0x%08X"%(s["idx"],ram,off,ram>>1)); ap("  all alias strict-text hits : %d"%s["total_hits"]); ap("  eligible halfwidth aliases : %s"%hc); ap("  aliases: %s"%(" | ".join(a) if a else "-")); eff=s["effective"]; ap("  rows: "+" ".join("%02d:%s"%(i,eff[i*3:(i+1)*3].hex().upper()) for i in range(12)))
    ap(""); ap("="*100); ap("HALFWIDTH TABLE A0..DD"); ap("="*100)
    for r in aliases:
        if r["kind"]!="HALF": continue
        st="-" if r["source"] is None else "idx=%d src=0x%08X"%(r["final_index"],r["source"][0]); ap("%02X %-10s table=%04X low9=%3d flags=%04X final=%3d %-27s PRG=%d SLPS=%d candidate=%s"%(r["code"],fmt_char(r["char"]),r["table"],r["raw_index"],r["flags"],r["final_index"],st,r.get("prg_hits",0),r.get("slps_hits",0),"YES" if r["eligible_halfwidth"] and r.get("text_hits",0)==0 else "NO"))
    ap(""); ap("="*100); ap("DATA-ONLY VIETNAMESE PROOF CANDIDATES"); ap("="*100); ap("Need 9 distinct sources for: %s"%" ".join(PROOF_UNITS)); ap("Clean distinct narrow sources found: %d"%len(clean))
    if len(selected)>=9:
        for u,(s,r) in zip(PROOF_UNITS,selected[:9]): ap("  %-5s -> byte=%02X %-8s source_index=%02d source=0x%08X flags=%04X"%(u,r["code"],fmt_char(r["char"]),s["idx"],s["source"][0],r["flags"]))
        ap(""); ap("[STATIC PASS] >=9 distinct native narrow sources have zero strict-text alias hits"); ap("Potential path: byte -> native halfwidth table -> narrow source -> native copy return 8 -> native advance 8px"); ap("NO CODE CAVE / NO CURSOR HOOK / NO record+6 HOOK / NO POINTER REDIRECT")
    else:
        ap("[STATIC NEGATIVE] Fewer than 9 clean distinct narrow sources were found."); ap("Do NOT force this path; continue offline cache-advance isolation.")
    ap(""); ap("NEXT GATE: if PASS, cross-check selected aliases against Translation Master before ONE data-only runtime proof.")
    report=os.path.join(os.path.dirname(src),"GaiaMaster_FontNarrowBankScanner_01.txt")
    with open(report,"w",encoding="utf-8") as f:f.write("\n".join(L)+"\n")
    print("[OK] READ-ONLY native narrow-bank scan complete."); print("Report:",report); print("Old zero-run overlap:",ov,"byte(s)"); print("Clean distinct narrow sources:",len(clean)); print("STATIC GATE:","PASS" if len(selected)>=9 else "NEGATIVE"); return 0
if __name__=="__main__":
    try: sys.exit(main())
    except Exception as e: print("[ERROR]",repr(e)); sys.exit(9)

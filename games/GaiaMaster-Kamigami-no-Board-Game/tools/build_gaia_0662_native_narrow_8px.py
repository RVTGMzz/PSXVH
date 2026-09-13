#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function
import os,sys,shutil,struct,unicodedata
import build_gaia_0653_mapping_only as m
import build_gaia_0654_native_base as n
import build_gaia_0655_accent_safe as a

TEST_TEXT="Chọn tướng"; FIELD_BYTES=24
LOAD_BASE=0x8000F800
NARROW_RAM=0x8006BAAC; NARROW_OFF=NARROW_RAM-LOAD_BASE
NARROW_STRIDE=6; TABLE1_OFF=0x8007E01C-LOAD_BASE; TABLE1_BYTES=192
UNITS=["C","h","ọ","n","t","ư","ớ","g"]
# index, direct one-byte code, original visible owner
CANDIDATES=[(2,0x23,"#"),(3,0x24,"$"),(5,0x26,"&"),(6,0x27,"'"),(7,0x28,"("),(8,0x29,")"),(9,0x2A,"*"),(10,0x2B,"+"),(1,0x22,'"'),(12,0x5A,"Z"),(13,0x58,"X")]


def fullwidth_code(ch):
    fw=chr(ord(ch)+0xFEE0)
    b=fw.encode("cp932")
    if len(b)!=2: raise RuntimeError("no native fullwidth code for %r"%ch)
    return (b[0]<<8)|b[1]


def native_base(slps,ch):
    code=fullwidth_code(ch); slot=m.mapping_value(slps,code)
    if slot is None or not 0<=slot<m.ATLAS_GLYPHS: raise RuntimeError("bad native base %r"%ch)
    off=m.ATLAS_OFF+slot*m.GLYPH_BYTES; raw=bytes(slps[off:off+m.GLYPH_BYTES])
    return code,slot,n.decode_glyph(raw)


def fit_vertical(g,marks):
    bb=n.bbox(g)
    if bb is None: raise RuntimeError("empty native base")
    x0,sy0,x1,sy1=bb
    top=2 if any(x in marks for x in ("\u0306","\u0302","\u031B","\u0301","\u0300","\u0309","\u0303")) else 0
    bottom=10 if "\u0323" in marks else 11
    if sy0>=top and sy1<=bottom: return [r[:] for r in g],bb,"native-preserved"
    src_h=sy1-sy0+1; y1=min(sy1,bottom); y0=max(top,y1-src_h+1)
    if y0>y1: y0,y1=top,bottom
    h=y1-y0+1; out=[[0]*12 for _ in range(12)]
    for dy in range(h):
        sy=sy0 if h==1 else sy0+int(round(dy*(src_h-1)/float(h-1)))
        out[y0+dy]=g[sy][:]
    return out,bb,"minimal-fit"


def glyph12(slps,ch,cache):
    if ord(ch)<128: base=ch; marks=[]
    else:
        d=unicodedata.normalize("NFD",ch); base=d[0]; marks=list(d[1:])
    if base not in cache: cache[base]=native_base(slps,base)
    code,slot,bg=cache[base]; fill,shadow,hist=a.choose_layers(bg)
    g,src_bb,fit=fit_vertical(bg,marks) if marks else ([r[:] for r in bg],n.bbox(bg),"native-plain")
    bb=n.bbox(g); x0,y0,x1,y1=bb; cx=(x0+x1)//2; top1=max(0,y0-1); top2=max(0,y0-2)
    if "\u031B" in marks:
        hx=min(10,x1+1); a.draw_dual(g,[(hx,y0),(min(10,hx+1),max(0,y0-1))],fill,shadow)
    if "\u0301" in marks: a.draw_dual(g,[(cx+1,top2),(cx,top1)],fill,shadow)
    if "\u0300" in marks: a.draw_dual(g,[(cx-1,top2),(cx,top1)],fill,shadow)
    if "\u0309" in marks: a.draw_dual(g,[(cx,top2),(cx+1,top2),(cx+1,top1),(cx,top1)],fill,shadow)
    if "\u0303" in marks: a.draw_dual(g,[(cx-2,top1),(cx-1,top2),(cx,top1),(cx+1,top1),(cx+2,top2)],fill,shadow)
    if "\u0302" in marks: a.draw_dual(g,[(cx-1,top1),(cx,top2),(cx+1,top1)],fill,shadow)
    if "\u0306" in marks: a.draw_dual(g,[(cx-2,top1),(cx-1,top2),(cx,top2),(cx+1,top2),(cx+2,top1)],fill,shadow)
    if "\u0323" in marks:
        bb=n.bbox(g); a.draw_dual(g,[((bb[0]+bb[2])//2,min(11,bb[3]+1))],fill,shadow)
    return g,{"base":base,"code":code,"slot":slot,"fill":fill,"shadow":shadow,"fit":fit,"bbox12":n.bbox(g),"marks":["U+%04X"%ord(x) for x in marks]}


def compress6(g,fill,shadow):
    out=[[0]*6 for _ in range(12)]
    for y in range(12):
        for x in range(6):
            p,q=g[y][2*x],g[y][2*x+1]
            if not p: v=q
            elif not q: v=p
            elif p==fill or q==fill: v=fill
            elif p!=shadow: v=p
            elif q!=shadow: v=q
            else: v=shadow
            out[y][x]=v
    return out


def bbox6(g):
    pts=[(x,y) for y in range(12) for x in range(6) if g[y][x]]
    if not pts:return None
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    return min(xs),min(ys),max(xs),max(ys)


def pack6(g):
    out=bytearray()
    for row in g:
        for x in range(0,6,2): out.append((row[x]&15)|((row[x+1]&15)<<4))
    if len(out)!=36: raise AssertionError(len(out))
    return bytes(out)


def narrow_off(idx):
    if not 0<=idx<15: raise ValueError(idx)
    return NARROW_OFF+3*((idx&~1)*12)+3*(idx&1)


def narrow_read(slps,idx):
    p=narrow_off(idx); out=bytearray()
    for y in range(12): out.extend(slps[p+y*NARROW_STRIDE:p+y*NARROW_STRIDE+3])
    return bytes(out)


def narrow_write(slps,idx,raw):
    if len(raw)!=36: raise ValueError(len(raw))
    p=narrow_off(idx); k=0
    for y in range(12):
        slps[p+y*NARROW_STRIDE:p+y*NARROW_STRIDE+3]=raw[k:k+3]; k+=3


def lead(b): return 0x81<=b<=0x9F or 0xE0<=b<=0xFC

def trail(b): return ((0x40<=b<=0x7E) or (0x80<=b<=0xFC)) and b!=0x7F


def textlike(s):
    if len(s)<2 or not all(c.isprintable() for c in s): return False
    jp=sum(0x3040<=ord(c)<=0x30FF or 0x3400<=ord(c)<=0x9FFF or 0xFF00<=ord(c)<=0xFFEF for c in s)
    aa=sum(c.isascii() and c.isalpha() for c in s)
    return jp>0 or aa>=2 or "%s" in s or "%d" in s


def segments(blob,base=0):
    s=0
    while s<len(blob):
        e=blob.find(b"\0",s)
        if e<0: break
        raw=blob[s:e]
        if 2<=len(raw)<=256:
            try: txt=raw.decode("cp932")
            except Exception: txt=None
            if txt is not None and textlike(txt): yield base+s,raw,txt
        s=e+1


def tokens(raw):
    i=0
    while i<len(raw):
        b=raw[i]
        if lead(b) and i+1<len(raw) and trail(raw[i+1]): i+=2
        else: yield i,b; i+=1


def slps_ranges():
    # Exclude narrow bank, main atlas, mapping + one-byte remap table.
    ex=[(NARROW_OFF,m.ATLAS_OFF),(m.ATLAS_OFF,m.ATLAS_OFF+m.ATLAS_GLYPHS*m.GLYPH_BYTES),(m.MAPPING_OFF,TABLE1_OFF+TABLE1_BYTES)]
    out=[]; cur=0
    for a0,b0 in sorted(ex):
        if cur<a0: out.append((cur,a0))
        cur=max(cur,b0)
    if cur<m.SLPS_SIZE: out.append((cur,m.SLPS_SIZE))
    return out


def choose_aliases(slps,prg,report):
    watch={c for _,c,_ in CANDIDATES}; use={c:[] for c in watch}; count=0
    def consume(src,off,raw,txt):
        nonlocal count; count+=1
        for pos,b in tokens(raw):
            if b in use and len(use[b])<20: use[b].append((src,off+pos,txt[:100]))
    for off,raw,txt in segments(bytes(prg)): consume("PRGPACK",off,raw,txt)
    for a0,b0 in slps_ranges():
        for off,raw,txt in segments(bytes(slps[a0:b0]),a0): consume("SLPS",off,raw,txt)
    report += ["TEXT SAFETY GATE","-"*78,"plausible CP932 strings scanned: %d"%count]
    safe=[]
    for idx,code,label in CANDIDATES:
        hits=use[code]; report.append("idx=%02d byte=%02X owner=%r text_hits=%d"%(idx,code,label,len(hits)))
        for src,off,txt in hits[:4]: report.append("  %s+0x%X %r"%(src,off,txt))
        if not hits:safe.append((idx,code,label))
    report.append("safe owners=%d / need=%d"%(len(safe),len(UNITS)))
    return safe[:len(UNITS)] if len(safe)>=len(UNITS) else None


def main():
    here=os.path.dirname(os.path.abspath(__file__)); src=os.path.abspath(sys.argv[1]) if len(sys.argv)>1 else os.path.join(here,"GaiaMaster - Kamigami no Board Game (Japan).bin")
    gate=os.path.join(here,"GaiaMaster_0.6.6.2_NATIVE_NARROW_GATE_REPORT.txt")
    report=["GAIA MASTER 0.6.6.2 NATIVE NARROW 8PX PROOF","="*78,"DATA ONLY / 6x12 / NO HOOK / NO CAVE / NO CURSOR PATCH","expected: "+TEST_TEXT,""]
    def save(path=gate):
        with open(path,"w",encoding="utf-8") as f:f.write("\n".join(report)+"\n")
    if not os.path.isfile(src): report.append("[BLOCKED] CLEAN BIN not found"); save(); print("[ERROR] BIN not found"); return 2
    if m.sha1_file(src).lower()!=m.EXPECTED_BIN_SHA1: report.append("[BLOCKED] wrong BIN SHA1"); save(); print("[ERROR] CLEAN BIN required"); return 3
    with open(src,"rb") as rf: slps=m.read_iso_file(rf,m.SLPS_EXTENT,m.SLPS_SIZE); prg=m.read_iso_file(rf,m.PRG_EXTENT,m.PRG_SIZE)
    if m.sha1_bytes(slps)!=m.EXPECTED_SLPS_SHA1 or m.sha1_bytes(prg)!=m.EXPECTED_PRG_SHA1: raise RuntimeError("embedded SHA1 mismatch")
    entries=m.parse_bdp_entries(prg); owner=[e for e in entries if e[1]<=m.PRG_TEST_OFF<e[2]]
    if len(owner)!=1 or owner[0][0]!=m.EXPECTED_OWNER_ENTRY: raise RuntimeError("Character Select owner mismatch")
    for c,e in [(0x8273,481),(0x8264,466),(0x8272,480),(0x889F,0)]:
        if m.mapping_value(slps,c)!=e: raise RuntimeError("mapping fact mismatch %04X"%c)
    report += ["BIN SHA1: "+m.sha1_file(src),"narrow bank: RAM 0x8006BAAC / SLPS+0x5C2AC","space: native byte 0x20 / 8px advance",""]
    selected=choose_aliases(slps,prg,report)
    if selected is None:
        report += ["","[BLOCKED] fewer than 8 text-unused direct narrow owners","No BIN/CUE created. Send this gate report."]; save(); print("[BLOCKED] safety gate"); print("Report:",gate); return 4
    alias={u:{"idx":x[0],"code":x[1],"owner":x[2]} for u,x in zip(UNITS,selected)}
    report += ["","SELECTED ALIASES","-"*78]+["%-2s -> %02X %r -> idx %02d"%(u,alias[u]["code"],alias[u]["owner"],alias[u]["idx"]) for u in UNITS]
    sn=bytearray(slps); pn=bytearray(prg); cache={}; report += ["","GLYPHS","-"*78]
    for u in UNITS:
        g12,meta=glyph12(slps,u,cache); g6=compress6(g12,meta["fill"],meta["shadow"]); raw=pack6(g6); old=narrow_read(slps,alias[u]["idx"]); narrow_write(sn,alias[u]["idx"],raw)
        report.append("%-2s idx=%02d off=0x%06X base=%s native=%04X/%d fit=%s bbox12=%r bbox6=%r old=%s new=%s marks=%s"%(u,alias[u]["idx"],narrow_off(alias[u]["idx"]),meta["base"],meta["code"],meta["slot"],meta["fit"],meta["bbox12"],bbox6(g6),m.sha1_bytes(old)[:12],m.sha1_bytes(raw)[:12],",".join(meta["marks"])))
    enc=bytes(0x20 if ch==" " else alias[ch]["code"] for ch in TEST_TEXT)
    if len(enc)+1>FIELD_BYTES: raise RuntimeError("proof text too long")
    old=bytes(pn[m.PRG_TEST_OFF:m.PRG_TEST_OFF+FIELD_BYTES]); field=enc+b"\0"+b"\0"*(FIELD_BYTES-len(enc)-1); pn[m.PRG_TEST_OFF:m.PRG_TEST_OFF+FIELD_BYTES]=field
    report += ["","FIELD","-"*78,"old24="+old.hex().upper(),"new24="+field.hex().upper(),"bytes="+" ".join("%02X"%b for b in enc)]
    _,start,end=owner[0]; struct.pack_into("<I",pn,start+4,m.bdp_checksum(bytearray(pn[start:end]))); struct.pack_into("<I",pn,4,m.bdp_checksum(pn))
    if m.bdp_checksum(pn)!=struct.unpack_from("<I",pn,4)[0] or m.bdp_checksum(bytes(pn[start:end]))!=struct.unpack_from("<I",pn,start+4)[0]: raise RuntimeError("BDP checksum rebuild failed")
    stem=os.path.splitext(src)[0]; ob=stem+" [VI 0.6.6.2 NATIVE NARROW 8PX].bin"; oc=stem+" [VI 0.6.6.2 NATIVE NARROW 8PX].cue"; ot=stem+" [VI 0.6.6.2 NATIVE NARROW 8PX].txt"
    shutil.copyfile(src,ob); changed=set()
    with open(ob,"r+b") as wf:
        m.write_changed_iso_file(wf,m.SLPS_EXTENT,slps,bytes(sn),changed); m.write_changed_iso_file(wf,m.PRG_EXTENT,prg,bytes(pn),changed)
        for sec in sorted(changed): wf.seek(sec*2352); raw=wf.read(2352); wf.seek(sec*2352); wf.write(m.regen_sector(raw))
    with open(oc,"w",encoding="ascii") as f:f.write('FILE "'+os.path.basename(ob)+'" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
    report += ["","RESULT: BUILD SUCCESS","changed sectors=%d"%len(changed),"output SHA1="+m.sha1_file(ob),"runtime: Character Select only; expect compact 8px Chọn tướng; stop on freeze/corruption"]
    save(ot); save(); print("[OK] 0.6.6.2 NATIVE NARROW 8PX BUILD SUCCESS"); print("Output:",oc); print("Report:",ot); return 0

if __name__=="__main__":
    try:sys.exit(main())
    except Exception as e:print("[ERROR]",repr(e));sys.exit(9)

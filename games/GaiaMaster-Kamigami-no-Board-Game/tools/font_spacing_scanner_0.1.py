#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function
import hashlib, os, struct, sys

CLEAN_BIN_SHA1="f4d5298583c90d89c4b7e51d2dde160ee07f2aec"
ALPHA061_BIN_SHA1="54d2fb026bc3b71c79861e723caffb4114caa34c"
CLEAN_SLPS_SHA1="1dfeb6b7cfda59c108dde2dc0b8abda9a40e6ae5"
SLPS_EXTENT=24
SLPS_SIZE=487424
REG=["zero","at","v0","v1","a0","a1","a2","a3","t0","t1","t2","t3","t4","t5","t6","t7",
     "s0","s1","s2","s3","s4","s5","s6","s7","t8","t9","k0","k1","gp","sp","fp","ra"]
FIELDS={0x18:"cursor_x",0x3C:"extra_tracking",0x3E:"special_or_small_advance",0x40:"native_dimension",
        0x44:"glyph_count",0x54:"cache_record_base",0x58:"cache_page_A",0x5C:"cache_page_B",
        0x60:"cache_current_ptr",0x64:"cache_write_ptr",0x68:"primitive_attr0",0x69:"primitive_attr1",
        0x6A:"primitive_attr2",0x6B:"primitive_attr3",0x6C:"cache_ring_index"}

def sha1_file(p):
    h=hashlib.sha1()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(8*1024*1024),b""): h.update(b)
    return h.hexdigest()

def sha1_bytes(b):
    h=hashlib.sha1(); h.update(b); return h.hexdigest()

def read_iso_file(f,extent,size):
    out=bytearray(); remain=size; sec=extent
    while remain:
        n=min(2048,remain); f.seek(sec*2352+24); b=f.read(n)
        if len(b)!=n: raise RuntimeError("Short read sector %d"%sec)
        out.extend(b); remain-=n; sec+=1
    return bytes(out)

def s16(x): return x-0x10000 if x&0x8000 else x
def u32(x): return x&0xffffffff
def ff(w):
    return ((w>>26)&0x3f,(w>>21)&31,(w>>16)&31,(w>>11)&31,(w>>6)&31,w&0x3f,w&0xffff,w&0x03ffffff)

def dec(w,pc):
    op,rs,rt,rd,sh,fn,imm,tgt=ff(w); si=s16(imm)
    if w==0:return "nop"
    if op==0:
        d={0x21:"addu",0x23:"subu",0x25:"or",0x24:"and"}
        if fn in d:return "%s %s,%s,%s"%(d[fn],REG[rd],REG[rs],REG[rt])
        if fn in (0,2,3):return "%s %s,%s,%d"%({0:"sll",2:"srl",3:"sra"}[fn],REG[rd],REG[rt],sh)
        if fn==8:return "jr %s"%REG[rs]
        if fn==0x18:return "mult %s,%s"%(REG[rs],REG[rt])
        if fn==0x12:return "mflo %s"%REG[rd]
        return "SPECIAL fn=%02X"%fn
    if op==0x0f:return "lui %s,0x%04X"%(REG[rt],imm)
    if op==0x09:return "addiu %s,%s,%d"%(REG[rt],REG[rs],si)
    if op==0x0d:return "ori %s,%s,0x%04X"%(REG[rt],REG[rs],imm)
    if op==0x0c:return "andi %s,%s,0x%04X"%(REG[rt],REG[rs],imm)
    mem={0x23:"lw",0x21:"lh",0x25:"lhu",0x20:"lb",0x24:"lbu",0x2b:"sw",0x29:"sh",0x28:"sb"}
    if op in mem:return "%s %s,%d(%s)"%(mem[op],REG[rt],si,REG[rs])
    if op in (4,5):
        dst=u32(pc+4+(si<<2))
        return "%s %s,%s,0x%08X"%("beq" if op==4 else "bne",REG[rs],REG[rt],dst)
    if op==2:return "j 0x%08X"%(((pc+4)&0xf0000000)|(tgt<<2))
    if op==3:return "jal 0x%08X"%(((pc+4)&0xf0000000)|(tgt<<2))
    return "op=%02X"%op

def typ(op):
    if op in (0x23,0x21,0x25,0x20,0x24):return "READ"
    if op in (0x2b,0x29,0x28):return "WRITE"
    return None

def context(lines,words,base,idx,b=8,a=10,label="<<<"):
    for j in range(max(0,idx-b),min(len(words),idx+a+1)):
        pc=base+0x800+j*4; off=0x800+j*4
        lines.append("0x%08X [0x%06X] %08X  %-42s%s"%(pc,off,words[j],dec(words[j],pc),
                     ("  "+label) if j==idx else ""))

def main():
    here=os.path.dirname(os.path.abspath(__file__))
    src=os.path.abspath(sys.argv[1]) if len(sys.argv)>1 else os.path.join(here,"GaiaMaster - Kamigami no Board Game (Japan).bin")
    if not os.path.isfile(src):
        print("[ERROR] BIN not found."); return 2
    bs=sha1_file(src).lower()
    if bs==CLEAN_BIN_SHA1: base_name="CLEAN"
    elif bs==ALPHA061_BIN_SHA1: base_name="ALPHA 0.6.1 FRONT"
    else:
        print("[ERROR] Unexpected BIN SHA1:",bs); return 3
    with open(src,"rb") as f: slps=read_iso_file(f,SLPS_EXTENT,SLPS_SIZE)
    ss=sha1_bytes(slps)
    if base_name=="CLEAN" and ss!=CLEAN_SLPS_SHA1:
        print("[ERROR] CLEAN SLPS SHA1 mismatch:",ss); return 4
    pc0,gp0,taddr,tsize=struct.unpack_from("<IIII",slps,0x10)
    load=u32(taddr-0x800)
    code=slps[0x800:min(len(slps),0x800+tsize)]
    code=code[:len(code)&~3]
    words=list(struct.unpack("<%dI"%(len(code)//4),code))
    refs={k:[] for k in FIELDS}
    for i,w in enumerate(words):
        op,rs,rt,rd,sh,fn,imm,tgt=ff(w); k=s16(imm); t=typ(op)
        if t and k in refs:
            refs[k].append((i,load+0x800+i*4,t,rs,rt))
    L=[]; ap=L.append
    ap("GAIA MASTER FONT SPACING SCANNER 0.1"); ap("="*90)
    ap("READ ONLY - KHONG SUA ROM - KHONG CAN BOOT GAME"); ap("")
    ap("Input: %s"%os.path.basename(src)); ap("Base: %s"%base_name); ap("BIN SHA1: %s"%bs); ap("SLPS SHA1: %s"%ss); ap("Load base: 0x%08X"%load); ap("")
    ap("PROVEN ADVANCE FORMULA"); ap("-"*90)
    ap("cache hit : advance = cache_record.byte6")
    ap("cache miss: copy_return == 8 ? state+0x3E : state+0x40 + 1")
    ap("tracking  : if advance != state+0x3E, add state+0x3C"); ap("")
    ap("STATE FIELD SUMMARY"); ap("-"*90)
    for k,name in FIELDS.items():
        r=refs[k]; rd=sum(x[2]=="READ" for x in r); wr=len(r)-rd
        ap("state+0x%02X %-28s refs=%d read=%d write=%d"%(k,name,len(r),rd,wr))
    ap("")
    for k in (0x3C,0x3E,0x40):
        ap("="*90); ap("OWNERSHIP: state+0x%02X %s"%(k,FIELDS[k])); ap("="*90)
        wr=[x for x in refs[k] if x[2]=="WRITE"]; rd=[x for x in refs[k] if x[2]=="READ"]
        if not wr: ap("[WARN] no direct write; possible aliased/block copy")
        for n,(idx,pc,t,rs,rt) in enumerate(wr,1):
            ap("[WRITE %02d] 0x%08X base=%s src=%s"%(n,pc,REG[rs],REG[rt]))
            context(L,words,load,idx,12,14,"<<< WRITE")
            ap("")
        ap("READS:")
        for n,(idx,pc,t,rs,rt) in enumerate(rd,1):
            ap("  [%02d] 0x%08X base=%s dst=%s  %s"%(n,pc,REG[rs],REG[rt],dec(words[idx],pc)))
        ap("")
    for k in (0x54,0x58,0x5C,0x60,0x64,0x6C):
        ap("="*90); ap("CACHE WRITES: state+0x%02X %s"%(k,FIELDS[k])); ap("="*90)
        wr=[x for x in refs[k] if x[2]=="WRITE"]
        for n,(idx,pc,t,rs,rt) in enumerate(wr,1):
            ap("[WRITE %02d] 0x%08X base=%s src=%s"%(n,pc,REG[rs],REG[rt]))
            context(L,words,load,idx,6,8,"<<<"); ap("")
        if not wr: ap("[INFO] no direct write")
    for title,v0,v1 in [
        ("CACHE HIT / ADVANCE",0x8003CB10,0x8003CC30),
        ("CACHE MISS / WIDTH",0x8003CC30,0x8003CDA0),
        ("RENDERER INIT NEIGHBORHOOD",0x8003D380,0x8003D780)]:
        ap("="*90); ap(title); ap("="*90)
        i0=max(0,((v0-load)-0x800)//4); i1=min(len(words)-1,((v1-load)-0x800)//4)
        for i in range(i0,i1+1):
            pc=load+0x800+i*4; ap("0x%08X [0x%06X] %08X  %s"%(pc,0x800+i*4,words[i],dec(words[i],pc)))
        ap("")
    ap("="*90); ap("DIRECT JAL CALLERS INTO 0x8003D380..0x8003D780"); ap("="*90)
    hits=0
    for i,w in enumerate(words):
        op,rs,rt,rd,sh,fn,imm,tgt=ff(w)
        if op!=3: continue
        pc=load+0x800+i*4; dst=((pc+4)&0xf0000000)|(tgt<<2)
        if 0x8003D380<=dst<=0x8003D780:
            hits+=1; ap("[CALL %02d] 0x%08X -> 0x%08X"%(hits,pc,dst)); context(L,words,load,i,10,8,"<<< CALL"); ap("")
    if not hits: ap("[INFO] no direct callers found")
    ap("="*90); ap("NEXT GATE"); ap("="*90)
    ap("Prove ownership/value source of state+0x3C/+0x3E/+0x40 before any runtime spacing patch.")
    report=os.path.join(os.path.dirname(src),"GaiaMaster_FontSpacingScanner_01.txt")
    with open(report,"w",encoding="utf-8") as f: f.write("\n".join(L)+"\n")
    print("[OK] READ-ONLY spacing scan complete")
    print("Report:",report)
    return 0

if __name__=="__main__":
    try: sys.exit(main())
    except Exception as e:
        print("[ERROR]",repr(e)); sys.exit(9)

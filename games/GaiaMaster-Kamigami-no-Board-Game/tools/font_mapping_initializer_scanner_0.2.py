#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gaia Master Font Mapping Initializer Scanner 0.2
READ ONLY. Does not modify the BIN.

Purpose:
- recover the runtime GP initialization that scanner 0.1 could not read from GP0;
- find every direct write to gp+0x518 and gp+0x51C across the full SLPS executable;
- find code/data references to the known atlas/mapping addresses;
- dump enough surrounding MIPS code to reverse the initializer offline.
"""
from __future__ import print_function

import hashlib
import os
import struct
import sys

CLEAN_BIN_SHA1 = "f4d5298583c90d89c4b7e51d2dde160ee07f2aec"
ALPHA061_BIN_SHA1 = "54d2fb026bc3b71c79861e723caffb4114caa34c"
CLEAN_SLPS_SHA1 = "1dfeb6b7cfda59c108dde2dc0b8abda9a40e6ae5"

SLPS_EXTENT = 24
SLPS_SIZE = 487424

ATLAS_ADDR = 0x8006BCEC
MAPPING_ADDR = 0x8007AECC
ATLAS_GP_OFF = 0x0518
MAPPING_GP_OFF = 0x051C

REG = [
    "zero","at","v0","v1","a0","a1","a2","a3",
    "t0","t1","t2","t3","t4","t5","t6","t7",
    "s0","s1","s2","s3","s4","s5","s6","s7",
    "t8","t9","k0","k1","gp","sp","fp","ra"
]

def sha1_bytes(data):
    h = hashlib.sha1(); h.update(data); return h.hexdigest()

def sha1_file(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        while True:
            b = f.read(8 * 1024 * 1024)
            if not b: break
            h.update(b)
    return h.hexdigest()

def read_iso_file(rawf, extent, size):
    out = bytearray(); remain = size; sec = extent
    while remain:
        n = min(2048, remain)
        rawf.seek(sec * 2352 + 24)
        b = rawf.read(n)
        if len(b) != n: raise RuntimeError("Short read at raw sector %d" % sec)
        out.extend(b); remain -= n; sec += 1
    return bytes(out)

def s16(x): return x - 0x10000 if x & 0x8000 else x

def u32(x): return x & 0xFFFFFFFF

def fields(w):
    return {"op":(w>>26)&0x3F,"rs":(w>>21)&0x1F,"rt":(w>>16)&0x1F,"rd":(w>>11)&0x1F,
            "sh":(w>>6)&0x1F,"fn":w&0x3F,"imm":w&0xFFFF,"target":w&0x03FFFFFF}

def decode(w, pc):
    f=fields(w); op,rs,rt,rd,imm=f["op"],f["rs"],f["rt"],f["rd"],f["imm"]; si=s16(imm)
    if w==0: return "nop"
    if op==0:
        fn=f["fn"]
        if fn==0x21:return "addu %s,%s,%s"%(REG[rd],REG[rs],REG[rt])
        if fn==0x25:return "or %s,%s,%s"%(REG[rd],REG[rs],REG[rt])
        if fn==0x23:return "subu %s,%s,%s"%(REG[rd],REG[rs],REG[rt])
        if fn==0x00:return "sll %s,%s,%d"%(REG[rd],REG[rt],f["sh"])
        if fn==0x02:return "srl %s,%s,%d"%(REG[rd],REG[rt],f["sh"])
        if fn==0x08:return "jr %s"%REG[rs]
        return "SPECIAL fn=0x%02X"%fn
    if op==0x0F:return "lui %s,0x%04X"%(REG[rt],imm)
    if op==0x09:return "addiu %s,%s,%d"%(REG[rt],REG[rs],si)
    if op==0x0D:return "ori %s,%s,0x%04X"%(REG[rt],REG[rs],imm)
    if op==0x0C:return "andi %s,%s,0x%04X"%(REG[rt],REG[rs],imm)
    if op==0x23:return "lw %s,%d(%s)"%(REG[rt],si,REG[rs])
    if op==0x2B:return "sw %s,%d(%s)"%(REG[rt],si,REG[rs])
    if op==0x29:return "sh %s,%d(%s)"%(REG[rt],si,REG[rs])
    if op==0x25:return "lhu %s,%d(%s)"%(REG[rt],si,REG[rs])
    if op==0x24:return "lbu %s,%d(%s)"%(REG[rt],si,REG[rs])
    if op==0x04:return "beq %s,%s,0x%08X"%(REG[rs],REG[rt],u32(pc+4+(si<<2)))
    if op==0x05:return "bne %s,%s,0x%08X"%(REG[rs],REG[rt],u32(pc+4+(si<<2)))
    if op==0x02:return "j 0x%08X"%(((pc+4)&0xF0000000)|(f["target"]<<2))
    if op==0x03:return "jal 0x%08X"%(((pc+4)&0xF0000000)|(f["target"]<<2))
    return "op=0x%02X"%op

def write_reg(w):
    f=fields(w); op=f["op"]
    if op==0:
        if f["fn"] in (0x00,0x02,0x03,0x21,0x23,0x25,0x2A,0x2B): return f["rd"]
        return None
    if op in (0x08,0x09,0x0A,0x0B,0x0C,0x0D,0x0E,0x0F,0x20,0x21,0x23,0x24,0x25): return f["rt"]
    return None

def forward_constants(words,start,end):
    states={}; c={0:0}
    for i in range(start,end):
        states[i]=dict(c); w=words[i]; f=fields(w); op,rs,rt,rd,imm=f["op"],f["rs"],f["rt"],f["rd"],f["imm"]
        if op==0x0F:c[rt]=u32(imm<<16)
        elif op==0x09:
            if rs in c:c[rt]=u32(c[rs]+s16(imm))
            else:c.pop(rt,None)
        elif op==0x0D:
            if rs in c:c[rt]=u32(c[rs]|imm)
            else:c.pop(rt,None)
        elif op==0x0C:
            if rs in c:c[rt]=u32(c[rs]&imm)
            else:c.pop(rt,None)
        elif op==0 and f["fn"]==0x21:
            if rs in c and rt in c:c[rd]=u32(c[rs]+c[rt])
            else:c.pop(rd,None)
        elif op==0 and f["fn"]==0x25:
            if rs in c and rt in c:c[rd]=u32(c[rs]|c[rt])
            else:c.pop(rd,None)
        elif op in (0x23,0x25,0x24):c.pop(rt,None)
        elif op==0x03:
            for r in [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,24,25,31]:c.pop(r,None)
        else:
            wr=write_reg(w)
            if wr not in (None,0) and op!=0:c.pop(wr,None)
        c[0]=0
    return states

def dump_context(lines,words,load_base,idx,before=8,after=8,marker="<<<"):
    a=max(0,idx-before); b=min(len(words),idx+after+1)
    for j in range(a,b):
        pc=load_base+0x800+j*4; off=0x800+j*4; w=words[j]; mark=("  "+marker) if j==idx else ""
        lines.append("0x%08X [0x%06X] %08X  %-38s%s"%(pc,off,w,decode(w,pc),mark))

def find_materializations(words,target):
    hits=[]
    for i,w in enumerate(words):
        f=fields(w)
        if f["op"]!=0x0F:continue
        rt=f["rt"]; base=u32(f["imm"]<<16)
        for j in range(i+1,min(i+7,len(words))):
            f2=fields(words[j]); wr=write_reg(words[j])
            if f2["op"]==0x09 and f2["rt"]==rt and f2["rs"]==rt:
                if u32(base+s16(f2["imm"]))==target:hits.append((i,j,rt,"lui+addiu"))
                break
            if f2["op"]==0x0D and f2["rt"]==rt and f2["rs"]==rt:
                if u32(base|f2["imm"])==target:hits.append((i,j,rt,"lui+ori"))
                break
            if wr==rt:break
    return hits

def find_gp_candidates(words):
    out=[]
    for i,w in enumerate(words):
        f=fields(w)
        if f["op"]==0x0F and f["rt"]==28:
            base=u32(f["imm"]<<16)
            for j in range(i+1,min(i+9,len(words))):
                f2=fields(words[j]); wr=write_reg(words[j])
                if f2["op"]==0x09 and f2["rt"]==28 and f2["rs"]==28:
                    out.append((i,j,u32(base+s16(f2["imm"])),"lui+addiu"));break
                if f2["op"]==0x0D and f2["rt"]==28 and f2["rs"]==28:
                    out.append((i,j,u32(base|f2["imm"]),"lui+ori"));break
                if wr==28:break
    return out

def find_gp_slot_stores(words,imm_wanted):
    out=[]
    for i,w in enumerate(words):
        f=fields(w)
        if f["op"] in (0x2B,0x29) and f["rs"]==28 and f["imm"]==imm_wanted:out.append((i,f["rt"],f["op"]))
    return out

def main():
    here=os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv)>=2:src=os.path.abspath(sys.argv[1])
    else:
        candidates=[os.path.join(here,"GaiaMaster - Kamigami no Board Game (Japan).bin"),os.path.join(os.path.dirname(here),"GaiaMaster - Kamigami no Board Game (Japan).bin")]
        src=next((p for p in candidates if os.path.isfile(p)),candidates[0])
    if not os.path.isfile(src):
        print("[ERROR] BIN not found.");print("Drag the CLEAN Gaia Master BIN onto 00_RUN_FONT_MAPPING_INITIALIZER_SCANNER_0.2.cmd");return 2
    bin_sha=sha1_file(src).lower()
    if bin_sha==CLEAN_BIN_SHA1:base_name="CLEAN"
    elif bin_sha==ALPHA061_BIN_SHA1:base_name="ALPHA 0.6.1 FRONT"
    else:
        print("[ERROR] Unexpected BIN SHA1:",bin_sha);print("Expected CLEAN :",CLEAN_BIN_SHA1);print("or Alpha 0.6.1:",ALPHA061_BIN_SHA1);return 3
    with open(src,"rb") as rf:slps=read_iso_file(rf,SLPS_EXTENT,SLPS_SIZE)
    slps_sha=sha1_bytes(slps)
    if base_name=="CLEAN" and slps_sha!=CLEAN_SLPS_SHA1:
        print("[ERROR] CLEAN BIN selected but SLPS SHA1 mismatch:",slps_sha);return 4
    if slps[:8]!=b"PS-X EXE":print("[ERROR] SLPS does not start with PS-X EXE header.");return 5
    pc0,gp0,t_addr,t_size=struct.unpack_from("<IIII",slps,0x10);load_base=u32(t_addr-0x800)
    code_start=0x800;code_end=min(len(slps),0x800+t_size);code=slps[code_start:code_end];code=code[:len(code)&~3]
    words=list(struct.unpack("<%dI"%(len(code)//4),code))
    lines=[];ap=lines.append
    ap("GAIA MASTER FONT MAPPING INITIALIZER SCANNER 0.2");ap("="*88);ap("READ ONLY - KHONG SUA ROM - KHONG CAN BOOT GAME");ap("")
    ap("Input      : %s"%os.path.basename(src));ap("Base       : %s"%base_name);ap("BIN SHA1   : %s"%bin_sha);ap("SLPS SHA1  : %s"%slps_sha);ap("SLPS size  : %d (0x%X)"%(len(slps),len(slps)));ap("")
    ap("PS-X EXE");ap("  PC0      : 0x%08X"%pc0);ap("  GP0      : 0x%08X"%gp0);ap("  T_ADDR   : 0x%08X"%t_addr);ap("  T_SIZE   : 0x%08X"%t_size);ap("  loadbase : 0x%08X  (RAM = SLPS file offset + loadbase)"%load_base);ap("")
    ep_off=pc0-load_base;ap("="*88);ap("ENTRYPOINT CONTEXT");ap("="*88)
    if ep_off<0x800 or ep_off>=code_end:ap("[WARN] PC0 is outside executable scan range.")
    else:dump_context(lines,words,load_base,(ep_off-0x800)//4,16,48,"<<< PC0")
    ap("")
    gp_cands=find_gp_candidates(words);ap("="*88);ap("STATIC GP INITIALIZATION CANDIDATES");ap("="*88)
    if not gp_cands:ap("[INFO] No direct lui gp + addiu/ori gp pair found.");ap("GP may be constructed indirectly; gp-relative store xrefs below are still valid.")
    else:
        seen=set()
        for k,(i,j,val,how) in enumerate(gp_cands):
            key=(val,i,j)
            if key in seen:continue
            seen.add(key);pc=load_base+0x800+i*4;ap("[%02d] GP candidate 0x%08X via %s at 0x%08X"%(k+1,val,how,pc));ap("     atlas slot = 0x%08X"%u32(val+ATLAS_GP_OFF));ap("     map slot   = 0x%08X"%u32(val+MAPPING_GP_OFF));dump_context(lines,words,load_base,i,4,max(8,j-i+4),"<<< GP build");ap("")
    ap("");ap("="*88);ap("DIRECT WRITES TO RENDERER GP GLOBALS");ap("="*88);all_store_hits=[]
    for label,imm in (("atlas gp+0x518",ATLAS_GP_OFF),("mapping gp+0x51C",MAPPING_GP_OFF)):
        hits=find_gp_slot_stores(words,imm);ap("%s: %d direct store hit(s)"%(label,len(hits)))
        if not hits:ap("  [NONE] No direct sw/sh with base=gp and this immediate.")
        for n,(idx,src_reg,op) in enumerate(hits):
            pc=load_base+0x800+idx*4;kind="sw" if op==0x2B else "sh";ap("  [%02d] 0x%08X : %s %s,+0x%03X(gp)"%(n+1,pc,kind,REG[src_reg],imm));start=max(0,idx-48);states=forward_constants(words,start,idx+1);st=states.get(idx,{})
            if src_reg in st:ap("       source constant immediately before store: 0x%08X"%st[src_reg])
            else:ap("       source constant immediately before store: <not statically resolved in local window>")
            dump_context(lines,words,load_base,idx,16,12,"<<< GLOBAL WRITE");ap("");all_store_hits.append((label,idx,src_reg,st.get(src_reg)))
    ap("");ap("="*88);ap("KNOWN FONT ADDRESS MATERIALIZATIONS");ap("="*88)
    for label,target in (("atlas",ATLAS_ADDR),("mapping",MAPPING_ADDR)):
        hits=find_materializations(words,target);ap("%s 0x%08X: %d materialization hit(s)"%(label,target,len(hits)))
        for n,(i,j,reg,how) in enumerate(hits):
            pc=load_base+0x800+i*4;ap("  [%02d] 0x%08X register %s via %s"%(n+1,pc,REG[reg],how));dump_context(lines,words,load_base,i,5,max(8,j-i+5),"<<< TARGET PTR");ap("")
    ap("="*88);ap("RAW 32-BIT LITERAL OCCURRENCES IN SLPS");ap("="*88)
    for label,target in (("atlas",ATLAS_ADDR),("mapping",MAPPING_ADDR)):
        pat=struct.pack("<I",target);pos=0;found=[]
        while True:
            p=slps.find(pat,pos)
            if p<0:break
            found.append(p);pos=p+1
        ap("%s 0x%08X: %d raw literal hit(s)"%(label,target,len(found)))
        for p in found[:64]:ap("  SLPS+0x%06X -> RAM 0x%08X"%(p,u32(load_base+p)))
        if len(found)>64:ap("  ... %d more"%(len(found)-64))
    ap("")
    atlas_file=ATLAS_ADDR-load_base;map_file=MAPPING_ADDR-load_base;ap("="*88);ap("KNOWN STATIC RESOURCE LOCATIONS");ap("="*88);ap("atlas   RAM 0x%08X -> SLPS+0x%06X"%(ATLAS_ADDR,atlas_file));ap("mapping RAM 0x%08X -> SLPS+0x%06X"%(MAPPING_ADDR,map_file))
    if 0<=map_file<len(slps):
        ap("mapping first 64 bytes:");raw=slps[map_file:map_file+64]
        for i in range(0,len(raw),16):ap("  +0x%04X  %s"%(i,raw[i:i+16].hex(" ")))
    ap("");ap("="*88);ap("KNOWN SAMPLE MAPPING ENTRIES (STATIC DATA CHECK)");ap("="*88)
    for codepoint,name,expected in [(0x8273,"Ｔ",481),(0x8264,"Ｅ",466),(0x8272,"Ｓ",480),(0x889F,"亜",0)]:
        idx=codepoint&0x7FFF;off=map_file+idx*2
        if 0<=off+2<=len(slps):
            val=struct.unpack_from("<H",slps,off)[0];status="MATCH" if val==expected else "MISMATCH";ap("0x%04X %-2s index=0x%04X SLPS+0x%06X -> glyph %d (expected %d) [%s]"%(codepoint,name,idx,off,val,expected,status))
        else:ap("0x%04X %-2s index=0x%04X -> outside SLPS"%(codepoint,name,idx))
    ap("");ap("="*88);ap("INTERPRETATION");ap("="*88)
    if all_store_hits:
        ap("[FOUND] Direct ownership writes to gp+0x518/gp+0x51C exist in executable code.");resolved=[x for x in all_store_hits if x[3] in (ATLAS_ADDR,MAPPING_ADDR)]
        if resolved:ap("[STRONG] At least one global write source resolves locally to a known font address.")
        else:ap("[NEXT] Inspect the printed store contexts/callers to resolve source registers.")
    else:ap("[NEXT] No direct gp-relative writers found; use GP candidate(s) to search absolute slot ownership.");ap("       This report still narrows the initializer without modifying the ROM.")
    ap("");ap("Hard gate remains: NO ROM proof until mapping ownership is demonstrated.");ap("No runtime pointer redirect. No 12x16 production path. No composite overlay.")
    report=os.path.join(here,"GaiaMaster_FontMappingInitializerScanner_02.txt")
    with open(report,"w",encoding="utf-8") as f:f.write("\n".join(lines)+"\n")
    print("[OK] READ-ONLY scan complete.");print("Report:",report);return 0

if __name__=="__main__":
    try:sys.exit(main())
    except Exception as e:print("[ERROR]",repr(e));sys.exit(9)

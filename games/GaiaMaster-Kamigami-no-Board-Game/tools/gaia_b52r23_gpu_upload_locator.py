#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B52R23 read-only GPU/DMA callsite locator for Gaia Master PS1."""
from __future__ import annotations
import argparse,csv,hashlib,struct
from collections import defaultdict
from pathlib import Path

CLEAN="f4d5298583c90d89c4b7e51d2dde160ee07f2aec"
BASE="0ced9982e1b00566b42ace047236378826c2aa1c"
RAW,USER=2352,2048
SLPS_EXTENT,SLPS_SIZE=24,487424
HDR=0x800
REG="r0 at v0 v1 a0 a1 a2 a3 t0 t1 t2 t3 t4 t5 t6 t7 s0 s1 s2 s3 s4 s5 s6 s7 t8 t9 k0 k1 gp sp s8 ra".split()
HW={0x1F801810:"GP0",0x1F801814:"GP1/GPUSTAT",0x1F8010A0:"DMA2_MADR",0x1F8010A4:"DMA2_BCR",0x1F8010A8:"DMA2_CHCR",0x1F8010F0:"DPCR",0x1F8010F4:"DICR"}
CMD={0xA000:"GP0_A0_CPU_TO_VRAM",0x8000:"GP0_80_VRAM_TO_VRAM",0xC000:"GP0_C0_VRAM_TO_CPU"}

def sha1(p):
 h=hashlib.sha1()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(8*1024*1024),b""): h.update(b)
 return h.hexdigest().lower()

def read_slps(p):
 out=bytearray(); left=SLPS_SIZE; lba=SLPS_EXTENT
 with p.open("rb") as f:
  while left:
   f.seek(lba*RAW); s=f.read(RAW)
   if len(s)!=RAW or s[15]!=2 or (s[18]&0x20) or s[16:20]!=s[20:24]: raise RuntimeError(f"Bad MODE2/Form1 sector {lba}")
   n=min(USER,left); out+=s[24:24+n]; left-=n; lba+=1
 return bytes(out)

def sx(v): return v-0x10000 if v&0x8000 else v
def op(w): return (w>>26)&63
def rs(w): return (w>>21)&31
def rt(w): return (w>>16)&31
def im(w): return w&0xffff

def dis(pc,w):
 o=op(w)
 if w==0:return "nop"
 if o==15:return f"lui {REG[rt(w)]},0x{im(w):04X}"
 if o==13:return f"ori {REG[rt(w)]},{REG[rs(w)]},0x{im(w):04X}"
 if o==9:return f"addiu {REG[rt(w)]},{REG[rs(w)]},{sx(im(w))}"
 mm={0x23:"lw",0x2b:"sw",0x20:"lb",0x24:"lbu",0x21:"lh",0x25:"lhu",0x28:"sb",0x29:"sh"}
 if o in mm:return f"{mm[o]} {REG[rt(w)]},{sx(im(w))}({REG[rs(w)]})"
 if o==3:return f"jal 0x{(((pc+4)&0xf0000000)|((w&0x3ffffff)<<2)):08X}"
 if o==0 and (w&63)==8:return f"jr {REG[rs(w)]}"
 return f"word 0x{w:08X}"

def scan(words,addr):
 hits=[]
 for i,w in enumerate(words):
  if op(w)!=15 or im(w)!=0x1f80: continue
  r=rt(w); val=0x1f800000; lui=addr+i*4
  for j in range(i+1,min(i+18,len(words))):
   x=words[j]; pc=addr+j*4; o=op(x)
   if o in (2,3) or (o==0 and (x&63) in (8,9)): break
   if o in (0x23,0x2b,0x20,0x24,0x21,0x25,0x28,0x29) and rs(x)==r:
    a=(val+sx(im(x)))&0xffffffff
    if a in HW:
     hits.append(dict(pc=pc,file_off=HDR+j*4,word=x,mnemonic=dis(pc,x),hw_addr=a,hw_name=HW[a],access="WRITE" if o in (0x2b,0x28,0x29) else "READ",lui_pc=lui,source_reg=REG[rt(x)]))
   if o==13 and rt(x)==r and rs(x)==r: val=(val|im(x))&0xffffffff
   elif o==9 and rt(x)==r and rs(x)==r: val=(val+sx(im(x)))&0xffffffff
   elif o==15 and rt(x)==r: val=im(x)<<16
   elif rt(x)==r and o not in (0x2b,0x28,0x29): break
 u={}
 for h in hits:u[(h["pc"],h["hw_addr"],h["access"])]=h
 return list(u.values())

def func_start(words,addr,pc):
 i=(pc-addr)//4
 for j in range(i,max(-1,i-96),-1):
  w=words[j]
  if op(w)==9 and rs(w)==29 and rt(w)==29 and sx(im(w))<0:return addr+j*4
  if j<i-4 and op(w)==0 and (w&63)==8 and rs(w)==31:break
 return pc&~0xf

def selftest():
 ws=[0x3c081f80,0xad091810,0x3c0aa000,0x03e00008,0]
 hs=scan(ws,0x80010000)
 assert any(h["hw_addr"]==0x1f801810 and h["access"]=="WRITE" for h in hs)
 assert any(op(w)==15 and im(w) in CMD for w in ws)
 print("B52R23 SELFTEST PASS")

def main():
 ap=argparse.ArgumentParser(); ap.add_argument("bin",nargs="?",type=Path); ap.add_argument("--selftest",action="store_true"); a=ap.parse_args()
 if a.selftest:selftest();return 0
 if a.bin is None:ap.error("BIN required unless --selftest")
 p=a.bin.expanduser().resolve(); sh=sha1(p)
 if sh not in (BASE,CLEAN):raise RuntimeError(f"Unknown BIN SHA1 {sh}; expected B52R14R1 {BASE} or CLEAN {CLEAN}")
 slps=read_slps(p)
 if not slps.startswith(b"PS-X EXE"):raise RuntimeError("SLPS_020.75 is not PS-X EXE")
 pc0,gp0,taddr,tsize=struct.unpack_from("<IIII",slps,0x10)
 if tsize<=0 or HDR+tsize>len(slps):tsize=len(slps)-HDR
 text=slps[HDR:HDR+tsize]; words=[struct.unpack_from("<I",text,i)[0] for i in range(0,len(text)-3,4)]
 hits=scan(words,taddr); calls=defaultdict(list); cmds=[]
 for i,w in enumerate(words):
  pc=taddr+i*4
  if op(w)==3:calls[((pc+4)&0xf0000000)|((w&0x3ffffff)<<2)].append(pc)
  if op(w)==15 and im(w) in CMD:cmds.append(dict(pc=pc,file_off=HDR+i*4,word=w,mnemonic=dis(pc,w),command=CMD[im(w)],reg=REG[rt(w)]))
 routines=defaultdict(list)
 for h in hits:
  h["func_start"]=func_start(words,taddr,h["pc"]); h["direct_callers"]=" ".join(f"0x{x:08X}" for x in calls.get(h["func_start"],[])[:24]); routines[h["func_start"]].append(h)
 scored=[]
 for fs,hs in routines.items():
  acc={(h["hw_name"],h["access"]) for h in hs}; names={h["hw_name"] for h in hs}; s=len(hs)
  s+=100 if ("GP0","WRITE") in acc else 0; s+=80 if ("DMA2_CHCR","WRITE") in acc else 0; s+=50 if ("DMA2_MADR","WRITE") in acc else 0; s+=40 if ("DMA2_BCR","WRITE") in acc else 0; s+=10 if ("GP1/GPUSTAT","WRITE") in acc else 0
  scored.append((s,fs,names,hs))
 scored.sort(reverse=True)
 out=p.parent; hp=out/"GaiaMaster_B52R23_GPU_MMIO_HITS.csv"; cp=out/"GaiaMaster_B52R23_GPU_COMMAND_BUILDERS.csv"; bp=out/"GaiaMaster_B52R23_GPU_BREAKPOINTS.txt"; rp=out/"GaiaMaster_B52R23_GPU_UPLOAD_LOCATOR_REPORT.txt"
 with hp.open("w",encoding="utf-8-sig",newline="") as f:
  fields="pc file_off word mnemonic hw_addr hw_name access lui_pc source_reg func_start direct_callers".split();w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for h in sorted(hits,key=lambda x:x["pc"]):
   r=h.copy()
   for k in "pc file_off word hw_addr lui_pc func_start".split():r[k]=f"0x{r[k]:08X}"
   w.writerow(r)
 with cp.open("w",encoding="utf-8-sig",newline="") as f:
  fields="pc file_off word mnemonic command reg".split();w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for z in cmds:
   r=z.copy()
   for k in "pc file_off word".split():r[k]=f"0x{r[k]:08X}"
   w.writerow(r)
 bl=["GAIA MASTER B52R23 GPU BREAKPOINT CANDIDATES","="*78,"Set Exec breakpoints on top routine/hit PCs while entering the green main menu.",""]
 for s,fs,names,hs in scored[:40]:
  bl.append(f"ROUTINE 0x{fs:08X} score={s} hw={','.join(sorted(names))} callers={','.join(f'0x{x:08X}' for x in calls.get(fs,[])[:12]) or '-'}")
  for h in sorted(hs,key=lambda x:x["pc"]):bl.append(f"  hit 0x{h['pc']:08X} {h['access']:5s} {h['hw_name']:12s} {h['mnemonic']}")
 bp.write_text("\n".join(bl)+"\n",encoding="utf-8")
 lines=["GAIA MASTER B52R23 GPU UPLOAD LOCATOR","="*78,f"Input SHA1    : {sh}",f"Authority     : {'B52R14R1 EXACT' if sh==BASE else 'CLEAN JAPAN EXACT (fallback)'}",f"EXE entry PC  : 0x{pc0:08X}",f"EXE initial GP: 0x{gp0:08X}",f"Text RAM addr : 0x{taddr:08X}",f"Text size     : 0x{tsize:X}","",f"GPU/DMA MMIO hits       : {len(hits)}",f"Heuristic GPU routines  : {len(routines)}",f"GP0 command builders    : {len(cmds)}","","TOP ROUTINES:"]
 lines += [f"- 0x{fs:08X} score={s} hits={len(hs)} hw={','.join(sorted(names))} callers={len(calls.get(fs,[]))}" for s,fs,names,hs in scored[:20]] or ["- none"]
 lines += ["","INTERPRETATION:","- Breakpoint locator only; not proof of menu ownership.","- In PCSX-Redux use interpreter + debugger for CPU breakpoints.","- Correlate target frame with GPU Logger + Show origins.","- Prefer GP0 + DMA2 setup routines over generic GP1/status helpers.","- Do not patch until live menu upload/render ownership is proven.","- Overall Runtime PASS remains NO.","",f"MMIO CSV       : {hp.name}",f"Command CSV    : {cp.name}",f"Breakpoint TXT : {bp.name}"]
 rp.write_text("\n".join(lines)+"\n",encoding="utf-8");print("\n".join(lines));print("Report:",rp);return 0

if __name__=="__main__":
 try:raise SystemExit(main())
 except SystemExit:raise
 except Exception as e:print("[ERROR]",repr(e));raise SystemExit(9)

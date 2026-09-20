#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B52R22 read-only live-source probe for Gaia Master PS1.

Never patches/copies a BIN. It verifies B52R14R1 or CLEAN, indexes ISO9660 from
MODE2/2352, inspects only the five B52R20 evidence spans, recursively opens
checksum-valid BDP containers, and performs bounded compression probes.
"""
from __future__ import annotations
import argparse, csv, hashlib, math, struct, zlib
from collections import Counter
from pathlib import Path

CLEAN_SHA1="f4d5298583c90d89c4b7e51d2dde160ee07f2aec"
BASE_SHA1="0ced9982e1b00566b42ace047236378826c2aa1c"
RAW,USER=2352,2048
MAX_DEPTH=8
TARGETS=("ストーリーモード","対戦モード","武器スキルリスト","オプション","キャラクターセレクト","冒険のはじまり")
TB={s:s.encode("cp932") for s in TARGETS}
REGIONS={
 "PRGPACK":((0xBF7AC,0xDDA98,"PRG_OWNER_A"),(0xDDA98,0x104660,"PRG_OWNER_B"),(0x14B970,0x155C1C,"PRG_OWNER_C")),
 "SCR_DATA":((0x9741A8,0x994850,"SCR_OWNER_A"),(0x9C1BF4,0x9CE4CC,"SCR_OWNER_B")),
}
TIM=b"\x10\x00\x00\x00"

def sha1_file(p):
 h=hashlib.sha1()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(8*1024*1024),b""): h.update(b)
 return h.hexdigest().lower()

def ent(b):
 if not b:return 0.0
 c=Counter(b); n=len(b)
 return -sum((v/n)*math.log2(v/n) for v in c.values())

def sector(f,lba):
 f.seek(lba*RAW); s=f.read(RAW)
 if len(s)!=RAW or s[15]!=2 or (s[18]&0x20) or s[16:20]!=s[20:24]:
  raise RuntimeError(f"Expected MODE2/Form1 sector at LBA {lba}")
 return s[24:24+USER]

def extent(f,lba,size):
 o=bytearray()
 while size:
  s=sector(f,lba); n=min(USER,size); o+=s[:n]; size-=n; lba+=1
 return bytes(o)

def rec(r):
 if len(r)<34: raise RuntimeError("short ISO9660 record")
 e=struct.unpack_from("<I",r,2)[0]; z=struct.unpack_from("<I",r,10)[0]; fl=r[25]; n=r[32]
 return e,z,fl,r[33:33+n]

def nm(x):
 if x==b"\0":return "."
 if x==b"\1":return ".."
 s=x.decode("ascii","replace").split(";",1)[0]
 return s.rstrip(".")

def iso_index(f):
 p=sector(f,16)
 if p[0]!=1 or p[1:6]!=b"CD001": raise RuntimeError("ISO9660 PVD missing")
 rl=p[156]; root=rec(p[156:156+rl]); out=[]; seen=set()
 def walk(e,z,parent):
  if (e,z) in seen:return
  seen.add((e,z)); d=extent(f,e,z); q=0
  while q<len(d):
   n=d[q]
   if n==0:q=((q//USER)+1)*USER; continue
   if q+n>len(d):break
   ee,zz,fl,raw=rec(d[q:q+n]); q+=n; name=nm(raw)
   if name in (".",".."):continue
   path=f"{parent}/{name}" if parent else name; isdir=bool(fl&2)
   out.append((path,ee,zz,isdir))
   if isdir:walk(ee,zz,path)
 walk(root[0],root[1],""); return out

def find_file(xs,tok):
 tok=tok.upper(); ys=[x for x in xs if not x[3] and tok in Path(x[0]).name.upper()]
 ys.sort(key=lambda x:(not Path(x[0]).name.upper().startswith(tok),x[0].count('/'),x[0]))
 return ys[0] if ys else None

def bdp_sum(b):
 if len(b)<8:return -1
 s=(sum(b[:4])+sum(b[8:]))&0xffff
 return ((~s&0xffff)<<16)|s

def bdp(b):
 if len(b)<16:return None
 magic,stored,toc,count=struct.unpack_from("<IIII",b,0)
 if magic!=0x10F0 or count>65535 or toc!=8+count*8 or bdp_sum(b)!=stored:return None
 base=8+toc
 if 16+count*8>base or base>len(b):return None
 mem=[]
 for i in range(count):
  rel,z=struct.unpack_from("<II",b,16+i*8); a=base+rel; e=a+z
  if z<=0 or a<base or e>len(b):return None
  mem.append((i,a,e))
 return mem

def tim_at(b,o):
 if o+8>len(b) or b[o:o+4]!=TIM:return False
 flags=struct.unpack_from("<I",b,o+4)[0]
 if flags&~0xf or (flags&7)>3:return False
 p=o+8
 def blk(q):
  if q+12>len(b):return None
  z=struct.unpack_from("<I",b,q)[0]
  if z<12 or q+z>len(b):return None
  x,y,w,h=struct.unpack_from("<HHHH",b,q+4)
  if not w or not h or x>=1024 or y>=512 or w>1024 or h>512 or z!=12+w*h*2:return None
  return z
 if flags&8:
  z=blk(p)
  if z is None:return False
  p+=z
 return blk(p) is not None

def tim_count(b,cap=64):
 n=0;q=0
 while n<cap:
  q=b.find(TIM,q)
  if q<0:break
  if tim_at(b,q):n+=1
  q+=1
 return n

def hits(b):return [s for s,x in TB.items() if x in b]

def zdec(d,w,maxout):
 try:
  o=zlib.decompressobj(w); b=o.decompress(d,maxout+1)
  if len(b)>maxout:return None
  b+=o.flush()
  return b if o.eof and len(b)<=maxout else None
 except zlib.error:return None

def lz10(d,maxout):
 if len(d)<4 or d[0]!=0x10:return None
 want=d[1]|d[2]<<8|d[3]<<16
 if not 0<want<=maxout:return None
 s=4;o=bytearray()
 try:
  while len(o)<want:
   fl=d[s];s+=1
   for bit in range(8):
    if len(o)>=want:break
    if fl&(0x80>>bit):
     x=(d[s]<<8)|d[s+1];s+=2; ln=(x>>12)+3; disp=(x&0xfff)+1
     if disp>len(o):return None
     for _ in range(ln):
      o.append(o[-disp])
      if len(o)>=want:break
    else:o.append(d[s]);s+=1
  return bytes(o)
 except IndexError:return None

def decodes(b,maxout):
 # only prefix 0 and small header skips, enough to catch common wrapped streams
 for p in (0,4,8,12,16,24,32):
  if p>=len(b):continue
  d=b[p:]
  for name,w in (("zlib",15),("gzip",31),("raw-deflate",-15)):
   o=zdec(d,w,maxout)
   if o is not None and len(o)>=32:yield name,p,o
  o=lz10(d,maxout)
  if o is not None and len(o)>=32:yield "lz10",p,o

def analyze(src,region_name,whole,a,e,maxout,leaves,decs,maplines):
 if a<0 or e>len(whole) or a>=e:
  maplines.append(f"[SKIP] {src} {region_name} out of bounds 0x{a:X}..0x{e:X} / 0x{len(whole):X}");return
 root=whole[a:e]
 def walk(b,abso,path,depth):
  m=bdp(b) if depth<MAX_DEPTH else None
  if m:
   maplines.append(f"[BDP] {src} {region_name} {path} abs=0x{abso:X} size={len(b)} count={len(m)}")
   for i,x,y in m:walk(b[x:y],abso+x,f"{path}/m{i:03d}",depth+1)
   return
  E=ent(b); zr=(b.count(0)/len(b)) if b else 0; hs=hits(b); tc=tim_count(b)
  leaves.append(dict(source_file=src,region=region_name,path=path,depth=depth,abs_offset_hex=f"0x{abso:X}",size=len(b),entropy=f"{E:.4f}",zero_ratio=f"{zr:.4f}",direct_targets=" | ".join(hs),direct_tim_count=tc,header_hex=b[:32].hex(),note="opaque/high-entropy" if E>=6.5 and len(b)>=512 else ""))
  if len(b)<32:return
  for method,p,o in decodes(b,maxout):
   th=hits(o); tt=tim_count(o)
   # keep only concrete evidence for raw-deflate, or signature decoders
   if not th and not tt and method=="raw-deflate":continue
   score=100*len(th)+30*tt+(15 if method in ("zlib","gzip","lz10") else 0)
   decs.append(dict(source_file=src,region=region_name,path=path,abs_offset_hex=f"0x{abso:X}",input_size=len(b),method=method,prefix=p,output_size=len(o),target_hits=" | ".join(th),tim_count=tt,score=score,note="NEW_EVIDENCE" if th or tt else "signature-decode"))
 walk(root,a,region_name,0)

def wcsv(p,rows,fields):
 with p.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def selftest():
 x=b"X"+TB["ストーリーモード"]+b"Y"*64; z=zlib.compress(x)
 if not any(TB["ストーリーモード"] in o for _,_,o in decodes(z,1<<20)):raise RuntimeError("zlib selftest")
 l=bytes([0x10,8,0,0,0])+b"ABCDEFGH"
 if lz10(l,1024)!=b"ABCDEFGH":raise RuntimeError("lz10 selftest")
 b=bytearray(28);struct.pack_into("<IIII",b,0,0x10F0,0,16,1);struct.pack_into("<II",b,16,0,4);b[24:]=b"TEST";struct.pack_into("<I",b,4,bdp_sum(b))
 if not bdp(bytes(b)):raise RuntimeError("BDP selftest")
 print("B52R22 SELFTEST PASS")

def main():
 ap=argparse.ArgumentParser(description="Gaia Master B52R22 read-only live-source probe")
 ap.add_argument("bin",nargs="?",type=Path);ap.add_argument("--max-output-mb",type=int,default=16);ap.add_argument("--selftest",action="store_true");a=ap.parse_args()
 if a.selftest:selftest();return 0
 if a.bin is None:ap.error("BIN path required unless --selftest")
 p=a.bin.expanduser().resolve()
 if not p.is_file():raise RuntimeError(f"BIN not found: {p}")
 if not 1<=a.max_output_mb<=64:raise RuntimeError("--max-output-mb must be 1..64")
 sh=sha1_file(p)
 if sh not in (BASE_SHA1,CLEAN_SHA1):raise RuntimeError(f"Unknown BIN SHA1 {sh}; expected B52R14R1 {BASE_SHA1} or CLEAN {CLEAN_SHA1}")
 authority="B52R14R1 EXACT" if sh==BASE_SHA1 else "CLEAN JAPAN EXACT (fallback)"
 with p.open("rb") as f:
  xs=iso_index(f); pe=find_file(xs,"PRGPACK"); se=find_file(xs,"SCR_DATA")
  if pe is None:raise RuntimeError("PRGPACK not found")
  prg=extent(f,pe[1],pe[2]); scr=extent(f,se[1],se[2]) if se else None
 leaves=[];decs=[];maps=[]; maxout=a.max_output_mb*1024*1024
 for x,y,n in REGIONS["PRGPACK"]:analyze("PRGPACK",n,prg,x,y,maxout,leaves,decs,maps)
 if scr is not None:
  for x,y,n in REGIONS["SCR_DATA"]:analyze("SCR_DATA",n,scr,x,y,maxout,leaves,decs,maps)
 else:maps.append("[MISSING] SCR_DATA not found")
 decs.sort(key=lambda r:(-r["score"],r["source_file"],r["abs_offset_hex"],r["method"]))
 out=p.parent; lp=out/"GaiaMaster_B52R22_LIVE_SOURCE_LEAVES.csv"; dp=out/"GaiaMaster_B52R22_LIVE_SOURCE_DECODES.csv"; rp=out/"GaiaMaster_B52R22_LIVE_SOURCE_PROBE_REPORT.txt"
 lf=["source_file","region","path","depth","abs_offset_hex","size","entropy","zero_ratio","direct_targets","direct_tim_count","header_hex","note"]
 df=["source_file","region","path","abs_offset_hex","input_size","method","prefix","output_size","target_hits","tim_count","score","note"]
 wcsv(lp,leaves,lf);wcsv(dp,decs,df)
 dt=[r for r in decs if r["target_hits"]]; di=[r for r in decs if r["tim_count"]]
 opaque=sorted((r for r in leaves if float(r["entropy"])>=6.5 and int(r["size"])>=512),key=lambda r:(-float(r["entropy"]),-int(r["size"])))[:30]
 lines=["GAIA MASTER B52R22 LIVE-SOURCE PROBE","="*78,f"Input BIN  : {p}",f"Input SHA1 : {sh}",f"Authority  : {authority}",f"ISO files  : {sum(not x[3] for x in xs)}",f"PRGPACK    : {pe[0]} extent={pe[1]} size={pe[2]}",f"SCR_DATA   : {se[0] if se else 'NOT FOUND'}","","SCOPE:","- READ ONLY. No BIN/CUE/ISO output.","- Only five B52R20 evidence spans are inspected.","- Known PRGPACK CP932 copies remain runtime-dead.","- New evidence = decoded target text and/or decoded structurally-valid TIM.","",f"Leaf observations    : {len(leaves)}",f"Decode rows kept     : {len(decs)}",f"Decoded target hits  : {len(dt)}",f"Decoded TIM hits     : {len(di)}","","BDP / REGION MAP:"]
 lines+=maps[:500]
 lines+=["","TOP DECODE CANDIDATES:"]
 if decs:
  for r in decs[:80]:lines.append(f"- score={r['score']} {r['source_file']} {r['region']} {r['path']} {r['abs_offset_hex']} {r['method']}@+0x{r['prefix']:X} out={r['output_size']} targets={r['target_hits'] or '-'} TIM={r['tim_count']}")
 else:lines.append("- none")
 lines+=["","OPAQUE/HIGH-ENTROPY LEAVES FOR RUNTIME TRACE:"]
 if opaque:
  for r in opaque:lines.append(f"- {r['source_file']} {r['region']} {r['path']} {r['abs_offset_hex']} size={r['size']} H={r['entropy']} zero={r['zero_ratio']} head={r['header_hex']}")
 else:lines.append("- none")
 if dt:nxt="B52R23: inspect highest decoded-target candidate and prove ownership before patching."
 elif di:nxt="B52R23: render highest decoded-TIM candidate only; do not patch text yet."
 else:nxt="B52R23: no static live-source proof. Trace main-menu VRAM/upload/decompression at runtime, using opaque leaves as candidates."
 lines+=["","VERDICT:",nxt,"Overall Runtime PASS remains NO.","",f"Leaves CSV : {lp.name}",f"Decodes CSV: {dp.name}"]
 rp.write_text("\n".join(lines)+"\n",encoding="utf-8");print("\n".join(lines));print("Report:",rp);return 0

if __name__=="__main__":
 try:raise SystemExit(main())
 except SystemExit:raise
 except Exception as e:print("[ERROR]",repr(e));raise SystemExit(9)

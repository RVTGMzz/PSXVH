#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv
from pathlib import Path
RAM=0x200000
def hx(s):return int(str(s).strip(),16)
def c16(v):return v if v else 0x10000
def load(p):
 o=[]
 with p.open("r",encoding="utf-8-sig",newline="") as f:
  for r in csv.DictReader(f,delimiter="\t"):r["_v"]=hx(r["value"]);o.append(r)
 return o
def tx(ev,pfx):
 starts=[i for i,e in enumerate(ev) if e["hw"]==pfx+"_CHCR" and((e["_v"]>>24)&1)]
 if not starts:return None
 i=starts[-1];m=b=None
 for e in ev[:i+1]:
  if e["hw"]==pfx+"_MADR":m=e["_v"]
  elif e["hw"]==pfx+"_BCR":b=e["_v"]
 return None if m is None else(m,b or 0,ev[i]["_v"])
def rng(m,b,ch):
 sync=(ch>>9)&3;step=(ch>>1)&1
 if sync==0:w=c16(b&0xffff)
 elif sync==1:w=c16(b&0xffff)*c16((b>>16)&0xffff)
 else:return None,sync,0
 w=min(w,RAM//4);n=w*4;m&=0x1fffff;start=m if not step else(m-(n-4))%RAM
 return ([(start,start+n)] if start+n<=RAM else[(start,RAM),(0,start+n-RAM)]),sync,n
def ov(a,b):return sum(max(0,min(e1,e2)-max(s1,s2)) for s1,e1 in a for s2,e2 in b)
def selftest():
 assert ov([(0x1000,0x1100)],[(0xf00,0x1080)])==0x80
 g,_,_=rng(0x1000,0x00010040,0x01000201);c,_,_=rng(0x1000,0x40,0x11000000);assert g==c and ov(g,c)==0x100
 print("B52R26 CD/GPU OVERLAP ANALYZER SELFTEST PASS")
def main():
 ap=argparse.ArgumentParser();ap.add_argument("gpu_trace",nargs="?",type=Path);ap.add_argument("cd_trace",nargs="?",type=Path);ap.add_argument("--selftest",action="store_true");a=ap.parse_args()
 if a.selftest:selftest();return 0
 if not a.gpu_trace or not a.cd_trace:ap.error("B52R24 TRACE.tsv and B52R26 CD_DMA_TRACE.tsv required")
 g=tx(load(a.gpu_trace),"DMA2");c=tx(load(a.cd_trace),"DMA3")
 if not g:raise RuntimeError("No B52R24 DMA2 start")
 if not c:raise RuntimeError("No B52R26 DMA3 start")
 gr,gs,gn=rng(*g);cr,cs,cn=rng(*c)
 L=["GAIA MASTER B52R26 CD->GPU OVERLAP","="*78,f"GPU MADR/BCR/CHCR: 0x{g[0]:08X} / 0x{g[1]:08X} / 0x{g[2]:08X}",f"GPU SyncMode: {gs}",f"CD MADR/BCR/CHCR : 0x{c[0]:08X} / 0x{c[1]:08X} / 0x{c[2]:08X}",f"CD SyncMode: {cs}",""]
 if gr is None:L+=["VERDICT: GPU_SYNC2_COMMAND_LIST","Direct CD-range overlap cannot identify the texture asset source. Keep tracing GPU-origin/texture upload.","Overall Runtime PASS remains NO."]
 else:
  x=ov(gr,cr);exact=gr==cr;cover=x==gn and gn>0;p=100*x/gn if gn else 0
  fmt=lambda z:", ".join(f"0x{s:06X}..0x{e:06X} ({e-s} bytes)" for s,e in z)
  verdict="EXACT_RANGE_MATCH" if exact else("GPU_SOURCE_FULLY_INSIDE_CD_DMA" if cover else("PARTIAL_OVERLAP" if x else"NO_OVERLAP"))
  L += [f"GPU source: {fmt(gr)}",f"CD destination: {fmt(cr)}",f"Overlap: {x} bytes ({p:.2f}% of GPU source)",f"VERDICT: {verdict}","","INTERPRETATION:","- EXACT/FULL-COVER is strong upstream RAM-load evidence only if both captures belong to the same target transition.","- PARTIAL needs more transactions or CPU-transform evidence.","- NO_OVERLAP means this CD DMA is not the direct fill of the captured GPU-source range.","- Even exact overlap does not yet identify ISO file/member/LBA.","- Next after a correlated match: trace CDROM command/LBA or archive load ownership.","- Overall Runtime PASS remains NO."]
 out=a.gpu_trace.with_name("GaiaMaster_B52R26_CD_GPU_OVERLAP_REPORT.txt");out.write_text("\n".join(L)+"\n",encoding="utf-8");print("\n".join(L));print("Report:",out);return 0
if __name__=="__main__":raise SystemExit(main())

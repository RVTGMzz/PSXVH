#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,struct
from collections import defaultdict
from pathlib import Path
CLEAN="f4d5298583c90d89c4b7e51d2dde160ee07f2aec"; BASE="0ced9982e1b00566b42ace047236378826c2aa1c"
RAW,USER,HDR=2352,2048,0x800; EXTENT,SIZE=24,487424
REG="r0 at v0 v1 a0 a1 a2 a3 t0 t1 t2 t3 t4 t5 t6 t7 s0 s1 s2 s3 s4 s5 s6 s7 t8 t9 k0 k1 gp sp s8 ra".split()
HW={0x1F8010B0:"DMA3_MADR",0x1F8010B4:"DMA3_BCR",0x1F8010B8:"DMA3_CHCR"}
def sha1(p):
 h=hashlib.sha1()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(8*1024*1024),b""):h.update(b)
 return h.hexdigest().lower()
def slps(p):
 o=bytearray();left=SIZE;lba=EXTENT
 with p.open("rb") as f:
  while left:
   f.seek(lba*RAW);s=f.read(RAW)
   if len(s)!=RAW or s[15]!=2 or (s[18]&0x20) or s[16:20]!=s[20:24]:raise RuntimeError(f"Bad MODE2/Form1 sector {lba}")
   n=min(USER,left);o+=s[24:24+n];left-=n;lba+=1
 return bytes(o)
def sx(v):return v-0x10000 if v&0x8000 else v
def op(w):return(w>>26)&63
def rs(w):return(w>>21)&31
def rt(w):return(w>>16)&31
def im(w):return w&0xffff
def scan(words,addr):
 out=[]
 for i,w in enumerate(words):
  if op(w)!=15 or im(w)!=0x1f80:continue
  r=rt(w);base=0x1f800000
  for j in range(i+1,min(i+18,len(words))):
   x=words[j];o=op(x);pc=addr+j*4
   if o in(2,3) or(o==0 and(x&63)in(8,9)):break
   if o in(0x23,0x2b,0x20,0x24,0x21,0x25,0x28,0x29) and rs(x)==r:
    a=(base+sx(im(x)))&0xffffffff
    if a in HW:out.append({"pc":pc,"hw_addr":a,"hw_name":HW[a],"access":"WRITE" if o in(0x2b,0x28,0x29) else "READ","source_reg":REG[rt(x)]})
   if o==13 and rt(x)==r and rs(x)==r:base|=im(x)
   elif o==9 and rt(x)==r and rs(x)==r:base=(base+sx(im(x)))&0xffffffff
   elif o==15 and rt(x)==r:base=im(x)<<16
   elif rt(x)==r and o not in(0x2b,0x28,0x29):break
 u={}
 for h in out:u[(h["pc"],h["hw_addr"],h["access"])]=h
 return list(u.values())
def fstart(words,addr,pc):
 i=(pc-addr)//4
 for j in range(i,max(-1,i-96),-1):
  w=words[j]
  if op(w)==9 and rs(w)==29 and rt(w)==29 and sx(im(w))<0:return addr+j*4
  if j<i-4 and op(w)==0 and(w&63)==8 and rs(w)==31:break
 return pc&~0xf
def selftest():
 h=scan([0x3c081f80,0xad0910b0,0xad0a10b8,0x03e00008],0x80010000)
 assert any(x["hw_addr"]==0x1f8010b0 for x in h) and any(x["hw_addr"]==0x1f8010b8 for x in h)
 print("B52R26 CD DMA LOCATOR SELFTEST PASS")
def main():
 ap=argparse.ArgumentParser();ap.add_argument("bin",nargs="?",type=Path);ap.add_argument("--selftest",action="store_true");a=ap.parse_args()
 if a.selftest:selftest();return 0
 if not a.bin:ap.error("BIN required")
 p=a.bin.resolve();sh=sha1(p)
 if sh not in(BASE,CLEAN):raise RuntimeError(f"Unknown BIN SHA1 {sh}")
 x=slps(p)
 if not x.startswith(b"PS-X EXE"):raise RuntimeError("SLPS is not PS-X EXE")
 entry,gp,taddr,tsize=struct.unpack_from("<IIII",x,0x10)
 if tsize<=0 or HDR+tsize>len(x):tsize=len(x)-HDR
 words=[struct.unpack_from("<I",x,HDR+i)[0] for i in range(0,tsize-3,4)]
 hits=scan(words,taddr);groups=defaultdict(list)
 for h in hits:
  h["func_start"]=fstart(words,taddr,h["pc"]);groups[h["func_start"]].append(h)
 ranked=[]
 for fs,hs in groups.items():
  names={h["hw_name"] for h in hs if h["access"]=="WRITE"};s=len(hs)+(120 if"DMA3_CHCR"in names else 0)+(90 if"DMA3_MADR"in names else 0)+(70 if"DMA3_BCR"in names else 0)+(250 if{"DMA3_MADR","DMA3_BCR","DMA3_CHCR"}<=names else 0)
  ranked.append((s,fs,hs))
 ranked.sort(reverse=True)
 out=p.parent;csvp=out/"GaiaMaster_B52R26_CD_DMA_MMIO_HITS.csv";luap=out/"GaiaMaster_B52R26_PCSX_CD_DMA_CAPTURE.lua";rpt=out/"GaiaMaster_B52R26_CD_DMA_LOCATOR_REPORT.txt"
 with csvp.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=["pc","hw_addr","hw_name","access","source_reg","func_start"]);w.writeheader()
  for h in sorted(hits,key=lambda z:z["pc"]):
   r=h.copy()
   for k in("pc","hw_addr","func_start"):r[k]=f"0x{r[k]:08X}"
   w.writerow(r)
 exact=[];seen=set()
 for score,fs,hs in ranked[:16]:
  for h in hs:
   if h["access"]!="WRITE":continue
   k=(h["pc"],h["hw_name"],h["source_reg"])
   if k not in seen:seen.add(k);exact.append((score,fs,h))
 regs=sorted({h["source_reg"] for _,_,h in exact})
 L=["-- Gaia Master B52R26 CD DMA capture","gaia26_bps={}","gaia26_ev={}","gaia26_armed=false","gaia26_skip=0","local function hx(v) return string.upper(bit.tohex(tonumber(v),8)) end",
"function gaia_arm26(skip) gaia26_ev={};gaia26_skip=tonumber(skip or 0) or 0;gaia26_armed=true;print('GAIA B52R26 armed skip='..tostring(gaia26_skip)) end",
"function gaia_next26() gaia_arm26(0);PCSX.resumeEmulator() end",
"function gaia_save26(prefix) prefix=prefix or 'GaiaMaster_B52R26';local f=assert(io.open(prefix..'_CD_DMA_TRACE.tsv','wb'));f:write('seq\\tpc\\tra\\thw\\treg\\tvalue\\tfunc_start\\tscore\\n');for i,e in ipairs(gaia26_ev) do f:write(tostring(i)..'\\t'..hx(e.pc)..'\\t'..hx(e.ra)..'\\t'..e.hw..'\\t'..e.reg..'\\t'..hx(e.value)..'\\t'..hx(e.func)..'\\t'..tostring(e.score)..'\\n') end;f:close();print('saved '..prefix..'_CD_DMA_TRACE.tsv') end","local T={"]
 for score,fs,h in exact:L.append(f"{{addr=0x{h['pc']:08X},func=0x{fs:08X},score={score},hw='{h['hw_name']}',reg='{h['source_reg']}'}},")
 L+=["}","for i,t in ipairs(T) do gaia26_bps[i]=PCSX.addBreakpoint(t.addr,'Exec',4,'Gaia B52R26 '..t.hw,function() if not gaia26_armed then return end local ok,msg=pcall(function() local r=PCSX.getRegisters();local v=0;if false then v=0"]
 for rg in regs:L.append(f"elseif t.reg=='{rg}' then v=tonumber(r.GPR.n.{rg})")
 L+=["end;gaia26_ev[#gaia26_ev+1]={pc=tonumber(r.pc),ra=tonumber(r.GPR.n.ra),hw=t.hw,reg=t.reg,value=v,func=t.func,score=t.score};print('GAIA26 '..t.hw..' pc='..hx(r.pc)..' '..t.reg..'='..hx(v));if t.hw=='DMA3_CHCR' and bit.band(bit.rshift(v,24),1)==1 then if gaia26_skip>0 then gaia26_skip=gaia26_skip-1;gaia26_ev={};print('skip CD DMA; remain='..tostring(gaia26_skip)) else gaia26_armed=false;PCSX.pauseEmulator();print('paused at CD DMA start; run gaia_save26()') end end end);if not ok then print('GAIA26 error '..tostring(msg));gaia26_armed=false;PCSX.pauseEmulator() end end) end",f"print('GAIA B52R26 loaded {len(exact)} breakpoints; run gaia_arm26() before target transition')"]
 luap.write_text("\n".join(L)+"\n",encoding="utf-8")
 rpt.write_text("\n".join(["GAIA MASTER B52R26 CD DMA LOCATOR","="*78,f"Input SHA1: {sh}",f"DMA3 MMIO hits: {len(hits)}",f"Ranked routines: {len(ranked)}",f"Exact Lua breakpoints: {len(exact)}","","Goal: capture CDROM DMA3 destination setup around the same transition as the B52R24 target GPU transaction.","A CD DMA range is provenance evidence only after overlap/correlation with the proven B52R24 RAM source.","Overall Runtime PASS remains NO.",f"CSV: {csvp.name}",f"Lua: {luap.name}"])+"\n",encoding="utf-8")
 print(rpt.read_text(encoding="utf-8"));return 0
if __name__=="__main__":
 try:raise SystemExit(main())
 except SystemExit:raise
 except Exception as e:print("[ERROR]",repr(e));raise SystemExit(9)

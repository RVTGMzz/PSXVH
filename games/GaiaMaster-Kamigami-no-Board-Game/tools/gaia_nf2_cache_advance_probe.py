#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,struct
from pathlib import Path

CLEAN_SHA1="f4d5298583c90d89c4b7e51d2dde160ee07f2aec"
B52R14R1_SHA1="0ced9982e1b00566b42ace047236378826c2aa1c"
SLPS_EXTENT=24
SLPS_SIZE=487424

HIT_LO,HIT_HI=0x8003CB10,0x8003CC30
MISS_LO,MISS_HI=0x8003CC30,0x8003CDA0

REG=["zero","at","v0","v1","a0","a1","a2","a3","t0","t1","t2","t3","t4","t5","t6","t7",
     "s0","s1","s2","s3","s4","s5","s6","s7","t8","t9","k0","k1","gp","sp","fp","ra"]

MEMOPS={0x20:"lb",0x24:"lbu",0x21:"lh",0x25:"lhu",0x23:"lw",0x28:"sb",0x29:"sh",0x2B:"sw"}

def sha1_file(p):
    h=hashlib.sha1()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(8*1024*1024),b""):
            h.update(b)
    return h.hexdigest().lower()

def sha1_bytes(b):
    return hashlib.sha1(b).hexdigest()

def read_iso_file(f,extent,size):
    out=bytearray(); left=size; sec=extent
    while left:
        n=min(2048,left)
        f.seek(sec*2352+24)
        b=f.read(n)
        if len(b)!=n: raise RuntimeError("Short Form1 read at LBA %d"%sec)
        out+=b; left-=n; sec+=1
    return bytes(out)

def s16(v): return v-0x10000 if v&0x8000 else v
def u32(v): return v&0xffffffff

def fields(w):
    return ((w>>26)&0x3f,(w>>21)&31,(w>>16)&31,(w>>11)&31,(w>>6)&31,w&0x3f,w&0xffff,w&0x03ffffff)

def decode(w,pc):
    op,rs,rt,rd,sh,fn,imm,tgt=fields(w); si=s16(imm)
    if w==0:return "nop"
    if op==0:
        d={0x21:"addu",0x23:"subu",0x25:"or",0x24:"and",0x2A:"slt",0x2B:"sltu"}
        if fn in d:return "%s %s,%s,%s"%(d[fn],REG[rd],REG[rs],REG[rt])
        if fn in (0,2,3):return "%s %s,%s,%d"%({0:"sll",2:"srl",3:"sra"}[fn],REG[rd],REG[rt],sh)
        if fn==8:return "jr %s"%REG[rs]
        if fn==0x18:return "mult %s,%s"%(REG[rs],REG[rt])
        if fn==0x12:return "mflo %s"%REG[rd]
        return "SPECIAL fn=%02X"%fn
    if op==0x0f:return "lui %s,0x%04X"%(REG[rt],imm)
    if op in (0x08,0x09):return "%s %s,%s,%d"%("addi" if op==8 else "addiu",REG[rt],REG[rs],si)
    if op==0x0d:return "ori %s,%s,0x%04X"%(REG[rt],REG[rs],imm)
    if op==0x0c:return "andi %s,%s,0x%04X"%(REG[rt],REG[rs],imm)
    if op in MEMOPS:return "%s %s,%d(%s)"%(MEMOPS[op],REG[rt],si,REG[rs])
    if op in (4,5):
        dst=u32(pc+4+(si<<2))
        return "%s %s,%s,0x%08X"%("beq" if op==4 else "bne",REG[rs],REG[rt],dst)
    if op==2:return "j 0x%08X"%(((pc+4)&0xf0000000)|(tgt<<2))
    if op==3:return "jal 0x%08X"%(((pc+4)&0xf0000000)|(tgt<<2))
    return "op=%02X"%op

def write_reg(w):
    op,rs,rt,rd,sh,fn,imm,tgt=fields(w)
    if op==0:
        if fn in (0,2,3,0x21,0x23,0x24,0x25,0x2A,0x2B,0x12): return rd
        return None
    if op in (0x08,0x09,0x0C,0x0D,0x0F,0x20,0x21,0x23,0x24,0x25): return rt
    return None

def context(words,load,idx,before=14,after=14):
    out=[]
    for j in range(max(0,idx-before),min(len(words),idx+after+1)):
        pc=load+0x800+j*4
        out.append((pc,words[j],decode(words[j],pc),j==idx))
    return out

def near_features(words,idx,radius=18):
    lo=max(0,idx-radius);hi=min(len(words),idx+radius+1)
    imms=[]; ops=[]; add1=False; branches=0
    for w in words[lo:hi]:
        op,rs,rt,rd,sh,fn,imm,tgt=fields(w); imms.append(s16(imm)); ops.append(op)
        if op in (0x08,0x09) and s16(imm)==1:add1=True
        if op in (4,5,2,3):branches+=1
    return {
        "state3c":0x3C in imms,
        "state3e":0x3E in imms,
        "state40":0x40 in imms,
        "add1":add1,
        "branches":branches,
    }

def recent_defs(words,idx,reg,limit=28):
    out=[]
    cur=reg
    for j in range(idx-1,max(-1,idx-limit-1),-1):
        w=words[j]
        if write_reg(w)==cur:
            out.append(j)
            op,rs,rt,rd,sh,fn,imm,tgt=fields(w)
            if op in (0x08,0x09,0x0C,0x0D) and rs!=0:
                cur=rs
            elif op==0 and fn in (0x21,0x23,0x24,0x25):
                break
            elif op in (0x20,0x21,0x23,0x24,0x25,0x0F):
                break
            else:
                break
    return list(reversed(out))

def scan(words,load):
    rows=[]
    for i,w in enumerate(words):
        op,rs,rt,rd,sh,fn,imm,tgt=fields(w); si=s16(imm)
        if op not in MEMOPS or si!=6: continue
        pc=load+0x800+i*4
        access="WRITE" if op in (0x28,0x29,0x2B) else "READ"
        window="MISS" if MISS_LO<=pc<MISS_HI else ("HIT" if HIT_LO<=pc<HIT_HI else "OTHER")
        feat=near_features(words,i)
        score=0
        if window=="MISS":score+=100
        if window=="HIT":score+=80
        if access=="WRITE":score+=35
        if op==0x28:score+=25
        if access=="READ" and op==0x24:score+=20
        if feat["state3e"]:score+=20
        if feat["state40"]:score+=20
        if feat["state3c"]:score+=8
        if feat["add1"]:score+=8
        defs=recent_defs(words,i,rt) if access=="WRITE" else []
        rows.append({
            "idx":i,"pc":pc,"word":w,"op":MEMOPS[op],"access":access,
            "base_reg":REG[rs],"value_reg":REG[rt],"window":window,"score":score,
            "near_state3c":feat["state3c"],"near_state3e":feat["state3e"],
            "near_state40":feat["state40"],"near_add1":feat["add1"],
            "recent_defs":defs,
        })
    rows.sort(key=lambda r:(r["score"],r["access"]=="WRITE"),reverse=True)
    return rows

def reg_lua(name):
    if name=="zero":return "0"
    return "tonumber(r.GPR.n.%s)"%name

def lua_for(rows,max_targets=8):
    stores=[r for r in rows if r["access"]=="WRITE"]
    chosen=stores[:max_targets]
    L=[
"-- Auto-generated by Gaia Master NF2 cache-advance probe",
"-- READ/CAPTURE ONLY. Requires PCSX-Redux debugger + interpreter.",
"gaia_nf2_bps = gaia_nf2_bps or {}",
"gaia_nf2_events = {}",
"gaia_nf2_armed = false",
"gaia_nf2_skip = 0",
"local function h2(v) return string.upper(bit.tohex(tonumber(v),8)) end",
"",
"local function dump16(addr)",
"  local mem=PCSX.getMemPtr()",
"  local p=bit.band(tonumber(addr),0x1FFFFF)",
"  local s=ffi.string(mem+p,16)",
"  local out={}",
"  for i=1,#s do out[#out+1]=string.format('%02X',string.byte(s,i)) end",
"  return table.concat(out,'')",
"end",
"",
"function gaia_arm_nf2(skip)",
"  gaia_nf2_events={}; gaia_nf2_skip=tonumber(skip or 0) or 0; gaia_nf2_armed=true",
"  print('GAIA NF2 advance capture ARMED; reproduce target text now')",
"end",
"function gaia_disarm_nf2() gaia_nf2_armed=false; print('GAIA NF2 disarmed') end",
"function gaia_next_nf2() gaia_arm_nf2(0); PCSX.resumeEmulator() end",
"",
"function gaia_save_nf2(prefix)",
"  prefix=prefix or 'GaiaMaster_NF2'",
"  local f=assert(io.open(prefix..'_ADVANCE_TRACE.tsv','wb'))",
"  f:write('seq\tpc\tra\tbase_reg\tbase\tvalue_reg\tadvance\twindow\tscore\trecord16\ta0\ta1\ta2\ta3\n')",
"  for i,e in ipairs(gaia_nf2_events) do",
"    f:write(tostring(i)..'\t'..h2(e.pc)..'\t'..h2(e.ra)..'\t'..e.base_reg..'\t'..h2(e.base)..'\t'..e.value_reg..'\t'..tostring(e.advance)..'\t'..e.window..'\t'..tostring(e.score)..'\t'..e.record16..'\t'..h2(e.a0)..'\t'..h2(e.a1)..'\t'..h2(e.a2)..'\t'..h2(e.a3)..'\n')",
"  end",
"  f:close()",
"  print('Saved '..prefix..'_ADVANCE_TRACE.tsv')",
"end",
"",
"local targets={"
]
    for r in chosen:
        L.append("  {pc=0x%08X, base_reg='%s', value_reg='%s', window='%s', score=%d},"%
                 (r["pc"],r["base_reg"],r["value_reg"],r["window"],r["score"]))
    L += ["}","",
"for i,t in ipairs(targets) do",
"  gaia_nf2_bps[i]=PCSX.addBreakpoint(t.pc,'Exec',4,'Gaia NF2 cache advance writer',function()",
"    if not gaia_nf2_armed then return end",
"    local ok,msg=pcall(function()",
"      local r=PCSX.getRegisters()",
"      local base=0; local value=0",
]
    regs=sorted({r["base_reg"] for r in chosen}|{r["value_reg"] for r in chosen})
    for reg in regs:
        expr=reg_lua(reg)
        L.append("      if t.base_reg == '%s' then base=%s end"%(reg,expr))
        L.append("      if t.value_reg == '%s' then value=%s end"%(reg,expr))
    L += [
"      if gaia_nf2_skip > 0 then gaia_nf2_skip=gaia_nf2_skip-1; return end",
"      local e={pc=tonumber(r.pc),ra=tonumber(r.GPR.n.ra),base_reg=t.base_reg,base=base,value_reg=t.value_reg,advance=bit.band(value,0xFF),window=t.window,score=t.score,record16=dump16(base),a0=tonumber(r.GPR.n.a0),a1=tonumber(r.GPR.n.a1),a2=tonumber(r.GPR.n.a2),a3=tonumber(r.GPR.n.a3)}",
"      gaia_nf2_events[#gaia_nf2_events+1]=e",
"      print('GAIA_NF2 pc='..h2(e.pc)..' advance='..tostring(e.advance)..' base='..h2(e.base)..' rec='..e.record16)",
"      gaia_nf2_armed=false; PCSX.pauseEmulator()",
"      print('Paused before cache_record+6 write. Run gaia_save_nf2(); gaia_next_nf2() catches the next writer.')",
"    end)",
"    if not ok then print('GAIA NF2 callback error: '..tostring(msg)); gaia_nf2_armed=false; PCSX.pauseEmulator() end",
"  end)",
"end",
"print(string.format('GAIA NF2 loaded %d candidate cache-advance writer breakpoint(s). Run gaia_arm_nf2() before target text.',#targets))",
]
    return "\n".join(L)+"\n",chosen

def selftest():
    # Synthetic MIPS window: lhu t0,0x40(s1); addiu t0,t0,1; sb t0,6(s2)
    words=[0]*40
    words[15]=(0x25<<26)|(17<<21)|(8<<16)|0x40
    words[16]=(0x09<<26)|(8<<21)|(8<<16)|1
    words[17]=(0x28<<26)|(18<<21)|(8<<16)|6
    rows=scan(words,0x8003C000)
    assert rows and rows[0]["access"]=="WRITE"
    assert rows[0]["base_reg"]=="s2" and rows[0]["value_reg"]=="t0"
    assert rows[0]["near_state40"] and rows[0]["near_add1"]
    lua,chosen=lua_for(rows)
    assert chosen and "gaia_arm_nf2" in lua and "cache advance writer" in lua
    print("NF2 CACHE ADVANCE PROBE SELFTEST PASS")

def main():
    ap=argparse.ArgumentParser(description="Gaia Master NF2 read-only cache advance writer probe")
    ap.add_argument("bin",nargs="?",type=Path)
    ap.add_argument("--selftest",action="store_true")
    a=ap.parse_args()
    if a.selftest:
        selftest();return 0
    if not a.bin:ap.error("exact CLEAN or B52R14R1 BIN required")
    src=a.bin.expanduser().resolve()
    if not src.is_file():raise RuntimeError("BIN not found: %s"%src)
    sh=sha1_file(src)
    if sh==CLEAN_SHA1:base="CLEAN"
    elif sh==B52R14R1_SHA1:base="B52R14R1"
    else:raise RuntimeError("Unexpected BIN SHA1 %s"%sh)
    with src.open("rb") as f:slps=read_iso_file(f,SLPS_EXTENT,SLPS_SIZE)
    if slps[:8]!=b"PS-X EXE":raise RuntimeError("SLPS is not PS-X EXE")
    pc0,gp0,taddr,tsize=struct.unpack_from("<IIII",slps,0x10)
    load=u32(taddr-0x800)
    code=slps[0x800:min(len(slps),0x800+tsize)]
    code=code[:len(code)&~3]
    words=list(struct.unpack("<%dI"%(len(code)//4),code))
    rows=scan(words,load)

    out=src.parent
    csvp=out/"GaiaMaster_NF2_CACHE_ADVANCE_CANDIDATES.csv"
    rpt=out/"GaiaMaster_NF2_CACHE_ADVANCE_REPORT.txt"
    luap=out/"GaiaMaster_NF2_PCSX_ADVANCE_CAPTURE.lua"

    with csvp.open("w",encoding="utf-8-sig",newline="") as f:
        fields_out=["rank","pc","word","op","access","base_reg","value_reg","window","score","near_state3c","near_state3e","near_state40","near_add1","recent_def_pcs"]
        w=csv.DictWriter(f,fieldnames=fields_out);w.writeheader()
        for rank,r in enumerate(rows,1):
            w.writerow({
                "rank":rank,"pc":"0x%08X"%r["pc"],"word":"0x%08X"%r["word"],"op":r["op"],"access":r["access"],
                "base_reg":r["base_reg"],"value_reg":r["value_reg"],"window":r["window"],"score":r["score"],
                "near_state3c":int(r["near_state3c"]),"near_state3e":int(r["near_state3e"]),"near_state40":int(r["near_state40"]),
                "near_add1":int(r["near_add1"]),
                "recent_def_pcs":";".join("0x%08X"%(load+0x800+j*4) for j in r["recent_defs"])
            })

    lua,chosen=lua_for(rows)
    luap.write_text(lua,encoding="utf-8")

    L=["GAIA MASTER NF2 CACHE ADVANCE PROBE","="*88,
       "READ ONLY / NO ROM PATCH","",
       "Input: %s"%src.name,"Base: %s"%base,"BIN SHA1: %s"%sh,"SLPS SHA1: %s"%sha1_bytes(slps),
       "PS-X EXE load base: 0x%08X"%load,"",
       "Known renderer spacing model:",
       "- cache hit: advance = cache_record.byte6",
       "- cache miss: advance = state+0x3E OR state+0x40 + 1",
       "- optional tracking: state+0x3C","",
       "OFFSET +6 MEMORY XREFS: %d"%len(rows)]
    if not rows:
        L += ["[STOP] No direct memory op with immediate +6 found.","Do not infer a writer. Inspect packed/block-copy ownership next."]
    else:
        for rank,r in enumerate(rows[:16],1):
            L += ["","[%02d] score=%d %s %s window=%s"%(rank,r["score"],r["access"],r["op"],r["window"]),
                  "pc=0x%08X word=0x%08X base=%s value=%s"%(r["pc"],r["word"],r["base_reg"],r["value_reg"]),
                  "near: state+3C=%s state+3E=%s state+40=%s addiu+1=%s"%(r["near_state3c"],r["near_state3e"],r["near_state40"],r["near_add1"])]
            if r["recent_defs"]:
                L.append("recent value-reg defs: "+", ".join("0x%08X"%(load+0x800+j*4) for j in r["recent_defs"]))
            L.append("context:")
            for pc,w,d,mark in context(words,load,r["idx"],10,12):
                L.append("  0x%08X %08X  %-42s%s"%(pc,w,d,"  <<<" if mark else ""))
    L += ["","RUNTIME CAPTURE:",
          "- Lua generated from the top direct +6 WRITE candidates.",
          "- Arm immediately before a known text line.",
          "- Breakpoint fires BEFORE the store, so source register still contains the proposed advance.",
          "- record16 is captured before byte6 is overwritten.",
          "- Repeat with gaia_next_nf2() to collect several glyph writes.","",
          "PROMOTION GATE:",
          "- Do not patch cursor/cache stride from this static report.",
          "- A viable NF2 hook requires a runtime-correlated cache-record+6 writer and stable source-width register.",
          "- Preferred future patch is local width-source substitution before cache write, not global stride mutation.",
          "- Overall Runtime PASS remains NO.",
          "CSV: %s"%csvp.name,"Lua: %s"%luap.name]
    rpt.write_text("\n".join(L)+"\n",encoding="utf-8")
    print("\n".join(L[:18]))
    print("Report:",rpt)
    print("CSV:",csvp)
    print("Lua:",luap)
    print("Breakpoints:",len(chosen))
    return 0

if __name__=="__main__":
    try:raise SystemExit(main())
    except SystemExit:raise
    except Exception as e:
        print("[ERROR]",repr(e));raise SystemExit(9)

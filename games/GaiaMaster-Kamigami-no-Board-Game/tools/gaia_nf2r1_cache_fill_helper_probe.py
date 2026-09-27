#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,struct
from pathlib import Path

CLEAN_SHA1="f4d5298583c90d89c4b7e51d2dde160ee07f2aec"
B52R14R1_SHA1="0ced9982e1b00566b42ace047236378826c2aa1c"
SLPS_EXTENT=24
SLPS_SIZE=487424

HELPER=0x8003C67C
CALL_PC=0x8003CC38
RETURN_PC=0x8003CC40
CALLER_PRE_LO=0x8003CC20
CALLER_POST_HI=0x8003CD90
HELPER_LO=0x8003C5F0
HELPER_HI=0x8003C760

REG=["zero","at","v0","v1","a0","a1","a2","a3","t0","t1","t2","t3","t4","t5","t6","t7",
     "s0","s1","s2","s3","s4","s5","s6","s7","t8","t9","k0","k1","gp","sp","fp","ra"]
MEM={0x20:"lb",0x24:"lbu",0x21:"lh",0x25:"lhu",0x23:"lw",0x28:"sb",0x29:"sh",0x2B:"sw"}

def sha1_file(p):
    h=hashlib.sha1()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(8*1024*1024),b""): h.update(b)
    return h.hexdigest().lower()

def sha1_bytes(b): return hashlib.sha1(b).hexdigest()

def read_iso_file(f,extent,size):
    out=bytearray();left=size;lba=extent
    while left:
        n=min(2048,left);f.seek(lba*2352+24);b=f.read(n)
        if len(b)!=n:raise RuntimeError("Short Form1 read at LBA %d"%lba)
        out+=b;left-=n;lba+=1
    return bytes(out)

def s16(v):return v-0x10000 if v&0x8000 else v
def u32(v):return v&0xffffffff
def fld(w):return ((w>>26)&0x3f,(w>>21)&31,(w>>16)&31,(w>>11)&31,(w>>6)&31,w&0x3f,w&0xffff,w&0x03ffffff)

def dec(w,pc):
    op,rs,rt,rd,sh,fn,imm,tgt=fld(w);si=s16(imm)
    if w==0:return "nop"
    if op==0:
        d={0x21:"addu",0x23:"subu",0x25:"or",0x24:"and",0x2A:"slt",0x2B:"sltu"}
        if fn in d:return "%s %s,%s,%s"%(d[fn],REG[rd],REG[rs],REG[rt])
        if fn in (0,2,3):return "%s %s,%s,%d"%({0:"sll",2:"srl",3:"sra"}[fn],REG[rd],REG[rt],sh)
        if fn==8:return "jr %s"%REG[rs]
        if fn==9:return "jalr %s,%s"%(REG[rd],REG[rs])
        if fn==0x12:return "mflo %s"%REG[rd]
        return "SPECIAL fn=%02X"%fn
    if op==0x0f:return "lui %s,0x%04X"%(REG[rt],imm)
    if op in (8,9):return "%s %s,%s,%d"%("addi" if op==8 else "addiu",REG[rt],REG[rs],si)
    if op==0x0c:return "andi %s,%s,0x%04X"%(REG[rt],REG[rs],imm)
    if op==0x0d:return "ori %s,%s,0x%04X"%(REG[rt],REG[rs],imm)
    if op in MEM:return "%s %s,%d(%s)"%(MEM[op],REG[rt],si,REG[rs])
    if op in (4,5):
        return "%s %s,%s,0x%08X"%("beq" if op==4 else "bne",REG[rs],REG[rt],u32(pc+4+(si<<2)))
    if op==2:return "j 0x%08X"%(((pc+4)&0xf0000000)|(tgt<<2))
    if op==3:return "jal 0x%08X"%(((pc+4)&0xf0000000)|(tgt<<2))
    return "op=%02X"%op

def word_at(slps,load,pc):
    off=pc-load
    if off<0 or off+4>len(slps):raise RuntimeError("PC outside SLPS: 0x%08X"%pc)
    return struct.unpack_from("<I",slps,off)[0]

def dump(slps,load,lo,hi):
    out=[]
    for pc in range(lo,hi,4):
        try:w=word_at(slps,load,pc)
        except RuntimeError:break
        out.append("0x%08X  %08X  %s"%(pc,w,dec(w,pc)))
    return out

def jal_target(w,pc):
    op,rs,rt,rd,sh,fn,imm,tgt=fld(w)
    if op!=3:return None
    return ((pc+4)&0xf0000000)|(tgt<<2)

def lua_text():
    return r'''-- Gaia Master NF2R1 Cache Fill Helper Probe
-- Generated for exact verified Gaia SLPS layout.
-- Requires PCSX-Redux debugger + interpreter.

gaia_nf2r1_bps = gaia_nf2r1_bps or {}
gaia_nf2r1_events = {}
gaia_nf2r1_armed = false
gaia_nf2r1_pending = nil
gaia_nf2r1_skip = 0

local HELPER = 0x8003C67C
local RETURN_PC = 0x8003CC40
local EXPECTED_RA = RETURN_PC

local function h(v) return string.upper(bit.tohex(tonumber(v),8)) end
local function mem8(addr)
  local mem=PCSX.getMemPtr()
  return tonumber(ffi.cast('uint8_t*',mem)[bit.band(tonumber(addr),0x1FFFFF)])
end
local function mem16(addr)
  local lo=mem8(addr); local hi=mem8(addr+1)
  return lo + hi*256
end
local function mem32(addr)
  return mem16(addr) + mem16(addr+2)*65536
end
local function dump16(addr)
  local mem=PCSX.getMemPtr()
  local p=bit.band(tonumber(addr),0x1FFFFF)
  local s=ffi.string(mem+p,16)
  local out={}
  for i=1,#s do out[#out+1]=string.format('%02X',string.byte(s,i)) end
  return table.concat(out,'')
end
local function snap_regs(r)
  return {
    pc=tonumber(r.pc), ra=tonumber(r.GPR.n.ra), sp=tonumber(r.GPR.n.sp),
    v0=tonumber(r.GPR.n.v0), v1=tonumber(r.GPR.n.v1),
    a0=tonumber(r.GPR.n.a0), a1=tonumber(r.GPR.n.a1),
    a2=tonumber(r.GPR.n.a2), a3=tonumber(r.GPR.n.a3),
    t0=tonumber(r.GPR.n.t0), t1=tonumber(r.GPR.n.t1),
    t2=tonumber(r.GPR.n.t2), t3=tonumber(r.GPR.n.t3),
    s0=tonumber(r.GPR.n.s0), s1=tonumber(r.GPR.n.s1),
    s2=tonumber(r.GPR.n.s2), s3=tonumber(r.GPR.n.s3),
    s4=tonumber(r.GPR.n.s4), s5=tonumber(r.GPR.n.s5),
    s6=tonumber(r.GPR.n.s6), s7=tonumber(r.GPR.n.s7),
  }
end
local function state_fields(state)
  return {
    track=mem16(state+0x3C),
    special=mem16(state+0x3E),
    normal=mem16(state+0x40),
    glyph_count=mem16(state+0x44),
    cache_base=mem32(state+0x54),
    cache_current=mem32(state+0x60),
    cache_write=mem32(state+0x64),
    cursor_x=mem16(state+0x18),
  }
end

function gaia_arm_nf2r1(skip)
  gaia_nf2r1_events={}
  gaia_nf2r1_pending=nil
  gaia_nf2r1_skip=tonumber(skip or 0) or 0
  gaia_nf2r1_armed=true
  print('GAIA NF2R1 armed. Show/re-enter a target text line now.')
end

function gaia_disarm_nf2r1()
  gaia_nf2r1_armed=false
  gaia_nf2r1_pending=nil
  print('GAIA NF2R1 disarmed')
end

function gaia_next_nf2r1()
  gaia_arm_nf2r1(0)
  PCSX.resumeEmulator()
end

function gaia_save_nf2r1(prefix)
  prefix=prefix or 'GaiaMaster_NF2R1'
  local f=assert(io.open(prefix..'_CACHE_FILL_TRACE.tsv','wb'))
  f:write('seq\tstate\trecord\tpre16\tpost16\tpre_byte6\tpost_byte6\treturn_v0\ttrack\tspecial\tnormal\tcursor_pre\tcursor_post\tglyph_count\ta1\ta3\ts0\ts2\ts3\ts4\ts5\n')
  for i,e in ipairs(gaia_nf2r1_events) do
    f:write(
      tostring(i)..'\t'..h(e.state)..'\t'..h(e.record)..'\t'..e.pre16..'\t'..e.post16..
      '\t'..tostring(e.pre_byte6)..'\t'..tostring(e.post_byte6)..'\t'..tostring(e.return_v0)..
      '\t'..tostring(e.track)..'\t'..tostring(e.special)..'\t'..tostring(e.normal)..
      '\t'..tostring(e.cursor_pre)..'\t'..tostring(e.cursor_post)..'\t'..tostring(e.glyph_count)..
      '\t'..h(e.a1)..'\t'..h(e.a3)..'\t'..h(e.s0)..'\t'..h(e.s2)..'\t'..h(e.s3)..'\t'..h(e.s4)..'\t'..h(e.s5)..'\n'
    )
  end
  f:close()
  print('Saved '..prefix..'_CACHE_FILL_TRACE.tsv')
end

gaia_nf2r1_bps.entry = PCSX.addBreakpoint(HELPER,'Exec',4,'Gaia NF2R1 cache-fill helper entry',function()
  if not gaia_nf2r1_armed then return end
  local ok,msg=pcall(function()
    local r=PCSX.getRegisters()
    if tonumber(r.GPR.n.ra) ~= EXPECTED_RA then return end
    if gaia_nf2r1_skip > 0 then
      gaia_nf2r1_skip=gaia_nf2r1_skip-1
      return
    end
    local rr=snap_regs(r)
    local st=state_fields(rr.a0)
    gaia_nf2r1_pending={
      regs=rr,
      state=rr.a0,
      record=rr.a2,
      pre16=dump16(rr.a2),
      pre_byte6=mem8(rr.a2+6),
      track=st.track,
      special=st.special,
      normal=st.normal,
      glyph_count=st.glyph_count,
      cursor_pre=st.cursor_x,
    }
    print('NF2R1 ENTRY state='..h(rr.a0)..' record='..h(rr.a2)..' pre6='..tostring(gaia_nf2r1_pending.pre_byte6)..' track='..tostring(st.track)..' special='..tostring(st.special)..' normal='..tostring(st.normal))
  end)
  if not ok then
    print('NF2R1 entry error: '..tostring(msg))
    gaia_nf2r1_armed=false
    PCSX.pauseEmulator()
  end
end)

gaia_nf2r1_bps.ret = PCSX.addBreakpoint(RETURN_PC,'Exec',4,'Gaia NF2R1 cache-fill helper return',function()
  if not gaia_nf2r1_armed or gaia_nf2r1_pending==nil then return end
  local ok,msg=pcall(function()
    local r=PCSX.getRegisters()
    local p=gaia_nf2r1_pending
    local st=state_fields(p.state)
    local e={
      state=p.state, record=p.record, pre16=p.pre16, post16=dump16(p.record),
      pre_byte6=p.pre_byte6, post_byte6=mem8(p.record+6),
      return_v0=bit.band(tonumber(r.GPR.n.v0),0xFFFFFFFF),
      track=p.track, special=p.special, normal=p.normal,
      cursor_pre=p.cursor_pre, cursor_post=st.cursor_x, glyph_count=p.glyph_count,
      a1=p.regs.a1, a3=p.regs.a3, s0=p.regs.s0, s2=p.regs.s2,
      s3=p.regs.s3, s4=p.regs.s4, s5=p.regs.s5,
    }
    gaia_nf2r1_events[#gaia_nf2r1_events+1]=e
    gaia_nf2r1_pending=nil
    gaia_nf2r1_armed=false
    print('NF2R1 RETURN v0='..tostring(e.return_v0)..' post6='..tostring(e.post_byte6)..' record='..h(e.record))
    print('Paused after one cache-fill event. Run gaia_save_nf2r1(); gaia_next_nf2r1() for another glyph.')
    PCSX.pauseEmulator()
  end)
  if not ok then
    print('NF2R1 return error: '..tostring(msg))
    gaia_nf2r1_pending=nil
    gaia_nf2r1_armed=false
    PCSX.pauseEmulator()
  end
end)

print('GAIA NF2R1 loaded. Run gaia_arm_nf2r1() before a target text line.')
'''

def selftest():
    # JAL encoding check for known caller/helper relationship.
    pc=CALL_PC
    tgt=(HELPER>>2)&0x03ffffff
    w=(3<<26)|tgt
    assert jal_target(w,pc)==HELPER
    assert RETURN_PC==CALL_PC+8
    print("NF2R1 CACHE FILL HELPER PROBE SELFTEST PASS")

def main():
    ap=argparse.ArgumentParser(description="Gaia Master NF2R1 cache-fill helper proof generator")
    ap.add_argument("bin",nargs="?",type=Path)
    ap.add_argument("--selftest",action="store_true")
    a=ap.parse_args()
    if a.selftest:selftest();return 0
    if not a.bin:ap.error("exact CLEAN or B52R14R1 BIN required")
    src=a.bin.expanduser().resolve()
    if not src.is_file():raise RuntimeError("BIN not found: %s"%src)
    sh=sha1_file(src)
    if sh==CLEAN_SHA1:base="CLEAN"
    elif sh==B52R14R1_SHA1:base="B52R14R1"
    else:raise RuntimeError("Unexpected BIN SHA1 %s"%sh)
    with src.open("rb") as f:slps=read_iso_file(f,SLPS_EXTENT,SLPS_SIZE)
    if slps[:8]!=b"PS-X EXE":raise RuntimeError("SLPS is not PS-X EXE")
    _,_,taddr,_=struct.unpack_from("<IIII",slps,0x10)
    load=u32(taddr-0x800)

    w_call=word_at(slps,load,CALL_PC)
    got=jal_target(w_call,CALL_PC)
    if got!=HELPER:
        raise RuntimeError("Expected jal 0x%08X at 0x%08X, got %s (%08X)"%(HELPER,CALL_PC,("0x%08X"%got) if got is not None else "non-jal",w_call))
    w_pre0=word_at(slps,load,0x8003CC30)
    w_pre1=word_at(slps,load,0x8003CC34)
    # addu a0,s1,zero = 0x02202021 ; lw a2,100(s1) = 0x8E260064
    if w_pre0!=0x02202021 or w_pre1!=0x8E260064:
        raise RuntimeError("Caller prelude contract drift: %08X %08X"%(w_pre0,w_pre1))

    out=src.parent
    rpt=out/"GaiaMaster_NF2R1_CACHE_FILL_HELPER_REPORT.txt"
    lua=out/"GaiaMaster_NF2R1_PCSX_CACHE_FILL_CAPTURE.lua"

    L=["GAIA MASTER NF2R1 CACHE FILL HELPER PROBE","="*88,
       "READ ONLY / NO ROM PATCH","",
       "Input: %s"%src.name,"Base: %s"%base,"BIN SHA1: %s"%sh,
       "SLPS SHA1: %s"%sha1_bytes(slps),"Load base: 0x%08X"%load,"",
       "CALLSITE CONTRACT:",
       "0x8003CC30 = addu a0,s1,zero     -> state pointer",
       "0x8003CC34 = lw a2,100(s1)       -> state+0x64 cache_write pointer",
       "0x8003CC38 = jal 0x8003C67C      -> cache-fill/copy helper",
       "0x8003CC40 = helper return site","",
       "CALLER WINDOW:"]
    L += dump(slps,load,CALLER_PRE_LO,CALLER_POST_HI)
    L += ["","HELPER WINDOW:"]
    L += dump(slps,load,HELPER_LO,HELPER_HI)
    L += ["","RUNTIME PLAN:",
          "- Break only on helper entry when RA == 0x8003CC40.",
          "- Capture state=a0 and destination cache record=a2 before helper writes.",
          "- At 0x8003CC40 capture return v0 and the same 16-byte record after helper.",
          "- Compare record byte6 before/after and correlate with state+3C/3E/40.",
          "- Repeat a few glyphs with gaia_next_nf2r1().","",
          "PROMOTION GATE:",
          "- Do not patch VWF yet.",
          "- If post byte6 equals the computed advance and changes per glyph, NF2 width injection should target this helper/caller path.",
          "- If byte6 is unchanged here, follow the later cache-record writer instead.",
          "- Overall Runtime PASS remains NO."]
    rpt.write_text("\n".join(L)+"\n",encoding="utf-8")
    lua.write_text(lua_text(),encoding="utf-8")
    print("[OK] NF2R1 helper contract verified")
    print("Report:",rpt)
    print("Lua:",lua)
    return 0

if __name__=="__main__":
    try:raise SystemExit(main())
    except SystemExit:raise
    except Exception as e:
        print("[ERROR]",repr(e));raise SystemExit(9)

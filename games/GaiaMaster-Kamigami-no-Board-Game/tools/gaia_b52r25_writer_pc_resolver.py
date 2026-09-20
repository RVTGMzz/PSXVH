#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,struct
from pathlib import Path

CLEAN='f4d5298583c90d89c4b7e51d2dde160ee07f2aec'
BASE='0ced9982e1b00566b42ace047236378826c2aa1c'
RAW,USER=2352,2048
SLPS_EXTENT,SLPS_SIZE=24,487424
HDR=0x800
REG='r0 at v0 v1 a0 a1 a2 a3 t0 t1 t2 t3 t4 t5 t6 t7 s0 s1 s2 s3 s4 s5 s6 s7 t8 t9 k0 k1 gp sp s8 ra'.split()

def sha1(p):
    h=hashlib.sha1()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest().lower()

def read_slps(p):
    out=bytearray(); left=SLPS_SIZE; lba=SLPS_EXTENT
    with p.open('rb') as f:
        while left:
            f.seek(lba*RAW); s=f.read(RAW)
            if len(s)!=RAW or s[15]!=2 or (s[18]&0x20) or s[16:20]!=s[20:24]:raise RuntimeError(f'Bad MODE2/Form1 sector {lba}')
            n=min(USER,left); out+=s[24:24+n]; left-=n; lba+=1
    return bytes(out)

def sx(v):return v-0x10000 if v&0x8000 else v
def op(w):return (w>>26)&63
def rs(w):return (w>>21)&31
def rt(w):return (w>>16)&31
def im(w):return w&0xffff

def dis(pc,w):
    o=op(w)
    if w==0:return 'nop'
    if o==15:return f'lui {REG[rt(w)]},0x{im(w):04X}'
    if o==13:return f'ori {REG[rt(w)]},{REG[rs(w)]},0x{im(w):04X}'
    if o==9:return f'addiu {REG[rt(w)]},{REG[rs(w)]},{sx(im(w))}'
    if o in (4,5):
        target=(pc+4+(sx(im(w))<<2))&0xffffffff
        return f"{'beq' if o==4 else 'bne'} {REG[rs(w)]},{REG[rt(w)]},0x{target:08X}"
    mm={0x23:'lw',0x2b:'sw',0x20:'lb',0x24:'lbu',0x21:'lh',0x25:'lhu',0x28:'sb',0x29:'sh'}
    if o in mm:return f'{mm[o]} {REG[rt(w)]},{sx(im(w))}({REG[rs(w)]})'
    if o==2:return f'j 0x{(((pc+4)&0xf0000000)|((w&0x3ffffff)<<2)):08X}'
    if o==3:return f'jal 0x{(((pc+4)&0xf0000000)|((w&0x3ffffff)<<2)):08X}'
    if o==0 and (w&63)==8:return f'jr {REG[rs(w)]}'
    return f'word 0x{w:08X}'

def func_start(words,addr,pc):
    i=(pc-addr)//4
    for j in range(i,max(-1,i-128),-1):
        w=words[j]
        if op(w)==9 and rs(w)==29 and rt(w)==29 and sx(im(w))<0:return addr+j*4
        if j<i-4 and op(w)==0 and (w&63)==8 and rs(w)==31:break
    return pc&~0xf

def load_trace(p):
    out=[]
    with p.open('r',encoding='utf-8-sig',newline='') as f:
        for r in csv.DictReader(f,delimiter='\t'):
            for k in ('address','pc','ra','sp','a0','a1','a2','a3'):r[k+'_i']=int(r[k],16)
            out.append(r)
    return out

def selftest():
    addr=0x80010000
    words=[0x27bdffe0,0xafbf001c,0x00000000,0x03e00008,0]
    assert func_start(words,addr,addr+8)==addr
    assert dis(addr,words[0])=='addiu sp,sp,-32'
    print('B52R25 WRITER PC RESOLVER SELFTEST PASS')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('trace',nargs='?',type=Path); ap.add_argument('bin',nargs='?',type=Path); ap.add_argument('--selftest',action='store_true'); a=ap.parse_args()
    if a.selftest:selftest();return 0
    if not a.trace or not a.bin:ap.error('WRITER_TRACE.tsv and exact B52R14R1/CLEAN BIN required')
    if a.trace.suffix.lower()=='.bin' and a.bin.suffix.lower()!='.bin': a.trace,a.bin=a.bin,a.trace
    sh=sha1(a.bin)
    if sh not in (BASE,CLEAN):raise RuntimeError(f'Unknown BIN SHA1 {sh}')
    slps=read_slps(a.bin)
    if not slps.startswith(b'PS-X EXE'):raise RuntimeError('SLPS_020.75 is not PS-X EXE')
    entry,gp,taddr,tsize=struct.unpack_from('<IIII',slps,0x10)
    if tsize<=0 or HDR+tsize>len(slps):tsize=len(slps)-HDR
    text=slps[HDR:HDR+tsize]; words=[struct.unpack_from('<I',text,i)[0] for i in range(0,len(text)-3,4)]
    callers={}
    for i,w in enumerate(words):
        if op(w)==3:
            pc=taddr+i*4; target=((pc+4)&0xf0000000)|((w&0x3ffffff)<<2); callers.setdefault(target,[]).append(pc)
    ev=load_trace(a.trace); lines=['GAIA MASTER B52R25 WRITER PC RESOLVE','='*78,f'BIN SHA1 : {sh}',f'Text RAM : 0x{taddr:08X}..0x{taddr+tsize:08X}',f'Events   : {len(ev)}','']
    for n,e in enumerate(ev,1):
        pc=e['pc_i']; lines += [f'[{n}] writer PC=0x{pc:08X} RA=0x{e["ra_i"]:08X} address=0x{e["address_i"]:08X} width={e["width"]} cause={e["cause"]}']
        if taddr<=pc<taddr+tsize:
            off=HDR+(pc-taddr); fs=func_start(words,taddr,pc); ci=callers.get(fs,[])
            lines += [f'    SLPS file offset : 0x{off:X}',f'    function start   : 0x{fs:08X}',f'    direct JAL callers: {", ".join(f"0x{x:08X}" for x in ci[:24]) or "none found"}', '    context:']
            idx=(pc-taddr)//4
            for j in range(max(0,idx-12),min(len(words),idx+13)):
                p2=taddr+j*4; mark='>>' if p2==pc else '  '; lines.append(f'    {mark} 0x{p2:08X}  {words[j]:08X}  {dis(p2,words[j])}')
        elif 0xBFC00000<=pc<0xBFC80000:
            lines.append('    classification: BIOS ROM code')
        elif 0x80000000<=pc<0x80200000 or 0xA0000000<=pc<0xA0200000:
            lines.append('    classification: RAM code outside main SLPS text, likely overlay/runtime-loaded code')
        else:
            lines.append('    classification: outside known SLPS/BIOS ranges')
        lines.append('')
    lines += ['INTERPRETATION:','- A main-SLPS writer PC gives a concrete code site to inspect for decompression/rasterization/load ownership.','- A RAM-code writer outside the main EXE suggests an overlay or dynamically loaded module and needs overlay ownership mapping.','- A writer hit proves code wrote the watched DMA-source buffer, not yet which disc bytes own the content.','- Overall Runtime PASS remains NO.']
    out=a.trace.with_name('GaiaMaster_B52R25_WRITER_RESOLVE.txt'); out.write_text('\n'.join(lines)+'\n',encoding='utf-8'); print('\n'.join(lines)); print('Report:',out)
    return 0
if __name__=='__main__':raise SystemExit(main())

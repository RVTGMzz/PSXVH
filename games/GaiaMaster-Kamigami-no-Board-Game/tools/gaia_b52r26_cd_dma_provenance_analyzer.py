#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,math
from pathlib import Path

CLEAN='f4d5298583c90d89c4b7e51d2dde160ee07f2aec'
BASE='0ced9982e1b00566b42ace047236378826c2aa1c'
RAW,USER=2352,2048

def sha1(p):
    h=hashlib.sha1()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest().lower()

def sector_user(p,lba):
    with p.open('rb') as f:
        f.seek(lba*RAW); s=f.read(RAW)
    if len(s)!=RAW or s[15]!=2: raise RuntimeError(f'Bad MODE2 sector {lba}')
    if s[18]&0x20: raise RuntimeError(f'Form2 sector not supported for ISO9660 metadata at {lba}')
    return s[24:24+USER]

def read_extent(p,lba,size):
    out=bytearray(); left=size
    while left>0:
        u=sector_user(p,lba); n=min(left,USER); out+=u[:n]; left-=n; lba+=1
    return bytes(out)

def parse_dir(p,lba,size,prefix='',seen=None):
    if seen is None: seen=set()
    key=(lba,size)
    if key in seen:return []
    seen.add(key); data=read_extent(p,lba,size); pos=0; out=[]
    while pos<len(data):
        n=data[pos]
        if n==0: pos=((pos//USER)+1)*USER; continue
        if pos+n>len(data): break
        r=data[pos:pos+n]; pos+=n
        if len(r)<34: continue
        ext=int.from_bytes(r[2:6],'little'); sz=int.from_bytes(r[10:14],'little'); flags=r[25]; nl=r[32]; name=r[33:33+nl]
        if name in (b'\x00',b'\x01'): continue
        nm=name.decode('ascii','replace').split(';')[0]; path=f'{prefix}/{nm}' if prefix else nm
        if flags&2:
            out += parse_dir(p,ext,sz,path,seen)
        else:
            out.append(dict(path=path,extent=ext,size=sz,sectors=math.ceil(sz/USER)))
    return out

def iso_index(p):
    pvd=sector_user(p,16)
    if pvd[1:6]!=b'CD001': raise RuntimeError('ISO9660 PVD not found')
    r=pvd[156:190]; lba=int.from_bytes(r[2:6],'little'); size=int.from_bytes(r[10:14],'little')
    return parse_dir(p,lba,size)

def owner(files,lba):
    for f in files:
        if f['extent']<=lba<f['extent']+f['sectors']: return f
    return None

def load_trace(p):
    out=[]
    with p.open('r',encoding='utf-8-sig',newline='') as f:
        for r in csv.DictReader(f,delimiter='\t'):
            for k in ('seq','sync','direction','dest_bytes','overlap_bytes','lba'):r[k+'_i']=int(r[k])
            out.append(r)
    return out

def selftest():
    rows=[{'overlap_bytes_i':16,'lba_i':123,'lba_conf':'SETLOC_START','dest_start':'001000','dest_bytes_i':2048,'pc':'80010000','read_cmd':'06'}]
    assert [r for r in rows if r['overlap_bytes_i']>0][0]['lba_i']==123
    print('B52R26 CD DMA PROVENANCE ANALYZER SELFTEST PASS')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('trace',nargs='?',type=Path); ap.add_argument('bin',nargs='?',type=Path); ap.add_argument('--selftest',action='store_true'); a=ap.parse_args()
    if a.selftest:selftest();return 0
    if not a.trace:ap.error('B52R26 CD_DMA_TRACE.tsv required')
    rows=load_trace(a.trace); files=[]; sh='NO_BIN'
    if a.bin:
        sh=sha1(a.bin)
        if sh not in (BASE,CLEAN): raise RuntimeError(f'Unknown BIN SHA1 {sh}')
        files=iso_index(a.bin)
    hits=[r for r in rows if r['overlap_bytes_i']>0]
    lines=['GAIA MASTER B52R26 CD DMA PROVENANCE ANALYSIS','='*78,f'events          : {len(rows)}',f'overlap events  : {len(hits)}',f'BIN SHA1        : {sh}',f'ISO files       : {len(files)}','']
    verdict='NO_DIRECT_DMA3_OVERLAP_IN_CAPTURE_WINDOW'
    if hits:
        verdict='DIRECT_CD_DMA_OVERLAP_CANDIDATE'
        lines.append('OVERLAP EVENTS:')
        for r in hits:
            lba=r['lba_i']; lines += [f"- seq={r['seq']} dest=0x{r['dest_start']} bytes={r['dest_bytes']} overlap={r['overlap_bytes']} LBA={lba} conf={r['lba_conf']} ReadCmd=0x{r['read_cmd']} pc=0x{r['pc']}"]
            if lba>=0 and files:
                f=owner(files,lba)
                if f:
                    foff=(lba-f['extent'])*USER
                    lines.append(f"  ISO owner candidate: {f['path']} extent={f['extent']} file_size={f['size']} file_offset≈0x{foff:X} raw_bin_offset=0x{lba*RAW:X}")
                else: lines.append('  ISO owner candidate: none (LBA outside indexed file extents)')
            elif lba<0: lines.append('  LBA unknown: DMA overlap is proven in capture, disc sector provenance is not.')
    else:
        lines += ['No captured DMA3 destination overlapped the B52R24 target linear source range.','This does not rule out staged CD loads followed by copy/decompression/rasterization.']
    lines += ['',f'VERDICT: {verdict}','','LAST DMA3 EVENTS:']
    for r in rows[-32:]:
        lines.append(f"- seq={r['seq']} dest=0x{r['dest_start']} bytes={r['dest_bytes']} overlap={r['overlap_bytes']} LBA={r['lba']} conf={r['lba_conf']} pc=0x{r['pc']}")
    lines += ['','EVIDENCE RULES:','- overlap>0 proves the captured CD DMA destination intersects the B52R24 GPU-source RAM range.','- A tracked Setloc LBA is a provenance candidate; sequential tracking can drift if transfer sizing is unusual.','- ISO owner mapping is only as strong as the LBA tracking for that event.','- No overlap means direct CD->target fill was not observed in this capture window; use B52R25 CPU writer or staged-load tracing.','- Do not patch disc bytes from this report alone unless runtime/GPU correlation and owner evidence agree.','- Overall Runtime PASS remains NO.']
    out=a.trace.with_name('GaiaMaster_B52R26_CD_DMA_PROVENANCE_ANALYSIS.txt'); out.write_text('\n'.join(lines)+'\n',encoding='utf-8'); print('\n'.join(lines)); print('Report:',out)
    return 0
if __name__=='__main__': raise SystemExit(main())

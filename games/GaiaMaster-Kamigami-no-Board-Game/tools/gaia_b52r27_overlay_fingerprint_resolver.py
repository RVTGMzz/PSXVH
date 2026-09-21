#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,math,struct
from pathlib import Path

CLEAN='f4d5298583c90d89c4b7e51d2dde160ee07f2aec'
BASE='0ced9982e1b00566b42ace047236378826c2aa1c'
RAW,USER=2352,2048
SLPS_EXTENT,SLPS_SIZE=24,487424
HDR=0x800
RAM_SIZE=0x200000

def sha1(p):
    h=hashlib.sha1()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest().lower()

def sector_user(p,lba):
    with p.open('rb') as f:
        f.seek(lba*RAW); s=f.read(RAW)
    if len(s)!=RAW or s[15]!=2: raise RuntimeError(f'Bad MODE2 sector {lba}')
    if s[18]&0x20: raise RuntimeError(f'Form2 sector at {lba}')
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
        if pos+n>len(data):break
        r=data[pos:pos+n]; pos+=n
        if len(r)<34:continue
        ext=int.from_bytes(r[2:6],'little'); sz=int.from_bytes(r[10:14],'little'); flags=r[25]; nl=r[32]; name=r[33:33+nl]
        if name in (b'\x00',b'\x01'):continue
        nm=name.decode('ascii','replace').split(';')[0]; path=f'{prefix}/{nm}' if prefix else nm
        if flags&2:out+=parse_dir(p,ext,sz,path,seen)
        else:out.append(dict(path=path,extent=ext,size=sz,sectors=math.ceil(sz/USER)))
    return out

def iso_index(p):
    pvd=sector_user(p,16)
    if pvd[1:6]!=b'CD001':raise RuntimeError('ISO9660 PVD not found')
    r=pvd[156:190]; return parse_dir(p,int.from_bytes(r[2:6],'little'),int.from_bytes(r[10:14],'little'))

def load_writer(p):
    out=[]
    with p.open('r',encoding='utf-8-sig',newline='') as f:
        for r in csv.DictReader(f,delimiter='\t'):
            r['pc_i']=int(r['pc'],16); r['ra_i']=int(r['ra'],16); out.append(r)
    return out

def slps_map(bin_path):
    slps=read_extent(bin_path,SLPS_EXTENT,SLPS_SIZE)
    if not slps.startswith(b'PS-X EXE'):raise RuntimeError('SLPS_020.75 is not PS-X EXE')
    _,_,taddr,tsize=struct.unpack_from('<IIII',slps,0x10)
    if tsize<=0 or HDR+tsize>len(slps):tsize=len(slps)-HDR
    return taddr,tsize

def phys(pc):return pc&0x1fffff

def similarity(a,b):
    n=min(len(a),len(b))
    if n==0:return 0.0
    return sum(x==y for x,y in zip(a[:n],b[:n]))/n

def find_matches(blob,anchor,max_hits=64):
    hits=[]; pos=0
    while len(hits)<max_hits:
        i=blob.find(anchor,pos)
        if i<0:break
        hits.append(i); pos=i+1
    return hits

def selftest():
    ram=bytearray(512); blob=bytearray(1024)
    pat=bytes(range(64)); ram[100:164]=pat; blob[400:464]=pat
    assert find_matches(blob,ram[100:164])==[400]
    assert similarity(pat,pat)==1.0
    print('B52R27 OVERLAY FINGERPRINT RESOLVER SELFTEST PASS')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('writer_trace',nargs='?',type=Path); ap.add_argument('writer_ram',nargs='?',type=Path); ap.add_argument('bin',nargs='?',type=Path)
    ap.add_argument('--selftest',action='store_true')
    a=ap.parse_args()
    if a.selftest:selftest();return 0
    if not a.writer_trace or not a.writer_ram or not a.bin:ap.error('WRITER_TRACE.tsv WRITER_RAM.bin exact_BIN required')
    sh=sha1(a.bin)
    if sh not in (BASE,CLEAN):raise RuntimeError(f'Unknown BIN SHA1 {sh}')
    ram=a.writer_ram.read_bytes()
    if len(ram)<RAM_SIZE:raise RuntimeError(f'Writer RAM snapshot too small: {len(ram)}')
    events=load_writer(a.writer_trace); files=iso_index(a.bin); taddr,tsize=slps_map(a.bin)
    file_cache={}
    rows=[]; notes=[]
    for ei,e in enumerate(events,1):
        pc=e['pc_i']; p=phys(pc)
        if taddr<=pc<taddr+tsize:
            notes.append(f'event {ei}: PC 0x{pc:08X} is inside main SLPS text; use B52R25 writer-PC resolver.')
            continue
        if not ((0x80000000<=pc<0x80200000) or (0xA0000000<=pc<0xA0200000) or pc<0x00200000):
            notes.append(f'event {ei}: PC 0x{pc:08X} is not main RAM code; skipped.')
            continue
        if p<128 or p+128>len(ram):
            notes.append(f'event {ei}: PC 0x{pc:08X} too close to RAM edge for fingerprint.')
            continue
        found_for_event=[]
        for alen in (96,64,48,32):
            astart=(p-(alen//2))&~3; anchor=ram[astart:astart+alen]
            if not any(anchor):continue
            for f in files:
                try:
                    if f['path'] not in file_cache:file_cache[f['path']]=read_extent(a.bin,f['extent'],f['size'])
                    blob=file_cache[f['path']]
                except RuntimeError:
                    continue
                for hit in find_matches(blob,anchor):
                    ram_ctx_start=max(0,astart-128); file_ctx_start=max(0,hit-(astart-ram_ctx_start))
                    ram_ctx=ram[ram_ctx_start:min(len(ram),ram_ctx_start+256)]
                    blob_ctx=blob[file_ctx_start:min(len(blob),file_ctx_start+len(ram_ctx))]
                    sim=similarity(ram_ctx,blob_ctx)
                    raw_lba=f['extent']+(hit//USER)
                    rows.append(dict(event=ei,pc=f'0x{pc:08X}',phys=f'0x{p:06X}',anchor_len=alen,path=f['path'],file_offset=f'0x{hit:X}',extent=f['extent'],raw_lba=raw_lba,raw_bin_offset=f'0x{raw_lba*RAW:X}',context_similarity=f'{sim:.4f}'))
                    found_for_event.append((alen,sim,f['path'],hit))
            if found_for_event:break
        if not found_for_event:notes.append(f'event {ei}: no exact 32+ byte overlay fingerprint match found.')
    outdir=a.writer_trace.parent
    csvp=outdir/'GaiaMaster_B52R27_OVERLAY_FINGERPRINTS.csv'
    with csvp.open('w',encoding='utf-8-sig',newline='') as f:
        fields=['event','pc','phys','anchor_len','path','file_offset','extent','raw_lba','raw_bin_offset','context_similarity']
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    ranked=sorted(rows,key=lambda r:(int(r['anchor_len']),float(r['context_similarity'])),reverse=True)
    rep=outdir/'GaiaMaster_B52R27_OVERLAY_FINGERPRINT_REPORT.txt'
    lines=['GAIA MASTER B52R27 OVERLAY FINGERPRINT RESOLVE','='*78,f'BIN SHA1       : {sh}',f'writer events  : {len(events)}',f'ISO files      : {len(files)}',f'fingerprint rows: {len(rows)}','']
    lines+=notes+['','TOP CANDIDATES:']
    if ranked:
        for r in ranked[:50]:
            lines.append(f"- event={r['event']} pc={r['pc']} anchor={r['anchor_len']}B sim={r['context_similarity']} file={r['path']} file_off={r['file_offset']} LBA={r['raw_lba']}")
    else:lines.append('- none')
    lines += ['','INTERPRETATION:','- 96/64-byte exact matches with high surrounding-context similarity are strong raw-overlay ownership candidates.','- 32/48-byte matches are weaker and require corroboration.','- No match does not rule out overlay code if it was decompressed, relocated, patched, or unloaded before the snapshot.','- Main-SLPS writer PCs belong in B52R25 resolver, not this tool.','- A code-owner match identifies where the writer code came from, not yet the data bytes that produced the visible Japanese UI.','- Overall Runtime PASS remains NO.',f'CSV: {csvp.name}']
    rep.write_text('\n'.join(lines)+'\n',encoding='utf-8');print('\n'.join(lines));print('Report:',rep)
    return 0
if __name__=='__main__':raise SystemExit(main())

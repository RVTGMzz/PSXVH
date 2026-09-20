#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,struct,math
from pathlib import Path

RAM_SIZE=0x200000

def hx(s):
    s=str(s).strip(); return int(s,16) if s else 0

def load_events(path):
    ev=[]
    with path.open('r',encoding='utf-8-sig',newline='') as f:
        for r in csv.DictReader(f,delimiter='\t'):
            ev.append({k:r[k] for k in r} | {'seq_i':int(r['seq']),'pc_i':hx(r['pc']),'ra_i':hx(r['ra']),'value_i':hx(r['value']),'func_i':hx(r['func_start']),'score_i':int(r['score'])})
    return ev

def phys(a): return a & 0x1fffff

def u32(data,off):
    if off<0 or off+4>len(data): raise IndexError(off)
    return struct.unpack_from('<I',data,off)[0]

def entropy(data):
    if not data:return 0.0
    c=[0]*256
    for b in data:c[b]+=1
    n=len(data); return -sum((x/n)*math.log2(x/n) for x in c if x)

def find_transaction(events):
    starts=[(i,e) for i,e in enumerate(events) if e['hw']=='DMA2_CHCR' and ((e['value_i']>>24)&1)]
    if not starts: return None
    i,ch=starts[-1]
    madr=bcr=None; gp0=[]
    for e in events[:i+1]:
        if e['hw']=='DMA2_MADR': madr=e
        elif e['hw']=='DMA2_BCR': bcr=e
        elif e['hw']=='GP0': gp0.append(e)
    return dict(index=i,chcr=ch,madr=madr,bcr=bcr,gp0=gp0)

def decode_chcr(v):
    return dict(direction=v&1,step=(v>>1)&1,chop=(v>>8)&1,sync=(v>>9)&3,start=(v>>24)&1,force=(v>>28)&1)

def count16(v): return v if v else 0x10000

def extract_linear(ram,madr,bcr,ch):
    sync=ch['sync']; step=ch['step']
    if sync==0: words=count16(bcr&0xffff)
    elif sync==1: words=count16(bcr&0xffff)*count16((bcr>>16)&0xffff)
    else:return b'',0
    words=min(words,0x80000)
    out=bytearray(); a=phys(madr)&~3; delta=-4 if step else 4
    for _ in range(words):
        if a+4>len(ram): break
        out += ram[a:a+4]; a=(a+delta)&0x1fffff
    return bytes(out),words

def parse_linked(ram,madr,max_nodes=4096,max_words=1_000_000):
    rows=[]; words=[]; seen=set(); a=phys(madr)&~3
    for ni in range(max_nodes):
        if a in seen: rows.append((ni,a,0,0,'LOOP')); break
        seen.add(a)
        if a+4>len(ram): rows.append((ni,a,0,0,'OOB')); break
        h=u32(ram,a); count=(h>>24)&0xff; nxt=h&0xffffff; rows.append((ni,a,count,nxt,'OK'))
        for j in range(count):
            off=a+4+j*4
            if off+4>len(ram): break
            words.append((ni,j,off,u32(ram,off)))
            if len(words)>=max_words: return rows,words
        if nxt>=0x800000 or nxt==0xffffff: break
        a=phys(nxt)&~3
    return rows,words

def gp0_sequence(events):
    vals=[e['value_i'] for e in events]
    out=[]
    for i,v in enumerate(vals):
        cmd=(v>>24)&0xff
        if cmd in (0xA0,0x80,0xC0):
            d={'index':i,'cmd':cmd,'word':v}
            if cmd==0xA0 and i+2<len(vals):
                xy=vals[i+1]; wh=vals[i+2]
                d.update(x=xy&0x3ff,y=(xy>>16)&0x1ff,w=wh&0xffff,h=(wh>>16)&0xffff)
            out.append(d)
    return out

def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p=Path(d); tr=p/'GaiaMaster_B52R24_TRACE.tsv'; rp=p/'GaiaMaster_B52R24_RAM.bin'
        tr.write_text('seq\tpc\tra\thw\treg\tvalue\tfunc_start\tscore\n1\t80010010\t80020000\tDMA2_MADR\tt0\t00001000\t80010000\t500\n2\t80010014\t80020000\tDMA2_BCR\tt1\t00010004\t80010000\t500\n3\t80010018\t80020000\tDMA2_CHCR\tt2\t01000201\t80010000\t500\n',encoding='utf-8')
        b=bytearray(RAM_SIZE)
        for i,v in enumerate([0xA0000000,0,0x00010001,0x11223344]): struct.pack_into('<I',b,0x1000+i*4,v)
        rp.write_bytes(b)
        events=load_events(tr); tx=find_transaction(events); assert tx and tx['madr']['value_i']==0x1000
        ch=decode_chcr(tx['chcr']['value_i']); raw,words=extract_linear(b,0x1000,0x00010004,ch)
        assert words==4 and len(raw)==16 and u32(raw,0)==0xA0000000
    print('B52R24 TRACE ANALYZER SELFTEST PASS')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('trace',nargs='?',type=Path); ap.add_argument('ram',nargs='?',type=Path); ap.add_argument('--selftest',action='store_true'); a=ap.parse_args()
    if a.selftest: selftest(); return 0
    if not a.trace: ap.error('TRACE.tsv required')
    ram_path=a.ram
    if ram_path is None:
        name=a.trace.name.replace('_TRACE.tsv','_RAM.bin')
        ram_path=a.trace.with_name(name)
    events=load_events(a.trace); ram=ram_path.read_bytes()
    if len(ram)<RAM_SIZE: raise RuntimeError(f'RAM snapshot too small: {len(ram)}')
    tx=find_transaction(events)
    if not tx: raise RuntimeError('No DMA2_CHCR start event found')
    chv=tx['chcr']['value_i']; ch=decode_chcr(chv); madr=tx['madr']['value_i'] if tx['madr'] else 0; bcr=tx['bcr']['value_i'] if tx['bcr'] else 0
    outdir=a.trace.parent; stem=a.trace.stem.replace('_TRACE','')
    report=outdir/f'{stem}_ANALYSIS.txt'; nodes_csv=outdir/f'{stem}_DMA_NODES.csv'; payload=outdir/f'{stem}_DMA_SOURCE.bin'
    lines=['GAIA MASTER B52R24 DMA SOURCE ANALYSIS','='*78,f'events       : {len(events)}',f'MADR         : 0x{madr:08X} (phys 0x{phys(madr):06X})',f'BCR          : 0x{bcr:08X}',f'CHCR         : 0x{chv:08X}',f'direction    : {ch["direction"]} ({"RAM->GPU" if ch["direction"] else "GPU->RAM"})',f'step         : {ch["step"]} ({"-4" if ch["step"] else "+4"})',f'sync mode    : {ch["sync"]}',f'start        : {ch["start"]}']
    seq=gp0_sequence(tx['gp0']); lines += ['',f'GP0 writes before DMA start: {len(tx["gp0"])}',f'GP0 notable commands: {len(seq)}']
    for d in seq[-20:]:
        if d['cmd']==0xA0 and 'x' in d: lines.append(f"- A0 CPU->VRAM at GP0 index {d['index']}: x={d['x']} y={d['y']} w={d['w']} h={d['h']}")
        else: lines.append(f"- GP0 cmd 0x{d['cmd']:02X} at index {d['index']} word=0x{d['word']:08X}")
    if ch['sync']==2:
        nodes,words=parse_linked(ram,madr)
        with nodes_csv.open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.writer(f); w.writerow(['node','addr','count','next','status'])
            for n,a2,c,nx,st in nodes:w.writerow([n,f'0x{a2:06X}',c,f'0x{nx:06X}',st])
        raw=b''.join(struct.pack('<I',w4) for _,_,_,w4 in words); payload.write_bytes(raw)
        lines += ['',f'linked-list nodes: {len(nodes)}',f'linked-list payload words: {len(words)}',f'payload bytes: {len(raw)}',f'payload entropy: {entropy(raw):.4f}',f'nodes CSV: {nodes_csv.name}',f'payload BIN: {payload.name}']
        cmds=[]
        for wi,(_,_,off,w4) in enumerate(words):
            c=(w4>>24)&0xff
            if c in (0xA0,0x80,0xC0):cmds.append((wi,off,c,w4))
        lines.append(f'linked-list notable GP0 words: {len(cmds)}')
        for wi,off,c,w4 in cmds[:50]:lines.append(f'- word#{wi} RAM+0x{off:06X}: cmd=0x{c:02X} word=0x{w4:08X}')
    else:
        raw,words=extract_linear(ram,madr,bcr,ch); payload.write_bytes(raw)
        lines += ['',f'linear DMA words requested/capped: {words}',f'payload bytes extracted: {len(raw)}',f'payload entropy: {entropy(raw):.4f}',f'payload BIN: {payload.name}']
    lines += ['','INTERPRETATION:','- This proves the RAM source used by the captured DMA transaction, not yet the disc/archive owner.','- For SyncMode 1, payload is the VRAM transfer source candidate.','- For SyncMode 2, payload is flattened GPU command-list words.','- If an A0 sequence is present, its x/y/w/h identifies the VRAM upload rectangle.','- Next step is correlate this RAM source back to CD/archive load/decompression ownership before patching.','- Overall Runtime PASS remains NO.']
    report.write_text('\n'.join(lines)+'\n',encoding='utf-8'); print('\n'.join(lines)); print('Report:',report)
    return 0

if __name__=='__main__': raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,struct,json
from pathlib import Path

CLEAN='f4d5298583c90d89c4b7e51d2dde160ee07f2aec'
BASE='0ced9982e1b00566b42ace047236378826c2aa1c'
RAW,USER=2352,2048
MAGIC=0x10F0

def sha1_bytes(b): return hashlib.sha1(b).hexdigest()
def sha1_file(p):
    h=hashlib.sha1()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
    return h.hexdigest().lower()

def sector_user(f,lba):
    f.seek(lba*RAW); s=f.read(RAW)
    if len(s)!=RAW or s[15]!=2 or s[16:20]!=s[20:24]: raise RuntimeError(f'Bad MODE2 sector {lba}')
    if s[18]&0x20: return None
    return s[24:24+USER]

def read_extent(f,lba,size):
    out=bytearray(); left=size; cur=lba
    while left:
        u=sector_user(f,cur)
        if u is None: raise RuntimeError(f'Expected Form1 file sector at LBA {cur}')
        n=min(USER,left); out+=u[:n]; left-=n; cur+=1
    return bytes(out)

def rec_name(rec):
    n=rec[32]; name=rec[33:33+n]
    if name in (b'\x00',b'\x01'): return None
    return name.decode('ascii','replace').split(';')[0].rstrip('.')

def iso_index(binpath):
    files=[]; seen=set()
    with binpath.open('rb') as f:
        pvd=sector_user(f,16)
        if pvd is None or pvd[0]!=1 or pvd[1:6]!=b'CD001': raise RuntimeError('ISO9660 PVD not found')
        root=pvd[156:156+pvd[156]]
        re=struct.unpack_from('<I',root,2)[0]; rs=struct.unpack_from('<I',root,10)[0]
        def walk(ext,size,prefix):
            if (ext,size) in seen:return
            seen.add((ext,size)); data=read_extent(f,ext,size); i=0
            while i<len(data):
                ln=data[i]
                if ln==0: i=((i//USER)+1)*USER; continue
                rec=data[i:i+ln]
                if len(rec)<34: break
                name=rec_name(rec); flags=rec[25]; e=struct.unpack_from('<I',rec,2)[0]; sz=struct.unpack_from('<I',rec,10)[0]
                i+=ln
                if name is None: continue
                path=(prefix+'/'+name) if prefix else name
                if flags&2: walk(e,sz,path)
                else: files.append(dict(path=path,extent=e,size=sz))
        walk(re,rs,'')
    return files

def bdp_checksum(block):
    if len(block)<8:return None
    s=(sum(block[:4])+sum(block[8:]))&0xffff
    return (((~s)&0xffff)<<16)|s

def parse_exact(data,start,end):
    if start<0 or end>len(data) or end-start<16:return None
    magic,stored,toc,count=struct.unpack_from('<IIII',data,start)
    if magic!=MAGIC or count>65535 or toc!=8+count*8:return None
    base=start+8+toc
    if start+16+count*8>base or base>end:return None
    members=[]
    for i in range(count):
        rel,z=struct.unpack_from('<II',data,start+16+i*8); a=base+rel; e=a+z
        if z<=0 or a<base or e>end:return None
        members.append((i,a,e))
    calc=bdp_checksum(data[start:end])
    if calc!=stored:return None
    return dict(start=start,end=end,size=end-start,count=count,stored=stored,calc=calc,members=members,source='exact-boundary')

def infer_container(data,start):
    if start<0 or start+16>len(data):return None
    magic,stored,toc,count=struct.unpack_from('<IIII',data,start)
    if magic!=MAGIC or count>65535 or toc!=8+count*8:return None
    base=start+8+toc
    if start+16+count*8>base or base>len(data):return None
    members=[]; mx=base
    for i in range(count):
        rel,z=struct.unpack_from('<II',data,start+16+i*8); a=base+rel; e=a+z
        if z<=0 or a<base or e>len(data):return None
        members.append((i,a,e)); mx=max(mx,e)
    calc=bdp_checksum(data[start:mx])
    if calc!=stored:return None
    return dict(start=start,end=mx,size=mx-start,count=count,stored=stored,calc=calc,members=members,source='inferred-end')

def enumerate_containers(data):
    found={}
    root=parse_exact(data,0,len(data))
    def add(c):
        if c: found[(c['start'],c['end'])]=c
    def recurse(c,depth=0):
        if not c or depth>12:return
        add(c)
        for i,a,e in c['members']:
            ch=parse_exact(data,a,e)
            if ch:
                ch=ch.copy(); ch['source']=f'member-boundary:{i}'; recurse(ch,depth+1)
    recurse(root)
    sig=struct.pack('<I',MAGIC); pos=0
    while True:
        pos=data.find(sig,pos)
        if pos<0:break
        add(infer_container(data,pos)); pos+=1
    return sorted(found.values(),key=lambda c:(c['start'],c['end']))

def containing(containers,start,end):
    return sorted([c for c in containers if c['start']<=start and end<=c['end']],key=lambda c:(c['size'],c['start']))

def member_for(c,start,end):
    hits=[i for i,a,e in c['members'] if a<=start and end<=e]
    return hits[0] if len(hits)==1 else None

def sectors_for(extent,start,length):
    if length<=0:return []
    a=extent+start//USER; b=extent+(start+length-1)//USER
    return list(range(a,b+1))

def raw_offset(extent,file_offset):
    return (extent+file_offset//USER)*RAW+24+(file_offset%USER)

def load_candidate_csv(path,row):
    with path.open('r',encoding='utf-8-sig',newline='') as f: rr=list(csv.DictReader(f))
    if not rr:raise RuntimeError('Candidate CSV empty')
    if row<1 or row>len(rr):raise RuntimeError(f'--row must be 1..{len(rr)}')
    r=rr[row-1]
    if 'path' not in r or 'file_offset' not in r:raise RuntimeError('CSV must contain path,file_offset')
    return r['path'],int(r['file_offset'],0),r

def simulate(data,off,repl,anc):
    work=bytearray(data); work[off:off+len(repl)]=repl; changes=[]
    for c in anc:
        old=struct.unpack_from('<I',work,c['start']+4)[0]
        new=bdp_checksum(bytes(work[c['start']:c['end']]))
        struct.pack_into('<I',work,c['start']+4,new)
        changes.append((c['start'],c['end'],old,new))
    for c in anc:
        stored=struct.unpack_from('<I',work,c['start']+4)[0]
        calc=bdp_checksum(bytes(work[c['start']:c['end']]))
        if stored!=calc: raise RuntimeError(f'Bottom-up checksum simulation failed at 0x{c["start"]:X}')
    return bytes(work),changes

def selftest():
    child=bytearray(28); struct.pack_into('<IIII',child,0,MAGIC,0,16,1); struct.pack_into('<II',child,16,0,4); child[24:28]=b'TEST'; struct.pack_into('<I',child,4,bdp_checksum(child))
    parent=bytearray(24+len(child)); struct.pack_into('<IIII',parent,0,MAGIC,0,16,1); struct.pack_into('<II',parent,16,0,len(child)); parent[24:]=child; struct.pack_into('<I',parent,4,bdp_checksum(parent))
    cs=enumerate_containers(bytes(parent)); anc=containing(cs,48,52)
    assert len(anc)==2 and member_for(anc[0],48,52)==0 and member_for(anc[1],48,52)==0
    out,chg=simulate(bytes(parent),48,b'BEST',anc)
    assert out[48:52]==b'BEST' and len(chg)==2
    assert struct.unpack_from('<I',out,4)[0]==bdp_checksum(out)
    print('B52R30 OWNERSHIP/PATCH PLANNER SELFTEST PASS')

def main():
    ap=argparse.ArgumentParser(description='Gaia Master B52R30 read-only ownership + patch planner')
    ap.add_argument('bin',nargs='?',type=Path)
    ap.add_argument('--file')
    ap.add_argument('--offset',type=lambda x:int(x,0))
    ap.add_argument('--length',type=lambda x:int(x,0),default=None)
    ap.add_argument('--candidate-csv',type=Path)
    ap.add_argument('--row',type=int,default=1)
    ap.add_argument('--payload',type=Path)
    ap.add_argument('--replacement',type=Path)
    ap.add_argument('--selftest',action='store_true')
    a=ap.parse_args()
    if a.selftest:selftest();return 0
    if not a.bin:ap.error('exact B52R14R1/CLEAN BIN required')
    b=a.bin.resolve(); sh=sha1_file(b)
    if sh not in(BASE,CLEAN):raise RuntimeError(f'Unknown BIN SHA1 {sh}')
    if a.candidate_csv:
        path,off,_meta=load_candidate_csv(a.candidate_csv,a.row)
        if a.file and a.file!=path:raise RuntimeError('--file disagrees with candidate CSV')
    else:
        if not a.file or a.offset is None:ap.error('use --candidate-csv or both --file and --offset')
        path,off=a.file,a.offset
    payload=a.payload.read_bytes() if a.payload else None
    length=a.length if a.length is not None else (len(payload) if payload is not None else 1)
    if length<=0:raise RuntimeError('length must be >0')
    entries=iso_index(b); matches=[e for e in entries if e['path'].upper()==path.upper()]
    if not matches: matches=[e for e in entries if Path(e['path']).name.upper()==Path(path).name.upper()]
    if len(matches)!=1:raise RuntimeError(f'ISO file resolution for {path!r}: {len(matches)} matches')
    ent=matches[0]
    if off<0 or off+length>ent['size']:raise RuntimeError('candidate range outside ISO file')
    with b.open('rb') as f:data=read_extent(f,ent['extent'],ent['size'])
    if payload is not None and data[off:off+len(payload)]!=payload:
        raise RuntimeError('payload does not match candidate file bytes at requested offset')
    containers=enumerate_containers(data); anc=containing(containers,off,off+length)
    patch_secs=set(sectors_for(ent['extent'],off,length)); checksum_secs=set(); rows=[]
    for depth,c in enumerate(anc):
        mi=member_for(c,off,off+length); checksum_secs.update(sectors_for(ent['extent'],c['start']+4,4))
        rows.append(dict(depth=depth,start=f"0x{c['start']:X}",end=f"0x{c['end']:X}",size=c['size'],count=c['count'],member_index='' if mi is None else mi,stored=f"0x{c['stored']:08X}",source=c['source'],checksum_file_offset=f"0x{c['start']+4:X}",checksum_lba=ent['extent']+(c['start']+4)//USER))
    replacement=None; changes=[]; patched_sha=None
    if a.replacement:
        replacement=a.replacement.read_bytes()
        if len(replacement)!=length:raise RuntimeError(f'replacement length {len(replacement)} != candidate length {length}')
        patched,changes=simulate(data,off,replacement,anc); patched_sha=sha1_bytes(patched)
    touched=sorted(patch_secs|checksum_secs); out=b.parent
    csvp=out/'GaiaMaster_B52R30_BDP_ANCESTRY.csv'; rpt=out/'GaiaMaster_B52R30_OWNERSHIP_PATCH_PLAN.txt'; jsp=out/'GaiaMaster_B52R30_PATCH_PLAN.json'
    with csvp.open('w',encoding='utf-8-sig',newline='') as f:
        fields=['depth','start','end','size','count','member_index','stored','source','checksum_file_offset','checksum_lba'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    plan=dict(input_sha1=sh,file=ent['path'],extent_lba=ent['extent'],file_size=ent['size'],candidate_offset=off,candidate_length=length,candidate_sha1=sha1_bytes(data[off:off+length]),payload_sha1=sha1_bytes(payload) if payload is not None else None,candidate_raw_bin_offset=raw_offset(ent['extent'],off),candidate_lbas=sorted(patch_secs),bdp_ancestor_count=len(anc),bdp_ancestors=[dict(start=x['start'],end=x['end'],size=x['size'],count=x['count'],stored=x['stored'],member_index=member_for(x,off,off+length),source=x['source']) for x in anc],checksum_lbas=sorted(checksum_secs),all_touched_lbas=touched,replacement_simulated=bool(replacement),replacement_sha1=sha1_bytes(replacement) if replacement is not None else None,checksum_changes=[dict(container_start=s,container_end=e,old=old,new=new) for s,e,old,new in changes],simulated_logical_file_sha1=patched_sha)
    jsp.write_text(json.dumps(plan,indent=2),encoding='utf-8')
    lines=['GAIA MASTER B52R30 OWNERSHIP + PATCH PLAN','='*78,f'BIN SHA1          : {sh}',f'ISO file          : {ent["path"]}',f'File extent LBA   : {ent["extent"]}',f'File size         : {ent["size"]}',f'Candidate offset  : 0x{off:X}',f'Candidate length  : {length}',f'Raw BIN offset    : 0x{raw_offset(ent["extent"],off):X}',f'Candidate LBAs    : {", ".join(map(str,sorted(patch_secs)))}',f'Valid BDP owners  : {len(anc)}','']
    if anc:
        lines.append('BDP ANCESTRY (deepest -> outermost):')
        for i,c in enumerate(anc):lines.append(f'- depth={i} 0x{c["start"]:X}..0x{c["end"]:X} size=0x{c["size"]:X} count={c["count"]} member={member_for(c,off,off+length)} checksum=0x{c["stored"]:08X} ({c["source"]})')
    else:lines.append('BDP ANCESTRY: none proven for this candidate range.')
    lines += ['',f'Checksum LBAs     : {", ".join(map(str,sorted(checksum_secs))) or "none"}',f'All touched LBAs  : {", ".join(map(str,touched))}',f'EDC/ECC sectors   : {len(touched)}']
    if replacement is not None:
        lines += ['','DRY-RUN REPLACEMENT: VERIFIED SIZE-PRESERVING',f'Replacement SHA1  : {sha1_bytes(replacement)}',f'Logical-file SHA1 : {patched_sha}','Checksum changes (deepest -> outermost):']
        for s,e,old,new in changes:lines.append(f'- BDP 0x{s:X}..0x{e:X}: 0x{old:08X} -> 0x{new:08X}')
    else:lines += ['','No replacement supplied: checksum values are not simulated yet.']
    lines += ['','PROMOTION GATE:','- This tool is READ ONLY. It never writes BIN/CUE/ISO.','- Candidate ownership must already come from runtime/fingerprint evidence; B52R30 only verifies disc structure around it.','- Any real size-preserving patch inside these BDP owners must repair checksums deepest -> outermost.','- Every listed touched raw sector must have MODE2/Form1 EDC/ECC regenerated after mutation.','- If no BDP ancestor is proven, do not invent one; use the file-specific format contract instead.','- Overall Runtime PASS remains NO.',f'Ancestry CSV: {csvp.name}',f'Plan JSON   : {jsp.name}']
    rpt.write_text('\n'.join(lines)+'\n',encoding='utf-8');print('\n'.join(lines));print('Report:',rpt);return 0

if __name__=='__main__':
    try:raise SystemExit(main())
    except SystemExit:raise
    except Exception as e:print('[ERROR]',repr(e));raise SystemExit(9)

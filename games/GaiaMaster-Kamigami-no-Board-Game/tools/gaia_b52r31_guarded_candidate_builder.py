#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,shutil,struct,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import gaia_b52r30_ownership_patch_planner as core

ECC_F=[0]*256; ECC_B=[0]*256; EDC_LUT=[0]*256
for i in range(256):
    j=((i<<1) ^ (0x11D if (i & 0x80) else 0)) & 0xFF
    ECC_F[i]=j; ECC_B[(i^j)&0xFF]=i
    x=i
    for _ in range(8): x=(x>>1) ^ (0xD8018001 if (x&1) else 0)
    EDC_LUT[i]=x & 0xFFFFFFFF

def edc_compute(src):
    edc=0
    for v in src: edc=(edc>>8) ^ EDC_LUT[(edc^v)&0xFF]
    return edc & 0xFFFFFFFF

def ecc_compute(src,major_count,minor_count,major_mult,minor_inc):
    size=major_count*minor_count; dest=bytearray(major_count*2)
    for major in range(major_count):
        index=(major>>1)*major_mult+(major&1); a=b=0
        for _ in range(minor_count):
            t=src[index]; index+=minor_inc
            if index>=size:index-=size
            a^=t; b^=t; a=ECC_F[a]
        a=ECC_B[ECC_F[a]^b]; dest[major]=a; dest[major+major_count]=a^b
    return dest

def regen_sector(sec):
    if len(sec)!=core.RAW:raise RuntimeError('regen_sector requires 2352 bytes')
    s=bytearray(sec)
    if s[15]!=2 or s[16:20]!=s[20:24] or (s[18]&0x20):raise RuntimeError('Only MODE2/Form1 sector regeneration is supported')
    s[2072:2076]=struct.pack('<I',edc_compute(s[16:2072]))
    hdr=s[12:16]; s[12:16]=b'\0\0\0\0'
    s[2076:2248]=ecc_compute(s[12:2076],86,24,2,86)
    s[2248:2352]=ecc_compute(s[12:2248],52,43,86,88)
    s[12:16]=hdr
    return bytes(s)

def resolve_entry(binpath,path):
    xs=core.iso_index(binpath); m=[e for e in xs if e['path'].upper()==path.upper()]
    if not m:m=[e for e in xs if Path(e['path']).name.upper()==Path(path).name.upper()]
    if len(m)!=1:raise RuntimeError(f'ISO file resolution for {path!r}: {len(m)} matches')
    return m[0]

def validate_plan(plan,bin_sha,ent,data,repl):
    need=['input_sha1','file','extent_lba','file_size','candidate_offset','candidate_length','candidate_sha1','bdp_ancestors','replacement_simulated','replacement_sha1','checksum_changes','simulated_logical_file_sha1','all_touched_lbas']
    miss=[k for k in need if k not in plan]
    if miss:raise RuntimeError(f'B52R30 plan missing required keys: {miss}')
    if plan['input_sha1'].lower()!=bin_sha:raise RuntimeError('Plan/input BIN SHA1 mismatch')
    if plan['file'].upper()!=ent['path'].upper() or int(plan['extent_lba'])!=ent['extent'] or int(plan['file_size'])!=ent['size']:raise RuntimeError('Plan ISO identity mismatch')
    off=int(plan['candidate_offset']); ln=int(plan['candidate_length'])
    if off<0 or ln<=0 or off+ln>len(data):raise RuntimeError('Plan candidate range invalid')
    if core.sha1_bytes(data[off:off+ln])!=plan['candidate_sha1']:raise RuntimeError('Current candidate bytes SHA1 differs from B52R30 plan')
    if not plan['replacement_simulated']:raise RuntimeError('B52R30 plan must be generated with --replacement before B52R31 build')
    if len(repl)!=ln or core.sha1_bytes(repl)!=plan['replacement_sha1']:raise RuntimeError('Replacement length/SHA1 differs from B52R30 plan')
    if data[off:off+ln]==repl:raise RuntimeError('Replacement is identical to current bytes')
    containers=core.enumerate_containers(data); anc=core.containing(containers,off,off+ln)
    got=[]
    for c in anc:got.append(dict(start=c['start'],end=c['end'],size=c['size'],count=c['count'],stored=c['stored'],member_index=core.member_for(c,off,off+ln),source=c['source']))
    if got!=plan['bdp_ancestors']:raise RuntimeError('Current BDP ancestry differs from B52R30 plan')
    patched,changes=core.simulate(data,off,repl,anc)
    exp=[dict(container_start=s,container_end=e,old=old,new=new) for s,e,old,new in changes]
    if exp!=plan['checksum_changes']:raise RuntimeError('Simulated checksum changes differ from B52R30 plan')
    if core.sha1_bytes(patched)!=plan['simulated_logical_file_sha1']:raise RuntimeError('Simulated logical-file SHA1 differs from B52R30 plan')
    return off,ln,anc,patched,changes

def write_changed_file(out,ent,old,new):
    changed=set(); sectors=(ent['size']+core.USER-1)//core.USER
    with out.open('r+b') as f:
        for i in range(sectors):
            a=i*core.USER; b=min(len(old),a+core.USER)
            if old[a:b]==new[a:b]:continue
            lba=ent['extent']+i; f.seek(lba*core.RAW); raw=f.read(core.RAW)
            if len(raw)!=core.RAW or raw[15]!=2 or raw[16:20]!=raw[20:24] or (raw[18]&0x20):raise RuntimeError(f'Expected MODE2/Form1 at LBA {lba}')
            sec=bytearray(raw); sec[24:24+(b-a)]=new[a:b]
            f.seek(lba*core.RAW); f.write(sec); changed.add(lba)
        for lba in sorted(changed):
            f.seek(lba*core.RAW); raw=f.read(core.RAW); f.seek(lba*core.RAW); f.write(regen_sector(raw))
    return changed

def selftest():
    child=bytearray(28);struct.pack_into('<IIII',child,0,core.MAGIC,0,16,1);struct.pack_into('<II',child,16,0,4);child[24:]=b'TEST';struct.pack_into('<I',child,4,core.bdp_checksum(child))
    parent=bytearray(24+len(child));struct.pack_into('<IIII',parent,0,core.MAGIC,0,16,1);struct.pack_into('<II',parent,16,0,len(child));parent[24:]=child;struct.pack_into('<I',parent,4,core.bdp_checksum(parent))
    data=bytes(parent); off=48; repl=b'BEST'; anc=core.containing(core.enumerate_containers(data),off,off+4); patched,changes=core.simulate(data,off,repl,anc)
    plan={'input_sha1':'x','file':'F','extent_lba':1,'file_size':len(data),'candidate_offset':off,'candidate_length':4,'candidate_sha1':core.sha1_bytes(b'TEST'),'bdp_ancestors':[dict(start=c['start'],end=c['end'],size=c['size'],count=c['count'],stored=c['stored'],member_index=core.member_for(c,off,off+4),source=c['source']) for c in anc],'replacement_simulated':True,'replacement_sha1':core.sha1_bytes(repl),'checksum_changes':[dict(container_start=s,container_end=e,old=o,new=n) for s,e,o,n in changes],'simulated_logical_file_sha1':core.sha1_bytes(patched),'all_touched_lbas':[1]}
    ent={'path':'F','extent':1,'size':len(data)}
    validate_plan(plan,'x',ent,data,repl)
    assert patched[48:52]==b'BEST'
    print('B52R31 GUARDED CANDIDATE BUILDER SELFTEST PASS')

def main():
    ap=argparse.ArgumentParser(description='Gaia Master B52R31 guarded candidate builder')
    ap.add_argument('bin',nargs='?',type=Path);ap.add_argument('plan',nargs='?',type=Path);ap.add_argument('replacement',nargs='?',type=Path)
    ap.add_argument('--build',action='store_true');ap.add_argument('--output',type=Path);ap.add_argument('--selftest',action='store_true')
    a=ap.parse_args()
    if a.selftest:selftest();return 0
    if not a.bin or not a.plan or not a.replacement:ap.error('BIN, B52R30 PATCH_PLAN.json, replacement blob required')
    b=a.bin.resolve(); sh=core.sha1_file(b)
    if sh not in(core.BASE,core.CLEAN):raise RuntimeError(f'Unknown BIN SHA1 {sh}')
    plan=json.loads(a.plan.read_text(encoding='utf-8')); repl=a.replacement.read_bytes(); ent=resolve_entry(b,plan.get('file',''))
    with b.open('rb') as f:data=core.read_extent(f,ent['extent'],ent['size'])
    off,ln,anc,patched,changes=validate_plan(plan,sh,ent,data,repl)
    planned=set(int(x) for x in plan['all_touched_lbas'])
    report=b.parent/'GaiaMaster_B52R31_GUARDED_BUILD_REPORT.txt'
    lines=['GAIA MASTER B52R31 GUARDED CANDIDATE BUILDER','='*78,f'Input SHA1       : {sh}',f'ISO file         : {ent["path"]}',f'Candidate        : +0x{off:X} length={ln}',f'Replacement SHA1 : {core.sha1_bytes(repl)}',f'BDP ancestors    : {len(anc)}',f'Planned LBAs     : {", ".join(map(str,sorted(planned)))}','']
    if not a.build:
        lines += ['VERDICT: GUARDED DRY-RUN PASS','No BIN/CUE was written. Use --build only after runtime/source ownership has been proven.','Overall Runtime PASS remains NO.']
        report.write_text('\n'.join(lines)+'\n',encoding='utf-8');print('\n'.join(lines));print('Report:',report);return 0
    out=a.output.resolve() if a.output else b.with_name(b.stem+' [B52R31 GUARDED CANDIDATE].bin')
    if out in (b,a.plan.resolve(),a.replacement.resolve()):raise RuntimeError('Output path collision')
    if out.exists():out.unlink()
    shutil.copyfile(b,out); changed=write_changed_file(out,ent,data,patched)
    if not changed:raise RuntimeError('Build produced no changed raw sectors')
    if not changed.issubset(planned):raise RuntimeError(f'Actual changed sectors outside B52R30 plan: {sorted(changed-planned)}')
    with out.open('rb') as f:verify=core.read_extent(f,ent['extent'],ent['size'])
    if verify!=patched:raise RuntimeError('Output logical file does not match simulated B52R30 file')
    if verify[off:off+ln]!=repl:raise RuntimeError('Output replacement readback failed')
    for c in anc:
        stored=struct.unpack_from('<I',verify,c['start']+4)[0]; calc=core.bdp_checksum(verify[c['start']:c['end']])
        if stored!=calc:raise RuntimeError(f'Output BDP checksum failed at 0x{c["start"]:X}')
    cue=out.with_suffix('.cue'); cue.write_text(f'FILE "{out.name}" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n',encoding='ascii')
    lines += ['VERDICT: GUARDED BUILD + STATIC READBACK PASS',f'Output BIN        : {out}',f'Output CUE        : {cue}',f'Output SHA1       : {core.sha1_file(out)}',f'Changed LBAs      : {", ".join(map(str,sorted(changed)))}',f'Changed sectors   : {len(changed)}','BDP checksum readback: PASS','MODE2/Form1 EDC/ECC regenerated for every changed sector.','Runtime validation is still REQUIRED. Overall Runtime PASS remains NO.']
    report.write_text('\n'.join(lines)+'\n',encoding='utf-8');print('\n'.join(lines));print('Report:',report);return 0

if __name__=='__main__':
    try:raise SystemExit(main())
    except SystemExit:raise
    except Exception as e:print('[ERROR]',repr(e));raise SystemExit(9)

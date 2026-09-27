#!/usr/bin/env python3
from __future__ import annotations
import hashlib, shutil, string, struct, sys
from pathlib import Path
import gaia_nf1_new_font_art as art

BASE_SHA1='0ced9982e1b00566b42ace047236378826c2aa1c'
SLPS_EXTENT=24; SLPS_SIZE=487424
PRG_EXTENT=2679; PRG_SIZE=1534236
ATLAS_OFF=0x5C4EC; ATLAS_GLYPHS=860; GLYPH_BYTES=72; MAPPING_OFF=0x6B6CC
KNOWN_SHADOW_INDEX=7
PRODUCTION_SLOTS=[18,33,58,160,182,261,301,371,392,420,421,422,423,424,425,426,427,428,429,430,431,432,433,434,435,436,437,438,439,440,517,695,704,713,38,94,108,109,129,130,150,208,295,326,335,345,372,385,394,398,400,403,702,715,729,745,750,754,757,790]
PLAIN=list(string.ascii_uppercase+string.ascii_lowercase+string.digits)

ECC_F=[0]*256;ECC_B=[0]*256;EDC_LUT=[0]*256
for i in range(256):
    j=((i<<1)^(0x11D if i&0x80 else 0))&255;ECC_F[i]=j;ECC_B[(i^j)&255]=i
    x=i
    for _ in range(8):x=(x>>1)^(0xD8018001 if x&1 else 0)
    EDC_LUT[i]=x&0xffffffff

def edc_compute(src):
    edc=0
    for v in src:edc=(edc>>8)^EDC_LUT[(edc^v)&255]
    return edc&0xffffffff

def ecc_compute(src,major_count,minor_count,major_mult,minor_inc):
    size=major_count*minor_count;dest=bytearray(major_count*2)
    for major in range(major_count):
        index=(major>>1)*major_mult+(major&1);a=b=0
        for _ in range(minor_count):
            t=src[index];index+=minor_inc
            if index>=size:index-=size
            a^=t;b^=t;a=ECC_F[a]
        a=ECC_B[ECC_F[a]^b];dest[major]=a;dest[major+major_count]=a^b
    return dest

def regen_sector(sec):
    if len(sec)!=2352:raise RuntimeError('Bad raw sector length')
    s=bytearray(sec)
    if s[15]!=2 or (s[18]&0x20) or s[16:20]!=s[20:24]:raise RuntimeError('Expected MODE2/Form1 sector')
    s[2072:2076]=struct.pack('<I',edc_compute(s[16:2072]));hdr=bytes(s[12:16]);s[12:16]=b'\0\0\0\0'
    s[2076:2248]=ecc_compute(s[12:2076],86,24,2,86);s[2248:2352]=ecc_compute(s[12:2248],52,43,86,88);s[12:16]=hdr
    return bytes(s)

def sha1_file(p):
    h=hashlib.sha1()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest().lower()

def read_iso_file(rawf,extent,size):
    out=bytearray();left=size;lba=extent
    while left:
        n=min(2048,left);rawf.seek(lba*2352+24);b=rawf.read(n)
        if len(b)!=n:raise RuntimeError('Short ISO read')
        out+=b;left-=n;lba+=1
    return bytes(out)

def write_changed(rawf,extent,old,new):
    if len(old)!=len(new):raise RuntimeError('File size changed')
    changed=set()
    for i in range((len(old)+2047)//2048):
        a=i*2048;b=min(a+2048,len(old))
        if old[a:b]==new[a:b]:continue
        lba=extent+i;rawf.seek(lba*2352);sec=bytearray(rawf.read(2352))
        if len(sec)!=2352 or sec[15]!=2 or (sec[18]&0x20):raise RuntimeError('Bad target sector %d'%lba)
        sec[24:24+(b-a)]=new[a:b];rawf.seek(lba*2352);rawf.write(sec);changed.add(lba)
    return changed

def fullwidth_code(ch):
    fw=chr(ord(ch)+0xFEE0);b=fw.encode('cp932')
    if len(b)!=2:raise RuntimeError('No fullwidth code for %r'%ch)
    return (b[0]<<8)|b[1]

def mapping_value(slps,code):
    off=MAPPING_OFF+((code&0x7fff)*2)
    if off+2>len(slps):return None
    return struct.unpack_from('<H',slps,off)[0]

def decode(raw):
    g=[[0]*12 for _ in range(12)];p=0
    for y in range(12):
        for x in range(0,12,2):
            b=raw[p];p+=1;g[y][x]=b&15;g[y][x+1]=(b>>4)&15
    return g

def choose_fill(g):
    h=[0]*16
    for r in g:
        for v in r:h[v]+=1
    candidates=[(h[i],i) for i in range(1,16) if h[i] and i!=KNOWN_SHADOW_INDEX]
    if not candidates:candidates=[(h[i],i) for i in range(1,16) if h[i]]
    if not candidates:raise RuntimeError('Reference glyph has no visible palette index')
    return max(candidates)[1],h

def selftest():
    assert len(PLAIN)==62 and len(art.CUSTOM_CHARS)==60 and len(PRODUCTION_SLOTS)==60
    assert len(set(PRODUCTION_SLOTS))==60
    for ch in PLAIN+art.CUSTOM_CHARS:assert len(art.encode_4bpp(art.render_char(ch),3))==72
    s=bytearray(2352);s[15]=2;s[16:20]=b'\0\0\x08\0';s[20:24]=s[16:20]
    out=regen_sector(s);assert len(out)==2352 and out[15]==2
    print('NF1 NEW FONT BUILDER SELFTEST PASS glyphs=122')

def main():
    if len(sys.argv)==2 and sys.argv[1]=='--selftest':selftest();return 0
    if len(sys.argv)!=2:
        print('Usage: %s B52R14R1.bin | --selftest'%Path(sys.argv[0]).name);return 2
    src=Path(sys.argv[1]).expanduser().resolve()
    if not src.is_file():raise RuntimeError('BIN not found: %s'%src)
    sh=sha1_file(src)
    if sh!=BASE_SHA1:raise RuntimeError('Need exact B52R14R1 SHA1 %s; got %s'%(BASE_SHA1,sh))
    with src.open('rb') as f:
        slps=read_iso_file(f,SLPS_EXTENT,SLPS_SIZE);prg=read_iso_file(f,PRG_EXTENT,PRG_SIZE)
    new=bytearray(slps)
    slots={};reverse={}
    for ch in PLAIN:
        code=fullwidth_code(ch);slot=mapping_value(slps,code)
        if slot is None or not(0<=slot<ATLAS_GLYPHS):raise RuntimeError('Invalid mapping %r %04X -> %r'%(ch,code,slot))
        if slot in reverse:raise RuntimeError('Plain glyph slot collision %r/%r -> %d'%(reverse[slot],ch,slot))
        slots[ch]=slot;reverse[slot]=ch
    overlap=set(slots.values())&set(PRODUCTION_SLOTS)
    if overlap:raise RuntimeError('Plain/custom slot overlap: %r'%sorted(overlap))
    a_slot=slots['A'];a_raw=slps[ATLAS_OFF+a_slot*72:ATLAS_OFF+(a_slot+1)*72];fill,hist=choose_fill(decode(a_raw))
    plan=[]
    for ch in PLAIN:plan.append((ch,slots[ch],'fullwidth-native-map'))
    for ch,slot in zip(art.CUSTOM_CHARS,PRODUCTION_SLOTS):plan.append((ch,slot,'frozen-custom-slot'))
    if len({slot for _,slot,_ in plan})!=122:raise RuntimeError('NF1 destination slots are not unique')
    for ch,slot,kind in plan:
        raw=art.encode_4bpp(art.render_char(ch),fill)
        if len(raw)!=72:raise RuntimeError('Bad glyph size %r'%ch)
        off=ATLAS_OFF+slot*72;new[off:off+72]=raw
    out=src.with_name(src.stem+' [NF1 NEW VI FONT].bin')
    cue=out.with_suffix('.cue');report=src.with_name('GaiaMaster_NF1_NEW_FONT_BUILD_REPORT.txt')
    if out.exists():out.unlink()
    shutil.copyfile(src,out)
    with out.open('r+b') as f:
        changed=write_changed(f,SLPS_EXTENT,slps,bytes(new))
        for lba in sorted(changed):
            f.seek(lba*2352);raw=f.read(2352);f.seek(lba*2352);f.write(regen_sector(raw))
    with out.open('rb') as f:
        check=read_iso_file(f,SLPS_EXTENT,SLPS_SIZE);prg2=read_iso_file(f,PRG_EXTENT,PRG_SIZE)
    if prg2!=prg:raise RuntimeError('NF1 font-only build changed PRGPACK')
    for ch,slot,_ in plan:
        want=art.encode_4bpp(art.render_char(ch),fill);off=ATLAS_OFF+slot*72
        if check[off:off+72]!=want:raise RuntimeError('Readback failed for %r slot=%d'%(ch,slot))
    cue.write_text('FILE "%s" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n'%out.name,encoding='ascii')
    lines=['GAIA MASTER NF1 NEW VIETNAMESE FONT BUILD','='*72,
           'Input B52R14R1 SHA1: '+sh,'Architecture: native 12x12 / 72-byte / 4bpp / static mapping','Artwork source: NF1 independent bitmap family (no native glyph body reuse)',
           'Plain Latin/digit glyphs replaced: %d'%len(PLAIN),'Vietnamese custom glyphs replaced: %d'%len(art.CUSTOM_CHARS),'Total new glyph artwork: %d'%len(plan),
           'Palette fill index inherited from native A: %d'%fill,'Native A palette histogram: '+repr(hist),'PRGPACK changed: NO','Changed raw SLPS sectors: %d'%len(changed),
           'Output SHA1: '+sha1_file(out),'','STATIC BUILD/READBACK PASS','Runtime screenshot still REQUIRED. Overall Runtime PASS remains NO.','','Destination plan:']
    lines += ['- U+%04X %s -> slot=%d (%s)'%(ord(ch),ch,slot,kind) for ch,slot,kind in plan]
    report.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('\n'.join(lines[:17]));print('Output:',out);print('Report:',report);return 0

if __name__=='__main__':
    try:raise SystemExit(main())
    except SystemExit:raise
    except Exception as e:print('[ERROR]',repr(e));raise SystemExit(9)

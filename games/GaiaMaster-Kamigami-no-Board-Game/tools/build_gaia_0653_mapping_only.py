#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function
import os, sys, hashlib, shutil, struct

EXPECTED_BIN_SHA1 = "f4d5298583c90d89c4b7e51d2dde160ee07f2aec"
EXPECTED_SLPS_SHA1 = "1dfeb6b7cfda59c108dde2dc0b8abda9a40e6ae5"
EXPECTED_PRG_SHA1 = "a9b195b8ae5d8cad7f4f755daa08337d4671632c"

SLPS_EXTENT = 24
SLPS_SIZE = 487424
PRG_EXTENT = 2679
PRG_SIZE = 1534236

ATLAS_OFF = 0x5C4EC
ATLAS_GLYPHS = 860
GLYPH_BYTES = 72
MAPPING_OFF = 0x6B6CC

VALID_CODE_RANGES = (
    (0x8140, 0x84BE),
    (0x8540, 0x9872),
)

TEST_CODES = list(range(0x889F, 0x88AB))
TEST_LABELS = ["A", "Â", "Ấ", "Ẳ", "E", "Ê", "Ế", "Ể", "O", "Ô", "Ố", "Ỗ"]
PRG_TEST_OFF = 0xBFD2C
EXPECTED_OWNER_ENTRY = 29
PROTECTED_SLOTS = {0, 466, 480, 481}

ECC_F = [0] * 256
ECC_B = [0] * 256
EDC_LUT = [0] * 256
for i in range(256):
    j = ((i << 1) ^ (0x11D if (i & 0x80) else 0)) & 0xFF
    ECC_F[i] = j
    ECC_B[(i ^ j) & 0xFF] = i
    x = i
    for _ in range(8):
        x = (x >> 1) ^ (0xD8018001 if (x & 1) else 0)
    EDC_LUT[i] = x & 0xFFFFFFFF

def edc_compute(src):
    edc = 0
    for v in src:
        if not isinstance(v, int): v = ord(v)
        edc = (edc >> 8) ^ EDC_LUT[(edc ^ v) & 0xFF]
    return edc & 0xFFFFFFFF

def ecc_compute(src, major_count, minor_count, major_mult, minor_inc):
    size = major_count * minor_count
    dest = bytearray(major_count * 2)
    for major in range(major_count):
        index = (major >> 1) * major_mult + (major & 1)
        a = 0; b = 0
        for _ in range(minor_count):
            t = src[index]
            if not isinstance(t, int): t = ord(t)
            index += minor_inc
            if index >= size: index -= size
            a ^= t; b ^= t; a = ECC_F[a]
        a = ECC_B[ECC_F[a] ^ b]
        dest[major] = a
        dest[major + major_count] = a ^ b
    return dest

def regen_sector(sec):
    if len(sec) != 2352: raise RuntimeError("Bad raw sector length")
    s = bytearray(sec)
    if s[15] != 2: raise RuntimeError("Expected MODE2 sector")
    if s[18] & 0x20: raise RuntimeError("Unexpected Mode2/Form2 sector")
    if s[16:20] != s[20:24]: raise RuntimeError("Mode2 subheader copies do not match")
    s[2072:2076] = struct.pack("<I", edc_compute(s[16:2072]))
    hdr = bytes(s[12:16]); s[12:16] = b"\0\0\0\0"
    s[2076:2248] = ecc_compute(s[12:2076], 86, 24, 2, 86)
    s[2248:2352] = ecc_compute(s[12:2248], 52, 43, 86, 88)
    s[12:16] = hdr
    return bytes(s)

def sha1_bytes(data):
    h=hashlib.sha1(); h.update(data); return h.hexdigest()

def sha1_file(path):
    h=hashlib.sha1()
    with open(path,"rb") as f:
        while True:
            c=f.read(8*1024*1024)
            if not c: break
            h.update(c)
    return h.hexdigest()

def read_iso_file(rawf, extent, size):
    out=bytearray(); remaining=size; sector=extent
    while remaining:
        n=min(2048,remaining)
        rawf.seek(sector*2352+24); c=rawf.read(n)
        if len(c)!=n: raise RuntimeError("Short read at raw sector %d"%sector)
        out.extend(c); remaining-=n; sector+=1
    return out

def write_changed_iso_file(rawf, extent, original, modified, changed):
    if len(original)!=len(modified): raise RuntimeError("File size changed")
    total=len(original)
    for i in range((total+2047)//2048):
        a=i*2048; b=min(a+2048,total)
        if original[a:b]==modified[a:b]: continue
        sec=extent+i
        rawf.seek(sec*2352); raw=bytearray(rawf.read(2352))
        if len(raw)!=2352: raise RuntimeError("Short sector %d"%sec)
        if raw[15]!=2 or (raw[18]&0x20): raise RuntimeError("Sector %d not MODE2/Form1"%sec)
        raw[24:24+(b-a)] = modified[a:b]
        rawf.seek(sec*2352); rawf.write(bytes(raw)); changed.add(sec)

def bdp_checksum(block):
    s=(sum(block[:4])+sum(block[8:]))&0xFFFF
    return (((~s)&0xFFFF)<<16)|s

def parse_bdp_entries(prg):
    magic, stored, toc_size, count = struct.unpack_from("<IIII", prg, 0)
    if magic != 0x10F0 or bdp_checksum(prg) != stored:
        raise RuntimeError("PRGPACK top checksum verification failed")
    payload_base=8+toc_size
    entries=[]
    for i in range(count):
        rel,size=struct.unpack_from("<II",prg,16+i*8)
        start=payload_base+rel; end=start+size; block=prg[start:end]
        if len(block)!=size or struct.unpack_from("<I",block,0)[0]!=0x10F0:
            raise RuntimeError("Bad nested BDP entry %d"%i)
        if bdp_checksum(block)!=struct.unpack_from("<I",block,4)[0]:
            raise RuntimeError("Nested BDP checksum mismatch at %d"%i)
        entries.append((i,start,end))
    return entries

def count_pair(blob, pair):
    n=0; start=0
    while True:
        p=blob.find(pair,start)
        if p<0: return n
        n+=1; start=p+1

def valid_codes():
    for a,b in VALID_CODE_RANGES:
        for code in range(a,b+1):
            yield code

def mapping_value(slps, code):
    idx=code & 0x7FFF
    off=MAPPING_OFF + idx*2
    if off+2>len(slps): return None
    return struct.unpack_from("<H",slps,off)[0]

def make_scan_slps(slps):
    max_idx=max(code & 0x7FFF for code in valid_codes())
    map_end=MAPPING_OFF+(max_idx+1)*2
    return b"".join((
        bytes(slps[:ATLAS_OFF]),
        bytes(slps[ATLAS_OFF+ATLAS_GLYPHS*GLYPH_BYTES:MAPPING_OFF]),
        bytes(slps[map_end:]),
    ))

def choose_slots(slps, prg, count=12):
    slot_codes={i:[] for i in range(ATLAS_GLYPHS)}
    for code in valid_codes():
        g=mapping_value(slps,code)
        if g is not None and g < ATLAS_GLYPHS:
            slot_codes[g].append(code)
    scan_slps=make_scan_slps(slps)
    scores=[]
    for slot in range(ATLAS_GLYPHS):
        if slot in PROTECTED_SLOTS: continue
        codes=slot_codes[slot]
        occ=0
        for code in codes:
            pair=bytes([(code>>8)&0xFF, code&0xFF])
            occ += count_pair(prg,pair)
            occ += count_pair(scan_slps,pair)
        mapped_penalty = 0 if not codes else 1
        scores.append((occ,mapped_penalty,len(codes),-slot,slot,codes))
    scores.sort()
    chosen=scores[:count]
    if len(chosen)<count: raise RuntimeError("Could not select %d slots"%count)
    return chosen

def setpix(grid,x,y,v=7):
    if 0<=x<12 and 0<=y<12: grid[y][x]=v

def draw_rows(grid, rows, x0, y0, v=7):
    for y,row in enumerate(rows):
        for x,ch in enumerate(row):
            if ch!=".": setpix(grid,x0+x,y0+y,v)

def base_pattern(letter):
    if letter=="A": return [".###.","#...#","#...#","#####","#...#","#...#","#...#"]
    if letter=="E": return ["#####","#....","#....","####.","#....","#....","#####"]
    if letter=="O": return [".###.","#...#","#...#","#...#","#...#","#...#",".###."]
    raise ValueError(letter)

def add_circumflex(g):
    for x,y in [(4,2),(5,1),(6,2)]: setpix(g,x,y)

def add_acute(g):
    for x,y in [(7,0),(6,1)]: setpix(g,x,y)

def add_hook(g):
    for x,y in [(7,0),(8,0),(8,1),(7,2)]: setpix(g,x,y)

def add_breve(g):
    for x,y in [(4,1),(5,2),(6,2),(7,1)]: setpix(g,x,y)

def add_tilde(g):
    for x,y in [(3,1),(4,0),(5,1),(6,1),(7,0),(8,1)]: setpix(g,x,y)

def make_glyph(label):
    g=[[0]*12 for _ in range(12)]
    base=label[0] if label[0] in "AEO" else "A"
    draw_rows(g,base_pattern(base),3,4,7)
    if label in ("Â","Ấ","Ê","Ế","Ể","Ô","Ố","Ỗ"): add_circumflex(g)
    if label in ("Ấ","Ế","Ố"): add_acute(g)
    if label=="Ể": add_hook(g)
    if label=="Ẳ":
        add_breve(g); add_hook(g)
    if label=="Ỗ": add_tilde(g)
    out=bytearray()
    for row in g:
        for x in range(0,12,2):
            out.append((row[x]&0xF)|((row[x+1]&0xF)<<4))
    if len(out)!=72: raise AssertionError(len(out))
    return bytes(out)

def code_bytes(codes):
    out=bytearray()
    for c in codes: out.extend([(c>>8)&0xFF,c&0xFF])
    return bytes(out)

def main():
    here=os.path.dirname(os.path.abspath(__file__))
    src=os.path.abspath(sys.argv[1]) if len(sys.argv)>=2 else os.path.join(here,"GaiaMaster - Kamigami no Board Game (Japan).bin")
    if not os.path.isfile(src):
        print("[ERROR] CLEAN BIN not found:"); print(src); return 2
    got=sha1_file(src).lower(); print("Input BIN SHA1:",got)
    if got!=EXPECTED_BIN_SHA1:
        print("[ERROR] Wrong/modified BIN. Expected CLEAN:",EXPECTED_BIN_SHA1); return 3
    with open(src,"rb") as rf:
        slps=read_iso_file(rf,SLPS_EXTENT,SLPS_SIZE)
        prg=read_iso_file(rf,PRG_EXTENT,PRG_SIZE)
    if sha1_bytes(slps)!=EXPECTED_SLPS_SHA1: raise RuntimeError("SLPS SHA1 mismatch")
    if sha1_bytes(prg)!=EXPECTED_PRG_SHA1: raise RuntimeError("PRGPACK SHA1 mismatch")

    entries=parse_bdp_entries(prg)
    owner=[e for e in entries if e[1] <= PRG_TEST_OFF < e[2]]
    if len(owner)!=1 or owner[0][0]!=EXPECTED_OWNER_ENTRY:
        raise RuntimeError("Character Select text ownership mismatch: %r"%(owner,))
    if PRG_TEST_OFF+24>owner[0][2]: raise RuntimeError("Test text crosses owner entry")

    facts=[(0x8273,481),(0x8264,466),(0x8272,480),(0x889F,0)]
    for code,exp in facts:
        gotv=mapping_value(slps,code)
        if gotv!=exp: raise RuntimeError("Mapping fact mismatch %04X: %r != %r"%(code,gotv,exp))

    choices=choose_slots(slps,prg,12)
    slots=[x[4] for x in choices]
    slps_new=bytearray(slps); prg_new=bytearray(prg)
    report=[]
    report.append("GAIA MASTER 0.6.5.3 MAPPING-ONLY NATIVE-CELL PROOF BUILD REPORT")
    report.append("="*78)
    report.append("NO CODE HOOK / NO POINTER REDIRECT / NATIVE 12x12 72-byte 4bpp")
    report.append("")
    report.append("Selected atlas slots:")
    for i,(score,label,code,slot) in enumerate(zip(choices,TEST_LABELS,TEST_CODES,slots)):
        occ,mapped_penalty,numcodes,negslot,slot2,codes=score
        report.append("  %02d %-2s code=%04X -> slot=%d  prior_codes=%d  static_text_hits=%d"%(i,label,code,slot,len(codes),occ))

    for label,code,slot in zip(TEST_LABELS,TEST_CODES,slots):
        goff=ATLAS_OFF+slot*GLYPH_BYTES
        old=bytes(slps_new[goff:goff+GLYPH_BYTES])
        slps_new[goff:goff+GLYPH_BYTES]=make_glyph(label)
        moff=MAPPING_OFF+((code&0x7FFF)*2)
        oldmap=struct.unpack_from("<H",slps_new,moff)[0]
        struct.pack_into("<H",slps_new,moff,slot)
        report.append("  patch %-2s: map SLPS+0x%06X %d->%d ; glyph SLPS+0x%06X old_sha1=%s"%(label,moff,oldmap,slot,goff,sha1_bytes(old)[:12]))

    old_text=bytes(prg_new[PRG_TEST_OFF:PRG_TEST_OFF+24])
    prg_new[PRG_TEST_OFF:PRG_TEST_OFF+24]=code_bytes(TEST_CODES)
    report.append("")
    report.append("Character Select test:")
    report.append("  PRGPACK+0x%X owner entry %d"%(PRG_TEST_OFF,EXPECTED_OWNER_ENTRY))
    report.append("  old24=%s"%old_text.hex().upper())
    report.append("  new24=%s"%code_bytes(TEST_CODES).hex().upper())
    report.append("  expected visual: A Â Ấ Ẳ E Ê Ế Ể O Ô Ố Ỗ")

    idx,start,end=owner[0]
    block=bytearray(prg_new[start:end])
    struct.pack_into("<I",prg_new,start+4,bdp_checksum(block))
    struct.pack_into("<I",prg_new,4,bdp_checksum(prg_new))
    if bdp_checksum(prg_new)!=struct.unpack_from("<I",prg_new,4)[0]: raise RuntimeError("Top BDP checksum rebuild failed")
    block2=bytes(prg_new[start:end])
    if bdp_checksum(block2)!=struct.unpack_from("<I",block2,4)[0]: raise RuntimeError("Nested BDP checksum rebuild failed")

    stem=os.path.splitext(src)[0]
    out_bin=stem+" [VI 0.6.5.3 MAPPING ONLY].bin"
    out_cue=stem+" [VI 0.6.5.3 MAPPING ONLY].cue"
    out_report=stem+" [VI 0.6.5.3 MAPPING ONLY].txt"
    shutil.copyfile(src,out_bin)
    changed=set()
    with open(out_bin,"r+b") as wf:
        write_changed_iso_file(wf,SLPS_EXTENT,slps,bytes(slps_new),changed)
        write_changed_iso_file(wf,PRG_EXTENT,prg,bytes(prg_new),changed)
        for sec in sorted(changed):
            wf.seek(sec*2352); raw=wf.read(2352)
            wf.seek(sec*2352); wf.write(regen_sector(raw))
    with open(out_cue,"w",encoding="ascii") as f:
        f.write('FILE "'+os.path.basename(out_bin)+'" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
    report.append("")
    report.append("Changed raw sectors: %d"%len(changed))
    report.append("Output BIN SHA1: %s"%sha1_file(out_bin))
    report.append("RESULT: BUILD SUCCESS")
    with open(out_report,"w",encoding="utf-8") as f: f.write("\n".join(report)+"\n")

    print("\n"+"="*68)
    print("[OK] GAIA MASTER 0.6.5.3 MAPPING-ONLY NATIVE-CELL BUILD SUCCESS")
    print("="*68)
    print("Selected slots:",slots)
    print("Expected visual: A Â Ấ Ẳ E Ê Ế Ể O Ô Ố Ỗ")
    print("Changed raw sectors:",len(changed))
    print("Output BIN:",out_bin)
    print("Output SHA1:",sha1_file(out_bin))
    print("Report:",out_report)
    return 0

if __name__=="__main__":
    try: sys.exit(main())
    except Exception as e:
        print("[ERROR]",repr(e)); sys.exit(9)

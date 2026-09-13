#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function
import os, sys, shutil, struct
import build_gaia_0653_mapping_only as m

TEST_CODES = list(range(0x889F, 0x88AB))
TEST_LABELS = ["A", "Â", "Ấ", "Ẳ", "E", "Ê", "Ế", "Ể", "O", "Ô", "Ố", "Ỗ"]
BASE_CODES = {"A": 0x8260, "E": 0x8264, "O": 0x826E}
A_FAMILY = {"A", "Â", "Ấ", "Ẳ"}
E_FAMILY = {"E", "Ê", "Ế", "Ể"}
O_FAMILY = {"O", "Ô", "Ố", "Ỗ"}


def family(label):
    if label in A_FAMILY: return "A"
    if label in E_FAMILY: return "E"
    if label in O_FAMILY: return "O"
    raise ValueError("Unknown label family: %r" % label)


def decode_glyph(raw):
    if len(raw) != 72: raise ValueError("glyph must be 72 bytes")
    g = [[0]*12 for _ in range(12)]
    p = 0
    for y in range(12):
        for x in range(0,12,2):
            b = raw[p]; p += 1
            g[y][x] = b & 0x0F
            g[y][x+1] = (b >> 4) & 0x0F
    return g


def encode_glyph(g):
    out = bytearray()
    for y in range(12):
        for x in range(0,12,2):
            out.append((g[y][x] & 0x0F) | ((g[y][x+1] & 0x0F) << 4))
    if len(out) != 72: raise AssertionError(len(out))
    return bytes(out)


def bbox(g):
    pts = [(x,y) for y in range(12) for x in range(12) if g[y][x] != 0]
    if not pts: return None
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def histogram(g):
    h = {i:0 for i in range(16)}
    for row in g:
        for v in row: h[v] += 1
    return h


def choose_foreground(g):
    h = histogram(g)
    nonzero = [(count, idx) for idx,count in h.items() if idx != 0 and count]
    if not nonzero: raise RuntimeError("native base glyph has no nonzero pixels")
    nonzero.sort(reverse=True)
    return nonzero[0][1], h


def shift_down(g, n):
    if n <= 0: return [row[:] for row in g]
    out = [[0]*12 for _ in range(12)]
    for y in range(12-n): out[y+n] = g[y][:]
    return out


def reserve_top(g, rows=3):
    b = bbox(g)
    if b is None: return [row[:] for row in g], 0
    x0,y0,x1,y1 = b
    if y0 >= rows: return [row[:] for row in g], 0
    n = min(rows-y0, 11-y1)
    return shift_down(g,n), n


def put(g, x, y, v):
    if 0 <= x < 12 and 0 <= y < 12: g[y][x] = v


def add_marks(g, label, fg):
    if label in ("A", "E", "O"): return g
    b = bbox(g)
    if b is None: return g
    x0,y0,x1,y1 = b; cx = (x0+x1)//2
    if label in ("Â", "Ê", "Ô"):
        pts=[(cx-1,1),(cx,0),(cx+1,1)]
    elif label in ("Ấ", "Ế", "Ố"):
        pts=[(cx-1,2),(cx,1),(cx+1,2),(cx+2,0),(cx+1,1)]
    elif label == "Ẳ":
        pts=[(cx-2,1),(cx-1,2),(cx,2),(cx+1,1),(cx+2,0),(cx+3,0),(cx+3,1),(cx+2,2)]
    elif label == "Ể":
        pts=[(cx-1,1),(cx,0),(cx+1,1),(cx+2,0),(cx+3,0),(cx+3,1),(cx+2,2)]
    elif label == "Ỗ":
        pts=[(cx-1,2),(cx,1),(cx+1,2),(cx-3,0),(cx-2,0),(cx-1,1),(cx,1),(cx+1,0),(cx+2,0)]
    else: raise ValueError(label)
    for x,y in pts: put(g,x,y,fg)
    return g


def native_base(slps, letter):
    code = BASE_CODES[letter]
    slot = m.mapping_value(slps, code)
    if slot is None or not (0 <= slot < m.ATLAS_GLYPHS):
        raise RuntimeError("native %s mapping invalid: code=%04X slot=%r"%(letter,code,slot))
    off = m.ATLAS_OFF + slot*m.GLYPH_BYTES
    raw = bytes(slps[off:off+m.GLYPH_BYTES])
    g = decode_glyph(raw)
    fg,h = choose_foreground(g)
    return code,slot,raw,g,fg,h


def make_glyph(slps, label, bases):
    letter = family(label)
    code,slot,raw,base_grid,fg,h = bases[letter]
    if label == letter: return raw, 0
    g, shifted = reserve_top(base_grid,3)
    return encode_glyph(add_marks(g,label,fg)), shifted


def main():
    here=os.path.dirname(os.path.abspath(__file__))
    src=os.path.abspath(sys.argv[1]) if len(sys.argv)>=2 else os.path.join(here,"GaiaMaster - Kamigami no Board Game (Japan).bin")
    if not os.path.isfile(src): print("[ERROR] CLEAN BIN not found:"); print(src); return 2
    got=m.sha1_file(src).lower(); print("Input BIN SHA1:",got)
    if got!=m.EXPECTED_BIN_SHA1: print("[ERROR] Wrong/modified BIN. Expected CLEAN:",m.EXPECTED_BIN_SHA1); return 3
    with open(src,"rb") as rf:
        slps=m.read_iso_file(rf,m.SLPS_EXTENT,m.SLPS_SIZE)
        prg=m.read_iso_file(rf,m.PRG_EXTENT,m.PRG_SIZE)
    if m.sha1_bytes(slps)!=m.EXPECTED_SLPS_SHA1: raise RuntimeError("SLPS SHA1 mismatch")
    if m.sha1_bytes(prg)!=m.EXPECTED_PRG_SHA1: raise RuntimeError("PRGPACK SHA1 mismatch")
    entries=m.parse_bdp_entries(prg)
    owner=[e for e in entries if e[1] <= m.PRG_TEST_OFF < e[2]]
    if len(owner)!=1 or owner[0][0]!=m.EXPECTED_OWNER_ENTRY: raise RuntimeError("Character Select text ownership mismatch: %r"%(owner,))
    if m.PRG_TEST_OFF+24>owner[0][2]: raise RuntimeError("Test text crosses owner entry")
    for code,exp in [(0x8273,481),(0x8264,466),(0x8272,480),(0x889F,0)]:
        gotv=m.mapping_value(slps,code)
        if gotv!=exp: raise RuntimeError("Mapping fact mismatch %04X: %r != %r"%(code,gotv,exp))
    bases={letter:native_base(slps,letter) for letter in ("A","E","O")}
    old_protected=set(m.PROTECTED_SLOTS); m.PROTECTED_SLOTS.update(v[1] for v in bases.values())
    try: choices=m.choose_slots(slps,prg,12)
    finally: m.PROTECTED_SLOTS.clear(); m.PROTECTED_SLOTS.update(old_protected)
    slots=[x[4] for x in choices]
    slps_new=bytearray(slps); prg_new=bytearray(prg); report=[]
    report += ["GAIA MASTER 0.6.5.4 NATIVE-BASE STYLE PROOF BUILD REPORT","="*78,
               "MAPPING-ONLY / NO CODE HOOK / NO POINTER REDIRECT / NATIVE 12x12 72-byte 4bpp","",
               "0.6.5.3 diagnosis:","  - hardcoded palette index 7 for every custom pixel",
               "  - Unicode family bug: accented Ê/Ế/Ể/Ô/Ố/Ỗ fell back to A base",
               "0.6.5.4 fix:","  - copy native full-width A/E/O glyphs as the base",
               "  - explicit A/E/O family mapping","  - derive accent color from native glyph's dominant nonzero palette index","",
               "Native source glyphs:"]
    for letter in ("A","E","O"):
        code,slot,raw,g,fg,h=bases[letter]; nz=" ".join("%X:%d"%(i,h[i]) for i in range(1,16) if h[i])
        report.append("  %s code=%04X -> slot=%d bbox=%r foreground=%X hist={%s}"%(letter,code,slot,bbox(g),fg,nz))
    report.append(""); report.append("Selected destination slots:")
    for i,(score,label,code,slot) in enumerate(zip(choices,TEST_LABELS,TEST_CODES,slots)):
        occ,mapped_penalty,numcodes,negslot,slot2,codes=score
        report.append("  %02d %-2s code=%04X -> slot=%d prior_codes=%d static_text_hits=%d"%(i,label,code,slot,len(codes),occ))
    for label,code,slot in zip(TEST_LABELS,TEST_CODES,slots):
        goff=m.ATLAS_OFF+slot*m.GLYPH_BYTES; old=bytes(slps_new[goff:goff+m.GLYPH_BYTES]); glyph,shifted=make_glyph(slps,label,bases)
        slps_new[goff:goff+m.GLYPH_BYTES]=glyph; moff=m.MAPPING_OFF+((code&0x7FFF)*2); oldmap=struct.unpack_from("<H",slps_new,moff)[0]
        struct.pack_into("<H",slps_new,moff,slot)
        report.append("  patch %-2s family=%s shift=%d map SLPS+0x%06X %d->%d glyph SLPS+0x%06X old_sha1=%s"%(label,family(label),shifted,moff,oldmap,slot,goff,m.sha1_bytes(old)[:12]))
    old_text=bytes(prg_new[m.PRG_TEST_OFF:m.PRG_TEST_OFF+24]); prg_new[m.PRG_TEST_OFF:m.PRG_TEST_OFF+24]=m.code_bytes(TEST_CODES)
    report += ["","Character Select test:","  PRGPACK+0x%X owner entry %d"%(m.PRG_TEST_OFF,m.EXPECTED_OWNER_ENTRY),
               "  old24=%s"%old_text.hex().upper(),"  new24=%s"%m.code_bytes(TEST_CODES).hex().upper(),
               "  expected visual: A Â Ấ Ẳ E Ê Ế Ể O Ô Ố Ỗ","  plain A/E/O are byte-for-byte native controls"]
    idx,start,end=owner[0]; block=bytearray(prg_new[start:end]); struct.pack_into("<I",prg_new,start+4,m.bdp_checksum(block)); struct.pack_into("<I",prg_new,4,m.bdp_checksum(prg_new))
    if m.bdp_checksum(prg_new)!=struct.unpack_from("<I",prg_new,4)[0]: raise RuntimeError("Top BDP checksum rebuild failed")
    block2=bytes(prg_new[start:end]);
    if m.bdp_checksum(block2)!=struct.unpack_from("<I",block2,4)[0]: raise RuntimeError("Nested BDP checksum rebuild failed")
    stem=os.path.splitext(src)[0]; out_bin=stem+" [VI 0.6.5.4 NATIVE BASE].bin"; out_cue=stem+" [VI 0.6.5.4 NATIVE BASE].cue"; out_report=stem+" [VI 0.6.5.4 NATIVE BASE].txt"
    shutil.copyfile(src,out_bin); changed=set()
    with open(out_bin,"r+b") as wf:
        m.write_changed_iso_file(wf,m.SLPS_EXTENT,slps,bytes(slps_new),changed); m.write_changed_iso_file(wf,m.PRG_EXTENT,prg,bytes(prg_new),changed)
        for sec in sorted(changed): wf.seek(sec*2352); raw=wf.read(2352); wf.seek(sec*2352); wf.write(m.regen_sector(raw))
    with open(out_cue,"w",encoding="ascii") as f: f.write('FILE "'+os.path.basename(out_bin)+'" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
    report += ["","Changed raw sectors: %d"%len(changed),"Output BIN SHA1: %s"%m.sha1_file(out_bin),"RESULT: BUILD SUCCESS"]
    with open(out_report,"w",encoding="utf-8") as f: f.write("\n".join(report)+"\n")
    print("\n"+"="*68); print("[OK] GAIA MASTER 0.6.5.4 NATIVE-BASE STYLE BUILD SUCCESS"); print("="*68)
    for letter in ("A","E","O"):
        code,slot,raw,g,fg,h=bases[letter]; print("Native %s: code %04X -> slot %d, foreground index %X"%(letter,code,slot,fg))
    print("Selected slots:",slots); print("Expected visual: A Â Ấ Ẳ E Ê Ế Ể O Ô Ố Ỗ"); print("Output BIN:",out_bin); print("Output SHA1:",m.sha1_file(out_bin)); print("Report:",out_report); return 0

if __name__=="__main__":
    try: sys.exit(main())
    except Exception as e: print("[ERROR]",repr(e)); sys.exit(9)

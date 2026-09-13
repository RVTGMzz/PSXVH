#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gaia Master Production Capacity Scanner 0.1
READ ONLY. No ROM patch. No emulator boot.

Purpose:
- test whether the proven 12x12 mapping-only architecture can support the
  FULL Vietnamese precomposed repertoire in one deterministic codepage;
- worst-case target = 134 custom Vietnamese glyphs:
    67 lowercase + 67 uppercase,
  excluding plain ASCII A/E/I/O/U/Y/a/e/i/o/u/y because Gaia can reuse native
  full-width Latin for those;
- count zero-static-hit custom codes;
- count zero-static-hit atlas slots, separating:
    * completely unmapped slots;
    * mapped-but-zero-static-hit slots;
- protect native base glyphs needed to synthesize Vietnamese;
- emit a deterministic proposed Unicode -> code -> slot allocation if capacity
  is sufficient.

This scanner does NOT modify the BIN.
"""

from __future__ import print_function
import hashlib, os, struct, sys, unicodedata

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
VALID_CODE_RANGES = ((0x8140, 0x84BE), (0x8540, 0x9872))
FIXED_PROTECTED = {0, 466, 480, 481}

LOWER_CUSTOM = "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"
UPPER_CUSTOM = LOWER_CUSTOM.upper()
CUSTOM_CHARS = list(LOWER_CUSTOM + UPPER_CUSTOM)
TARGET = len(CUSTOM_CHARS)

if TARGET != 134 or len(set(CUSTOM_CHARS)) != 134:
    raise RuntimeError("Vietnamese repertoire constant is not 134 unique chars")


def sha1_bytes(data):
    h = hashlib.sha1(); h.update(data); return h.hexdigest()


def sha1_file(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        while True:
            b = f.read(8 * 1024 * 1024)
            if not b: break
            h.update(b)
    return h.hexdigest()


def read_iso_file(rawf, extent, size):
    out = bytearray(); remain = size; sec = extent
    while remain:
        n = min(2048, remain)
        rawf.seek(sec * 2352 + 24)
        b = rawf.read(n)
        if len(b) != n: raise RuntimeError("Short read at raw sector %d" % sec)
        out.extend(b); remain -= n; sec += 1
    return bytes(out)


def valid_codes():
    for a, b in VALID_CODE_RANGES:
        for code in range(a, b + 1):
            pair = bytes([(code >> 8) & 0xFF, code & 0xFF])
            try: pair.decode("cp932")
            except Exception: continue
            yield code


def mapping_region_end():
    return MAPPING_OFF + (max(c & 0x7FFF for c in valid_codes()) + 1) * 2


def mapping_value(slps, code):
    off = MAPPING_OFF + ((code & 0x7FFF) * 2)
    if off + 2 > len(slps): return None
    return struct.unpack_from("<H", slps, off)[0]


def count_pair(blob, pair):
    n = 0; p = 0
    while True:
        p = blob.find(pair, p)
        if p < 0: return n
        n += 1; p += 1


def scan_slps_without_font_tables(slps):
    mend = mapping_region_end()
    return b"".join((
        slps[:ATLAS_OFF],
        slps[ATLAS_OFF + ATLAS_GLYPHS * GLYPH_BYTES:MAPPING_OFF],
        slps[mend:],
    ))


def fullwidth_code(ch):
    fw = chr(ord(ch) + 0xFEE0)
    b = fw.encode("cp932")
    if len(b) != 2: raise RuntimeError("Expected 2-byte CP932 for %r" % ch)
    return (b[0] << 8) | b[1]


def source_base(ch):
    if ch in ("đ", "Đ"): return "d" if ch == "đ" else "D"
    nfd = unicodedata.normalize("NFD", ch)
    if not nfd: raise RuntimeError("Cannot decompose %r" % ch)
    base = nfd[0]
    if not (base.isascii() and base.isalpha()):
        raise RuntimeError("Unexpected base for %r -> %r" % (ch, base))
    return base


def protected_base_slots(slps):
    bases = sorted(set(source_base(ch) for ch in CUSTOM_CHARS)); out = {}
    for ch in bases:
        code = fullwidth_code(ch); slot = mapping_value(slps, code)
        if slot is None or not (0 <= slot < ATLAS_GLYPHS):
            raise RuntimeError("Invalid native base %r code=%04X slot=%r" % (ch, code, slot))
        out[ch] = (code, slot)
    return out


def build_code_pool(slps, prg):
    rest = scan_slps_without_font_tables(slps); zero = []; used = []
    for code in valid_codes():
        if code < 0x889F: continue
        pair = bytes([(code >> 8) & 0xFF, code & 0xFF])
        hits = count_pair(prg, pair) + count_pair(rest, pair)
        (zero if hits == 0 else used).append((hits, code))
    zero.sort(key=lambda x: x[1]); used.sort()
    return zero, used


def build_slot_pool(slps, prg, protected):
    rest = scan_slps_without_font_tables(slps)
    slot_codes = {i: [] for i in range(ATLAS_GLYPHS)}
    for code in valid_codes():
        slot = mapping_value(slps, code)
        if slot is not None and 0 <= slot < ATLAS_GLYPHS:
            slot_codes[slot].append(code)
    cache = {}
    def hits_for(code):
        if code not in cache:
            pair = bytes([(code >> 8) & 0xFF, code & 0xFF])
            cache[code] = count_pair(prg, pair) + count_pair(rest, pair)
        return cache[code]
    zero_unmapped = []; zero_mapped = []; nonzero = []
    for slot in range(ATLAS_GLYPHS):
        if slot in protected: continue
        codes = slot_codes[slot]; occ = sum(hits_for(c) for c in codes)
        rec = {"slot": slot, "codes": codes, "hits": occ}
        if occ == 0:
            (zero_mapped if codes else zero_unmapped).append(rec)
        else: nonzero.append(rec)
    zero_unmapped.sort(key=lambda r: r["slot"])
    zero_mapped.sort(key=lambda r: (len(r["codes"]), r["slot"]))
    return zero_unmapped, zero_mapped, nonzero


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.abspath(sys.argv[1]) if len(sys.argv) >= 2 else os.path.join(here, "GaiaMaster - Kamigami no Board Game (Japan).bin")
    report_path = os.path.join(here, "GaiaMaster_ProductionCapacityScanner_01.txt")
    def save(lines):
        with open(report_path, "w", encoding="utf-8") as f: f.write("\n".join(lines) + "\n")
    if not os.path.isfile(src):
        save(["GAIA MASTER PRODUCTION CAPACITY SCANNER 0.1", "[BLOCKED] CLEAN BIN not found:", src])
        print("[ERROR] CLEAN BIN not found."); print("Report:", report_path); return 2
    got = sha1_file(src).lower()
    if got != EXPECTED_BIN_SHA1:
        save(["GAIA MASTER PRODUCTION CAPACITY SCANNER 0.1", "[BLOCKED] Wrong/modified BIN.", "Got: %s" % got, "Expected: %s" % EXPECTED_BIN_SHA1])
        print("[ERROR] CLEAN BIN required."); print("Report:", report_path); return 3
    with open(src, "rb") as rf:
        slps = read_iso_file(rf, SLPS_EXTENT, SLPS_SIZE); prg = read_iso_file(rf, PRG_EXTENT, PRG_SIZE)
    if sha1_bytes(slps) != EXPECTED_SLPS_SHA1: raise RuntimeError("SLPS SHA1 mismatch")
    if sha1_bytes(prg) != EXPECTED_PRG_SHA1: raise RuntimeError("PRGPACK SHA1 mismatch")
    for code, expected in [(0x8273,481),(0x8264,466),(0x8272,480),(0x889F,0)]:
        if mapping_value(slps, code) != expected: raise RuntimeError("Mapping fact mismatch %04X" % code)
    bases = protected_base_slots(slps)
    protected = set(FIXED_PROTECTED); protected.update(slot for code, slot in bases.values())
    zero_codes, used_codes = build_code_pool(slps, prg)
    zero_unmapped, zero_mapped, nonzero = build_slot_pool(slps, prg, protected)
    all_zero = zero_unmapped + zero_mapped
    code_pass = len(zero_codes) >= TARGET; slot_pass = len(all_zero) >= TARGET
    strong = len(zero_unmapped) >= TARGET; overall = code_pass and slot_pass
    L=[]; ap=L.append
    ap("GAIA MASTER PRODUCTION CAPACITY SCANNER 0.1"); ap("="*92)
    ap("READ ONLY - KHONG SUA ROM - KHONG BOOT GAME"); ap("")
    ap("BIN SHA1   : %s" % got); ap("SLPS SHA1  : %s" % sha1_bytes(slps)); ap("PRG SHA1   : %s" % sha1_bytes(prg)); ap("")
    ap("ARCHITECTURE LOCK"); ap("-"*92)
    ap("production font : native 12x12 / 72-byte / 4bpp")
    ap("routing         : static mapping data only")
    ap("spacing         : keep 0.6.6.1 full-width behavior for now")
    ap("runtime hooks   : NONE"); ap("pointer redirect: NONE"); ap("12x16: REJECTED"); ap("6x12 narrow: RETIRED after 0.6.6.2c runtime failure"); ap("")
    ap("WORST-CASE VIETNAMESE REPERTOIRE"); ap("-"*92)
    ap("custom lowercase chars : %d" % len(LOWER_CUSTOM)); ap("custom uppercase chars : %d" % len(UPPER_CUSTOM)); ap("TOTAL custom glyphs    : %d" % TARGET)
    ap("lower: %s" % LOWER_CUSTOM); ap("upper: %s" % UPPER_CUSTOM); ap("")
    ap("PROTECTED NATIVE BASE GLYPHS"); ap("-"*92)
    for ch in sorted(bases):
        code,slot=bases[ch]; ap("%r -> code %04X -> slot %d" % (ch,code,slot))
    ap("Fixed protected slots: %s" % ", ".join(map(str,sorted(FIXED_PROTECTED)))); ap("Total unique protected slots: %d" % len(protected)); ap("")
    ap("CUSTOM CODE CAPACITY"); ap("-"*92)
    ap("zero-static-hit codes >=0x889F : %d" % len(zero_codes)); ap("needed                         : %d" % TARGET); ap("code gate: %s" % ("PASS" if code_pass else "FAIL")); ap("")
    ap("ATLAS SLOT CAPACITY"); ap("-"*92)
    ap("zero-hit completely unmapped       : %d" % len(zero_unmapped)); ap("zero-hit mapped but static-unused    : %d" % len(zero_mapped)); ap("total zero-static-hit allocatable    : %d" % len(all_zero)); ap("needed                               : %d" % TARGET)
    ap("strong gate (unmapped only): %s" % ("PASS" if strong else "NO")); ap("normal gate: %s" % ("PASS" if slot_pass else "FAIL")); ap("")
    ap("FINAL STATIC CAPACITY VERDICT"); ap("-"*92)
    if overall:
        ap("[PASS] Full 134-glyph Vietnamese codepage fits the proven 12x12 mapping-only architecture.")
        ap("[STRONG PASS] All 134 glyphs can use unmapped slots." if strong else "[PASS WITH MIXED SLOTS] mapped-but-zero-hit slots are required.")
        ap(""); ap("DETERMINISTIC PROPOSED CODEPAGE"); ap("-"*92)
        chosen_codes=[c for _,c in zero_codes[:TARGET]]; chosen_slots=[r["slot"] for r in all_zero[:TARGET]]
        for i,(ch,code,slot) in enumerate(zip(CUSTOM_CHARS,chosen_codes,chosen_slots)):
            ap("%03d U+%04X %-2s base=%s -> code=%04X -> slot=%d" % (i,ord(ch),ch,source_base(ch),code,slot))
    else:
        if not code_pass: ap("[FAIL] Not enough zero-hit custom codes for all 134 glyphs.")
        if not slot_pass: ap("[FAIL] Not enough zero-hit atlas slots for all 134 glyphs.")
        ap("NEXT: inventory exact vi_full chars and allocate the smaller real corpus.")
    ap(""); ap("FIRST 40 ZERO-HIT CUSTOM CODES"); ap("-"*92)
    for _,code in zero_codes[:40]:
        pair=bytes([(code>>8)&0xFF,code&0xFF]); ap("%04X %s %r" % (code,pair.hex().upper(),pair.decode("cp932",errors="replace")))
    ap(""); ap("FIRST 80 COMPLETELY UNMAPPED ZERO-HIT SLOTS"); ap("-"*92); ap(" ".join(str(r["slot"]) for r in zero_unmapped[:80]) or "<none>")
    ap(""); ap("FIRST 80 MAPPED-BUT-ZERO-HIT SLOTS"); ap("-"*92)
    for r in zero_mapped[:80]: ap("slot=%d mapped_codes=%s" % (r["slot"],",".join("%04X"%c for c in r["codes"]) or "<none>"))
    ap(""); ap("NO RUNTIME BUILD WAS CREATED."); ap("If PASS, next step is a production codepage builder + multi-string translation proof.")
    save(L)
    print("[OK] READ-ONLY production capacity scan complete.")
    print("Target custom glyphs:",TARGET); print("Zero-hit custom codes:",len(zero_codes)); print("Zero-hit atlas slots :",len(all_zero)); print("Unmapped zero slots  :",len(zero_unmapped)); print("Verdict              :","PASS" if overall else "FAIL"); print("Report:",report_path)
    return 0


if __name__ == "__main__":
    try: sys.exit(main())
    except Exception as e:
        print("[ERROR]",repr(e)); sys.exit(9)

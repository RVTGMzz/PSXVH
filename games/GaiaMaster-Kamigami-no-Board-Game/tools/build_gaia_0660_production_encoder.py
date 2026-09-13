#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function
import os, sys, shutil, struct, unicodedata
import build_gaia_0653_mapping_only as m
import build_gaia_0654_native_base as n
import build_gaia_0655_accent_safe as a

TEST_TEXT = "Chọn tướng"
FIELD_BYTES = 24
KNOWN_SHADOW_INDEX = 7


def fullwidth_code(ch):
    if ch == " ":
        fw = "\u3000"
    elif 0x21 <= ord(ch) <= 0x7E:
        fw = chr(ord(ch) + 0xFEE0)
    else:
        raise ValueError("No native fullwidth mapping for %r" % ch)
    b = fw.encode("cp932")
    if len(b) != 2:
        raise RuntimeError("Expected 2-byte CP932 for %r" % fw)
    return (b[0] << 8) | b[1]


def native_base(slps, letter):
    code = fullwidth_code(letter)
    slot = m.mapping_value(slps, code)
    if slot is None or not (0 <= slot < m.ATLAS_GLYPHS):
        raise RuntimeError("Native base mapping invalid: %s %04X -> %r" % (letter, code, slot))
    off = m.ATLAS_OFF + slot * m.GLYPH_BYTES
    raw = bytes(slps[off:off + m.GLYPH_BYTES])
    return code, slot, raw, n.decode_glyph(raw)


def custom_chars(text):
    out = []
    for ch in text:
        if ch == " " or (0x21 <= ord(ch) <= 0x7E):
            continue
        if ch not in out:
            out.append(ch)
    return out


def scan_slps_without_font(slps):
    max_idx = max(code & 0x7FFF for code in m.valid_codes())
    map_end = m.MAPPING_OFF + (max_idx + 1) * 2
    return b"".join((
        bytes(slps[:m.ATLAS_OFF]),
        bytes(slps[m.ATLAS_OFF + m.ATLAS_GLYPHS*m.GLYPH_BYTES:m.MAPPING_OFF]),
        bytes(slps[map_end:]),
    ))


def safe_codes(slps, prg, need):
    scan_slps = scan_slps_without_font(slps)
    out = []
    for code in m.valid_codes():
        if code < 0x889F:
            continue
        pair = bytes([(code >> 8) & 0xFF, code & 0xFF])
        try:
            pair.decode("cp932")
        except Exception:
            continue
        if m.count_pair(prg, pair) + m.count_pair(scan_slps, pair) == 0:
            out.append(code)
            if len(out) == need:
                return out
    raise RuntimeError("Not enough zero-static-hit custom codes: need %d found %d" % (need, len(out)))


def compress_body(g, y0=2, height=8):
    b = n.bbox(g)
    if b is None:
        raise RuntimeError("Empty native base glyph")
    x0, sy0, x1, sy1 = b
    src_h = sy1 - sy0 + 1
    out = [[0]*12 for _ in range(12)]
    for dy in range(height):
        sy = sy0 if height == 1 else sy0 + int(round(dy * (src_h - 1) / float(height - 1)))
        out[y0 + dy] = g[sy][:]
    return out


def decompose(ch):
    if ch in ("đ", "Đ"):
        return ("d" if ch == "đ" else "D"), ["stroke"]
    d = unicodedata.normalize("NFD", ch)
    if not d:
        raise ValueError(ch)
    return d[0], list(d[1:])


def make_vi_glyph(slps, ch, cache):
    base, marks = decompose(ch)
    if base not in cache:
        cache[base] = native_base(slps, base)
    code, src_slot, raw, base_grid = cache[base]
    fill, shadow, hist = a.choose_layers(base_grid)
    g = compress_body(base_grid)
    bb = n.bbox(g)
    x0, y0, x1, y1 = bb
    cx = (x0 + x1) // 2

    def dual(points):
        a.draw_dual(g, points, fill, shadow)

    if "\u0306" in marks:  # breve
        dual([(cx-2,1),(cx-1,0),(cx,0),(cx+1,0),(cx+2,1)])
    if "\u0302" in marks:  # circumflex
        dual([(cx-1,1),(cx,0),(cx+1,1)])
    if "\u031B" in marks:  # horn
        hx = min(10, x1 + 1)
        dual([(hx,2),(min(10,hx+1),1)])
    if "stroke" in marks:  # đ / Đ
        dual([(max(0,x0-1),5),(x0,5),(min(11,x0+1),5),(min(11,x0+2),5)])

    if "\u0301" in marks:  # acute
        dual([(cx+1,0),(cx,1)])
    if "\u0300" in marks:  # grave
        dual([(cx-1,0),(cx,1)])
    if "\u0309" in marks:  # hook
        dual([(cx,0),(cx+1,0),(cx+1,1),(cx,1)])
    if "\u0303" in marks:  # tilde
        dual([(cx-2,1),(cx-1,0),(cx,1),(cx+1,1),(cx+2,0)])
    if "\u0323" in marks:  # dot below
        dual([(cx,10)])

    return n.encode_glyph(g), {
        "base": base,
        "native_code": code,
        "native_slot": src_slot,
        "fill": fill,
        "shadow": shadow,
        "marks": ["stroke" if x == "stroke" else "U+%04X" % ord(x) for x in marks],
        "bbox": n.bbox(g),
    }


def encode_text(text, cmap):
    out = bytearray(); details = []
    for ch in text:
        code = cmap[ch] if ch in cmap else fullwidth_code(ch)
        out.extend([(code >> 8) & 0xFF, code & 0xFF])
        details.append((ch, code))
    return bytes(out), details


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.abspath(sys.argv[1]) if len(sys.argv) >= 2 else os.path.join(here, "GaiaMaster - Kamigami no Board Game (Japan).bin")
    if not os.path.isfile(src):
        print("[ERROR] CLEAN BIN not found:"); print(src); return 2
    if m.sha1_file(src).lower() != m.EXPECTED_BIN_SHA1:
        print("[ERROR] Wrong/modified BIN. Expected CLEAN:", m.EXPECTED_BIN_SHA1); return 3

    with open(src, "rb") as rf:
        slps = m.read_iso_file(rf, m.SLPS_EXTENT, m.SLPS_SIZE)
        prg = m.read_iso_file(rf, m.PRG_EXTENT, m.PRG_SIZE)
    if m.sha1_bytes(slps) != m.EXPECTED_SLPS_SHA1: raise RuntimeError("SLPS SHA1 mismatch")
    if m.sha1_bytes(prg) != m.EXPECTED_PRG_SHA1: raise RuntimeError("PRGPACK SHA1 mismatch")

    entries = m.parse_bdp_entries(prg)
    owner = [e for e in entries if e[1] <= m.PRG_TEST_OFF < e[2]]
    if len(owner) != 1 or owner[0][0] != m.EXPECTED_OWNER_ENTRY:
        raise RuntimeError("Character Select ownership mismatch")
    if m.PRG_TEST_OFF + FIELD_BYTES > owner[0][2]:
        raise RuntimeError("Character Select proof field crosses owner entry")

    chars = custom_chars(TEST_TEXT)
    codes = safe_codes(slps, prg, len(chars))

    cache = {}
    protected = set(m.PROTECTED_SLOTS)
    for ch in TEST_TEXT:
        if ch == " ": continue
        base = decompose(ch)[0] if ch in chars else ch
        if base.isascii() and base.isalpha():
            nb = native_base(slps, base)
            cache[base] = nb
            protected.add(nb[1])

    old_protected = set(m.PROTECTED_SLOTS)
    m.PROTECTED_SLOTS.clear(); m.PROTECTED_SLOTS.update(protected)
    try:
        choices = m.choose_slots(slps, prg, len(chars))
    finally:
        m.PROTECTED_SLOTS.clear(); m.PROTECTED_SLOTS.update(old_protected)
    if any(x[0] != 0 for x in choices):
        raise RuntimeError("Refusing production proof: selected atlas slot has static text hits")

    slots = [x[4] for x in choices]
    cmap = dict(zip(chars, codes))
    slps_new = bytearray(slps); prg_new = bytearray(prg)
    report = [
        "GAIA MASTER 0.6.6.0 PRODUCTION ENCODER REAL-TEXT PROOF",
        "="*80,
        "MAPPING-ONLY / NATIVE 12x12 / NO HOOK / NO POINTER REDIRECT",
        "Test text: %s" % TEST_TEXT,
        "Custom chars: %s" % " ".join(chars),
        "",
    ]

    for ch, code, choice in zip(chars, codes, choices):
        slot = choice[4]
        glyph, meta = make_vi_glyph(slps, ch, cache)
        goff = m.ATLAS_OFF + slot*m.GLYPH_BYTES
        old = bytes(slps_new[goff:goff+m.GLYPH_BYTES])
        slps_new[goff:goff+m.GLYPH_BYTES] = glyph
        moff = m.MAPPING_OFF + ((code & 0x7FFF)*2)
        oldmap = struct.unpack_from("<H", slps_new, moff)[0]
        struct.pack_into("<H", slps_new, moff, slot)
        report.append("%s U+%04X code=%04X -> slot=%d oldmap=%d base=%s native=%04X/%d fill=%X shadow=%X marks=%s bbox=%r old_sha1=%s" %
                      (ch, ord(ch), code, slot, oldmap, meta["base"], meta["native_code"], meta["native_slot"], meta["fill"], meta["shadow"], ",".join(meta["marks"]), meta["bbox"], m.sha1_bytes(old)[:12]))

    encoded, details = encode_text(TEST_TEXT, cmap)
    if len(encoded) + 2 > FIELD_BYTES:
        raise RuntimeError("Encoded proof text exceeds 24-byte field")
    field = encoded + b"\x00\x00" + b"\x00"*(FIELD_BYTES-len(encoded)-2)
    old_field = bytes(prg_new[m.PRG_TEST_OFF:m.PRG_TEST_OFF+FIELD_BYTES])
    prg_new[m.PRG_TEST_OFF:m.PRG_TEST_OFF+FIELD_BYTES] = field
    report += ["", "Encoded text:"] + ["%r -> %04X" % x for x in details]
    report += ["old24=%s" % old_field.hex().upper(), "new24=%s" % field.hex().upper(), "expected=%s" % TEST_TEXT]

    idx, start, end = owner[0]
    block = bytearray(prg_new[start:end])
    struct.pack_into("<I", prg_new, start+4, m.bdp_checksum(block))
    struct.pack_into("<I", prg_new, 4, m.bdp_checksum(prg_new))
    if m.bdp_checksum(prg_new) != struct.unpack_from("<I", prg_new, 4)[0]: raise RuntimeError("Top checksum rebuild failed")
    if m.bdp_checksum(bytes(prg_new[start:end])) != struct.unpack_from("<I", prg_new, start+4)[0]: raise RuntimeError("Nested checksum rebuild failed")

    stem = os.path.splitext(src)[0]
    out_bin = stem + " [VI 0.6.6.0 PROD ENCODER].bin"
    out_cue = stem + " [VI 0.6.6.0 PROD ENCODER].cue"
    out_report = stem + " [VI 0.6.6.0 PROD ENCODER].txt"
    shutil.copyfile(src, out_bin); changed = set()
    with open(out_bin, "r+b") as wf:
        m.write_changed_iso_file(wf, m.SLPS_EXTENT, slps, bytes(slps_new), changed)
        m.write_changed_iso_file(wf, m.PRG_EXTENT, prg, bytes(prg_new), changed)
        for sec in sorted(changed):
            wf.seek(sec*2352); raw = wf.read(2352); wf.seek(sec*2352); wf.write(m.regen_sector(raw))
    with open(out_cue, "w", encoding="ascii") as f:
        f.write('FILE "'+os.path.basename(out_bin)+'" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
    report += ["", "Changed raw sectors: %d" % len(changed), "Output BIN SHA1: %s" % m.sha1_file(out_bin), "RESULT: BUILD SUCCESS"]
    with open(out_report, "w", encoding="utf-8") as f: f.write("\n".join(report)+"\n")

    print("[OK] Gaia Master 0.6.6.0 production encoder build success")
    print("Expected Character Select:", TEST_TEXT)
    print("Custom chars:", chars)
    print("Custom codes:", ["%04X" % x for x in codes])
    print("Atlas slots:", slots)
    print("Output:", out_cue)
    print("Report:", out_report)
    return 0


if __name__ == "__main__":
    try: sys.exit(main())
    except Exception as e:
        print("[ERROR]", repr(e)); sys.exit(9)

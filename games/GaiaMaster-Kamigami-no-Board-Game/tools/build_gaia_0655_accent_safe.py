#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function
import os, sys, shutil, struct
import build_gaia_0653_mapping_only as m
import build_gaia_0654_native_base as n

TEST_CODES = list(range(0x889F, 0x88AB))
TEST_LABELS = ["A", "Â", "Ấ", "Ẳ", "E", "Ê", "Ế", "Ể", "O", "Ô", "Ố", "Ỗ"]
BODY_Y0 = 3
BODY_H = 9
KNOWN_SHADOW_INDEX = 7


def choose_layers(g):
    h = n.histogram(g)
    nonzero = [(count, idx) for idx, count in h.items() if idx != 0 and count]
    if not nonzero:
        raise RuntimeError("native glyph has no nonzero pixels")
    nonzero.sort(reverse=True)
    shadow = KNOWN_SHADOW_INDEX if h.get(KNOWN_SHADOW_INDEX, 0) else None
    fill_candidates = [(count, idx) for count, idx in nonzero if idx != shadow]
    fill = fill_candidates[0][1] if fill_candidates else nonzero[0][1]
    if shadow is None:
        shadow_candidates = [(count, idx) for count, idx in nonzero if idx != fill]
        shadow = shadow_candidates[0][1] if shadow_candidates else fill
    return fill, shadow, h


def compress_into_band(g, y0=BODY_Y0, height=BODY_H):
    b = n.bbox(g)
    if b is None:
        return [[0]*12 for _ in range(12)], None, None
    x0, sy0, x1, sy1 = b
    src_h = sy1 - sy0 + 1
    out = [[0]*12 for _ in range(12)]
    if height <= 0 or y0 < 0 or y0 + height > 12:
        raise ValueError("invalid destination band")
    for dy in range(height):
        if height == 1:
            sy = sy0
        else:
            sy = sy0 + int(round(dy * (src_h - 1) / float(height - 1)))
        ty = y0 + dy
        out[ty] = g[sy][:]
    return out, b, n.bbox(out)


def put(g, x, y, v):
    if 0 <= x < 12 and 0 <= y < 12:
        g[y][x] = v


def draw_dual(g, points, fill, shadow):
    if shadow != fill:
        for x, y in points:
            put(g, x+1, y+1, shadow)
    for x, y in points:
        put(g, x, y, fill)


def mark_points(label, cx):
    circumflex = [(cx-1, 2), (cx, 1), (cx+1, 2)]
    acute = [(cx+2, 0), (cx+1, 1)]
    breve = [(cx-2, 1), (cx-1, 2), (cx, 2), (cx+1, 2), (cx+2, 1)]
    hook = [(cx+1, 0), (cx+2, 0), (cx+2, 1), (cx+1, 2)]
    tilde = [(cx-2, 1), (cx-1, 0), (cx, 1), (cx+1, 1), (cx+2, 0)]
    if label in ("Â", "Ê", "Ô"):
        return [circumflex]
    if label in ("Ấ", "Ế", "Ố"):
        return [circumflex, acute]
    if label == "Ẳ":
        return [breve, hook]
    if label == "Ể":
        return [circumflex, hook]
    if label == "Ỗ":
        return [circumflex, tilde]
    if label in ("A", "E", "O"):
        return []
    raise ValueError(label)


def build_glyph(label, bases):
    letter = n.family(label)
    code, slot, raw, base_grid, old_fg, old_hist = bases[letter]
    if label == letter:
        return raw, {
            "mode": "native-control",
            "src_bbox": n.bbox(base_grid),
            "dst_bbox": n.bbox(base_grid),
            "fill": None,
            "shadow": None,
        }
    fill, shadow, hist = choose_layers(base_grid)
    g, src_bbox, dst_bbox = compress_into_band(base_grid, BODY_Y0, BODY_H)
    if dst_bbox is None:
        raise RuntimeError("compressed base is empty")
    cx = (dst_bbox[0] + dst_bbox[2]) // 2
    for pts in mark_points(label, cx):
        draw_dual(g, pts, fill, shadow)
    return n.encode_glyph(g), {
        "mode": "compact-accent",
        "src_bbox": src_bbox,
        "dst_bbox": n.bbox(g),
        "fill": fill,
        "shadow": shadow,
        "hist": hist,
    }


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.abspath(sys.argv[1]) if len(sys.argv) >= 2 else os.path.join(here, "GaiaMaster - Kamigami no Board Game (Japan).bin")
    if not os.path.isfile(src):
        print("[ERROR] CLEAN BIN not found:")
        print(src)
        return 2
    got = m.sha1_file(src).lower()
    print("Input BIN SHA1:", got)
    if got != m.EXPECTED_BIN_SHA1:
        print("[ERROR] Wrong/modified BIN. Expected CLEAN:", m.EXPECTED_BIN_SHA1)
        return 3

    with open(src, "rb") as rf:
        slps = m.read_iso_file(rf, m.SLPS_EXTENT, m.SLPS_SIZE)
        prg = m.read_iso_file(rf, m.PRG_EXTENT, m.PRG_SIZE)
    if m.sha1_bytes(slps) != m.EXPECTED_SLPS_SHA1:
        raise RuntimeError("SLPS SHA1 mismatch")
    if m.sha1_bytes(prg) != m.EXPECTED_PRG_SHA1:
        raise RuntimeError("PRGPACK SHA1 mismatch")

    entries = m.parse_bdp_entries(prg)
    owner = [e for e in entries if e[1] <= m.PRG_TEST_OFF < e[2]]
    if len(owner) != 1 or owner[0][0] != m.EXPECTED_OWNER_ENTRY:
        raise RuntimeError("Character Select text ownership mismatch: %r" % (owner,))
    if m.PRG_TEST_OFF + 24 > owner[0][2]:
        raise RuntimeError("Test text crosses owner entry")

    for code, exp in [(0x8273, 481), (0x8264, 466), (0x8272, 480), (0x889F, 0)]:
        gotv = m.mapping_value(slps, code)
        if gotv != exp:
            raise RuntimeError("Mapping fact mismatch %04X: %r != %r" % (code, gotv, exp))

    bases = {letter: n.native_base(slps, letter) for letter in ("A", "E", "O")}
    old_protected = set(m.PROTECTED_SLOTS)
    m.PROTECTED_SLOTS.update(v[1] for v in bases.values())
    try:
        choices = m.choose_slots(slps, prg, 12)
    finally:
        m.PROTECTED_SLOTS.clear()
        m.PROTECTED_SLOTS.update(old_protected)
    slots = [x[4] for x in choices]

    slps_new = bytearray(slps)
    prg_new = bytearray(prg)
    report = []
    report += [
        "GAIA MASTER 0.6.5.5 ACCENT-SAFE COMPACT NATIVE STYLE BUILD REPORT",
        "="*82,
        "MAPPING-ONLY / NO CODE HOOK / NO POINTER REDIRECT / NATIVE 12x12 72-byte 4bpp",
        "",
        "Purpose:",
        "  - keep plain A/E/O byte-for-byte native as controls",
        "  - vertically compact accented bases into rows 3..11",
        "  - reserve rows 0..2 for Vietnamese marks",
        "  - draw marks with native fill + shadow layers",
        "",
        "Known runtime fact from 0.6.5.3: palette index 7 rendered as the dark/shadow layer.",
        "",
        "Native source glyphs:",
    ]

    for letter in ("A", "E", "O"):
        code, slot, raw, g, old_fg, h = bases[letter]
        fill, shadow, h2 = choose_layers(g)
        nz = " ".join("%X:%d" % (i, h2[i]) for i in range(1, 16) if h2[i])
        report.append("  %s code=%04X -> slot=%d bbox=%r fill=%X shadow=%X hist={%s}" %
                      (letter, code, slot, n.bbox(g), fill, shadow, nz))

    report += ["", "Selected destination slots:"]
    for i, (score, label, code, slot) in enumerate(zip(choices, TEST_LABELS, TEST_CODES, slots)):
        occ, mapped_penalty, numcodes, negslot, slot2, codes = score
        report.append("  %02d %-2s code=%04X -> slot=%d prior_codes=%d static_text_hits=%d" %
                      (i, label, code, slot, len(codes), occ))

    for label, code, slot in zip(TEST_LABELS, TEST_CODES, slots):
        goff = m.ATLAS_OFF + slot*m.GLYPH_BYTES
        old = bytes(slps_new[goff:goff+m.GLYPH_BYTES])
        glyph, meta = build_glyph(label, bases)
        slps_new[goff:goff+m.GLYPH_BYTES] = glyph
        moff = m.MAPPING_OFF + ((code & 0x7FFF)*2)
        oldmap = struct.unpack_from("<H", slps_new, moff)[0]
        struct.pack_into("<H", slps_new, moff, slot)
        report.append("  patch %-2s family=%s mode=%s src_bbox=%r dst_bbox=%r fill=%r shadow=%r map SLPS+0x%06X %d->%d glyph SLPS+0x%06X old_sha1=%s" %
                      (label, n.family(label), meta["mode"], meta["src_bbox"], meta["dst_bbox"],
                       meta["fill"], meta["shadow"], moff, oldmap, slot, goff, m.sha1_bytes(old)[:12]))

    old_text = bytes(prg_new[m.PRG_TEST_OFF:m.PRG_TEST_OFF+24])
    prg_new[m.PRG_TEST_OFF:m.PRG_TEST_OFF+24] = m.code_bytes(TEST_CODES)
    report += [
        "",
        "Character Select test:",
        "  PRGPACK+0x%X owner entry %d" % (m.PRG_TEST_OFF, m.EXPECTED_OWNER_ENTRY),
        "  old24=%s" % old_text.hex().upper(),
        "  new24=%s" % m.code_bytes(TEST_CODES).hex().upper(),
        "  expected visual: A Â Ấ Ẳ E Ê Ế Ể O Ô Ố Ỗ",
        "  plain A/E/O remain native controls; accented variants are compacted for headroom",
    ]

    idx, start, end = owner[0]
    block = bytearray(prg_new[start:end])
    struct.pack_into("<I", prg_new, start+4, m.bdp_checksum(block))
    struct.pack_into("<I", prg_new, 4, m.bdp_checksum(prg_new))
    if m.bdp_checksum(prg_new) != struct.unpack_from("<I", prg_new, 4)[0]:
        raise RuntimeError("Top BDP checksum rebuild failed")
    block2 = bytes(prg_new[start:end])
    if m.bdp_checksum(block2) != struct.unpack_from("<I", block2, 4)[0]:
        raise RuntimeError("Nested BDP checksum rebuild failed")

    stem = os.path.splitext(src)[0]
    out_bin = stem + " [VI 0.6.5.5 ACCENT SAFE].bin"
    out_cue = stem + " [VI 0.6.5.5 ACCENT SAFE].cue"
    out_report = stem + " [VI 0.6.5.5 ACCENT SAFE].txt"
    shutil.copyfile(src, out_bin)
    changed = set()
    with open(out_bin, "r+b") as wf:
        m.write_changed_iso_file(wf, m.SLPS_EXTENT, slps, bytes(slps_new), changed)
        m.write_changed_iso_file(wf, m.PRG_EXTENT, prg, bytes(prg_new), changed)
        for sec in sorted(changed):
            wf.seek(sec*2352)
            raw = wf.read(2352)
            wf.seek(sec*2352)
            wf.write(m.regen_sector(raw))

    with open(out_cue, "w", encoding="ascii") as f:
        f.write('FILE "' + os.path.basename(out_bin) + '" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')

    report += [
        "",
        "Changed raw sectors: %d" % len(changed),
        "Output BIN SHA1: %s" % m.sha1_file(out_bin),
        "RESULT: BUILD SUCCESS",
    ]
    with open(out_report, "w", encoding="utf-8") as f:
        f.write("\n".join(report) + "\n")

    print("\n" + "="*72)
    print("[OK] GAIA MASTER 0.6.5.5 ACCENT-SAFE COMPACT BUILD SUCCESS")
    print("="*72)
    for letter in ("A", "E", "O"):
        code, slot, raw, g, old_fg, h = bases[letter]
        fill, shadow, h2 = choose_layers(g)
        print("Native %s: code %04X -> slot %d, fill=%X shadow=%X bbox=%r" %
              (letter, code, slot, fill, shadow, n.bbox(g)))
    print("Body band for accented glyphs: rows %d..%d" % (BODY_Y0, BODY_Y0+BODY_H-1))
    print("Accent band: rows 0..2")
    print("Expected visual: A Â Ấ Ẳ E Ê Ế Ể O Ô Ố Ỗ")
    print("Output BIN:", out_bin)
    print("Output SHA1:", m.sha1_file(out_bin))
    print("Report:", out_report)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("[ERROR]", repr(e))
        sys.exit(9)

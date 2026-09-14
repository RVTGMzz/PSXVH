#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gaia Master 0.6.10.0
HYBRID FULL-COVERAGE + FRONT ACCENT UPGRADE

Architecture lock:
- native main font 12x12 / 72-byte / 4bpp / low-nibble-first
- static mapping data only
- no renderer hook
- no pointer redirect
- no 12x16
- no 6x12 narrow path
- keep full-width spacing behavior from last-good 0.6.6.1

Installs the exact 60 custom Vietnamese glyphs currently required by vi_full,
using the clean-BIN capacity audit:
- 34 completely-unmapped zero-hit atlas slots
- 26 mapped-but-zero-static-hit slots
- 4 zero-hit slots intentionally left in reserve

Then patches three nearby setup UI strings:
  Đã ổn?
  Chọn tướng
  Nhấn O

The builder verifies clean hashes, mapping facts, slot safety, source Japanese
bytes, field lengths, BDP checksums, and raw-CD EDC/ECC before output.
"""

from __future__ import print_function
import hashlib
import os
import shutil
import struct
import sys
import unicodedata
import csv
import io
import re
import urllib.request

# ---------------------------------------------------------------------------
# Verified clean baselines
# ---------------------------------------------------------------------------

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

KNOWN_SHADOW_INDEX = 7

# Exact custom Vietnamese set from GaiaMaster_ViFullInventory_01.
CUSTOM_CHARS = list(
    "àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ"
)
if len(CUSTOM_CHARS) != 60 or len(set(CUSTOM_CHARS)) != 60:
    raise RuntimeError("CUSTOM_CHARS must contain exactly 60 unique characters")

# Frozen 60-slot production allocation from Production Capacity Scanner 0.1.
# First 34 are completely unmapped; next 26 are mapped but zero-static-hit.
PRODUCTION_SLOTS = [
    18, 33, 58, 160, 182, 261, 301, 371, 392,
    420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431,
    432, 433, 434, 435, 436, 437, 438, 439, 440,
    517, 695, 704, 713,
    38, 94, 108, 109, 129, 130, 150, 208, 295, 326, 335, 345, 372,
    385, 394, 398, 400, 403, 702, 715, 729, 745, 750, 754, 757, 790,
]
if len(PRODUCTION_SLOTS) != 60 or len(set(PRODUCTION_SLOTS)) != 60:
    raise RuntimeError("PRODUCTION_SLOTS must contain exactly 60 unique slots")

# Deliberately untouched reserve from the same zero-hit capacity audit.
RESERVE_SLOTS = [794, 807, 821, 824]

FIXED_PROTECTED = {0, 466, 480, 481}

# Quick-access UI proof targets. Builder verifies source bytes and capacity.
PROOF_STRINGS = [
    # offset, source Japanese, Vietnamese
    (0xBFBEC, "この設定でいいかしら？", "Đã ổn?"),
    (0xBFD2C, "キャラクターをえらんでね", "Chọn tướng"),
    (0xBFE4C, "○ボタンをおしてね！", "Nhấn O"),
]


TRANSLATION_BRANCH = "gaia-character-select-font-atlas-reverse-01"
TRANSLATION_REPO = "ronvotri/Viet-Hoa-PS1"
TRANSLATION_BASE = (
    "https://raw.githubusercontent.com/%s/%s/"
    "games/GaiaMaster-Kamigami-no-Board-Game/translation/"
    % (TRANSLATION_REPO, TRANSLATION_BRANCH)
)
MASTER_FILES = [
    "TRANSLATION_MASTER_0.6_part01.csv",
    "TRANSLATION_MASTER_0.6_part02.csv",
    "TRANSLATION_MASTER_0.6_part03.csv",
    "TRANSLATION_MASTER_0.6_part04.csv",
    "TRANSLATION_MASTER_0.6_part05.csv",
    "TRANSLATION_MASTER_0.6_part06.csv",
]
FRONT_FILE = "FRONT_DEMO_ADDED_061.csv"


# 0.6.10.0: accented, byte-budget-safe upgrades for every dedicated front-demo row.
# Wording stays compact on purpose so each line still fits the original Japanese field.
FRONT_ACCENT_OVERRIDES = {
    0xC00B4: "Thần chiến",
    0xC00D0: "Người=cờ",
    0xC00E4: "Thếgiới=bàncờ",
    0xC0100: "Ko chống",
    0xC0118: "Lực thần",
    0xC0130: "Đất ảo",
    0xC0144: "Vua tu sĩ",
    0xC0158: "Luật Gaia",
    0xC0178: "Giờ thế giới",
    0xC0194: "Tan nát hết",
    0xC01B0: "Hôm nay",
    0xC01C0: "Luật người",
    0xC01DC: "Đến lúc!",
    0xC01F0: "Thời Gaia Master",
    0xC0218: "Lực địa loạn",
    0xC0234: "100 năm mệnh",
    0xC0258: "Đất ảo trời",
    0xC0274: "Che cả trời",
    0xC028C: "Thế giới mất chủ",
    0xBFC20: "Tải dữ liệu VK?",
    0xBFC44: "Tải mới kỹ năng",
    0xBFC64: "Nếu không tải",
    0xBFC84: "Dùng dữ liệu cũ",
    0xBFCA8: "Kỹ năng LV1",
    0xBFCCC: "Cẩn thận khi lưu",
    0xBFD48: "/VCOM%d chọn NV",
    0xBFD80: "Nhân vật này?",
    0xBFDA0: "Xác nhận?",
    0xBFE64: "Tay cầm",
    0xBFC04: "Có      ko",
    0xBFE00: "Có   ko",
}

# Same token grammar used by the old Alpha 0.6.1 patch generator.
RUNTIME_TOKEN_RE = re.compile(r'%[+\-0-9.]*[sdifuxX]')

# ---------------------------------------------------------------------------
# Raw CD Mode2/Form1 EDC/ECC
# ---------------------------------------------------------------------------

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
        edc = (edc >> 8) ^ EDC_LUT[(edc ^ v) & 0xFF]
    return edc & 0xFFFFFFFF


def ecc_compute(src, major_count, minor_count, major_mult, minor_inc):
    size = major_count * minor_count
    dest = bytearray(major_count * 2)
    for major in range(major_count):
        index = (major >> 1) * major_mult + (major & 1)
        a = 0
        b = 0
        for _ in range(minor_count):
            t = src[index]
            index += minor_inc
            if index >= size:
                index -= size
            a ^= t
            b ^= t
            a = ECC_F[a]
        a = ECC_B[ECC_F[a] ^ b]
        dest[major] = a
        dest[major + major_count] = a ^ b
    return dest


def regen_sector(sec):
    if len(sec) != 2352:
        raise RuntimeError("Bad raw sector length")
    s = bytearray(sec)
    if s[15] != 2:
        raise RuntimeError("Expected MODE2 sector")
    if s[18] & 0x20:
        raise RuntimeError("Unexpected Mode2/Form2 sector")
    if s[16:20] != s[20:24]:
        raise RuntimeError("Mode2 subheader copies do not match")

    s[2072:2076] = struct.pack("<I", edc_compute(s[16:2072]))
    hdr = bytes(s[12:16])
    s[12:16] = b"\0\0\0\0"
    s[2076:2248] = ecc_compute(s[12:2076], 86, 24, 2, 86)
    s[2248:2352] = ecc_compute(s[12:2248], 52, 43, 86, 88)
    s[12:16] = hdr
    return bytes(s)


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------

def sha1_bytes(data):
    h = hashlib.sha1()
    h.update(data)
    return h.hexdigest()


def sha1_file(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        while True:
            b = f.read(8 * 1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def read_iso_file(rawf, extent, size):
    out = bytearray()
    remaining = size
    sector = extent
    while remaining:
        n = min(2048, remaining)
        rawf.seek(sector * 2352 + 24)
        c = rawf.read(n)
        if len(c) != n:
            raise RuntimeError("Short read at raw sector %d" % sector)
        out.extend(c)
        remaining -= n
        sector += 1
    return bytes(out)


def write_changed_iso_file(rawf, extent, original, modified, changed):
    if len(original) != len(modified):
        raise RuntimeError("File size changed")
    total = len(original)
    for i in range((total + 2047) // 2048):
        a = i * 2048
        b = min(a + 2048, total)
        if original[a:b] == modified[a:b]:
            continue
        sec = extent + i
        rawf.seek(sec * 2352)
        raw = bytearray(rawf.read(2352))
        if len(raw) != 2352:
            raise RuntimeError("Short raw sector %d" % sec)
        if raw[15] != 2 or (raw[18] & 0x20):
            raise RuntimeError("Sector %d is not MODE2/Form1" % sec)
        raw[24:24 + (b - a)] = modified[a:b]
        rawf.seek(sec * 2352)
        rawf.write(bytes(raw))
        changed.add(sec)


def count_pair(blob, pair):
    n = 0
    pos = 0
    while True:
        pos = blob.find(pair, pos)
        if pos < 0:
            return n
        n += 1
        pos += 1


def valid_codes():
    for a, b in VALID_CODE_RANGES:
        for code in range(a, b + 1):
            yield code


def mapping_value(slps, code):
    off = MAPPING_OFF + ((code & 0x7FFF) * 2)
    if off + 2 > len(slps):
        return None
    return struct.unpack_from("<H", slps, off)[0]


def mapping_region_end():
    max_idx = max(code & 0x7FFF for code in valid_codes())
    return MAPPING_OFF + (max_idx + 1) * 2


def scan_slps_without_font(slps):
    map_end = mapping_region_end()
    return b"".join((
        bytes(slps[:ATLAS_OFF]),
        bytes(slps[ATLAS_OFF + ATLAS_GLYPHS * GLYPH_BYTES:MAPPING_OFF]),
        bytes(slps[map_end:]),
    ))


# ---------------------------------------------------------------------------
# BDP
# ---------------------------------------------------------------------------

def bdp_checksum(block):
    s = (sum(block[:4]) + sum(block[8:])) & 0xFFFF
    return (((~s) & 0xFFFF) << 16) | s


def parse_bdp_entries(prg):
    magic, stored, toc_size, count = struct.unpack_from("<IIII", prg, 0)
    if magic != 0x10F0 or bdp_checksum(prg) != stored:
        raise RuntimeError("PRGPACK top checksum verification failed")
    payload_base = 8 + toc_size
    entries = []
    for i in range(count):
        rel, size = struct.unpack_from("<II", prg, 16 + i * 8)
        start = payload_base + rel
        end = start + size
        block = prg[start:end]
        if len(block) != size or struct.unpack_from("<I", block, 0)[0] != 0x10F0:
            raise RuntimeError("Bad nested BDP entry %d" % i)
        if bdp_checksum(block) != struct.unpack_from("<I", block, 4)[0]:
            raise RuntimeError("Nested BDP checksum mismatch at %d" % i)
        entries.append((i, start, end))
    return entries


def owner_for_offset(entries, off):
    owner = [e for e in entries if e[1] <= off < e[2]]
    if len(owner) != 1:
        raise RuntimeError("Offset 0x%X has ambiguous/no BDP owner: %r" % (off, owner))
    return owner[0]


# ---------------------------------------------------------------------------
# Native 12x12 glyph decode/encode
# ---------------------------------------------------------------------------

def decode_glyph(raw):
    if len(raw) != 72:
        raise ValueError("Expected 72-byte glyph")
    g = [[0] * 12 for _ in range(12)]
    p = 0
    for y in range(12):
        for x in range(0, 12, 2):
            b = raw[p]
            p += 1
            g[y][x] = b & 0x0F
            g[y][x + 1] = (b >> 4) & 0x0F
    return g


def encode_glyph(g):
    if len(g) != 12 or any(len(row) != 12 for row in g):
        raise ValueError("Expected 12x12 grid")
    out = bytearray()
    for row in g:
        for x in range(0, 12, 2):
            out.append((row[x] & 0xF) | ((row[x + 1] & 0xF) << 4))
    if len(out) != 72:
        raise AssertionError(len(out))
    return bytes(out)


def bbox(g):
    pts = [(x, y) for y, row in enumerate(g) for x, v in enumerate(row) if v]
    if not pts:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def histogram(g):
    h = {i: 0 for i in range(16)}
    for row in g:
        for v in row:
            h[v] += 1
    return h


def choose_layers(g):
    h = histogram(g)
    nonzero = [(count, idx) for idx, count in h.items() if idx and count]
    if not nonzero:
        raise RuntimeError("Native glyph has no visible pixels")
    nonzero.sort(reverse=True)

    shadow = KNOWN_SHADOW_INDEX if h.get(KNOWN_SHADOW_INDEX, 0) else None
    fill_candidates = [(count, idx) for count, idx in nonzero if idx != shadow]
    fill = fill_candidates[0][1] if fill_candidates else nonzero[0][1]

    if shadow is None:
        others = [(count, idx) for count, idx in nonzero if idx != fill]
        shadow = others[0][1] if others else fill

    return fill, shadow, h


def put(g, x, y, value):
    if 0 <= x < 12 and 0 <= y < 12:
        g[y][x] = value


def draw_dual(g, points, fill, shadow):
    if shadow != fill:
        for x, y in points:
            put(g, x + 1, y + 1, shadow)
    for x, y in points:
        put(g, x, y, fill)


# ---------------------------------------------------------------------------
# Production encoder / 0.6.6.1-style baseline-normalized composition
# ---------------------------------------------------------------------------

def fullwidth_code(ch):
    if ch == " ":
        fw = "\u3000"
    elif 0x21 <= ord(ch) <= 0x7E:
        fw = chr(ord(ch) + 0xFEE0)
    else:
        raise ValueError("No native full-width code for %r" % ch)
    b = fw.encode("cp932")
    if len(b) != 2:
        raise RuntimeError("Expected 2-byte CP932 for %r" % fw)
    return (b[0] << 8) | b[1]


def native_base(slps, letter):
    code = fullwidth_code(letter)
    slot = mapping_value(slps, code)
    if slot is None or not (0 <= slot < ATLAS_GLYPHS):
        raise RuntimeError("Native base mapping invalid: %r %04X -> %r" %
                           (letter, code, slot))
    off = ATLAS_OFF + slot * GLYPH_BYTES
    raw = bytes(slps[off:off + GLYPH_BYTES])
    return code, slot, raw, decode_glyph(raw)


def decompose(ch):
    if ch in ("đ", "Đ"):
        return ("d" if ch == "đ" else "D"), ["stroke"]
    d = unicodedata.normalize("NFD", ch)
    if not d:
        raise ValueError(ch)
    return d[0], list(d[1:])


def fit_body_native(g, marks):
    """Preserve native baseline/body whenever enough accent room already exists.
    Otherwise perform the smallest vertical resample needed."""
    src = bbox(g)
    if src is None:
        raise RuntimeError("Empty native base glyph")

    x0, sy0, x1, sy1 = src

    top_marks = any(
        mark in marks
        for mark in ("\u0306", "\u0302", "\u031B",
                     "\u0301", "\u0300", "\u0309", "\u0303")
    )
    bottom_mark = "\u0323" in marks

    top_need = 2 if top_marks else 0
    bottom_limit = 10 if bottom_mark else 11

    if sy0 >= top_need and sy1 <= bottom_limit:
        return [row[:] for row in g], src, src, "native-preserved"

    src_h = sy1 - sy0 + 1
    dst_y1 = min(sy1, bottom_limit)
    dst_y0 = max(top_need, dst_y1 - src_h + 1)

    if dst_y0 > dst_y1:
        dst_y0 = top_need
        dst_y1 = bottom_limit

    dst_h = dst_y1 - dst_y0 + 1
    if dst_h <= 0:
        raise RuntimeError("No vertical room for glyph")

    out = [[0] * 12 for _ in range(12)]
    for dy in range(dst_h):
        sy = sy0 if dst_h == 1 else (
            sy0 + int(round(dy * (src_h - 1) / float(dst_h - 1)))
        )
        out[dst_y0 + dy] = g[sy][:]

    return out, src, bbox(out), "minimal-fit"


def make_vi_glyph(slps, ch, base_cache):
    base, marks = decompose(ch)

    if base not in base_cache:
        base_cache[base] = native_base(slps, base)

    native_code, native_slot, raw, base_grid = base_cache[base]
    fill, shadow, hist = choose_layers(base_grid)

    g, src_bbox, body_bbox, fit_mode = fit_body_native(base_grid, marks)
    if body_bbox is None:
        raise RuntimeError("Empty fitted glyph for %r" % ch)

    x0, y0, x1, y1 = body_bbox
    cx = (x0 + x1) // 2
    top1 = max(0, y0 - 1)
    top2 = max(0, y0 - 2)

    # Structural marks first.
    if "\u0306" in marks:  # breve
        draw_dual(g, [
            (cx - 2, top1),
            (cx - 1, top2),
            (cx, top2),
            (cx + 1, top2),
            (cx + 2, top1),
        ], fill, shadow)

    if "\u0302" in marks:  # circumflex
        draw_dual(g, [
            (cx - 1, top1),
            (cx, top2),
            (cx + 1, top1),
        ], fill, shadow)

    horn_anchor = None
    if "\u031B" in marks:  # horn
        # 0.6.7.1 polish: the horn should hug the letter body more tightly.
        hx = min(10, x1)
        hy = min(10, y0 + 1)
        horn_anchor = (hx, hy)
        draw_dual(g, [
            (hx, hy),
            (min(10, hx + 1), max(0, hy - 1)),
        ], fill, shadow)

    if "stroke" in marks:  # đ / Đ
        yy = max(y0, min(y1, (y0 + y1) // 2))
        draw_dual(g, [
            (max(0, x0 - 1), yy),
            (x0, yy),
            (min(11, x0 + 1), yy),
            (min(11, x0 + 2), yy),
        ], fill, shadow)

    # Tone marks.
    # 0.6.7.1 polish: when a horn is present (ơ/ư family), keep the horn close
    # to the body but separate the tone mark slightly so the two apostrophe-like
    # shapes do not visually merge together.
    if "\u0301" in marks:  # acute
        if horn_anchor is not None:
            hx, hy = horn_anchor
            # 0.6.7.2 polish: pull acute farther away so it no longer touches the horn.
            draw_dual(g, [
                (min(11, hx + 3), max(0, hy - 4)),
                (min(11, hx + 2), max(0, hy - 3)),
            ], fill, shadow)
        else:
            draw_dual(g, [(cx + 1, top2), (cx, top1)], fill, shadow)

    if "\u0300" in marks:  # grave
        if horn_anchor is not None:
            hx, hy = horn_anchor
            # Keep symmetry with acute: separate the grave a touch more as well.
            draw_dual(g, [
                (max(0, hx - 2), max(0, hy - 4)),
                (max(0, hx - 1), max(0, hy - 3)),
            ], fill, shadow)
        else:
            draw_dual(g, [(cx - 1, top2), (cx, top1)], fill, shadow)

    if "\u0309" in marks:  # hook above
        draw_dual(g, [
            (cx, top2),
            (cx + 1, top2),
            (cx + 1, top1),
            (cx, top1),
        ], fill, shadow)

    if "\u0303" in marks:  # tilde
        draw_dual(g, [
            (cx - 2, top1),
            (cx - 1, top2),
            (cx, top1),
            (cx + 1, top1),
            (cx + 2, top2),
        ], fill, shadow)

    if "\u0323" in marks:  # dot below
        dot_y = min(11, y1 + 1)
        draw_dual(g, [(cx, dot_y)], fill, shadow)

    return encode_glyph(g), {
        "base": base,
        "native_code": native_code,
        "native_slot": native_slot,
        "fill": fill,
        "shadow": shadow,
        "src_bbox": src_bbox,
        "body_bbox": body_bbox,
        "final_bbox": bbox(g),
        "fit": fit_mode,
        "marks": [
            "stroke" if x == "stroke" else "U+%04X" % ord(x)
            for x in marks
        ],
    }


def safe_custom_codes(slps, prg, need):
    scan_slps = scan_slps_without_font(slps)
    out = []
    for code in valid_codes():
        if code < 0x889F:
            continue
        pair = bytes([(code >> 8) & 0xFF, code & 0xFF])
        try:
            pair.decode("cp932")
        except Exception:
            continue
        hits = count_pair(prg, pair) + count_pair(scan_slps, pair)
        if hits == 0:
            out.append(code)
            if len(out) == need:
                return out
    raise RuntimeError("Need %d zero-hit custom codes; found only %d" %
                       (need, len(out)))


def slot_static_hits(slps, prg, slot):
    scan_slps = scan_slps_without_font(slps)
    codes = []
    for code in valid_codes():
        if mapping_value(slps, code) == slot:
            codes.append(code)

    hits = 0
    for code in codes:
        pair = bytes([(code >> 8) & 0xFF, code & 0xFF])
        hits += count_pair(prg, pair)
        hits += count_pair(scan_slps, pair)
    return hits, codes


def encode_text(text, cmap):
    out = bytearray()
    details = []

    for ch in text:
        if ch in cmap:
            code = cmap[ch]
        elif ch == " " or (0x21 <= ord(ch) <= 0x7E):
            code = fullwidth_code(ch)
        else:
            raise RuntimeError(
                "Text contains non-ASCII char outside frozen production codepage: %r U+%04X"
                % (ch, ord(ch))
            )
        out.extend([(code >> 8) & 0xFF, code & 0xFF])
        details.append((ch, code))

    return bytes(out), details



def fetch_csv(here, name):
    local = os.path.join(here, name)
    if os.path.isfile(local):
        with open(local, "rb") as f:
            data = f.read()
        return data.decode("utf-8-sig"), "local"

    url = TRANSLATION_BASE + name
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "GaiaMaster-0.6.10.0/1.0"},
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        data = r.read()
    try:
        with open(local, "wb") as f:
            f.write(data)
    except Exception:
        pass
    return data.decode("utf-8-sig"), url


def load_translation_rows(here):
    rows = []
    source_log = []

    for name in MASTER_FILES:
        content, source = fetch_csv(here, name)
        part = list(csv.DictReader(io.StringIO(content)))
        rows.extend(part)
        source_log.append((name, source, len(part)))

    front_content, front_source = fetch_csv(here, FRONT_FILE)
    front_rows = list(csv.DictReader(io.StringIO(front_content)))
    source_log.append((FRONT_FILE, front_source, len(front_rows)))
    return rows, front_rows, source_log


def encode_runtime_text(text, cmap):
    """Encode game runtime text while preserving formatter/control tokens raw.

    Old Alpha behavior:
    - ordinary ASCII -> full-width CP932;
    - space -> ideographic full-width space;
    - printf tokens such as %s, %d, %+3d stay raw ASCII;
    - /V and /v stay raw ASCII;
    - Vietnamese precomposed chars use the frozen custom codepage.
    """
    out = bytearray()
    detail = []
    i = 0

    while i < len(text):
        if text[i] == "%":
            m = RUNTIME_TOKEN_RE.match(text, i)
            if m:
                token = m.group(0)
                raw = token.encode("ascii")
                out.extend(raw)
                detail.append((token, "RAW"))
                i = m.end()
                continue

        if text.startswith("/V", i) or text.startswith("/v", i):
            token = text[i:i+2]
            out.extend(token.encode("ascii"))
            detail.append((token, "RAW"))
            i += 2
            continue

        ch = text[i]

        if ch in cmap:
            code = cmap[ch]
            out.extend([(code >> 8) & 0xFF, code & 0xFF])
            detail.append((ch, "%04X" % code))
        elif ch == " " or (0x21 <= ord(ch) <= 0x7E):
            code = fullwidth_code(ch)
            out.extend([(code >> 8) & 0xFF, code & 0xFF])
            detail.append((ch, "%04X" % code))
        else:
            # Preserve CP932 punctuation/symbols used by the old Alpha fallback
            # (for example Japanese corner quotes 「 」).
            try:
                raw = ch.encode("cp932")
            except Exception:
                raise RuntimeError(
                    "Unsupported runtime char %r U+%04X in %r" % (ch, ord(ch), text)
                )
            out.extend(raw)
            detail.append((ch, "CP932:" + raw.hex().upper()))

        i += 1

    return bytes(out), detail


def make_hybrid_patch(file_name, off, jp, vi_full, vi_fallback, cmap):
    orig = jp.encode("cp932")

    candidates = []
    if (vi_full or "").strip():
        candidates.append(("vi_full", vi_full))
    if (vi_fallback or "").strip():
        candidates.append(("vi_game_current", vi_fallback))

    attempts = []
    for source, text in candidates:
        try:
            enc, detail = encode_runtime_text(text, cmap)
        except Exception as e:
            attempts.append((source, text, "ENCODE_FAIL", repr(e)))
            continue

        if len(enc) <= len(orig):
            new = enc + b"\x00" * (len(orig) - len(enc))
            return {
                "file": file_name,
                "offset": off,
                "orig": orig,
                "new": new,
                "jp": jp,
                "vi": text,
                "source": source,
                "encoded_len": len(enc),
                "orig_len": len(orig),
                "detail": detail,
                "attempts": attempts,
            }

        attempts.append(
            (source, text, "TOO_LONG", "%d>%d" % (len(enc), len(orig)))
        )

    return {
        "file": file_name,
        "offset": off,
        "orig": orig,
        "new": None,
        "jp": jp,
        "vi": None,
        "source": None,
        "encoded_len": None,
        "orig_len": len(orig),
        "detail": [],
        "attempts": attempts,
    }


def compute_alpha061_legacy_keys(master_rows, front_rows, cmap):
    """Reproduce the old Alpha 0.6.1 generator's coverage exactly.

    A master row belonged to Alpha only when:
    - vi_game_current was non-empty;
    - that fallback encoding fit inside the original Japanese byte budget;
    - the (file, offset) had not already been accepted.

    FRONT_DEMO_ADDED_061 rows were then added only for offsets not already used.
    This returns the exact proven legacy key set, which must contain 397 items.
    """
    seen = set()
    legacy = set()

    for r in master_rows:
        file_name = (r.get("file") or "").strip()
        off = int((r.get("offset_hex") or "0"), 16)
        key = (file_name, off)
        vi = (r.get("vi_game_current") or "").strip()
        if not vi or key in seen:
            continue

        jp = r.get("japanese") or ""
        orig = jp.encode("cp932")
        try:
            enc, _ = encode_runtime_text(vi, cmap)
        except Exception:
            continue

        if len(enc) <= len(orig):
            legacy.add(key)
            seen.add(key)

    for r in front_rows:
        file_name = "PRGPACK.BDP"
        off = int((r.get("offset_hex") or "0"), 16)
        key = (file_name, off)
        if key in seen:
            continue

        jp = r.get("japanese") or ""
        vi = (r.get("vi_no_accents") or "").strip()
        orig = jp.encode("cp932")
        enc, _ = encode_runtime_text(vi, cmap)
        if len(enc) > len(orig):
            raise RuntimeError(
                "Front legacy row no longer fits at 0x%X (%d>%d)"
                % (off, len(enc), len(orig))
            )
        legacy.add(key)
        seen.add(key)

    return legacy


def generate_hybrid_patches(here, cmap):
    master_rows, front_rows, source_log = load_translation_rows(here)
    legacy_keys = compute_alpha061_legacy_keys(master_rows, front_rows, cmap)

    if len(legacy_keys) != 397:
        raise RuntimeError(
            "Exact Alpha 0.6.1 legacy reconstruction failed: expected 397, got %d"
            % len(legacy_keys)
        )

    patches = []
    skipped = []
    seen = set()

    # Hybrid master coverage: prefer vi_full, fall back to vi_game_current.
    for r in master_rows:
        file_name = (r.get("file") or "").strip()
        off = int((r.get("offset_hex") or "0"), 16)
        key = (file_name, off)

        if key in seen:
            continue

        vi_full = r.get("vi_full") or ""
        vi_fallback = r.get("vi_game_current") or ""
        if not vi_full.strip() and not vi_fallback.strip():
            continue

        p = make_hybrid_patch(
            file_name,
            off,
            r.get("japanese") or "",
            vi_full,
            vi_fallback,
            cmap,
        )
        p["legacy_basis"] = key in legacy_keys

        if p["new"] is not None:
            patches.append(p)
            seen.add(key)
        else:
            skipped.append(p)

    # Dedicated Alpha front additions.
    for r in front_rows:
        file_name = "PRGPACK.BDP"
        off = int((r.get("offset_hex") or "0"), 16)
        key = (file_name, off)
        if key in seen:
            continue

        accented_front = FRONT_ACCENT_OVERRIDES.get(off, "")
        p = make_hybrid_patch(
            file_name,
            off,
            r.get("japanese") or "",
            accented_front,
            r.get("vi_no_accents") or "",
            cmap,
        )
        p["legacy_basis"] = key in legacy_keys

        if p["new"] is None:
            raise RuntimeError(
                "Front demo fallback unexpectedly does not fit at 0x%X" % off
            )
        patches.append(p)
        seen.add(key)

    patches.sort(key=lambda x: (x["file"], x["offset"]))

    # Every dedicated front row must now use the accented override.
    front_accented = [
        p for p in patches
        if p["file"] == "PRGPACK.BDP"
        and p["offset"] in FRONT_ACCENT_OVERRIDES
        and p["source"] == "vi_full"
    ]
    if len(front_accented) != len(FRONT_ACCENT_OVERRIDES):
        got = {p["offset"] for p in front_accented}
        missing = sorted(set(FRONT_ACCENT_OVERRIDES) - got)
        raise RuntimeError(
            "Front accent gate failed: %d/%d accented; missing=%s"
            % (len(front_accented), len(FRONT_ACCENT_OVERRIDES),
               ",".join("0x%X" % x for x in missing))
        )

    patch_keys = {(p["file"], p["offset"]) for p in patches}
    missing_legacy = sorted(legacy_keys - patch_keys)
    if missing_legacy:
        preview = ", ".join("%s+0x%X" % x for x in missing_legacy[:12])
        raise RuntimeError(
            "Hybrid lost %d exact Alpha legacy patch key(s): %s"
            % (len(missing_legacy), preview)
        )

    legacy_count = len(legacy_keys & patch_keys)
    extra_keys = patch_keys - legacy_keys
    extra_full_only = len(extra_keys)

    if legacy_count != 397:
        raise RuntimeError(
            "Hybrid exact legacy gate failed: %d / 397" % legacy_count
        )

    coverage = {
        "legacy": legacy_count,
        "extra_vi_full_only": extra_full_only,
        "front_accented": len(front_accented),
        "total": len(patches),
    }
    return patches, skipped, source_log, coverage


def apply_translation_patch(buf, patch):
    off = patch["offset"]
    orig = patch["orig"]
    new = patch["new"]
    current = bytes(buf[off:off + len(orig)])
    if current != orig:
        raise RuntimeError(
            "Original bytes mismatch at %s+0x%X\nexpected=%s\nactual=%s"
            % (
                patch["file"],
                off,
                orig.hex().upper(),
                current.hex().upper(),
            )
        )
    if len(orig) != len(new):
        raise RuntimeError("Patch length mismatch at %s+0x%X" %
                           (patch["file"], off))
    buf[off:off + len(new)] = new


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.abspath(sys.argv[1]) if len(sys.argv) >= 2 else os.path.join(
        here, "GaiaMaster - Kamigami no Board Game (Japan).bin"
    )

    if not os.path.isfile(src):
        print("[ERROR] CLEAN BIN not found:")
        print(src)
        return 2

    got = sha1_file(src).lower()
    print("Input BIN SHA1:", got)
    if got != EXPECTED_BIN_SHA1:
        print("[ERROR] Wrong/modified BIN. Expected CLEAN:", EXPECTED_BIN_SHA1)
        return 3

    with open(src, "rb") as rf:
        slps = read_iso_file(rf, SLPS_EXTENT, SLPS_SIZE)
        prg = read_iso_file(rf, PRG_EXTENT, PRG_SIZE)

    if sha1_bytes(slps) != EXPECTED_SLPS_SHA1:
        raise RuntimeError("SLPS SHA1 mismatch")
    if sha1_bytes(prg) != EXPECTED_PRG_SHA1:
        raise RuntimeError("PRGPACK SHA1 mismatch")

    # Mapping ownership facts.
    for code, expected in [
        (0x8273, 481),
        (0x8264, 466),
        (0x8272, 480),
        (0x889F, 0),
    ]:
        got_slot = mapping_value(slps, code)
        if got_slot != expected:
            raise RuntimeError(
                "Mapping fact mismatch %04X: %r != %r"
                % (code, got_slot, expected)
            )

    # Protect all native base glyphs used by the current 60-char codepage.
    base_cache = {}
    protected = set(FIXED_PROTECTED)
    for ch in CUSTOM_CHARS:
        base, marks = decompose(ch)
        if base not in base_cache:
            base_cache[base] = native_base(slps, base)
        protected.add(base_cache[base][1])

    overlap = protected.intersection(PRODUCTION_SLOTS)
    if overlap:
        raise RuntimeError("Production slots overlap protected native bases: %r" %
                           sorted(overlap))

    # Verify every frozen production slot is still zero-static-hit on CLEAN.
    slot_audit = []
    for slot in PRODUCTION_SLOTS + RESERVE_SLOTS:
        hits, old_codes = slot_static_hits(slps, prg, slot)
        slot_audit.append((slot, hits, old_codes))
        if hits != 0:
            raise RuntimeError(
                "Frozen slot %d is no longer zero-static-hit (hits=%d)" %
                (slot, hits)
            )

    codes = safe_custom_codes(slps, prg, len(CUSTOM_CHARS))
    cmap = dict(zip(CUSTOM_CHARS, codes))

    slps_new = bytearray(slps)
    prg_new = bytearray(prg)

    report = [
        "GAIA MASTER 0.6.10.0 HYBRID FULL-COVERAGE + FRONT ACCENT UPGRADE",
        "=" * 92,
        "NATIVE 12x12 / MAPPING-ONLY / NO HOOK / NO POINTER REDIRECT",
        "0.6.6.1 BASELINE-NORMALIZED GLYPH COMPOSITION",
        "",
        "Input BIN SHA1: %s" % got,
        "Custom glyph count: %d" % len(CUSTOM_CHARS),
        "Production slots: %d" % len(PRODUCTION_SLOTS),
        "Reserve zero-hit slots left untouched: %s" %
        ", ".join(map(str, RESERVE_SLOTS)),
        "",
        "SLOT AUDIT",
        "-" * 92,
    ]

    for slot, hits, old_codes in slot_audit:
        report.append(
            "slot=%d hits=%d old_codes=%s%s"
            % (
                slot,
                hits,
                ",".join("%04X" % c for c in old_codes) or "<unmapped>",
                " [RESERVE]" if slot in RESERVE_SLOTS else "",
            )
        )

    report += [
        "",
        "FROZEN PRODUCTION CODEPAGE",
        "-" * 92,
    ]

    # Install all 60 glyphs + mappings.
    for index, (ch, code, slot) in enumerate(
        zip(CUSTOM_CHARS, codes, PRODUCTION_SLOTS)
    ):
        glyph, meta = make_vi_glyph(slps, ch, base_cache)

        goff = ATLAS_OFF + slot * GLYPH_BYTES
        old_glyph = bytes(slps_new[goff:goff + GLYPH_BYTES])
        slps_new[goff:goff + GLYPH_BYTES] = glyph

        moff = MAPPING_OFF + ((code & 0x7FFF) * 2)
        old_map = struct.unpack_from("<H", slps_new, moff)[0]
        struct.pack_into("<H", slps_new, moff, slot)

        report.append(
            "%02d U+%04X %-2s -> code=%04X -> slot=%d oldmap=%d "
            "base=%s native=%04X/%d fit=%s src=%r body=%r final=%r "
            "fill=%X shadow=%X marks=%s oldglyph=%s newglyph=%s"
            % (
                index,
                ord(ch),
                ch,
                code,
                slot,
                old_map,
                meta["base"],
                meta["native_code"],
                meta["native_slot"],
                meta["fit"],
                meta["src_bbox"],
                meta["body_bbox"],
                meta["final_bbox"],
                meta["fill"],
                meta["shadow"],
                ",".join(meta["marks"]),
                sha1_bytes(old_glyph)[:12],
                sha1_bytes(glyph)[:12],
            )
        )

    # Multi-UI proof.
    entries = parse_bdp_entries(prg)
    touched_owners = set()

    report += [
        "",
        "ANCHOR UI SANITY CHECK",
        "-" * 92,
    ]

    for off, jp, vi in PROOF_STRINGS:
        jp_bytes = jp.encode("cp932")
        actual = bytes(prg_new[off:off + len(jp_bytes)])
        if actual != jp_bytes:
            raise RuntimeError(
                "Source Japanese mismatch at PRGPACK+0x%X\nexpected=%s\nactual  =%s"
                % (off, jp_bytes.hex().upper(), actual.hex().upper())
            )

        vi_bytes, details = encode_text(vi, cmap)
        if len(vi_bytes) > len(jp_bytes):
            raise RuntimeError(
                "Proof text does not fit source field at 0x%X: %r %d > %d"
                % (off, vi, len(vi_bytes), len(jp_bytes))
            )

        owner_idx, start, end = owner_for_offset(entries, off)
        if off + len(jp_bytes) + 1 > end:
            raise RuntimeError("Proof field crosses nested BDP owner at 0x%X" % off)

        old_field = bytes(prg_new[off:off + len(jp_bytes) + 1])
        new_field = (
            vi_bytes
            + b"\x00"
            + b"\x00" * (len(jp_bytes) - len(vi_bytes))
        )
        if len(new_field) != len(old_field):
            raise AssertionError((len(new_field), len(old_field)))

        prg_new[off:off + len(old_field)] = new_field
        touched_owners.add(owner_idx)

        report.append(
            "PRGPACK+0x%X owner=%d  %r -> %r  old_bytes=%d new_bytes=%d"
            % (off, owner_idx, jp, vi, len(jp_bytes), len(vi_bytes))
        )
        report.append("  old=%s" % old_field.hex().upper())
        report.append("  new=%s" % new_field.hex().upper())
        report.append(
            "  encoded=%s"
            % " ".join("%r:%04X" % x for x in details)
        )

    # -------------------------------------------------------------------
    # HYBRID FULL-COVERAGE GAMEPLAY PIPELINE
    # -------------------------------------------------------------------
    gameplay_patches, gameplay_skipped, tm_sources, coverage_gate = generate_hybrid_patches(
        here, cmap
    )

    # The three proof anchors above intentionally override the matching gameplay
    # rows if present. Skip exact duplicate offsets here.
    proof_offsets = {("PRGPACK.BDP", off) for off, _, _ in PROOF_STRINGS}

    applied_gameplay = 0
    accented_gameplay = 0
    fallback_gameplay = 0
    by_file = {"PRGPACK.BDP": 0, "SLPS_020.75": 0}

    report += [
        "",
        "TRANSLATION SOURCES",
        "-" * 92,
    ]
    for name, source, count in tm_sources:
        report.append("%s rows=%d source=%s" % (name, count, source))

    report += [
        "",
        "HYBRID GAMEPLAY PATCHES",
        "-" * 92,
    ]

    for p in gameplay_patches:
        key = (p["file"], p["offset"])
        if key in proof_offsets:
            report.append(
                "OVERRIDE_SKIP %s+0x%X %r (explicit anchor wins)"
                % (p["file"], p["offset"], p["jp"])
            )
            continue

        target = prg_new if p["file"] == "PRGPACK.BDP" else slps_new
        apply_translation_patch(target, p)

        applied_gameplay += 1
        by_file[p["file"]] = by_file.get(p["file"], 0) + 1
        if p["source"] == "vi_full":
            accented_gameplay += 1
        else:
            fallback_gameplay += 1

        if p["file"] == "PRGPACK.BDP":
            owner_idx, start, end = owner_for_offset(entries, p["offset"])
            if p["offset"] + len(p["orig"]) > end:
                raise RuntimeError(
                    "Gameplay patch crosses nested BDP owner at 0x%X"
                    % p["offset"]
                )
            touched_owners.add(owner_idx)

        report.append(
            "%s+0x%X [%s] old=%d new=%d  %r -> %r"
            % (
                p["file"],
                p["offset"],
                p["source"],
                p["orig_len"],
                p["encoded_len"],
                p["jp"],
                p["vi"],
            )
        )

    report += [
        "",
        "GAMEPLAY COVERAGE SUMMARY",
        "-" * 92,
        "Generated hybrid patches      : %d" % len(gameplay_patches),
        "Legacy Alpha coverage gate    : %d / 397" % coverage_gate["legacy"],
        "Extra vi_full-only patches    : %d" % coverage_gate["extra_vi_full_only"],
        "Applied gameplay patches      : %d" % applied_gameplay,
        "  vi_full accented            : %d" % accented_gameplay,
        "  vi_game_current fallback    : %d" % fallback_gameplay,
        "PRGPACK gameplay patches      : %d" % by_file.get("PRGPACK.BDP", 0),
        "SLPS gameplay patches         : %d" % by_file.get("SLPS_020.75", 0),
        "Rows with no fitting candidate: %d" % len(gameplay_skipped),
    ]

    if gameplay_skipped:
        report += [
            "",
            "SKIPPED GAMEPLAY ROWS",
            "-" * 92,
        ]
        for p in gameplay_skipped:
            report.append(
                "%s+0x%X %r attempts=%r"
                % (p["file"], p["offset"], p["jp"], p["attempts"])
            )

    # Rebuild every nested owner touched, then top-level BDP checksum.
    entry_by_index = {i: (i, s, e) for i, s, e in entries}
    for owner_idx in sorted(touched_owners):
        _, start, end = entry_by_index[owner_idx]
        block = bytearray(prg_new[start:end])
        struct.pack_into("<I", prg_new, start + 4, bdp_checksum(block))

    struct.pack_into("<I", prg_new, 4, bdp_checksum(prg_new))

    # Verify BDP checksums after modifications.
    if bdp_checksum(prg_new) != struct.unpack_from("<I", prg_new, 4)[0]:
        raise RuntimeError("Top BDP checksum rebuild failed")

    for owner_idx in sorted(touched_owners):
        _, start, end = entry_by_index[owner_idx]
        if bdp_checksum(bytes(prg_new[start:end])) != struct.unpack_from(
            "<I", prg_new, start + 4
        )[0]:
            raise RuntimeError(
                "Nested BDP checksum rebuild failed for owner %d" % owner_idx
            )

    # Output.
    stem = os.path.splitext(src)[0]
    out_bin = stem + " [VI 0.6.10.0 HYBRID GAMEPLAY].bin"
    out_cue = stem + " [VI 0.6.10.0 HYBRID GAMEPLAY].cue"
    out_report = stem + " [VI 0.6.10.0 HYBRID GAMEPLAY].txt"
    out_codepage = stem + " [VI 0.6.10.0 CODEPAGE60].txt"

    shutil.copyfile(src, out_bin)
    changed = set()

    with open(out_bin, "r+b") as wf:
        write_changed_iso_file(
            wf, SLPS_EXTENT, slps, bytes(slps_new), changed
        )
        write_changed_iso_file(
            wf, PRG_EXTENT, prg, bytes(prg_new), changed
        )

        for sec in sorted(changed):
            wf.seek(sec * 2352)
            raw = wf.read(2352)
            wf.seek(sec * 2352)
            wf.write(regen_sector(raw))

    with open(out_cue, "w", encoding="ascii") as f:
        f.write(
            'FILE "' + os.path.basename(out_bin) + '" BINARY\n'
            "  TRACK 01 MODE2/2352\n"
            "    INDEX 01 00:00:00\n"
        )

    report += [
        "",
        "BUILD RESULT",
        "-" * 92,
        "Touched nested BDP owners: %s" %
        ", ".join(map(str, sorted(touched_owners))),
        "Changed raw sectors: %d" % len(changed),
        "Output BIN SHA1: %s" % sha1_file(out_bin),
        "RESULT: BUILD SUCCESS",
        "",
        "RUNTIME CHECK:",
        "1. Boot generated CUE.",
        "2. Open setup / player-selection flow.",
        "3. Check these three strings:",
        "   Đã ổn?",
        "   Chọn tướng",
        "   Nhấn O",
        "4. Full-width spacing is EXPECTED and accepted for this phase.",
        "5. Stop immediately on freeze/global corruption.",
        "6. Start a real match and check cards/menu/gameplay prompts.",
        "7. Expected: broad Vietnamese coverage, not just Character Select.",
        "8. If any screen stays Japanese, screenshot it and send generated TXT.",
    ]

    with open(out_report, "w", encoding="utf-8") as f:
        f.write("\n".join(report) + "\n")

    with open(out_codepage, "w", encoding="utf-8") as f:
        f.write("GAIA MASTER PRODUCTION CODEPAGE 60 - 0.6.10.0\n")
        f.write("=" * 72 + "\n")
        for ch, code, slot in zip(CUSTOM_CHARS, codes, PRODUCTION_SLOTS):
            f.write(
                "U+%04X\t%s\t%04X\t%d\n"
                % (ord(ch), ch, code, slot)
            )
        f.write("\nRESERVE ZERO-HIT SLOTS: %s\n" %
                ", ".join(map(str, RESERVE_SLOTS)))

    print("")
    print("=" * 80)
    print("[OK] Gaia Master 0.6.10.0 HYBRID GAMEPLAY build success")
    print("=" * 80)
    print("Installed custom glyphs :", len(CUSTOM_CHARS))
    print("Reserve zero-hit slots  :", len(RESERVE_SLOTS))
    print("Proof strings           :")
    for _, _, vi in PROOF_STRINGS:
        print("  ", vi)
    print("Hybrid coverage total   :", coverage_gate["total"])
    print("  legacy Alpha gate     :", "%d / 397" % coverage_gate["legacy"])
    print("  extra vi_full-only    :", coverage_gate["extra_vi_full_only"])
    print("  front accented        :", coverage_gate["front_accented"])
    print("Gameplay patches        :", applied_gameplay)
    print("  accented vi_full      :", accented_gameplay)
    print("  fallback no-accent    :", fallback_gameplay)
    print("  PRGPACK               :", by_file.get("PRGPACK.BDP", 0))
    print("  SLPS                  :", by_file.get("SLPS_020.75", 0))
    print("Skipped no-fit rows     :", len(gameplay_skipped))
    print("Output:", out_cue)
    print("Report:", out_report)
    print("Codepage:", out_codepage)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("[ERROR]", repr(e))
        sys.exit(9)

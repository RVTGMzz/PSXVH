# Gaia Master — Font Isolation 0.6.3.0 EXTENDED HEIGHT 12x16 — FAIL

Runtime test date: **2026-09-12**

## Goal

Test whether Character Select can render a single Vietnamese glyph at **12x16 / 96 bytes** while leaving untouched Japanese/Latin glyphs on the native **12x12 / 72-byte** path.

Control string:

```text
ＴＥＳＴ亜
```

Target:

```text
ＴＥＳＴẾ
```

The extended glyph allocated extra headroom for Vietnamese stacked diacritics so characters such as `Ế`, `Ể`, `Ẳ`, `Ỗ`, `Ử`, `Ấ`, `Ố` would not have to compress the native base-letter body.

## Runtime result

**FAIL.**

User screenshot shows normal `ＴＥＳＴ` followed by a malformed/insufficient accented glyph. The expected clearly extended 16-row `Ế` was **not** observed.

Important:

- game still boots;
- surrounding `ＴＥＳＴ` remains normal;
- failure is target-glyph rendering/extended-height behavior, not a global text corruption;
- do **not** treat 12x16 as proven yet.

## What remains proven from 0.6.2.x

Native custom atlas:

```text
atlas file   = SLPS + 0x5C4EC
mapping file = SLPS + 0x6B6CC
atlas RAM    = 0x8006BCEC
mapping RAM  = 0x8007AECC
860 glyphs
72 bytes/glyph
12x12
4bpp
LOW nibble first
```

Confirmed mappings:

```text
0x8273 Ｔ -> glyph 481
0x8264 Ｅ -> glyph 466
0x8272 Ｓ -> glyph 480
0x889F 亜 -> glyph 0
```

`0.6.2.13 STATIC SLOT / NO HOOK` proved that direct static-atlas replacement renders a custom Vietnamese glyph at runtime without breaking other text.

Therefore the Vietnamese font pipeline itself is real; the unresolved problem is **vertical capacity / extended-height rendering**.

## 0.6.3.0 design that failed

The experiment attempted target-only extended rendering:

- remap `0x889F` to diagnostic slot 850;
- place a 12x16 / 96-byte `Ế` beginning at the normal slot-850 address;
- target-only hook to set source/copy height to 16 rows;
- target-only hook to set visible sprite height to 16;
- leave untouched glyphs at native 12x12.

Native atlas pointer math is still hardcoded around:

```text
0x8003C4F8  sll  v0,v1,3
0x8003C4FC  addu v0,v0,v1
0x8003C500  sll  a1,v0,3
```

which computes `glyph_index * 72`.

## Do not assume the cause yet

Possible causes to investigate next, **not yet proven**:

1. one of the height hooks did not reach the actual Character Select copy/draw path;
2. source row count changed but an intermediate buffer is still sized for the native path;
3. visible primitive/sprite is still clipping to native height elsewhere;
4. 96-byte source placed inside the 72-byte-stride atlas is not safe for the way the renderer fetches/caches the glyph;
5. converted glyph buffer footprint or row pitch differs from the assumption used by 0.6.3.0;
6. there is an additional height/UV/texture-window field not yet patched.

Do not return to endless 12x12 accent pixel polishing. The user explicitly prefers solving the structural height limitation because stacked Vietnamese marks such as `Ể` and `Ẳ` are not production-quality inside two spare rows.

## NEXT TASK FOR NEW CHAT

Start from `HANDOFF_CURRENT.md` on branch:

```text
gaia-character-select-font-atlas-reverse-01
```

Then:

1. inspect/reconstruct the exact 0.6.3.0 builder/hook locations;
2. disassemble the full target render path from final glyph pointer through copy/unpack to GPU primitive creation;
3. identify every field controlling source rows, destination buffer size, sprite height, row pitch and clipping;
4. build the next probe only after proving where the 16-row path failed;
5. keep the next runtime test at Character Select and maximize information per test.

Do **not** ask the user to retest 0.6.3.0.

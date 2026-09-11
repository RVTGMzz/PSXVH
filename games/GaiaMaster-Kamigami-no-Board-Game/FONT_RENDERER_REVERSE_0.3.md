# Gaia Master — Font renderer reverse / custom Vietnamese glyph test 0.3

## Breakthrough

Static reverse of `SLPS_020.75` found the actual text-rendering split between Japanese 2-byte Shift-JIS and single-byte BIOS font.

### Renderer function

Relevant renderer loop is around virtual address `0x80036460`.

At `0x800364D0`, the original game checks a global font/region mode. When that global is zero it reads two bytes and calls the BIOS KROM path; when non-zero it uses the single-byte font path.

### Japanese path

At `0x800364E4` the game reads two bytes, combines them into a 16-bit Shift-JIS code and calls the BIOS wrapper at `0x80068208`.

That wrapper is the standard PS1 BIOS `B(51h) Krom2RawAdd` trampoline.

This confirms the normal Japanese renderer obtains 16x15 glyphs through the BIOS KROM character set.

### Single-byte path

At `0x80036528` / `0x80036544`, the original code constructs base address:

```text
BFC7F8DE
```

This is the PS1 BIOS 8x15 single-byte/ASCII character set.

The glyph address calculation is effectively:

```text
glyph = base + (byte - 0x21) * 15
```

The helper at `0x80036788` scans 15 rows and bits 7..0, confirming an 8x15, 1 byte-per-row bitmap layout.

## Why the previous ASCII test failed

The old ASCII test only replaced text bytes. The Japanese build still had the renderer in Japanese/2-byte mode, so ASCII bytes were consumed in pairs and interpreted as Shift-JIS. That is why the game showed random symbols.

Therefore the old result does **not** mean the renderer cannot draw single-byte Latin; it means text encoding and renderer mode did not match.

## Font Test 0.3 design

A diagnostic build named `GaiaMaster_VI_Font_Test_0.3_CUSTOM_GLYPH` was created.

It intentionally:

1. forces the renderer to the single-byte path for the test;
2. redirects the single-byte font base away from BIOS ROM to a custom atlas in executable RAM;
3. injects an 8x15 1bpp atlas into an unused zero-filled region of `SLPS_020.75`;
4. assigns custom one-byte codes to Vietnamese uppercase accented glyphs;
5. replaces the first intro lines so the result is visible immediately after cold boot.

### Custom atlas

```text
SLPS file offset: 0x6FE10
RAM address:      0x8007F610
size:             3345 bytes
range:            byte codes 0x21..0xFF
format:           8x15, 15 bytes/glyph, bit7 = leftmost pixel
```

The chosen region was verified to be zero-filled in the clean executable before injection.

Printable ASCII keeps normal code values. Vietnamese uppercase accented characters are mapped to custom bytes starting at `0x80`.

The atlas currently contains all 67 non-ASCII uppercase Vietnamese characters needed for a full uppercase Vietnamese codepage.

## Visible runtime test

The first intro screens are replaced with:

```text
TIẾNG VIỆT
Ă Â Ê Ô Ơ Ư Đ
Á À Ả Ã Ạ
Ắ Ằ Ẳ Ẵ Ặ
Ế Ề Ể Ễ Ệ
Ớ Ờ Ở Ỡ Ợ
Ứ Ừ Ử Ữ Ự
```

No deep gameplay testing is needed.

## Builder verification

Local builder verification on the clean BIN passed:

```text
[OK] GAIA MASTER VI FONT TEST 0.3 BUILD SUCCESS
Patched text locations: 11
Touched nested BDP entries: 1 [29]
Changed raw sectors: 6
Output SHA1: 5099867923398aad35c59ca177c24409a41514d6
```

Runtime result is still pending user test.

## Important diagnostic caveat

The 0.3 build forces single-byte mode globally. Therefore Japanese text after the intro may render incorrectly. This is expected and irrelevant to this diagnostic.

Only the intro accented glyphs should be judged.

## If 0.3 passes

Next engineering step is a **hybrid renderer**:

- ASCII/custom Vietnamese bytes -> custom single-byte atlas;
- untouched Japanese Shift-JIS -> existing 2-byte KROM path.

This would allow mixed development builds while translation is incomplete and opens the door to a compact 1-byte Vietnamese runtime encoding, which also removes much of the current 2-byte full-width slot pressure.

After hybrid mode is stable, migrate `vi_full` into the custom encoder and continue full translation/repack/graphic patching.

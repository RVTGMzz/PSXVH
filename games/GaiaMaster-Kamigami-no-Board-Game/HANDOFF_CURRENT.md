# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** native 12x12 Vietnamese glyph pipeline is proven but rejected for production stacked diacritics. 0.6.3.0 12x16 was initially marked FAIL, then reclassified after pixel-level review as a **STRUCTURAL EXTENDED-HEIGHT PASS**. Current probe is **0.6.3.1 BASELINE + 16-ROW STRIDE**.

## Source game

- `GaiaMaster - Kamigami no Board Game (Japan).bin`
- MODE2/2352
- serial `SLPS-02075`
- clean BIN SHA1 `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- executable `SLPS_020.75`
- main archive `PRGPACK.BDP`
- stable translation baseline: Alpha 0.6.1 FRONT SHA1 `54d2fb026bc3b71c79861e723caffb4114caa34c`
- working branch: `gaia-character-select-font-atlas-reverse-01`

## Translation status

- Master: 596 rows, `vi_full` = accented source-of-truth.
- Alpha 0.6.1 FRONT: 397 runtime-stable patches.
- 230 rows pending due fixed-slot/full-width overflow.
- mixed JP/VI + graphic-text menus remain after font work.

## Encoding rules

- Shift-JIS Japanese: OK.
- Full-width Latin CP932: OK runtime.
- ASCII 1-byte: FAIL/mis-render; do not use runtime control text.
- UTF-8 direct: not used.

## Character Select probe

```text
PRGPACK.BDP + 0xBFD2C
owner nested BDP = entry 29
local offset = +0x580
```

Native control historically:

```text
ＴＥＳＴ亜
82 73 82 64 82 72 82 73 88 9F
```

## Custom font path — proven

```text
atlas RAM    = 0x8006BCEC
mapping RAM  = 0x8007AECC
atlas file   = SLPS + 0x5C4EC
mapping file = SLPS + 0x6B6CC
```

Native atlas:

```text
860 glyphs
72 bytes/glyph
12x12 pixels
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

Native full-width `Ｅ` = glyph 466 style reference.

## Rejected paths

- Krom2RawAdd direct/global wrapper path does not control Character Select target glyph.
- Do not return to Krom hooks.
- Do not return to endless stacked-diacritic pixel polishing inside native 12x12.
- 0.6.2.18 has already been tested; never request a retest.

## 0.6.2.x conclusion

### 0.6.2.13 STATIC SLOT / NO HOOK — BREAKTHROUGH PASS

Direct static-atlas glyph replacement visibly renders custom Vietnamese data while surrounding text remains normal.

=> Vietnamese custom glyph pipeline is proven.

### 0.6.2.14..0.6.2.20

Production stacked marks inside 12x12 remain cramped. Compact-body strategy makes accented capitals too small; full-height body leaves only two accent rows.

=> Native 12x12 is rejected for production stacked Vietnamese marks such as `Ế`, `Ể`, `Ẳ`, `Ỗ`, `Ử`, `Ấ`, `Ố`.

## Extended-height renderer reverse

Character renderer:

```text
0x8003C210
```

Custom mapping/atlas branch:

```text
0x8003C4DC .. 0x8003C51C
```

Native glyph pointer math hardcodes:

```text
glyph_index * 72
```

near:

```text
0x8003C4F8
0x8003C4FC
0x8003C500
```

### Glyph metadata struct produced by 0x8003C210

Relevant fields:

```text
+0  glyph width metric
+2  source/copy height metric
+4  source glyph pointer
+8  custom-atlas flag
```

### Wide-glyph source copy / unpack

Function:

```text
0x8003C67C
```

Wide path reads 6 source bytes per row and writes 8 destination/cache bytes per row.

Therefore:

```text
native 12 rows -> 96 converted bytes
extended 16 rows -> 128 converted bytes
```

The loop count genuinely comes from metadata `+2`, so target height 15 means 16 processed rows.

### Descriptor width/height

The character descriptor is 16 bytes. Relevant bytes:

```text
+4/+5 = texture UV
+6    = visible width
+7    = visible height
```

Draw path later copies descriptor +6/+7 into the variable-size sprite primitive, so a target-specific visible height 16 is architecturally valid.

## 0.6.3.0 EXTENDED HEIGHT 12x16 — RECLASSIFIED STRUCTURAL PASS

0.6.3.0 used:

- 12x16 / 96-byte target source;
- target metadata height = 16 rows;
- target visible sprite height = 16;
- native glyphs untouched at 12x12.

It was initially called FAIL because the glyph looked wrong. Pixel-level review of the screenshot shows the opposite technical result:

- extra headroom/accent pixels are visible;
- target footprint is taller;
- the complete E body appears lower than surrounding `TEST`;
- that body shift is exactly expected because baseline correction was intentionally omitted.

=> **12x16 source/copy/display path is structurally proven.**

Historical file `FONT_ISOLATION_0.6.3.0_FAIL.md` has been updated with the correction.

Do not retest 0.6.3.0.

## Missing production fixes found after deeper reverse

### 1. Baseline

Native E body begins at source row 2.
Extended E body in the diagnostic begins at row 6.

Difference:

```text
+4 rows
```

So the extended target descriptor Y must be shifted **-4 px**.

Descriptor Y source/store is around:

```text
0x8003CD08 .. 0x8003CD10
```

### 2. Converted RAM / VRAM cache stride

0.6.3.0 copied 16 rows but native post-copy allocator still used the global 12-row font height.

Native advances:

```text
0x8003CD94 .. 0x8003CDA4
    converted-glyph pointer += (fontHeight+1) * 8

0x8003CDA8 .. 0x8003CDB4
    VRAM glyph Y += (fontHeight+1)
```

For native Character Select:

```text
12 rows -> +96 converted bytes, +12 VRAM rows
```

Extended target needs:

```text
16 rows -> +128 converted bytes, +16 VRAM rows
```

Without this fix a following glyph can overlap/corrupt the extended target cache footprint.

## CURRENT PROBE — 0.6.3.1 BASELINE + 16-ROW STRIDE

Keep the proven 0.6.3.0 16-row source/copy/sprite path.

Add only:

1. target descriptor Y shift `-4 px`;
2. target converted-buffer pointer advance = 128 bytes;
3. target VRAM Y advance = 16 rows.

Control string becomes:

```text
ＴＥＳＴ亜Ａ
```

Expected visible result:

```text
ＴＥＳＴẾＡ
```

Why trailing `Ａ` exists:

- it checks that a normal native glyph immediately after a 16-row target is not overlapped/corrupted;
- if `Ế` aligns with `TEST` and `Ａ` is intact, extended-height cache allocation is production-viable.

## Long-term after 0.6.3.1 passes

1. move extended Vietnamese source data to production-safe storage rather than diagnostic overlap inside native 72-byte atlas slots;
2. build full Vietnamese glyph inventory;
3. compact runtime codepage/mapping without breaking untranslated Japanese;
4. encode `vi_full` with accents;
5. solve/repack 230 pending rows;
6. clean mixed JP/VI;
7. patch graphic menus/title text;
8. full runtime QA + reproducible build.

## Windows builder pitfalls

- avoid parsing `(Japan).bin` inside parenthesized BAT blocks;
- launcher ASCII + CRLF;
- current test PC Python: `C:\Python312\python.exe`;
- Japanese JSON: explicit UTF-8 or `ensure_ascii=True`.

## User testing preference

- Character Select visible probes;
- no deep gameplay unless necessary;
- maximize information per test;
- never repeat already-tested builds;
- structural renderer fixes are preferred over cosmetic one-pixel iteration.

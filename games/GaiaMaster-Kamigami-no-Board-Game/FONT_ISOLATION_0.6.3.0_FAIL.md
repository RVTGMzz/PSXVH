# Gaia Master — Font Isolation 0.6.3.0 EXTENDED HEIGHT 12x16 — RECLASSIFIED

Runtime test date: **2026-09-12**

> Historical filename still says `FAIL`, but the technical conclusion has been corrected after pixel-level review of the runtime screenshot.

## Corrected result

0.6.3.0 is **NOT a structural 12x16 failure**.

The runtime screenshot shows:

- surrounding `ＴＥＳＴ` remains native and normal;
- the target glyph has a taller visible footprint;
- extra accent/headroom pixels are visible above the base letter;
- the native E body appears lower than surrounding text, exactly as expected because 0.6.3.0 intentionally had **no baseline correction**;
- the full E body is present rather than being reduced to the first 12 source rows.

Therefore the primary diagnostic question:

> Can Gaia Master process/display a target glyph taller than the native 12-row cell?

is answered **YES**.

Reclassification:

```text
0.6.3.0 = STRUCTURAL 12x16 PASS
           + production layout/cache-stride incomplete
```

## What 0.6.3.0 proved

Target-only path used:

- source glyph: 12x16 / 96 bytes;
- target code: `0x889F`;
- custom source slot: 850;
- source-copy metadata height: 16 rows;
- visible sprite height: 16 pixels;
- untouched Japanese/Latin remained native 12x12.

Native custom font facts remain:

```text
atlas file   = SLPS + 0x5C4EC
mapping file = SLPS + 0x6B6CC
atlas RAM    = 0x8006BCEC
mapping RAM  = 0x8007AECC
native glyph = 12x12, 4bpp, 72 bytes
```

## Reverse finding after the screenshot review

The full render path was traced farther.

### Source copy/unpack

`0x8003C67C` consumes the glyph metadata struct built by `0x8003C210`.

For wide glyphs it reads **6 source bytes per row** and writes **8 destination bytes per row**:

```text
native 12 rows -> 12 * 8 = 96-byte converted footprint
extended 16 rows -> 16 * 8 = 128-byte converted footprint
```

The row loop count comes from glyph metadata `+2`, so the 0.6.3.0 16-row metadata hook can genuinely make this routine process 16 rows.

### Missing production stride in 0.6.3.0

After the copy, native code still advances two cache/allocation cursors from the global font height at `s1+64`:

```text
0x8003CD94 .. 0x8003CDA4
    converted-glyph RAM pointer += (fontHeight+1) * 8

0x8003CDA8 .. 0x8003CDB4
    VRAM glyph Y cursor += (fontHeight+1)
```

For Character Select native height is 12 rows, so 0.6.3.0 still advanced:

```text
RAM:  96 bytes
VRAM: 12 rows
```

while the target glyph actually needs:

```text
RAM:  128 bytes
VRAM: 16 rows
```

This is harmless enough for a single last diagnostic glyph to show, but it is not production-safe for following glyphs.

### Baseline

Native `Ｅ` body starts at source row 2.
Extended diagnostic `Ế` body starts at row 6.

Difference:

```text
+4 rows
```

So the target visible Y must be shifted **up 4 px** to align the base-letter body with native surrounding text.

## Next probe — 0.6.3.1

Do not retest 0.6.3.0.

0.6.3.1 keeps the proven 16-row source/copy/sprite path and adds only the two missing production-layout fixes:

1. target descriptor Y `-4 px` baseline correction;
2. target cache allocation stride = 16 rows / 128 converted bytes.

Control line is extended to:

```text
ＴＥＳＴ亜Ａ
```

Expected:

```text
ＴＥＳＴẾＡ
```

The trailing native `Ａ` checks that a glyph following the 16-row target is not overlapped/corrupted by a stale 12-row cache stride.

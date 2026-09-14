# Gaia Master 0.6.55.1 — Batch45R2 Font Micro Polish

Updated: **2026-09-15**

## Runtime evidence that triggered R2

A gameplay screenshot from the exact Batch45 line `Thế giới đổi chủ` confirms the old front-face garbage-glyph problem is substantially improved, but **0.6.55.0 is not Runtime PASS**.

Visible font issues remain:

1. lowercase `đ` still does not read naturally as `đ`;
2. its horizontal stroke needs to move **one further pixel upward** versus 0.6.55.0 and must cross the real right-hand ascender of lowercase `d`;
3. circumflex `^` in `â/ê/ô` is too close to the base body;
4. circumflex/breve + tone combinations can visually merge because the structural mark and tone mark occupy the same tiny top band;
5. no runtime evidence currently proves uppercase `Đ` itself was bad before Batch45.

## Why Đ and đ are now separate

The old generator treated both as one generic `stroke` family and anchored the bar to `x0`.

That is geometrically wrong:

- uppercase `D` has its primary vertical stem on the **left**;
- lowercase `d` has its ascender on the **right**.

R2 therefore separates them:

```text
Đ -> left-stem rule, pre-Batch45 vertical placement
đ -> detect right-side vertical stem, cross through that stem,
     one pixel higher than 0.6.55.0
```

The lowercase stem detector searches only the right half of the native `d`, prioritizing the longest continuous vertical run and actual fill pixels. A fixed 4-pixel bar is then clamped inside the 12x12 cell while being required to contain the detected stem.

## Circumflex / breve fix

The 0.6.55.0 generator used the normal two-row top reservation for all top accents. `draw_dual()` adds a down-right shadow, so the shadow of `^` / breve can fall onto the first body row.

R2 changes only the structural families:

```text
circumflex / breve top reservation: 2 rows -> 3 rows
structural mark: raised 1 pixel
```

This keeps the same native 12x12 architecture while preventing the structural accent shadow from being written onto the body row.

For stacked forms such as `ấ/ầ/ẩ/ẫ`, `ế/ề/ể`, `ố/ồ/ổ/ỗ` and `ắ`, the tone mark is moved to a separate side lane instead of reusing the same coordinates as the structural mark. Breve gets a wider side lane than circumflex because it is physically wider.

## Scope lock

Frozen production codepage remains exactly **60 glyphs**.

R2 changes only:

- `Đ`, `đ`;
- every currently frozen glyph containing circumflex or breve.

All other frozen glyphs must remain **byte-identical** to the 0.6.55.0 generator. This is an explicit build gate, not a convention.

## New builder

```text
tools/build_gaia_06551_batch45r2_font_micro_polish.py
tools/00_BUILD_0.6.55.1_BATCH45R2_FONT_POLISH.cmd
```

The builder first reproduces 0.6.55.0 from CLEAN ROM, then applies a **font-only SLPS patch**. It does not rewrite the historical 0.6.55.0 builder.

## Safety gates

R2 must block the build if any of these fail:

```text
CLEAN BIN SHA1 = f4d5298583c90d89c4b7e51d2dde160ee07f2aec
Batch42 exact contract preserved = 560/560
Batch45 intro polish preserved = 19/19
PRGPACK unchanged by R2 font patch = byte-for-byte
frozen codepage = 60 glyphs
all glyphs = exactly 72 bytes
all final glyph bounding boxes = inside 12x12
all unaffected glyphs = byte-identical to 0.6.55.0
Đ = uppercase left-stem rule
đ = lowercase right-stem rule
structural/tone rendered pixels = no collision
written glyphs = read back and byte-verified after EDC/ECC regeneration
```

Batch43's 102 visible fields are inherited from the already-verified 0.6.55.0 build path; because R2 changes only SLPS font sectors and requires PRGPACK to remain byte-for-byte unchanged, the `560 + 102 = 662` exact contract is not rewritten by this patch.

## Architecture remains frozen

```text
native 12x12 / 72-byte / 4bpp / LOW nibble first
static mapping-only
frozen 60-glyph Vietnamese codepage
```

Still forbidden:

- renderer hook;
- pointer redirect;
- 12x16;
- 6x12;
- composite overlay.

## Runtime gate

**0.6.55.1 is not Runtime PASS from static evidence.**

After a successful CLEAN-ROM build, inspect at minimum:

1. lowercase `đ` in `đổi`;
2. uppercase `Đ` when a visible string contains it;
3. plain `â`, `ê`, `ô`;
4. at least one stacked circumflex+tone glyph such as `ấ/ế/ố` when reachable;
5. `ă/ắ` if reachable;
6. regression check on ordinary accented glyphs outside the changed family.

Only gameplay screenshots can close this font gate.

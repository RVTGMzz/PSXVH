# Gaia Master — Character Select custom glyph cache/font atlas reverse 0.1

## Mục tiêu

Visible probe chuẩn dùng full-width CP932:

```text
ＴＥＳＴ亜
```

Mục tiêu cuối:

```text
ＴＥＳＴẾ
```

Không quay lại hook `Krom2RawAdd`: direct caller #1, direct caller #2 và global safe wrapper đều không chạm glyph Character Select.

## Source-of-truth

- clean BIN SHA1: `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- Alpha 0.6.1 FRONT SHA1: `54d2fb026bc3b71c79861e723caffb4114caa34c`
- `SLPS_020.75` SHA1: `1dfeb6b7cfda59c108dde2dc0b8abda9a40e6ae5`
- `PRGPACK.BDP` SHA1: `a9b195b8ae5d8cad7f4f755daa08337d4671632c`
- Character Select text: `PRGPACK + 0xBFD2C`
- owner nested BDP: entry 29
- local offset: `+0x580`

## Custom atlas path

Renderer function around `0x8003C210` has two glyph sources.
Character Select uses custom mapping/atlas branch:

```text
0x8003C4DC sll  v0,v0,1
0x8003C4E0 lw   v1,0x51C(gp)   # mapping base
0x8003C4E4 lw   a0,0x518(gp)   # atlas base
0x8003C4E8 addu v0,v0,v1
0x8003C4EC lhu  v1,0(v0)       # glyph index
0x8003C4F8 sll  v0,v1,3
0x8003C4FC addu v0,v0,v1
0x8003C500 sll  a1,v0,3        # glyph_index * 72
0x8003C504 addu a0,a0,a1       # final glyph pointer
```

Default pointers:

```text
atlas RAM   = 0x8006BCEC
mapping RAM = 0x8007AECC
atlas file  = SLPS + 0x5C4EC
mapping file= SLPS + 0x6B6CC
```

Mapping confirmed:

```text
0x8273 Ｔ -> glyph 481
0x8264 Ｅ -> glyph 466
0x8272 Ｓ -> glyph 480
0x889F 亜 -> glyph 0
```

## Atlas format

```text
860 glyphs
72 bytes/glyph
12x12 pixels
4bpp
LOW nibble first
```

`Ｅ` full-width = glyph 466 and is style/palette reference.

## Native 12x12 probe conclusion

### 0.6.2.13 STATIC SLOT / NO HOOK — PASS

Direct static atlas replacement works at runtime while other text stays normal.

=> custom Vietnamese glyph pipeline is proven.

### 0.6.2.14..0.6.2.20

Multiple compact/full-height/AA/variant-grid attempts showed that production stacked Vietnamese marks do not fit cleanly in native 12x12 while preserving base-letter size.

Reject native 12x12 for production `Ế, Ể, Ẳ, Ỗ, Ử, Ấ, Ố...`.

## Extended-height reverse — 0.6.3.x

### Glyph metadata

Relevant struct fields:

```text
+0  width metric
+2  source/copy height metric
+4  source glyph pointer
+8  custom-atlas flag
```

### Wide custom copy/unpack

Function:

```text
0x8003C67C
```

Two branches exist based on width metric, but both advance source 6 bytes per row and destination 8 bytes per row.

Wide branch core:

```text
row source: 3 halfwords = 6 bytes
row dest:   3 halfwords + zero halfword = 8 bytes
```

Loop count comes from metadata `+2` as `(heightMetric + 1)`.

Therefore:

```text
12x12 source = 72 bytes
12 rows converted = 96 bytes

12x16 source = 96 bytes
16 rows converted = 128 bytes
```

### Descriptor fields

```text
+4/+5 = texture U/V
+6    = visible width
+7    = visible height
```

## 0.6.3.0 — structural 12x16 pass

A 12x16 / 96-byte target with metadata height=15 produces a taller target footprint. Baseline was intentionally not corrected.

Do not retest.

## 0.6.3.1 — unsafe shared-stride failure

Target baseline correction plus rewriting shared cache RAM/VRAM cursor advance around:

```text
0x8003CD94..0x8003CDB4
```

caused global Japanese corruption and later freeze.

=> never repeat naive shared cursor rewrite.

## 0.6.3.2 — stable baseline-only pass

Keeps 16-row target path, adds only Y -4.

Stable runtime, trailing A sentinel intact, but target lower rows missing.

## 0.6.3.3 — EOL overwrite disproven

Target moved to end-of-line. Lower rows still missing.

=> following glyph does not overwrite target bottom.

## 0.6.3.4 — UV +4 negative diagnostic

Only target texture V was shifted +4.

Runtime remained stable but lower native E did not reappear cleanly/correctly.

=> simple wrong texture-V/window model is insufficient.

Do not retest.

## VRAM/cache page reverse after 0.6.3.4

Font cache initialization function begins around:

```text
0x8003D3EC
```

Default parameters when no custom config is supplied include:

```text
sp+0x1A = 256   # VRAM/cache Y base
sp+0x1C = 32    # cache page width parameter
sp+0x1E = 240   # cache page height
```

State setup:

```text
state+40 = page start Y
state+42 = state+40 + pageHeight - 1
state+48 = page start X
state+50 = current cache Y cursor
state+96 = upload RAM base
state+100 = current converted-cache write pointer
```

Per-character copy calls:

```text
0x8003CC38  jal 0x8003C67C
```

with destination:

```text
state+100
```

### Final page flush

Function around:

```text
0x8003DB78..0x8003DBE0
```

queues VRAM upload only when cache contains glyph data.

RECT uses:

```text
x = state+48
y = state+40
w = 4
h = state+42 - state+40 + 1
source = state+96
```

With default setup this is a cache-page upload roughly 240 rows high, not a single 12-row glyph upload.

=> lower-row loss is not explained by `RECT.h` being hardcoded to native glyph height.

## CURRENT — 0.6.3.5 POST-COPY RAM SENTINEL

Clean hook site after successful `0x8003C67C` copy:

```text
0x8003CC4C
```

Target `0x889F` only, using current converted destination `state+100`.

Overwrite converted rows:

```text
rows 10..11 = full palette-index-7 band  # control
rows 12..15 = full palette-index-1 band  # bright test
```

Purpose:

> Determine whether converted RAM rows 12..15 survive into VRAM/sprite display.

Interpretation:

- both bands visible => post-copy RAM rows12..15 survive; investigate source/copy glyph construction;
- only rows10..11 control visible => loss occurs after converted RAM row11;
- neither visible => sentinel hook/target condition did not execute, no clipping conclusion.

Package:

```text
GaiaMaster_FontIsolation_0.6.3.5_POST_COPY_RAM_SENTINEL.zip
```

## Reference files

```text
HANDOFF_CURRENT.md
LATEST.md
PROBE_BUILD_INDEX.md
FONT_ISOLATION_0.6.3.1_UNSAFE_FAIL.md
FONT_ISOLATION_0.6.3.2_STABLE_PASS.md
FONT_ISOLATION_0.6.3.3_EOL_OVERWRITE_TEST.md
FONT_ISOLATION_0.6.3.4_UV_WINDOW_TEST.md
FONT_ISOLATION_0.6.3.5_POST_COPY_RAM_SENTINEL.md
```

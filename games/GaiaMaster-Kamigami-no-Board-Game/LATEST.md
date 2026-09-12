# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-12 sau pixel-level review của runtime 0.6.3.0**.

## Chốt mới nhất

- 0.6.2.x đã chứng minh custom Vietnamese glyph pipeline hoạt động.
- Native production 12x12 bị loại cho stacked Vietnamese diacritics vì quá chật.
- **0.6.3.0 EXTENDED HEIGHT 12x16 được reclassify thành STRUCTURAL PASS**, không phải renderer failure.

## Vì sao 0.6.3.0 được reclassify

Runtime screenshot cho thấy:

- `ＴＥＳＴ` native bình thường;
- target glyph có footprint cao hơn;
- vùng dấu nằm cao hơn;
- thân E đầy đủ nằm thấp xuống so với surrounding text.

Đó chính là hành vi expected của probe đầu tiên vì 0.6.3.0 cố tình chưa sửa baseline.

=> Gaia Master **có thể copy/display target 16-row glyph**.

## Renderer reverse mới

Native atlas:

```text
atlas file   = SLPS + 0x5C4EC
mapping file = SLPS + 0x6B6CC
860 glyphs
12x12
4bpp
72 bytes/glyph
LOW nibble first
```

Wide-glyph unpack/copy routine:

```text
0x8003C67C
```

For each source row:

```text
6 source bytes -> 8 converted/cache bytes
```

Therefore:

```text
12 rows = 96-byte converted footprint
16 rows = 128-byte converted footprint
```

0.6.3.0 changed target source-copy height and visible sprite height to 16, but native post-copy allocation still used global 12-row height at:

```text
0x8003CD94..0x8003CDA4  # destination RAM pointer advance
0x8003CDA8..0x8003CDB4  # VRAM Y cursor advance
```

So the next production-safe extended glyph needs target-specific 16-row stride.

## Baseline finding

Native E body begins at row 2.
Extended diagnostic E body begins at row 6.

=> target glyph needs visible Y correction:

```text
-4 px
```

## NEXT — 0.6.3.1 BASELINE + 16-ROW STRIDE

Control:

```text
ＴＥＳＴ亜Ａ
```

Expected:

```text
ＴＥＳＴẾＡ
```

0.6.3.1 keeps the proven extended path and adds:

1. target descriptor Y `-4 px`;
2. target converted-buffer pointer advance `16*8 = 128 bytes`;
3. target VRAM Y advance `16 rows`.

The trailing native full-width `Ａ` is deliberate. It verifies the glyph after an extended target is not overlapped/corrupted.

## Long-term after 0.6.3.1

1. production-safe external/extended Vietnamese atlas storage;
2. full Vietnamese glyph inventory;
3. compact runtime codepage/mapping;
4. encode `vi_full` with accents;
5. solve/repack 230 pending overflow rows;
6. clean mixed JP/VI;
7. patch graphic menu/title text;
8. full runtime QA + reproducible build.

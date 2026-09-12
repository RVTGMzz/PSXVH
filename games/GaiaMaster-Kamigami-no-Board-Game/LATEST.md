# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-12 sau runtime test 0.6.3.0 EXTENDED HEIGHT 12x16 — FAIL**.

## Chốt kỹ thuật

- BDP checksum reverse + verify 60/60 nested + top-level.
- MODE2/Form1 patcher + EDC/ECC ổn định.
- Full-width Latin CP932/Shift-JIS: OK.
- ASCII 1-byte: FAIL/mis-render, không dùng.
- Alpha 0.6.1 FRONT là baseline runtime ổn định: **397 patch**, SHA1 `54d2fb026bc3b71c79861e723caffb4114caa34c`.
- Translation master: **596 vị trí**; **230 dòng pending** vì full-width 2-byte overflow slot.

## Custom font path đã reverse

Visible probe:

```text
PRGPACK.BDP + 0xBFD2C
owner nested BDP: entry 29
local offset: +0x580
```

Native custom font:

```text
atlas static:    SLPS + 0x5C4EC
mapping static:  SLPS + 0x6B6CC
atlas RAM:       0x8006BCEC
mapping RAM:     0x8007AECC
860 glyphs
72 bytes/glyph
12x12 pixels
4bpp
LOW nibble first
```

Mapping confirmed:

```text
0x8273 Ｔ -> glyph 481
0x8264 Ｅ -> glyph 466
0x8272 Ｓ -> glyph 480
0x889F 亜 -> glyph 0
```

## 0.6.2.x conclusion

### 0.6.2.13 — BREAKTHROUGH PASS
Direct static-atlas replacement renders a Vietnamese custom glyph at runtime while other text stays normal.

=> **Vietnamese glyph pipeline PASS.**

### 0.6.2.14–0.6.2.20
Tried many full-height/compact accent geometries inside native 12x12.

Final production conclusion:

> **12x12 is structurally too cramped for stacked Vietnamese diacritics** if the native base-letter body must remain full-size.

This is especially problematic for `Ế`, `Ể`, `Ẳ`, `Ỗ`, `Ử`, `Ấ`, `Ố`, etc.

=> Stop polishing production stacked marks inside 12x12.

## 0.6.3.0 EXTENDED HEIGHT 12x16 — runtime result

Goal: prove that one target Vietnamese glyph can use **12x16 / 96 bytes** while untouched Japanese/Latin remains native 12x12.

Runtime screenshot:

- `ＴＥＳＴ` remains normal;
- final target glyph is malformed / still does not show a clearly extended 16-row `Ế`;
- game boots, so failure is localized to extended target-glyph behavior.

=> **0.6.3.0 FAIL. 12x16 is NOT proven yet.**

Do not ask user to retest 0.6.3.0.

Full failure note:

```text
FONT_ISOLATION_0.6.3.0_FAIL.md
```

## What 0.6.3.0 attempted

- remap `0x889F` to diagnostic slot 850;
- write a 12x16 / 96-byte `Ế` at the slot-850 source position;
- target-only height hook for 16 copied source rows;
- target-only visible sprite-height hook for 16 pixels;
- leave all untouched glyphs native 12x12.

Native atlas stride math remains hardcoded as `glyph_index * 72` around:

```text
0x8003C4F8
0x8003C4FC
0x8003C500
```

## Immediate next reverse task

Do **not** guess another height patch yet.

Next chat should trace the complete target render path after final glyph pointer generation and identify every field controlling:

1. source row count;
2. source row pitch / 4bpp unpacking;
3. converted glyph buffer size;
4. destination/cache allocation;
5. visible sprite/primitive height;
6. UV/texture-window/clipping behavior.

Main possibilities still unresolved:

- target height hook may not affect the actual Character Select copy path;
- intermediate buffer may still be native-sized;
- GPU primitive may still clip at native height;
- 96-byte source inside a 72-byte-stride atlas may be unsuitable;
- another metric/height field may exist.

## After extended-height path is truly solved

1. build full Vietnamese glyph inventory;
2. design compact runtime codepage/mapping;
3. encode `vi_full` with accents;
4. solve/repack 230 pending overflow rows;
5. clean mixed JP/VI;
6. patch graphic menu/title text;
7. full runtime QA + reproducible final build.

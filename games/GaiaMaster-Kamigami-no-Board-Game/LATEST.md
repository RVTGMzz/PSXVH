# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-12 sau 0.6.2.19/0.6.2.20**, chuyển hướng sang **0.6.3.0 EXTENDED HEIGHT 12x16**.

## Chốt kỹ thuật

- BDP checksum reverse + verify 60/60 nested + top-level.
- MODE2/Form1 patcher + EDC/ECC ổn định.
- Full-width Latin CP932/Shift-JIS: OK.
- ASCII 1-byte: FAIL/mis-render, không dùng.
- Alpha 0.6.1 FRONT là baseline runtime ổn định: 397 patch, SHA1 `54d2fb026bc3b71c79861e723caffb4114caa34c`.
- Translation master: 596 vị trí; 230 dòng pending vì full-width 2-byte overflow slot.

## Custom font path

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
Static atlas replacement works at runtime. Vietnamese glyph pipeline is real; other text stays normal.

### 0.6.2.14 / 0.6.2.15
Compact-body strategy rejected because accented capitals become visibly smaller.

### 0.6.2.16 / 0.6.2.17 / 0.6.2.18
Full-height body retained, but stacked marks must fit inside only two spare rows. `Ế` can be made recognizable, but quality remains poor/awkward.

### 0.6.2.19 VARIANT GRID
Six variants shown in one runtime line. User selected **sample 2 from the left** as best base shape, but noted:
- too thin;
- lacks shadow/weight;
- circumflex slightly off-center;
- circumflex too attached to E top bar.

### 0.6.2.20 SAMPLE2 REFINED
Refined sample 2 with more weight and centering. Runtime/preview exposed the real production blocker:

> **12x12 itself is too small for Vietnamese stacked diacritics.**

This becomes severe not only for `Ế`, but also `Ể`, `Ẳ`, `Ỗ`, `Ử`, `Ấ`, `Ố`, etc.

=> **Stop spending time polishing stacked Vietnamese marks inside 12x12.**

## New reverse finding — extended height is architecturally possible

Renderer function around `0x8003C210` stores glyph pointer/metrics separately.

Native atlas pointer math is explicitly hardcoded as:

```text
0x8003C4F8  sll  v0,v1,3
0x8003C4FC  addu v0,v0,v1
0x8003C500  sll  a1,v0,3
```

which computes:

```text
glyph_index * 72
```

Downstream glyph copy uses a **separate per-glyph height field**. The visible GPU sprite height is also assigned separately in the caller.

Therefore one diagnostic glyph can be tested at:

```text
12x16
4bpp
96 bytes/glyph
```

without converting the entire Japanese font immediately.

## NEXT — 0.6.3.0 EXTENDED HEIGHT 12x16

First extended-height diagnostic:

- remap `0x889F` to diagnostic atlas slot 850;
- put a 12x16 / 96-byte Vietnamese `Ế` there;
- use target-only safe-cave hooks to make only `0x889F` copy **16 source rows** and draw a **16-pixel-high sprite**;
- leave every untouched Japanese/Latin glyph on the native 12x12 path.

12x16 test layout:

```text
rows 0..5  = dedicated Vietnamese diacritic headroom
rows 6..15 = native E body at original pixel size
```

0.6.3.0 intentionally does **not** correct baseline yet. If successful, final E body may sit ~4 pixels too low. This is acceptable for the first probe.

Primary question:

> Can Gaia Master actually copy and display all 16 rows for a target glyph?

If YES, 0.6.3.1 will handle:
- y-offset/baseline correction;
- expanded glyph buffer accounting;
- production extended-height Vietnamese atlas/codepage.

## After extended-height font passes

1. build full Vietnamese glyph inventory;
2. compact runtime codepage/mapping;
3. encode `vi_full` with accents;
4. solve/repack 230 pending overflow rows;
5. clean mixed JP/VI;
6. patch graphic menus/title text;
7. full runtime QA + reproducible final build.

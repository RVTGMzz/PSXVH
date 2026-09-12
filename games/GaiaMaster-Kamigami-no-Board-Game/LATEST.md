# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-12 sau runtime test 0.6.3.1 BASELINE + 16-ROW STRIDE — UNSAFE FAIL**.

## Chốt kỹ thuật hiện tại

- 0.6.2.x đã chứng minh custom Vietnamese glyph pipeline hoạt động.
- Native 12x12 bị loại cho production stacked diacritics vì quá chật.
- 0.6.3.0 12x16 vẫn được giữ là **STRUCTURAL PASS**: target glyph có footprint cao hơn, extra rows thực sự xuất hiện, body E tụt xuống đúng như probe chưa baseline-correct.
- **0.6.3.1 FAIL nặng**: global text corruption + later game freeze.

## 0.6.3.1 runtime failure

User screenshots show:

- unrelated Japanese text becomes corrupted/repeated;
- Character Select header corrupts;
- probe line no longer behaves as an isolated target (`Ａ/Ｅ`-like corruption appears across the line);
- later screen becomes garbled and game freezes.

=> 0.6.3.1 is **unsafe**. Do not retest.

## Diff 0.6.3.0 -> 0.6.3.1

0.6.3.1 added only two structural experiments on top of 0.6.3.0:

1. target baseline Y correction `-4 px` near `0x8003CD08`;
2. target-specific cache/VRAM advance hook near `0x8003CD94` intended to change native 12-row advance to 16 rows.

The strongest regression suspect is the `0x8003CD94` cache-advance hook because it mutates shared font-cache state:

```text
converted RAM pointer
VRAM glyph Y cursor
```

Once that shared state is desynchronized, all later glyphs can read/write the wrong cache locations, matching the observed global corruption and freeze.

## Important native code around the suspect block

Native sequence:

```text
0x8003CD94  lw    v0,100(s1)
0x8003CD98  sll   v1,v1,3
0x8003CD9C  addu  v0,v0,v1
0x8003CDA4  sw    v0,100(s1)
0x8003CDA8  lhu   v0,50(s1)
0x8003CDAC  addiu v1,v1,1
0x8003CDB0  addu  v0,v0,v1
0x8003CDB4  sh    v0,50(s1)
```

This shared allocator/cursor logic is more global than the 0.6.3.1 assumption allowed.

## NEXT — 0.6.3.2 BASELINE ONLY

High-information rollback probe:

- start from the structurally safe 0.6.3.0 extended-height path;
- keep 16-row source/copy + visible sprite height;
- add **only** target baseline Y `-4 px`;
- **do not patch `0x8003CD94` cache stride/advance at all**;
- add trailing full-width `Ａ` sentinel.

Control:

```text
ＴＥＳＴ亜Ａ
```

Expected diagnostic goal:

```text
ＴＥＳＴẾＡ
```

Interpretation:

- if unrelated text stays normal and game no longer freezes, CD94 advance hook is confirmed as the regression source;
- if `Ａ` after target is damaged but the rest of game remains stable, extended target footprint still needs a safer cache/storage solution;
- if global text corrupts again, stop immediately and revisit earlier 0.6.3.0 assumptions.

## Long-term after a stable 12x16 path

1. production-safe external/extended Vietnamese atlas storage;
2. full Vietnamese glyph inventory;
3. compact runtime codepage/mapping;
4. encode `vi_full` with accents;
5. solve/repack 230 pending overflow rows;
6. clean mixed JP/VI;
7. patch graphic menu/title text;
8. full runtime QA + reproducible build.

# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** custom Vietnamese atlas path is proven. Native 12x12 is rejected for production stacked diacritics. 0.6.3.7 proved lower source rows are not fully visible. 0.6.3.10 used the dataflow-proven current glyph height from `sp+18` and runtime stayed stable but looked identical to 0.6.3.7, so final visible sprite height is not the remaining blocker. Reverse now places the blocker before final primitive sampling, in converted RAM / cache / VRAM placement. Current probe: **0.6.3.11 RAM TAIL MIRROR**.

## Source / baseline

- Game: `GaiaMaster - Kamigami no Board Game (Japan).bin`
- MODE2/2352, serial `SLPS-02075`
- clean BIN SHA1 `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- Alpha 0.6.1 FRONT SHA1 `54d2fb026bc3b71c79861e723caffb4114caa34c`
- executable `SLPS_020.75`
- main archive `PRGPACK.BDP`
- branch `gaia-character-select-font-atlas-reverse-01`

## Translation status

- master 596 rows, `vi_full` accented source-of-truth;
- Alpha 0.6.1 FRONT has 397 runtime-stable patches;
- 230 rows pending because full-width 2-byte text overflows fixed slots;
- mixed JP/VI + graphic text remain after font work.

## Atlas facts

```text
atlas RAM    = 0x8006BCEC
mapping RAM  = 0x8007AECC
atlas file   = SLPS + 0x5C4EC
mapping file = SLPS + 0x6B6CC
860 glyphs
native 12x12 / 72-byte / 4bpp / LOW nibble first
```

Confirmed mappings:

```text
0x8273 Ｔ -> glyph 481
0x8264 Ｅ -> glyph 466
0x8272 Ｓ -> glyph 480
0x889F 亜 -> glyph 0
```

Character Select probe:

```text
PRGPACK.BDP + 0xBFD2C
owner nested BDP = entry 29
local offset = +0x580
```

## Production direction

0.6.2.13 proved direct custom-atlas rendering.
0.6.2.14..20 proved stacked Vietnamese marks such as `Ế/Ể/Ẳ/Ỗ/Ử/Ấ/Ố` do not fit production-quality inside native 12x12 without shrinking the base body.

=> Production direction remains extended height.

## Extended-height renderer facts

Renderer entry:

```text
0x8003C210
```

Glyph metadata struct:

```text
+0 width metric
+2 source/copy height_minus_1
+4 source glyph pointer
+8 custom-atlas flag
```

### Source/copy

Wide copy routine:

```text
0x8003C67C
```

For target custom-atlas metadata width=12, it uses the wide path:

```text
6 source bytes per row -> 8 converted/cache bytes per row
12 rows -> 96 bytes
16 rows -> 128 bytes
```

Height=15 genuinely drives 16 iterations.

### Caller metadata lifetime

```text
0x8003CAC0  a2 = sp+16
0x8003C210  writes metadata there
0x8003CC3C  a1 = sp+16
0x8003C67C  consumes same metadata
```

Current source pointer is therefore `*(sp+20)`.
Current height_minus_1 is `lhu 18(sp)`.

### Converted cache state

Before copy:

```text
0x8003CC34  a2 = *(s1+100)   # current converted destination
```

Native allocator later advances at:

```text
0x8003CD94..0x8003CDB4
```

Do not rewrite this block naively; 0.6.3.1 proved that unsafe.

### VRAM upload

Page upload queue around:

```text
0x8003CDE8..0x8003CE24
```

Cleanup/final page upload around:

```text
0x8003DBA4..0x8003DBE0
```

Upload is page-based, not a hardcoded per-glyph 12-row RECT.

### Final primitive consumer

16-byte glyph output record is consumed around `0x8003D9FC..0x8003DA50`.

Confirmed:

```text
record+4  -> texture U
record+5  -> texture V
record+6  -> primitive width
record+7  -> primitive height
```

Thus sprite record height really reaches final GPU primitive.

## High-value probe history

### 0.6.3.1 — UNSAFE FAIL
Naive shared cache/VRAM cursor stride rewrite caused global corruption + freeze. Never repeat.

### 0.6.3.2 — STABLE WITH LOWER-ROW LOSS
Stable baseline correction, target bottom still missing.

### 0.6.3.3 — EOL OVERWRITE DISPROVEN
Target at end-of-line still loses same bottom.

### 0.6.3.4 — UV+4 NEGATIVE
Texture V shift does not recover bottom.

### 0.6.3.6 — UNSAFE FAIL
Persistent early/global target flag freezes after Sony logo. Never reuse.

### 0.6.3.7 — SOURCE ROW SENTINEL / HIGH VALUE
Target source rows:

```text
rows10..11 = dark/gray full band
rows12..15 = bright white full band
```

Runtime:
- header/TEST normal;
- dark rows10..11 visible;
- rows12..15 do not appear as full 4-row white block;
- only thin bright edge below.

### 0.6.3.8 — DIAGNOSTIC FAIL
Global force-height16 breaks layout.

### 0.6.3.9 — DIAGNOSTIC FAIL
`s3+2` false metadata assumption; runtime vertical TEST/garbage. Reverse proved `s3=s5+15`.

### 0.6.3.10 — STABLE NEGATIVE
Uses proven `lhu 18(sp)` per-current-glyph height. Runtime is **same as 0.6.3.7**.

=> final primitive height is not the missing-row blocker.
=> do not retest 0.6.3.10.

## CURRENT — 0.6.3.11 RAM TAIL MIRROR

Question:

> Do converted rows12..15 exist in RAM immediately after `0x8003C67C` returns?

Target identity does not use late `s0` and does not use global flag.

Use source pointer from current metadata:

```text
*(sp+20) == 0x8007ABFC
```

where:

```text
0x8007ABFC = atlas RAM 0x8006BCEC + slot850 * 72
```

At hook `0x8003CC4C`, before native allocator advance:

```text
dest = *(s1+100)
rows12..15 = dest+96..127
```

Mirror them to visible native area:

```text
rows8..11 = dest+64..95
```

Because source rows12..15 are solid bright sentinel, successful mirror should create an obvious bright 4-row block higher inside the target.

Interpretation:

- bright mirror block appears => converted rows12..15 exist; downstream VRAM/cache placement is the blocker;
- no bright mirror block => lower rows are absent/wrong immediately after conversion, or destination model is wrong.

Package:

```text
GaiaMaster_FontIsolation_0.6.3.11_RAM_TAIL_MIRROR.zip
```

Launcher:

```text
00_RUN_PROBE_06311.cmd
```

## Hard do-not-repeat

- no Krom path;
- no production 12x12 stacked-accent polishing;
- no retest 0.6.2.18;
- no retest 0.6.3.0..0.6.3.10;
- no naive shared `0x8003CD94..0x8003CDB4` rewrite;
- no persistent/global target flag;
- no global force-height16;
- no `s3+2` metadata assumption.

## User testing preference

- Character Select visible probes only when needed;
- maximize information per runtime test;
- never repeat tested builds;
- stop on true freeze/global corruption;
- reverse first, probe second.

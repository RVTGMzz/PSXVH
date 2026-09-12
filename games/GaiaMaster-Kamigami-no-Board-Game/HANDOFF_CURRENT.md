# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** custom Vietnamese glyph pipeline is proven. Native 12x12 is rejected for production stacked diacritics. 0.6.3.0 proves 12x16 structurally. 0.6.3.1 shared cache-stride rewrite is unsafe. 0.6.3.2 is stable with lower-row loss. 0.6.3.3 disproved following-glyph overwrite. 0.6.3.4 UV+4 was negative. 0.6.3.5 late-s0 sentinel did not fire. 0.6.3.6 persistent early-flag froze after Sony logo. 0.6.3.7 source-row sentinel finally proved rows 10..11 display while rows 12..15 do not fully display. 0.6.3.8 global force-height16 broke layout. Current probe is **0.6.3.9 HEIGHT FROM METADATA**.

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

## Encoding facts

- Shift-JIS Japanese OK.
- Full-width Latin CP932 OK runtime.
- ASCII 1-byte fails/mis-renders in this renderer.
- UTF-8 direct not used.

## Character Select probe

```text
PRGPACK.BDP + 0xBFD2C
owner nested BDP = entry 29
local offset = +0x580
```

## Proven custom atlas path

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
12x12
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

Native `Ｅ` glyph 466 is style reference.

## Native 12x12 conclusion

`0.6.2.13 STATIC SLOT / NO HOOK` proved direct static-atlas Vietnamese rendering works. 0.6.2.14..20 proved stacked Vietnamese marks do not fit production-quality inside 12x12 without shrinking the base letter.

=> Production direction is extended height.

## Extended-height facts

Character renderer:

```text
0x8003C210
```

Native custom-atlas pointer math near `0x8003C4F8..0x8003C500` computes `glyph_index * 72`.

Glyph metadata struct:

```text
+0 width metric
+2 source/copy height_minus_1
+4 source glyph pointer
+8 custom-atlas flag
```

Wide custom copy routine:

```text
0x8003C67C
6 source bytes/row -> 8 converted/cache bytes/row
```

Therefore:

```text
12 rows -> 96 converted bytes
16 rows -> 128 converted bytes
```

Metadata height=15 genuinely runs 16 source rows.

Sprite descriptor relevant bytes:

```text
+4/+5 texture U/V
+6 visible width
+7 visible height
```

Font cache page itself is far taller than 12 rows, so a simple page/upload-height=12 explanation is insufficient.

## Probe history

### 0.6.3.0 EXTENDED HEIGHT — STRUCTURAL PASS

12x16 source + 16-row copy + taller footprint is real. Baseline intentionally not corrected. Do not retest.

### 0.6.3.1 BASELINE + 16-ROW STRIDE — UNSAFE FAIL

Naive shared cache/VRAM advance rewrite around `0x8003CD94..0x8003CDB4` caused global corruption and freeze. Never repeat.

### 0.6.3.2 BASELINE ONLY — STABLE WITH LOWER-ROW LOSS

Control `ＴＥＳＴ亜Ａ`. Japanese/TEST stable, A sentinel intact, baseline improved, lower target rows missing.

### 0.6.3.3 EOL OVERWRITE — OVERWRITE DISPROVEN

Target at end-of-line still loses same lower rows.

### 0.6.3.4 UV WINDOW — NEGATIVE

Target texture `V+4` does not restore lower E cleanly.

### 0.6.3.5 POST-COPY SENTINEL — NO SENTINEL

Late `s0` target check at `0x8003CC4C` was unreliable. No conclusion about rows12..15.

### 0.6.3.6 EARLY-FLAG SENTINEL — UNSAFE FAIL

Persistent/global early flag causes repeatable freeze immediately after Sony logo. Never retest. Never use global mutable cave flag for target identity.

### 0.6.3.7 SOURCE ROW SENTINEL — RUNTIME COMPLETE

Diagnostic baked directly into target 12x16 source:

```text
rows 10..11 = full dark/gray band
rows 12..15 = full bright white band
```

Runtime:

- Japanese header and TEST normal;
- dark rows10..11 clearly visible;
- rows12..15 do not appear as a thick 4-row white block;
- only a thin bright edge remains below.

=> source reaches at least rows10..11 and the lower four source rows are not fully visible.
=> this result is independent of late target identity because sentinel is source data.

### 0.6.3.8 FORCE SPRITE HEIGHT16 — DIAGNOSTIC FAIL

Forced visible sprite height=16 for every glyph.

Runtime:

- textbox can become blank;
- `TEST` stacks vertically;
- global text layout is disturbed.

=> `0x8003CCC0`/height path is not safe to force globally.
=> do not retest.

## Current hypothesis

The early metadata stage already stores per-glyph height:

```text
metadata +2 = height_minus_1
native = 11
extended target = 15
```

Earlier target-specific sprite-height probes used late `s0`, which is not trustworthy. 0.6.3.8 removed `s0` but wrongly forced all glyphs to 16.

A cleaner solution is to derive final visible height from the current glyph metadata itself.

## CURRENT — 0.6.3.9 HEIGHT FROM METADATA

Start from stable 0.6.3.7 source-sentinel build.

At sprite-height hook `0x8003CCC0`, replace global/native height load with:

```text
lhu v0,2(s3)   # current glyph metadata height_minus_1
```

then resume at native:

```text
0x8003CCC8 addiu v0,v0,1
```

Expected:

```text
native glyphs: 11+1 = 12px
extended target: 15+1 = 16px
```

No late `s0`, no global force-height16, no flag, no post-copy hook, no UV patch, no shared allocator patch.

Source sentinel remains:

```text
rows10..11 dark/gray
rows12..15 bright white
```

Runtime question:

> Does TEST/native layout return to normal AND does the target finally show a thick 4-row white lower block?

Package:

```text
GaiaMaster_FontIsolation_0.6.3.9_HEIGHT_FROM_METADATA.zip
```

Launcher:

```text
00_RUN_PROBE_0639.cmd
```

## Hard do-not-repeat

- no Krom path;
- no production 12x12 stacked-accent polishing;
- no retest 0.6.2.18;
- no retest 0.6.3.0..0.6.3.8;
- no naive shared `CD94` allocator/cursor rewrite;
- no persistent/global flag like 0.6.3.6;
- no global force-height16 like 0.6.3.8.

## After extended-height path is stable

1. production-safe Vietnamese extended atlas/cache storage;
2. full Vietnamese glyph inventory;
3. compact runtime codepage/mapping;
4. encode `vi_full` có dấu;
5. solve/repack 230 pending rows;
6. clean mixed JP/VI;
7. patch graphic menu/title text;
8. full runtime QA + reproducible build.

## User testing preference

- Character Select visible probes;
- no deep gameplay unless necessary;
- maximize information per runtime test;
- never repeat tested builds;
- stop immediately on true global corruption/freeze;
- structural fixes over cosmetic iteration.

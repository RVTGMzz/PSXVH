# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** custom Vietnamese glyph pipeline is proven. Native 12x12 is rejected for production stacked diacritics. Extended-height reverse reached 0.6.3.9, which failed because the assumed per-glyph height source at `s3+2` near `0x8003CCC0` was wrong. There is currently **NO user probe to test**. Next phase is reverse-only around `0x8003CCA0..0x8003CD20` before building 0.6.3.10.

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

=> production needs an extended-height path.

## Extended-height facts proven so far

Character renderer:

```text
0x8003C210
```

Native custom-atlas pointer math near `0x8003C4F8..0x8003C500` computes `glyph_index * 72`.

Early glyph metadata struct produced in the `0x8003C210` path:

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

Metadata height=15 genuinely drives 16 source-row loop iterations at the copy stage.

Font cache page is much taller than 12 rows, so a simple fixed 12-row page/upload rectangle is not enough to explain the missing lower rows.

## Probe history — 0.6.3.x

### 0.6.3.0 EXTENDED HEIGHT
Historical structural evidence that taller source/copy behavior is possible. Do not retest. Later late-stage display assumptions must be revalidated.

### 0.6.3.1 BASELINE + 16-ROW STRIDE — UNSAFE FAIL
Naive shared cache/VRAM advance rewrite around `0x8003CD94..0x8003CDB4` caused global text corruption + freeze. Never repeat.

### 0.6.3.2 BASELINE ONLY — STABLE WITH LOWER-ROW LOSS
Control `ＴＥＳＴ亜Ａ`. Japanese/TEST stable, A sentinel intact, lower target rows still missing.

### 0.6.3.3 EOL OVERWRITE — OVERWRITE DISPROVEN
Target at end-of-line still loses same lower rows.

### 0.6.3.4 UV WINDOW — NEGATIVE
Target texture `V+4` does not recover the lower E cleanly.

### 0.6.3.5 POST-COPY SENTINEL — NO SENTINEL
Late `s0` target identity was unreliable; no conclusion about rows12..15.

### 0.6.3.6 EARLY-FLAG SENTINEL — UNSAFE FAIL
Persistent/global flag causes repeatable freeze just after Sony logo. Never retest and never reuse this flag strategy.

### 0.6.3.7 SOURCE ROW SENTINEL — HIGH-VALUE RESULT
Sentinel is baked directly into the target 12x16 source:

```text
rows10..11 = dark/gray full band
rows12..15 = bright white full band
```

Runtime:
- Japanese header and TEST normal;
- dark rows10..11 clearly visible;
- bright rows12..15 do not appear as a thick four-row block;
- only a thin bright edge remains.

=> lower source rows are genuinely not fully visible. This result does not depend on late target detection.

### 0.6.3.8 FORCE SPRITE HEIGHT16 — DIAGNOSTIC FAIL
Forcing height16 globally causes blank textbox / vertical TEST layout. Therefore the block at `0x8003CCC0` is not a simple safe global visible-height field.

### 0.6.3.9 HEIGHT FROM METADATA — DIAGNOSTIC FAIL
Probe used:

```text
lhu v0,2(s3)
```

at `0x8003CCC0`, assuming `s3` still pointed to the early current-glyph metadata struct.

Runtime screenshot:
- TEST stacks vertically;
- target becomes noisy/garbled texture block;
- layout remains broken;
- thick bright rows12..15 still not recovered.

=> assumption is false. `s3` at `0x8003CCC0` is not proven to be the original glyph metadata pointer.

## CURRENT PHASE — REVERSE ONLY

**Do not ask the user to test another build yet.**

Reverse exact range:

```text
0x8003CCA0 .. 0x8003CD20
```

Required questions before 0.6.3.10:

1. trace lifetime/meaning of `s1`, `s2`, `s3` entering this block;
2. identify what `lbu 64(s1)` at `0x8003CCC0` really means;
3. identify every consumer/store of the value after `0x8003CCC8 addiu v0,v0,1`;
4. determine whether this value is texture height, glyph advance, line metric, tile/cache dimension, or something else;
5. identify the actual descriptor/primitive field controlling vertical texture sampling for the current glyph by dataflow, not register-name inference;
6. re-check the earlier claim that descriptor byte `+7` is visible height and prove where/when that descriptor exists.

Only after those are resolved should a new runtime probe be built.

## Hard do-not-repeat

- no Krom path;
- no production 12x12 stacked-accent polishing;
- no retest 0.6.2.18;
- no retest 0.6.3.0..0.6.3.9;
- no naive shared `0x8003CD94..0x8003CDB4` rewrite;
- no persistent/global target flag;
- no global force-height16;
- no late `s0` target identity without proof;
- no `s3+2` height assumption at `0x8003CCC0` without register-lifetime proof.

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

- Character Select visible probes only when needed;
- no deep gameplay unless necessary;
- maximize information per runtime test;
- never repeat tested builds;
- stop immediately on true global corruption/freeze;
- reverse first, probe second.

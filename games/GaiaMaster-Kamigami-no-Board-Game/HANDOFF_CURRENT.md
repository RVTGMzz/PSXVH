# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** custom Vietnamese glyph pipeline is proven. Native 12x12 is rejected for production stacked diacritics. Extended-height reverse reached 0.6.3.9, whose `s3+2` height assumption was disproven by runtime and by full caller dataflow. New proven path: current glyph metadata lives at caller `sp+16`, so its `height_minus_1` is `lhu 18(sp)` at the sprite-geometry stage. Current probe is **0.6.3.10 HEIGHT FROM STACK METADATA**.

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

## Encoding / atlas facts

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

Character Select visible probe:

```text
PRGPACK.BDP + 0xBFD2C
owner nested BDP = entry 29
local offset = +0x580
```

## Native 12x12 conclusion

0.6.2.13 proved static custom-atlas Vietnamese rendering. 0.6.2.14..20 proved production stacked Vietnamese marks do not fit cleanly in native 12x12 without shrinking the base body.

=> production direction remains extended height.

## Extended-height proven facts

Renderer entry:

```text
0x8003C210
```

Early glyph metadata struct:

```text
+0 width metric
+2 source/copy height_minus_1
+4 source glyph pointer
+8 custom-atlas flag
```

Wide copy routine:

```text
0x8003C67C
6 source bytes/row -> 8 converted/cache bytes/row
```

Therefore:

```text
12 rows -> 96 converted bytes
16 rows -> 128 converted bytes
```

Metadata height=15 genuinely drives 16 source-row iterations.

## High-value probe history

### 0.6.3.1 — UNSAFE FAIL
Shared cache/VRAM stride mutation around `0x8003CD94..0x8003CDB4` caused global corruption + freeze. Never repeat.

### 0.6.3.2 — STABLE WITH LOWER-ROW LOSS
Baseline-only path stable; target bottom still missing.

### 0.6.3.3 — overwrite disproven
Target at end-of-line still loses same lower rows.

### 0.6.3.4 — UV+4 negative
Simple texture-V shift does not recover lower rows cleanly.

### 0.6.3.6 — UNSAFE FAIL
Persistent/global early flag causes repeatable freeze just after Sony logo. Never reuse.

### 0.6.3.7 — SOURCE ROW SENTINEL / HIGH-VALUE RESULT
Target source contains:

```text
rows10..11 = dark/gray full band
rows12..15 = bright white full band
```

Runtime:
- Japanese header/TEST normal;
- rows10..11 visible;
- rows12..15 not fully visible as thick 4-row block;
- only thin bright edge remains.

=> lower source rows are genuinely not fully visible.

### 0.6.3.8 — DIAGNOSTIC FAIL
Global visible-height=16 makes textbox blank / TEST appear vertically corrupted. Never repeat.

### 0.6.3.9 — DIAGNOSTIC FAIL
Used `lhu 2(s3)` at `0x8003CCC0` under the false assumption `s3` still pointed to glyph metadata. Runtime: TEST vertical + target texture garbage.

## Reverse breakthrough after 0.6.3.9

Full caller disassembly around `0x8003C8BC..0x8003CD20` proves:

```text
s5 = current 16-byte output/cache record base
s3 = s5 + 15
```

So at `0x8003CCC0`, `s3+2` is outside the current record and cannot be metadata height.

### Proven current-glyph metadata lifetime

Caller creates metadata buffer:

```text
0x8003CAC0  a2 = sp+16
0x8003C210  writes metadata into sp+16
```

Later in the same caller frame:

```text
0x8003CC3C  a1 = sp+16
0x8003C67C  copy routine
```

The copy routine reads:

```text
lhu 2(a1)
```

as source-row `height_minus_1`.

Therefore at `0x8003CCC0` the dataflow-proven current-glyph height is:

```text
lhu v0,18(sp)   # (sp+16)+2
```

Expected:

```text
native metadata 11 -> native +1 -> 12 px
target metadata 15 -> native +1 -> 16 px
```

## CURRENT PROBE — 0.6.3.10 HEIGHT FROM STACK METADATA

Start from stable 0.6.3.7 source-sentinel build.

At `0x8003CCC0`, replace native global height load with:

```text
lhu v0,18(sp)
```

Then resume native:

```text
0x8003CCC8 addiu v0,v0,1
```

No late target-code check is needed.

Unchanged:
- source sentinel;
- 16-row target metadata/copy;
- baseline Y -4;
- target at EOL;
- no global force-height;
- no persistent flag;
- no post-copy hook;
- no UV patch;
- no shared CD94 allocator rewrite.

Package:

```text
GaiaMaster_FontIsolation_0.6.3.10_HEIGHT_FROM_STACK_METADATA.zip
```

Launcher:

```text
00_RUN_PROBE_06310.cmd
```

Runtime question:

> Does TEST/native stay normal while the target finally shows the full bright rows12..15 block?

## Hard do-not-repeat

- no Krom path;
- no production 12x12 stacked-accent polishing;
- no retest 0.6.2.18;
- no retest 0.6.3.0..0.6.3.9;
- no naive shared `0x8003CD94..0x8003CDB4` rewrite;
- no persistent/global target flag;
- no global force-height16;
- no `s3+2` height assumption at `0x8003CCC0`.

## User testing preference

- Character Select visible probes only when needed;
- maximize information per runtime test;
- never repeat tested builds;
- stop immediately on real freeze/global corruption;
- reverse first, probe second.

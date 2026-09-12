# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** custom Vietnamese atlas path is proven. Native 12x12 is rejected for production stacked diacritics. Extended-height 12x16 remains the production direction. 0.6.3.7 proved lower source rows are not fully visible. 0.6.3.10 ruled out final primitive height as the main blocker. 0.6.3.11 RAM TAIL MIRROR showed no bright mirrored tail, but lacked an independent control proving the post-copy hook/destination model. Current probe is **0.6.3.12 CONTROLLED RAM TAIL MIRROR**.

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

## Proven atlas / encoding facts

```text
atlas RAM    = 0x8006BCEC
mapping RAM  = 0x8007AECC
atlas file   = SLPS + 0x5C4EC
mapping file = SLPS + 0x6B6CC
860 glyphs
native 12x12 / 72-byte / 4bpp / LOW nibble first
```

Confirmed:

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

0.6.2.13 proved static custom-atlas Vietnamese rendering.
0.6.2.14..20 proved stacked Vietnamese diacritics do not fit production-quality inside native 12x12 without shrinking the base letter.

=> Keep extended-height work. Do not resume 12x12 polish.

## Extended-height proven facts

Renderer entry:

```text
0x8003C210
```

Glyph metadata:

```text
+0 width metric
+2 source/copy height_minus_1
+4 source glyph pointer
+8 custom-atlas flag
```

Caller lifetime:

```text
0x8003CAC0  a2 = sp+16
0x8003C210  builds metadata there
0x8003CC3C  a1 = sp+16
0x8003C67C  consumes same metadata
```

Therefore:

```text
current height_minus_1 = lhu 18(sp)
current source pointer  = *(sp+20)
```

Wide copy routine:

```text
0x8003C67C
6 source bytes/row -> 8 converted bytes/row
```

Target metadata height=15 requests 16 source rows:

```text
12 rows -> 96 converted bytes
16 rows -> 128 converted bytes
```

Before copy:

```text
0x8003CC34  a2 = *(s1+100)
```

Native allocator later advances around:

```text
0x8003CD94..0x8003CDB4
```

Never rewrite that shared block naively; 0.6.3.1 caused global corruption/freeze.

VRAM upload is page-based, not a per-glyph hardcoded 12-row RECT.

Final 16-byte glyph record is consumed around `0x8003D9FC..0x8003DA50`:

```text
record+4 -> texture U
record+5 -> texture V
record+6 -> primitive width
record+7 -> primitive height
```

## High-value probe history

### 0.6.3.7 SOURCE ROW SENTINEL

Target source:

```text
rows10..11 = full 0x77 dark/gray
rows12..15 = full 0x11 bright white
```

Runtime:
- Japanese/TEST normal;
- dark rows10..11 visible;
- bright rows12..15 not visible as full 4-row block;
- only thin bright edge below.

### 0.6.3.10 HEIGHT FROM STACK METADATA

Uses proven `lhu 18(sp)` for final geometry. Runtime stable but visually same as 0.6.3.7.

=> primitive visible height is not the main blocker.

### 0.6.3.11 RAM TAIL MIRROR — RUNTIME COMPLETE / INCONCLUSIVE NEGATIVE

Mirrored:

```text
converted rows12..15 dest+96..127
-> rows8..11 dest+64..95
```

Runtime screenshot:
- TEST/header normal;
- no obvious bright 4-row mirror block;
- target essentially same as earlier stable probes.

But 0.6.3.11 had no visual control proving its post-copy hook and `state+100` destination assumption were both correct.

=> do not yet conclude rows12..15 are absent.
=> do not retest 0.6.3.11.

## CURRENT — 0.6.3.12 CONTROLLED RAM TAIL MIRROR

Purpose: resolve 0.6.3.11 ambiguity in one screenshot.

Target identity now uses only proven metadata:

```text
lhu 18(sp) == 15
```

At hook `0x8003CC4C` before native allocator advance:

```text
dest = *(s1+100)
```

### CONTROL

Write:

```text
converted rows6..7 = full 0x77 dark/gray
```

These rows are safely inside the visible region.

### MIRROR

Copy:

```text
converted rows12..15 -> rows8..11
```

Since source rows12..15 are full `0x11`, a valid converted tail should mirror as a bright 4-row block immediately below the dark control.

### Interpret exactly

A. **Dark control + bright mirror**

> Hook fires, destination is correct, rows12..15 exist after conversion. Continue downstream into cache/VRAM placement.

B. **Dark control but no bright mirror**

> Hook fires and destination is correct, but converted rows12..15 do not contain expected tail immediately after `0x8003C67C`. Reverse the copy routine/loop state/source-to-dest writes.

C. **No dark control**

> Hook or `state+100` destination model is still wrong. Do not infer tail loss.

Package:

```text
GaiaMaster_FontIsolation_0.6.3.12_CONTROLLED_RAM_TAIL_MIRROR.zip
```

Launcher:

```text
00_RUN_PROBE_06312.cmd
```

## Hard do-not-repeat

- no Krom path;
- no production 12x12 stacked-accent polishing;
- no retest 0.6.2.18;
- no retest 0.6.3.0..0.6.3.11;
- no shared `0x8003CD94..0x8003CDB4` rewrite;
- no persistent/global target flag;
- no global force-height16;
- no `s3+2` metadata assumption.

## User testing preference

- Character Select visible probes only when needed;
- maximize information per test;
- never repeat tested builds;
- stop on real freeze/global corruption;
- reverse first, probe second.

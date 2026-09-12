# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** 0.6.2.x proved the custom Vietnamese glyph pipeline works, but native 12x12 is rejected for production stacked diacritics. First 12x16 experiment **0.6.3.0 EXTENDED HEIGHT failed at runtime**. Next chat must reverse the full copy/unpack/sprite path before building another height probe.

## Source game

- `GaiaMaster - Kamigami no Board Game (Japan).bin`
- MODE2/2352
- serial `SLPS-02075`
- clean BIN SHA1 `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- executable `SLPS_020.75`
- main archive `PRGPACK.BDP`
- stable translation baseline: Alpha 0.6.1 FRONT SHA1 `54d2fb026bc3b71c79861e723caffb4114caa34c`
- working branch: `gaia-character-select-font-atlas-reverse-01`

## BDP / raw-sector facts

BDP:

```text
magic    +0x00 = 0x000010F0
checksum +0x04
TOC size +0x08
count    +0x0C
descriptor = (offset,size), 8 bytes
```

Checksum:

```text
sum16 = sum(all bytes except +0x04..+0x07) & 0xFFFF
checksum = ((~sum16 & 0xFFFF) << 16) | sum16
```

Verified 60/60 nested BDP + top-level PRGPACK.
Raw disc MODE2/Form1; changed sectors require regenerated EDC/ECC.

## Translation status

- Alpha 0.5.1: 203 patch, runtime user-confirmed.
- Master 0.6: 596 rows, `vi_full` is source-of-truth with accents.
- Alpha 0.6: 366 patch.
- Alpha 0.6.1 FRONT: 397 patch, runtime stable.
- 230 rows still pending because full-width 2-byte text overflows original slots.
- mixed JP/VI fragments + graphic-text menus remain for later.

## Encoding rules

- Shift-JIS Japanese: OK.
- Full-width Latin CP932: OK runtime.
- ASCII 1-byte: FAIL/mis-render in Japanese renderer; do not use as control/runtime text.
- UTF-8 direct: not used.

## Character Select visible probe

```text
PRGPACK.BDP + 0xBFD2C
owner nested BDP = entry 29
local offset = +0x580
```

Useful control:

```text
ＴＥＳＴ亜
82 73 82 64 82 72 82 73 88 9F
```

## Krom path — rejected for Character Select

C2/D2/E2 did not affect visible `亜` at Character Select. Do not return to Krom2RawAdd direct/global-wrapper experiments.

## Custom Character Select atlas — proven

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
12x12 pixels
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

Native full-width `Ｅ` = glyph 466 and is the style/palette reference.

## Critical probe history

### 0.6.2.13 STATIC SLOT / NO HOOK — BREAKTHROUGH PASS

- no renderer hook;
- no code cave;
- full-width control text;
- direct static atlas glyph replacement.

Runtime:

- all surrounding text normal;
- target glyph visibly changes into a Vietnamese accented-E-like glyph.

=> **Custom Vietnamese glyph pipeline is proven.**

### 0.6.2.14 / 0.6.2.15 — compact body rejected

Compressing base `E` to gain accent headroom makes accented capitals visibly smaller. Not acceptable for production.

### 0.6.2.16 / 0.6.2.17 / 0.6.2.18 — full-height 12x12

Kept native base-letter body size and used only two spare rows above it. Runtime became increasingly recognizable but accents remain cramped/awkward.

Important: **0.6.2.18 has already been tested. Never ask user to retest it.**

### 0.6.2.19 VARIANT GRID

Six `Ế` variants shown in one Character Select line. User selected **sample 2 from the left** as best base shape, but noted:

- too thin;
- lacks shadow/weight;
- circumflex not centered enough;
- circumflex too visually attached to top bar of E.

### 0.6.2.20 SAMPLE2 REFINED

Refined sample 2, then user inspected preview/runtime and correctly identified the structural blocker:

> A 12x12 cell cannot comfortably support stacked Vietnamese diacritics while keeping the native capital body at full size.

This is worse for `Ể`, `Ẳ`, `Ỗ`, `Ử`, `Ấ`, `Ố`, etc.

=> **Stop production work inside 12x12.**

## Native renderer reverse relevant to extended height

Character renderer around `0x8003C210` separates several stages:

1. character code -> mapping -> glyph index;
2. glyph index -> atlas source pointer;
3. glyph metrics / source height;
4. bitmap copy/unpack;
5. visible GPU primitive/sprite metrics.

Native atlas stride is explicitly hardcoded near:

```text
0x8003C4F8  sll  v0,v1,3
0x8003C4FC  addu v0,v0,v1
0x8003C500  sll  a1,v0,3
```

which computes:

```text
glyph_index * 72
```

A separate height field exists later in the render/copy path, which motivated the 12x16 experiment. However, **12x16 support is not yet proven**.

## 0.6.3.0 EXTENDED HEIGHT 12x16 — RUNTIME FAIL

Goal:

- keep normal Japanese/Latin on native 12x12;
- make only target `0x889F` use a 12x16 / 96-byte `Ế`;
- prove all 16 rows can be copied and displayed.

Diagnostic design attempted:

- remap `0x889F` to high atlas slot 850;
- write 96-byte / 16-row glyph beginning at that target source location;
- target-only hook to request 16 copied rows;
- target-only hook to request a 16-pixel visible sprite;
- no baseline correction in first probe.

Runtime user screenshot result:

- `ＴＥＳＴ` still renders normally;
- final target glyph remains malformed/insufficient;
- clearly expanded 16-row Vietnamese glyph was **not** observed;
- game boots, so this is not a global renderer crash.

=> **0.6.3.0 = FAIL.**

Do **not** ask user to test 0.6.3.0 again.

Dedicated failure note:

```text
FONT_ISOLATION_0.6.3.0_FAIL.md
```

## Cause is NOT yet proven

Do not claim that 12x16 is impossible. The failed probe does not isolate which stage is still native-sized.

Main possibilities for next reverse:

1. 16-row metadata hook did not affect the actual Character Select copy path;
2. intermediate converted-glyph buffer remains native-sized;
3. row pitch / unpack loop still assumes 12-row/72-byte geometry;
4. visible GPU primitive remains clipped elsewhere despite one height patch;
5. 96-byte source embedded in a 72-byte-stride static atlas is unsafe for cache/fetch behavior;
6. another source-height/destination-height/UV/texture-window field exists;
7. target glyph source pointer is correct but downstream copy consumes a different footprint than assumed.

## NEXT TASK — START HERE IN NEW CHAT

**Do not build another blind 12x16 probe immediately.**

First reverse the entire target path from final glyph pointer to GPU primitive:

1. reconstruct exact 0.6.3.0 patch/hook locations;
2. disassemble after final glyph pointer generation through bitmap copy/unpack;
3. identify exact source row count and row pitch;
4. identify converted glyph destination-buffer footprint/allocation;
5. identify all per-glyph width/height metrics;
6. identify visible sprite/primitive height and any UV/texture-window/clipping fields;
7. determine whether an external production-safe extended atlas should be used instead of overlapping a 96-byte glyph inside the native 72-byte-stride atlas;
8. only then build the next high-information Character Select probe.

The next probe should answer one precise question, not mix multiple uncertain assumptions.

## Long-term path after extended-height problem is solved

1. full Vietnamese glyph inventory;
2. compact runtime codepage/mapping without breaking untranslated Japanese;
3. encode `vi_full` with accents;
4. solve/repack 230 pending rows;
5. clean mixed JP/VI;
6. patch graphic main-menu/Character-Select text;
7. full runtime QA;
8. reproducible final patch/build package.

## Windows builder pitfalls

- avoid parsing `(Japan).bin` inside parenthesized BAT blocks;
- use ASCII + CRLF launcher;
- current test PC Python: `C:\Python312\python.exe`;
- Japanese JSON: explicit UTF-8 or `ensure_ascii=True`.

## User testing preference

- visible probes at intro/main menu/Character Select;
- no deep gameplay unless necessary;
- maximize information per test;
- never repeat already-tested builds;
- avoid long sequences of one-pixel cosmetic ROM probes when a structural renderer fix is the real issue.

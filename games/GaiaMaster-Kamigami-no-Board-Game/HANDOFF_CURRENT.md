# HANDOFF — Gaia Master PS1 Việt hóa

> Current source-of-truth: **0.6.2.x Vietnamese 12x12 pipeline PASS, but 12x12 is rejected as production geometry for stacked Vietnamese diacritics. Next probe: 0.6.3.0 EXTENDED HEIGHT 12x16.**

## Source game

- `GaiaMaster - Kamigami no Board Game (Japan).bin`
- MODE2/2352
- serial `SLPS-02075`
- clean BIN SHA1 `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- executable `SLPS_020.75`
- main archive `PRGPACK.BDP`
- stable translation baseline: Alpha 0.6.1 FRONT SHA1 `54d2fb026bc3b71c79861e723caffb4114caa34c`

## BDP / raw sector

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
Raw disc MODE2/Form1; modified sectors regenerate EDC/ECC.

## Translation status

- Alpha 0.5.1: 203 patch, runtime confirmed.
- Master 0.6: 596 rows, `vi_full` source-of-truth có dấu.
- Alpha 0.6: 366 patch; 230 rows pending do full-width 2-byte overflow slot.
- Alpha 0.6.1 FRONT: 397 patch, runtime stable.
- mixed JP/VI + graphic text xử lý sau font.

## Encoding rules

- Shift-JIS Japanese: OK.
- Full-width Latin CP932: OK.
- ASCII 1-byte: FAIL/mis-render; do not use for runtime control text.
- UTF-8 direct: not used.

## Character Select visible probe

```text
PRGPACK.BDP + 0xBFD2C
owner nested BDP = entry 29
local offset = +0x580
```

## Custom atlas path

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

Mapping confirmed:

```text
0x8273 Ｔ -> glyph 481
0x8264 Ｅ -> glyph 466
0x8272 Ｓ -> glyph 480
0x889F 亜 -> glyph 0
```

Native full-width `Ｅ` = glyph 466 style reference.

## Probe history — important conclusions

### Krom path rejected
C2/D2/E2 did not affect Character Select. Do not return to Krom wrapper hooks.

### 0.6.2.13 STATIC SLOT / NO HOOK — BREAKTHROUGH PASS
- full-width control text
- direct static atlas replacement
- other text normal
- Vietnamese accented glyph visibly renders

=> **Vietnamese glyph pipeline PASS.**

### 0.6.2.14 / 0.6.2.15 — compact body rejected
Shrinking the native body to gain accent rows makes accented capitals too small. Production must preserve native base-letter size.

### 0.6.2.16 / 0.6.2.17 / 0.6.2.18 — full-height inside 12x12
Kept native E body full size and used only two spare top rows. `Ế` became increasingly recognizable, but stacked marks remain cramped/dirty because only two rows are available.

### 0.6.2.19 VARIANT GRID — runtime result
One ROM showed six full-height `Ế` variants in one line. User selected **sample 2 from the left** as the best base shape, but feedback:

- too thin;
- no shadow/weight;
- circumflex not centered enough;
- circumflex feels attached to the E top bar.

### 0.6.2.20 SAMPLE2 REFINED — production blocker identified
Refined sample 2 with more weight/centering. User then inspected the glyph preview and identified the structural issue correctly:

> A 12x12 cell simply does not provide enough vertical room for stacked Vietnamese marks while keeping the native capital body untouched.

This will be worse for `Ể`, `Ẳ`, `Ỗ`, `Ử`, `Ấ`, `Ố`, etc.

=> **Stop trying to perfect production Vietnamese stacked marks inside 12x12.**

## New reverse finding — renderer can likely support target-only extended height

Character renderer around `0x8003C210` separates:

1. character code -> mapping -> glyph index;
2. glyph index -> atlas pointer;
3. per-glyph metadata including source height;
4. downstream bitmap copy;
5. visible GPU sprite height.

### Native stride is explicitly hardcoded

At:

```text
0x8003C4F8  sll  v0,v1,3
0x8003C4FC  addu v0,v0,v1
0x8003C500  sll  a1,v0,3
```

result is:

```text
glyph_index * 72
```

### Per-glyph height is separate

Renderer tail writes a glyph-struct height field at `s3+2`.
Downstream function `0x8003C67C` loops using that field, so native 12 rows are not the only possible loop count.

Caller later assigns visible sprite height separately near:

```text
0x8003CCC0  lbu v0,64(s1)
0x8003CCC8  addiu v0,v0,1
```

Therefore a target-specific 16-row diagnostic is feasible without converting every native glyph.

## NEXT — 0.6.3.0 EXTENDED HEIGHT 12x16

Diagnostic design:

- keep Character Select full-width `ＴＥＳＴ亜` control;
- remap `0x889F` to high diagnostic atlas slot `850`;
- write a **12x16 / 96-byte** Vietnamese `Ế` beginning at `slot850*72`;
- use target-only safe-cave hook at renderer tail so only `0x889F` gets glyph metadata height `15` => 16 copied rows;
- use second target-only safe-cave hook so only `0x889F` gets visible sprite height `16`;
- untouched Japanese/Latin remains native 12x12.

Diagnostic glyph layout:

```text
rows 0..5  = dedicated diacritic/headroom
rows 6..15 = native E body at original pixel size
```

### Important scope of 0.6.3.0

Do **not** judge baseline yet.

The expanded E body is expected to sit about 4 px lower because the first probe does not yet shift the sprite upward.

Primary test question only:

> Does the final glyph visibly use all 16 rows, with substantially more room for circumflex + tone mark?

If YES, next is **0.6.3.1**:

- shift target sprite up ~4 px so native E baseline matches surrounding text;
- fix expanded output-buffer accounting (16 rows = 128-byte converted buffer footprint instead of native 96-byte footprint where applicable);
- move from diagnostic overlapped slot to production-safe extended Vietnamese atlas storage;
- then build the full Vietnamese glyph/codepage family.

## Windows builder pitfalls

- avoid parsing `(Japan).bin` inside parenthesized BAT blocks;
- launchers ASCII + CRLF;
- current test PC Python: `C:\Python312\python.exe`;
- Japanese JSON: explicit UTF-8 or `ensure_ascii=True`.

## User testing preference

- Character Select visible probes;
- no deep gameplay unless necessary;
- maximize information per test;
- never repeat already-tested builds;
- stop pixel-art iteration when a renderer-level fix solves the whole glyph family better.

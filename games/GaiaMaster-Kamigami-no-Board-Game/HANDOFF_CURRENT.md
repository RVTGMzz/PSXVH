# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** custom Vietnamese glyph pipeline is proven. Native 12x12 is rejected for production stacked diacritics. 0.6.3.0 proves target 12x16 structurally. 0.6.3.1 shared cache-stride rewrite is unsafe and caused global corruption/freeze. 0.6.3.2 BASELINE ONLY is stable but lower target rows are missing. 0.6.3.3 EOL test gives the same lower-row loss, disproving following-glyph overwrite. Current diagnostic is **0.6.3.4 UV WINDOW TEST**.

## Source / baseline

- Game: `GaiaMaster - Kamigami no Board Game (Japan).bin`
- MODE2/2352, serial `SLPS-02075`
- clean BIN SHA1: `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- stable Alpha 0.6.1 FRONT SHA1: `54d2fb026bc3b71c79861e723caffb4114caa34c`
- executable: `SLPS_020.75`
- main archive: `PRGPACK.BDP`
- branch: `gaia-character-select-font-atlas-reverse-01`

## Translation status

- Master: 596 rows, `vi_full` = accented source-of-truth.
- Alpha 0.6.1 FRONT: 397 runtime-stable patches.
- 230 rows pending because full-width 2-byte text overflows fixed slots.
- mixed JP/VI fragments + graphic text remain after font work.

## Encoding facts

- Shift-JIS Japanese: OK.
- Full-width Latin CP932: OK runtime.
- ASCII 1-byte: FAIL/mis-render in this renderer. Do not use for control text.
- UTF-8 direct: not used.

## Character Select visible probe

```text
PRGPACK.BDP + 0xBFD2C
owner nested BDP = entry 29
local offset = +0x580
```

## Custom atlas path — proven

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

Native full-width `Ｅ` = glyph 466 style reference.

## Hard do-not-repeat rules

- Krom2RawAdd path does not control Character Select target. Do not return to Krom hooks.
- Do not resume endless stacked-diacritic polishing inside native 12x12.
- 0.6.2.18 already tested; never retest.
- 0.6.3.0 already tested; never retest.
- 0.6.3.1 is unsafe; never retest.
- 0.6.3.2 already tested; do not repeat without a new structural reason.
- 0.6.3.3 already tested; do not repeat.
- Never repeat the 0.6.3.1 shared cache-advance rewrite around `0x8003CD94..0x8003CDB4`.

## 0.6.2.x conclusion

### 0.6.2.13 STATIC SLOT / NO HOOK — BREAKTHROUGH PASS
Direct static-atlas replacement visibly renders custom Vietnamese glyph data while surrounding text remains normal.

### 0.6.2.14..0.6.2.20
12x12 cannot comfortably hold stacked Vietnamese marks while preserving native base-letter size.

=> reject native 12x12 for production `Ế, Ể, Ẳ, Ỗ, Ử, Ấ, Ố...`.

## Extended-height renderer facts

Character renderer:

```text
0x8003C210
```

Custom atlas pointer math near:

```text
0x8003C4F8
0x8003C4FC
0x8003C500
```

computes:

```text
glyph_index * 72
```

Glyph metadata struct:

```text
+0  width metric
+2  source/copy height metric (height-1)
+4  source glyph pointer
+8  custom-atlas flag
```

### Wide-glyph unpack/copy

Function:

```text
0x8003C67C
```

For each row on the wide custom path:

```text
6 source bytes -> 8 converted/cache bytes
```

So:

```text
12 source rows -> 96 converted bytes
16 source rows -> 128 converted bytes
```

Target metadata height=15 genuinely makes the loop process 16 rows.

### Sprite descriptor

Relevant descriptor bytes:

```text
+4/+5 = texture U/V
+6    = visible width
+7    = visible height
```

Target visible height=16 is architecturally possible and already exercised.

## 0.6.3.0 EXTENDED HEIGHT 12x16 — STRUCTURAL PASS

- target source = 12x16 / 96 bytes;
- target source/copy height = 16 rows;
- target visible sprite height = 16;
- native glyphs remain 12x12.

Runtime shows extra headroom and taller target footprint; body appears lower because baseline correction was intentionally absent.

## 0.6.3.1 BASELINE + 16-ROW STRIDE — UNSAFE FAIL

Added:

1. target Y `-4 px`;
2. target-specific rewrite of shared cache RAM pointer/VRAM Y advance near `0x8003CD94`.

Runtime:

- unrelated Japanese corrupt/repeat;
- Character Select corrupt;
- later screen garbled;
- game freezes.

=> unsafe. Strongest cause is mutation of shared cache allocator/cursor state.

## 0.6.3.2 BASELINE ONLY — STABLE PASS WITH LOWER-ROW LOSS

Control:

```text
ＴＥＳＴ亜Ａ
```

Keeps 16-row copy/display path, adds only target `Y -= 4`, leaves shared cache stride native.

Runtime:

- Japanese header normal;
- `ＴＥＳＴ` normal;
- target baseline improved;
- trailing `Ａ` intact;
- no global corruption/freeze;
- lower part of extended target missing/cut.

=> baseline hook itself is safe.

## 0.6.3.3 EOL OVERWRITE TEST — SAME RESULT, OVERWRITE DISPROVEN

Control:

```text
ＴＥＳＴ亜
```

Target ends the line, so there is no following glyph that can overwrite its converted footprint.

Runtime screenshot is essentially the same as 0.6.3.2:

- surrounding text normal;
- target stable;
- no freeze;
- lower target rows still missing.

=> The hypothesis “following native glyph overwrites last 4 rows” is **false**.
=> The loss happens inside target copy/upload/window/display behavior itself.

## New reverse finding — VRAM upload queue identified

At:

```text
0x8003CDE8 .. 0x8003CE24
```

the renderer builds a PS1 RECT on stack and queues an upload through:

```text
jal 0x800406F8
```

RECT fields:

```text
x = lhu state+48
y = lhu state+40
w = 4
h = (lhu state+42) - (lhu state+40) + 1
```

Source pointer:

```text
state+96
```

`0x800406F8` records exactly `(x,y,w,h,source)` into an upload queue.

This is important because the font pipeline now has three distinct geometries:

1. source glyph: 12x16 = 96 bytes;
2. converted RAM/cache: 16 rows × 8 bytes = 128 bytes;
3. VRAM texture upload + sprite UV/window.

## CURRENT PROBE — 0.6.3.4 UV WINDOW TEST

Start from stable 0.6.3.3.

Target still ends line:

```text
ＴＥＳＴ亜
```

New diagnostic changes **only**:

```text
target texture V += 4
```

Hook site:

```text
0x8003CCF0
```

Native:

```text
0x8003CCF4 subu v0,v0,v1
```

remains in jump delay slot, so cave receives the exact native V coordinate. Cave adds 4 only when `s0 & 0xFFFF == 0x889F`, stores descriptor V, then resumes at `0x8003CCFC`.

No change to:

- metadata 16-row hook;
- target visible height 16;
- baseline Y -4;
- shared cache allocator;
- `CD94` block;
- source glyph bytes.

### Interpretation

If target lower rows **appear after V+4** while top accents shift/disappear:

> all 16 rows exist in VRAM; unresolved bug is UV/window/draw sampling.

If lower rows **remain missing / blank / garbage**:

> truncation occurs before texture sampling, most likely converted cache contents or VRAM upload content/rectangle.

Package:

```text
GaiaMaster_FontIsolation_0.6.3.4_UV_WINDOW_TEST.zip
```

## Long-term after extended-height path is stable

1. production-safe extended Vietnamese atlas/cache storage;
2. full Vietnamese glyph inventory;
3. compact runtime codepage/mapping without breaking untranslated Japanese;
4. encode `vi_full` with accents;
5. solve/repack 230 pending rows;
6. clean mixed JP/VI;
7. patch graphic menus/title text;
8. full runtime QA + reproducible final build.

## Windows builder pitfalls

- avoid parsing `(Japan).bin` inside parenthesized BAT blocks;
- launcher ASCII + CRLF;
- test PC Python: `C:\Python312\python.exe`;
- Japanese JSON: explicit UTF-8 or `ensure_ascii=True`.

## User testing preference

- Character Select visible probes;
- no deep gameplay unless necessary;
- maximize information per test;
- never repeat already-tested builds;
- stop immediately on global corruption/freeze;
- structural fixes preferred over cosmetic pixel iteration.

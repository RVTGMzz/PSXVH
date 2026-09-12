# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** custom Vietnamese glyph pipeline is proven. Native 12x12 is rejected for production stacked diacritics. 0.6.3.0 proves target 12x16 structurally. 0.6.3.1 shared cache-stride rewrite is unsafe and caused global corruption/freeze. 0.6.3.2 is stable with lower-row loss. 0.6.3.3 disproved following-glyph overwrite. 0.6.3.4 UV+4 did not recover the lower E correctly. Current probe: **0.6.3.5 POST-COPY RAM SENTINEL**.

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
- ASCII 1-byte: FAIL/mis-render. Do not use runtime control text.
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

- Do not return to Krom2RawAdd path for Character Select.
- Do not resume production stacked-diacritic polishing inside native 12x12.
- 0.6.2.18 already tested; never retest.
- 0.6.3.0 already tested; never retest.
- 0.6.3.1 unsafe; never retest.
- 0.6.3.2 already tested; do not repeat.
- 0.6.3.3 already tested; do not repeat.
- 0.6.3.4 already tested; do not repeat.
- Never repeat naive shared cache/VRAM cursor rewrite at `0x8003CD94..0x8003CDB4`.

## 0.6.2.x conclusion

### 0.6.2.13 STATIC SLOT / NO HOOK — breakthrough pass

Direct static-atlas replacement renders custom Vietnamese glyph data while surrounding text remains normal.

### 0.6.2.14..0.6.2.20 — production 12x12 rejected

12x12 cannot comfortably hold stacked Vietnamese marks while preserving native base-letter size.

Reject for production `Ế, Ể, Ẳ, Ỗ, Ử, Ấ, Ố...`.

## Extended-height renderer facts

Character renderer:

```text
0x8003C210
```

Custom mapping/atlas pointer math near:

```text
0x8003C4F8
0x8003C4FC
0x8003C500
```

computes native `glyph_index * 72`.

Glyph metadata struct:

```text
+0  width metric
+2  source/copy height metric (height-1)
+4  source glyph pointer
+8  custom-atlas flag
```

### Wide custom copy routine

```text
0x8003C67C
```

Per source row:

```text
6 source bytes -> 8 converted/cache bytes
```

So:

```text
12 rows -> 96 converted bytes
16 rows -> 128 converted bytes
```

Metadata height=15 genuinely makes the loop iterate 16 rows.

### Sprite descriptor

```text
+4/+5 = texture U/V
+6    = visible width
+7    = visible height
```

Target visible-height hook requests 16.

## 0.6.3.0 EXTENDED HEIGHT — structural pass

12x16 source + 16-row copy + taller target footprint is real. Baseline was intentionally not corrected in that build.

## 0.6.3.1 BASELINE + 16-ROW STRIDE — unsafe fail

Added baseline Y -4 plus target rewrite of shared cache RAM/VRAM advance around `CD94`.

Runtime:

- unrelated Japanese corrupt/repeat;
- Character Select corrupt;
- later screen garbled;
- freeze.

=> shared allocator/cursor rewrite is unsafe.

## 0.6.3.2 BASELINE ONLY — stable pass with lower-row loss

Control:

```text
ＴＥＳＴ亜Ａ
```

Runtime stable, `Ａ` intact, baseline improved, but lower extended target rows missing/cut.

## 0.6.3.3 EOL OVERWRITE — overwrite disproven

Control:

```text
ＴＥＳＴ亜
```

Target at EOL still loses the same lower rows.

=> following glyph does not cause the loss.

## 0.6.3.4 UV WINDOW TEST — negative diagnostic

Kept stable EOL path and changed only:

```text
target texture V += 4
```

Runtime user screenshot:

- Japanese header normal;
- TEST normal;
- target remains malformed/truncated;
- lower native E does not return cleanly/correctly;
- no global corruption/freeze.

=> a simple bad texture-V/window explanation is insufficient.

Do not retest 0.6.3.4.

## New reverse after 0.6.3.4

### Font cache page/upload is not native-12-row-sized

Initialization around:

```text
0x8003D488..0x8003D5F4
```

uses default cache page parameters roughly:

```text
width  = 32
height = 240
VRAM Y = 256
```

State:

```text
state+40 = page start Y
state+42 = page start Y + pageHeight - 1
```

Final flush around:

```text
0x8003DB78..0x8003DBE0
```

queues a RECT for the full cache page using source `state+96`.

Therefore missing target rows are **not explained by VRAM upload RECT.h being hardcoded to 12**.

## CURRENT PROBE — 0.6.3.5 POST-COPY RAM SENTINEL

Purpose: directly test converted RAM rows 10..15 immediately after `0x8003C67C` returns.

Clean hook site:

```text
0x8003CC4C
```

Target `0x889F` only, current converted destination = `state+100`.

Overwrite:

```text
rows 10..11 = full palette-index-7 band  # dark/gray CONTROL
rows 12..15 = full palette-index-1 band  # bright TEST
```

Interpretation:

### A — both bands visible
Rows 12..15 survive RAM -> VRAM -> sprite. Old missing bottom was due source/copy glyph contents/construction.

### B — control rows10..11 visible, bright rows12..15 absent
Hook executed, but rows12..15 are lost after converted RAM. Focus on post-copy cache/upload/draw geometry.

### C — neither band visible
Do not infer clipping. Sentinel hook/target condition failed or did not reach visible target.

Package:

```text
GaiaMaster_FontIsolation_0.6.3.5_POST_COPY_RAM_SENTINEL.zip
```

Launcher:

```text
00_RUN_PROBE_0635.cmd
```

## After extended-height path is truly stable

1. production-safe Vietnamese extended atlas/cache storage;
2. full Vietnamese glyph inventory;
3. compact runtime codepage/mapping without breaking untranslated Japanese;
4. encode `vi_full` with accents;
5. solve/repack 230 pending rows;
6. clean mixed JP/VI;
7. patch graphic menus/title text;
8. full runtime QA + reproducible build.

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
- structural fixes preferred over cosmetic one-pixel iteration.

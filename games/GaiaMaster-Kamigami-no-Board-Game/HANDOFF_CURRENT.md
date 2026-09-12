# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** custom Vietnamese glyph pipeline is proven. Native 12x12 is rejected for production stacked diacritics. 0.6.3.0 proves target 12x16 structurally. 0.6.3.1 shared cache-stride rewrite is unsafe and caused global corruption/freeze. 0.6.3.2 is stable with lower-row loss. 0.6.3.3 disproved following-glyph overwrite. 0.6.3.4 UV+4 did not recover the lower E. 0.6.3.5 post-copy sentinel showed no sentinel because target identification at the late hook was unreliable. Current probe: **0.6.3.6 EARLY-FLAG POST-COPY SENTINEL**.

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
- 0.6.3.2 / 0.6.3.3 / 0.6.3.4 / 0.6.3.5 already tested; do not repeat.
- Never repeat naive shared cache/VRAM cursor rewrite at `0x8003CD94..0x8003CDB4`.

## Native 12x12 conclusion

`0.6.2.13 STATIC SLOT / NO HOOK` proved direct static-atlas Vietnamese glyph rendering works. Later 12x12 geometry experiments showed stacked marks such as `Ế, Ể, Ẳ, Ỗ, Ử, Ấ, Ố` do not have enough headroom without shrinking the native base-letter body.

=> production must use an extended-height path.

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

Therefore:

```text
12 rows -> 96 converted bytes
16 rows -> 128 converted bytes
```

Metadata height=15 genuinely drives 16 loop iterations.

### Sprite descriptor

```text
+4/+5 = texture U/V
+6    = visible width
+7    = visible height
```

Target visible-height hook requests 16.

### Cache/upload page

Font cache initialization uses a page much taller than 12 rows, roughly 240 rows. Final flush uploads the cache page, so missing target rows are not explained by a glyph-only VRAM upload RECT hardcoded to 12.

## Probe history — 0.6.3.x

### 0.6.3.0 EXTENDED HEIGHT — structural pass

12x16 source + 16-row copy + taller target footprint is real. Baseline was intentionally not corrected.

### 0.6.3.1 BASELINE + 16-ROW STRIDE — unsafe fail

Target-specific mutation of shared cache RAM/VRAM advance around `CD94` caused unrelated Japanese corruption, Character Select corruption, later garbling and freeze.

=> never repeat shared allocator/cursor rewrite.

### 0.6.3.2 BASELINE ONLY — stable pass with lower-row loss

Control:

```text
ＴＥＳＴ亜Ａ
```

Runtime stable, baseline improved, trailing A intact, but lower extended target rows missing/cut.

### 0.6.3.3 EOL OVERWRITE — overwrite disproven

Target at end-of-line still loses same lower rows.

=> following glyph is not overwriting the bottom.

### 0.6.3.4 UV WINDOW TEST — negative

Target texture `V += 4` did not restore lower E rows correctly.

=> simple UV/window offset is insufficient.

### 0.6.3.5 POST-COPY RAM SENTINEL — sentinel not observed

Intended post-copy diagnostic at `0x8003CC4C`:

```text
rows 10..11 = dark/gray band
rows 12..15 = bright white band
```

Runtime:

- Japanese header normal;
- TEST normal;
- target resembles previous truncated glyph;
- neither obvious gray nor white full-width band is visible;
- no global corruption/freeze.

=> do **not** infer clipping.

Strongest issue: 0.6.3.5 checked target using late-stage `s0 & 0xFFFF == 0x889F`. At `0x8003CC4C`, `s0` is not proven to still be the original Shift-JIS code.

## CURRENT PROBE — 0.6.3.6 EARLY-FLAG POST-COPY SENTINEL

Purpose: rerun the exact same RAM sentinel question with reliable target identity.

### Early target flag

At the metadata hook, where `s0` is already proven trustworthy:

```text
0x889F -> FLAG = 1
other  -> FLAG = 0
```

A dedicated runtime flag word is stored in the proven executable safe-cave region.

The late post-copy hook at `0x8003CC4C` reads only FLAG. It never checks `s0`.

### Sentinel remains unchanged

For FLAG=1 only:

```text
rows 10..11 = full palette-index-7 band  # dark/gray CONTROL
rows 12..15 = full palette-index-1 band  # bright white TEST
```

### Interpretation

A. Gray + white bands visible:

> rows12..15 survive converted RAM -> VRAM -> sprite. Previous lower-row loss is caused by source/copy glyph contents/construction, not downstream clipping.

B. Gray control visible, white bottom absent:

> rows12..15 are lost after converted RAM; reverse post-copy cache/upload/draw geometry.

C. Neither visible:

> the assumed current converted destination/path is still wrong. Do not infer clipping.

### Safety

Unchanged from stable path:

- 12x16 target source;
- 16-row metadata/copy path;
- visible height 16;
- baseline Y -4;
- target at end-of-line;
- no UV +4;
- no `CD94` shared allocator patch.

Package:

```text
GaiaMaster_FontIsolation_0.6.3.6_EARLY_FLAG_POST_COPY_SENTINEL.zip
```

Launcher:

```text
00_RUN_PROBE_0636.cmd
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

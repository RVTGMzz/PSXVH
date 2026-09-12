# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** custom Vietnamese glyph pipeline is proven. Native 12x12 is rejected for production stacked diacritics. 0.6.3.0 proves 12x16 structurally. 0.6.3.1 shared cache-stride rewrite is unsafe and caused global corruption/freeze. 0.6.3.2 BASELINE ONLY is stable, but the extended target loses its lower rows when a native glyph follows. Current diagnostic: **0.6.3.3 EOL OVERWRITE TEST**.

## Source game

- `GaiaMaster - Kamigami no Board Game (Japan).bin`
- MODE2/2352
- serial `SLPS-02075`
- clean BIN SHA1 `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- executable `SLPS_020.75`
- main archive `PRGPACK.BDP`
- stable translation baseline: Alpha 0.6.1 FRONT SHA1 `54d2fb026bc3b71c79861e723caffb4114caa34c`
- working branch: `gaia-character-select-font-atlas-reverse-01`

## Translation status

- Master: 596 rows, `vi_full` = accented source-of-truth.
- Alpha 0.6.1 FRONT: 397 runtime-stable patches.
- 230 rows pending due fixed-slot/full-width overflow.
- mixed JP/VI + graphic text remain after font work.

## Encoding rules

- Shift-JIS Japanese: OK.
- Full-width Latin CP932: OK runtime.
- ASCII 1-byte: FAIL/mis-render; do not use runtime control text.
- UTF-8 direct: not used.

## Character Select probe

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

Native full-width `Ｅ` = glyph 466 style reference.

## Rejected / do-not-repeat paths

- Krom2RawAdd direct/global wrapper does not control Character Select target glyph.
- Do not return to Krom hooks.
- Do not return to endless stacked-diacritic polishing inside 12x12.
- 0.6.2.18 already tested; never retest.
- 0.6.3.0 already tested; never retest.
- 0.6.3.1 is unsafe; never retest.

## 0.6.2.x conclusion

### 0.6.2.13 STATIC SLOT / NO HOOK — BREAKTHROUGH PASS
Direct static-atlas replacement renders custom Vietnamese glyph data while surrounding text remains normal.

### 0.6.2.14..0.6.2.20
12x12 cannot comfortably hold stacked Vietnamese marks while keeping the native base-letter body full-size.

=> reject native 12x12 for production `Ế, Ể, Ẳ, Ỗ, Ử, Ấ, Ố...`.

## Extended-height renderer facts

Character renderer:

```text
0x8003C210
```

Native atlas pointer math hardcodes `glyph_index * 72` near:

```text
0x8003C4F8
0x8003C4FC
0x8003C500
```

Glyph metadata struct produced by renderer includes:

```text
+0  glyph width metric
+2  source/copy height metric
+4  source glyph pointer
+8  custom-atlas flag
```

Wide-glyph unpack/copy:

```text
0x8003C67C
```

Each row:

```text
6 source bytes -> 8 converted/cache bytes
```

Therefore:

```text
native 12 rows -> 96 converted bytes
extended 16 rows -> 128 converted bytes
```

Descriptor relevant bytes:

```text
+4/+5 = texture UV
+6    = visible width
+7    = visible height
```

## 0.6.3.0 EXTENDED HEIGHT 12x16 — STRUCTURAL PASS

- target source 12x16 / 96 bytes;
- target source/copy height = 16 rows;
- target visible sprite height = 16;
- native glyphs remain 12x12.

Runtime review shows extra headroom + full E body lower than surrounding text, exactly matching an extended glyph before baseline correction.

=> 16-row copy/display is structurally proven.

## 0.6.3.1 BASELINE + 16-ROW STRIDE — UNSAFE FAIL

Added:

1. target Y `-4 px`;
2. shared cache/VRAM advance rewrite around `0x8003CD94` to reserve 16 rows.

Runtime:

- unrelated Japanese corrupt/repeat;
- Character Select corrupt;
- later screen garbled;
- game freezes.

=> shared cache allocator/cursor mutation is unsafe.

Strongest suspect block:

```text
0x8003CD94 .. 0x8003CDB4
```

Do not patch this block globally/naively again.

## 0.6.3.2 BASELINE ONLY — STABLE PASS WITH LOWER-ROW LOSS

Control:

```text
ＴＥＳＴ亜Ａ
```

Changes from 0.6.3.0:

- keep 16-row source/copy/display path;
- add only target Y `-4 px`;
- leave shared cache RAM pointer and VRAM Y cursor native.

Runtime user result:

- Japanese header normal;
- `ＴＥＳＴ` normal;
- extended target baseline improved;
- trailing `Ａ` intact;
- no global text corruption;
- no freeze;
- but the lower part of `Ế` is missing/cut.

=> baseline-only hook is safe.
=> 0.6.3.1 regression comes from cache-stride/shared-state experiment, not baseline correction.

## Strong hypothesis after 0.6.3.2 — following glyph overwrites target bottom

Target writes 16 converted rows = 128 bytes, but native shared cursor still advances only 12 rows = 96 bytes.

Thus the following native glyph may start 4 rows too early and overwrite the target's last 4 rows.

The runtime pattern fits this: target upper/body region exists, lower region disappears, while following `Ａ` itself remains intact.

This is NOT yet proven.

## CURRENT PROBE — 0.6.3.3 EOL OVERWRITE TEST

Change exactly one variable:

```text
0.6.3.2: ＴＥＳＴ亜Ａ
0.6.3.3: ＴＥＳＴ亜
```

Target deliberately ends the line.

No new renderer hook.
No cache-stride/CD94 hook.
No changed copy/display logic.

Diagnostic question:

> Does the bottom of the 16-row `Ế` return when there is no following glyph to overwrite it?

Interpretation:

- bottom returns => following-glyph cache overwrite confirmed;
- bottom still missing => target's own copy/display/clipping path still truncates lower rows.

## Production direction if overwrite is confirmed

Do NOT advance the shared global font-cache cursor differently for one glyph.

Preferred next reverse:

1. identify a dedicated/isolated converted-cache region for extended Vietnamese glyphs;
2. use target-specific RAM/VRAM destination addresses while preserving native shared allocator state;
3. or build a separate extended Vietnamese cache/atlas path;
4. then test multiple extended Vietnamese glyphs followed by native glyphs.

## Saved checkpoint / archive map

The following files must be preserved and read before continuing in a future chat:

```text
LATEST.md
HANDOFF_CURRENT.md
CHARACTER_SELECT_FONT_REVERSE_0.1.md
PROBE_BUILD_INDEX.md
FONT_ISOLATION_0.6.3.1_UNSAFE_FAIL.md
FONT_ISOLATION_0.6.3.2_STABLE_PASS.md
FONT_ISOLATION_0.6.3.3_EOL_OVERWRITE_TEST.md
PS1_LOCALIZATION_REUSABLE_LESSONS.md
NEXT_CHAT_PROMPT.md
```

Local packages referenced by the current checkpoint:

```text
GaiaMaster_FontIsolation_0.6.3.2_BASELINE_ONLY.zip
GaiaMaster_FontIsolation_0.6.3.3_EOL_OVERWRITE_TEST.zip
```

`PROBE_BUILD_INDEX.md` is the authoritative anti-confusion index for old probe statuses and package names.

`PS1_LOCALIZATION_REUSABLE_LESSONS.md` preserves methodology reusable across future PS1 projects, including the conclusion that Japanese Shift-JIS/custom-font titles are often harder than US/EU Latin titles, though engine-specific exceptions remain.

## Long-term after stable extended-height path

1. production-safe extended Vietnamese atlas/cache storage;
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

- visible Character Select probes;
- no deep gameplay unless necessary;
- maximize information per test;
- never repeat already-tested builds;
- stop immediately on global corruption/freeze;
- prefer structural fixes over cosmetic one-pixel iteration.

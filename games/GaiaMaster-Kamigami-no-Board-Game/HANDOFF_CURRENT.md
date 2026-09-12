# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** custom Vietnamese glyph pipeline is proven. Native 12x12 is rejected for production stacked diacritics. 0.6.3.0 proves target 12x16 structurally. 0.6.3.1 shared cache-stride rewrite is unsafe. 0.6.3.2 is stable with lower-row loss. 0.6.3.3 disproved following-glyph overwrite. 0.6.3.4 UV+4 is negative. 0.6.3.5 sentinel did not fire because late `s0` identity was unreliable. **0.6.3.6 EARLY-FLAG is UNSAFE and freezes immediately after Sony logo.** Next work must identify the target inside the copy pipeline using existing source/metadata pointer state, without persistent/global flags.

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
- mixed JP/VI + graphic text remain after font work.

## Encoding facts

- Shift-JIS Japanese: OK.
- Full-width Latin CP932: OK runtime.
- ASCII 1-byte: FAIL/mis-render.
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

## Native 12x12 conclusion

`0.6.2.13 STATIC SLOT / NO HOOK` proved direct static-atlas Vietnamese glyph rendering works. Later 12x12 experiments proved stacked marks such as `Ế, Ể, Ẳ, Ỗ, Ử, Ấ, Ố` do not have enough headroom without shrinking the base body.

=> Production must use extended height.

## Extended-height renderer facts

Character renderer:

```text
0x8003C210
```

Custom atlas native pointer math near:

```text
0x8003C4F8
0x8003C4FC
0x8003C500
```

computes `glyph_index * 72`.

Glyph metadata struct:

```text
+0  width metric
+2  source/copy height metric (height-1)
+4  source glyph pointer
+8  custom-atlas flag
```

Wide custom copy routine:

```text
0x8003C67C
```

Per row:

```text
6 source bytes -> 8 converted/cache bytes
```

So:

```text
12 rows -> 96 converted bytes
16 rows -> 128 converted bytes
```

Metadata height=15 genuinely runs 16 iterations.

Sprite descriptor relevant bytes:

```text
+4/+5 = texture U/V
+6    = visible width
+7    = visible height
```

Font cache page is much taller than 12 rows, so a simple glyph upload-height=12 explanation is not sufficient.

## 0.6.3.x probe history

### 0.6.3.0 EXTENDED HEIGHT — STRUCTURAL PASS

12x16 source + 16-row copy + taller target footprint is real. Baseline intentionally not corrected.

### 0.6.3.1 BASELINE + 16-ROW STRIDE — UNSAFE FAIL

Naive target-specific rewrite of shared cache RAM/VRAM advance around `0x8003CD94..0x8003CDB4` causes global text corruption and later freeze.

Never repeat.

### 0.6.3.2 BASELINE ONLY — STABLE PASS WITH LOWER-ROW LOSS

Control `ＴＥＳＴ亜Ａ`.

- Japanese stable;
- TEST normal;
- baseline improved;
- trailing A intact;
- lower target rows missing/cut.

### 0.6.3.3 EOL OVERWRITE — OVERWRITE DISPROVEN

Target at end of line still loses same lower rows.

### 0.6.3.4 UV WINDOW — NEGATIVE

Target texture V+4 does not restore lower native E cleanly.

### 0.6.3.5 POST-COPY RAM SENTINEL — NO SENTINEL

Late hook at `0x8003CC4C` tried target detection with `s0==0x889F`.

Runtime stable but neither control nor test band appears.

Conclusion: late `s0` identity is not trustworthy. This build says nothing about row12..15 survival.

### 0.6.3.6 EARLY-FLAG POST-COPY SENTINEL — UNSAFE FAIL

Changed target identity strategy:

```text
metadata stage: target 0x889F -> FLAG=1
other glyphs -> FLAG=0
late sentinel hook reads FLAG
```

Runtime result:

- Sony logo appears;
- game freezes immediately afterward, before Character Select;
- repeated test gives the same freeze.

=> no sentinel result exists.
=> 0.6.3.6 must never be retested.

Strongest new suspect: introducing persistent mutable runtime state in the cave / enlarging the metadata hook changed boot-time behavior. A zero-filled file region is not automatically safe as long-lived runtime storage.

Dedicated note:

```text
FONT_ISOLATION_0.6.3.6_UNSAFE_FAIL.md
```

## NEXT TASK — REVERSE BEFORE BUILDING

Do not immediately build 0.6.3.7 from another guessed state flag.

Return to the stable 0.6.3.5/0.6.3.3 architecture and reverse exact live arguments/registers around the actual copy call into `0x8003C67C`.

Goal: identify the extended target using data that already exists in the local pipeline, preferably:

1. unique 12x16 source glyph pointer;
2. metadata `+4` source pointer;
3. target-specific height/source combination;
4. a register/stack argument inside `0x8003C67C` itself.

Preferred diagnostic after this reverse:

- hook inside or immediately adjacent to `0x8003C67C` where source pointer is proven live;
- compare that source pointer against the unique extended target source address;
- write sentinel only for that call;
- no late `s0` check;
- no persistent FLAG;
- no shared cache allocator mutation.

The next runtime probe should answer one question only: do converted rows 12..15 exist after the copy routine?

## Hard do-not-repeat rules

- no Krom path;
- no production 12x12 stacked-accent polishing;
- no retest 0.6.2.18;
- no retest any 0.6.3.0..0.6.3.6 build;
- no `CD94` shared allocator/cursor rewrite;
- no 0.6.3.6-style persistent early FLAG.

## Long-term after extended-height path is stable

1. production-safe Vietnamese extended atlas/cache storage;
2. full Vietnamese glyph inventory;
3. compact runtime codepage/mapping;
4. encode `vi_full` có dấu;
5. solve/repack 230 pending rows;
6. clean mixed JP/VI;
7. patch graphic menus/title;
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
- never repeat tested builds;
- stop immediately on global corruption/freeze;
- structural fixes over cosmetic pixel iteration.

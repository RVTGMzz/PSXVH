# HANDOFF — Gaia Master PS1 Việt hóa

> Current source-of-truth sau runtime test **0.6.2.18 CLEAN ACCENT**. Next diagnostic: **0.6.2.19 VARIANT GRID**.

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
- ASCII 1-byte: FAIL/mis-render, không dùng runtime control text.
- UTF-8 trực tiếp: không dùng.

## Character Select visible probe

```text
PRGPACK.BDP + 0xBFD2C
owner nested BDP = entry 29
local offset = +0x580
```

## Custom atlas path đã reverse

```text
atlas RAM    = 0x8006BCEC
mapping RAM  = 0x8007AECC
atlas file   = SLPS + 0x5C4EC
mapping file = SLPS + 0x6B6CC
```

Atlas:

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

Native full-width `Ｅ` = glyph 466 and is the style reference.

## Probe history chốt

### Krom path rejected
C2/D2/E2 do not affect Character Select. Do not return to Krom wrapper hooks.

### 0.6.2.13 STATIC SLOT / NO HOOK — BREAKTHROUGH PASS
- no renderer hook
- no code cave
- full-width control text
- direct static atlas replacement

Runtime: other text normal; target glyph becomes near-Vietnamese accented E.

=> **Vietnamese glyph pipeline PASS.**

### 0.6.2.14 / 0.6.2.15 — compact body rejected
Shrinking E body to gain accent headroom makes accented capitals visually smaller. Not acceptable for production.

### 0.6.2.16 FULL HEIGHT
Production rule: preserve native capital body size. E rows 2..11 remain native byte-for-byte; accents use only rows 0..1. Runtime size/baseline is correct, but accent silhouette remains weak.

### 0.6.2.17 FULL HEIGHT AA ACCENT
Tried bright peak + darker shoulders/shadow. Runtime closer, but marks look blotchy/dark and not clean enough.

### 0.6.2.18 CLEAN ACCENT — runtime result
Removed dark AA/shadow from accent and used bright strokes only. Runtime screenshot still not aesthetically acceptable: glyph is close to `Ế`, but mũ + sắc remain unclear/awkward.

Important: **0.6.2.18 has already been runtime tested. Do not ask user to test it again.**

## NEXT — 0.6.2.19 VARIANT GRID

Stop one-build-per-pixel-tweak loop.

Build one diagnostic ROM showing six full-height `Ế` candidates in one Character Select line.

Probe bytes:

```text
ＴＥＳＴ + 889F + 88A0 + 88A1 + 88A2 + 88A3 + 88A5
```

Temporary diagnostic mappings:

```text
889F -> slot 850
88A0 -> slot 851
88A1 -> slot 852
88A2 -> slot 853
88A3 -> slot 854
88A5 -> slot 855
```

All six variants:
- native E body rows 2..11 preserved byte-for-byte;
- only rows 0..1 differ;
- no renderer hook;
- no Krom hook;
- no code cave.

Variants left-to-right:

1. clean compact
2. narrow / less clutter
3. wide circumflex
4. light native-edge shading
5. minimal sparse
6. left-shifted circumflex

User should send one screenshot and select best sample `1..6` left-to-right. Then lock that geometry for the Vietnamese glyph family instead of doing more single-variant ROM probes.

## After variant selection

1. lock full-height glyph template;
2. build full Vietnamese glyph inventory;
3. design compact runtime codepage/mapping without breaking untranslated Japanese;
4. encode `vi_full` with accents;
5. solve/repack 230 pending overflow rows;
6. clean mixed JP/VI;
7. patch graphic menus/title text;
8. full runtime QA + reproducible build package.

## Windows builder pitfalls

- avoid parsing `(Japan).bin` inside parenthesized BAT blocks;
- launcher ASCII + CRLF;
- test PC currently has `C:\Python312\python.exe`;
- Japanese JSON: explicit UTF-8 or `ensure_ascii=True`.

## User testing preference

- visible Character Select probes;
- no deep gameplay unless necessary;
- maximize information per test;
- never repeat an already-tested build because of checkpoint confusion.

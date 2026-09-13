# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** giữ renderer/font geometry native **12x12 / 72-byte / 4bpp**. Nhánh 12x16 và composite overlay không còn là production path. Build runtime mới nhất `0.6.5.2 ATLAS-BACKED CUSTOM BANK` là **UNSAFE FAIL**: màn đen, Game FPS 0, treo trước khi có output hữu ích. Hiện tại chuyển sang **READ-ONLY font mapping recovery**. Không có ROM probe nào cần test lúc này.

## Baseline

- Game: `GaiaMaster - Kamigami no Board Game (Japan).bin`
- serial: `SLPS-02075`
- clean BIN SHA1: `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- Alpha 0.6.1 FRONT SHA1: `54d2fb026bc3b71c79861e723caffb4114caa34c`
- branch: `gaia-character-select-font-atlas-reverse-01`
- repo: `ronvotri/Viet-Hoa-PS1`

## Proven font facts

```text
atlas RAM    = 0x8006BCEC
mapping RAM  = 0x8007AECC
atlas file   = SLPS + 0x5C4EC
mapping file = SLPS + 0x6B6CC
860 glyphs
native 12x12 / 72-byte / 4bpp / LOW nibble first
```

Confirmed examples:

```text
0x8273 Ｔ -> glyph 481
0x8264 Ｅ -> glyph 466
0x8272 Ｓ -> glyph 480
0x889F 亜 -> glyph 0
```

Character Select test text location:

```text
PRGPACK.BDP + 0xBFD2C
owner nested BDP = entry 29
local offset = +0x580
```

## Historical conclusions

### 0.6.2.x

- `0.6.2.13` proved static custom-atlas replacement works.
- Later 0.6.2.x art tests showed that one native 12x12 cell cannot hold a full-size Latin body plus stacked Vietnamese marks with acceptable quality.

### 0.6.3.x

Extended-height 12x16 research touched too much shared renderer state and repeatedly produced layout corruption/freezes. Keep the reverse notes for reference, but do not revive this as the production direction.

### 0.6.4.x composite overlay

The accent artwork itself became visually acceptable, but overlay placement was not reliable enough across Gaia's real render/cache paths. Stop tuning X/Y offsets. Composite is no longer the production direction.

## External reference — Yu-Gi-Oh! MCBB Vietnamese PS1 patch

Reference repo:

`https://github.com/2ez4gcx/yugioh-mcbb-vi-patch`

Its public README states that the release patch includes translated text, redrawn font and a few code-adjustment bytes. The user also supplied `yugioh-mcbb-vi.ppf` for study.

Strategic lesson for Gaia:

> prefer native geometry + font/resource replacement + targeted mapping/data changes over a large renderer redesign.

Do not claim the Yu-Gi-Oh patch uses Gaia's exact structures or exact technique.

## 0.6.5.x mapping pivot

Full note:

`FONT_MAPPING_PIVOT_0.6.5.md`

### 0.6.5.0 UNIFIED NATIVE-CELL FONT

Intended style board:

```text
A Â Ấ Ẳ E Ê Ế Ể O Ô Ố Ỗ
```

Runtime instead showed mostly repeated A-like glyphs plus one unrelated Kanji.

Conclusion:

> consecutive CP932 codes do **not** map linearly to consecutive atlas slots.

### 0.6.5.1

Builder stopped before patching because it incorrectly assumed a much larger zero-filled storage area than actually exists. Clean ROM was valid.

### 0.6.5.2

Attempted a runtime redirect into a contiguous custom bank.

Result: **UNSAFE FAIL**

- black screen;
- Game FPS 0;
- hard freeze.

Do not retest and do not reuse this redirect design.

## CURRENT — Font Mapping Scanner 0.1

There is currently **NO ROM probe** to run.

Local package:

```text
GaiaMaster_FontMappingScanner_0.1.zip
```

Launcher:

```text
00_RUN_FONT_MAPPING_SCANNER.cmd
```

Expected report:

```text
GaiaMaster_FontMappingScanner_01.txt
```

The scanner is READ ONLY. It reads CLEAN or Alpha 0.6.1 BIN, does not patch anything, and does not require emulator boot.

Goal:
- recover the exact mapping relationship used by Gaia;
- confirm where the mapping data lives;
- determine whether it can be patched as data only;
- only after that, build a new native-cell Vietnamese font proof.

Preferred production architecture after mapping is proven:

```text
Vietnamese/internal code
  -> mapping table entry
  -> chosen unused Japanese glyph slot
  -> native 12x12 / 72-byte Vietnamese glyph
```

## Hard do-not-repeat

- no Krom path;
- no production 12x16 path;
- no retest 0.6.2.18;
- no retest 0.6.3.x failed probes;
- no composite X/Y tuning loop;
- no runtime redirect like 0.6.5.2;
- no assumption that consecutive codes map to consecutive atlas slots;
- no new runtime probe until mapping ownership is proven.

## User testing preference

- minimize emulator tests;
- maximize information per test;
- never repeat tested builds;
- prefer READ-ONLY scanner/reverse work first;
- stop immediately on freeze/global corruption.

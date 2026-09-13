# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** `0.6.6.1 BASELINE-NORMALIZED` remains LAST GOOD runtime architecture. Production is locked to **native 12x12 / 72-byte / 4bpp / static mapping-only**. `0.6.6.2c` narrow 6x12 runtime failed and is retired. Full theoretical 134-glyph Vietnamese does not fit the conservative clean atlas, but the **actual current `vi_full` corpus requires exactly 60 custom Vietnamese glyphs and DOES fit the 64 zero-hit slot capacity**. Current runtime candidate is **0.6.7.0 Production Codepage 60 / Multi-UI Proof**.

## Baselines

- Game: `GaiaMaster - Kamigami no Board Game (Japan).bin`
- serial: `SLPS-02075`
- clean BIN SHA1: `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- clean SLPS SHA1: `1dfeb6b7cfda59c108dde2dc0b8abda9a40e6ae5`
- clean PRGPACK SHA1: `a9b195b8ae5d8cad7f4f755daa08337d4671632c`
- repo: `ronvotri/Viet-Hoa-PS1`
- branch: `gaia-character-select-font-atlas-reverse-01`

## Proven font facts

```text
runtime GP     = 0x80085F28
atlas global   = gp+0x518
mapping global = gp+0x51C
main atlas RAM = 0x8006BCEC
mapping RAM    = 0x8007AECC
main atlas file= SLPS+0x5C4EC
mapping file   = SLPS+0x6B6CC
860 glyphs
native main font = 12x12 / 72-byte / 4bpp / LOW nibble first
```

Mapping pipeline:

```text
code & 0x7FFF
 -> mapping[index]
 -> glyph index
 -> glyph_index * 72
 -> atlas base + offset
```

Known mapping facts:

```text
0x8273 Ｔ -> glyph 481
0x8264 Ｅ -> glyph 466
0x8272 Ｓ -> glyph 480
0x889F 亜 -> glyph 0
```

## Runtime locks

- `0.6.2.13`: static custom-atlas replacement PASS.
- `0.6.3.x`: 12x16 caused corruption/freezes. Historical only.
- `0.6.4.x`: composite overlay unreliable. Stop.
- `0.6.5.2`: **UNSAFE FAIL / NEVER RETEST**, pointer redirect caused black screen/FPS0/hard freeze.
- `0.6.5.3`: mapping-only structural PASS.
- `0.6.5.4`: native base copy PASS.
- `0.6.5.5`: compact accent style PASS enough for production.
- `0.6.6.0`: real text `Chọn tướng` rendered end-to-end.
- `0.6.6.1`: baseline-normalized real text **PASS / LAST GOOD**.
- `0.6.6.2`: gate false block, no runtime.
- `0.6.6.2b`: gate false block, no runtime.
- `0.6.6.2c`: native narrow 6x12 one-byte alias **RUNTIME FAIL**, garbled glyphs. Retired.

Wide horizontal spacing in 0.6.6.1 is now classified as **visual polish only**. Do not rewrite architecture to chase it.

## Production Capacity Scanner 0.1 — result

Worst-case full Vietnamese target:

```text
134 custom glyphs
837 zero-static-hit custom codes
64 zero-static-hit atlas slots
34 completely unmapped zero-hit slots
30 mapped-but-static-unused zero-hit slots
```

Result: **134-glyph theoretical full repertoire does NOT fit**. This was a valid capacity FAIL, not a broken build.

## vi_full Inventory 0.1 — PASS

Translation Master 0.6:

```text
total rows               = 596
rows with non-empty vi_full = 393
unique chars in vi_full  = 125
custom Vietnamese glyphs = 60
lowercase custom         = 56
uppercase custom         = 4
zero-hit atlas capacity  = 64
```

Actual current `vi_full` therefore **fits** with 4 conservative reserve slots.

Exact current custom set:

```text
àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ
```

No other non-ASCII/non-Vietnamese policy characters are currently required by `vi_full`.

## Production slot allocation

Frozen 60 production slots:

```text
# 34 completely unmapped zero-hit
18 33 58 160 182 261 301 371 392
420 421 422 423 424 425 426 427 428 429 430 431
432 433 434 435 436 437 438 439 440
517 695 704 713

# 26 mapped-but-static-unused zero-hit
38 94 108 109 129 130 150 208 295 326 335 345 372
385 394 398 400 403 702 715 729 745 750 754 757 790
```

Reserve zero-hit slots left untouched:

```text
794 807 821 824
```

Custom code selection remains deterministic from the verified CLEAN BIN using the existing zero-static-hit scan. Code space is not the bottleneck.

## 0.6.6.1 baseline helper preserved

Repo helper:

```text
tools/gaia_0661_baseline.py
```

This preserves the baseline-normalized 12x12 glyph composition used by the last-good runtime direction so production work does not fall back to the older 0.6.6.0 fixed-body compression.

## CURRENT — 0.6.7.0 Production Codepage 60 / Multi-UI Proof

Design note:

```text
PRODUCTION_CODEPAGE_0.6.7.0.md
```

Local test package:

```text
GaiaMaster_0.6.7.0_PRODUCTION_CODEPAGE_60_MULTI_UI_PROOF.zip
```

The package installs all 60 current `vi_full` custom glyphs into the frozen production slots using native 12x12 + static mapping-only routing.

Quick runtime proof patches three nearby setup/player-selection strings:

```text
PRGPACK+0xBFBEC -> Đã ổn?
PRGPACK+0xBFD2C -> Chọn tướng
PRGPACK+0xBFE4C -> Nhấn O
```

Builder safety:
- CLEAN BIN SHA1 gate;
- clean SLPS/PRGPACK SHA1 gate;
- mapping facts rechecked;
- all 60 production + 4 reserve slots rechecked as zero-static-hit;
- native base slots protected;
- source Japanese bytes verified before replacement;
- Vietnamese proof must fit the old source field;
- nested + top BDP checksums rebuilt;
- raw CD EDC/ECC rebuilt;
- emits runtime report + exact CODEPAGE60 manifest.

Expected runtime behavior:
- stable boot;
- three proof strings render as Vietnamese;
- spacing remains full-width and is **not a fail** for this phase;
- no global corruption.

If runtime PASS:
1. freeze the emitted `CODEPAGE60` manifest as production source-of-truth;
2. integrate encoder into Translation Master rebuild;
3. patch batches of real `vi_full` rows whose encoded text fits safely;
4. design explicit relocation/length strategy for rows that do not fit in-place.

## Hard do-not-repeat

- no Krom path;
- no production 12x16;
- no failed 0.6.3.x retests;
- no composite overlay loop;
- no 0.6.5.2 pointer redirect;
- no 0.6.6.2 / 2b retests;
- no 0.6.6.2c retest;
- no one-byte narrow alias production path;
- no global cursor/cache/spacing mutation;
- no spacing-driven architecture rewrite;
- no repeated 134-glyph scanner unless reclaim policy changes;
- stop immediately on freeze/global corruption.

## Testing preference

- minimize emulator tests;
- maximize information per test;
- never repeat known failed/already-proven builds;
- read reports immediately when uploaded.

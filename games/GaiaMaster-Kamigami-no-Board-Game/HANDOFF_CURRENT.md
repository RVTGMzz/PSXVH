# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** production is locked to **native 12x12 / 72-byte / 4bpp / static mapping-only**. `0.6.7.2` is the frozen **FONT VISUAL PASS**. `0.6.9.2` re-established the old Alpha gameplay coverage with an exact 397-key legacy gate. The active candidate is **0.6.10.0 HYBRID FULL-COVERAGE + FRONT ACCENT BATCH 1**, which keeps broad gameplay coverage while upgrading all 31 dedicated intro/setup fallback rows to compact accented Vietnamese.

## Baselines

- Game: `GaiaMaster - Kamigami no Board Game (Japan).bin`
- serial: `SLPS-02075`
- clean BIN SHA1: `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- clean SLPS SHA1: `1dfeb6b7cfda59c108dde2dc0b8abda9a40e6ae5`
- clean PRGPACK SHA1: `a9b195b8ae5d8cad7f4f755daa08337d4671632c`
- repo: `ronvotri/Viet-Hoa-PS1`
- branch: `gaia-character-select-font-atlas-reverse-01`

## Proven font architecture

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

Pipeline:

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

## Runtime history / hard locks

- `0.6.2.13`: static custom-atlas replacement PASS.
- `0.6.3.x`: 12x16 caused corruption/freezes. Historical only.
- `0.6.4.x`: composite overlay unreliable. Stop.
- `0.6.5.2`: **UNSAFE FAIL / NEVER RETEST**, pointer redirect caused black screen/FPS0/hard freeze.
- `0.6.5.3`: mapping-only structural PASS.
- `0.6.5.4`: native-base copy PASS.
- `0.6.5.5`: compact accent style PASS enough for production.
- `0.6.6.0`: real text `Chọn tướng` rendered end-to-end.
- `0.6.6.1`: baseline-normalized real text PASS.
- `0.6.6.2` + `0.6.6.2b`: safety-gate false blocks, no runtime.
- `0.6.6.2c`: native narrow 6x12 one-byte alias runtime FAIL, garbled glyphs. Retired.
- `0.6.7.0`: full 60-glyph production codepage boots and renders correctly.
- `0.6.7.1`: horn placement improved; acute/grave still too close.
- `0.6.7.2`: **FONT VISUAL PASS / FREEZE THIS STYLE.** User judged `Chọn tướng` perfect. Horn hugs `ơ/ư`; acute/grave are separated cleanly. Do not retune unless a real production regression appears.

Wide horizontal spacing is accepted polish and is not an architecture blocker.

## Production capacity / frozen codepage

Worst-case 134-glyph theoretical Vietnamese set does not fit conservative clean capacity:

```text
837 zero-static-hit custom codes
64 zero-static-hit atlas slots
34 completely unmapped zero-hit slots
```

Actual Translation Master 0.6 corpus:

```text
596 rows total
393 rows with non-empty vi_full
60 custom Vietnamese glyphs
```

Result: **PASS with 4 reserve slots**.

Frozen custom set:

```text
àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ
```

Frozen production slots:

```text
# 34 completely unmapped zero-hit
18 33 58 160 182 261 301 371 392
420 421 422 423 424 425 426 427 428 429 430 431
432 433 434 435 436 437 438 439 440
517 695 704 713

# 26 mapped-but-static-unused zero-hit
38 94 108 109 129 130 150 208 295 326 335 345 372
385 394 398 400 403 702 715 729 745 750 754 757 790

# reserve
794 807 821 824
```

## Coverage recovery — 0.6.8.x / 0.6.9.x

### 0.6.8.0 / 0.6.8.1

These safe-fit/front-end experiments did not visibly restore the expected menu/card/gameplay coverage. `Chọn tướng` worked, but user runtime testing showed most gameplay still Japanese. Do not treat these as the production coverage baseline.

### Old Alpha coverage source

Old Alpha 0.6.1 used:

```text
tools/generate_alpha061_patches.py
tools/build_alpha061_front.py
```

The old generator produced exactly **397 patches** from:

- `TRANSLATION_MASTER_0.6_part01..06.csv` using `vi_game_current` when it fit;
- `FRONT_DEMO_ADDED_061.csv` for dedicated front/setup additions.

### 0.6.9.0

Hybrid pipeline preferred `vi_full`, fell back to `vi_game_current`, and preserved raw runtime tokens `%s/%d/%+3d`, `/V`, `/v`.

Builder found `399` total patches, but a bad gate demanded total exactly `397`.

**BUILD GATE BUG ONLY. No runtime conclusion. Do not retest.**

### 0.6.9.1

Second gate incorrectly treated every non-empty `vi_game_current` row as a legacy Alpha patch, even rows Alpha itself skipped for length. It reported `228` lost fitting rows.

**BUILD GATE BUG ONLY. No runtime conclusion. Do not retest.**

### 0.6.9.2 — exact legacy gate

Gate was fixed by reconstructing the old Alpha patch-key set exactly:

```text
legacy Alpha key set = 397 / 397
extra vi_full-only rows are allowed
```

Runtime screenshot showed translated intro text such as:

```text
100 NAM MENH
LUC DIA LOAN
THOI GAIA MASTER
DEN LUC!
```

This proves the broad old Alpha coverage pipeline is active again. However these intro rows were still unaccented because `FRONT_DEMO_ADDED_061.csv` only had `vi_no_accents`.

**Conclusion:** `0.6.9.2 = COVERAGE PASS / ACCENT COVERAGE INCOMPLETE.`

## CURRENT — 0.6.10.0 HYBRID FULL-COVERAGE + FRONT ACCENT BATCH 1

Design note:

```text
ACCENT_UPGRADE_0.6.10.0.md
```

Exact current builder snapshot + launcher:

```text
tools/build_gaia_06100_hybrid_accent_b1.py
tools/00_BUILD_0.6.10.0_HYBRID_ACCENT_B1.cmd
```

The GitHub Python file is a runnable compressed snapshot of the exact readable builder source used for the local package.

Readable-source SHA1:

```text
faea2fbf90d3b4038ad64d3872934c043115878a
```

Local package:

```text
GaiaMaster_0.6.10.0_HYBRID_FRONT_ACCENT_BATCH1.zip
SHA1 d43e8547f9baca4e254f96fdb7850a5c6f873e86
```

### Hybrid text priority

```text
vi_full accented, if it fits
-> vi_game_current fallback, if it fits
-> dedicated front fallback/override
```

The exact old Alpha legacy set must still satisfy:

```text
397 / 397
```

Extra newer `vi_full`-only patches are allowed.

### Front Accent Batch 1

All 31 dedicated rows from `FRONT_DEMO_ADDED_061.csv` now have compact accented overrides stored in:

```text
translation/FRONT_ACCENT_OVERRIDES_0.6.10.0.csv
```

Examples:

```text
100 năm mệnh
Lực địa loạn
Thời Gaia Master
Đến lúc!
Thế giới mất chủ
Tải dữ liệu VK?
Kỹ năng LV1
Nhân vật này?
Xác nhận?
```

The builder requires all 31 accented front overrides to fit. If any one fails, it blocks instead of silently reverting to no-accent text.

### Next runtime gate

1. Build from CLEAN BIN.
2. Intro first: verify the previously unaccented intro strings now show accents.
3. If intro is good, enter a real match.
4. Check card/menu/item/prompt text.
5. Any remaining Vietnamese without accents should be treated as a **content fallback issue**, not a font/reverse issue.
6. Next production step is **Accent Upgrade Batch 2**: convert gameplay rows still using `vi_game_current` fallback into compact accented wording while retaining the 397/397 legacy coverage gate.

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
- no accent retuning after 0.6.7.2 without a demonstrated regression;
- no 0.6.9.0 / 0.6.9.1 retests;
- do not throw away `vi_game_current` fallback until an accented replacement actually fits;
- stop immediately on freeze/global corruption.

## Testing preference

- minimize emulator tests;
- maximize information per test;
- never repeat known failed/already-proven builds;
- read generated reports immediately when supplied;
- prioritize real gameplay coverage over isolated proof strings.

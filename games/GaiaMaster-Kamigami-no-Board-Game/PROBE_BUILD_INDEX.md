# Gaia Master — probe/build index

Updated: **2026-09-13**

Purpose: prevent checkpoint confusion and accidental retesting.

## Stable baselines

```text
Clean Japan BIN SHA1
f4d5298583c90d89c4b7e51d2dde160ee07f2aec

Alpha 0.6.1 FRONT SHA1
54d2fb026bc3b71c79861e723caffb4114caa34c
```

## Historical locks

- `0.6.2.13` static custom atlas: **PASS**.
- `0.6.3.x` 12x16: corruption/freezes. **Do not revive**.
- `0.6.4.x` composite overlay: unreliable. **Not production**.
- `0.6.5.2` runtime pointer redirect: **UNSAFE FAIL / NEVER RETEST**.
- Mapping Initializer Scanner 0.2: mapping/global ownership **PROVEN**.
- `0.6.5.3`: mapping-only **STRUCTURAL PASS**.
- `0.6.5.4`: native-base copy **PASS**.
- `0.6.5.5`: compact accent style **PASS enough for production**.

## 0.6.6.x

### 0.6.6.0 REAL-TEXT ENCODER
`Chọn tướng` rendered end-to-end. **PASS**, baseline needed polish.

### 0.6.6.1 BASELINE-NORMALIZED
**PASS / PREVIOUS LAST GOOD.** Native 12x12 + mapping-only + acceptable baseline.

### 0.6.6.2 / 0.6.6.2b
Safety-gate false blocks. No runtime build. Do not retest.

### 0.6.6.2c NATIVE NARROW 8PX
Builder succeeded; runtime produced unrelated/garbled glyphs. **RUNTIME FAIL / RETIRED.** Do not retest.

## Production capacity

### Capacity Scanner 0.1

```text
134 theoretical custom glyphs
837 zero-hit custom codes
64 zero-hit atlas slots
34 completely unmapped zero-hit slots
Verdict: FAIL for full theoretical Vietnamese repertoire
```

### vi_full Inventory 0.1

```text
596 Translation Master rows
393 rows with non-empty vi_full
60 custom Vietnamese glyphs
64 zero-hit atlas slots available
Verdict: PASS with 4 reserve slots
```

Frozen custom set:

```text
àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ
```

## 0.6.7.x Production Codepage 60

### 0.6.7.0
Full 60-glyph production codepage boots and renders. **PASS**, accent placement still needed polish.

### 0.6.7.1
Horn on `ơ/ư` moved closer to the body. Acute/grave still too close. Intermediate only.

### 0.6.7.2
**FONT VISUAL PASS / FREEZE.** Runtime `Chọn tướng` judged perfect by user.

Frozen rule:
- horn hugs `ơ/ư` body;
- acute/grave separated farther from horn;
- 0.6.6.1 baseline normalization retained;
- no further retuning without a demonstrated regression.

Frozen production slots:

```text
34 unmapped zero-hit:
18 33 58 160 182 261 301 371 392
420 421 422 423 424 425 426 427 428 429 430 431
432 433 434 435 436 437 438 439 440
517 695 704 713

26 mapped-but-static-unused zero-hit:
38 94 108 109 129 130 150 208 295 326 335 345 372
385 394 398 400 403 702 715 729 745 750 754 757 790

Reserve:
794 807 821 824
```

## 0.6.8.x — safe-fit/front-end experiments

### 0.6.8.0
Safe-fit `vi_full` batch. User runtime saw little visible difference beyond `Chọn tướng`. Not the desired gameplay-coverage baseline.

### 0.6.8.1
Front-end scan/coverage attempt. User still reported menu/cards/gameplay largely untranslated. Retire as current direction.

## 0.6.9.x — hybrid old-Alpha coverage recovery

Old Alpha generator/builders:

```text
tools/generate_alpha061_patches.py
tools/build_alpha061_front.py
```

Old Alpha legacy coverage = exactly **397 patch keys**.

### 0.6.9.0
Hybrid total became `399`, but gate incorrectly required total exactly `397`.

**BUILD GATE BUG. No runtime. Do not retest.**

### 0.6.9.1
Gate incorrectly counted many `vi_game_current` rows as legacy even when Alpha skipped them for length. Error reported 228 lost rows.

**BUILD GATE BUG. No runtime. Do not retest.**

### 0.6.9.2 EXACT LEGACY GATE
Reconstructed the exact old Alpha legacy set before comparing hybrid coverage:

```text
legacy = 397 / 397
extra newer vi_full-only rows allowed
```

Runtime intro screenshot showed Vietnamese fallback text:

```text
100 NAM MENH
LUC DIA LOAN
THOI GAIA MASTER
DEN LUC!
```

**COVERAGE PASS / ACCENT COVERAGE INCOMPLETE.**

This proves the gameplay/front patch pipeline is active again. The unaccented intro is expected because `FRONT_DEMO_ADDED_061.csv` only contained `vi_no_accents`.

## CURRENT — 0.6.10.0 HYBRID FULL COVERAGE + FRONT ACCENT BATCH 1

Current files:

```text
tools/build_gaia_06100_hybrid_accent_b1.py
tools/00_BUILD_0.6.10.0_HYBRID_ACCENT_B1.cmd
ACCENT_UPGRADE_0.6.10.0.md
translation/FRONT_ACCENT_OVERRIDES_0.6.10.0.csv
```

Exact readable builder source SHA1:

```text
faea2fbf90d3b4038ad64d3872934c043115878a
```

Local package:

```text
GaiaMaster_0.6.10.0_HYBRID_FRONT_ACCENT_BATCH1.zip
SHA1 d43e8547f9baca4e254f96fdb7850a5c6f873e86
```

Coverage rule:

```text
exact legacy Alpha key coverage = 397 / 397
extra vi_full-only patches allowed
```

Text priority:

```text
vi_full accented if it fits
-> vi_game_current fallback if it fits
-> dedicated front fallback/override
```

0.6.10.0 adds accented compact overrides for all **31** `FRONT_DEMO_ADDED_061.csv` rows. Builder blocks if any of those 31 accented overrides fails to fit.

Expected intro improvements:

```text
100 năm mệnh
Lực địa loạn
Thời Gaia Master
Đến lúc!
Thế giới mất chủ
```

### Next gate

1. runtime-test intro accents;
2. if intro passes, enter real match;
3. inspect card/menu/item/prompt text;
4. remaining no-accent Vietnamese means fallback content still needs an accented compact rewrite;
5. proceed to **0.6.10.x / 0.6.11.0 Accent Upgrade Batch 2** for gameplay fallback rows, while keeping exact 397/397 legacy coverage.

## Do not repeat

- no Krom path;
- no production 12x16;
- no failed 0.6.3.x retests;
- no composite overlay loop;
- no 0.6.5.2 pointer redirect;
- no 0.6.6.2 / 2b retests;
- no 0.6.6.2c retest;
- no one-byte narrow alias path;
- no global cursor/cache spacing mutation;
- no spacing-driven architecture rewrite;
- no accent retuning after 0.6.7.2 without a demonstrated regression;
- no 0.6.9.0 / 0.6.9.1 retests;
- do not remove fallback coverage unless an accented replacement really fits;
- stop immediately on freeze/global corruption.

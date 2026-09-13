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
**PASS / PREVIOUS LAST GOOD.** Native 12x12 + mapping-only + acceptable baseline. Full-width spacing is polish only.

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
Horn on `ơ/ư` moved closer to the body successfully. Acute/grave became too close to horn. **INTERMEDIATE VISUAL PASS.**

### 0.6.7.2
**FONT VISUAL PASS / FREEZE.** Runtime screenshot of `Chọn tướng` judged perfect by user.

Production accent rule now locked:
- horn hugs the `ơ/ư` body;
- acute/grave are separated farther from horn;
- 0.6.6.1 baseline normalization retained;
- do not retune unless a new production regression appears.

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

## CURRENT — 0.6.8.0 PROD60 SAFE-FIT vi_full BATCH 1

Package:

```text
GaiaMaster_0.6.8.0_PRODUCTION_SAFE_FIT_BATCH1.zip
```

Immediate sanity anchors:

```text
Đã ổn?
Chọn tướng
Nhấn O
```

Then builder processes Translation Master 0.6 parts 01..06 and applies every non-empty `vi_full` row that can safely replace its clean Japanese source in-place.

A row is applied only when:
- source file is PRGPACK.BDP or SLPS_020.75;
- exact Japanese bytes match clean data;
- source is NUL-terminated;
- no printf/control token requires raw ASCII semantics;
- encoded Vietnamese <= original Japanese byte budget.

Skipped in Batch 1:
- `%s`, `%d`, `%4d`, `%+3d` and related formatter rows;
- `/V` / `/v` control-marker rows;
- overlength rows;
- source mismatches or unsupported rows.

Safety:
- no relocation;
- no file expansion;
- no overwrite of following string;
- all touched nested BDP checksums rebuilt;
- top PRGPACK checksum rebuilt;
- Mode2/Form1 EDC/ECC rebuilt.

### PASS gate

If the three anchors remain visually identical to 0.6.7.2 and normal play shows stable translated `vi_full` strings:
- freeze CODEPAGE60 manifest;
- proceed to 0.6.8.x Batch 2 token-aware encoder;
- preserve raw format/control tokens while encoding surrounding display text.

### FAIL gate

On freeze/global corruption/unrelated glyphs:
- stop immediately;
- send screenshot + generated `PROD60 SAFEFIT B1` report;
- do not retest blindly.

## Do not repeat

- no Krom path;
- no production 12x16;
- no failed 0.6.3.x retests;
- no composite overlay loop;
- no 0.6.5.2 pointer redirect;
- no 0.6.6.2 / 2b retest;
- no 0.6.6.2c retest;
- no one-byte narrow alias path;
- no global cursor/cache spacing mutation;
- no spacing-driven architecture rewrite;
- no accent retuning after 0.6.7.2 without a demonstrated regression;
- do not patch printf/control-token rows with the plain display encoder;
- stop immediately on freeze/global corruption.

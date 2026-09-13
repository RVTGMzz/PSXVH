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
**PASS / LAST GOOD.** Native 12x12 + mapping-only + acceptable baseline. Full-width spacing is polish only.

### 0.6.6.2
Gate false-positive. No runtime build. Do not retest.

### 0.6.6.2b
Gate false-positive. No runtime build. Do not retest.

### 0.6.6.2c NATIVE NARROW 8PX
Builder succeeded; runtime produced unrelated/garbled glyphs. **RUNTIME FAIL / RETIRED.** Do not retest.

## Production Capacity Scanner 0.1

READ-ONLY worst-case result:

```text
134 custom glyph target
837 zero-hit custom codes
64 zero-hit atlas slots
34 completely unmapped zero-hit slots
Verdict: FAIL
```

Interpretation: code space is abundant; atlas capacity is the bottleneck for a theoretical full 134-glyph repertoire.

## vi_full Inventory 0.1 — PASS

Actual Translation Master 0.6 corpus:

```text
596 total rows
393 rows with non-empty vi_full
125 unique characters in vi_full
60 custom Vietnamese glyphs
56 lowercase + 4 uppercase
64 conservative zero-hit atlas slots available
```

Result: **PASS with 4 slots reserve.**

Current custom set:

```text
àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ
```

## 0.6.7.0 PRODUCTION CODEPAGE 60 / MULTI-UI

**CURRENT RUNTIME CANDIDATE.**

Production slots:

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

Repo helper preserving last-good vertical composition:

```text
tools/gaia_0661_baseline.py
```

Design note:

```text
PRODUCTION_CODEPAGE_0.6.7.0.md
```

Local package:

```text
GaiaMaster_0.6.7.0_PRODUCTION_CODEPAGE_60_MULTI_UI_PROOF.zip
```

Runtime proof strings:

```text
Đã ổn?
Chọn tướng
Nhấn O
```

Spacing remains intentionally full-width. Do not treat it as failure.

### PASS gate

If all three strings render correctly and boot/UI remain stable:
- freeze emitted `CODEPAGE60` manifest;
- integrate the encoder into real Translation Master batch rebuild;
- patch in-place rows that fit;
- separately solve relocation/length expansion for rows that do not fit.

### FAIL gate

If freeze/global corruption/unrelated glyphs occur:
- stop immediately;
- send screenshot + generated `PROD60 MULTIUI` report + `CODEPAGE60` manifest;
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
- no repeated 134-glyph capacity scan without reclaim-policy changes;
- stop immediately on freeze/global corruption.

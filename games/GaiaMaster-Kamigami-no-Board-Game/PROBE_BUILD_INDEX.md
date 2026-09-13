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

## 0.6.2.x

### 0.6.2.13 STATIC SLOT / NO HOOK
**BREAKTHROUGH PASS.** Static custom Vietnamese atlas replacement works.

## 0.6.3.x
Extended-height 12x16 research caused shared-state corruption/freezes in multiple probes.

**Do not revive 12x16 as production.**

## 0.6.4.x
Composite accents could look acceptable, but placement was unreliable.

**Not production.**

## 0.6.5.x mapping/native-cell pivot

### 0.6.5.0
**MAPPING ASSUMPTION FAIL.** Consecutive CP932 codes do not map linearly to atlas slots.

### 0.6.5.2
**UNSAFE FAIL. NEVER RETEST.** Runtime pointer redirect caused black screen / Game FPS 0 / hard freeze.

### Font Mapping Initializer Scanner 0.2
**OWNERSHIP PROVEN.**

```text
runtime GP = 0x80085F28
atlas global = gp+0x518
map global   = gp+0x51C
atlas = 0x8006BCEC
map   = 0x8007AECC
```

### 0.6.5.3 MAPPING-ONLY NATIVE-CELL
**STRUCTURAL PASS / GLYPH-GENERATOR FAIL.**

Mapping-only path boots, reaches custom atlas cells, no hook or pointer redirect required.

### 0.6.5.4 NATIVE-BASE STYLE
**PIPELINE PASS / VERTICAL CROWDING.**

Native A/E/O copied byte-for-byte render correctly.

### 0.6.5.5 ACCENT-SAFE COMPACT
**VISUAL PASS ENOUGH TO LEAVE GLYPH-BOARD PHASE.**

Compact Vietnamese marks readable. Mapping-only + native 12x12 locked as production direction.

## 0.6.6.x production encoder

### 0.6.6.0 PRODUCTION ENCODER REAL-TEXT

Expected/runtime text:

```text
Chọn tướng
```

Runtime result: **REAL-TEXT ENCODER PASS / BASELINE POLISH NEEDED.**

Passed:
- actual Vietnamese phrase appears;
- plain Latin uses native Gaia full-width glyphs;
- `ọ`, `ư`, `ớ` use custom zero-static-hit CP932 codes + safe atlas cells;
- static mapping-only production encoder works end-to-end;
- stable boot/UI; no freeze/global corruption.

Visual issue:
- custom chars sit at uneven vertical positions relative to native Latin.

Root cause:
- custom base glyphs were always compressed into fixed rows `2..9`, unnecessarily changing native baseline.

**Do not reinterpret 0.6.6.0 as mapping/encoder failure.**

## CURRENT — 0.6.6.1 BASELINE-NORMALIZED REAL-TEXT

Detailed note:

```text
BASELINE_NORMALIZATION_0.6.6.1.md
```

Expected Character Select:

```text
Chọn tướng
```

New policy:
- preserve native body geometry/baseline when the base glyph already has enough room for marks;
- only minimal-fit when required;
- preserve native bottom edge whenever possible;
- accents are positioned relative to the body bbox;
- report records `fit_mode`, `src_bbox`, `body_bbox`, `final_bbox`.

Package:

```text
GaiaMaster_0.6.6.1_BASELINE_NORMALIZED_REAL_TEXT_PROOF.zip
```

Status: **READY FOR ONE RUNTIME TEST.**

If wrong, collect:

```text
screenshot
[VI 0.6.6.1 BASELINE].txt
```

## Current do-not-repeat

- no Krom path;
- no production 12x16;
- no failed 0.6.3.x retests;
- no composite X/Y tuning loop;
- no 0.6.5.2 runtime redirect;
- no assumption consecutive code == consecutive atlas slot;
- no 0.6.5.3 retest;
- no more 12-glyph style-board loops unless production regression requires it;
- no reopening mapping/encoder questions because of 0.6.6.0 baseline polish;
- stop immediately on freeze/global corruption.

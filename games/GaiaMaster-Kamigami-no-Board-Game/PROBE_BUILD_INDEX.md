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

### 0.6.2.14..0.6.2.20
Native-cell art experiments. One 12x12 cell requires a compact unified Vietnamese style.

## 0.6.3.x extended-height research

- `0.6.3.1` **UNSAFE FAIL**: corruption + freeze.
- `0.6.3.2` stable with lower-row loss.
- `0.6.3.3` following-glyph overwrite disproven.
- `0.6.3.4` UV-window negative.
- `0.6.3.6` **UNSAFE FAIL**: boot freeze.
- `0.6.3.7` rows10..11 visible, lower rows not fully visible.
- `0.6.3.8/9/12` diagnostic/layout failures.
- `0.6.3.10` stable negative.

**Do not revive 12x16 as production.**

## 0.6.4.x composite accent experiments

Accent art became acceptable, but overlay placement remained unreliable across real render/cache paths.

**Conclusion:** stop composite X/Y tuning. Not production.

## 0.6.5.x native-cell / mapping pivot

### 0.6.5.0 UNIFIED NATIVE-CELL VIETNAMESE
Runtime showed repeated A-like glyphs + unrelated Kanji.

**MAPPING ASSUMPTION FAIL:** consecutive CP932 codes do not map linearly to atlas slots.

### 0.6.5.1 POST-LOOKUP CUSTOM BANK
**BUILD-TIME FAIL ONLY.** Bad zero-filled-region assumption. No runtime conclusion.

### 0.6.5.2 ATLAS-BACKED CUSTOM BANK
**UNSAFE FAIL. NEVER RETEST.**

- black screen;
- Game FPS 0;
- hard freeze.

Reject runtime post-lookup pointer redirect.

### Font Mapping Scanner 0.1
Found `GP0=0` in EXE header. Final GP is initialized later.

### Font Mapping Initializer Scanner 0.2 — OWNERSHIP PROVEN

```text
runtime GP = 0x80085F28
atlas global = gp+0x518
map global   = gp+0x51C
```

Initializer `0x8003DD48..0x8003DD5C` writes:

```text
atlas   = 0x8006BCEC
mapping = 0x8007AECC
```

Known mapping samples all matched.

**Gate opened:** static mapping/data-only proof allowed.

### 0.6.5.3 MAPPING-ONLY NATIVE-CELL

Runtime: **STRUCTURAL PASS / GLYPH-GENERATOR FAIL.**

Passed:
- boot stable;
- mapping-controlled slots reached;
- no hook/pointer redirect required;
- no global corruption.

Generator bugs:
- hardcoded palette index 7 produced dark/shadow strokes;
- accented E/O Unicode labels fell back to A.

**Do not retest 0.6.5.3.**

### 0.6.5.4 NATIVE-BASE STYLE

Runtime: **PIPELINE PASS / VERTICAL CROWDING.**

- byte-for-byte native A/E/O controls looked correct;
- mapping and slot ownership remained correct;
- Vietnamese marks were present;
- full-height native bases left too little headroom.

### 0.6.5.5 ACCENT-SAFE COMPACT

Runtime screenshot: **VISUAL PASS ENOUGH TO LEAVE GLYPH-BOARD PHASE.**

- A/E/O native controls remain correct;
- compacted accented variants are readable;
- circumflex/acute/hook/tilde marks are distinguishable;
- no freeze/global corruption;
- remaining roughness is normal 12x12 pixel-art polish, not architecture.

**Decision:** lock mapping-only + native 12x12 as production direction. Stop spending runtime tests on the 12-glyph board.

## CURRENT — 0.6.6.0 PRODUCTION ENCODER REAL-TEXT PROOF

Purpose: first end-to-end proof using an actual Vietnamese UI phrase instead of a glyph board.

Expected Character Select text:

```text
Chọn tướng
```

Architecture:

```text
plain ASCII letters/space
  -> Gaia native full-width CP932 codes/glyphs

Vietnamese-specific chars (ọ, ư, ớ)
  -> builder-selected zero-static-hit CP932 codes
  -> builder-selected zero-static-hit atlas slots
  -> compact native-derived 12x12 glyphs
```

Builder safety:
- CLEAN BIN SHA1 enforced;
- scans PRGPACK + executable data for zero-hit custom codes;
- chooses atlas slots whose mapped source codes have zero static text hits;
- patches mapping data + glyph cells only;
- no code hook;
- no pointer redirect;
- no 12x16;
- no composite overlay;
- 24-byte Character Select field is terminated/padded explicitly.

Package:

```text
GaiaMaster_0.6.6.0_PRODUCTION_ENCODER_REAL_TEXT_PROOF.zip
```

Status: **READY FOR ONE RUNTIME TEST.**

If wrong, collect:

```text
screenshot
[VI 0.6.6.0 PROD ENCODER].txt
```

## Current do-not-repeat

- no Krom path;
- no production 12x16;
- no failed 0.6.3.x retests;
- no composite X/Y tuning loop;
- no 0.6.5.2 runtime redirect;
- no assumption consecutive code == consecutive atlas slot;
- no 0.6.5.3 retest;
- no more 12-glyph style-board runtime loops unless a production glyph regression demands it;
- stop immediately on freeze/global corruption.

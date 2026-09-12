# Gaia Master — probe/build index

Updated: **2026-09-12**

Purpose: prevent checkpoint confusion and accidental retesting of obsolete/unsafe probes.

## Stable baselines

```text
Clean Japan BIN SHA1
f4d5298583c90d89c4b7e51d2dde160ee07f2aec

Alpha 0.6.1 FRONT SHA1
54d2fb026bc3b71c79861e723caffb4114caa34c
```

## 0.6.2.x

### 0.6.2.13 STATIC SLOT / NO HOOK
Status: **BREAKTHROUGH PASS**.
Direct static-atlas replacement works at runtime while other text stays normal.

### 0.6.2.14..0.6.2.20
Status: geometry/cosmetic experiments.
Production conclusion: native 12x12 is too cramped for stacked Vietnamese diacritics.

## 0.6.3.x — extended-height path

### 0.6.3.0 EXTENDED HEIGHT 12x16
Status: **STRUCTURAL PASS**.
Do not retest.

### 0.6.3.1 BASELINE + 16-ROW STRIDE
Status: **UNSAFE FAIL**.
Global text corruption + later freeze. Never retest.

### 0.6.3.2 BASELINE ONLY
Status: **STABLE PASS WITH LOWER-ROW LOSS**.
Do not retest.

### 0.6.3.3 EOL OVERWRITE TEST
Status: **RUNTIME COMPLETE — overwrite disproven**.
Do not retest.

### 0.6.3.4 UV WINDOW TEST
Status: **RUNTIME COMPLETE — negative diagnostic**.
Do not retest.

### 0.6.3.5 POST-COPY RAM SENTINEL
Status: **RUNTIME COMPLETE — SENTINEL NOT OBSERVED**.
Late `s0` identity unreliable. Do not retest.

### 0.6.3.6 EARLY-FLAG POST-COPY SENTINEL
Status: **UNSAFE FAIL — BOOT FREEZE**.

Repeated runtime:

```text
Sony logo appears
-> immediate freeze
-> Character Select never reached
```

Never retest.
Do not use persistent/global cave flag to carry target identity.

Dedicated note:

```text
FONT_ISOLATION_0.6.3.6_UNSAFE_FAIL.md
```

### 0.6.3.7 SOURCE ROW SENTINEL
Status: **BUILT / awaiting runtime result**.

Package:

```text
GaiaMaster_FontIsolation_0.6.3.7_SOURCE_ROW_SENTINEL.zip
```

Launcher:

```text
00_RUN_PROBE_0637.cmd
```

No post-copy hook and no target flag.
Diagnostic is baked directly into the unique 12x16 source glyph:

```text
source rows 10..11 = dark/gray full band
source rows 12..15 = bright white full band
```

Interpretation:

- gray + white visible => rows12..15 survive source->display;
- gray visible, white absent => structural lower-row truncation confirmed;
- neither visible => source/slot/copy-path assumption needs further reverse.

## Current do-not-repeat list

- no Krom path;
- no production 12x12 stacked-accent polishing;
- no retest 0.6.2.18;
- no retest any 0.6.3.0..0.6.3.6 build;
- no shared `0x8003CD94..0x8003CDB4` rewrite;
- no persistent early FLAG like 0.6.3.6.

## Current next action

Runtime-test **0.6.3.7 SOURCE ROW SENTINEL** at Character Select only.

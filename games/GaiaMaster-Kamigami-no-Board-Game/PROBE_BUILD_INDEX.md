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
12x16 target source and 16-row path visibly work. Do not retest.

### 0.6.3.1 BASELINE + 16-ROW STRIDE
Status: **UNSAFE FAIL**.
Global text corruption + later freeze. Never retest.

### 0.6.3.2 BASELINE ONLY
Status: **STABLE PASS WITH LOWER-ROW LOSS**.
Japanese stable, target baseline improved, lower extended rows missing. Do not retest.

### 0.6.3.3 EOL OVERWRITE TEST
Status: **RUNTIME COMPLETE — overwrite disproven**.
Target still truncated at end-of-line. Do not retest.

### 0.6.3.4 UV WINDOW TEST
Status: **RUNTIME COMPLETE — negative diagnostic**.
`V+4` does not restore lower E cleanly. Do not retest.

### 0.6.3.5 POST-COPY RAM SENTINEL
Status: **RUNTIME COMPLETE — SENTINEL NOT OBSERVED**.
Late `s0` identity is unreliable; no clipping conclusion. Do not retest.

### 0.6.3.6 EARLY-FLAG POST-COPY SENTINEL
Status: **UNSAFE FAIL — BOOT FREEZE**.

Runtime:

```text
Sony logo appears
-> immediate freeze
-> Character Select never reached
```

Repeated test gives the same result.

New strategy that caused the regression:

```text
early metadata stage sets persistent FLAG
late post-copy hook reads FLAG
```

No sentinel conclusion is valid because the game never reaches the probe.

Never retest.

Dedicated note:

```text
FONT_ISOLATION_0.6.3.6_UNSAFE_FAIL.md
```

## Current do-not-repeat list

- no Krom path;
- no production 12x12 stacked-accent polishing;
- no retest 0.6.2.18;
- no retest any 0.6.3.0..0.6.3.6 build;
- no shared `0x8003CD94..0x8003CDB4` rewrite;
- no persistent early FLAG like 0.6.3.6.

## Current next action

**Reverse before building.**

Inspect the live arguments/registers around the call to `0x8003C67C` and identify the extended target using its unique source glyph pointer or existing metadata state.

Next probe must:

- avoid late `s0`;
- avoid persistent/global flags;
- avoid shared allocator mutation;
- identify target locally from source pointer / metadata pointer;
- answer only whether converted rows 12..15 exist after the copy routine.

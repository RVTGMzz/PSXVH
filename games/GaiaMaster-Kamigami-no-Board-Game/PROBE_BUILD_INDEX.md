# Gaia Master — probe/build index

Updated: **2026-09-12**

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
**BREAKTHROUGH PASS**. Static custom Vietnamese atlas path works.

### 0.6.2.14..0.6.2.20
Geometry/cosmetic experiments. Production conclusion: native 12x12 is too cramped for stacked Vietnamese diacritics.

## 0.6.3.x extended-height

### 0.6.3.0 EXTENDED HEIGHT 12x16
**STRUCTURAL EVIDENCE / historical pass classification.** Do not retest. Later visible-height probes show that some interpretation of the late display path must be revisited.

### 0.6.3.1 BASELINE + 16-ROW STRIDE
**UNSAFE FAIL**. Global corruption + later freeze. Never retest.

### 0.6.3.2 BASELINE ONLY
**STABLE PASS WITH LOWER-ROW LOSS**. Do not retest.

### 0.6.3.3 EOL OVERWRITE
**RUNTIME COMPLETE**. Following-glyph overwrite disproven. Do not retest.

### 0.6.3.4 UV WINDOW
**RUNTIME COMPLETE / NEGATIVE**. V+4 does not restore lower rows. Do not retest.

### 0.6.3.5 POST-COPY RAM SENTINEL
**RUNTIME COMPLETE / NO SENTINEL**. Late `s0` identity unreliable. Do not retest.

### 0.6.3.6 EARLY-FLAG POST-COPY SENTINEL
**UNSAFE FAIL / BOOT FREEZE**. Persistent/global flag strategy rejected. Never retest.

### 0.6.3.7 SOURCE ROW SENTINEL
**RUNTIME COMPLETE / HIGH-VALUE RESULT**.

Source target contains:

```text
rows10..11 dark/gray full band
rows12..15 bright white full band
```

Runtime:
- Japanese/TEST normal;
- dark rows10..11 visible;
- rows12..15 do not appear as thick white 4-row block;
- only thin bright edge remains.

=> lower four source rows are not fully visible.

### 0.6.3.8 FORCE SPRITE HEIGHT16
**DIAGNOSTIC FAIL**.

Global force-height16 causes blank textbox / vertical TEST layout. `0x8003CCC0` path is not a simple safe global visible-height override. Do not retest.

### 0.6.3.9 HEIGHT FROM METADATA
**DIAGNOSTIC FAIL / RUNTIME COMPLETE**.

Probe replaced the load at `0x8003CCC0` with:

```text
lhu v0,2(s3)
```

assuming `s3+2` still held current glyph `height_minus_1`.

Runtime:
- TEST stacks vertically;
- target becomes noisy/garbled texture block;
- normal layout does not return;
- lower source white block is not recovered.

Conclusion:

```text
s3 at 0x8003CCC0 is NOT proven to be the original glyph metadata pointer
```

Do not retest and do not derive another height patch from `s3+2` without register/dataflow proof.

## CURRENT STATUS

**NO CURRENT USER PROBE.**

Reverse-only phase before 0.6.3.10.

Required reverse target:

```text
0x8003CCA0 .. 0x8003CD20
```

Questions to answer before another build:

1. lifetime/meaning of `s1`, `s2`, `s3` at this stage;
2. exact semantic meaning of `lbu 64(s1)` at `0x8003CCC0`;
3. exact store/consumer of the value after `0x8003CCC8 addiu`;
4. distinguish glyph visible texture height from advance/layout/line metric;
5. locate the true per-current-glyph draw height field by dataflow, not register-name assumption.

## Current do-not-repeat

- no Krom path;
- no production 12x12 stacked-accent polishing;
- no retest 0.6.2.18;
- no retest 0.6.3.0..0.6.3.9;
- no shared `0x8003CD94..0x8003CDB4` rewrite;
- no persistent/global flag;
- no global force-height16;
- no `s3+2` metadata assumption at `0x8003CCC0` without proof.

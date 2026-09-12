# Gaia Master — probe/build index

Updated: **2026-09-12**

This index exists to prevent checkpoint confusion and accidental retesting of obsolete/unsafe probes.

## Stable baselines

```text
Clean Japan BIN SHA1
f4d5298583c90d89c4b7e51d2dde160ee07f2aec

Alpha 0.6.1 FRONT SHA1
54d2fb026bc3b71c79861e723caffb4114caa34c
```

## 0.6.2.x — native 12x12 custom atlas reverse

### 0.6.2.7 CUSTOM ATLAS
Status: diagnostic breakthrough, but control used ASCII and produced repeated accented glyph behavior.

### 0.6.2.8 TARGETED HOOK
Status: not final; hook/control assumptions still wrong.

### 0.6.2.9 FULLWIDTH CONTROL
Status: builder bug (`S0` undefined), superseded.

### 0.6.2.10 STYLE MATCH
Status: unsafe mapping-stage hook; global text collapsed/repeated. Do not retest.

### 0.6.2.11 POST-LOOKUP
Runtime: `ＴＥＳＴ?`.
Status: target isolation useful, custom cave glyph path still wrong.

### 0.6.2.12 CORRECT PACKING
Runtime still `ＴＥＳＴ?`.
Status: superseded.

### 0.6.2.13 STATIC SLOT / NO HOOK
Status: **BREAKTHROUGH PASS**.

Direct static atlas replacement works at runtime while other text stays normal.

### 0.6.2.14 COMPACT FIT
Status: cosmetic test; compact body not acceptable.

### 0.6.2.15 ACCENT SHAPE
Status: cosmetic test; still not production quality.

### 0.6.2.16 FULL HEIGHT
Status: keeps native base body, accent geometry weak.

### 0.6.2.17 FULL HEIGHT AA ACCENT
Status: accent closer but blotchy/dark.

### 0.6.2.18 CLEAN ACCENT
Status: already runtime-tested. Do not retest.

### 0.6.2.19 VARIANT GRID
Status: six Ế variants shown together.
User preferred **sample 2 from the left** as base geometry.

### 0.6.2.20 SAMPLE2 REFINED
Status: revealed structural 12x12 limitation.

Production conclusion:

```text
native 12x12 is too cramped for stacked Vietnamese diacritics
```

Do not return to endless 12x12 accent polishing.

## 0.6.3.x — extended-height path

### 0.6.3.0 EXTENDED HEIGHT 12x16
Package:

```text
GaiaMaster_FontIsolation_0.6.3.0_EXTENDED_HEIGHT_12x16.zip
```

Initially misclassified as fail; later pixel-level review reclassified it as:

**STRUCTURAL PASS**

Reason:

- extra rows/headroom are visible;
- target footprint is taller;
- E body is lower exactly because baseline correction was intentionally absent.

Do not retest.

### 0.6.3.1 BASELINE + 16-ROW STRIDE
Package:

```text
GaiaMaster_FontIsolation_0.6.3.1_BASELINE_STRIDE.zip
```

Status: **UNSAFE FAIL**.

Runtime:

- unrelated Japanese text corrupts/repeats;
- Character Select corrupts;
- later screen garbles;
- game freezes.

Likely regression source:

```text
shared cache/VRAM advance rewrite around 0x8003CD94..0x8003CDB4
```

Never retest.

### 0.6.3.2 BASELINE ONLY
Package:

```text
GaiaMaster_FontIsolation_0.6.3.2_BASELINE_ONLY.zip
```

Status: **STABLE PASS WITH LOWER-ROW LOSS**.

Control:

```text
ＴＥＳＴ亜Ａ
```

Runtime:

- header normal;
- TEST normal;
- target baseline improved;
- A sentinel intact;
- no global corruption/freeze;
- target lower rows missing/cut.

Strong hypothesis:

```text
16-row target writes 128 converted bytes
native cursor advances only 96 bytes
following glyph may overwrite last 32 bytes / 4 rows
```

Dedicated note:

```text
FONT_ISOLATION_0.6.3.2_STABLE_PASS.md
```

### 0.6.3.3 EOL OVERWRITE TEST
Package:

```text
GaiaMaster_FontIsolation_0.6.3.3_EOL_OVERWRITE_TEST.zip
```

Status: **BUILT / awaiting runtime result**.

Control:

```text
ＴＥＳＴ亜
```

Only change from 0.6.3.2: remove trailing glyph so nothing can overwrite target bottom.

Question:

```text
Does target bottom return at end-of-line?
```

Dedicated note:

```text
FONT_ISOLATION_0.6.3.3_EOL_OVERWRITE_TEST.md
```

## Current do-not-repeat list

- do not return to Krom path for Character Select;
- do not retest 0.6.2.18;
- do not retest 0.6.3.0;
- never retest unsafe 0.6.3.1;
- do not globally/naively rewrite `0x8003CD94..0x8003CDB4` again;
- do not resume production 12x12 stacked-diacritic polishing.

## Current next action

Runtime-test **0.6.3.3 EOL OVERWRITE TEST**.

After result:

- if bottom returns, reverse/design isolated extended cache destination;
- if bottom remains cut, reverse target copy/upload/primitive clipping path further.

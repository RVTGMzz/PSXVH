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

## 0.6.2.x — native 12x12 custom atlas reverse

### 0.6.2.13 STATIC SLOT / NO HOOK
Status: **BREAKTHROUGH PASS**.
Direct static-atlas replacement works at runtime while other text stays normal.

### 0.6.2.14..0.6.2.20
Status: cosmetic/geometry experiments.
Production conclusion:

```text
native 12x12 is too cramped for stacked Vietnamese diacritics
```

Do not return to endless 12x12 accent polishing.

## 0.6.3.x — extended-height path

### 0.6.3.0 EXTENDED HEIGHT 12x16
Status: **STRUCTURAL PASS**.

- 12x16 / 96-byte target source;
- target copy path can run 16 rows;
- taller target footprint observed;
- baseline intentionally not fixed in first probe.

Do not retest.

### 0.6.3.1 BASELINE + 16-ROW STRIDE
Status: **UNSAFE FAIL**.

Runtime:
- unrelated Japanese corrupts/repeats;
- Character Select corrupts;
- later screen garbles;
- game freezes.

Likely regression source:

```text
shared cache/VRAM advance rewrite around 0x8003CD94..0x8003CDB4
```

Never retest.

### 0.6.3.2 BASELINE ONLY
Status: **STABLE PASS WITH LOWER-ROW LOSS**.

Control:

```text
ＴＥＳＴ亜Ａ
```

Runtime stable, baseline improved, A sentinel intact, lower target rows missing.

Do not retest.

### 0.6.3.3 EOL OVERWRITE TEST
Status: **RUNTIME COMPLETE — overwrite hypothesis disproven**.

Control:

```text
ＴＥＳＴ亜
```

Same lower-row loss despite no following glyph.

Do not retest.

### 0.6.3.4 UV WINDOW TEST
Status: **RUNTIME COMPLETE — negative diagnostic**.

Only change:

```text
target texture V += 4
```

Result:
- Japanese/TEST stable;
- target still malformed/truncated;
- lower native E not restored cleanly;
- no global corruption/freeze.

=> simple UV offset insufficient.

Do not retest.

### 0.6.3.5 POST-COPY RAM SENTINEL
Status: **RUNTIME COMPLETE — SENTINEL NOT OBSERVED**.

Intended post-copy pattern:

```text
rows 10..11 = dark/gray band
rows 12..15 = bright white band
```

Runtime:
- Japanese/TEST stable;
- target looks like prior truncated glyph;
- neither obvious band visible.

Conclusion:

```text
late s0 target check at 0x8003CC4C is unreliable
```

Do not infer clipping from this build and do not retest.

Dedicated note:

```text
FONT_ISOLATION_0.6.3.5_POST_COPY_RAM_SENTINEL.md
```

### 0.6.3.6 EARLY-FLAG POST-COPY SENTINEL
Status: **BUILT / awaiting runtime result**.

Package:

```text
GaiaMaster_FontIsolation_0.6.3.6_EARLY_FLAG_POST_COPY_SENTINEL.zip
```

Launcher:

```text
00_RUN_PROBE_0636.cmd
```

Key change:

At early metadata stage where `s0` is proven trustworthy:

```text
target 0x889F -> FLAG=1
other glyph    -> FLAG=0
```

Late post-copy hook reads FLAG only, never `s0`.

Sentinel pattern is unchanged:

```text
rows 10..11 = gray/dark control
rows 12..15 = bright white test
```

Interpretation:
- gray + white => rows12..15 survive RAM->VRAM->sprite;
- gray only => rows12..15 lost after converted RAM;
- neither => assumed post-copy destination/path wrong.

## Current do-not-repeat list

- do not return to Krom path;
- do not retest 0.6.2.18;
- do not retest 0.6.3.0;
- never retest unsafe 0.6.3.1;
- do not retest 0.6.3.2 / 0.6.3.3 / 0.6.3.4 / 0.6.3.5;
- do not naively rewrite shared `0x8003CD94..0x8003CDB4`;
- do not resume production 12x12 stacked-diacritic polishing.

## Current next action

Runtime-test **0.6.3.6 EARLY-FLAG POST-COPY SENTINEL** at Character Select only.

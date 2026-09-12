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
- target copy path can be driven at 16 rows;
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

Strongest regression source:

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

Result remains essentially same as 0.6.3.2 despite no following glyph.

=> following-glyph overwrite is false.

Do not retest.

### 0.6.3.4 UV WINDOW TEST
Status: **RUNTIME COMPLETE — negative diagnostic**.

Only new change:

```text
target texture V += 4
```

Result:

- surrounding Japanese/TEST stable;
- target still malformed/truncated;
- lower native E not restored cleanly;
- no global corruption/freeze.

=> simple UV/window offset is insufficient.

Do not retest.

### Reverse after 0.6.3.4

Wide copy:

```text
0x8003C67C
6 source bytes/row -> 8 converted bytes/row
```

Font cache/upload page is not 12 rows tall.
Default cache page setup is roughly:

```text
width 32
height 240
VRAM Y 256
```

Final flush uploads the cache page, so missing rows are not explained by upload RECT height being 12.

### 0.6.3.5 POST-COPY RAM SENTINEL
Status: **BUILT / awaiting runtime result**.

Package:

```text
GaiaMaster_FontIsolation_0.6.3.5_POST_COPY_RAM_SENTINEL.zip
```

Control remains:

```text
ＴＥＳＴ亜
```

After successful copy, target only:

```text
rows 10..11 = dark/gray full band  # control
rows 12..15 = bright white full band  # test
```

Interpretation:

- both bands visible => rows12..15 survive RAM->VRAM->sprite;
- control visible but bottom white absent => loss after converted RAM row11;
- neither band => hook/path issue, no clipping conclusion.

## Current do-not-repeat list

- do not return to Krom path;
- do not retest 0.6.2.18;
- do not retest 0.6.3.0;
- never retest unsafe 0.6.3.1;
- do not retest 0.6.3.2 / 0.6.3.3 / 0.6.3.4;
- do not naively rewrite shared `0x8003CD94..0x8003CDB4`;
- do not resume production 12x12 stacked-diacritic polishing.

## Current next action

Runtime-test **0.6.3.5 POST-COPY RAM SENTINEL** at Character Select only.

# Gaia Master — 0.6.6.1 Baseline Normalization

## Runtime result from 0.6.6.0

`0.6.6.0 PRODUCTION ENCODER REAL-TEXT` successfully rendered the real Vietnamese UI phrase:

```text
Chọn tướng
```

This confirms the production encoder path works end-to-end:

```text
Vietnamese text
 -> production encoder
 -> native full-width CP932 for plain Latin
 -> custom zero-hit CP932 codes for Vietnamese-specific chars
 -> static mapping entries
 -> safe native 12x12 atlas slots
```

No hook, pointer redirect, 12x16 path, or composite overlay is required.

Observed issue: `ọ / ư / ớ` sat at noticeably different vertical positions from untouched native Latin.

## Root cause

0.6.6.0 unconditionally compressed every Vietnamese-specific base glyph into a fixed vertical band:

```text
rows 2..9
```

That was unnecessary for lowercase native `o/u`, which already contain useful headroom in the original 12x12 cell. The fixed band altered their native baseline and made the sentence look wavy.

## 0.6.6.1 rule

Preserve the native base glyph byte geometry whenever its existing bbox already leaves enough room for required marks.

Only if a mark truly needs unavailable space:
- fit/shift the body minimally;
- preserve the original bottom/baseline as much as possible;
- reserve only the rows actually required by top or bottom marks.

Examples:
- `ư`, `ớ`: keep the native `u` baseline whenever possible;
- `ọ`: keep native `o` if there is a free row below, otherwise move/fit only enough to place the dot-below.

The builder report now records:

```text
src_bbox
body_bbox
final_bbox
fit_mode = native-preserved | minimal-fit
```

This turns further visual tuning into deterministic bbox work rather than screenshot guessing.

## Status

`0.6.6.0`: **REAL-TEXT ENCODER PASS / BASELINE POLISH NEEDED**

`0.6.6.1`: **READY FOR ONE RUNTIME TEST**

Expected Character Select text remains:

```text
Chọn tướng
```

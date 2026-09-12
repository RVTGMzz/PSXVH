# Gaia Master — Font Isolation 0.6.2.14 COMPACT FIT

## Status entering this build

0.6.2.13 STATIC SLOT / NO HOOK produced a near-correct Vietnamese `Ế` in Character Select.

Runtime screenshot/user result:

- other text normal;
- `ＴＥＳＴ` normal;
- final glyph visually close to `Ế`;
- native color/style substantially improved;
- top mark is clipped/touches the top boundary.

Therefore custom Vietnamese glyph rendering is considered **pipeline PASS**. 0.6.2.14 is a glyph-fit test, not another renderer reverse test.

## Strategy

Keep the exact successful 0.6.2.13 path:

- no Krom hook;
- no renderer hook;
- no code cave;
- no mapping-table edit;
- visible probe remains `ＴＥＳＴ亜`;
- replace static atlas glyph #0 (`亜`) directly.

Font source:

```text
atlas: SLPS + 0x5C4EC
format: 12x12 / 4bpp / 72 bytes per glyph
packing used by current builder: LOW nibble first
source style glyph: full-width Ｅ, index 466
```

## Compact Ế layout

The native full-width E uses rows 2..11, leaving only two blank top rows. That is too tight for circumflex + acute without touching the ceiling.

0.6.2.14 uses:

```text
row 0      blank safety headroom
row 1      acute
row 2      circumflex
rows 3-11 compact native E body
```

The original E body is 10 rows. Two upper vertical-stem rows are duplicates, so one duplicate is removed. The 9 remaining body rows are copied directly from the native E glyph, preserving the game's palette/shadow/edge style rather than redrawing the Latin body.

Source-row mapping for body:

```text
native E rows: 2,3,4,6,7,8,9,10,11
probe rows:    3,4,5,6,7,8,9,10,11
```

## Expected runtime

```text
ＴＥＳＴẾ
```

Acceptance criteria:

1. both circumflex and acute are visible;
2. no top clipping;
3. E body remains recognizably native style/color;
4. other text remains normal.

If accepted, end single-glyph diagnostics and move directly to full Vietnamese glyph inventory + compact codepage/encoder.

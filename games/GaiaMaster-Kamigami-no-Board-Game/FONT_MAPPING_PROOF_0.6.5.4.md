# Gaia Master — 0.6.5.4 NATIVE-BASE STYLE PROOF

Date: 2026-09-13

## Why 0.6.5.4 exists

Runtime test of 0.6.5.3 was a structural success but an artwork/generator failure.

Observed on Character Select:
- mapping-only path booted and rendered safely;
- the test line was routed through the chosen custom slots;
- glyphs looked like dark/shadow-only strokes;
- accented E/O-family glyphs looked A-like.

## Root causes found in 0.6.5.3 builder

### 1. Hardcoded palette index

All custom pixels were drawn with palette index `7`.

That was an unjustified assumption about Gaia's native 4bpp font style and likely explains the dark/shadow-like appearance.

### 2. Unicode family-selection bug

0.6.5.3 used:

```python
base = label[0] if label[0] in "AEO" else "A"
```

This works for plain `A/E/O`, but not for Unicode accented letters such as `Ê`, `Ế`, `Ô`, `Ố`.
Those labels therefore fell through to the `A` base.

This exactly explains why the runtime screenshot showed A-like bodies where E/O accented glyphs were expected.

## 0.6.5.4 design

Keep the proven architecture unchanged:

```text
text code
  -> patched static mapping entry
  -> selected atlas slot
  -> native 12x12 / 72-byte / 4bpp glyph
```

No code hook.
No runtime pointer redirect.
No 12x16.
No composite overlay.

Changes are limited to glyph generation:

1. Read Gaia's own full-width `Ａ`, `Ｅ`, `Ｏ` through the proven mapping table.
2. Copy those native glyphs as base shapes.
3. Plain A/E/O are byte-for-byte native controls.
4. Use explicit A/E/O family tables for accented letters.
5. Derive accent color from each native base glyph's dominant non-zero palette index instead of hardcoding `7`.
6. Add compact marks inside the same native 12x12 cell.

## Expected Character Select line

```text
A Â Ấ Ẳ E Ê Ế Ể O Ô Ố Ỗ
```

## Interpretation

If plain A/E/O now look exactly like normal game text:
- static mapping ownership is confirmed in runtime;
- selected atlas slots are confirmed;
- native 12x12 glyph replacement is confirmed;
- remaining work is only Vietnamese accent artwork/layout inside 12x12.

If accented families now keep the correct A/E/O bodies, the Unicode family bug is fixed.

Status: **READY FOR ONE RUNTIME TEST.**

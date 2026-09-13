# Gaia Master — 0.6.5.5 ACCENT-SAFE COMPACT NATIVE STYLE

## Why this build exists

0.6.5.4 established that mapping, destination slots, and byte-for-byte native A/E/O glyph copying are working. Runtime showed the remaining problem is visual composition inside the fixed native 12x12 cell: Vietnamese marks were present but crowded into the top of full-height native letters.

## Design

Keep the proven production direction:

```text
text code -> mapping entry -> chosen atlas slot -> native 12x12 / 72-byte / 4bpp glyph
```

No renderer hook. No pointer redirect. No 12x16. No composite overlay.

For the Character Select proof:

```text
A Â Ấ Ẳ E Ê Ế Ể O Ô Ố Ỗ
```

- plain A/E/O remain byte-for-byte native controls;
- accented variants derive from the native A/E/O source glyphs;
- accented body is vertically compacted into rows 3..11;
- rows 0..2 are reserved for Vietnamese marks;
- marks use two native palette layers: fill + shadow;
- palette index 7 is explicitly treated as the dark/shadow layer because 0.6.5.3 runtime showed hardcoded index 7 rendered as dark/shadow.

## Test target

Build with:

```text
00_BUILD_0.6.5.5_ACCENT_SAFE.cmd
```

Boot generated:

```text
[VI 0.6.5.5 ACCENT SAFE].cue
```

Judge only the Character Select test line. Expected order:

```text
A Â Ấ Ẳ E Ê Ế Ể O Ô Ố Ỗ
```

If visual result is still wrong, send both screenshot and generated build report:

```text
[VI 0.6.5.5 ACCENT SAFE].txt
```

The report records native source bbox, palette histogram, chosen fill/shadow indices, destination slots, and compacted glyph bbox.

# Gaia Master — Font Spacing Scanner 0.1

Status: **READ-ONLY / NO ROM PATCH / NO EMULATOR BOOT**

## Why this scanner exists

`0.6.6.1 BASELINE-NORMALIZED REAL-TEXT` is visually good enough to mark the Vietnamese glyph/encoder path as PASS. The remaining visible issue is horizontal spacing: Gaia still advances Latin-looking glyphs with a wide Japanese-style cell.

Static reverse already proves the renderer has a cached per-glyph advance value rather than a single hardcoded X step.

### Cache hit

The cache record is 16 bytes. `record+6` is loaded and added to `state+24` (cursor X). If the advance differs from `state+62`, `state+60` is added as extra tracking.

### Cache miss

The native miss path computes advance as:

```text
copy_return == 8 ? state+62 : state+64 + 1
```

Then, when the computed advance differs from `state+62`, it adds `state+60`.

This strongly suggests Gaia already owns font metrics / spacing state that may allow a cleaner native or per-renderer solution.

## Gate

Do **not** build a runtime spacing patch yet.

We first need ownership/value sources for:

```text
state+0x3C = state+60 = extra tracking
state+0x3E = state+62 = special/small advance
state+0x40 = state+64 = native dimension used by normal advance
```

The old 0.6.3 reverse dump ends before the full constructor path is visible, so this scanner searches the entire SLPS executable.

## Files

```text
tools/font_spacing_scanner_0.1.py
tools/00_RUN_FONT_SPACING_SCANNER_0.1.cmd
```

Expected report:

```text
GaiaMaster_FontSpacingScanner_01.txt
```

## Scanner output

- every direct READ/WRITE xref to `+0x3C`, `+0x3E`, `+0x40`;
- cache-field writes around `+0x54/+0x58/+0x5C/+0x60/+0x64/+0x6C`;
- cache-hit and cache-miss advance neighborhoods;
- renderer/cache init neighborhood `0x8003D380..0x8003D780`;
- direct JAL callers into that init range.

## Next decision

If spacing metrics are constructor/config data, prefer a local/native spacing path or data-side metric change. Do not modify global cursor advance unless the scanner proves that is the only safe route.

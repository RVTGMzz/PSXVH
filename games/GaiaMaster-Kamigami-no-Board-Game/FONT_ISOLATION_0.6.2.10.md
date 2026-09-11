# Gaia Master — Font Isolation 0.6.2.10 STYLE MATCH

## Context

0.6.2.7 and 0.6.2.8 proved that the Character Select custom-atlas path is real, but the visible probe showed the same injected glyph for all five characters and the injected glyph color/style looked darker than the game's normal font.

0.6.2.9 attempted to fix the mapping/control path but had a builder bug: `S0` was referenced without being defined in Python, causing a `NameError` before any ROM patch occurred.

## Reverse facts now locked

- Character Select text: `PRGPACK.BDP + 0xBFD2C`
- owner nested entry: 29
- custom atlas: `SLPS_020.75 + 0x5C4EC`
- atlas glyph count: 860
- glyph format: 12x12, 4bpp, 72 bytes/glyph, low nibble first
- mapping table: `SLPS_020.75 + 0x6B6CC`
- `0x889F = 亜` maps to glyph index 0 in the static table
- full-width `Ｅ` maps to glyph index 466
- renderer custom-atlas branch: `VA 0x8003C4DC` / SLPS file `+0x2CCDC`
- safe cave: `SLPS +0x5C0E0`, VA `0x8006B8E0`

## 0.6.2.10 fixes

### Correct register

`S0` is explicitly defined as MIPS register 16.

The renderer function entry copies `a1 -> s0`, so the hook compares the original 16-bit character input directly:

```text
s0 == 0x889F
```

### Correct control text

The probe no longer uses 1-byte ASCII. It uses known-good full-width CP932:

```text
ＴＥＳＴ亜
82 73 82 64 82 72 82 73 88 9F
```

Only the final `亜` should be intercepted.

### Exact game style/color preservation

The injected `Ế` is no longer hand-colored.

The builder reads the game's own full-width `Ｅ` glyph (atlas index 466). The original glyph has rows 0 and 1 completely blank. The builder:

1. keeps rows 2..11 exactly unchanged;
2. adds a compact circumflex + acute only into rows 0..1;
3. uses CLUT/index values already present in the original E glyph;
4. rejects the build if the original E fingerprint differs or if the E body changes.

This means the body of the Vietnamese glyph uses the exact original font palette/intensity/outline/shadow pattern.

## Expected runtime result

```text
ＴＥＳＴẾ
```

Expected details:

- the four full-width TEST glyphs remain normal;
- only the final `亜` becomes `Ế`;
- the body of `Ế` should visually match the game's original full-width `Ｅ` color/style.

## Offline verification before user test

The 0.6.2.10 builder was unit-tested directly against the Stage 2 extracted `SLPS_020.75` and `PRGPACK.BDP`:

- `S0 = 16`: PASS
- renderer hook write: PASS
- Character Select owner entry 29: PASS
- probe bytes: PASS
- nested BDP checksum: PASS
- top-level BDP checksum: PASS
- style check: rows 2..11 of custom glyph exactly equal original E: PASS
- safe cave baseline: PASS

Next action: runtime test only. If `ＴＥＳＴẾ` appears with matched color/style, stop single-glyph diagnostics and move directly to the full Vietnamese glyph/codepage implementation.

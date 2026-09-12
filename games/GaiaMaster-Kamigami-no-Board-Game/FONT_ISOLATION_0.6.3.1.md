# Gaia Master — Font Isolation 0.6.3.1 BASELINE + 16-ROW STRIDE

## Why this probe exists

0.6.3.0 was initially misclassified as a structural failure. Pixel-level review shows that it actually displayed the expected extended vertical footprint: extra headroom plus a complete E body shifted downward because baseline correction had intentionally not been implemented.

Therefore 0.6.3.1 does **not** ask whether 12x16 works anymore. It asks the next production question:

> Can a 16-row Vietnamese target align to the native baseline and coexist safely with a following native glyph without cache overlap?

## Reverse facts used

### 16-row copy path

`0x8003C67C` reads glyph metadata height `+2` and for wide glyphs converts each row as:

```text
6 source bytes -> 8 destination bytes
```

Footprints:

```text
12 rows -> 96 bytes
16 rows -> 128 bytes
```

### Native post-copy stride that must be corrected

```text
0x8003CD94..0x8003CDA4
    CPU converted-glyph pointer advance

0x8003CDA8..0x8003CDB4
    VRAM glyph Y advance
```

Native code derives both from global font height `s1+64`, which remains 12 rows for Character Select.

### Baseline

Native E visible body begins at row 2.
Extended diagnostic E body begins at row 6.

Target needs:

```text
Y -= 4
```

around descriptor Y construction at `0x8003CD08..0x8003CD10`.

## Probe design

Keep 0.6.3.0 target-only hooks for:

- source/copy height 16 rows;
- visible sprite height 16.

Add target-only hooks for:

- descriptor Y `-4 px`;
- converted cache pointer `+128 bytes`;
- VRAM Y cursor `+16 rows`.

Control string:

```text
ＴＥＳＴ亜Ａ
```

Expected runtime:

```text
ＴＥＳＴẾＡ
```

The trailing native `Ａ` is intentional. It is a stride sentinel:

- if `Ế` aligns with `TEST` and `Ａ` is intact, 16-row allocation is behaving correctly;
- if `Ａ` corrupts or overlaps the target, the allocator/VRAM stride is still incomplete.

## Scope

This is still diagnostic source storage: 96-byte target data is placed in high native atlas space for the test. Production storage will be moved to a dedicated extended Vietnamese atlas after the 16-row layout/cache path is proven stable.

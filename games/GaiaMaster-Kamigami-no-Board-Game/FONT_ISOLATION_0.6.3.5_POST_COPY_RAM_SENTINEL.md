# Gaia Master — Font Isolation 0.6.3.5 POST-COPY RAM SENTINEL

Runtime test date: **2026-09-12**
Status: **RUNTIME COMPLETE — SENTINEL NOT OBSERVED**

## Goal

Test whether converted RAM rows 12..15 survive into VRAM/sprite display by overwriting the post-copy destination with obvious horizontal sentinel bands.

Stable control:

```text
ＴＥＳＴ亜
```

Kept:

- target 12x16 / 96-byte source;
- metadata/copy height = 16 rows;
- visible sprite height = 16;
- baseline Y `-4`;
- target at end-of-line;
- no UV +4;
- no shared `0x8003CD94..0x8003CDB4` allocator/cursor rewrite.

## Diagnostic design

Hook after `0x8003C67C` at:

```text
0x8003CC4C
```

For target only, intended overwrite:

```text
rows 10..11 = dark/gray full-width band
rows 12..15 = bright white full-width band
```

0.6.3.5 identified the target at this late stage with:

```text
s0 & 0xFFFF == 0x889F
```

## Runtime result

User screenshot shows:

- Japanese header normal;
- `ＴＥＳＴ` normal;
- final target still resembles the previous truncated/malformed extended glyph;
- **no obvious dark control band**;
- **no obvious bright 4-row lower band**;
- no reported global corruption/freeze.

=> This is interpretation **C** from the probe design.

## Conclusion

0.6.3.5 did **not** successfully answer whether rows 12..15 survive the post-copy RAM -> VRAM -> sprite path.

The strongest problem is target identification at the late hook. By `0x8003CC4C`, `s0` is not proven to still contain the original Shift-JIS character code.

Therefore:

> Do not infer clipping from 0.6.3.5.

## Next probe

Use **0.6.3.6 EARLY-FLAG POST-COPY SENTINEL**.

At the early metadata stage where `s0` is already proven trustworthy:

```text
0x889F -> runtime FLAG = 1
other glyph -> FLAG = 0
```

The late post-copy sentinel hook reads only FLAG and never checks `s0`.

The same sentinel pattern is retained so the next runtime result answers the original question without changing copy/upload/sprite geometry.

Do not retest 0.6.3.5.

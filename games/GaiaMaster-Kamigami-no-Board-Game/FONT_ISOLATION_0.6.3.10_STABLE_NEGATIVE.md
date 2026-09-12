# Gaia Master — Font Isolation 0.6.3.10 HEIGHT FROM STACK METADATA — STABLE NEGATIVE

Runtime date: **2026-09-12**

## Runtime result

User reports the result looks **the same as before**.

Interpretation:

- native text/layout remains stable;
- target still resembles 0.6.3.7;
- source sentinel rows12..15 still do not appear as the intended thick 4-row bright block.

Therefore 0.6.3.10 is a **stable negative diagnostic**.

Do not retest.

## What 0.6.3.10 proved

0.6.3.9 failed because it assumed `s3` still pointed to glyph metadata at `0x8003CCC0`.
Full caller dataflow proved instead:

```text
s5 = current 16-byte output record base
s3 = s5 + 15
```

The true current glyph metadata remains at caller `sp+16`, and the true height field is:

```text
lhu 18(sp)
```

0.6.3.10 used that proven field and kept layout stable, but lower rows remained missing.

## Final draw consumer reverse

The 16-byte glyph output record is later consumed around `0x8003D9FC..0x8003DA50`.

Confirmed mapping:

```text
record+4 -> texture U
record+5 -> texture V
record+6 -> primitive width
record+7 -> primitive height
```

So the record height really does reach the final GPU primitive.

Because 0.6.3.10 still looks unchanged, **final visible sprite height is not the remaining lower-row blocker**.

## New focus

Reverse converted RAM / cache / VRAM placement.

The wide copy path for target width=12 genuinely reads 6 source bytes per row and, with height=15, writes 16 converted rows:

```text
16 * 8 = 128 converted bytes
```

Next probe: **0.6.3.11 RAM TAIL MIRROR**.

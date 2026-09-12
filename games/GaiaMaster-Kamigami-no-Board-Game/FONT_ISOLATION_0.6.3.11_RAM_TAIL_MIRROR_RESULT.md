# Gaia Master — 0.6.3.11 RAM TAIL MIRROR — runtime result

Runtime date: **2026-09-12**

## Result

Character Select remained stable:

- Japanese header normal;
- `ＴＥＳＴ` normal;
- target glyph looked essentially the same as 0.6.3.7 / 0.6.3.10;
- the expected obvious bright 4-row mirror block did **not** appear.

## Why this is not yet proof of tail loss

0.6.3.11 mirrored:

```text
converted rows12..15 dest+96..127
-> rows8..11 dest+64..95
```

but did not emit an independent visual control proving:

1. the post-copy hook fired for the target;
2. `*(s1+100)` was the current converted destination at that exact point.

Therefore no bright mirror can mean either:

- converted tail content is missing/wrong;
- or the hook/destination model was not actually acting on the displayed target.

Do not retest 0.6.3.11.

Next probe: `0.6.3.12 CONTROLLED RAM TAIL MIRROR`, which writes a visible dark control band to rows6..7 and mirrors rows12..15 into rows8..11 in the same hook.

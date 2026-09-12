# Gaia Master — Font Isolation 0.6.3.5 POST-COPY RAM SENTINEL

Prepared: **2026-09-12**
Status: **BUILT / awaiting runtime result**

## Why this probe exists

0.6.3.4 shifted target texture `V +4` but did not recover the missing lower E rows in a clean/useful way.

Further reverse shows:

- custom wide copy loop `0x8003C67C` can process 16 rows from metadata;
- each row writes 8 bytes to converted cache;
- font VRAM upload flush uses a cache page about 240 rows high, not a 12-row glyph-only RECT.

So the next precise question is:

> Do converted RAM rows 12..15 actually survive from the post-copy buffer into VRAM/sprite display?

## Stable base

Start from 0.6.3.3 behavior:

```text
ＴＥＳＴ亜
```

Keep:

- target 12x16 / 96-byte source;
- target metadata height = 16 rows;
- target visible sprite-height request = 16;
- target baseline Y `-4`;
- target at end-of-line;
- native shared cache allocator untouched;
- no `0x8003CD94..0x8003CDB4` rewrite;
- no UV +4 patch.

## New hook

Hook after successful copy at:

```text
0x8003CC4C
```

Original:

```text
lhu v0,108(s1)
```

`0x8003CC50` is NOP, so this is a clean jump-hook site.

For `s0 & 0xFFFF == 0x889F` only, use current converted destination:

```text
state+100
```

and overwrite:

```text
rows 10..11 = 0x77 nibbles across full 8-byte row
rows 12..15 = 0x11 nibbles across full 8-byte row
```

Interpretation:

### A — gray/dark control band + bright 4-row lower band both visible

Rows 12..15 survive RAM -> VRAM -> sprite.

Then the old lower-row loss came from source/copy glyph contents or target glyph construction rather than downstream clipping.

### B — gray/dark control band visible, bright lower band absent

Hook executed and rows 10..11 display, but rows 12..15 are lost after converted RAM.

Focus next on texture cache/upload/draw geometry after row 11.

### C — neither band visible

Do not infer clipping. The sentinel hook or target condition did not execute as expected.

## Safety

This probe does **not** mutate shared cache allocation/cursor state and does not repeat the unsafe 0.6.3.1 strategy.

Stop immediately on unrelated Japanese corruption or freeze.

## Package

```text
GaiaMaster_FontIsolation_0.6.3.5_POST_COPY_RAM_SENTINEL.zip
```

Launcher:

```text
00_RUN_PROBE_0635.cmd
```

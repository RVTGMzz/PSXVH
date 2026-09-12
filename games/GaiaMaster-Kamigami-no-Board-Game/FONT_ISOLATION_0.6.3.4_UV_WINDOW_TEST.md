# Gaia Master — Font Isolation 0.6.3.4 UV WINDOW TEST

Runtime test date: **2026-09-12**
Status: **NEGATIVE DIAGNOSTIC / DO NOT RETEST**

## Why this probe existed

0.6.3.3 placed the extended target at end-of-line and still showed the same lower-row loss as 0.6.3.2, disproving following-glyph overwrite.

0.6.3.4 tested whether the missing lower rows already existed in VRAM but the sprite sampled the wrong vertical texture window.

## Probe design

Start from stable 0.6.3.3:

```text
ＴＥＳＴ亜
```

Keep:

- 12x16 / 96-byte target source;
- metadata copy height = 16 rows;
- visible sprite height request = 16;
- baseline Y `-4`;
- target at end-of-line;
- native shared cache allocator untouched;
- no `CD94` rewrite.

Change only:

```text
target texture V += 4
```

Hook site:

```text
0x8003CCF0
```

## Runtime result

User screenshot shows:

- Japanese header normal;
- `ＴＥＳＴ` normal;
- target remains malformed/truncated rather than becoming a clean full lower-E view;
- no global corruption/freeze;
- shifting texture V did **not** recover the missing native E bottom in a useful/clean way.

=> A simple wrong-V/window explanation is **not sufficient**.
=> Do not repeat 0.6.3.4.

## Reverse after runtime result

### Wide copy loop is still structurally 16-row capable

Function:

```text
0x8003C67C
```

For custom wide glyphs:

```text
6 source bytes/row -> 8 converted/cache bytes/row
```

Metadata `height=15` makes the loop process 16 rows.

### VRAM upload rectangle is NOT a 12-row glyph rectangle

Font-cache initialization shows default cache page geometry:

```text
cache page width parameter  = 32
cache page height parameter = 240
VRAM base Y                 = 256
```

State setup around:

```text
0x8003D488..0x8003D5F4
```

creates:

```text
state+40 = VRAM page start Y
state+42 = state+40 + pageHeight - 1
```

Final flush around:

```text
0x8003DB78..0x8003DBE0
```

queues a RECT covering the full cache page height, not a native 12-row glyph-only upload.

Therefore the missing four rows are **not explained by RECT.h being hardcoded to 12**.

## Next diagnostic

Use **0.6.3.5 POST-COPY RAM SENTINEL**.

Immediately after `0x8003C67C` returns successfully, target `0x889F` only will overwrite converted RAM rows:

```text
rows 10..11 = palette-index-7 full band  # control
rows 12..15 = palette-index-1 full band  # test
```

This directly answers whether converted rows 12..15 survive the RAM -> VRAM -> sprite path.

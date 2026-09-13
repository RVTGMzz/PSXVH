# Gaia Master — Font Private Bank Scanner 0.1

Date: **2026-09-13**

## Why this scan exists

`0.6.6.1 BASELINE-NORMALIZED` is a runtime PASS for the real Vietnamese phrase `Chọn tướng`, but the text still looks too widely spaced because its current Latin/custom codes use the Japanese full-width renderer class.

`GaiaMaster_FontSpacingScanner_01.txt` closed the spacing-ownership gate:

- cache record size = 16 bytes;
- `record+6` is the final horizontal advance;
- cache hit reuses `record+6` directly;
- cache miss uses `copy_return == 8 ? state+0x3E : state+0x40+1`;
- renderer setup has native narrow advance `state+0x3E = 8` for the narrow class;
- Character Select tracking `state+0x3C` is zero;
- therefore the current wide spacing is caused by glyph/copy classification, not by global tracking.

## Important cache finding

The cache is not keyed by character code. The key is the glyph source returned from `0x8003C210`, effectively:

```text
cache_key = glyph_source_pointer >> 1
```

Therefore a Vietnamese code must not simply map to a native Latin slot that may already have a full-width cache record. Plain Latin characters used by Vietnamese text must also be duplicated into private native atlas slots if we want a private 8px advance without cache aliasing.

For the first phrase:

```text
Chọn tướng
```

nine distinct private display units are needed:

```text
C h ọ n SPACE t ư ớ g
```

## Preferred architecture

Keep all production geometry native:

```text
reserved zero-hit CP932 code
 -> static mapping entry
 -> private native 12x12 / 72-byte atlas slot
 -> normal 12x12 wide copy
 -> private cache key from source pointer
 -> record+6 overridden to 8px only for private-bank source keys
```

This deliberately does **not** change copy width. Trying to force the renderer's narrow copy class on a 12px-wide 4bpp glyph risks clipping bitmap data.

The desired isolation is three layers:

1. private character code;
2. private atlas glyph source;
3. private cache key/advance.

Japanese/native text outside the private atlas block must retain the original advance formula unchanged.

## Scanner 0.1

Local package:

```text
GaiaMaster_FontPrivateBankScanner_0.1.zip
```

Expected report:

```text
GaiaMaster_FontPrivateBankScanner_01.txt
```

The scanner is READ-ONLY and performs one pass over the CLEAN BIN to find:

- contiguous 9-slot atlas runs with zero static text hits;
- zero-static-hit CP932 codes for the nine private units;
- source-pointer and `source>>1` cache-key ranges for candidate banks;
- aligned executable NOP/zero runs as **code-cave candidates only**;
- the exact cache-miss advance neighborhood around `0x8003CC98`.

A NOP/zero run is **not** automatically a proven-safe code cave. Manual reverse review is still required before any runtime build.

## Current gate

No runtime `0.6.6.2` exists yet.

Only after the scanner identifies a private bank and a candidate cave is manually proven safe may we build one Character Select proof:

```text
Chọn tướng
```

with private native slots and private 8px cached advance.

## Do not regress

- no production 12x16;
- no composite overlay;
- no pointer redirect/new runtime font bank;
- no global cursor patch;
- no global spacing mutation;
- no reuse of native Latin slots for the private proof;
- stop immediately on freeze or global text corruption.

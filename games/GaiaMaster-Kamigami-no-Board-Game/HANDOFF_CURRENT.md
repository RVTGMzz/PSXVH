# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** giữ renderer/font geometry native **12x12 / 72-byte / 4bpp**. Mapping-data-only + production encoder + baseline đã runtime PASS. `0.6.6.1 BASELINE-NORMALIZED` hiện là runtime baseline tốt. Vấn đề còn lại là **horizontal advance**. FontSpacingScanner 0.1 đã chứng minh native narrow metric 8px và cache `record+6` ownership. Pure data-only spacing không đủ vì custom mapping path thuộc full-width copy class. Current step là **READ-ONLY FontPrivateBankScanner 0.1**: tìm 9 native atlas slots liên tiếp + zero-hit codes + source/cache-key range + code-cave candidate. Chưa build runtime 0.6.6.2.

## Baseline

- Game: `GaiaMaster - Kamigami no Board Game (Japan).bin`
- serial: `SLPS-02075`
- clean BIN SHA1: `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- clean SLPS SHA1: `1dfeb6b7cfda59c108dde2dc0b8abda9a40e6ae5`
- clean PRGPACK SHA1: `a9b195b8ae5d8cad7f4f755daa08337d4671632c`
- branch: `gaia-character-select-font-atlas-reverse-01`
- repo: `ronvotri/Viet-Hoa-PS1`

## Proven font / mapping facts

```text
runtime GP     = 0x80085F28
atlas global   = gp+0x518
mapping global = gp+0x51C
atlas RAM      = 0x8006BCEC
mapping RAM    = 0x8007AECC
atlas file     = SLPS + 0x5C4EC
mapping file   = SLPS + 0x6B6CC
860 glyphs
native 12x12 / 72-byte / 4bpp / LOW nibble first
```

Renderer custom mapping consumer:

```text
code & 0x7FFF
 -> mapping[index]
 -> glyph index
 -> glyph index * 72
 -> atlas base + offset
```

Known samples:

```text
0x8273 Ｔ -> glyph 481
0x8264 Ｅ -> glyph 466
0x8272 Ｓ -> glyph 480
0x889F 亜 -> glyph 0
```

Character Select proof field:

```text
PRGPACK.BDP + 0xBFD2C
owner nested BDP = entry 29
24-byte proof field
```

## Hard historical conclusions

- `0.6.2.13`: static custom-atlas replacement PASS.
- `0.6.3.x`: 12x16 touched shared renderer/cache state and produced corruption/freezes. Reverse notes may be reused, production design may not.
- `0.6.4.x`: composite overlay placement unreliable. Not production.
- `0.6.5.2`: **UNSAFE FAIL / NEVER RETEST**, runtime pointer redirect caused black screen, Game FPS 0, hard freeze.
- Mapping ownership is proven statically at `0x8003DD48..0x8003DD5C`.
- `0.6.5.3`: mapping-only structural PASS.
- `0.6.5.4`: native base glyph copy pipeline PASS.
- `0.6.5.5`: accent-safe compact glyph board good enough to pivot to real text.
- `0.6.6.0`: production encoder rendered `Chọn tướng` end-to-end.
- `0.6.6.1`: baseline-normalized real text runtime PASS.

## 0.6.6.1 runtime conclusion

`Chọn tướng` now has acceptable vertical alignment. Do not reopen glyph/baseline polishing merely because horizontal spacing is wide.

Current visible issue:

> each Latin-looking unit still occupies Japanese full-width horizontal space.

## Proven spacing/cache facts

FontSpacingScanner report closes the old ownership gate.

### Cache record

```text
record size = 16 bytes
record+6    = final horizontal advance
```

Cache hit reads `record+6` and advances cursor with it.

Cache miss around `0x8003CC98` computes:

```text
if copy_return == 8:
    advance = state+0x3E
else:
    advance = state+0x40 + 1
record.byte6 = advance
```

Tracking:

```text
if advance != state+0x3E:
    advance += state+0x3C
```

For Character Select renderer setup:

```text
state+0x3C = 0
```

Metric setter around `0x8003CED0` proves a native narrow metric:

```text
state+0x3E = 8
state+0x40 = dimension
```

for the narrow/special dimension class.

Therefore wide spacing is **not** a global tracking problem.

## Why pure data-only narrow spacing is blocked

Renderer metadata function `0x8003C210` classifies Japanese multibyte ranges as full-width. The custom static mapping branch is reached through those same full-width code ranges.

The 1-byte/ASCII narrow path uses a separate remap/source path and is not a drop-in replacement for custom mapping.

Do not simply switch production encoder to ASCII.

Also do not force wide 12px bitmap data into the narrow copy routine: copy width and advance are coupled, so bitmap clipping is a real risk.

## Cache-key ownership — important

Caller keeps current character in `s0`, but the stronger isolation key is glyph source.

`0x8003C210` returns a value derived from source glyph pointer:

```text
cache_key = glyph_source_pointer >> 1
```

Cache lookup compares this key against `state+112[...]`.

Therefore cache is **not keyed by character code**.

Consequence:

> a reserved Vietnamese code must not map to an existing native Latin slot if we want a private 8px cache advance, because it may alias an already-created full-width cache record.

## Preferred production spacing architecture — private native bank

For the first real-text proof `Chọn tướng`, use nine distinct private display units:

```text
C h ọ n SPACE t ư ớ g
```

All nine get dedicated native atlas slots, including plain Latin and space.

Pipeline:

```text
zero-static-hit CP932 code
 -> static mapping entry
 -> private native 12x12 / 72-byte atlas slot
 -> normal wide 12x12 bitmap copy
 -> unique source pointer / cache key
 -> cache record+6 = 8px only for private-bank key range
```

This gives three-layer isolation:

1. private code;
2. private glyph source;
3. private cache key/advance.

Japanese/native glyph sources outside the private block must use the original advance formula unchanged.

## CURRENT — READ-ONLY FontPrivateBankScanner 0.1

Detailed note:

```text
FONT_PRIVATE_BANK_SCANNER_0.1.md
```

Local package:

```text
GaiaMaster_FontPrivateBankScanner_0.1.zip
```

Expected report:

```text
GaiaMaster_FontPrivateBankScanner_01.txt
```

Scanner accepts CLEAN BIN only and does not patch or boot anything.

One-pass goals:

1. find contiguous 9-slot atlas runs where every prior mapped code has zero static text hits;
2. strongly prefer a run whose slots are completely unmapped;
3. find >=9 CP932 codes with zero static hits;
4. compute private source pointer range and `source>>1` cache-key range;
5. dump exact `0x8003CC88..0x8003CCD0` patch neighborhood;
6. list aligned executable NOP/zero runs as **code-cave candidates only**.

A zero/NOP run is not automatically safe. Manual reverse-check remains mandatory.

## Next gate

After receiving `GaiaMaster_FontPrivateBankScanner_01.txt`:

1. validate best 9-slot private bank;
2. validate selected zero-hit codes;
3. manually reverse candidate cave/control references;
4. only if cave ownership is sufficiently safe, build **one** isolated runtime `0.6.6.2` proof for Character Select;
5. patch only cached advance for private source/key range to 8px;
6. no global cursor hook;
7. one emulator run, stop immediately on freeze/global corruption.

## Hard do-not-repeat

- no Krom path;
- no production 12x16;
- no failed 0.6.3.x retests;
- no composite X/Y tuning loop;
- no 0.6.5.2 runtime pointer redirect;
- no assumption consecutive code == consecutive atlas slot;
- no 0.6.5.3 retest;
- do not reopen mapping/encoder/baseline because of horizontal spacing;
- do not reuse native Latin atlas slots for private spacing proof;
- do not globally modify `state+0x3C/+0x3E/+0x40`;
- do not globally modify cursor advance;
- stop immediately on freeze/global corruption.

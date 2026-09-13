# Gaia Master — probe/build index

Updated: **2026-09-13**

Purpose: prevent checkpoint confusion and accidental retesting.

## Stable baselines

```text
Clean Japan BIN SHA1
f4d5298583c90d89c4b7e51d2dde160ee07f2aec

Alpha 0.6.1 FRONT SHA1
54d2fb026bc3b71c79861e723caffb4114caa34c
```

## Historical locks

- `0.6.2.13` static custom atlas: **PASS**.
- `0.6.3.x` 12x16: shared-state corruption/freezes. **Do not revive**.
- `0.6.4.x` composite overlay: placement unreliable. **Not production**.
- `0.6.5.2` runtime pointer redirect: **UNSAFE FAIL / NEVER RETEST**.
- Font Mapping Initializer Scanner 0.2: mapping/global ownership **PROVEN**.
- `0.6.5.3`: mapping-only **STRUCTURAL PASS**, glyph generator bugs only.
- `0.6.5.4`: native-base pipeline **PASS**, vertical crowding only.
- `0.6.5.5`: compact Vietnamese glyphs **VISUAL PASS ENOUGH FOR PRODUCTION**.

## 0.6.6.x production encoder

### 0.6.6.0 PRODUCTION ENCODER REAL-TEXT

Runtime text:

```text
Chọn tướng
```

Result: **REAL-TEXT ENCODER PASS / BASELINE POLISH NEEDED.**

Proven:
- accented Vietnamese phrase appears end-to-end;
- plain Latin uses native Gaia glyphs;
- `ọ`, `ư`, `ớ` use safe custom mapping + atlas cells;
- no hook/pointer redirect required;
- stable boot/UI.

### 0.6.6.1 BASELINE-NORMALIZED REAL-TEXT

Runtime screenshot: **PASS.**

- custom Vietnamese glyphs align acceptably with native Latin;
- mapping, encoder, native 12x12 glyph composition, and vertical baseline are production-ready enough;
- remaining issue is horizontal spacing only.

Do not retest `0.6.6.1` just to re-evaluate baseline.

## HORIZONTAL SPACING REVERSE

Static reverse proves Gaia uses a cached per-glyph advance.

Cache hit:

```text
record = state+84 + cache_slot*16
advance = record.byte6
state+24 += advance
if advance != state+62:
    state+24 += state+60
```

Cache miss:

```text
copy_return == 8
    ? advance = state+62
    : advance = state+64 + 1

if advance != state+62:
    advance += state+60

state+24 += advance
```

Current interpretation:

```text
state+60 = extra tracking
state+62 = special/small advance candidate
state+64 = native dimension feeding normal advance
record+6 = final cached advance
```

This explains why Latin-looking full-width glyphs remain visually far apart even though their bitmaps are narrow.

## CURRENT — READ-ONLY FONT SPACING SCANNER 0.1

There is **NO runtime 0.6.6.2 build yet**.

Files:

```text
FONT_SPACING_SCANNER_0.1.md
tools/font_spacing_scanner_0.1.py
tools/00_RUN_FONT_SPACING_SCANNER_0.1.cmd
```

Expected report:

```text
GaiaMaster_FontSpacingScanner_01.txt
```

Scanner is READ-ONLY and searches the full SLPS for ownership/value sources of:

```text
state+0x3C / +60
state+0x3E / +62
state+0x40 / +64
```

It also dumps cache-field writes, renderer/cache init context and direct callers.

### Gate

**Do not build a spacing runtime probe until ownership is proven.**

Preferred result after scanner:
- reuse a native/local small-width or per-renderer metric if one exists;
- avoid global cursor/spacing mutation and avoid affecting untranslated Japanese text.

## Current do-not-repeat

- no Krom path;
- no production 12x16;
- no failed 0.6.3.x retests;
- no composite X/Y loop;
- no 0.6.5.2 runtime redirect;
- no assumption consecutive code == consecutive atlas slot;
- no 0.6.5.3 retest;
- no more glyph-board loops unless a production regression requires it;
- no reopening mapping/encoder/baseline due to horizontal spacing;
- no runtime spacing patch before scanner ownership proof;
- stop immediately on freeze/global corruption.

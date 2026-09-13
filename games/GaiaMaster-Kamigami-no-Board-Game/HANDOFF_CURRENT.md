# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** mapping-data-only + production encoder + baseline đã runtime PASS. `0.6.6.1 BASELINE-NORMALIZED` là runtime baseline tốt. Vấn đề còn lại là horizontal spacing. Private 12x12 bank đã static PASS, nhưng code-cave candidate bị REJECT vì overlap native narrow font resource. Current step là **READ-ONLY FontNarrowBankScanner 0.1** để kiểm tra một hướng tốt hơn: dùng chính native 1-byte narrow glyph bank để nhận advance 8px **không cần runtime hook**. Chưa build runtime `0.6.6.2`.

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

Custom mapping path:

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
- `0.6.3.x`: 12x16 touched shared renderer/cache state and produced corruption/freezes. Reverse notes may be reused; production design may not.
- `0.6.4.x`: composite overlay placement unreliable. Not production.
- `0.6.5.2`: **UNSAFE FAIL / NEVER RETEST**, pointer redirect caused black screen / FPS0 / hard freeze.
- Mapping ownership proven at `0x8003DD48..0x8003DD5C`.
- `0.6.5.3`: mapping-only structural PASS.
- `0.6.5.4`: native base glyph copy pipeline PASS.
- `0.6.5.5`: accent-safe compact board good enough for production pivot.
- `0.6.6.0`: production encoder rendered real text `Chọn tướng`.
- `0.6.6.1`: baseline-normalized real text runtime PASS.

## Proven spacing/cache facts

Cache record:

```text
record size = 16 bytes
record+6    = final horizontal advance
```

Cache miss around `0x8003CC98`:

```text
copy_return == 8
  ? advance = state+0x3E
  : advance = state+0x40 + 1
```

Tracking:

```text
if advance != state+0x3E:
    advance += state+0x3C
```

For the relevant renderer setup:

```text
state+0x3C = 0
```

Metric setter around `0x8003CED0` proves:

```text
dimension 11 -> state+0x3E = 8
state+0x40 = dimension
```

So current wide spacing is not a global tracking problem.

## Why current custom CP932 mapping stays wide

Renderer `0x8003C210` classifies Japanese two-byte ranges (`0x81..0x9F`, `0xE0..0xFC`) into the full-width branch before custom mapping lookup. Current Vietnamese custom codes live in that class, so they inherit wide-copy geometry.

Cache is keyed by glyph source, not code:

```text
cache_key = glyph_source_pointer >> 1
```

This was why the first spacing plan duplicated all 9 display units into a private 12x12 bank.

## FontPrivateBankScanner 0.1 — RESULT

Uploaded report: `GaiaMaster_FontPrivateBankScanner_01.txt`.

Static result:

```text
best private bank = atlas slots 432..440
all 9 slots       = UNMAPPED
static text hits  = 0 for every slot
safe CP932 codes  = 32 found
```

Best bank source/key range:

```text
source : 0x8007366C .. <0x800738F4
key    : 0x40039B36 .. <0x40039C7A
```

This proves the private 12x12 bank itself is available.

### Code-cave candidate — REJECTED

Scanner found only one large aligned zero run:

```text
SLPS+0x5C0E0 .. <0x5C2B8
VA 0x8006B8E0 .. <0x8006BAB8
size 472
4 direct control refs
```

Manual reverse then identified the native narrow font bank at:

```text
RAM  0x8006BAAC
SLPS 0x5C2AC
```

Therefore the zero-run's final **12 bytes overlap the native narrow font resource**.

Decision:

> `0x5C0E0..<0x5C2B8` is NOT a safe cave. Never inject code there.

Do not build the private-cache-hook architecture using that run.

## New native narrow-bank finding

Gaia already has a native 1-byte narrow source pipeline.

Key addresses:

```text
halfwidth remap table RAM = 0x8007E01C
narrow source base RAM    = 0x8006BAAC
main atlas RAM            = 0x8006BCEC
```

Caller parser around `0x8003C934..0x8003C9DC` accepts one-byte halfwidth class `0xA0..0xDF`; `0xDE/0xDF` have modifier/composition behavior, so production candidates should avoid them.

Renderer one-byte path around `0x8003C310..0x8003C438` uses the halfwidth table and, for resolved source indices `<15`, calculates a source inside the native narrow bank.

For dimension 11:

```text
rows = 12
3 bytes per narrow glyph per row
6-byte packed row = glyph A half + glyph B half
pair block = 72 bytes
```

The region:

```text
0x8006BAAC .. <0x8006BCEC
```

is exactly 576 bytes = 8 packed pairs. It can represent 15 narrow source indices.

Source formula for resolved index `i`:

```text
source = 0x8006BAAC
       + 3 * ((i & ~1) * 12)
       + 3 * (i & 1)
```

Narrow copy uses this 3-byte half with 6-byte source stride and returns `8`, so cache miss naturally selects the existing 8px advance.

## CURRENT — READ-ONLY FontNarrowBankScanner 0.1

Files:

```text
tools/font_narrow_bank_scanner_0.1.py
tools/00_RUN_FONT_NARROW_BANK_SCANNER_0.1.cmd
FONT_NARROW_BANK_SCANNER_0.1.md
```

Local package:

```text
GaiaMaster_FontNarrowBankScanner_0.1.zip
```

Expected report:

```text
GaiaMaster_FontNarrowBankScanner_01.txt
```

Scanner goals:

1. decode ASCII `0x21..0x7F` aliases into the native narrow bank;
2. decode halfwidth `0xA0..0xDD` table aliases;
3. resolve actual narrow source indices `0..14`;
4. group aliases by source index so alias collisions are visible;
5. scan strict null-terminated text-like usage in PRGPACK + SLPS;
6. reject state-dependent halfwidth table entries (`0x2000` flag);
7. find distinct source indices with zero strict-text alias hits and at least one valid halfwidth byte candidate;
8. test whether >=9 clean sources exist for:

```text
C h ọ n SPACE t ư ớ g
```

## Next gate

If `FontNarrowBankScanner 0.1` finds >=9 clean distinct sources:

1. cross-check selected aliases/source indices against Translation Master / known Japanese strings;
2. design compact ~6px-wide Vietnamese glyphs in the native packed bank;
3. only then build **ONE data-only Character Select runtime proof**;
4. desired path:

```text
private Vietnamese 1-byte code
 -> existing halfwidth table
 -> native narrow source
 -> native narrow copy
 -> copy_return 8
 -> native cached advance 8px
```

No code cave, no cursor hook, no `record+6` hook, no pointer redirect.

If scanner finds <9 clean sources:

- no emulator test;
- keep `0.6.6.1` as runtime baseline;
- continue offline isolated cache-advance research.

## Hard do-not-repeat

- no Krom path;
- no production 12x16;
- no failed 0.6.3.x retests;
- no composite X/Y tuning;
- no `0.6.5.2` pointer redirect;
- no global `state+0x3C/+0x3E/+0x40` mutation;
- no global cursor/spacing hook;
- never use `SLPS+0x5C0E0..<0x5C2B8` as a cave;
- no runtime `0.6.6.2` until the narrow-bank static gate + Translation Master cross-check close;
- stop immediately on freeze/global corruption.

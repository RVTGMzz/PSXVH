# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** `0.6.6.1 BASELINE-NORMALIZED` là LAST GOOD runtime build. Câu Việt thật `Chọn tướng` render đúng qua pipeline mapping-only + native 12x12, baseline đạt mức production-usable. Các thử nghiệm 6x12/narrow sau đó không thay đổi kết luận này. `0.6.6.2c` đã runtime FAIL vì one-byte alias không route tới narrow glyph như giả định. Narrow path RETIRED cho production. Current step là **Production Capacity Scanner 0.1**, READ-ONLY, kiểm tra liệu full Vietnamese codepage 134 custom glyph có fit vào kiến trúc 12x12 đã chứng minh hay không.

## Baseline

- Game: `GaiaMaster - Kamigami no Board Game (Japan).bin`
- serial: `SLPS-02075`
- clean BIN SHA1: `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- clean SLPS SHA1: `1dfeb6b7cfda59c108dde2dc0b8abda9a40e6ae5`
- clean PRGPACK SHA1: `a9b195b8ae5d8cad7f4f755daa08337d4671632c`
- repo: `ronvotri/Viet-Hoa-PS1`
- branch: `gaia-character-select-font-atlas-reverse-01`

## Proven production font facts

```text
runtime GP     = 0x80085F28
atlas global   = gp+0x518
mapping global = gp+0x51C
main atlas RAM = 0x8006BCEC
mapping RAM    = 0x8007AECC
main atlas file= SLPS+0x5C4EC
mapping file   = SLPS+0x6B6CC
860 glyphs
native main font = 12x12 / 72-byte / 4bpp / LOW nibble first
```

Renderer mapping path:

```text
code & 0x7FFF
 -> mapping[index]
 -> glyph index
 -> glyph_index * 72
 -> atlas base + offset
```

Known mapping facts:

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
field = 24 bytes
```

## Runtime history locks

- `0.6.2.13`: static custom-atlas replacement PASS.
- `0.6.3.x`: 12x16 caused shared-state corruption/freezes. Historical only.
- `0.6.4.x`: composite overlay placement unreliable. Stop.
- `0.6.5.2`: **UNSAFE FAIL / NEVER RETEST**, runtime pointer redirect caused black screen/FPS0/hard freeze.
- `0.6.5.3`: mapping-only structural PASS.
- `0.6.5.4`: native A/E/O base copy PASS.
- `0.6.5.5`: compact accented glyph board visual PASS enough for production pivot.
- `0.6.6.0`: real Vietnamese text `Chọn tướng` rendered end-to-end.
- `0.6.6.1`: baseline-normalized real text **PASS / LAST GOOD**.

## 0.6.6.1 LAST GOOD

What is proven:

- main 12x12 atlas works with custom Vietnamese glyphs;
- static mapping entries route custom codes correctly;
- plain Latin can reuse native Gaia full-width Latin glyphs;
- `ọ`, `ư`, `ớ` rendered correctly enough;
- vertical baseline is acceptable;
- no code hook;
- no pointer redirect;
- stable boot/UI.

Remaining visual issue:

```text
horizontal spacing is wider than ideal because these are full-width cells
```

Decision:

> spacing is POLISH, not a reason to change the production encoding architecture.

Do not retest or replace `0.6.6.1` architecture merely to chase tighter spacing.

## Spacing reverse knowledge retained

Cache record:

```text
record size = 16 bytes
record+6    = final horizontal advance
```

Cache miss:

```text
copy_return == 8
  ? advance = state+0x3E
  : advance = state+0x40 + 1
```

Character Select tracking is 0 and dimension-11 narrow advance is 8px.

Useful reverse knowledge, but no production spacing patch is approved.

## 6x12 narrow experiments — RETIRED

### 0.6.6.2

Builder safety gate false-positive. No BIN/CUE. No runtime conclusion.

### 0.6.6.2b

Strict gate still false-positive on binary-looking CP932 runs. No BIN/CUE. No runtime conclusion.

### 0.6.6.2c CORPUS-AUDITED

Builder succeeded and user runtime-tested Character Select.

Generated field bytes:

```text
22 23 24 26 20 27 2A 5A 26 58
```

Expected:

```text
Chọn tướng
```

Actual runtime screenshot showed unrelated/garbled glyphs instead of the intended Latin/Vietnamese text.

Conclusion:

```text
0.6.6.2c = RUNTIME FAIL
one-byte alias -> assumed narrow index routing is false in actual Character Select state
RETIRE this path
DO NOT RETEST
```

This does NOT invalidate the 12x12 mapping-only production path.

## Code cave REJECT remains

Never inject into:

```text
SLPS+0x5C0E0..<0x5C2B8
RAM 0x8006B8E0..<0x8006BAB8
```

It overlaps real narrow-font data beginning at `SLPS+0x5C2AC`.

## CURRENT — Production Capacity Scanner 0.1

Purpose:

> Before optimizing around the current translation corpus, test the stronger question: can Gaia support the **entire Vietnamese precomposed repertoire** using the proven 12x12 mapping-only architecture?

Worst-case repertoire:

```text
67 lowercase custom glyphs
67 uppercase custom glyphs
TOTAL = 134 custom glyphs
```

Plain ASCII vowel/base letters remain native Gaia full-width glyphs and do not consume custom slots.

Scanner is READ-ONLY and checks:

1. CLEAN BIN / SLPS / PRGPACK hashes;
2. known mapping facts;
3. native base slots required to synthesize Vietnamese and protects them;
4. zero-static-hit CP932 custom codes in the runtime-proven >=0x889F region;
5. zero-static-hit atlas slots;
6. separates completely unmapped slots from mapped-but-zero-static-hit slots;
7. PASS/FAIL for a full 134-glyph codepage;
8. if PASS, emits deterministic `Unicode -> code -> atlas slot` allocation.

Expected report:

```text
GaiaMaster_ProductionCapacityScanner_01.txt
```

No runtime BIN is created by this scanner.

### Next if scanner PASS

- freeze full Vietnamese production codepage;
- build glyph generator from 0.6.6.1 baseline-preserving 12x12 composition;
- integrate production encoder;
- patch multiple real `vi_full` strings in one maximally informative runtime build;
- keep current full-width spacing until translation pipeline is stable at scale.

### Next if scanner FAIL

- inventory exact non-ASCII characters actually present in `vi_full`;
- allocate only that smaller real corpus;
- do not return to narrow/spacing experiments.

## Hard do-not-repeat

- no Krom path;
- no production 12x16;
- no failed 0.6.3.x retests;
- no composite X/Y tuning loop;
- no 0.6.5.2 pointer redirect;
- no one-byte narrow alias production path;
- no 0.6.6.2 / 0.6.6.2b retests;
- no 0.6.6.2c retest;
- no global cursor/cache/spacing mutation;
- no code cave at the narrow-font boundary;
- do not reopen mapping/encoder/baseline due to horizontal spacing;
- stop immediately on freeze/global corruption.

## User testing preference

- minimize emulator tests;
- maximize information per test;
- scanners/read-only analysis before risky runtime builds;
- never repeat a known failed or already-proven build.

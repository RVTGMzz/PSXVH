# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** giữ renderer/font geometry native **12x12 / 72-byte / 4bpp**. Mapping ownership đã được chứng minh. Mapping-data-only đã runtime PASS. `0.6.6.0 PRODUCTION ENCODER REAL-TEXT` đã hiện đúng câu Việt thật `Chọn tướng`; vấn đề còn lại chỉ là baseline của `ọ / ư / ớ` chưa đều với Latin native. Current proof là **0.6.6.1 BASELINE-NORMALIZED REAL-TEXT**: giữ nguyên bbox/baseline native khi glyph gốc đã đủ chỗ cho dấu, chỉ fit tối thiểu khi thật sự thiếu headroom/footroom. Không code hook, không pointer redirect, không 12x16, không composite.

## Baseline

- Game: `GaiaMaster - Kamigami no Board Game (Japan).bin`
- serial: `SLPS-02075`
- clean BIN SHA1: `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- Alpha 0.6.1 FRONT SHA1: `54d2fb026bc3b71c79861e723caffb4114caa34c`
- branch: `gaia-character-select-font-atlas-reverse-01`
- repo: `ronvotri/Viet-Hoa-PS1`

## Proven font facts

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

Initializer ownership:

```text
0x8003DD48..0x8003DD50 -> atlas 0x8006BCEC -> gp+0x518
0x8003DD54..0x8003DD5C -> map   0x8007AECC -> gp+0x51C
```

Renderer consumer:

```text
code & 0x7FFF
 -> mapping[index]
 -> glyph index
 -> glyph index * 72
 -> atlas base + offset
```

Known mapping samples:

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
24 bytes used safely by current proof
```

## Historical conclusions

### 0.6.2.x
- `0.6.2.13` proved static custom-atlas replacement works.
- Native 12x12 needs a compact Vietnamese style.

### 0.6.3.x
12x16 touched shared renderer/cache state and caused corruption/freezes. Historical only; do not revive.

### 0.6.4.x
Composite overlay placement was unreliable. Not production.

### 0.6.5.2
**UNSAFE FAIL / NEVER RETEST**: runtime pointer redirect caused black screen, Game FPS 0, hard freeze.

### Mapping Scanner 0.2
Recovered runtime GP and direct atlas/mapping ownership. Static mapping data can be patched directly.

### 0.6.5.3
**STRUCTURAL PASS / GLYPH GENERATOR FAIL.** Mapping-controlled custom slots reached without hook/redirect.

### 0.6.5.4
**PIPELINE PASS / VERTICAL CROWDING.** Native A/E/O controls correct; remaining issue was mark headroom.

### 0.6.5.5
**VISUAL PASS ENOUGH FOR PRODUCTION PIVOT.** Compact Vietnamese marks readable; stop glyph-board runtime loops.

## Translation source

Translation Master 0.6:
- 596 rows;
- `vi_full` = accented source-of-truth;
- `vi_game_current` = old no-accent fallback.

Production strategy:

```text
plain Latin / numbers / punctuation
  -> reuse Gaia native full-width CP932 glyphs

Vietnamese-specific precomposed chars
  -> dedicated custom mapping entries
  -> selected zero-static-hit native 12x12 atlas slots
```

## 0.6.6.0 PRODUCTION ENCODER REAL-TEXT — PASS WITH BASELINE POLISH NEEDED

Runtime screenshot showed:

```text
Chọn tướng
```

What this proves:
- actual Vietnamese text is encoded end-to-end;
- plain Latin uses native Gaia glyphs;
- `ọ`, `ư`, `ớ` use custom zero-hit codes + custom atlas cells;
- static mapping-only architecture works for production text;
- stable boot/UI; no corruption/freeze.

Observed visual issue:
- custom Vietnamese-specific bodies sit at uneven vertical positions relative to untouched native Latin.

Root cause:

```text
0.6.6.0 unconditionally compressed every custom base into rows 2..9.
```

This altered the natural baseline even when lowercase native `o/u` already had enough headroom.

Conclusion:

> `0.6.6.0 = REAL-TEXT ENCODER PASS / BASELINE POLISH NEEDED`.

Do not reinterpret this as an encoder/mapping failure.

## CURRENT — 0.6.6.1 BASELINE-NORMALIZED REAL-TEXT

Detailed note:

`BASELINE_NORMALIZATION_0.6.6.1.md`

Expected Character Select text remains:

```text
Chọn tướng
```

New glyph fitting rule:

1. inspect native base bbox;
2. if existing bbox already leaves enough room for requested marks, keep the body byte geometry unchanged (`native-preserved`);
3. only when space is insufficient, fit/shift the minimum amount (`minimal-fit`);
4. preserve the original bottom/baseline whenever possible;
5. place accents relative to the fitted body bbox, not hardcoded absolute y rows.

Report now records per custom glyph:

```text
fit_mode
src_bbox
body_bbox
final_bbox
```

This makes remaining polish deterministic.

Package:

```text
GaiaMaster_0.6.6.1_BASELINE_NORMALIZED_REAL_TEXT_PROOF.zip
```

Status: **READY FOR ONE RUNTIME TEST.**

If still uneven, collect:

```text
screenshot
[VI 0.6.6.1 BASELINE].txt
```

## Next after 0.6.6.1 visual pass

1. inventory exact non-ASCII chars used by `vi_full`;
2. measure safe custom-code and atlas-slot capacity;
3. freeze deterministic Vietnamese production codepage;
4. integrate encoder into Translation Master rebuild;
5. migrate real rows from `vi_game_current` to accented `vi_full` encoding.

## Hard do-not-repeat

- no Krom path;
- no production 12x16;
- no failed 0.6.3.x retests;
- no composite X/Y tuning loop;
- no 0.6.5.2 runtime redirect;
- no assumption consecutive code == consecutive atlas slot;
- no 0.6.5.3 retest;
- no more 12-glyph style-board runtime loops unless a production regression demands it;
- do not reinterpret 0.6.6.0 baseline unevenness as mapping failure;
- stop immediately on freeze/global corruption.

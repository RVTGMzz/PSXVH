# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** giữ renderer/font geometry native **12x12 / 72-byte / 4bpp**. Mapping ownership đã được chứng minh. `0.6.5.3` runtime chứng minh kiến trúc mapping-data-only hoạt động; `0.6.5.4` chứng minh native A/E/O copy đúng; `0.6.5.5 ACCENT-SAFE COMPACT` đã đạt mức visual pass đủ để khóa hướng sản xuất. Không tiếp tục vòng lặp bảng 12 glyph nữa. Current proof là **0.6.6.0 PRODUCTION ENCODER REAL-TEXT**, dùng câu Việt thật `Chọn tướng`, native glyph cho Latin thường và chỉ custom-map các ký tự tiếng Việt đặc thù. Không code hook, không pointer redirect, không 12x16, không composite.

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

Known mapping samples:

```text
0x8273 Ｔ -> glyph 481
0x8264 Ｅ -> glyph 466
0x8272 Ｓ -> glyph 480
0x889F 亜 -> glyph 0
```

Renderer consumer:

```text
code & 0x7FFF
 -> mapping[index]
 -> glyph index
 -> glyph index * 72
 -> atlas base + offset
```

Character Select test text:

```text
PRGPACK.BDP + 0xBFD2C
owner nested BDP = entry 29
local offset = +0x580
24-byte proof field used safely by 0.6.5.x
```

## Historical conclusions

### 0.6.2.x
- `0.6.2.13` proved static custom-atlas replacement works.
- Native 12x12 needs a compact Vietnamese style.

### 0.6.3.x
12x16 touched shared renderer/cache state and caused corruption/freezes. Historical only; do not revive.

### 0.6.4.x
Composite overlay placement was unreliable. Stop X/Y tuning; not production.

### 0.6.5.0
Consecutive CP932 codes do not map linearly to atlas slots.

### 0.6.5.1
Build-time cave assumption bug only. No runtime conclusion.

### 0.6.5.2 ATLAS-BACKED CUSTOM BANK
**UNSAFE FAIL / NEVER RETEST**: black screen, Game FPS 0, hard freeze. Reject runtime pointer redirect.

## Mapping recovery

### Scanner 0.1
Found `GP0=0` in header; GP is initialized after entry.

### Scanner 0.2 — PASS
Recovered runtime GP and direct ownership writes. Static mapping data can be patched directly.

## 0.6.5.3 MAPPING-ONLY NATIVE-CELL

**STRUCTURAL PASS / GLYPH GENERATOR FAIL.**

Runtime proved:
- game boots;
- Character Select reaches patched mapping-controlled slots;
- no hook or pointer redirect is needed;
- no freeze/global corruption.

Do not retest.

## 0.6.5.4 NATIVE-BASE STYLE

**PIPELINE PASS / VERTICAL CROWDING.**

- plain A/E/O native controls looked correct;
- mapping and slot ownership correct;
- Vietnamese marks present;
- full-height base glyphs left too little accent headroom.

## 0.6.5.5 ACCENT-SAFE COMPACT

Runtime screenshot result: **VISUAL PASS ENOUGH FOR PRODUCTION PIVOT.**

Observed:
- A/E/O controls correct;
- compact accents readable;
- circumflex / acute / hook / tilde families visually distinct;
- stable boot and UI;
- remaining roughness is 12x12 pixel-art polish only.

Decision:

> lock mapping-only + native 12x12 pipeline; stop testing glyph boards and move to a real Vietnamese encoder.

## Translation source

Translation Master 0.6:
- 596 rows;
- `vi_full` is the accented source-of-truth;
- `vi_game_current` is the old no-accent fallback.

Production strategy:

```text
plain Latin / numbers / punctuation
  -> reuse Gaia native full-width CP932 glyphs

Vietnamese-specific precomposed chars
  -> dedicated custom mapping entries
  -> selected safe native 12x12 atlas slots
```

This avoids wasting custom slots on plain A-Z/a-z and minimizes damage to untranslated Japanese text.

## CURRENT — 0.6.6.0 PRODUCTION ENCODER REAL-TEXT PROOF

Expected Character Select text:

```text
Chọn tướng
```

Why this phrase:
- actual UI wording rather than a glyph board;
- fits the 24-byte proof field at 20 encoded bytes + terminator;
- tests lowercase native Latin and Vietnamese-specific `ọ`, `ư`, `ớ`;
- exercises dot-below, horn, and horn+acute composition.

Builder behavior:
- requires CLEAN BIN SHA1;
- native full-width CP932 for plain ASCII letters/space;
- scans for zero-static-hit custom CP932 codes;
- scans for zero-static-hit atlas destination slots;
- patches only mapping entries + 12x12 glyph data + Character Select text bytes;
- writes explicit terminator/padding into the 24-byte proof field;
- outputs a detailed allocation report.

Package:

```text
GaiaMaster_0.6.6.0_PRODUCTION_ENCODER_REAL_TEXT_PROOF.zip
```

Status: **READY FOR ONE RUNTIME TEST.**

Expected screenshot line:

```text
Chọn tướng
```

If wrong, collect:

```text
screenshot
[VI 0.6.6.0 PROD ENCODER].txt
```

## Next after 0.6.6.0 PASS

1. inventory the exact non-ASCII character set currently used by `vi_full`;
2. measure safe custom-code and safe atlas-slot capacity;
3. freeze a deterministic Vietnamese codepage allocation;
4. add full encoder integration to Translation Master rebuild;
5. migrate real translated rows from `vi_game_current` fallback to `vi_full` production encoding.

## Hard do-not-repeat

- no Krom path;
- no production 12x16 path;
- no failed 0.6.3.x retests;
- no composite X/Y tuning loop;
- no runtime redirect like 0.6.5.2;
- no assumption consecutive code == consecutive atlas slot;
- no 0.6.5.3 retest;
- no more 12-glyph style-board runtime loops unless a production regression demands it;
- stop immediately on freeze/global corruption.

## User testing preference

- minimize emulator tests;
- maximize information per test;
- never repeat tested builds;
- prefer read-only reverse work before risky probes;
- stop immediately on freeze/global corruption.

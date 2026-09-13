# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** giữ renderer/font geometry native **12x12 / 72-byte / 4bpp**. Mapping ownership đã được chứng minh. `0.6.5.3` runtime chứng minh kiến trúc **mapping-data-only** hoạt động. `0.6.5.4` tiếp tục chứng minh copy A/E/O native byte-for-byte là đúng; vấn đề còn lại chỉ là bố cục dấu trong ô 12x12. Current runtime proof là **0.6.5.5 ACCENT-SAFE COMPACT NATIVE STYLE**: A/E/O thường giữ native control, chữ có dấu nén thân vào rows 3..11 và dành rows 0..2 cho dấu hai lớp fill+shadow. Không code hook, không pointer redirect, không 12x16, không composite.

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

Generic setter:

```text
0x8003DD68 sw a0,0x518(gp)
0x8003DD6C sw a1,0x51C(gp)
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
- Character Select reaches the patched mapping-controlled slots;
- no hook or pointer redirect is needed;
- no freeze/global corruption.

Generator bugs:

```python
setpix(..., v=7)
base = label[0] if label[0] in "AEO" else "A"
```

Index `7` rendered as the dark/shadow layer. Unicode `Ê/Ế/Ể/Ô/Ố/Ỗ` fell back to A. Do not retest 0.6.5.3.

## 0.6.5.4 NATIVE-BASE STYLE

Runtime screenshot proved:
- plain A/E/O copied from Gaia native glyphs look correct;
- mapping and slot ownership remain correct;
- Vietnamese marks are actually present;
- remaining issue is vertical crowding: full-height native bases leave too little headroom, so marks merge into the top of A/E/O.

Conclusion:

> mapping -> slot -> native glyph pipeline is solved. Remaining work is glyph composition/art only.

Do not treat 0.6.5.4 as a mapping failure.

## CURRENT — 0.6.5.5 ACCENT-SAFE COMPACT NATIVE STYLE

Detailed note:

`FONT_MAPPING_PROOF_0.6.5.5.md`

Builder:

```text
tools/build_gaia_0655_accent_safe.py
tools/00_BUILD_0.6.5.5_ACCENT_SAFE.cmd
```

Design:

```text
0x889F..0x88AA
  -> patched static mapping entries
  -> selected low-use atlas slots
  -> native A/E/O source glyphs
  -> accented variants vertically compacted into rows 3..11
  -> rows 0..2 reserved for Vietnamese marks
  -> marks rendered with native fill + shadow layers
```

Controls:
- plain `A`, `E`, `O` remain byte-for-byte native;
- palette index 7 is treated as shadow, based on 0.6.5.3 runtime evidence;
- fill is selected from the remaining native nonzero palette indices;
- no runtime engine changes.

Expected Character Select order:

```text
A Â Ấ Ẳ E Ê Ế Ể O Ô Ố Ỗ
```

Status: **READY FOR ONE RUNTIME TEST.**

If visual output is wrong, collect both:

```text
screenshot
[VI 0.6.5.5 ACCENT SAFE].txt
```

The report includes native bbox, palette histogram, fill/shadow indices, selected slots, and compacted glyph bbox.

## Hard do-not-repeat

- no Krom path;
- no production 12x16 path;
- no retest 0.6.2.18;
- no retest failed 0.6.3.x probes;
- no composite X/Y tuning loop;
- no runtime redirect like 0.6.5.2;
- no assumption consecutive code == consecutive atlas slot;
- no retest 0.6.5.3;
- do not reinterpret 0.6.5.4 visual crowding as a mapping failure;
- stop immediately on freeze/global corruption.

## User testing preference

- minimize emulator tests;
- maximize information per test;
- never repeat tested builds;
- prefer read-only reverse work before risky probes;
- stop immediately on freeze/global corruption.

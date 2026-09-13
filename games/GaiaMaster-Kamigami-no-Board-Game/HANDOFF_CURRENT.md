# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** giữ renderer/font geometry native **12x12 / 72-byte / 4bpp**. Mapping ownership đã được chứng minh bằng Font Mapping Initializer Scanner 0.2. `0.6.5.3 MAPPING-ONLY NATIVE-CELL` đã runtime **STRUCTURAL PASS / GLYPH-GENERATOR FAIL**: game boot, mapping-data-only hoạt động và glyph test đi đúng custom slots, nhưng art bị tối/bóng và các chữ E/O có dấu bị thân A do bug generator. Current runtime proof kế tiếp là **0.6.5.4 NATIVE-BASE STYLE**: copy A/E/O native của game làm thân, explicit family mapping, dấu dùng palette suy ra từ glyph native. Vẫn không code hook, không runtime pointer redirect, không 12x16, không composite.

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

Initializer ownership proven at:

```text
0x8003DD48..0x8003DD50 -> atlas 0x8006BCEC -> gp+0x518
0x8003DD54..0x8003DD5C -> map   0x8007AECC -> gp+0x51C
```

Generic setter exists at:

```text
0x8003DD68 sw a0,0x518(gp)
0x8003DD6C sw a1,0x51C(gp)
```

Static mapping samples match all known runtime facts:

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
- Later art tests showed native 12x12 requires a compact unified Vietnamese style.

### 0.6.3.x
12x16 touched shared renderer/cache state and repeatedly caused layout corruption/freezes. Historical only; do not revive.

### 0.6.4.x
Composite overlay art became acceptable but runtime placement was unreliable. Stop X/Y tuning; not production.

### 0.6.5.0
Consecutive CP932 codes were incorrectly assumed to map linearly to slots 0..11. Runtime disproved that assumption.

### 0.6.5.1
Build-time cave assumption bug only. No runtime conclusion.

### 0.6.5.2 ATLAS-BACKED CUSTOM BANK
**UNSAFE FAIL / NEVER RETEST**: black screen, Game FPS 0, hard freeze. Reject post-lookup runtime pointer redirect.

## Mapping recovery result

### Scanner 0.1
Found `GP0=0` in PS-X EXE header. The game initializes GP after entry.

### Scanner 0.2 — PASS
Recovered runtime GP and direct ownership writes. Mapping ownership is demonstrated and static data-only patching is permitted.

```text
GP = 0x80085F28
atlas slot = 0x80086440
map slot   = 0x80086444
```

All four known static mapping entries matched expected glyph indices.

## 0.6.5.3 MAPPING-ONLY NATIVE-CELL — STRUCTURAL PASS / GENERATOR FAIL

Runtime screenshot confirmed:
- game boots normally;
- Character Select line is replaced by the 12 mapping-controlled test codes;
- custom atlas cells are reached without pointer redirect or renderer hook;
- no freeze/global corruption.

Observed visual issue:
- glyph strokes look dark/shadow-like;
- accented E/O-family bodies look A-like.

Root causes found in builder:

```python
setpix(..., v=7)  # hardcoded palette index
base = label[0] if label[0] in "AEO" else "A"
```

The second line is a Unicode bug: `Ê/Ế/Ể/Ô/Ố/Ỗ` do not start with ASCII `E/O`, so they fell back to `A`.

Conclusion:

> mapping-only architecture is runtime-proven; remaining problem is glyph generation/style.

Do not retest 0.6.5.3.

## CURRENT — 0.6.5.4 NATIVE-BASE STYLE PROOF

Detailed note:

`FONT_MAPPING_PROOF_0.6.5.4.md`

Builder:

```text
tools/build_gaia_0654_native_base.py
tools/00_BUILD_0.6.5.4_NATIVE_BASE.cmd
```

Design:

```text
0x889F..0x88AA
  -> patched static mapping entries
  -> selected low-use atlas slots
  -> A/E/O bodies copied from Gaia native full-width glyphs
  -> compact Vietnamese marks inside same 12x12 cell
```

Controls:
- plain `A`, `E`, `O` are byte-for-byte copies of Gaia native glyphs;
- A/E/O family classification is explicit;
- accent palette index is derived from each native base glyph, not hardcoded `7`.

Expected Character Select visual:

```text
A Â Ấ Ẳ E Ê Ế Ể O Ô Ố Ỗ
```

Status: **READY FOR ONE RUNTIME TEST.**

## Hard do-not-repeat

- no Krom path;
- no production 12x16 path;
- no retest 0.6.2.18;
- no retest failed 0.6.3.x probes;
- no composite X/Y tuning loop;
- no runtime redirect like 0.6.5.2;
- no assumption consecutive code == consecutive atlas slot;
- no retest 0.6.5.3 now that its generator bugs are identified;
- stop immediately on freeze/global corruption.

## User testing preference

- minimize emulator tests;
- maximize information per test;
- never repeat tested builds;
- prefer read-only reverse work before risky probes;
- stop immediately on freeze/global corruption.

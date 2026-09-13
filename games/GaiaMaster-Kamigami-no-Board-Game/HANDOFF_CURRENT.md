# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** `0.6.6.1 BASELINE-NORMALIZED` runtime PASS về real Vietnamese glyph + vertical baseline. Static reverse đã mở native **6x12 / 8px narrow path**. `0.6.6.2` không có runtime result vì safety gate false-positive và bị BLOCKED trước khi tạo ROM. Current approved proof là **0.6.6.2b NATIVE NARROW 8PX STRICT GATE**. Chỉ runtime-test nếu builder in `[OK]`. Nếu `[BLOCKED]`, gửi report và không boot gì cả.

## Baseline

- Game: `GaiaMaster - Kamigami no Board Game (Japan).bin`
- serial: `SLPS-02075`
- clean BIN SHA1: `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- clean SLPS SHA1: `1dfeb6b7cfda59c108dde2dc0b8abda9a40e6ae5`
- clean PRGPACK SHA1: `a9b195b8ae5d8cad7f4f755daa08337d4671632c`
- repo: `ronvotri/Viet-Hoa-PS1`
- branch: `gaia-character-select-font-atlas-reverse-01`

## Proven main-font facts

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

Custom mapping pipeline:

```text
code & 0x7FFF
 -> mapping[index]
 -> glyph index
 -> glyph_index * 72
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
proof field = 24 bytes
```

## Historical no-repeat

- `0.6.2.13`: static custom-atlas replacement PASS.
- `0.6.3.x`: 12x16 touched shared renderer/cache state; corruption/freezes. Historical reverse only.
- `0.6.4.x`: composite overlay placement unreliable. Stop.
- `0.6.5.2`: **UNSAFE FAIL / NEVER RETEST**, pointer redirect caused black screen / FPS0 / hard freeze.
- `0.6.5.3`: mapping-only structural PASS.
- `0.6.5.4`: native base-glyph copy PASS.
- `0.6.5.5`: compact accent visual pass enough to leave glyph board.
- `0.6.6.0`: real-text encoder rendered `Chọn tướng`.
- `0.6.6.1`: baseline-normalized real text runtime PASS.

## Spacing facts already proven

Cache record:

```text
size     = 16 bytes
record+6 = final horizontal advance
```

Cache miss:

```text
copy_return == 8
  ? advance = state+0x3E
  : advance = state+0x40 + 1
```

Character Select has:

```text
state+0x3C tracking = 0
```

Native narrow metric:

```text
dimension 11 -> state+0x3E = 8
```

Therefore 0.6.6.1 spacing issue is full-width classification/geometry, not global tracking.

## Private 12x12 bank result

FontPrivateBankScanner found a perfect static private block:

```text
slots 432..440
9/9 all-unmapped
9/9 zero static text hits
32 zero-static-hit CP932 codes
```

This remains useful for future designs, but the old code-cave spacing plan is rejected.

## Code cave REJECT

Only large zero/NOP candidate:

```text
SLPS+0x5C0E0..<0x5C2B8
RAM 0x8006B8E0..<0x8006BAB8
```

Native narrow font begins:

```text
SLPS+0x5C2AC
RAM 0x8006BAAC
```

The supposed cave overlaps real font data. **Never inject code there.**

## Native narrow bank — proven

FontNarrowBankScanner confirms:

```text
RAM        = 0x8006BAAC
SLPS       = 0x5C2AC
geometry   = 6x12 / 4bpp
3 bytes per glyph row
indices 0..14 reachable through current narrow gate
native cached advance = 8px
```

Source formula for dimension 11:

```text
source = 0x8006BAAC
       + 3 * ((index & ~1) * 12)
       + 3 * (index & 1)
```

Renderer path:

```text
1-byte char
 -> direct/table remap
 -> narrow index
 -> native 6x12 source
 -> narrow copy
 -> return 8
 -> cached advance 8px
```

## 0.6.6.2 — BUILD GATE FALSE POSITIVE ONLY

User ran the 0.6.6.2 builder and got:

```text
[BLOCKED] safety gate
```

No BIN/CUE was created, so there is **no runtime conclusion**.

Gate report showed many false-positive binary-looking strings such as:

```text
62R#eUReVR"T"WTV
wp&#"a
s&qﾟ
```

The old text classifier accepted too much ASCII-like binary.

Conclusion:

```text
0.6.6.2 = FALSE BLOCK
DO NOT RETEST OLD PACKAGE
```

## Confirmed narrow owners that must not be borrowed

Translation Master review found real uses:

```text
(  )   -> (速い者順)
+      -> 通行税 %+3d％
```

Already excluded before:

```text
!      punctuation risk
%      format token (%d / %s)
, -    punctuation/control risk
. /    punctuation/control-code risk
```

## CURRENT — 0.6.6.2b NATIVE NARROW 8PX STRICT GATE

Source/launcher:

```text
tools/build_gaia_0662b_native_narrow_8px.py
tools/00_BUILD_0.6.6.2b_NATIVE_NARROW_8PX.cmd
```

Design note:

```text
FONT_NARROW_PROOF_0.6.6.2b.md
```

Local package:

```text
GaiaMaster_0.6.6.2b_NATIVE_NARROW_8PX_STRICT_GATE.zip
```

Expected Character Select text:

```text
Chọn tướng
```

Eight visible custom units:

```text
C h ọ n t ư ớ g
```

Space remains native byte `0x20` and already uses 8px advance.

Temporary diagnostic owners:

```text
"  #  $  &  '  *  Z  X
```

### Strict gate change

`0.6.6.2b` only considers:

1. decoded strings containing Japanese characters as definite text;
2. ASCII-only strings that look like compact uppercase UI/debug labels;
3. mixed-case random-looking byte runs are ignored.

If any of the eight owners still appears in accepted text:

```text
[BLOCKED]
```

=> no BIN/CUE, send:

```text
GaiaMaster_0.6.6.2b_NATIVE_NARROW_GATE_REPORT.txt
```

If `[OK]`, builder writes native 6x12 halves + Character Select proof only, then rebuilds BDP checksums and CD EDC/ECC.

No renderer instruction is modified.

## Runtime gate for 0.6.6.2b

Only if builder prints `[OK]`:

1. boot `[VI 0.6.6.2b NATIVE NARROW 8PX].cue`;
2. go only to Character Select;
3. expected text `Chọn tướng`;
4. spacing should be clearly tighter than 0.6.6.1, around native 8px;
5. stop immediately on freeze/global corruption;
6. send screenshot + generated TXT.

If `[BLOCKED]`, do not boot.

## Important production-scale reverse finding

At `0x8003C3E8`:

```asm
sltiu v0,a1,15
```

selects whether the source uses the narrow formula.

The narrow formula continues linearly in memory. Index 16 would land exactly at main atlas base:

```text
0x8006BAAC + 576 = 0x8006BCEC
```

A normal 12x12 / 72-byte atlas cell is naturally two 6x12 / 36-byte halves by row layout. Therefore the main atlas can theoretically provide a much larger narrow source space.

This is a major production lead, but **do not simply raise the `<15` threshold globally**. That would reclassify existing ASCII/Table1 entries and can break normal text. After 0.6.6.2b proof, design a selective private-code marker/range before any renderer patch.

## Hard do-not-repeat

- no Krom path;
- no production 12x16;
- no failed 0.6.3.x retests;
- no composite X/Y tuning loop;
- no 0.6.5.2 pointer redirect;
- no global cursor/cache/spacing mutation;
- never use `SLPS+0x5C0E0..<0x5C2B8` as cave;
- do not treat `0xE0..0xFC` as private one-byte code space;
- do not retest blocked `0.6.6.2`;
- do not globally raise the `a1 < 15` narrow threshold;
- stop immediately on freeze/global corruption.

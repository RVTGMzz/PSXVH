# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** `0.6.6.1 BASELINE-NORMALIZED` runtime PASS về real Vietnamese glyph + vertical baseline. FontSpacingScanner + FontPrivateBankScanner + FontNarrowBankScanner đã chứng minh Gaia có native **6x12 narrow bank + 8px advance**. Code-cave route bị REJECT vì overlap resource. Current build là **0.6.6.2 NATIVE NARROW 8PX REAL-TEXT PROOF**, data-only, có built-in safety gate. Chỉ runtime-test nếu builder in `[OK]`; nếu `[BLOCKED]` thì gửi gate report và không boot gì cả.

## Baseline

- Game: `GaiaMaster - Kamigami no Board Game (Japan).bin`
- serial: `SLPS-02075`
- clean BIN SHA1: `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- clean SLPS SHA1: `1dfeb6b7cfda59c108dde2dc0b8abda9a40e6ae5`
- clean PRGPACK SHA1: `a9b195b8ae5d8cad7f4f755daa08337d4671632c`
- repo: `ronvotri/Viet-Hoa-PS1`
- branch: `gaia-character-select-font-atlas-reverse-01`

## Main font facts already proven

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

Known facts:

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

## Runtime history to preserve

- `0.6.2.13`: static custom-atlas replacement PASS.
- `0.6.3.x`: 12x16 research touched shared renderer/cache state; corruption/freezes. Historical reverse only, never production.
- `0.6.4.x`: composite accent overlay placement unreliable. Stop.
- `0.6.5.2`: **UNSAFE FAIL / NEVER RETEST**, runtime pointer redirect => black screen / FPS0 / hard freeze.
- `0.6.5.3`: mapping-only structural PASS.
- `0.6.5.4`: native base-glyph copy PASS.
- `0.6.5.5`: compact accents good enough to leave glyph-board phase.
- `0.6.6.0`: real-text production encoder renders `Chọn tướng` end-to-end.
- `0.6.6.1`: baseline-normalized `Chọn tướng` runtime PASS. Remaining issue was wide horizontal spacing.

## Spacing facts proven by FontSpacingScanner

Cache record:

```text
size      = 16 bytes
record+6  = final horizontal advance
```

Cache miss around `0x8003CC98`:

```text
copy_return == 8
  ? advance = state+0x3E
  : advance = state+0x40 + 1
```

Relevant tracking:

```text
state+0x3C = 0
```

Metric init proves native narrow metric:

```text
dimension 11 -> state+0x3E = 8
```

Thus the 0.6.6.1 spacing issue is classification/geometry, not global tracking.

## Private 12x12 bank result

FontPrivateBankScanner found:

```text
slots 432..440
9/9 all-unmapped
9/9 zero static text hits
32 zero-static-hit CP932 codes
```

This bank exists, but its original hook-based spacing plan was abandoned after cave review.

### Code cave REJECT

Only large zero/NOP candidate:

```text
SLPS+0x5C0E0..<0x5C2B8
RAM 0x8006B8E0..<0x8006BAB8
```

Native narrow resource starts at:

```text
SLPS+0x5C2AC
RAM 0x8006BAAC
```

The candidate overlaps real font data. **Never inject code there.**

## Native narrow bank — proven

FontNarrowBankScanner report confirms:

```text
RAM        = 0x8006BAAC
SLPS       = 0x5C2AC
geometry   = 6x12 / 4bpp
row data   = 3 bytes per narrow glyph
packing    = two 6px halves per 6-byte row
bank bytes = 576
indices    = 0..14 reachable; index 15 blank
```

Narrow source formula for dimension 11:

```text
source = 0x8006BAAC
       + 3 * ((index & ~1) * 12)
       + 3 * (index & 1)
```

Original renderer path:

```text
1-byte char
 -> direct/table remap
 -> narrow index <15
 -> native 6x12 source
 -> native narrow copy
 -> copy_return=8
 -> original cached advance=8px
```

Scanner recovered **15 distinct reachable narrow indices**. This opens a no-hook spacing route.

Important: bytes `0xE0..0xFC` are Shift-JIS lead-byte class in the renderer and must not be treated as production one-byte private codes merely because table bytes exist there.

## 0.6.6.2 — CURRENT BUILD

Detailed design note:

```text
FONT_NARROW_PROOF_0.6.6.2.md
```

Source/launcher:

```text
tools/build_gaia_0662_native_narrow_8px.py
tools/00_BUILD_0.6.6.2_NATIVE_NARROW_8PX.cmd
```

Local test package:

```text
GaiaMaster_0.6.6.2_NATIVE_NARROW_8PX_REAL_TEXT_PROOF.zip
```

Expected visual:

```text
Chọn tướng
```

### Why only 8 custom narrow glyphs

Unique visible glyph units are:

```text
C h ọ n t ư ớ g
```

ASCII space remains byte `0x20`; Gaia already handles it as native narrow space with 8px advance.

### Temporary proof aliases

0.6.6.2 intentionally does NOT add the production half-width codepage yet. It temporarily borrows eight direct native narrow ASCII owners selected from:

```text
# $ & ' ( ) * + " Z X
```

Hard-excluded owner classes:

```text
!      punctuation risk
%      format-token risk (%d / %s)
- ,    punctuation/control risk
. /    punctuation/path risk
```

### Built-in safety gate

Before any ROM output, the builder scans plausible zero-terminated CP932 strings in CLEAN PRGPACK + SLPS, excluding font/mapping binary regions.

For each candidate owner it records actual one-byte text-token hits.

If fewer than eight owners are text-unused:

```text
[BLOCKED]
```

then:

```text
NO BIN/CUE is created
GaiaMaster_0.6.6.2_NATIVE_NARROW_GATE_REPORT.txt is created
```

User should send that report. No emulator test.

If eight safe owners are found, builder:

1. derives native 12x12 base glyphs;
2. applies 0.6.6.1-style baseline-preserving Vietnamese marks;
3. compresses width 12 -> 6;
4. writes only each selected 3-byte half per row, preserving the paired half;
5. writes one-byte Character Select proof bytes;
6. rebuilds nested/top BDP checksums + raw CD EDC/ECC;
7. outputs `[VI 0.6.6.2 NATIVE NARROW 8PX].bin/.cue/.txt`.

No renderer instruction is modified.

## Runtime gate for 0.6.6.2

Only if CMD prints `[OK]`:

1. boot generated `[VI 0.6.6.2 NATIVE NARROW 8PX].cue`;
2. go only to Character Select;
3. expected visual = `Chọn tướng`;
4. expected spacing = clearly tighter than 0.6.6.1, native ~8px advance;
5. stop immediately on freeze/global corruption;
6. send screenshot + generated TXT if glyph art is wrong;
7. never blindly retest a failed build.

If CMD prints `[BLOCKED]`, do not boot anything; send `GaiaMaster_0.6.6.2_NATIVE_NARROW_GATE_REPORT.txt`.

## Next after 0.6.6.2 PASS

Temporary ASCII aliases are proof-only and must not become production encoding.

Production sequence:

1. validate unused true one-byte half-width code candidates in `0xA1..0xDF` (avoid `0xDE/0xDF` composition semantics and any source-used codes);
2. patch the existing remap table at RAM `0x8007E01C` / corresponding SLPS data-side only;
3. freeze deterministic Vietnamese 6x12 codepage;
4. inventory full `vi_full` character set from Translation Master;
5. generate complete compact Vietnamese glyph bank;
6. integrate codepage encoder into Translation Master rebuild;
7. migrate real translated rows in batches.

## Hard do-not-repeat

- no Krom path;
- no production 12x16;
- no failed 0.6.3.x retests;
- no composite X/Y tuning loop;
- no `0.6.5.2` runtime pointer redirect;
- no global `state+0x3C/+0x3E/+0x40` mutation;
- no global cursor or cached-advance hook;
- never use `SLPS+0x5C0E0..<0x5C2B8` as code cave;
- do not treat `0xE0..0xFC` as private one-byte code space;
- no `%` narrow slot reuse;
- no runtime test when the 0.6.6.2 safety gate says BLOCKED;
- stop immediately on freeze/global corruption.

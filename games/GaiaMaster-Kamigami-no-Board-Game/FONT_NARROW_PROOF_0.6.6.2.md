# Gaia Master — 0.6.6.2 Native Narrow 8px Real-Text Proof

Date: **2026-09-13**

## Why this pivot exists

`0.6.6.1 BASELINE-NORMALIZED` already proves the real Vietnamese sentence `Chọn tướng` can render correctly through the native 12x12 mapping pipeline, but horizontal advance is too wide because those codes are classified as Japanese full-width glyphs.

The read-only spacing and narrow-bank reverse work established a better path than a renderer hook.

## Native narrow bank — proven

FontNarrowBankScanner 0.1 found Gaia's built-in narrow font bank:

```text
RAM        0x8006BAAC
SLPS       0x5C2AC
geometry   6x12 / 4bpp
row bytes  3 bytes per glyph half
packing    two 6px glyphs share each 72-byte pair block
```

Renderer behavior:

```text
native narrow copy -> return 8
cache miss         -> advance = state+0x3E
state+0x3E         -> 8 px for Character Select narrow class
```

The scanner recovered 15 reachable narrow indices (`0..14`).

## Code-cave route rejected

The previous only zero/NOP-run candidate ended at:

```text
SLPS+0x5C2B8
```

but the native narrow bank begins at:

```text
SLPS+0x5C2AC
```

Therefore that candidate overlaps actual font data and is **not a code cave**. Do not place executable code there.

This removes the need for the previously considered private-cache/advance hook.

## 0.6.6.2 proof design

Goal:

```text
Chọn tướng
```

Use Gaia's native one-byte/narrow path directly.

Unique custom visible glyphs:

```text
C h ọ n t ư ớ g
```

ASCII space remains native byte `0x20`, which already has a native narrow-space advance, so only **8** custom narrow glyphs are needed.

For this proof, the builder temporarily aliases eight direct ASCII narrow owners selected from a conservative candidate set:

```text
# $ & ' ( ) * + " Z X
```

Hard exclusions:

```text
!      common punctuation risk
%      format-token risk (%d / %s)
- ,    punctuation/control-text risk
. /    punctuation/path risk
```

## Built-in safety gate

The builder scans plausible zero-terminated CP932 strings in CLEAN `PRGPACK.BDP` and `SLPS_020.75` before making any output.

It excludes the binary font/mapping regions themselves from this scan.

For each candidate native narrow owner it checks whether that original one-byte character appears as a real token inside plausible text.

If fewer than eight candidate owners have zero text hits:

```text
[BLOCKED]
```

and **no BIN/CUE is created**.

The builder instead writes:

```text
GaiaMaster_0.6.6.2_NATIVE_NARROW_GATE_REPORT.txt
```

This makes the runtime test conditional on a local safety proof from the user's exact CLEAN BIN.

## Glyph generation

Each target glyph starts from Gaia's existing full-width native lowercase/capital base glyph.

Pipeline:

```text
native 12x12 base
 -> 0.6.6.1 baseline-preserving accent placement
 -> horizontal 12px -> 6px compression
 -> write only that 3-byte half per row in the native narrow bank
```

The paired neighboring narrow half is preserved.

No main atlas pointer or runtime font pointer changes.

## Architecture

```text
one-byte alias code
 -> Gaia original one-byte renderer path
 -> native 6x12 source
 -> original narrow copy
 -> copy_return = 8
 -> original cached 8px advance
```

No changes to:

- renderer instructions;
- cache code;
- cursor code;
- global tracking;
- `state+0x3C/+0x3E/+0x40`;
- runtime font pointers.

## Runtime gate

Only if the builder prints `[OK]` and creates the generated CUE:

1. boot the generated CUE;
2. go only to Character Select;
3. expected line is `Chọn tướng`;
4. spacing should be visibly tighter than `0.6.6.1`, around native 8px advance;
5. stop immediately on freeze/global corruption;
6. on a visual mismatch, send screenshot + generated report and do not blindly retest.

## If 0.6.6.2 passes

Do **not** keep the temporary ASCII aliases as production encoding.

Next production step:

1. allocate genuinely private one-byte half-width codes from the `0xA1..0xDF` class after text-use validation;
2. patch Gaia's existing one-byte remap table (`0x8007E01C`) data-side;
3. freeze a deterministic Vietnamese narrow codepage;
4. inventory the full `vi_full` character set;
5. grow the compact Vietnamese 6x12 glyph set;
6. integrate it with Translation Master rebuild.

## Hard do-not-repeat

- no code-cave injection near `0x5C2AC`;
- no global cached-advance patch;
- no production 12x16;
- no pointer redirect;
- no composite overlay;
- no reuse of `%` slot for Vietnamese glyphs;
- no runtime test if the builder safety gate says BLOCKED.

# Gaia Master — 0.6.6.2b NATIVE NARROW 8PX STRICT-GATE PROOF

Date: 2026-09-13

## Why 0.6.6.2b exists

`0.6.6.2` never reached runtime. Its safety gate blocked before producing BIN/CUE because the scanner accepted many binary-looking zero-terminated byte runs as plausible CP932 text.

Examples from the gate report included strings like:

```text
62R#eUReVR"T"WTV
wp&#"a
s&qﾟ
```

These are false-positive text detections.

Therefore:

```text
0.6.6.2 = BUILD GATE FALSE POSITIVE
NO RUNTIME CONCLUSION
DO NOT RETEST THE OLD PACKAGE
```

## Confirmed real-text owners removed

Manual review of Translation Master confirms these direct narrow owners are genuinely used by game text and must not be borrowed:

```text
(  )   -> (速い者順)
+      -> 通行税 %+3d％
```

Already excluded from the earlier design:

```text
!      punctuation risk
%      format token
, -    punctuation/control risk
. /    punctuation/control-code risk
```

## 0.6.6.2b diagnostic owner set

The remaining eight direct narrow owners are:

```text
"  #  $  &  '  *  Z  X
```

These provide exactly eight narrow indices for the unique visible units in:

```text
Chọn tướng
```

Space remains native byte `0x20` and already uses the narrow 8px advance.

## Strict gate change

The old classifier accepted any ASCII-ish run with two alphabetic characters. This admitted binary garbage.

0.6.6.2b now classifies text conservatively:

1. any decoded string containing Japanese characters is real text;
2. ASCII-only text counts only when it looks like a compact uppercase UI/debug label;
3. mixed-case random binary runs are ignored;
4. font/mapping binary regions remain excluded.

If any of the eight selected owners is still seen in real text, the builder prints:

```text
[BLOCKED]
```

and does not create BIN/CUE.

## Renderer remains untouched

0.6.6.2b is still data-only:

```text
native 6x12 narrow glyph data
+ Character Select proof bytes
+ BDP checksum rebuild
+ CD EDC/ECC rebuild
```

No renderer hook.
No code cave.
No cursor/cache patch.
No 12x16.
No pointer redirect.

## Important reverse finding for future scale

At `0x8003C3E8` the renderer chooses the native narrow path with:

```asm
sltiu v0,a1,15
```

The narrow source formula is:

```text
source = 0x8006BAAC
       + 3 * ((index & ~1) * 12)
       + 3 * (index & 1)
```

Index 16 would land exactly at the main atlas base:

```text
0x8006BAAC + 576 = 0x8006BCEC
```

Because one native 12x12 / 72-byte cell is naturally two 6x12 / 36-byte halves, the main atlas can theoretically be interpreted as a much larger narrow source space.

This is a promising production direction, but it is **not yet approved for runtime**. Raising the `<15` threshold globally would reclassify normal ASCII/table entries and can break existing text. A selective private-code route must be reverse-designed first.

## Runtime gate

Only if builder prints `[OK]`:

1. boot generated `[VI 0.6.6.2b NATIVE NARROW 8PX].cue`;
2. go only to Character Select;
3. expected text: `Chọn tướng`;
4. expected horizontal advance: clearly tighter than 0.6.6.1, about native 8px;
5. stop immediately on freeze/global corruption;
6. send screenshot + generated TXT.

If `[BLOCKED]`, send:

```text
GaiaMaster_0.6.6.2b_NATIVE_NARROW_GATE_REPORT.txt
```

and do not boot anything.

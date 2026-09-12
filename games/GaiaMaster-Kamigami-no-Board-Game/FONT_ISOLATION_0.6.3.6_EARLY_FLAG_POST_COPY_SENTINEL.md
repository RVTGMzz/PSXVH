# Gaia Master — Font Isolation 0.6.3.6 EARLY-FLAG POST-COPY RAM SENTINEL

Prepared: **2026-09-12**
Status: **BUILT / awaiting runtime result**

## Why this probe exists

0.6.3.5 attempted to overwrite converted RAM rows 10..15 after `0x8003C67C` with obvious horizontal sentinel bands, but runtime showed neither band.

That build identified the target at the late hook with:

```text
s0 & 0xFFFF == 0x889F
```

At `0x8003CC4C`, `s0` is not proven to still contain the original Shift-JIS character code.

Therefore 0.6.3.5 did not answer the clipping question.

## 0.6.3.6 design

Keep the exact same stable extended-height geometry and sentinel question, but make target identity persistent.

### Early flag

At the metadata hook around the custom glyph tail, where `s0` is already proven trustworthy:

```text
0x889F -> FLAG = 1
other glyph -> FLAG = 0
```

The flag is a dedicated 32-bit runtime word in the already-used executable safe-cave region.

### Late hook

At:

```text
0x8003CC4C
```

the post-copy hook reads FLAG only.

It never inspects `s0`.

For FLAG=1:

```text
rows 10..11 = 0x77 nibbles across full 8-byte converted row
rows 12..15 = 0x11 nibbles across full 8-byte converted row
```

This gives:

- dark/gray 2-row control band;
- bright white 4-row test band.

## Unchanged from stable path

- control: `ＴＥＳＴ亜`;
- target 12x16 / 96-byte source;
- target copy height = 16 rows;
- target visible sprite height = 16;
- baseline Y `-4`;
- target at end-of-line;
- no UV +4;
- no shared cache allocator/cursor rewrite;
- no patch to `0x8003CD94..0x8003CDB4`.

## Interpretation

### A — gray + white both visible

Rows 12..15 survive converted RAM -> VRAM -> sprite.

Then the old lower-row loss is not downstream clipping; focus on source/copy glyph data construction.

### B — gray control visible, white bottom absent

Rows 10..11 survive display but rows 12..15 are lost after converted RAM.

Focus on post-copy cache/upload/draw geometry.

### C — neither visible

Even with reliable early target identity, the assumed current converted destination or hook placement is not the visible target path.

Do not infer clipping.

## Safety

Builder performs explicit cave-layout checks:

- META cave fits its 0x60-byte slot;
- SENT cave does not overlap FLAG;
- FLAG remains before the static atlas;
- entire used cave/flag region must be zero-filled in the clean/Alpha 0.6.1 baseline before patching.

## Package

```text
GaiaMaster_FontIsolation_0.6.3.6_EARLY_FLAG_POST_COPY_SENTINEL.zip
```

Launcher:

```text
00_RUN_PROBE_0636.cmd
```

Test only Character Select and send one screenshot of the final target glyph.

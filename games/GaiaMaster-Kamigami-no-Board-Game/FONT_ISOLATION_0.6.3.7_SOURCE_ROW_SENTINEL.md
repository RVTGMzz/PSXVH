# Gaia Master — Font Isolation 0.6.3.7 SOURCE ROW SENTINEL

Prepared: **2026-09-12**
Status: **BUILT / awaiting runtime result**

## Why this probe exists

0.6.3.5 tried to write post-copy sentinel rows but relied on late-stage `s0` target identity; sentinel was not observed.

0.6.3.6 tried a persistent early target FLAG and caused an immediate freeze after Sony logo.

Therefore 0.6.3.7 removes both risky mechanisms.

## Design

Start from the stable extended-height path:

- target source = 12x16 / 96 bytes;
- target metadata/copy height = 16 rows;
- target visible sprite height = 16;
- baseline Y -= 4;
- target at end-of-line;
- no UV+4;
- no shared cache allocator rewrite;
- no post-copy hook;
- no late `s0` target check;
- no persistent/global FLAG.

The diagnostic is baked directly into the unique target source glyph:

```text
source rows 10..11 = palette index 7 across full width
source rows 12..15 = palette index 1 across full width
```

Expected visual meaning:

```text
rows10..11 -> dark/gray control band
rows12..15 -> bright white test band
```

## Interpretation

### A. Gray + white both visible

Rows12..15 survive the full path:

```text
source -> 0x8003C67C copy -> converted cache -> VRAM -> sprite
```

Then the old lower-E loss is related to source glyph construction/content rather than a hard 12-row downstream truncation.

### B. Gray visible, white absent

Rows10..11 survive but 12..15 do not.

=> structural lower-row loss is confirmed somewhere in source/copy/cache/upload/display.

### C. Neither visible

The assumed extended source/slot/copy path is not feeding the visible target the way current reverse expects.

=> reverse the actual target source pointer / slot layout before another runtime probe.

## Safety

0.6.3.7 introduces no new mutable runtime state and no new hook beyond the previously stable 16-row metadata/sprite/baseline path.

Stop immediately on unrelated text corruption or freeze.

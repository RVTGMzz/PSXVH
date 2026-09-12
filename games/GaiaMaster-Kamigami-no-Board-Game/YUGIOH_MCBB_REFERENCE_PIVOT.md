# Gaia Master — reference study: Yu-Gi-Oh! MCBB Vietnamese PS1 patch

Reference repo:

`https://github.com/2ez4gcx/yugioh-mcbb-vi-patch`

## What the public repo actually proves

The public repository is release-oriented: it contains a PPF3 patch, a Python patch applier, README, and screenshots. It does not publish the author's development/reverse-engineering source.

The README explicitly states that the release patch contains:

- Vietnamese translated text;
- a redrawn font;
- a few code-adjustment bytes;
- a Vietnamese character page on the creature naming screen.

Therefore we cannot claim the author used any specific renderer hook/compositing implementation from the public source. However, it is strong evidence that a complete Japanese PS1 -> Vietnamese result can be achieved with targeted font/code changes rather than a large renderer redesign.

## Strategic lesson for Gaia Master

Gaia already has several pieces that Yu-Gi-Oh-style minimal patching would need:

- native custom atlas replacement works (0.6.2.13);
- native 12x12 cache/VRAM path is stable;
- target-only descriptor Y shift has worked without global corruption;
- full-size native E body already has correct game shading/style.

The expensive part of the 0.6.3.x branch has been trying to enlarge one native cache cell from 12 rows to 16 rows. That crosses source stride, converted-cache stride, Y cursor, page placement, sprite geometry and shared allocator state.

A lower-risk alternative is **composite accent rendering**:

1. Render the base Latin glyph normally using native 12x12 geometry.
2. Render a second 12x12 glyph containing only Vietnamese accent pixels.
3. Move that second sprite backward in X so it overlaps the base letter.
4. Move it upward/downward in Y to provide real headroom/footroom outside the base cell.
5. Keep all source/cache/VRAM cells native 72-byte/12-row.

This is NOT a claim that the Yu-Gi-Oh patch uses this exact implementation. It is a Gaia-specific design inspired by the minimal-patch evidence from that successful PS1 Vietnamese release.

## 0.6.4.0 proof concept

Internal Character Select text:

`ＴＥＳＴＥ亜`

- native `Ｅ` renders unchanged;
- `亜` slot is replaced by an accent-only `mũ + sắc` glyph;
- target overlay descriptor gets `X -= 12`, `Y -= 4`;
- visually expected result: `ＴＥＳＴẾ`.

No extended-height glyph.
No 96-byte source.
No cache-stride mutation.
No CD94 allocator rewrite.
No sprite-height rewrite.
No persistent flag.

If this proof works, 12x16 reverse becomes optional/background research rather than the production blocker.

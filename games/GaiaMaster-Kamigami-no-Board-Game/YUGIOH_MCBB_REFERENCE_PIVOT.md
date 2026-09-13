# Gaia Master — reference study: Yu-Gi-Oh! MCBB Vietnamese PS1 patch

Reference repo:

`https://github.com/2ez4gcx/yugioh-mcbb-vi-patch`

## What the public repo proves

The public repository is release-oriented. It contains:
- `yugioh-mcbb-vi.ppf`;
- `apply_patch.py`;
- README;
- screenshots.

It does **not** publish the author's development/reverse-engineering source.

The README explicitly says the release patch contains:
- Vietnamese translated text;
- a redrawn font;
- a few code-adjustment bytes;
- a Vietnamese character page on the creature naming screen.

The user also supplied the release `yugioh-mcbb-vi.ppf` for study during the Gaia session.

We must not claim the author used any exact Gaia-specific mechanism. The valuable evidence is architectural:

> a finished Japanese PS1 -> Vietnamese patch can remain close to the game's native rendering model and succeed through targeted font/resource/data/code changes.

## What Gaia should take from this

Gaia already has stable native-font evidence:
- custom atlas replacement PASS at 0.6.2.13;
- native 12x12 / 72-byte / 4bpp path is stable;
- broad renderer geometry changes repeatedly created shared-state problems.

Therefore the preferred Gaia production strategy is now:

1. keep native renderer geometry;
2. create Vietnamese glyphs inside native 12x12 cells using one unified cap-height/style system;
3. assign those glyphs to unused Japanese atlas slots;
4. patch the code->glyph mapping data directly when ownership is proven;
5. keep runtime code changes minimal and only if data-only mapping proves impossible.

## Historical composite experiment

0.6.4.x tested a Gaia-specific idea where accents were rendered as a second sprite over a native base letter.

It was useful as an art experiment, but runtime placement did not remain reliable enough across Gaia's render/cache paths. Composite is therefore **not** the current production direction.

Do not attribute composite rendering to the Yu-Gi-Oh patch.

## Current Gaia pivot

See:

`FONT_MAPPING_PIVOT_0.6.5.md`

Current goal:

```text
Vietnamese/internal code
  -> mapping table entry
  -> chosen unused Japanese glyph slot
  -> native 12x12 / 72-byte Vietnamese glyph
```

Current work is read-only mapping-table recovery before any new runtime probe.

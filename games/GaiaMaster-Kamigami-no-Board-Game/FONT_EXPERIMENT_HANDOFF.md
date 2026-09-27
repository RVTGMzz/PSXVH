# FONT EXPERIMENT HANDOFF

Branch: `gaia-new-vietnamese-font-experiment-01`

Purpose: replace Gaia Master's patched-looking Vietnamese font with a coherent newly designed Latin/Vietnamese family.

Do not edit the canonical B52 branch for artwork experiments.

Phase NF1 keeps:
- 12x12
- 72 bytes/glyph
- 4bpp LOW-nibble-first
- current renderer/static mapping

But NF1 must not reuse native glyph pixel bodies as the visual source.

First task:
- map all Latin/digit/punctuation glyph slots actually used by the translation;
- define complete new-font coverage;
- build preview/contact sheet before any ROM patch.

Only after NF1 artwork is proven visually may NF2 investigate VWF/per-glyph advance.

Overall Runtime PASS remains NO.

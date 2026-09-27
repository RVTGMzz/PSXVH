# NF1 V0.3 - Reference Metrics / VWF Preparation

Date: 2026-09-28

## New visual evidence

Two runtime screenshots were supplied from the Yu-Gi-Oh PS1 Vietnamese patch:

Vietnamese:
- Hoàng tử ơi!
- Người lại ra phố
- chơi bài nữa sao!?

Original English:
- Your duellist code has
- been recorded.

Measured visible bright-glyph bands are approximately 21-23 screenshot pixels high in both images. The Vietnamese font therefore tracks the original font's vertical metrics closely rather than using oversized accent cells.

The screenshots also reinforce the value of per-glyph horizontal metrics: narrow glyphs remain compact while Vietnamese accents do not force every character into an exaggerated wide visual cell.

## NF1 V0.3 action

Add width metadata to the complete V0.2 source font without patching the game renderer yet.

New tool:

`tools/gaia_nf1_v03_width_metrics.py`

It provides:
- ink-width measurement from each 12x12 source glyph;
- a proposed per-glyph advance table;
- special compact advances for narrow punctuation/letters;
- wider advances for naturally wide glyphs;
- a proportional preview containing both Vietnamese and English reference sentences;
- CSV output for future NF2 renderer work.

This is **design metadata only**.

It does not claim Gaia currently honors these widths.

## Why this comes before an NF2 runtime hook

Historical Gaia experiments show renderer/cache/pointer changes can freeze or corrupt runtime state.

Therefore:
1. settle full charset artwork;
2. settle width metrics offline;
3. use screenshots to approve the visual result;
4. only then reverse/prove the smallest safe way to feed per-glyph advance into Gaia.

## Runtime architecture status

Current NF1 build remains:
- native 12x12;
- static mapping;
- fixed native advance;
- no renderer hook.

NF2 goal, if pursued:
- keep the new full font source;
- add only the smallest proven per-glyph advance mechanism;
- do not repeat old global cache-stride or pointer-redirection patches.

Overall Runtime PASS remains NO.

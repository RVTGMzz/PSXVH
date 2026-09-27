# NF1 V0.2 - Full Vietnamese Charset Plan

Date: 2026-09-28
Branch: gaia-new-vietnamese-font-experiment-01

## Goal

NF1 V0.1 was enough for the current translation corpus, but it was not a complete reusable Vietnamese font.
V0.2 separates font-source completeness from current runtime slot capacity.

## Full source inventory

- 95 printable ASCII characters, space through tilde
- 67 uppercase Vietnamese non-ASCII precomposed letters
- 67 lowercase Vietnamese non-ASCII precomposed letters
- total source glyphs: 229
- Vietnamese non-ASCII glyphs: 134

## Runtime capacity gap

The currently proven mapping-only custom allocation contains:

- 60 production custom slots
- 4 reserve custom slots
- 64 proven-safe custom slots total

A full Vietnamese non-ASCII runtime codepage needs 134 custom glyph destinations.

Current proven-safe shortage: 70 slots.

This is a storage/mapping limitation, not an artwork limitation.

## V0.2 rule

From V0.2 onward:

- artwork/source charset stays complete
- runtime mapping is a separately proven subset/capacity problem

Do not shrink the source font back to the current 60 glyphs just to fit the old allocation.

## What NF1 can still do safely

- replace full-width ASCII/Latin/digit/punctuation artwork in their already-mapped native slots
- replace the existing 60 custom Vietnamese glyphs in their proven slots
- keep renderer geometry 12x12 / 72-byte / 4bpp unchanged
- avoid renderer hooks while evaluating the visual family

## What NF2 must solve

To make all 134 Vietnamese non-ASCII glyphs available at runtime, prove one of:

1. more reclaimable atlas slots through whole-game usage evidence;
2. a separate custom font bank/codepage;
3. another renderer-owned storage path with sufficient capacity.

The historical 8x15 custom-bank experiment proves Gaia can be redirected to a separate font source, but old global renderer/cache mutations were not production-safe. NF2 must not replay those unsafe patches.

Overall Runtime PASS remains NO.

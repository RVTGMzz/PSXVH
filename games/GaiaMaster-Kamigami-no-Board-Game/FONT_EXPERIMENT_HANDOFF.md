# FONT EXPERIMENT HANDOFF

Updated: 2026-09-28

Branch: `gaia-new-vietnamese-font-experiment-01`
Parent/canonical reverse branch: `gaia-character-select-font-atlas-reverse-01`

## Purpose

Replace Gaia Master's patched-looking Vietnamese font with a coherent newly designed Latin/Vietnamese family.

Do not edit the canonical B52 branch for artwork experiments.

## NF1 V0.1 current state

Implemented:

- `tools/gaia_nf1_new_font_art.py`
- `tools/00_PREVIEW_NF1_NEW_FONT.cmd`
- `tools/build_gaia_nf1_new_font.py`
- `tools/00_BUILD_NF1_NEW_FONT.cmd`
- `tools/gaia_nf1_glyph_coverage.py`
- `tools/00_RUN_NF1_GLYPH_COVERAGE.cmd`

Artwork coverage:

- A-Z: 26
- a-z: 26
- digits: 10
- frozen Vietnamese custom set: 60
- total newly drawn glyphs: **122**

The glyph bodies are newly authored pixel patterns. They do not reuse native Gaia glyph shapes.

Current style:

- 1-pixel foreground strokes
- no synthetic shadow layer
- compact retro PS1 pixel look
- dedicated `Đ/đ`
- dedicated horn forms for `Ơ/ơ/Ư/ư`
- separate structural/tone lanes
- dot-below on row 11

## Runtime architecture retained for NF1

NF1 intentionally keeps:

- native 12x12 cells
- 72 bytes/glyph
- 4bpp LOW-nibble-first
- current mapping table
- no renderer hook
- no pointer redirect
- no cache-stride change

Reason: old 8x15 / extended-height / pointer-redirect experiments proved renderer/cache mutation can be unsafe. NF1 isolates **art quality** from renderer engineering.

## Authoring validation

Executed successfully on the authored tools:

- `NF1 NEW FONT ART SELFTEST PASS glyphs=122`
- `NF1 NEW FONT BUILDER SELFTEST PASS glyphs=122`
- SVG contact-sheet generation succeeded

These are tooling/static checks only.

## Guarded B52R14R1 builder

Input required:

`0ced9982e1b00566b42ace047236378826c2aa1c`

Builder behavior:

1. verifies exact whole-BIN SHA1;
2. reads SLPS from raw MODE2/2352 image;
3. resolves full-width Latin/digit slots from Gaia's own mapping table;
4. aborts on duplicate Latin mappings;
5. aborts if any Latin/digit slot overlaps the frozen 60 Vietnamese slots;
6. derives the foreground palette index from the existing native A only as a palette/color reference;
7. installs all 122 newly drawn glyphs;
8. writes only changed SLPS sectors to a copied output BIN;
9. regenerates MODE2/Form1 EDC/ECC;
10. requires PRGPACK byte-for-byte unchanged;
11. rereads all 122 glyphs and requires exact byte match;
12. creates a matching CUE.

Input BIN is never overwritten.

## User test flow

### Preview first

Run:

`tools/00_PREVIEW_NF1_NEW_FONT.cmd`

No ROM is needed. It creates and opens:

`font_experiment/NF1_FONT_PREVIEW.svg`

Judge mainly:

- lowercase body style
- `Đ/đ`
- `ă/â/ê/ô/ơ/ư`
- `ấ/ế/ố`
- `ẫ/ễ/ỗ`
- `ạ/ệ/ộ/ự/ỵ`

### Runtime build

Only if preview is acceptable:

Drag exact B52R14R1 BIN onto:

`tools/00_BUILD_NF1_NEW_FONT.cmd`

Expected output next to the BIN:

- `[NF1 NEW VI FONT].bin`
- matching `.cue`
- `GaiaMaster_NF1_NEW_FONT_BUILD_REPORT.txt`

## Runtime proof required

Static build success is not Runtime PASS.

Minimum screenshots:

1. one translated dialogue line with lowercase Vietnamese;
2. one line containing `Đ/đ`;
3. one horn family example `ơ/ư`;
4. one stacked accent example such as `ế/ố`;
5. one ordinary ASCII/Latin line to judge family consistency.

## NF2 gate

Do not start VWF yet.

Open NF2 only if:
- NF1 artwork is visually good;
- runtime is stable;
- fixed 12-pixel advance is clearly the remaining visual limitation.

Then investigate per-glyph width/advance separately.

Overall Runtime PASS remains **NO**.

# Gaia Master - New Vietnamese Font Experiment 01

Date: 2026-09-27
Branch: `gaia-new-vietnamese-font-experiment-01`
Parent: `gaia-character-select-font-atlas-reverse-01`

## Decision

Stop visually polishing the old Vietnamese glyph construction.

The old production line remains preserved on the parent branch. This experimental branch treats the old atlas only as a **binary format/runtime contract**, not as artwork to imitate.

## Visual goal

Create a coherent new Latin/Vietnamese font family from scratch:

- thin/clean PS1-era pixel strokes;
- high legibility at 1x and on Steam Deck;
- consistent cap height, x-height and baseline;
- `Đ/đ` designed as real letters, not generic bars added to D/d;
- `Ă/Â/Ê/Ô/Ơ/Ư` designed with dedicated headroom;
- tone marks aligned by family, not bolted onto arbitrary native bodies;
- no fake bold/shadow look;
- no accent/body collisions;
- all Vietnamese forms share the same visual DNA as unaccented Latin.

## Technical Phase NF1

First experiment keeps the proven runtime format:

```
12x12 cell
72 bytes per glyph
4bpp
LOW nibble first
static mapping
```

But the **artwork is new**.

Why keep the format first:
- separates font quality from renderer risk;
- proves whether a clean font alone is enough;
- keeps rollback trivial;
- does not mix a renderer hook with the unresolved B52 live-UI reverse.

## Scope change from the old 60-glyph patch

The old line only custom-built the 60 Vietnamese glyphs required by the translation corpus.

NF1 must instead treat the font as a family.

Target families:
- A-Z
- a-z
- 0-9
- common punctuation used by the translation
- complete Vietnamese precomposed alphabet required by corpus
- reserve glyphs for future translation growth

The existing native glyphs may be used only to identify slot/mapping/runtime behavior. Their pixel shapes are not the new design source.

## Two-stage architecture

### NF1 - New artwork, old renderer

Goal:
- replace the visible Latin/Vietnamese family while retaining 12x12 and existing renderer behavior;
- no VWF hook yet;
- no pointer redirect;
- no live-UI source assumptions;
- compare screenshots against the old font.

PASS criteria:
- readable at native resolution;
- accents are visually distinct;
- no clipping/collision;
- ordinary Latin and accented Vietnamese look like one family;
- no regression in unrelated Japanese/system glyphs needed by the game.

### NF2 - Optional VWF renderer experiment

Open NF2 only if NF1 proves:
- glyph artwork is good;
- fixed 12-pixel advance is the remaining visual limitation.

NF2 may investigate:
- per-glyph width table;
- variable cursor advance;
- spacing/kerning rules;
- larger or differently packed font atlas if required.

NF2 is a separate runtime/code experiment and must not be silently merged into NF1.

## Safety contract

The canonical B52 branch remains untouched.

This branch must never claim:
- Runtime PASS from a generated preview;
- VWF compatibility before renderer proof;
- remaining Japanese UI ownership from font work.

Any ROM build remains output-copy only with exact input hash + EDC/ECC regeneration.

## Immediate next implementation

1. inventory every currently rendered Latin/digit/punctuation mapping and atlas slot;
2. freeze the exact glyph set actually needed by the current Vietnamese corpus;
3. create a new-font source format independent of native glyph artwork;
4. render a contact-sheet preview before writing any ROM bytes;
5. make one reversible NF1 runtime build for a small visible test phrase;
6. compare old vs new screenshots;
7. expand only after the family passes visually.

## Reference lesson

The public `2ez4gcx/yugioh-fm-vi-patch` release demonstrates that a PS1 Vietnamese localization can ship with a redrawn font and variable character widths.

Its public repository does not expose the underlying renderer/font build source, so Gaia must independently prove its own renderer path.

## Current status

Branch created.

New-font artwork implementation: **NF1 V0.1 READY FOR PREVIEW / GUARDED BUILD**.

Implemented:
- `tools/gaia_nf1_new_font_art.py`
- `tools/00_PREVIEW_NF1_NEW_FONT.cmd`
- `tools/build_gaia_nf1_new_font.py`
- `tools/00_BUILD_NF1_NEW_FONT.cmd`

NF1 V0.1 artwork coverage:
- 26 uppercase Latin
- 26 lowercase Latin
- 10 digits
- 60 frozen Vietnamese custom glyphs
- total: **122 newly drawn glyphs**

Artwork characteristics:
- independent 5x7-derived pixel family placed inside the proven 12x12 cell;
- one-pixel foreground strokes;
- no native glyph-body reuse;
- no synthetic shadow layer;
- dedicated `Đ/đ` construction;
- dedicated horn for `Ơ/ơ/Ư/ư`;
- structural/tone separation for circumflex/breve combinations;
- dot-below uses the bottom row.

Authoring checks completed:
- `NF1 NEW FONT ART SELFTEST PASS glyphs=122`
- `NF1 NEW FONT BUILDER SELFTEST PASS glyphs=122`
- preview SVG generation succeeded.

Guarded builder behavior:
- accepts **only** exact B52R14R1 SHA1 `0ced9982e1b00566b42ace047236378826c2aa1c`;
- resolves full-width Latin/digit mappings from the actual SLPS mapping table;
- aborts on duplicate mappings or collision with the 60 frozen Vietnamese slots;
- patches only SLPS font bytes;
- requires PRGPACK byte-for-byte unchanged;
- regenerates MODE2/Form1 EDC/ECC;
- rereads all 122 destination glyphs before reporting static PASS;
- never overwrites the input BIN.

Real B52R14R1 build execution: **PENDING on user-side exact BIN**.
Runtime screenshot: **PENDING**.
Canonical B52 line: unchanged.
Overall Runtime PASS: **NO**.

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


## NF1 V0.1 artwork locked

User reviewed the generated contact sheet and accepted the direction as visually good enough to proceed.

Therefore:
- treat NF1 V0.1 artwork as the current baseline;
- do not continue speculative glyph polishing before runtime;
- next authority is in-game screenshots, not more offline tweaking.

Runtime checklist:
`NF1_V01_RUNTIME_TEST.md`

Known useful existing translated targets:
- `Thế giới đổi chủ`
- `Đã ổn?`
- `Chọn tướng`
- `Nhấn O`

These cover lowercase, uppercase Đ, đ, ã, ọ, ư, ấ and ordinary Latin without adding synthetic test text.


## NF1 V0.2 reference pivot - complete Vietnamese screenshot

User supplied a complete Vietnamese pixel-font screenshot and prefers it over the NF1 V0.1 contact sheet.

Decision:
- NF1 V0.1 remains a technical proof only;
- it is no longer the final visual target;
- NF1 V0.2 uses the supplied screenshot as the visual reference for thin strokes, accent spacing, baseline and charset completeness.

Image analysis note:
- the supplied screenshot is nearest-neighbor enlarged on a clean 3x pixel grid;
- therefore bitmap tracing/reconstruction is feasible without guessing anti-aliased contours.

V0.2 source inventory target:
- 95 printable ASCII glyphs;
- 67 uppercase Vietnamese non-ASCII glyphs;
- 67 lowercase Vietnamese non-ASCII glyphs;
- 229 source glyphs total.

Current proven mapping-only custom capacity is 64 slots, so complete 134-glyph Vietnamese runtime coverage exceeds the proven custom capacity by 70 slots.

Therefore:
- source artwork must stay complete;
- runtime storage/codepage expansion becomes NF2 work;
- do not reduce the source inventory back to 60 just to fit the old atlas allocation.


## NF1 V0.3 proportional metrics

Additional user screenshots show:
- Vietnamese dialogue using the target reference font;
- original English dialogue using the game's native visual style.

The visible bright-text bands measure about 21-23 screenshot pixels high in both samples, so Vietnamese should preserve the original vertical rhythm rather than grow a visibly taller accent box.

New files:
- `tools/gaia_nf1_v03_width_metrics.py`
- `tools/00_PREVIEW_NF1_V03_VWF_METRICS.cmd`
- `NF1_V03_REFERENCE_METRICS.md`

V0.3 adds design-time per-glyph metrics to the 229-glyph V0.2 source:
- ink width;
- proposed advance width;
- compact widths for narrow glyphs/punctuation;
- wider metrics for naturally wide glyphs;
- proportional reference preview using both Vietnamese and English sample sentences.

Important:
- Gaia runtime does not honor V0.3 widths yet;
- V0.3 is preparation for a future NF2 VWF mechanism;
- do not patch renderer/cache/stride until a minimal safe hook is reverse-proven.

The target is now:
**complete Vietnamese charset + original-game-like vertical metrics + proportional spacing**, not merely "current corpus fits".


## NF2 cache-advance probe

Prepared read-only VWF reverse tooling:

- `tools/gaia_nf2_cache_advance_probe.py`
- `tools/00_RUN_NF2_CACHE_ADVANCE_PROBE.cmd`
- `NF2_CACHE_ADVANCE_PROBE.md`

Why this path matters:

Previous Gaia reverse already proved:
- cache-hit horizontal advance comes from `cache_record.byte6`;
- cache-miss advance comes from `state+0x3E` or `state+0x40 + 1`;
- optional tracking comes from `state+0x3C`.

NF2 therefore targets the **writer of cache_record+6**, not the global cursor/cache stride.

The probe:
- scans exact CLEAN/B52R14R1 SLPS for direct memory operations at offset `+6`;
- ranks writers/readers inside known cache hit/miss ranges;
- boosts candidates near `state+0x3C/+0x3E/+0x40`;
- prints local MIPS dataflow context;
- emits candidate CSV;
- generates a PCSX-Redux Lua capture that pauses before the highest-ranked `+6` write and records the source advance value.

Current status:
- tooling committed;
- real exact-B52R14R1 scan **PENDING**;
- runtime capture **PENDING**;
- no VWF ROM patch exists yet.

Promotion rule:
only after a runtime-correlated writer proves stable may NF2 replace/override the width value locally before cache byte6 is written.

Do not return to global cache-stride or pointer-redirection experiments.

## Superseded runtime action

Real B52R14R1 results showed the broad +6 writer ranking contains many unrelated struct/UI writes and no direct +6 write inside the cache-miss window. Do **not** use the original 8-breakpoint NF2 Lua for promotion evidence.

Use NF2R1 instead:

- `gaia_nf2r1_cache_fill_helper_probe.py`
- `GaiaMaster_NF2R1_PCSX_CACHE_FILL_CAPTURE.lua`

NF2R1 targets the verified cache-fill helper call at `0x8003CC38 -> 0x8003C67C` and compares the exact cache record before/after the helper.

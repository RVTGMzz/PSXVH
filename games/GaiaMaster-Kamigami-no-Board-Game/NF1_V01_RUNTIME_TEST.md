# NF1 V0.1 Runtime Test

Date: 2026-09-28
Branch: `gaia-new-vietnamese-font-experiment-01`

## Artwork decision

NF1 V0.1 contact-sheet artwork is accepted as the visual baseline.

Do not polish glyph shapes further until runtime screenshots show an actual problem.

## Build target

Input:

`B52R14R1 SHA1 = 0ced9982e1b00566b42ace047236378826c2aa1c`

Launcher:

`tools/00_BUILD_NF1_NEW_FONT.cmd`

Expected output:

- `[NF1 NEW VI FONT].bin`
- matching `.cue`
- `GaiaMaster_NF1_NEW_FONT_BUILD_REPORT.txt`

The build is font-only:
- SLPS font bytes may change;
- PRGPACK must remain byte-for-byte unchanged;
- no renderer hook;
- no pointer redirect;
- no text rewrite;
- no gameplay/code change.

## Runtime targets

Use a cold boot. Do not load an old save state created by another build.

Check these existing translated lines/screens when reachable:

1. Intro/front text containing **`Thế giới đổi chủ`**
   - checks lowercase family;
   - checks `ế`;
   - checks `đ`.

2. Character/select/setup line **`Đã ổn?`**
   - checks uppercase `Đ`;
   - checks `ã`.

3. Character/select/setup line **`Chọn tướng`**
   - checks `ọ`;
   - checks `ư`;
   - checks lowercase family spacing.

4. Character/select/setup line **`Nhấn O`**
   - checks stacked circumflex + acute `ấ`;
   - checks Latin O against Vietnamese artwork family.

5. Any visible line with `ơ`, `ư`, `ế`, `ố`, `ự` if encountered.

## Screenshot gate

Capture at least:
- one intro/dialogue screenshot;
- one Character Select/setup screenshot;
- one screenshot with a horn family glyph (`ơ/ư`);
- one screenshot with a stacked accent (`ấ/ế/ố`).

Judge:
- body readability;
- accent separation;
- baseline;
- clipping;
- whether plain Latin and Vietnamese glyphs look like one family;
- whether the fixed 12-pixel cell feels acceptably spaced.

## PASS meanings

### NF1 ART PASS
Artwork is visually acceptable in-game.

### NF1 RUNTIME STABLE
No freeze/corruption and unrelated UI remains normal during the tested path.

### Not yet VWF PASS
Fixed-width spacing is still the native renderer behavior. VWF is a later, separate NF2 experiment.

Overall Runtime PASS for the whole translation remains **NO** until broader gameplay validation exists.

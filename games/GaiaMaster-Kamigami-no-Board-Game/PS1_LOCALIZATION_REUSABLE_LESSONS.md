# PS1 localization — reusable lessons from Gaia Master

Updated: **2026-09-12**

This file records project-level knowledge that should be reused on future PS1 localization projects instead of rediscovering the same techniques from scratch.

## Why later PS1 projects should generally be easier

Gaia Master forced reverse-engineering across several layers at once:

1. raw MODE2/2352 sector patching;
2. EDC/ECC regeneration;
3. nested BDP archive checksums;
4. fixed-slot text replacement and overflow handling;
5. Shift-JIS / CP932 encoding behavior;
6. custom character-code -> glyph-index mapping;
7. static font atlas discovery;
8. glyph format / stride / packing;
9. renderer disassembly;
10. source glyph -> converted cache -> VRAM -> sprite pipeline;
11. target-only runtime probes;
12. distinguishing cosmetic glyph-art failure from structural renderer/cache failure.

Future PS1 projects can reuse this workflow even when offsets and engines differ.

The exact code is not portable, but the **reverse methodology is highly reusable**.

## Reusable workflow

### 1. Establish immutable baselines first

Always record:

- clean disc hash;
- executable hash;
- main archive hash;
- known-good translated alpha hash.

Never build later probes from an already-patched diagnostic ROM unless explicitly intended.

### 2. Prove text encoding before translation scale-up

Test:

- ASCII 1-byte;
- Shift-JIS / CP932;
- full-width Latin;
- control characters / terminators.

Gaia Master lesson:

```text
ASCII 1-byte = unsafe/mis-render
full-width CP932 Latin = runtime-safe
```

Do not assume Latin-looking text means ASCII is accepted.

### 3. Separate text storage from font rendering

A valid text replacement does not prove the renderer can display the desired glyph.

Reverse separately:

```text
text bytes
-> code mapping
-> glyph index
-> glyph source pointer
-> unpack/copy
-> converted cache
-> VRAM upload
-> primitive/sprite
```

### 4. Use visible, high-information probes

Prefer one Character Select / menu probe that answers one exact question.

Good examples:

- replace one known glyph;
- add a native sentinel immediately after target;
- place target at end-of-line to isolate overwrite;
- show several art variants in one runtime screen.

Avoid one-build-per-pixel iteration when one grid can compare several variants.

### 5. Do not mutate shared state until ownership is proven

Gaia Master 0.6.3.1 lesson:

A cache pointer / VRAM cursor that looks local may actually be global/shared.

Changing shared allocator/cursor behavior for one target glyph caused:

- unrelated text corruption;
- repeated glyphs;
- later garbled screens;
- game freeze.

Target-specific state must be proven target-specific before changing it.

### 6. Distinguish source size from converted/cache footprint

For Gaia Master's wide path:

```text
12x12 4bpp source = 72 bytes
6 source bytes per row
8 converted bytes per row
12 rows -> 96 converted bytes
16 rows -> 128 converted bytes
```

A source glyph fitting in storage does not guarantee the downstream cache allocation is large enough.

### 7. Preserve known-good native art whenever possible

For Vietnamese glyph design:

- preserve native base-letter body;
- reuse native palette/edge/shadow indices;
- add/extend only the required diacritic area.

This avoids style mismatch.

## Japanese games vs US/EU Latin games

### Japanese games are often harder for Vietnamese localization

Common extra complications:

- Shift-JIS / CP932 2-byte text;
- full-width Latin instead of ASCII;
- custom kanji/kana mapping tables;
- glyph cells optimized for Japanese characters rather than tall stacked Latin diacritics;
- fixed 12x12 / 16x16 bitmap fonts;
- custom glyph caches;
- fewer preexisting Latin diacritics.

Gaia Master demonstrates all of these issues in some form.

### US/EU games are often easier, but not guaranteed

A typical US/EU release may already contain:

- ASCII/Latin rendering;
- A-Z / a-z;
- punctuation suitable for Vietnamese sentence structure;
- sometimes Western European accented letters;
- proportional-font logic designed around Latin.

Therefore Vietnamese support can require less renderer surgery.

However there are important exceptions:

- text stored as images;
- compressed scripts;
- custom encodings;
- tiny fixed atlases;
- hardcoded glyph tables;
- narrow buffers or strict fixed-length slots.

So region/language is a strong predictor of difficulty, not a guarantee.

## Practical conclusion for future projects

After Gaia Master, future PS1 localization work should begin with a reusable checklist:

```text
[ ] hash clean image
[ ] identify executable/archive
[ ] prove text encoding
[ ] prove terminator/control format
[ ] locate font atlas
[ ] locate mapping table
[ ] determine glyph format/stride
[ ] test one visible glyph replacement
[ ] trace source -> cache -> VRAM -> primitive only if needed
[ ] verify raw-sector checksum/ECC requirements
[ ] build reproducible patcher
[ ] only then scale translation
```

Gaia Master is effectively the project's reference case for a difficult Japanese PS1 custom-font localization.

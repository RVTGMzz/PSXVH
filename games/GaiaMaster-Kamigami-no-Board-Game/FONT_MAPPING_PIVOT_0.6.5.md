# Gaia Master — 0.6.5 native-cell / mapping-table pivot

Updated: **2026-09-13**

## Why this pivot exists

The 0.6.3.x extended-height path proved too invasive for production. It touched shared cache stride, VRAM Y placement, sprite height and allocator state. The 0.6.4 composite-overlay experiments proved that accent art can look good, but runtime X/Y placement across cache-hit/cache-miss paths was not reliable enough to become the production architecture.

After studying the public PS1 Vietnamese patch repo `2ez4gcx/yugioh-mcbb-vi-patch` and the user-provided `yugioh-mcbb-vi.ppf`, the current strategy is intentionally smaller:

> keep Gaia's native 12x12 / 72-byte renderer geometry, replace font resources, and patch mapping data rather than redesigning the renderer.

Do not claim the Yu-Gi-Oh patch uses Gaia's exact data structures. The useful lesson is architectural minimalism: font/resource replacement plus targeted mapping/code changes can be enough on PS1.

## Proven native font facts

```text
atlas RAM    = 0x8006BCEC
mapping RAM  = 0x8007AECC
atlas file   = SLPS + 0x5C4EC
mapping file = SLPS + 0x6B6CC
860 glyphs
native 12x12 / 72-byte / 4bpp / LOW nibble first
```

Confirmed examples:

```text
0x8273 Ｔ -> glyph 481
0x8264 Ｅ -> glyph 466
0x8272 Ｓ -> glyph 480
0x889F 亜 -> glyph 0
```

## 0.6.5.0 UNIFIED NATIVE-CELL FONT

Goal:
- reserve rows 0..2 for Vietnamese marks;
- normalize Latin bodies into rows 3..11;
- keep plain and accented letters at one common cap-height;
- test a 12-glyph style board:

```text
A Â Ấ Ẳ E Ê Ế Ể O Ô Ố Ỗ
```

Runtime result:
- line rendered mostly as repeated A-like glyphs;
- one unrelated Kanji appeared;
- engine remained alive.

Conclusion:
- the font-art idea was not actually being tested;
- assumption that `0x889F..0x88AA` map linearly to atlas slots `0..11` was false.

## 0.6.5.1 POST-LOOKUP CUSTOM BANK

Attempted to bypass the non-linear Kanji mapping by redirecting the final glyph pointer to a custom 12-glyph bank.

Build did not run because the builder incorrectly required the entire region from the executable cave to the atlas to be zero-filled.

This was a builder assumption bug, not a ROM problem. User's clean BIN SHA1 was correct.

## 0.6.5.2 ATLAS-BACKED CUSTOM BANK

Fixed the zero-cave assumption and stored the 12-glyph bank in native atlas slots 0..11 while keeping a runtime post-lookup redirect hook.

Runtime result:

**UNSAFE FAIL**

- black screen;
- emulator Game FPS = 0;
- hard freeze before useful font output.

Conclusion:

> runtime pointer redirect for this 0.6.5 path is rejected.

Do not retest 0.6.5.2.

## Current direction — mapping-table patch only

Renderer already exposes the lower-risk path conceptually:

```text
character code
  -> mapping_table[code]
  -> glyph index
  -> glyph index * 72
  -> atlas base + offset
```

Production goal:
- no code hook;
- no cache/VRAM geometry change;
- no runtime pointer redirect;
- patch mapping entries directly;
- patch glyph data directly.

## Current tool — Font Mapping Scanner 0.1

Package generated locally:

```text
GaiaMaster_FontMappingScanner_0.1.zip
```

Launcher:

```text
00_RUN_FONT_MAPPING_SCANNER.cmd
```

Output requested from user:

```text
GaiaMaster_FontMappingScanner_01.txt
```

The scanner is READ ONLY. It does not patch ROM and does not require emulator boot.

It attempts to recover:
- PS-X EXE initial GP;
- global atlas pointer slot around `gp+0x518`;
- global mapping-table pointer slot around `gp+0x51C`;
- exact static mapping for `0x889F..0x88AA` if those globals are statically initialized.

If pointers are runtime-initialized, next task is to reverse their initializer offline before creating another ROM probe.

## Hard do-not-repeat

- no Krom path;
- no 12x16 production path;
- no shared CD94 stride/cursor rewrite;
- no global force-height16;
- no persistent/global target flag;
- no post-copy RAM write diagnostic;
- no composite accent runtime X/Y placement path;
- no post-lookup runtime pointer redirect like 0.6.5.2;
- no assumption that consecutive CP932 codes map to consecutive atlas slots.

## User testing preference

- minimize emulator tests;
- maximize information per test;
- prefer READ-ONLY scanners/reverse dumps before new runtime probes;
- never retest a failed/unsafe build;
- stop immediately on freeze/global corruption.

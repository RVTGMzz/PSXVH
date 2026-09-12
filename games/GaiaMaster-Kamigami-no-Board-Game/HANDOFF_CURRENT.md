# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** custom Vietnamese atlas path is proven. One-glyph stacked Vietnamese accents do not fit production-quality in native 12x12, but the 0.6.3.x attempt to enlarge cache cells to 12x16 crossed too much shared renderer state and produced repeated diagnostic failures. After studying the public PS1 Vietnamese patch repo `2ez4gcx/yugioh-mcbb-vi-patch`, the current production experiment is a lower-risk **composite accent overlay**. Current runtime probe: **0.6.4.0 COMPOSITE ACCENT OVERLAY**.

## Baseline

- Game: `GaiaMaster - Kamigami no Board Game (Japan).bin`
- serial `SLPS-02075`
- clean BIN SHA1 `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- Alpha 0.6.1 FRONT SHA1 `54d2fb026bc3b71c79861e723caffb4114caa34c`
- branch `gaia-character-select-font-atlas-reverse-01`

## Proven atlas facts

```text
atlas RAM    = 0x8006BCEC
mapping RAM  = 0x8007AECC
atlas file   = SLPS + 0x5C4EC
mapping file = SLPS + 0x6B6CC
860 glyphs
native 12x12 / 72-byte / 4bpp / LOW nibble first
```

Confirmed mappings:

```text
0x8273 Ｔ -> glyph 481
0x8264 Ｅ -> glyph 466
0x8272 Ｓ -> glyph 480
0x889F 亜 -> glyph 0
```

Character Select probe location:

```text
PRGPACK.BDP + 0xBFD2C
owner nested BDP = entry 29
local offset = +0x580
```

## What 0.6.2.x proved

### 0.6.2.13
Direct static custom-atlas replacement PASS.

### 0.6.2.14..20
Trying to draw `Ế` as one native 12x12 glyph while preserving full-size E body is cosmetically unacceptable for production stacked marks (`Ế/Ể/Ẳ/Ỗ/Ử/Ấ/Ố...`).

This does **not** mean native 12x12 rendering itself is unusable. It means one cell cannot hold both full base body and stacked marks cleanly.

## What 0.6.3.x proved

Extended-height 12x16 research touched:
- source height/stride;
- converted cache stride;
- shared Y cursor;
- VRAM page placement;
- sprite/primitive geometry;
- allocator state.

High-value facts:
- metadata struct `+2` drives source-row count;
- `0x8003C67C` is custom copy routine;
- final record `+7` really reaches primitive height;
- 0.6.3.10 ruled out final visible height as the main lower-row blocker;
- 0.6.3.12 post-copy RAM write probe corrupted layout and is rejected.

Reverse dump 0.1 further proved:

```text
0x8003CC34  a2 = *(s1+100)
0x8003CC38  jal 0x8003C67C
...
0x8003CD94  state+100 advance begins
```

So `state+100` still points to current converted start immediately after the copy call. The 0.6.3.12 failure therefore came from a deeper live-state/register interaction, not simply "state+100 already moved".

## External reference study — Yu-Gi-Oh! MCBB Vietnamese PS1 patch

Reference:

`https://github.com/2ez4gcx/yugioh-mcbb-vi-patch`

Public repo contains release PPF3, patch applier, screenshots and README, not development/reverse source.

README explicitly states the release patch includes:
- Vietnamese translated text;
- redrawn font;
- a few code-adjustment bytes;
- Vietnamese characters on the naming screen.

Do **not** claim the author used Gaia's composite method. Their exact implementation is not public.

Strategic lesson only: a finished Japanese PS1 -> Vietnamese patch can succeed with targeted font/code changes rather than a large global renderer redesign.

Full note:

`YUGIOH_MCBB_REFERENCE_PIVOT.md`

## CURRENT — 0.6.4.0 COMPOSITE ACCENT OVERLAY

Core idea:

> Keep base Latin glyph native and full-size. Render Vietnamese marks as a second native 12x12 sprite positioned on top of it.

Probe internal text:

```text
ＴＥＳＴＥ亜
```

Expected visual:

```text
ＴＥＳＴẾ
```

Implementation:
- native `Ｅ` untouched;
- static glyph #0 (`亜`) replaced by transparent accent-only `mũ + sắc`;
- target overlay uses proven late descriptor-position neighborhood at `0x8003CD08`;
- target overlay descriptor gets:

```text
X -= 12
Y -= 4
```

Thus the second glyph is drawn backward over the preceding E and above its native cell.

No:
- extended 12x16 source;
- 96-byte glyph;
- source/cache stride change;
- CD94 allocator patch;
- sprite-height patch;
- persistent/global target flag;
- post-copy RAM writes.

Package:

```text
GaiaMaster_FontIsolation_0.6.4.0_COMPOSITE_ACCENT_OVERLAY.zip
```

Launcher:

```text
00_RUN_PROBE_0640.cmd
```

Runtime question:

> Do the circumflex + acute appear cleanly above the full-size native E?

If PASS:
- composite rendering becomes production path;
- 0.6.3.x extended-height work becomes optional/background reverse;
- next tasks are zero/neutral overlay advance for in-line use, accent families, bottom marks and encoding/export rules.

## Reverse dump 0.2

Read-only `GaiaMaster_063_REVERSE_DUMP_0.2.zip` remains useful for documenting the old 12x16 path, but it is not required before testing 0.6.4.0.

## Hard do-not-repeat

- no Krom path;
- no production one-glyph 12x12 stacked-accent polishing;
- no retest 0.6.2.18;
- no retest 0.6.3.0..0.6.3.12;
- no naive shared `0x8003CD94..0x8003CDB4` rewrite;
- no persistent/global target flag;
- no global force-height16;
- no `s3+2` metadata assumption;
- no post-copy RAM write diagnostic through state+100.

## User testing preference

- minimize emulator tests;
- maximize information per test;
- never repeat tested builds;
- reverse first unless a probe is isolated and low-risk;
- stop on true freeze/global corruption.

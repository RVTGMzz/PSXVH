# HANDOFF — Gaia Master PS1 Việt hóa

Updated: 2026-09-15
Branch: `gaia-character-select-font-atlas-reverse-01`

## Current checkpoint

**0.6.55.1 — Batch45R2 Font Micro Polish**

Status: **SOURCE READY / STATIC SELFTEST DESIGN READY / RUNTIME NOT YET PROVEN**.

Do **not** call Runtime PASS yet.

The last actual CLEAN-ROM build fully proven by user build log remains **0.6.54.0 / R5**.

## Proven actual build milestone — 0.6.54.0 R5

```text
Clean Japan BIN SHA1                  = f4d5298583c90d89c4b7e51d2dde160ee07f2aec
Batch42 exact fields                  = 560 / 560
Batch43 whole-game visible fields     = 102 / 102
Combined exact fields                 = 662 / 662
Legacy Alpha gate                     = 397 / 397
Current Translation Master coverage   = 596 / 596
Build return code                     = 0
Final report                          = YES
```

Important: **596/596 is only the current Translation Master, not whole-game coverage.**

## Runtime evidence from 0.6.55.0 Batch45

User supplied a gameplay screenshot showing the intro line:

```text
Thế giới đổi chủ
```

Good news from the screenshot:

- the old unsafe `=` garbage-glyph problem is no longer visible in this shown line;
- the rewritten intro wording is readable enough to continue polishing.

But Batch45 is **not font Runtime PASS**. The screenshot proves:

1. lowercase `đ` still does not read naturally as `đ`;
2. its horizontal stroke needs to move **one further pixel upward** versus 0.6.55.0;
3. the bar must cross the actual right-hand ascender of lowercase `d`, not reuse the uppercase-D anchor;
4. circumflex `^` in the `â/ê/ô` family sits too close to the body;
5. stacked structural + tone marks can visually merge in the same small top band.

There is currently **no screenshot proving uppercase `Đ` itself was bad before Batch45**. Therefore R2 restores uppercase `Đ` to its pre-Batch45 vertical placement and keeps a separate left-stem rule.

## 0.6.55.1 Batch45R2 font fix

New files:

```text
tools/build_gaia_06551_batch45r2_font_micro_polish.py
tools/00_BUILD_0.6.55.1_BATCH45R2_FONT_POLISH.cmd
BATCH45R2_0.6.55.1_FONT_MICRO_POLISH.md
```

R2 deliberately does **not** rewrite the historical 0.6.55.0 builder. It first reproduces the 0.6.55.0 chain from CLEAN ROM, then applies a font-only SLPS patch.

### Đ / đ are now separate geometry families

```text
Đ uppercase
- native D stem is LEFT
- bar anchored to left stem
- restore pre-Batch45 vertical placement

đ lowercase
- native d ascender is RIGHT
- detect real right-side vertical stem from native bitmap
- 4-pixel bar is required to cross that stem
- move one more pixel UP relative to 0.6.55.0
```

The lowercase stem detector searches only the right half of native `d` and prioritizes the longest vertical run, then real fill-pixel count. It no longer assumes `x0` is the correct anchor.

### Circumflex / breve families

Root cause found in the generator:

- 0.6.55.0 reserves only two top rows;
- `draw_dual()` adds a down-right shadow;
- the shadow of circumflex/breve can therefore fall onto the first body row;
- stacked tone marks then reuse the same small band.

R2 changes only structural-accent families:

```text
circumflex/breve top reservation : 2 -> 3 rows
structural mark                  : UP 1 px
stacked tone                     : separate side lane
breve stacked-tone lane          : one pixel wider than circumflex lane
```

Current affected frozen glyph set is limited to `Đ`, `đ`, plus every existing 60-codepage glyph containing circumflex or breve. All other glyphs are required to remain byte-identical to the 0.6.55.0 generator.

### R2 hard gates

```text
CLEAN SHA1                             = exact known CLEAN
frozen codepage                        = 60 glyphs
all glyphs                             = exactly 72 bytes
all generated bounding boxes           = inside 12x12
unaffected glyphs                      = byte-identical to 0.6.55.0
Đ                                      = uppercase left-stem rule
đ                                      = lowercase detected right-stem rule
structural/tone rendered pixel overlap = forbidden
font patch target                      = SLPS only
PRGPACK after font patch               = byte-for-byte unchanged
written glyphs                         = read-back byte verification
EDC/ECC                                = regenerated on changed raw sectors
Batch42 exact contract                 = rechecked before and after font patch
Batch45 intro 19/19                    = rechecked before and after font patch
```

Batch43 102 fields are inherited from the already-gated 0.6.55.0 chain; R2 requires PRGPACK to remain byte-for-byte unchanged during its font-only patch.

## Frozen architecture

```text
native 12x12 / 72-byte / 4bpp / LOW nibble first
static mapping-only
frozen 60-glyph Vietnamese codepage
legacy Alpha coverage gate = 397/397
```

Still forbidden:

- renderer hook;
- pointer redirect;
- 12x16;
- 6x12;
- composite overlay;
- changing token order for `%s`, `%d`, `%4d`, `%+3d`, `/V`.

## Critical production fixes from R5 that must not regress

1. production source consumes staged `Core/translation`, not silent GitHub/tools cache;
2. dynamic new-row injections do not overlap Translation Master owners;
3. same-offset dynamic replacement requires exact Japanese-source identity;
4. staging protects the full final exact contract;
5. proof anchors use `Xác nhận?`, `Chọn tướng`, `Nhấn O!`;
6. Batch43 validates source identity against CLEAN ROM;
7. Batch43 span-protects all 560 Batch42 exact fields;
8. actual R5 build contract remains 560/560 + 102/102 = 662/662.

## Reverse Workbench 0.1 — source-only, read-only

Files:

```text
tools/gaia_graphic_asset_census_0.1.py
tools/gaia_runtime_target_locator_0.1.py
tools/00_RUN_REVERSE_WORKBENCH_0.1.cmd
REVERSE_WORKBENCH_0.1.md
```

Purpose:

- fill the asset-discovery gap left by the CP932-only whole-game scanner;
- census structurally valid standard PS-X TIM assets by PRGPACK BDP owner;
- prioritize Character Select owner 29 and assets near its proven text anchors;
- exact-locate runtime Japanese such as `冒険のはじまり` in CLEAN `PRGPACK.BDP` / `SLPS_020.75`;
- report owner/local offset/NUL-field context without patching anything.

Known Character Select text anchor:

```text
PRGPACK.BDP + 0xBFD2C
owner = nested BDP entry 29
owner-local = +0x580
source = キャラクターをえらんでね
```

The full 0.6.38 scanner CSV is not committed, and `冒険のはじまり` is not in the committed Batch43 102-row manifest/code search. Do not invent its offset.

## Next priority

1. Build **0.6.55.1** from exact CLEAN BIN.
2. If BUILD_LOG fails, fix the first failing gate before anything else.
3. If FINAL_REPORT succeeds, runtime-test lowercase `đ`, uppercase `Đ`, plain `â/ê/ô`, and reachable stacked marks such as `ấ/ế/ố/ắ`.
4. Only after gameplay screenshots prove the font stable should intro/font be locked.
5. Continue Reverse Workbench for Main Menu + Character Select.
6. Continue scanner-driven exact-offset work for Story / chapter / land-purchase prompt.
7. Do not create Batch46 from scanner/static evidence while the font runtime gate is still open.
8. Never call whole-game Runtime PASS until relevant gameplay paths are screenshot-proven and corruption-free.

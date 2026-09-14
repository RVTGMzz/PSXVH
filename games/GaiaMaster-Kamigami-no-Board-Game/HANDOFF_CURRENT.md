# HANDOFF — Gaia Master PS1 Việt hóa

Updated: 2026-09-15
Branch: `gaia-character-select-font-atlas-reverse-01`

## Current checkpoint

**0.6.55.0 — Batch45 Front-Face Runtime Polish**

Status: **PACKAGE BUILD-READY / STATIC PASS**. This is **NOT whole-game Runtime PASS**.

The last actual CLEAN-ROM build proven by the user is **0.6.54.0 / R5**.

## Proven actual build milestone — 0.6.54.0 R5

User build log returned code 0 and final report exists.

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

## Runtime evidence after 0.6.54.0

The game boots and translated text is visible, but screenshots prove coverage is still far from complete.

Visible Japanese / pending areas include:

- main menu buttons;
- Character Select header, names and description;
- opening Story dialogue;
- chapter/title card `冒険のはじまり`;
- land-purchase prompt;
- additional gameplay/story/help text.

The main-menu and Character Select labels were not found as ordinary text in the earlier text scans and are still strong **graphic/texture asset candidates**. Do not pretend they are normal text until the asset is identified.

Runtime also exposed two front-face quality bugs:

1. intro strings contained awkward wording and unsafe `=` output, visible as a garbage Japanese-looking glyph between Vietnamese words;
2. glyph `Đ/đ` had its horizontal crossbar too low and was hard to read.

## 0.6.55.0 Batch45 package

Package prepared from the proven R5 chain:

`GaiaMaster_0.6.55.0_Batch45_FRONTFACE_ONECLICK.zip`

Root workflow stays ONECLICK:

```text
CLEAN Japan BIN beside 00_VIET_HOA_GAME.bat
-> double-click 00_VIET_HOA_GAME.bat
-> no drag/drop
-> no path selection
```

Static gates passed:

```text
Python compile                    = 61 files / 0 errors
Batch42 selftest                  = PASS
Batch44 selftest                  = PASS
Batch45 selftest                  = PASS
Base exact contract               = 560
Whole-game visible exact fields   = 102
Combined exact contract           = 662
Intro polish                      = 19 / 19 fit
Unsafe intro '='                  = removed
Intro/exact-manifest collisions   = 0
Đ/đ crossbar source polish        = UP 1 PX
```

0.6.55 changes are runtime-driven only:

- rewrite 19 intro lines within their existing fixed byte budgets;
- remove unsafe `=` from intro;
- raise `Đ/đ` crossbar by one pixel;
- preserve native 12x12 / mapping-only architecture.

### New intro wording

```text
Thế giới đổi chủ
Trời u tối
Miền đất ảo
100 năm một lần
Đại lục loạn
Trò Gaia Master
Bắt đầu!
Luật người
Hôm nay
Tan biến hết
Giờ thế giới
Theo luật Gaia
Vua,tu sĩ
Miền ảo
Trước thần
Khuất phục
Đời là bàn cờ
Người: cờ
Thần chiến!
```

## Frozen architecture

```text
native 12x12 / 72-byte / 4bpp / LOW nibble first
static mapping-only
frozen 60-glyph Vietnamese codepage
legacy Alpha coverage gate = 397/397
```

Hard exclusions remain:

- no renderer hook;
- no pointer redirect;
- no 12x16;
- no 6x12;
- no composite overlay;
- preserve `%s`, `%d`, `%4d`, `%+3d`, `/V` and token order.

The only font retune currently allowed is the runtime-evidenced `Đ/đ` crossbar adjustment in Batch45.

## Critical production fixes from R5 that must not regress

1. 0.6.10 production source must read staged `Core/translation` data instead of silently using GitHub/tools cache.
2. Dynamic new-row injections must not overlap a Translation Master owner.
3. Same-offset dynamic replacement requires exact Japanese-source identity, not prefix identity.
4. Staging protects the full final exact contract, not only newly-added targets.
5. Proof anchors use current wording (`Xác nhận?`, `Chọn tướng`, `Nhấn O!`).
6. Batch43 validates Japanese source against CLEAN ROM, not already-modified intermediate output.
7. Batch43 span-protects all 560 Batch42 exact fields.
8. Actual R5 build must remain reproducible at 560/560 + 102/102 = 662/662.

## Reverse Workbench 0.1 added — source-only, read-only

Added on this branch without changing the production version or runtime verdict:

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

Known Character Select text anchor remains:

```text
PRGPACK.BDP + 0xBFD2C
owner = nested BDP entry 29
owner-local = +0x580
source = キャラクターをえらんでね
```

The full `0.6.38.0` scanner output CSV is **not committed in the repo**, and `冒険のはじまり` is not present in the committed Batch43 102-row manifest or code search. Its exact clean-ROM location therefore still requires running the new locator against the CLEAN BIN.

Do not create production Batch46 from workbench/static evidence alone while Batch45 runtime is unresolved.

## Next-session priority

1. Runtime-test the exact **0.6.55.0 CUE**, especially intro and `Đ/đ`.
2. If gameplay screenshots pass, lock Batch45 intro/font.
3. Run/analyze Reverse Workbench 0.1 and reverse **main menu + Character Select** graphic assets.
4. Use exact screenshot-derived Japanese for Story dialogue, chapter card and land-purchase prompt.
5. Build the next curated exact-offset production batch only after CLEAN-source/owner/field/fit/token/overlap gates pass.
6. Never call whole-game Runtime PASS until screenshots show the relevant paths and no freeze/corruption.

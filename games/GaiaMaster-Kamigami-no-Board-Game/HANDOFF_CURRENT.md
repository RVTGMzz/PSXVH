# HANDOFF — Gaia Master PS1 Việt hóa

Updated: 2026-09-14
Branch: `gaia-character-select-font-atlas-reverse-01`

## Current checkpoint

**0.6.52.0 — Batch 42 Current Translation Master Closure**

Status: **BUILD-READY / STATIC PASS**. This is still **not Runtime PASS**.

## Current data milestone

The 596-row Translation Master is now fully covered by the union of Batch40 final exact keys, Batch19 exact locks and runtime-fit historical locks.

```text
Translation Master rows       = 596
Batch40 final exact keys      = 560
Batch19 exact locks           = 24
Runtime-fit historical locks  = 25
Union covered master keys     = 596 / 596
Uncovered master keys         = 0
Uncovered with Alpha fallback = 0
Uncovered with vi_full        = 0
RESULT                        = MASTER FALLBACK COVERAGE PASS
```

This **does not mean whole-game translation is complete**. Runtime screenshots already proved that Memory Card, Story, Tutorial and Help strings exist outside the current master.

## How closure was reached

After Batch34 there were 218 residual fallback rows.

Batch36 large curated compact sweep:

```text
Curated Japanese keys       = 184
New exact rows exported     = 185
Exact-full-field rows       = 65
Errors                      = 0
RESULT                      = STATIC CURATED PASS
```

Batch38 then found only 33 residual fallback rows. Batch39 closed all 33, preserving special runtime token identity/order including `/V`, `/v`, `%s` and `%d` sequences.

Batch40 merge:

```text
B37 new rows               = 514
B37 final rows             = 527
B39 closure rows           = 33
Merged new exact targets   = 547
Merged final verify set    = 560
Errors                     = 0
RESULT                     = STATIC MERGE PASS
```

## Production builder

Stage wrapper:

`tools/batch40_stage_06500.py`

Builder:

`tools/build_gaia_06520_batch42_master_closure.py`

CI has PASSed:

- Batch40 real source staging/restoration selftest;
- Batch41 full 596-row master coverage audit;
- Batch42 builder selftest.

Production chain remains the proven chain:

```text
0.6.52 staging
 -> 0.6.14
    -> 0.6.13
       -> 0.6.12
          -> 0.6.11
             -> 0.6.10 exact builder
```

No second encoder or ROM patch engine was introduced.

Clean Japan BIN required:

`SHA1 f4d5298583c90d89c4b7e51d2dde160ee07f2aec`

Hard local-build contract:

```text
new exact targets staged = 547
final exact fields        = 560 / 560 byte verification required
legacy Alpha gate         = 397 / 397
source restoration        = PASS
```

A mismatch blocks the build.

## EASY package

Current package:

`GaiaMaster_0.6.52.0_Batch42_EASY.zip`

Root launchers:

```text
00_VIET_HOA_GAME.cmd
01_QUET_TOAN_BO_GAME.cmd
02_DOC_TRUOC.txt
```

Build launcher auto-selects the CLEAN BIN by SHA1.

## Whole-game scanner remains the next critical input

Run:

`01_QUET_TOAN_BO_GAME.cmd`

Return:

```text
GaiaMaster_0.6.38.0_FULL_JAPANESE_SCAN.csv
GaiaMaster_0.6.38.0_FULL_JAPANESE_SCAN_REPORT.txt
```

Use scanner output to expand beyond the current 596-row master, prioritizing visible Memory Card, Story, Tutorial and Help text by exact offset.

## Runtime interpretation

Do not use emulator Recent/History if it can point at an older image. Boot the newly generated output containing `0.6.52.0` in its name.

A known visual anchor remains `%sの番よ！`, which is mapped to `Tới %s`. Seeing old `LUOT` indicates an old image is still being booted.

## Architecture remains frozen

```text
native 12x12 / 72-byte / 4bpp / LOW nibble first
static mapping-only
frozen 60-glyph Vietnamese codepage
legacy Alpha coverage gate = 397/397
```

Hard exclusions:

- no renderer hook
- no pointer redirect
- no 12x16
- no 6x12
- no composite overlay
- no font retune without runtime evidence

Preserve `%s`, `%d`, `%4d`, `%+3d`, `/V` and token order.

## Next priority

1. Build 0.6.52 from CLEAN Japan BIN.
2. Require report to show **560/560** byte verification, **397/397** legacy gate and source restore PASS.
3. Boot the new 0.6.52 output and review screenshots.
4. Run whole-game scanner and return CSV + REPORT.
5. Expand Translation Master with UNSEEN-JAPANESE Story/Tutorial/Help strings.
6. Never call Runtime PASS before actual gameplay screenshots/logs are reviewed.

# HANDOFF — Gaia Master PS1 Việt hóa

Updated: 2026-09-14
Branch: `gaia-character-select-font-atlas-reverse-01`

## Current checkpoint

**0.6.40.0 — Batch 30 Accent Sweep + Whole-Game Discovery**

Status: **BUILD-READY / STATIC PASS**.

This is still **not Runtime PASS**.

Read next:

```text
BATCH30_0.6.40.0.md
checkpoints/0.6.37.0/BATCH28_SAME_ROW_ACCENT_REPORT.txt
checkpoints/0.6.39.0/BATCH29_MERGE_VALIDATION.txt
translation/BATCH29_NEW_EXACT_OFFSET_0.6.39.0.csv
translation/BATCH29_FINAL_EXACT_SET_0.6.39.0.csv
tools/batch29_stage_06390.py
tools/build_gaia_06400_batch30_accent_sweep.py
tools/scan_full_japanese_text_06380.py
```

## What changed after runtime screenshots

User screenshots proved that closing the 147 residual rows inside the 596-row Translation Master did **not** mean whole-game coverage. Visible Memory Card, story/tutorial and card-help Japanese strings are absent from the current master.

The priority is now visible runtime coverage, not merely residual closure inside the old master.

Two tracks are active:

1. upgrade known Alpha ASCII fallback rows to accented Vietnamese where wording can be proven safely;
2. scan CLEAN PRGPACK/SLPS to discover Japanese strings that never entered the current Translation Master.

## Accent sweep state

Batch27 Japanese-key promotion added 2 safe rows.

Batch28 same-row lexical transplant, after excluding all runtime-fit historical locks and Batch19 exact locks, adds **71 safe accented rewrites**.

Examples:

```text
NHAN THE SK   -> Nhận thẻ SK
THE VK DA DAY -> Thẻ VK đã đầy
DOI DUONG?    -> Đổi đường?
HUY            -> Hủy
CHON KHU?      -> Chọn khu?
PHA CAI NAO!!  -> Phá cái nào!!
```

## Batch29 merged exact state

```text
Input candidates B20/B24/B27/B28 = 295
Unique final candidate keys       = 295
Runtime-fit protected keys        = 49
Historical no-op/unfit rows       = 13
Already-locked identical          = 13
Protected wording conflicts       = 0
New exact rows exported           = 282
Final exact verification set      = 295
Errors                            = 0
RESULT                            = STATIC PASS
```

## Batch30 production staging / builder contract

CI selftest proves:

```text
New exact targets     = 282
Final exact verify    = 295
Legacy shadows        = 282
Dynamic sinks         = 5
Legacy gate           = 397/397
Gameplay masks        = 180
Compact13 masks       = 67
Compact14 masks       = 2
Global-map preserves  = 33
Source restore        = PASS
```

Production chain remains the proven chain:

```text
0.6.40 staging
 -> 0.6.14
    -> 0.6.13
       -> 0.6.12
          -> 0.6.11
             -> 0.6.10 exact builder
```

Windows build entrypoint:

```text
tools/00_BUILD_0.6.40.0_BATCH30_ACCENT_SWEEP.cmd
```

Python builder:

```text
tools/build_gaia_06400_batch30_accent_sweep.py
```

Clean Japan BIN required:

```text
SHA1 f4d5298583c90d89c4b7e51d2dde160ee07f2aec
```

After a real local build, the output BIN must pass **295/295 exact byte verification** before the builder reports success.

## Whole-game Japanese scanner

Read-only scanner:

```text
tools/00_SCAN_0.6.38.0_FULL_JAPANESE.cmd
tools/scan_full_japanese_text_06380.py
```

It scans CLEAN `PRGPACK.BDP` + `SLPS_020.75`, excludes font/mapping regions, and compares candidates against the current 596-row master.

Outputs expected from the user:

```text
GaiaMaster_0.6.38.0_FULL_JAPANESE_SCAN.csv
GaiaMaster_0.6.38.0_FULL_JAPANESE_SCAN_REPORT.txt
```

These files are the next critical input for story/tutorial expansion.

## Runtime screenshot interpretation

`XONG!` and `LUOT ジガ` are separate runtime keys. The `%sの番よ！` key is already exact-mapped to `Tới %s`. If a runtime screenshot still shows `LUOT`, the emulator is not running the successfully built current output.

Use the 0.6.40 EASY launcher, which auto-selects the CLEAN BIN by SHA1, then boot the newly generated 0.6.40 output rather than an emulator Recent/History entry.

## Production architecture remains frozen

```text
native 12x12 / 72-byte / 4bpp / LOW nibble first
static mapping-only
frozen 60-glyph Vietnamese codepage
legacy Alpha coverage gate = 397/397
```

Hard exclusions remain:

- no renderer hook
- no pointer redirect
- no 12x16
- no 6x12
- no composite overlay
- no font retuning without new runtime evidence

Preserve `%s`, `%d`, `%4d`, `%+3d`, `/V` and token order.

## Next priority

1. User runs 0.6.40 EASY build against CLEAN Japan BIN.
2. Require `GaiaMaster_0.6.40.0_BATCH30_FINAL_REPORT.txt` to show 295/295 exact byte verification and 397/397 legacy gate.
3. User runs the whole-game scanner against the same CLEAN BIN.
4. Import/review scanner output, prioritizing `UNSEEN-JAPANESE` and screenshot anchor hits.
5. Expand Translation Master with story/tutorial/help strings by exact offset.
6. Build the next large visible-coverage batch.
7. Never call Runtime PASS without actual gameplay screenshots/logs.

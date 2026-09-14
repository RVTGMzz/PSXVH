# Gaia Master 0.6.40.0 — Batch 30 Accent Sweep + Whole-Game Discovery

Updated: 2026-09-14

## Why this batch exists

Runtime screenshots showed two distinct coverage problems:

1. many known master rows could still fall back to old Alpha ASCII text such as `NHAN THE`, `DOI DUONG`, `HUY`;
2. visible story/tutorial strings such as Memory Card text, `ようし、行くぜ！`, `同じエリア...` and `バトルカード...` are absent from the current 596-row Translation Master.

Therefore 0.6.40.0 changes the project priority from residual-only cleanup to visible-runtime coverage.

## Accent sweep

Batch27 added safe Japanese-key accent promotion.

Batch28 added same-row lexical accent transplant. It only promotes text when the row's own `vi_full` proves the wording after accent folding. It never infers meaning from an ambiguous accentless fallback.

After runtime-fit historical locks and Batch19 exact locks are excluded, Batch28 contributes 71 new safe accent rewrites.

Examples include:

- `NHAN THE SK` -> `Nhận thẻ SK`
- `THE VK DA DAY` -> `Thẻ VK đã đầy`
- `DOI DUONG?` -> `Đổi đường?`
- `HUY` -> `Hủy`
- `CHON KHU?` -> `Chọn khu?`
- `PHA CAI NAO!!` -> `Phá cái nào!!`

## Batch29 merged exact set

```text
Input rows across B20/B24/B27/B28 = 295
Unique final candidate keys        = 295
Runtime-fit protected keys         = 49
Historical no-op/unfit rows        = 13
Already-locked identical           = 13
Protected wording conflicts        = 0
New exact rows exported            = 282
Final exact verification set       = 295
Errors                             = 0
RESULT                             = STATIC PASS
```

Files:

```text
translation/BATCH29_NEW_EXACT_OFFSET_0.6.39.0.csv
translation/BATCH29_FINAL_EXACT_SET_0.6.39.0.csv
checkpoints/0.6.39.0/BATCH29_MERGE_VALIDATION.txt
```

## Production staging proof

`tools/batch29_stage_06390.py` dynamically computes precedence instead of using old Batch26 hard-coded counts.

Batch30 builder selftest proves:

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

The builder still calls the proven 0.6.14 -> 0.6.10 production chain.

## Whole-game Japanese scanner

New read-only scanner:

```text
tools/scan_full_japanese_text_06380.py
tools/00_SCAN_0.6.38.0_FULL_JAPANESE.cmd
```

It scans CLEAN `PRGPACK.BDP` and `SLPS_020.75`, excludes SLPS font/mapping regions, and compares Japanese candidates with the current Translation Master.

Outputs:

```text
GaiaMaster_0.6.38.0_FULL_JAPANESE_SCAN.csv
GaiaMaster_0.6.38.0_FULL_JAPANESE_SCAN_REPORT.txt
```

Priority classifications:

- `KNOWN`
- `REPEATED-UNMAPPED`
- `UNSEEN-JAPANESE`

Screenshot anchors include Memory Card, story/tutorial, battle-card help and end-turn text.

## Build entrypoint

```text
tools/build_gaia_06400_batch30_accent_sweep.py
tools/00_BUILD_0.6.40.0_BATCH30_ACCENT_SWEEP.cmd
```

After an actual clean-ROM build, the output BIN must pass:

```text
295 / 295 exact fields byte-for-byte
397 / 397 legacy Alpha gate
```

## Status

**BUILD-READY / STATIC PASS only.**

No Runtime PASS until the user runs the generated image and provides screenshots/logs.

The whole-game scanner must be run against the CLEAN Japan BIN before story/tutorial coverage can be expanded safely by exact offset.

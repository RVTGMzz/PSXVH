# Gaia Master PS1 - Session Handoff 0.6.34.0

Date: 2026-09-14
Branch: `gaia-character-select-font-atlas-reverse-01`

## Current checkpoint

`0.6.34.0 - Batch 25 Dependency-Locked Exact Merge`

This is the current static/data checkpoint. It is not a Runtime PASS.

## Hard locks

- native font 12x12 / 72-byte / 4bpp / LOW nibble first
- static mapping-only
- frozen 60-glyph Vietnamese codepage
- legacy Alpha coverage gate must remain 397/397
- no renderer hook
- no pointer redirect
- no 12x16
- no 6x12
- no composite overlay
- no font retuning without new runtime glyph evidence

## Translation policy

Japanese-first -> natural Vietnamese when it fits -> compact fantasy wording -> micro/ultra only when necessary.

Preserve runtime tokens and order, including `%s`, `%d`, `%4d`, `%+3d`, `/V`.

Menus should stay immediately understandable. Dialogue/world/card text may use compact readable fantasy phrasing.

## Batch 21-24 residual closure

The persisted 0.6.28.0 `RESIDUAL_ALPHA` set contained 147 rows / 62 unique Japanese strings.

Batch 21 supplied meaning-first semantic translations for all 62 unique strings:

```text
covered residual rows = 147 / 147
remaining rows        = 0
errors                = 0
```

Field analysis then split the 147 rows into:

```text
29 semantic rows already fitting
118 pressure rows requiring compact wording
```

Batch 22 solved 21 pressure rows / 12 unique Japanese keys.
Batch 23 solved the remaining 97 pressure rows / 36 unique Japanese keys.

Batch 24 compiles the complete result into:

`translation/BATCH24_EXACT_OFFSET_0.6.33.0.csv`

Verified Batch 24 total:

```text
147 / 147 residual exact rows
0 errors
STATIC PASS
```

## Batch 25 merged exact state

Batch 25 merges:

```text
Batch 20 exact candidates = 75
Batch 24 residual exact   = 147
candidate exact keys      = 222
```

Verified merge:

```text
Runtime-fit protected keys            = 49
Historical rows skipped no-op/unfit   = 13
Already-locked identical              = 13
Protected wording conflicts           = 0
New exact rows exported               = 209
Errors                                = 0
RESULT                                = STATIC PASS
```

Primary output:

`translation/BATCH25_NEW_EXACT_OFFSET_0.6.34.0.csv`

Validation:

`checkpoints/0.6.34.0/BATCH25_MERGE_VALIDATION.txt`

## Historical exact-lock rule

Do not blindly treat every 0.6.14.1 CSV row as a runtime-applied lock.

A historical 0.6.14.1 row protects its exact offset only when it actually fits and encodes under the frozen runtime contract. Batch 19 exact locks remain unconditionally protected.

Thirteen proven runtime-fit historical strings are identical to Batch 24 candidates and are intentionally not exported twice.

The newer compact values below remain valid because the older historical alternatives were unfit/no-op:

```text
%sの番よ！      -> Tới %s
はい　　いいえ -> Có/Ko
```

## Dependency/race fix

Batch 25 CI now rebuilds Batch 24 from current Batch 21/22/23 source CSVs in the same checkout before merging. This is required because bot-generated commits do not form a reliable downstream workflow chain and parallel validation jobs can otherwise leave a stale persisted manifest.

Do not remove this dependency rebuild unless it is replaced by an equally deterministic pipeline.

## Intro cleanup remains mandatory

```text
NGUOI=CO      -> NGUOI CO
THEGIOI=BANCO -> THEGIOI BANCO
```

## Runtime status

STATIC PASS only.

No clean-ROM/runtime evidence has yet promoted 0.6.34.0 to Runtime PASS.

Never call Runtime PASS without user screenshots/logs demonstrating the built result.

## Next session priority

1. Read `HANDOFF_CURRENT.md`, this file, and `BATCH25_0.6.34.0.md`.
2. Integrate `translation/BATCH25_NEW_EXACT_OFFSET_0.6.34.0.csv` into the proven production exact-offset build path as the final wording layer.
3. Keep older proven runtime-fit locks protected and preserve the legacy 397/397 gate.
4. Ensure older global/style/fallback promotions cannot overwrite Batch 25 exact wording.
5. Clean-ROM build.
6. Runtime QA from screenshots/logs: visible Japanese, clipping, token corruption, intro separators, and glyph defects.
7. Font remains frozen unless runtime evidence proves a real glyph defect.

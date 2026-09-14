# HANDOFF — Gaia Master PS1 Việt hóa

Updated: 2026-09-14
Branch: `gaia-character-select-font-atlas-reverse-01`

## Current checkpoint

**0.6.34.0 — Batch 25 Dependency-Locked Exact Merge**

This is the latest verified **static/data** checkpoint. It is not a Runtime PASS.

Read next:

```text
BATCH25_0.6.34.0.md
SESSION_HANDOFF_0.6.34.0.md
NEXT_SESSION_START_0.6.34.0.txt
checkpoints/0.6.34.0/BATCH25_MERGE_VALIDATION.txt
translation/BATCH25_NEW_EXACT_OFFSET_0.6.34.0.csv
```

## Verified translation closure

The persisted 0.6.28.0 Alpha residual set is now closed at the translation-data layer:

```text
Residual source rows = 147
Unique Japanese      = 62
Resolved exact rows  = 147 / 147
Errors               = 0
```

Resolution path:

```text
Batch 21 semantic-fit rows = 29
Batch 22 compact rows      = 21
Batch 23 compact rows      = 97
--------------------------------
Batch 24 exact rows        = 147
```

Batch 24 output:

`translation/BATCH24_EXACT_OFFSET_0.6.33.0.csv`

## Batch 25 merged exact state

Batch 25 merges:

```text
Batch 20 exact candidates = 75
Batch 24 residual exact   = 147
Unique candidate keys     = 222
```

Verified Batch 25 result:

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

## Historical-lock semantics

Do not blindly treat every row in `COMPACT_TRANSLATION_OVERRIDES_0.6.14.1.csv` as an applied runtime lock.

A 0.6.14.1 row is protected only when it actually fits the original Japanese field, preserves runtime tokens, and is safe under CP932/frozen codepage rules. Batch 19 exact locks remain unconditionally protected.

Thirteen Batch 24 candidates are already identical to real runtime-fit historical locks and are intentionally not exported twice.

The newer compact values below remain intentional because their old historical alternatives were unfit/no-op:

```text
%sの番よ！      -> Tới %s
はい　　いいえ -> Có/Ko
```

## Deterministic CI dependency

Batch 25 CI rebuilds Batch 24 from the current Batch 21/22/23 sources **inside the same checkout** before merging. Keep this behavior unless replaced by an equally deterministic dependency pipeline.

Reason: bot-generated persistence commits and parallel workflow runs can otherwise leave a stale Batch 24 manifest behind newer source CSVs.

## Production locks remain frozen

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

Translation policy remains Japanese-first. Use natural Vietnamese when it fits, then compact fantasy wording, then micro/ultra only when necessary. Preserve `%s`, `%d`, `%4d`, `%+3d`, `/V` and token order.

Intro cleanup remains mandatory:

```text
NGUOI=CO      -> NGUOI CO
THEGIOI=BANCO -> THEGIOI BANCO
```

## Runtime status

**STATIC PASS only.**

No clean-ROM build/runtime screenshot or log evidence has yet promoted 0.6.34.0 to Runtime PASS.

Never call Runtime PASS without actual user runtime evidence.

## Next session priority

1. Integrate `translation/BATCH25_NEW_EXACT_OFFSET_0.6.34.0.csv` into the proven production exact-offset build path as the final wording layer.
2. Preserve all proven runtime-fit historical locks and the legacy 397/397 gate.
3. Ensure older global/style/fallback promotion layers cannot overwrite Batch 25 exact wording.
4. Build from a clean verified ROM.
5. Runtime QA with screenshots/logs: visible Japanese, clipping, token corruption, intro separators, and glyph defects.
6. Font/codepage stays frozen unless runtime evidence proves a real glyph problem.

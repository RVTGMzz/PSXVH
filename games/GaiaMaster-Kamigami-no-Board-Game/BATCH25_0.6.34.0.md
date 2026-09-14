# Gaia Master PS1 - Batch 25 / 0.6.34.0

Date: 2026-09-14
Branch: `gaia-character-select-font-atlas-reverse-01`

## Goal

Merge the two current exact-offset work streams into one production-ready data manifest without changing the frozen renderer/font architecture:

- Batch 20 exact candidates: 75 rows
- Batch 24 residual exact manifest: 147 rows
- total candidate exact keys: 222

Batch 24 itself resolves the complete persisted 0.6.28.0 Alpha residual set:

```text
29 semantic-fit rows
21 Batch 22 compact rows
97 Batch 23 compact rows
-------------------------
147 / 147 residual rows
```

## Verified Batch 25 result

`checkpoints/0.6.34.0/BATCH25_MERGE_VALIDATION.txt` reports:

```text
Batch20 + Batch24 input rows : 222
Unique candidate exact keys  : 222
Runtime-fit protected keys   : 49
Historical rows skipped as no-op/unfit: 13
Already-locked identical     : 13
Protected wording conflicts  : 0
New exact rows exported      : 209
Errors                       : 0
RESULT                       : STATIC PASS
```

Output manifest:

`translation/BATCH25_NEW_EXACT_OFFSET_0.6.34.0.csv`

## Historical-lock rule

The old `COMPACT_TRANSLATION_OVERRIDES_0.6.14.1.csv` is not treated blindly as 100% applied production state.

A 0.6.14.1 row is protected only when it actually satisfies the frozen runtime contract:

1. its exact `file + offset` exists in Translation Master;
2. the original Japanese field is CP932-encodable;
3. the Vietnamese candidate fits the original field;
4. runtime token identity/order is preserved;
5. the text is CP932/frozen-codepage safe.

Thirteen historical rows are therefore classified as no-op/unfit and are not allowed to block a newer fitting exact candidate.

Batch 19 exact locks remain unconditionally protected.

## Regression alignment

Thirteen Batch 24 candidates are already identical to proven runtime-fit 0.6.14.1 locks, so Batch 25 does not export them twice.

Important examples include:

```text
Hồi 50HP!
Dừng %s
Đất %s
Đã dừng!
Chiến lấy đất
Nhận VK
Mất20% tiền
Mất20% đất
%s nghỉ
Thách đấu?
Được?
Chọn thẻ
Dùng %s
```

Two compact replacements remain intentionally newer because their historical alternatives were unfit/no-op under the frozen field contract:

```text
%sの番よ！      -> Tới %s
はい　　いいえ -> Có/Ko
```

## CI dependency fix

Batch 25 no longer trusts a previously persisted Batch 24 manifest blindly.

`.github/workflows/gaia-batch25-merge.yml` now rebuilds Batch 24 from the current Batch 21/22/23 sources inside the same checkout before running the Batch 25 merge. This prevents a race where source CSVs are newer than a bot-persisted Batch 24 manifest.

The successful dependency-locked run executed:

1. rebuild Batch 24 exact manifest;
2. merge Batch 20 + rebuilt Batch 24;
3. validate field bytes, runtime tokens and frozen codepage;
4. persist Batch 24 and Batch 25 outputs together.

## Production locks unchanged

```text
native 12x12 / 72-byte / 4bpp / LOW nibble first
static mapping-only
frozen 60-glyph Vietnamese codepage
legacy Alpha coverage gate = 397/397
```

Do not add a renderer hook, pointer redirect, 12x16, 6x12, composite overlay, or font retuning without new runtime evidence.

## Status

`0.6.34.0` is a **static/data exact-merge checkpoint**.

It is **not** a Runtime PASS.

No clean-ROM build or in-game screenshot/log evidence for this merged exact manifest has been accepted yet. Do not claim Runtime PASS until the exact layer is integrated through the proven production build path, the 397/397 gate remains intact, and user runtime evidence is reviewed.

## Next production step

1. Integrate `BATCH25_NEW_EXACT_OFFSET_0.6.34.0.csv` as the final exact-offset layer in the proven production builder path.
2. Ensure it executes after older global/style promotions so those sources cannot overwrite Batch 25 wording.
3. Preserve all proven runtime-fit historical locks and the 397/397 legacy gate.
4. Build from a clean verified ROM.
5. Runtime QA with screenshots/logs, focusing on visible Japanese, clipping, runtime token corruption, intro separators, and glyph defects.
6. Keep font/codepage frozen unless runtime evidence proves a real glyph problem.

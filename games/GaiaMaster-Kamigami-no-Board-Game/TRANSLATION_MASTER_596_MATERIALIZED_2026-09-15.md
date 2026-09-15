# Gaia Master - Translation Master 596/596 source milestone

Date: 2026-09-15
Branch: `gaia-character-select-font-atlas-reverse-01`

## Result

All **596 current Translation Master exact keys** now have editorially reviewed Vietnamese source translations materialized directly into the `vi_full` column of the six Master CSVs.

This is a **source-translation milestone only**. It does not claim new runtime coverage and does not change the compact runtime strings in `vi_game_current`.

Master row contract:

- Part01: 100
- Part02: 100
- Part03: 100
- Part04: 100
- Part05: 100
- Part06: 96
- Total: **596/596**

## Editorial review proof

Global audit tool:

`tools/audit_master_source_review_596_20260915.py`

Successful CI audit:

- workflow: `Gaia Master 596 Source Review Audit`
- run: `34929621705`
- head: `11d87938c574f88e50a037666a6e5be49c79cb02`
- result: SUCCESS
- audit artifact ID: `10381217668`
- audit artifact digest: `sha256:78278567ef1a14d926cbc52d76b4edaa0ae2103a4421be12a5caeeb525eb78a6`

Proven by the audit:

- Translation Master rows: 596/596
- unique exact Master keys: 596/596
- exact Japanese identity: PASS/GATED
- format-token order: PASS/GATED
- `vi_game_current` mutations: 0
- runtime/build integration: NONE
- Runtime PASS claim: NO

Part-level reviewed source coverage:

- Part01: 100/100 = 92 reviewed queue rows + 8 reviewed existing rows
- Part02: 100/100 = 94 existing exact source companions + 6 newly reviewed exact gaps
- Part03: 100/100 exact reviewed companion
- Part04: 100/100 = 77 reviewed completion rows + 23 reviewed existing rows
- Part05: 100/100 exact reviewed companion
- Part06: 96/96 exact reviewed companion

The six Part02 gaps closed before final PASS were:

- `PRGPACK.BDP + 0x5b048` - `なかなかやるね`
- `PRGPACK.BDP + 0x674b8` - `「%s」と`
- `PRGPACK.BDP + 0x674c4` - `「%s」を`
- `PRGPACK.BDP + 0x6762c` - `体力が完全回復したよ`
- `PRGPACK.BDP + 0x67a58` - `すると体力を回復して`
- `PRGPACK.BDP + 0x67ab0` - `やめる`

They are reviewed in:

`translation/PART02_SOURCE_REVIEW_GAPS_2026-09-15.csv`

## Materialization proof

Materializer:

`tools/materialize_master_source_review_596_20260915.py`

The tool is dry-run by default. `--write` may change only `vi_full`. It gates exact file + offset + Japanese identity, preserves format-token count/order, snapshots every non-`vi_full` field, snapshots `vi_game_current`, writes, rereads all six Master files, and verifies no forbidden field changed.

Successful CI materialization:

- run: `34929747559`
- head: `0550ecf8e9513a9b0fafb382adabf9048655f2e5`
- result: SUCCESS
- logs artifact ID: `10381465741`
- logs digest: `sha256:c7bbd0c12658acc82d173685a6dc6b9ecf8027c7f163e15c9aa3ab5fe5e7524c`
- materialized Master artifact ID: `10380807414`
- materialized Master digest: `sha256:c0e1e5330dcea959aa92ab0b1599e5bf4ed8b2f52670952d21e63263d7577019`

Materialization report:

- Master exact rows: 596/596
- reviewed exact keys: 596/596
- blank `vi_full` before: **203**
- already identical: **62**
- editorial replacements: **331**
- rows changed in `vi_full`: **534**
- Part01 changes: 100
- Part02 changes: 82
- Part03 changes: 93
- Part04 changes: 93
- Part05 changes: 81
- Part06 changes: 85
- non-`vi_full` field changes: **0**
- `vi_game_current` changes: **0**
- post-write audit: **596/596 PASS**
- WRITE VERIFY: PASS

## Commit-back proof

The verified CI checkout committed the six materialized Master files back to the branch in one guarded commit.

Bot commit:

`8e76d0bdbf87f66fbcec855cf650970c76ab67b1`

Message:

`Gaia Master: materialize 596 reviewed source translations`

Commit-back workflow run:

- run: `34929881083`
- triggering head: `485536a57e4f1a39fe50276ce4dba9a830e7c5b2`
- job: `source-review-audit`
- job ID: `104255714756`
- result: SUCCESS
- compile: SUCCESS
- 596 audit: SUCCESS
- dry-run materialization: SUCCESS
- materialize/write: SUCCESS
- post-write audit: SUCCESS
- guarded commit-back: SUCCESS

The bot commit is exactly one commit ahead of `485536a...` and modifies only these six paths:

- `translation/TRANSLATION_MASTER_0.6_part01.csv`
- `translation/TRANSLATION_MASTER_0.6_part02.csv`
- `translation/TRANSLATION_MASTER_0.6_part03.csv`
- `translation/TRANSLATION_MASTER_0.6_part04.csv`
- `translation/TRANSLATION_MASTER_0.6_part05.csv`
- `translation/TRANSLATION_MASTER_0.6_part06.csv`

No seventh tracked file was changed by materialization.

## Spot checks

Part01 now stores natural source Vietnamese while preserving the old compact runtime field. Example:

- Japanese: `酒場へようこそ`
- `vi_full`: `Chào mừng đến quán rượu.`
- `vi_game_current`: `QUAN!`

Part05 token-sensitive example:

- Japanese: `Ｌ/V%d（あと/V%d）`
- `vi_full`: `Cấp /V%d (còn /V%d)`
- `vi_game_current`: `LV%d CON%d`

This proves the source layer recovered both `/V` tokens without altering the existing runtime text.

## Important scope statement

**596/596 here means editorial source coverage of the current Translation Master only.**

It does NOT mean whole-game Japanese coverage. The 0.6.38 scanner report still records 6,361 unique unseen-Japanese candidates outside the currently recovered source corpus, and the original full scanner CSV is still unavailable.

It also does NOT mean Runtime PASS. Runtime PASS still requires gameplay screenshots and the existing runtime/build validation rules.

## Next translation direction

1. Treat the six materialized Master files as the current canonical source-translation layer.
2. Stop creating duplicate companions for Master rows unless a later correction needs an auditable patch.
3. Continue mining committed Japanese sources outside the 596 Master exact keys.
4. Recover or regenerate the 0.6.38 full scanner CSV when a CLEAN Japan BIN is available.
5. When the scanner corpus becomes available, dedupe against all 596 Master exact keys, Batch43, intro and known historical source companions before counting new translation coverage.
6. Keep source translation, byte-fit runtime wording, build integration and gameplay QA as separate gates.

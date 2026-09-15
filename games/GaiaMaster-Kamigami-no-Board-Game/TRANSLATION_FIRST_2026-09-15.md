# Gaia Master - Translation-first pass - 2026-09-15

## User direction
For the next sessions, prioritize translation completion. Runtime testing may be unavailable while the user is at work.

Do not call Runtime PASS without gameplay screenshots.

## Font items parked, not forgotten
- Revert ONLY plain lowercase `ă` (U+0103) to the proven 0.6.55.0 historical glyph.
- Keep the current R2 `â` and circumflex work. Do NOT reset `â`.
- Do not broadly revert `ắ/ằ/ẳ/ẵ/ặ` without runtime evidence.
- `ẻ/ể` hook-above polish remains a separate later task.

## Translation source completion pass
The six current Translation Master parts were reviewed for blank `vi_full` cells. Prepared translation-only queues were created without altering runtime fallbacks.

Prepared rows:
- Part01: 92
- Part02: 31
- Part03: 1
- Part04: 77
- Part05: 0 (already source-translated)
- Part06: 2
- Total newly prepared `vi_full`: 203

Queue files:
- `translation/TRANSLATION_COMPLETION_QUEUE_01_PART01.csv`
- `translation/TRANSLATION_COMPLETION_QUEUE_02_PART02.csv`
- `translation/TRANSLATION_COMPLETION_QUEUE_03_PART03.csv`
- `translation/TRANSLATION_COMPLETION_QUEUE_04_PART04.csv`
- `translation/TRANSLATION_COMPLETION_QUEUE_05_PART06.csv`

All queue rows use status `PREPARED_TRANSLATION_ONLY`.
No `vi_game_current` field was changed in this pass.
Tokens such as `%s` and `%d` were preserved in the prepared translations.

## Batch43 full-source translation companion pass
The complete 102-row `BATCH43_WHOLEGAME_VISIBLE_0.6.53.0.csv` selection now also has full Vietnamese source translations, while its byte-fit runtime strings remain untouched.

Split files:
- `translation/BATCH43_SOURCE_FULL_MEMCARD_WEAPONS_2026-09-15.csv` - 70 rows
- `translation/BATCH43_SOURCE_FULL_TUTORIAL_2026-09-15.csv` - 32 rows
- Total: 102/102 Batch43 rows now have a source-full companion translation.

Rules used:
- status `SOURCE_FULL_TRANSLATED_ONLY`
- keep current `vi_runtime_current` text exactly separate from the new source-level translation
- preserve `%s` / `%d` token count and order
- preserve sentence-fragment status where the Japanese scanner split one sentence across multiple fields
- no runtime/build integration in this pass

This does not increase the proven 662 exact runtime fields. It improves the translation source so later integration can choose compact byte-fit wording without losing the intended full meaning.

## Intro full-source companion pass
All 19 Batch45 intro fields now have a natural Vietnamese source-level translation in:
- `translation/INTRO_SOURCE_FULL_2026-09-15.csv` - 19 rows

The current compact runtime wording remains separate and unchanged. Example: source `世界はもはや人のものではなくなった` is recorded as `Thế giới đã không còn thuộc về con người nữa.`, while the current compact runtime line remains `Thế giới đổi chủ`.

## Historical exact-offset source companion pass
Because the original 0.6.38 full scanner CSV is still unavailable, committed exact-offset manifests are being mined without inventing addresses.

The entire `BATCH40_FINAL_EXACT_SET_0.6.50.0.csv` contract is now source-translated: **560/560 exact-offset records**.

Companion files:
- `translation/BATCH40_SOURCE_FULL_TAVERN_SETTINGS_2026-09-15.csv` - 35 rows
- `translation/BATCH40_SOURCE_FULL_GAMEPLAY_LAND_UI_2026-09-15.csv` - 67 rows
- `translation/BATCH40_SOURCE_FULL_CARDS_EVENTS_CHARACTERS_2026-09-15.csv` - 71 rows
- `translation/BATCH40_SOURCE_FULL_RULE_HELP_PROMPTS_2026-09-15.csv` - 44 rows
- `translation/BATCH40_SOURCE_FULL_WEAPONS_ITEMS_2026-09-15.csv` - 62 rows
- `translation/BATCH40_SOURCE_FULL_EVENTS_FACILITIES_NAMES_2026-09-15.csv` - 63 rows
- `translation/BATCH40_SOURCE_FULL_EVENT_EFFECTS_SYMBOLS_2026-09-15.csv` - 70 rows
- `translation/BATCH40_SOURCE_FULL_PROMPTS_LOOKUP_LABELS_2026-09-15.csv` - 43 rows
- `translation/BATCH40_SOURCE_FULL_TAVERN_REPEAT_OFFSETS_2026-09-15.csv` - 92 rows
- `translation/BATCH40_SOURCE_FULL_FINAL_ONLY_13_2026-09-15.csv` - 13 rows
- Total: **560/560** rows.

`BATCH40_NEW_EXACT_OFFSET_0.6.50.0.csv` contains 547 data rows; all 547 are covered by the companion set above. `BATCH40_FINAL_EXACT_SET_0.6.50.0.csv` adds 13 rows not present in the NEW manifest; those 13 are covered separately in `BATCH40_SOURCE_FULL_FINAL_ONLY_13_2026-09-15.csv`.

The 13 FINAL-only exact rows are:
- SLPS `0x958`, `0x970`, `0x980`, `0x98c`, `0x9ac`, `0x9dc`, `0xa14`, `0xa50`, `0xabc`, `0xb08`, `0xe54`, `0xe9c`, `0xeb8`.

These exact-offset rows are historical known-source records and may overlap Japanese strings already represented in Translation Master. They are therefore NOT counted as new entries toward the 6,361 unique unseen-Japanese scanner corpus.

All exact-offset companion rows:
- keep `file` and `offset_hex` from the committed exact-offset source manifest
- keep the current compact runtime wording in `vi_runtime_current`
- put the natural source-level Vietnamese in `vi_full`
- use status `SOURCE_FULL_TRANSLATED_ONLY`
- preserve format tokens and token order, including `%s`, `%d`, `%4d`, `%+3d`, and `/V%d`
- preserve sentence-fragment status instead of guessing missing text
- do not alter runtime/build data

## Translation-first artifact count so far
Prepared translation/source-companion row records in this pass:
- Translation Master blank `vi_full` completion queues: 203
- Batch43 source-full companion: 102
- Intro source-full companion: 19
- Batch40 FINAL exact-offset source companions: 560
- Total prepared row records: **884**

This is a work-record count, not a claim of 884 unique Japanese strings. Exact-offset rows can repeat the same Japanese text at multiple addresses and can overlap Translation Master source text.

## Whole-game translation reality
Current Translation Master: 596 keys. Existing runtime contract protects 596/596 master coverage, but this is NOT whole-game coverage.

The full Japanese scanner report from 0.6.38.0 states:
- scanner candidates: 13,330
- known same offset: 561
- known text at other offset: 120
- unseen Japanese candidates: 12,649
- unique unseen Japanese: 6,361
- screenshot-anchor hits: 18

The actual `GaiaMaster_0.6.38.0_FULL_JAPANESE_SCAN.csv` is not currently present in the repo and has not been recovered from File Library yet. File Library search on 2026-09-15 found the scanner report but not the CSV itself. Do not invent offsets.

## Next translation priority
1. Recover the full scanner CSV if possible.
2. If recovered, build a translation-only priority queue:
   - HIGH confidence first
   - null/control-terminated first
   - exclude known master offsets
   - exclude already-covered Batch43 rows
   - dedupe repeated Japanese text
   - prioritize story/tutorial/help/menu/runtime prompts
3. Translate in large batches without requiring runtime testing.
4. Keep runtime integration and fit/byte verification separate from source translation work.
5. Until the full scanner CSV is recovered, keep mining committed source/reports for Japanese text not yet represented by a source-full companion, without inventing missing offsets.

## Existing proven runtime/build contract to preserve later
- Batch42: 560/560
- Batch43: 102/102
- combined: 662/662
- intro: 19/19
- legacy Alpha: 397/397
- architecture: native 12x12 / 72-byte / 4bpp / mapping-only / frozen 60-glyph codepage

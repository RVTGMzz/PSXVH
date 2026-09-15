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
5. Until the full scanner CSV is recovered, keep mining committed source/reports for untranslated Japanese without inventing missing offsets.

## Existing proven runtime/build contract to preserve later
- Batch42: 560/560
- Batch43: 102/102
- combined: 662/662
- intro: 19/19
- legacy Alpha: 397/397
- architecture: native 12x12 / 72-byte / 4bpp / mapping-only / frozen 60-glyph codepage

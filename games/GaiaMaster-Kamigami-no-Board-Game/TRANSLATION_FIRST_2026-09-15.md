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

## Whole-game translation reality
Current Translation Master: 596 keys. Existing runtime contract protects 596/596 master coverage, but this is NOT whole-game coverage.

The full Japanese scanner report from 0.6.38.0 states:
- scanner candidates: 13,330
- known same offset: 561
- known text at other offset: 120
- unseen Japanese candidates: 12,649
- unique unseen Japanese: 6,361
- screenshot-anchor hits: 18

The actual `GaiaMaster_0.6.38.0_FULL_JAPANESE_SCAN.csv` is not currently present in the repo and has not been recovered from File Library yet. Do not invent offsets.

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

## Existing proven runtime/build contract to preserve later
- Batch42: 560/560
- Batch43: 102/102
- combined: 662/662
- intro: 19/19
- legacy Alpha: 397/397
- architecture: native 12x12 / 72-byte / 4bpp / mapping-only / frozen 60-glyph codepage

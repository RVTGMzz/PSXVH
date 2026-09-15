# Gaia Master - HIGH-FIRST translation checkpoint - 2026-09-15

## Scope
Translation-first source work only. Runtime/build integration remains untouched. This checkpoint is **not** a Runtime PASS.

## Scanner / queue baseline
- CLEAN Japan BIN SHA1: `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- Full scanner candidates: **13,330**
- Raw unique unseen Japanese: **6,361**
- Reviewed committed unique Japanese subtracted: **634**
- New unique source queue: **6,229**
- HIGH-FIRST queue: **3,504**
- REVIEW-MEDIUM queue: **2,725**

## HIGH-FIRST progress through Batch10
- Source-translated rows: **1,135**
- Proper-name rows handled/preserved: **58**
- System input-table rows preserved: **10**
- Scanner false positives flagged: **24**
- Context-review rows parked: **10**
- Untouched HIGH-FIRST rows remaining: **2,267**
- Total HIGH-FIRST rows: **3,504**

## Batch coverage
- Batch01: save/load/password, setup/team/map, ending/dialogue - 217 translated
- Batch02: character story/dialogue around Jiger, Hayate, Erina, Titania - 97 translated
- Batch03: combat/card/help - 82 translated
- Batch04: Yasutsuna / Goliath / Galahad / Princess Tiara story - 166 translated
- Batch05: Princess Tiara / Sinbad / Sun Wukong / Megumegu / Jiger-Erina story - 226 translated
- Batch06: credits - 16 role labels translated; 58 personal/company names preserved; 1 false positive
- Batch07: character profiles/traits + clean SLPS weapon/stat strings - 145 translated
- Batch08: weapon-skill/multitap + event/shop + results/ranking - 70 translated
- Batch09: scanner-prefixed weapon/item labels + clean gameplay islands - 92 translated; 4 context-review
- Batch10: event/money/Demon King/setup/SLPS protection strings - 24 translated; 10 kana input-table rows preserved

## Latest local checkpoint identity
File: `GaiaMaster_TRANSLATION_QUEUE_HIGH_FIRST_VI_PROGRESS_B10.csv`

- Size: **554,587 bytes**
- SHA256: `c8d8855f8f0b4ceb30b69acc31d1bcc94e570f0d8e6cd7f97ea1c99e83006733`

Recent batch SHA256s:
- Batch09: `cb806dd51e69735ccfca355fb24e6fdee578241b2e0954bdd7b9f2692e455674`
- Batch10: `bd7871a8452b5d8031b355b941c7e361a7a4f0f5db6fbebc448b766a66379604`

Earlier verified checkpoint:
- B08 progress SHA256: `b471d7854e309ad8d9d8fb629db4dd4bb5109dfd287d9f2ac018310bfc8cb3cc`

## Translation contracts
- Preserve exact Japanese/file/offset metadata.
- Fill source `vi_full` only; do not mutate runtime strings.
- Preserve `%s`, `%d`, `%2d`, `%4d`, `%+3d`, `%5d`, `/V`, `/v`, and special `＠` count/order.
- Keep sentence fragments as fragments.
- Preserve scanner prefixes in the Japanese evidence field; translate only the readable meaning into `vi_full`.
- Mark obvious scanner mojibake as false positive instead of translating it.
- Park ambiguous but plausible rows for context review.
- Keep character-entry/kana tables as system data rather than localizing them.
- Preserve proper names when the reading is uncertain.
- Do not call whole-game translation complete.
- Do not call Runtime PASS without gameplay screenshot evidence.

## Next source checkpoint
Continue from local `GaiaMaster_TRANSLATION_QUEUE_HIGH_FIRST_VI_PROGRESS_B10.csv`, with **2,267 HIGH-FIRST rows still untouched**.

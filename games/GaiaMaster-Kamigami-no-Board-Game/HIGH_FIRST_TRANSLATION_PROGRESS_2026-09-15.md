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

## HIGH-FIRST progress through Batch08
- Source-translated rows: **1,019**
- Proper-name rows handled/preserved: **58**
- Scanner false positives flagged: **24**
- Context-review rows parked: **6**
- Untouched HIGH-FIRST rows remaining: **2,397**
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

## Latest local checkpoint identity
File: `GaiaMaster_TRANSLATION_QUEUE_HIGH_FIRST_VI_PROGRESS_B08.csv`

- Size: **549,833 bytes**
- SHA256: `b471d7854e309ad8d9d8fb629db4dd4bb5109dfd287d9f2ac018310bfc8cb3cc`

Individual batch SHA256s:
- Batch01: `a293dfaf6ae500faf9d917f325977d21d8025203e5a116e3d330ddf1d85f37fe`
- Batch02: `86cd130adcab8ad14c9d539fbc569678cbce0b9f3cc273004941f636aada5e12`
- Batch03: `ebfd4e168f340845f44a3441f4e52fe95a661efd7e8ea0100cf8fbdcb43954c4`
- Batch04: `b27be599e791cffb7a8da4d7374bae8eb35544a9a6899a00d1bbc0893e832327`
- Batch05: `159fa91da9bdcc1049669481b4c8a5c4ad4de1080234fe2a1aebeafc20882cd4`
- Batch06: `9ed3e8bb05bab170f6092d66469b87d97d7b5076da39c994e4137a8d25816b69`
- Batch07: `298f52d0f64e8a55107d88ff4666cba09870bdacf19d5ef70ef498030d387518`
- Batch08: `634f9dc1fd33096d511d7cd4195cbaf81155054e942d8451cb3a228e9489e8a4`

## Translation contracts
- Preserve exact Japanese/file/offset metadata.
- Fill source `vi_full` only; do not mutate runtime strings.
- Preserve `%s`, `%d`, `%2d`, `%4d`, `%+3d`, `%5d`, `/V`, `/v`, and special `＠` count/order.
- Keep sentence fragments as fragments.
- Mark obvious scanner mojibake as false positive instead of translating it.
- Park ambiguous but plausible rows for context review.
- Preserve proper names when the reading is uncertain.
- Do not call whole-game translation complete.
- Do not call Runtime PASS without gameplay screenshot evidence.

## Next source checkpoint
Continue from local `GaiaMaster_TRANSLATION_QUEUE_HIGH_FIRST_VI_PROGRESS_B08.csv`, with **2,397 HIGH-FIRST rows still untouched**.

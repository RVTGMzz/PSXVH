# Gaia Master PS1 - Session Handoff 0.6.28.0

Date: 2026-09-14
Branch: `gaia-character-select-font-atlas-reverse-01`

## Current candidate
`0.6.28.0 - Exact-Offset Lock / Handoff Batch 19`

## Hard locks
- native font 12x12 / 72-byte / 4bpp / LOW nibble first
- static mapping-only
- frozen 60-glyph Vietnamese codepage
- legacy Alpha coverage gate must remain 397/397
- no renderer hook, pointer redirect, 12x16, 6x12, or composite overlay
- font tuning stays frozen unless runtime proves a glyph fault

## Translation policy
Japanese-first -> natural Vietnamese -> fantasy compact -> micro/ultra compact.
Preserve `%s`, `%d`, `%4d`, `%+3d`, and runtime token order.
Menus stay clear; dialogue/world/card text may use readable medieval fantasy tone.

## Batch 19 core
1. Keep Batch 18 consensus + fit-pressure engine.
2. After fitting Translation Master rows, export every safe fitting `vi_full` into the proven exact `file + offset` compact override path.
3. Never auto-replace historical 0.6.14.1 exact locks.
4. Generate three reports after build: `RESIDUAL_ALPHA`, `FIT_PRESSURE`, `EXACT_OFFSET_LOCKS`.
5. Recover outputs recursively from package and temporary source locations before rename.
6. Keep intro separator cleanup: `NGUOI=CO -> NGUOI CO`, `THEGIOI=BANCO -> THEGIOI BANCO`.

## Runtime status
Candidate only. Loader syntax PASS. Clean-ROM build and runtime QA pending. Never call runtime PASS without user screenshots/log evidence.

## Next session workflow
Ask for the three 0.6.28.0 report CSVs and runtime screenshots. Prioritize exact-offset compact wording for `FIT_PRESSURE` rows and any visible Japanese. Do not reopen font work without new evidence.

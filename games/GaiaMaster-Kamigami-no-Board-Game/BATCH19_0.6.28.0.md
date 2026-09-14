# Gaia Master 0.6.28.0 - Batch 19

## Exact-Offset Lock / Session Handoff

Batch 19 keeps the Batch 18 residual/consensus fitting engine and adds exact `file + offset` locking through the proven 0.6.14 compact override path.

New in this batch:
- Fitting `vi_full` rows are exported as exact compact overrides before the inner build.
- Historical 0.6.14.1 exact locks are preserved.
- New report: `GaiaMaster_0.6.28.0_EXACT_OFFSET_LOCKS.csv`.
- Existing residual reports remain: `RESIDUAL_ALPHA` and `FIT_PRESSURE`.
- Output recovery scans both package and temporary source folders.
- A session handoff snapshot is included for the next working session.

Manual delta: 20 semantic edits, 20 style edits, 12 dynamic literal edits.

Production locks remain unchanged: native 12x12 / 72-byte / 4bpp, static mapping-only, frozen Vietnamese codepage, legacy Alpha gate 397/397.

0.6.28.0 is a candidate. Syntax PASS only. Clean-ROM build and runtime QA are still pending user evidence.

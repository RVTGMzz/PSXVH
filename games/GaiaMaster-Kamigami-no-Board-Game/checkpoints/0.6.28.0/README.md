# Checkpoint 0.6.28.0 - Batch 19

Current candidate: Exact-Offset Lock / Session Handoff.

Key behavior:
- keeps Batch 18 residual/consensus fitting;
- exports fitting translated rows into the proven exact `file + offset` compact override path;
- preserves historical 0.6.14.1 locks;
- generates `RESIDUAL_ALPHA`, `FIT_PRESSURE`, and `EXACT_OFFSET_LOCKS` reports;
- recovers outputs from package or temporary source folders;
- font remains frozen;
- legacy coverage gate remains 397/397.

## Restored repo-native report stage

The original Batch 19 handoff snapshot did not contain the executable report stage. It has now been reconstructed in the repo without changing the production font/codepage architecture:

```text
../../tools/gaia_batch19_report_compiler_06280.py
../../tools/00_RUN_0.6.28.0_BATCH19_REPORTS.cmd
```

Run the CMD from a current checkout. Default output is written to:

```text
checkpoints/0.6.28.0/reports/
```

Expected files:

```text
GaiaMaster_0.6.28.0_RESIDUAL_ALPHA.csv
GaiaMaster_0.6.28.0_FIT_PRESSURE.csv
GaiaMaster_0.6.28.0_EXACT_OFFSET_LOCKS.csv
GaiaMaster_0.6.28.0_AUTO_EXACT_OVERRIDES.csv
GaiaMaster_0.6.28.0_REPORT_SUMMARY.txt
```

The reconstruction is report-only. It does not patch BIN/CUE, BDP checksums, font atlas, renderer, pointers, or the frozen codepage. Historical exact locks from `COMPACT_TRANSLATION_OVERRIDES_0.6.14.1.csv` remain protected.

Runtime status: candidate only. Syntax PASS. Clean-ROM build and runtime QA pending.

Next work should consume the generated Batch 19 reports and runtime screenshots. Do not reopen font work unless runtime demonstrates a real glyph defect.

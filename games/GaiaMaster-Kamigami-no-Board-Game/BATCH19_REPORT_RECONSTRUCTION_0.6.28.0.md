# Gaia Master 0.6.28.0 - Batch 19 Report Reconstruction

Date: 2026-09-14
Branch: `gaia-character-select-font-atlas-reverse-01`

## Why this exists

The Batch 19 handoff documents `RESIDUAL_ALPHA`, `FIT_PRESSURE`, and `EXACT_OFFSET_LOCKS`, but the repo snapshot at the handoff point contained only the Batch 19 translation deltas and handoff/checkpoint notes. The executable report stage itself was not committed.

This reconstruction restores that missing repo-native stage without reopening font work and without patching the ROM.

## Tool

```text
tools/gaia_batch19_report_compiler_06280.py
tools/00_RUN_0.6.28.0_BATCH19_REPORTS.cmd
```

Default output:

```text
checkpoints/0.6.28.0/reports/
  GaiaMaster_0.6.28.0_RESIDUAL_ALPHA.csv
  GaiaMaster_0.6.28.0_FIT_PRESSURE.csv
  GaiaMaster_0.6.28.0_EXACT_OFFSET_LOCKS.csv
  GaiaMaster_0.6.28.0_AUTO_EXACT_OVERRIDES.csv
  GaiaMaster_0.6.28.0_REPORT_SUMMARY.txt
```

## Safety rules

- Reads all six Translation Master parts.
- Requires the 596-row Translation Master gate.
- Loads cumulative `BATCH*_JP_EXACT_*` and `BATCH*_STYLE_*` maps, with later batches taking priority.
- Reconstructs Batch 18 duplicate consensus using normalized Japanese/fallback text.
- Preserves runtime token identity and order for `%...` and `/V` tokens.
- Uses the proven 0.6.14 fit estimate: normal display units are 2 bytes, runtime tokens retain ASCII byte length, and a candidate must not exceed the original Japanese CP932 field length.
- `EXACT_OFFSET_LOCKS` and `AUTO_EXACT_OVERRIDES` are generated only from direct non-empty `vi_full` rows that fit and preserve tokens.
- Existing `COMPACT_TRANSLATION_OVERRIDES_0.6.14.1.csv` keys are protected and never auto-replaced.
- Semantic/style/consensus candidates are analysis-only; they are not silently written into Translation Master.
- Does not modify BIN/CUE, BDP checksums, atlas, renderer, pointers, font, or frozen codepage.

## Runtime status

This restores report reproducibility only. It does **not** turn 0.6.28.0 into runtime PASS. Clean-ROM build and runtime screenshots/log evidence are still required before any runtime PASS claim.

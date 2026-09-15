# Gaia Master - Committed Japanese source corpus exhausted

Date: 2026-09-15
Branch: `gaia-character-select-font-atlas-reverse-01`

## Result

The committed translation-source inventory has been exhausted for source-level Vietnamese review.

Audit tool:

`tools/inventory_translation_residual_sources_20260915.py`

Workflow:

`.github/workflows/gaia-translation-residual-audit.yml`

Successful CI proof:

- workflow: `Gaia Master Committed Residual Japanese Audit`
- run: `34930304637`
- job: `residual-source-audit`
- job ID: `104256942014`
- head: `2f55f4cb30dd7dcc7a4ccd585bce74becb932588`
- result: SUCCESS
- artifact: `GaiaMaster_Committed_Residual_Japanese_Audit`
- artifact ID: `10381273532`
- artifact digest: `sha256:cf8001fb2c277cc0fe4732b96427722e8b977971d05814f56b85530fd8529975`

Audit report:

```text
Translation CSV files scanned       : 108
CSV files with japanese column      : 85
Trusted reviewed source files       : 43
Materialized Master reviewed rows   : 596 / 596
Reviewed unique Japanese strings    : 634
Residual committed source rows      : 0
Residual UNIQUE Japanese strings    : 0
Runtime/build changes               : 0
Whole-game coverage claim           : NO
```

## Meaning

`Residual committed source rows = 0` means every Japanese string currently present in committed `translation/*.csv` sources is represented by the reviewed/source-full Japanese coverage set.

It does **not** mean the whole game has been translated.

The historical 0.6.38 full scanner report still records:

- scanner candidates: 13,330
- known same offset: 561
- known text at other offset: 120
- unseen Japanese candidates: 12,649
- unique unseen Japanese: 6,361
- screenshot-anchor hits: 18

The original `GaiaMaster_0.6.38.0_FULL_JAPANESE_SCAN.csv` has not been recovered from the repository, Git history, File Library or workflow artifacts checked so far.

Therefore the next source-translation expansion cannot honestly be obtained by mining the current committed translation CSVs again. New source material requires either:

1. recovering the original 0.6.38 scanner CSV, or
2. regenerating an equivalent scanner corpus from the exact CLEAN Japan BIN.

## Counting rule

The 634 reviewed unique Japanese strings are the unique Japanese strings represented in the current committed translation-source coverage set. They must not be added mechanically to the historical 6,361 unseen scanner count because the source sets overlap and use different selection rules.

Likewise, exact-offset row counts such as 596 Master, 560 Batch40, 102 Batch43 and 19 intro are work/contract counts, not unique-Japanese counts.

## Next direction

- Treat Translation Master `vi_full` 596/596 as canonical for current committed Master sources.
- Do not create more duplicate source companions for already-reviewed Master rows.
- Preserve the residual audit as a regression gate so new committed Japanese sources cannot silently remain unreviewed.
- Prepare a reproducible full scanner regeneration path for the exact CLEAN Japan BIN SHA1 `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`.
- When a regenerated scanner CSV is available, dedupe it against the reviewed committed corpus before starting the next large translation batch.
- Keep scanner/source translation separate from byte-fit runtime integration and gameplay QA.

Runtime PASS remains unavailable without gameplay screenshots.

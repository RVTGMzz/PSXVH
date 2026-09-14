# HANDOFF — Gaia Master PS1 Việt hóa

Updated: 2026-09-14
Branch: `gaia-character-select-font-atlas-reverse-01`

## Current checkpoint

**0.6.35.0 — Batch 26 Final Exact Production Wrapper**

Status: **BUILD-READY / STATIC PRECEDENCE PASS**.

This is still **not Runtime PASS**.

Read next:

```text
BATCH26_0.6.35.0.md
SESSION_HANDOFF_0.6.35.0.md
NEXT_SESSION_START_0.6.35.0.txt
checkpoints/0.6.35.0/BATCH26_PRECEDENCE_AUDIT.txt
tools/batch26_stage_06350.py
tools/build_gaia_06350_batch26_final.py
```

## Translation closure inherited from Batch 21-25

```text
0.6.28.0 residual Alpha rows = 147
resolved exact rows           = 147 / 147
Batch20 + Batch24 candidates  = 222 exact keys
historical proven locks reused = 13
new Batch25 exact rows         = 209
Batch25 merge conflicts        = 0
```

## Batch 26 production-precedence proof

```text
Batch25 new exact targets          = 209
Legacy shadow rows                 = 209
Dynamic sink rows                  = 4
0.6.11 exact collisions masked     = 149
0.6.13 exact collisions masked     = 23
0.6.14 exact collisions masked     = 2
Global-map preservation entries    = 29
Effective dynamic hits             = 10
Dynamic hits already identical     = 6
Dynamic differing hits safely sunk = 4
Dynamic sink failures              = 0
Legacy gate before                 = 397
Legacy gate with wrapper layout    = 397
Final exact mismatches (static)     = 0
Errors                              = 0
RESULT                              = STATIC PRECEDENCE PASS
```

## Why the wrapper is safe

Batch 26 keeps the existing production chain and does not introduce a second translation encoder:

```text
0.6.35 staging
 -> 0.6.14
    -> 0.6.13
       -> 0.6.12
          -> 0.6.11
             -> 0.6.10 exact builder
```

For each new exact target, the primary row receives Batch25 `vi_full` and temporarily hides `vi_game_current` from global promotion. A legacy shadow row immediately after it keeps the exact 397-key Alpha reconstruction intact.

Only four keys need a dynamic sink. The sink absorbs a conflicting 0.6.14 dynamic write, has a zero-byte Japanese source field so 0.6.10 skips it, then the real exact primary is processed.

Filtering old 0.6.11 exemplars would change the 0.6.12 global map, so Batch26 appends 29 temporary preservation rows. Static audit proves the global map stays identical to the production baseline.

All mutable source CSVs are restored in `finally` and hash-checked. CI has executed the real stage/restore cycle successfully.

## Production launcher

```text
tools/00_BUILD_0.6.35.0_BATCH26_FINAL_EXACT.cmd
```

Python entrypoint:

```text
tools/build_gaia_06350_batch26_final.py
```

Clean Japan BIN required:

```text
SHA1 f4d5298583c90d89c4b7e51d2dde160ee07f2aec
```

## Post-build hard gate

After the 0.6.14 chain finishes, Batch26 reads the produced BIN and uses the verified readable 0.6.10 encoder/codepage logic to require:

```text
222 / 222 final exact fields = byte-for-byte PASS
```

One mismatch blocks the build.

CI currently passes:

- production precedence audit;
- actual source staging/restoration selftest;
- final builder `--selftest`.

GitHub does not contain the clean ROM, so the real BIN build remains local/user-side.

## Production architecture remains frozen

```text
native 12x12 / 72-byte / 4bpp / LOW nibble first
static mapping-only
frozen 60-glyph Vietnamese codepage
legacy Alpha coverage gate = 397/397
```

Hard exclusions remain:

- no renderer hook
- no pointer redirect
- no 12x16
- no 6x12
- no composite overlay
- no font retuning without new runtime evidence

Translation policy remains Japanese-first. Preserve `%s`, `%d`, `%4d`, `%+3d`, `/V` and token order.

Intro cleanup remains mandatory:

```text
NGUOI=CO      -> NGUOI CO
THEGIOI=BANCO -> THEGIOI BANCO
```

## Next priority

1. Run the Batch26 launcher against the verified clean Japan BIN.
2. Require `GaiaMaster_0.6.35.0_BATCH26_FINAL_REPORT.txt` to show 222/222 byte verification and source restore PASS.
3. Runtime-test the generated image.
4. Review screenshots/logs for visible Japanese, clipping, token corruption, intro separators and glyph defects.
5. Keep font/codepage frozen unless actual runtime evidence proves a glyph problem.
6. Never call Runtime PASS before actual gameplay evidence.

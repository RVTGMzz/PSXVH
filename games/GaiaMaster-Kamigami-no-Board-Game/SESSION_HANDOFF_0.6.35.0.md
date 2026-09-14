# Gaia Master PS1 - Session Handoff 0.6.35.0

Date: 2026-09-14
Branch: `gaia-character-select-font-atlas-reverse-01`

## Current checkpoint

`0.6.35.0 - Batch 26 Final Exact Production Wrapper`

Status: **BUILD-READY / STATIC PRECEDENCE PASS**.

It is not Runtime PASS.

## Read first

```text
HANDOFF_CURRENT.md
BATCH26_0.6.35.0.md
checkpoints/0.6.35.0/BATCH26_PRECEDENCE_AUDIT.txt
tools/batch26_stage_06350.py
tools/build_gaia_06350_batch26_final.py
```

## What is now solved

Batch 21-24 closed all 147 persisted 0.6.28.0 Alpha residual rows.

Batch 25 merged Batch 20 + Batch 24 into 222 candidate exact keys and exported 209 new exact rows after protecting 13 already proven historical locks.

Batch 26 now gives those 209 rows a deterministic production path through the existing 0.6.10 -> 0.6.14 chain.

## Batch 26 static gates

```text
Batch25 new exact targets          = 209
Legacy shadows                     = 209
Dynamic sinks                      = 4
0.6.11 exact masks                 = 149
0.6.13 exact masks                 = 23
0.6.14 exact masks                 = 2
Global fallback preservation rows  = 29
Effective dynamic hits             = 10
Identical dynamic hits             = 6
Differing dynamic hits safely sunk = 4
Legacy gate before                 = 397
Legacy gate during wrapper         = 397
Final exact static mismatches      = 0
Errors                             = 0
```

Current audit result: `STATIC PRECEDENCE PASS`.

## Real staging behavior

Batch 26 temporarily modifies only translation input CSVs. Every mutable source is backed up and restored in `finally`, then hash-checked.

CI has executed a real stage/verify/restore cycle successfully.

## Production wrapper

Run:

`tools/00_BUILD_0.6.35.0_BATCH26_FINAL_EXACT.cmd`

with the clean Japan BIN.

The Python entrypoint is:

`tools/build_gaia_06350_batch26_final.py`

It only accepts:

```text
SHA1 f4d5298583c90d89c4b7e51d2dde160ee07f2aec
```

The wrapper calls the proven 0.6.14 production builder. It does not introduce a second string patch/encoder engine.

## Post-build verification contract

After the inner build returns, the wrapper reads the produced BIN and uses the verified readable 0.6.10 encoder/codepage logic to verify the full final exact candidate set:

```text
222 / 222 exact fields must match byte-for-byte
```

Failure of any single field blocks success.

## CI state

Current CI passes:

- Batch26 precedence audit
- real source staging/restoration selftest
- final builder `--selftest`

GitHub does not contain the clean ROM, so actual image building is still local/user-side.

## Hard architecture locks

```text
native 12x12 / 72-byte / 4bpp / LOW nibble first
static mapping-only
frozen 60-glyph Vietnamese codepage
legacy Alpha coverage gate = 397/397
```

Do not add renderer hook, pointer redirect, 12x16, 6x12, composite overlay, or font retuning without new runtime evidence.

## Translation/token rules

Japanese-first. Natural Vietnamese if it fits, then compact fantasy, then micro/ultra only as needed.

Preserve runtime tokens and order:

```text
%s
%d
%4d
%+3d
/V
```

Intro cleanup remains mandatory:

```text
NGUOI=CO      -> NGUOI CO
THEGIOI=BANCO -> THEGIOI BANCO
```

## Next session priority

1. Build 0.6.35.0 from the clean Japan BIN using the Batch26 launcher.
2. Read `GaiaMaster_0.6.35.0_BATCH26_FINAL_REPORT.txt`.
3. Require `222/222` final exact byte verification and source restore PASS.
4. Runtime-test the generated image.
5. Review screenshots/logs for Japanese remnants, clipping, token corruption, intro separators and glyph defects.
6. Do not reopen font work unless runtime evidence proves a glyph issue.
7. Never call Runtime PASS before actual gameplay evidence.

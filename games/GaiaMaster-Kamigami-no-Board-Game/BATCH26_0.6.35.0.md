# Gaia Master PS1 - Batch 26 / 0.6.35.0

Date: 2026-09-14
Branch: `gaia-character-select-font-atlas-reverse-01`

## Goal

Turn the verified Batch 25 exact data into a deterministic production build path without replacing the proven 0.6.10 -> 0.6.14 renderer/font/encoder chain.

Primary builder:

`tools/build_gaia_06350_batch26_final.py`

Windows launcher:

`tools/00_BUILD_0.6.35.0_BATCH26_FINAL_EXACT.cmd`

## Static precedence proof

`checkpoints/0.6.35.0/BATCH26_PRECEDENCE_AUDIT.txt` currently verifies:

```text
Batch25 new exact targets          : 209
Legacy shadow rows required        : 209
Dynamic sink rows required         : 4
0.6.11 exact collisions to mask    : 149
0.6.13 exact collisions to mask    : 23
0.6.14.1 exact collisions to mask  : 2
Global-map preservation entries    : 29
Effective dynamic hits             : 10
Dynamic hits already identical     : 6
Dynamic differing hits sunk        : 4
Dynamic sink failures              : 0
Legacy gate before                 : 397
Legacy gate with wrapper layout    : 397
Final exact mismatches (static)     : 0
Errors                              : 0
RESULT                              : STATIC PRECEDENCE PASS
```

## Wrapper strategy

The wrapper does not patch translated strings into the BIN itself. It stages CSV inputs, calls the proven 0.6.14 production builder, restores every source CSV, then verifies the produced BIN.

### 1. Final exact primaries

For each of the 209 new Batch 25 exact targets:

- `vi_full` is set to the Batch 25 exact wording;
- primary `vi_game_current` is temporarily blanked so 0.6.12 global fallback promotion cannot overwrite it.

### 2. Legacy shadow rows

Every target gets a duplicate shadow row after the primary with the original `vi_game_current` fallback.

This preserves the exact Alpha 0.6.1 legacy reconstruction while the primary remains protected from global promotion.

Verified:

```text
legacy before staging  = 397
legacy during staging  = 397
```

### 3. Exact-layer masking

Only Batch 25 target keys are temporarily removed from older exact tables:

```text
0.6.11 gameplay exact = 149 masked rows
0.6.13 compact exact  = 23 masked rows
0.6.14 compact exact  = 2 masked rows
```

0.6.14 uses the codepage-safe 0.6.14.1 compact table during staging, so the old unsupported `Đồng ý?` form cannot return.

### 4. Global fallback preservation

Filtering 0.6.11 exemplars would otherwise change the 0.6.12 global accent map.

Batch 26 therefore appends 29 temporary rows to the Batch 3 fallback map so the global map seen by non-target rows remains exactly identical to the production baseline.

### 5. Dynamic literal sinks

Ten effective 0.6.14 dynamic literal hits overlap Batch 25 targets.

Six are already identical and need no special handling.

Four differ:

```text
シールド       exact=Mộc      dynamic=Thủ
バトルアックス exact=Rìu đấu  dynamic=Rìu
ジャンビーヤ   exact=Jambia   dynamic=Jamb
ティアラ       exact=Mão      dynamic=Tiar
```

For only these four exact keys, the wrapper inserts a duplicate dynamic sink before the primary row. The sink has the same `file + offset` but an empty Japanese source field. The 0.6.11 dynamic injection writes to the sink first; the 0.6.10 builder cannot emit that non-empty text into a zero-byte source field, so it skips the sink and then processes the real exact primary.

The global dynamic literal table remains intact for every other occurrence.

## Source restoration

`tools/batch26_stage_06350.py` stages and restores:

- all six Translation Master parts;
- `GAMEPLAY_ACCENT_OVERRIDES_0.6.11.0.csv`;
- `BATCH3_FALLBACK_ACCENT_MAP_0.6.12.0.csv`;
- `COMPACT_TRANSLATION_OVERRIDES_0.6.13.0.csv`;
- the live 0.6.14 compact slot.

CI performs a real staging cycle and checks hashes after restore.

Current staging selftest: **PASS**.

## Production builder chain

Batch 26 calls the existing production chain, ending at the readable/proven 0.6.10 exact builder:

```text
0.6.35 Batch26 staging
  -> 0.6.14 Batch5
     -> 0.6.13
        -> 0.6.12
           -> 0.6.11
              -> 0.6.10 exact builder
```

The frozen architecture therefore remains unchanged.

## Clean-ROM gate

The Batch 26 builder accepts only the verified clean Japan BIN:

```text
SHA1 = f4d5298583c90d89c4b7e51d2dde160ee07f2aec
```

## Post-build byte verification

After the inner production chain returns successfully, Batch 26 does not trust exit code alone.

It loads the verified readable 0.6.10 encoder, derives the same frozen codepage from the CLEAN image, reads SLPS/PRGPACK back out of the produced BIN, and requires all final exact candidates to match byte-for-byte:

```text
Batch20 + Batch24 final exact set = 222 keys
required output verification       = 222 / 222
```

Any missing or different field makes the wrapper fail.

## CI state

Current CI checks all pass:

1. static production precedence audit;
2. real CSV staging + restoration selftest;
3. final Batch 26 builder `--selftest` contract.

No clean ROM is stored in GitHub, so CI does not produce the actual game BIN.

## Architecture locks unchanged

```text
native 12x12 / 72-byte / 4bpp / LOW nibble first
static mapping-only
frozen 60-glyph Vietnamese codepage
legacy Alpha coverage gate = 397/397
```

No renderer hook, pointer redirect, 12x16, 6x12, composite overlay, or font retuning without new runtime evidence.

## Status

**0.6.35.0 = BUILD-READY / STATIC PRECEDENCE PASS.**

This is still **not Runtime PASS**.

Next evidence required:

1. run the Batch 26 CMD against the verified CLEAN Japan BIN;
2. require the generated report to show 222/222 final exact byte verification;
3. launch the produced image;
4. inspect screenshots/logs for visible Japanese, clipping, token corruption, intro separators and glyph defects;
5. only then consider promoting the candidate to Runtime PASS.

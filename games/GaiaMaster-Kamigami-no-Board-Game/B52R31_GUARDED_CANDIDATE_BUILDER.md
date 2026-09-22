# B52R31 - Guarded candidate builder

Date: 2026-09-23  
Repo: `RVTGMzz/PSXVH`  
Branch: `gaia-character-select-font-atlas-reverse-01`

## Status

**BUILDER TOOLING READY / EXECUTION GATED ON REAL OWNERSHIP / NO RUNTIME PASS**

B52R31 is the first mutation-capable layer after the B52R30 structural plan.

It is deliberately hard-gated. A build is refused if any identity or checksum expectation differs from the B52R30 plan.

## Files

- `tools/gaia_b52r31_guarded_candidate_builder.py`
- `tools/00_DRYRUN_B52R31_GUARDED_CANDIDATE.cmd`
- `tools/00_BUILD_B52R31_GUARDED_CANDIDATE.cmd`

## Required inputs

1. exact B52R14R1/CLEAN BIN used by B52R30;
2. `GaiaMaster_B52R30_PATCH_PLAN.json`;
3. the exact replacement blob that was already simulated by B52R30.

B52R30 was strengthened to store:
- candidate SHA1;
- optional payload SHA1;
- replacement SHA1;
- full BDP ancestry;
- expected bottom-up checksum changes;
- simulated logical-file SHA1.

## Guards before any build

B52R31 verifies:
- input BIN SHA1 equals the plan;
- ISO path, extent and file size equal the plan;
- current candidate bytes SHA1 equal the plan;
- replacement length and SHA1 equal the simulated replacement;
- current BDP ancestry exactly equals the recorded ancestry;
- recalculated checksum changes exactly equal the plan;
- simulated logical-file SHA1 exactly equals the plan.

If any guard differs, build stops.

## Dry-run

Default execution performs all guards and writes only:

`GaiaMaster_B52R31_GUARDED_BUILD_REPORT.txt`

No BIN/CUE is created.

## Build mode

Only `--build` mutates an output copy.

Build flow:
1. copy the exact input BIN to a new output path;
2. write only changed bytes in the target ISO logical file;
3. use the B52R30 bottom-up BDP checksum result;
4. regenerate MODE2/Form1 EDC/ECC for every actually changed raw sector;
5. verify no changed sector falls outside the B52R30 planned LBA set;
6. read the logical file back from the output BIN;
7. require byte-for-byte equality with the B52R30 simulated file;
8. require replacement readback;
9. revalidate all proven BDP ancestor checksums;
10. create a matching CUE.

The input BIN is never overwritten.

## Validation

Authoring validation:
- `python -m py_compile`: PASS
- **B52R31 GUARDED CANDIDATE BUILDER SELFTEST PASS**

The self-test reuses a nested BDP model and proves that plan identity, replacement identity and checksum simulation guards agree.

## Promotion rule

Having a valid B52R30 plan is not enough to justify running build mode.

Build mode should only be used after real evidence has established:
- visible target-frame ownership;
- the correct disc/archive candidate;
- the intended replacement bytes.

A successful B52R31 build is only a **static build/readback PASS**. Runtime validation still must be performed by the user.

Overall Runtime PASS remains **NO**.

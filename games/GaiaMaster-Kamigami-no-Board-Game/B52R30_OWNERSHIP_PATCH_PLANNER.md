# B52R30 - Ownership verifier + guarded patch planner

Date: 2026-09-23  
Repo: `RVTGMzz/PSXVH`  
Branch: `gaia-character-select-font-atlas-reverse-01`

## Status

**TOOLING READY / REAL OWNERSHIP CANDIDATE PENDING / READ-ONLY**

B52R30 is the structural gate between provenance evidence and any future disc mutation.

It does not identify the live UI by itself and it never writes BIN/CUE/ISO.

## Files

- `tools/gaia_b52r30_ownership_patch_planner.py`
- `tools/00_PLAN_B52R30_FROM_B52R27.cmd`

## Inputs

Preferred route:
1. exact B52R14R1 BIN;
2. B52R27 candidate CSV;
3. B52R24 `DMA_SOURCE.bin`;
4. optional candidate row number;
5. optional same-length replacement blob for dry-run checksum simulation.

Manual route is also supported with explicit `--file --offset --length`.

The exact known BIN SHA1 contract is enforced.

## What it verifies

For the selected ISO file/range B52R30:
- resolves the ISO9660 file and extent;
- verifies optional payload bytes exactly match the candidate offset;
- enumerates checksum-valid BDP containers;
- follows exact member boundaries recursively where available;
- also recognizes checksum-valid inferred-end BDP islands;
- lists every valid BDP owner containing the complete candidate range;
- records the member index for each owner when uniquely determined;
- reports candidate LBA/raw BIN offset;
- reports each ancestor checksum field and its LBA;
- computes the union of raw sectors that a future patch/checksum rewrite would touch.

Outputs:
- `GaiaMaster_B52R30_OWNERSHIP_PATCH_PLAN.txt`
- `GaiaMaster_B52R30_BDP_ANCESTRY.csv`
- `GaiaMaster_B52R30_PATCH_PLAN.json`

## Optional replacement simulation

When a replacement blob is supplied:
- replacement length must exactly equal the candidate length;
- the logical ISO file is mutated only in memory;
- BDP checksums are recalculated **deepest -> outermost**;
- all simulated checksum changes are recorded;
- all affected containers are revalidated after the bottom-up repair;
- no disc image is written.

This is specifically designed around Gaia Master's proven nested-BDP checksum behavior.

## Validation

Authoring validation:
- `python -m py_compile`: PASS
- **B52R30 OWNERSHIP/PATCH PLANNER SELFTEST PASS**

The self-test constructs a nested parent/child BDP, changes bytes in the child payload, repairs the child first and parent second, and verifies both checksums afterward.

## Evidence rules

B52R30 is not an ownership discovery tool. The candidate must come from stronger evidence such as:
- B52R27 exact payload fingerprint;
- a corroborated B52R28 file/LBA candidate;
- later archive/member provenance.

A BDP ancestry result only describes the structural checksum obligations around that already-supported candidate.

If no valid BDP owner is found, do not manufacture one. Use the candidate file's actual format contract instead.

## Promotion gate

Only after a real candidate has:
1. target-frame runtime correlation;
2. disc/archive ownership evidence;
3. B52R30 structural/checksum plan;

may a future guarded builder be allowed to mutate an output copy.

Any actual raw-sector mutation must regenerate MODE2/Form1 EDC/ECC for every touched sector.

Overall Runtime PASS remains **NO**.

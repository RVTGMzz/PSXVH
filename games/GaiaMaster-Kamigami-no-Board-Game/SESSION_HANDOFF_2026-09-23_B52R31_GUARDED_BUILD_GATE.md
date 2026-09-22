# SESSION HANDOFF - 2026-09-23 - B52R31 guarded build gate

Repo: `RVTGMzz/PSXVH`  
Branch: `gaia-character-select-font-atlas-reverse-01`

## Current authority

Exact working base remains B52R14R1:

`0ced9982e1b00566b42ace047236378826c2aa1c`

CLEAN Japan:

`f4d5298583c90d89c4b7e51d2dde160ee07f2aec`

No newer runtime build has been promoted.

## New tooling this session

### B52R30
Ownership verifier + patch planner:
- exact ISO candidate identity;
- checksum-valid BDP ancestry;
- member ownership where provable;
- candidate/checksum/touched LBAs;
- optional in-memory same-length replacement simulation;
- bottom-up nested BDP checksum repair simulation;
- PATCH_PLAN.json with candidate/replacement SHA1 and full ancestry.

Validation:
- compile PASS
- B52R30 self-test PASS

### B52R31
Guarded builder:
- dry-run default;
- build requires exact B52R30 plan identity;
- writes only to a copied output BIN;
- refuses source/replacement/ancestry/checksum-plan drift;
- regenerates MODE2/Form1 EDC/ECC;
- logical-file + replacement + BDP checksum readback required;
- CUE generated only after static verification.

Validation:
- compile PASS
- B52R31 self-test PASS

## Critical gate

B52R30/B52R31 do not solve the missing runtime evidence.

Before build mode:
1. correlate visible `ストーリーモード` with a real B52R24 transaction;
2. prove/corroborate disc/archive ownership using B52R27/B52R28/B52R25/B52R29 as applicable;
3. run B52R30 on that exact candidate;
4. prepare exact same-length replacement and rerun B52R30 with replacement simulation;
5. run B52R31 dry-run;
6. only then consider B52R31 build.

No source-found claim, no ownership-found claim and no overall Runtime PASS yet.

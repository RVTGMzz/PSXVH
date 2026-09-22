# B52R32 - Capture session manager

Date: 2026-09-23  
Repo: `RVTGMzz/PSXVH`  
Branch: `gaia-character-select-font-atlas-reverse-01`

## Status

**WORKFLOW TOOLING READY / NO RUNTIME EVIDENCE CREATED BY ITSELF**

B52R32 is not another reverse probe. It is the workflow controller for B52R22-B52R31.

The goal is to stop requiring the user to remember which report/Lua/trace belongs to which batch.

## Files

- `tools/gaia_b52r32_capture_session_manager.py`
- `tools/00_CHECK_B52R32_SESSION.cmd`
- `tools/00_ADVANCE_B52R32_READONLY.cmd`

## Modes

### Status-only

`00_CHECK_B52R32_SESSION.cmd`

Given exact B52R14R1/CLEAN BIN, it:
- verifies SHA1;
- scans the BIN folder for known B52R22-B52R31 evidence outputs;
- reports which stages are present/missing;
- prints one next action;
- writes:
  - `GaiaMaster_B52R32_SESSION_STATUS.txt`
  - `GaiaMaster_B52R32_SESSION_STATUS.json`

It runs no probes.

### Safe read-only advance

`00_ADVANCE_B52R32_READONLY.cmd`

It may automatically run, when prerequisites exist:
- B52R22 static probe;
- B52R23 GPU/DMA locator;
- B52R24 Lua generator;
- B52R24 analyzer;
- B52R27 disc fingerprint;
- B52R25 writer-watch generator;
- B52R25 writer-PC resolver;
- B52R29 overlay fingerprint resolver;
- B52R28 Lua generator/analyzer;
- B52R30 read-only structural planner when B52R27 contains exactly one `EXACT` candidate.

It does not perform emulator actions.

## Hard stops

B52R32 always stops for:
- B52R24 PCSX capture;
- B52R25 PCSX writer capture;
- B52R28 PCSX CD provenance capture;
- ambiguous multiple B52R27 EXACT candidates;
- B52R31 replacement/build gate.

B52R32 never invokes B52R31 build mode.

## Next-action logic

Examples:
- missing B52R23 CSV -> run B52R23;
- B52R24 Lua exists but TRACE missing -> tell user exactly to load Lua, call `gaia_arm24()`, enter green menu, then `gaia_save24()`;
- B52R25 Lua exists but writer trace missing -> tell user to `gaia_arm25()` then `gaia_save25()`;
- B52R28 Lua exists but trace missing -> explain `gaia_arm26()` / `gaia_save26()`;
- one B52R27 EXACT candidate -> B52R30 can be run read-only automatically;
- multiple EXACT candidates -> require runtime/provenance disambiguation;
- B52R30 plan exists -> stop at the B52R31 guarded dry-run/build gate.

## Safety

B52R32:
- never modifies BIN/CUE/ISO;
- never calls a builder;
- never promotes static evidence into Runtime PASS;
- never treats an exact disc fingerprint alone as visible-target proof.

## Validation

Authoring validation:
- `python -m py_compile`: PASS
- **B52R32 CAPTURE SESSION MANAGER SELFTEST PASS**

Self-test verifies:
- empty workspace starts at B52R22;
- an existing B52R24 Lua without TRACE correctly becomes a RUNTIME stop;
- exact-row parsing for B52R27 works.

Overall Runtime PASS remains **NO**.

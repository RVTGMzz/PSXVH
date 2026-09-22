# SESSION HANDOFF - 2026-09-23 - B52R32 capture session manager

Repo: `RVTGMzz/PSXVH`  
Branch: `gaia-character-select-font-atlas-reverse-01`

## Authority

Exact working base remains B52R14R1:

`0ced9982e1b00566b42ace047236378826c2aa1c`

No newer runtime build has been promoted.

## New preferred entry point

Use:

`tools/00_ADVANCE_B52R32_READONLY.cmd`

with exact B52R14R1.

B52R32:
- verifies SHA1;
- scans B52R22-B52R31 evidence files;
- automatically runs safe static/read-only stages;
- generates downstream Lua when prerequisites exist;
- stops at manual PCSX steps;
- stops at ambiguous ownership;
- never invokes B52R31 build;
- writes one next-action status report.

Outputs:
- `GaiaMaster_B52R32_SESSION_STATUS.txt`
- `GaiaMaster_B52R32_SESSION_STATUS.json`

Validation:
- compile PASS
- B52R32 self-test PASS

## Current real-evidence state

Still pending:
- real B52R24 target-frame capture;
- live source proof;
- disc/archive ownership proof;
- real B52R30 candidate plan;
- B52R31 runtime build/test.

No overall Runtime PASS.

## Likely first runtime stop

After B52R32 auto-runs B52R22/B52R23 and generates B52R24 Lua:

1. PCSX-Redux interpreter + debugger.
2. Load `GaiaMaster_B52R24_PCSX_DMA_SOURCE_CAPTURE.lua`.
3. Immediately before the green main menu call `gaia_arm24()`.
4. Enter the menu.
5. On pause call `gaia_save24()`.
6. Run B52R32 read-only advance again.

The first visual target remains `ストーリーモード`.

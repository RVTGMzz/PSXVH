# NF2R1 - Cache Fill Helper Probe

Date: 2026-09-28

## Why NF2 V1 was refined

The first NF2 scan against exact B52R14R1 found:

- three high-confidence cache-hit reads from record offset +6;
- no direct +6 write inside the known cache-miss window;
- many direct +6 writes elsewhere that are clearly unrelated UI/struct code.

Therefore direct-offset writer ranking is too broad for the miss path.

## Stronger static contract

At the known cache-miss caller:

```
0x8003CC30  addu a0,s1,zero
0x8003CC34  lw   a2,100(s1)
0x8003CC38  jal  0x8003C67C
0x8003CC40  return site
```

Since `state+0x64` is the known cache write pointer, this gives a much stronger target:

- `a0` = renderer state;
- `a2` = destination cache record;
- helper = `0x8003C67C`.

## New files

- `tools/gaia_nf2r1_cache_fill_helper_probe.py`
- `tools/00_RUN_NF2R1_CACHE_FILL_HELPER_PROBE.cmd`

The generator verifies the caller instruction contract before producing runtime tooling.

Outputs:

- `GaiaMaster_NF2R1_CACHE_FILL_HELPER_REPORT.txt`
- `GaiaMaster_NF2R1_PCSX_CACHE_FILL_CAPTURE.lua`

## Runtime capture

Lua breakpoints:

1. helper entry `0x8003C67C`, filtered to `RA == 0x8003CC40`;
2. caller return site `0x8003CC40`.

At entry:
- state pointer;
- destination cache-record pointer;
- 16 record bytes before fill;
- byte6 before fill;
- state tracking/special/normal width fields;
- cursor X;
- glyph count;
- relevant GPR snapshot.

At return:
- helper return `v0`;
- same 16 record bytes after fill;
- byte6 after fill;
- cursor X after helper.

Helpers:
- `gaia_arm_nf2r1()`
- `gaia_next_nf2r1()`
- `gaia_disarm_nf2r1()`
- `gaia_save_nf2r1()`

## Decision rule

If byte6 is populated/changed by this helper and correlates with the caller's computed advance, NF2 should target this local fill path.

If byte6 is not changed here, the trace still identifies the exact record pointer, so the next probe can place a memory write watch on `record+6` instead of searching all executable stores.

No VWF ROM patch yet.

Overall Runtime PASS remains **NO**.

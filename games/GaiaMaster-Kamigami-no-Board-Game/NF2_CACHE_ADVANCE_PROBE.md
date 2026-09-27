# NF2 - Cache Advance Writer Probe

Date: 2026-09-28
Branch: `gaia-new-vietnamese-font-experiment-01`

## Purpose

Find the smallest safe insertion point for variable-width font metrics.

Previous reverse work already established:

- cache hit uses `cache_record.byte6` as horizontal advance;
- cache miss computes advance from `state+0x3E` or `state+0x40 + 1`;
- `state+0x3C` may add tracking.

This is much better than starting from a global cursor hook.

The preferred NF2 architecture is now:

`character/glyph -> width lookup -> cache_record.byte6 -> existing Gaia cursor logic`

rather than rewriting cache stride, VRAM geometry or global cursor state.

## Files

- `tools/gaia_nf2_cache_advance_probe.py`
- `tools/00_RUN_NF2_CACHE_ADVANCE_PROBE.cmd`

## Static phase

The probe:

1. verifies exact CLEAN or B52R14R1 whole-BIN SHA1;
2. extracts SLPS;
3. scans MIPS code for direct memory operations at immediate offset `+6`;
4. ranks cache-miss/cache-hit candidates;
5. boosts candidates near reads of `state+0x3C/+0x3E/+0x40`;
6. records recent definitions of the value register;
7. writes full disassembly context.

Outputs:

- `GaiaMaster_NF2_CACHE_ADVANCE_REPORT.txt`
- `GaiaMaster_NF2_CACHE_ADVANCE_CANDIDATES.csv`

## Runtime capture

The same probe also generates:

`GaiaMaster_NF2_PCSX_ADVANCE_CAPTURE.lua`

The Lua installs Exec breakpoints on the highest-ranked direct `+6` writers.

At the breakpoint, before the store executes, it records:

- PC / RA;
- cache-record base register + value;
- source advance register + low-byte advance value;
- 16 bytes of cache record before the write;
- A0-A3;
- candidate score/window.

Helpers:

- `gaia_arm_nf2()`
- `gaia_next_nf2()`
- `gaia_disarm_nf2()`
- `gaia_save_nf2()`

## Why breakpoint before the store matters

If the candidate is really:

`sb width,6(record)`

then the width source register still contains the exact value Gaia is about to cache.

That is stronger evidence than patching cursor X and observing spacing afterward.

## Promotion gate

NF2 does not patch the ROM yet.

A VWF runtime patch is allowed only after:

1. a candidate direct `cache_record+6` writer is statically identified;
2. runtime capture correlates that writer with visible target text;
3. repeated glyph events show stable source-width behavior;
4. the smallest width-source substitution site is understood.

Preferred patch:

**replace/override the width value locally before cache byte6 is written.**

Avoid repeating historical:
- global cache-stride rewrites;
- pointer redirect hooks;
- extended-height allocator changes.

Overall Runtime PASS remains **NO**.

## Superseded runtime action

Real B52R14R1 results showed the broad +6 writer ranking contains many unrelated struct/UI writes and no direct +6 write inside the cache-miss window. Do **not** use the original 8-breakpoint NF2 Lua for promotion evidence.

Use NF2R1 instead:

- `gaia_nf2r1_cache_fill_helper_probe.py`
- `GaiaMaster_NF2R1_PCSX_CACHE_FILL_CAPTURE.lua`

NF2R1 targets the verified cache-fill helper call at `0x8003CC38 -> 0x8003C67C` and compares the exact cache record before/after the helper.

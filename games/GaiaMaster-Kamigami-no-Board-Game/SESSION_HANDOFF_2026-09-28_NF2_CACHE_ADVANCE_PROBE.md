# SESSION HANDOFF - 2026-09-28 - NF2 Cache Advance Probe

Repo: `RVTGMzz/PSXVH`
Branch: `gaia-new-vietnamese-font-experiment-01`

## Font direction

Current visual target is no longer NF1 V0.1.

Reference direction:
- complete Vietnamese charset;
- thin PS1-style strokes matching the supplied Yu-Gi-Oh runtime screenshots;
- original-game-like vertical metrics;
- proportional per-glyph spacing.

Prepared source layers:
- NF1 V0.2 full charset: 95 printable ASCII + 134 Vietnamese non-ASCII = 229 glyphs;
- NF1 V0.3 width metadata for future proportional rendering.

## Runtime capacity fact

Current proven mapping-only custom capacity:
- 60 production slots
- 4 reserve slots
- 64 total

Complete Vietnamese non-ASCII source:
- 134 glyphs

Proven custom-slot shortage:
- 70 glyphs

Therefore source completeness and runtime storage are now separate concerns.

## NF2 breakthrough direction

Old spacing reverse proves Gaia already caches per-glyph horizontal advance in `cache_record.byte6`.

Known formula:
- cache hit: use record byte6;
- cache miss: `state+0x3E` OR `state+0x40+1`;
- optional tracking: `state+0x3C`.

New read-only tool:
`tools/gaia_nf2_cache_advance_probe.py`

Launcher:
`tools/00_RUN_NF2_CACHE_ADVANCE_PROBE.cmd`

Outputs next to the BIN:
- `GaiaMaster_NF2_CACHE_ADVANCE_REPORT.txt`
- `GaiaMaster_NF2_CACHE_ADVANCE_CANDIDATES.csv`
- `GaiaMaster_NF2_PCSX_ADVANCE_CAPTURE.lua`

## Next action

Run the launcher on exact B52R14R1:

`0ced9982e1b00566b42ace047236378826c2aa1c`

Then inspect the report/CSV.

If a strong direct `cache_record+6` writer is found:
1. load the generated Lua in PCSX-Redux interpreter/debugger;
2. call `gaia_arm_nf2()` before a known visible text line;
3. reproduce the line;
4. when paused call `gaia_save_nf2()`;
5. use `gaia_next_nf2()` for subsequent glyph writes.

## Hard gate

No VWF ROM build yet.

Preferred future patch is a **local width-source substitution before cache byte6 is written**.

Do not modify:
- global cache stride;
- VRAM row geometry;
- extended-height allocator;
- broad pointer redirection.

Overall Runtime PASS remains NO.

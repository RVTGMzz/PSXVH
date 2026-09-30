# SESSION HANDOFF - 2026-09-30 - Gaia New Vietnamese Font / NF2R1

Repo: `RVTGMzz/PSXVH`

Active branch:
`gaia-new-vietnamese-font-experiment-01`

Parent/canonical reverse branch:
`gaia-character-select-font-atlas-reverse-01`

## Authority

Exact B52R14R1 base:

`0ced9982e1b00566b42ace047236378826c2aa1c`

SLPS SHA1:

`267a2b12d01b3ecc5d657ce8c5e9f4108c56a5fd`

CLEAN Japan:

`f4d5298583c90d89c4b7e51d2dde160ee07f2aec`

No newer runtime base has been promoted.

## Font decision

Stop polishing the old patched-looking font.

NF1 V0.1:
- technical proof only;
- 122 newly drawn glyphs;
- not final visual target.

User supplied a more complete Vietnamese PS1 pixel font reference and prefers that direction.

Current visual target:
- thin/clean strokes;
- full Vietnamese uppercase + lowercase coverage;
- accents with proper headroom;
- vertical rhythm close to native English font;
- proportional-looking spacing.

## NF1 V0.2 - complete source charset

Prepared:
- 95 printable ASCII;
- 67 uppercase Vietnamese non-ASCII;
- 67 lowercase Vietnamese non-ASCII;
- **229 total source glyphs**.

Vietnamese non-ASCII total:
**134**.

Current proven custom mapping-only runtime capacity:
**64 slots**.

Shortage for complete Vietnamese non-ASCII runtime set:
**70 slots**.

Therefore:
- source charset stays complete;
- runtime storage/codepage is a separate NF2 problem;
- never shrink source back to 60 just to fit the old allocation.

## NF1 V0.3 - proportional design metrics

Prepared:
- per-glyph ink width;
- proposed per-glyph advance;
- proportional preview.

Reference screenshots supplied by user show Vietnamese and original English text with similar visible vertical height, supporting the goal of preserving native vertical rhythm.

V0.3 metrics are design data only. Gaia runtime does not use them yet.

## Real NF2 scan - COMPLETED

User ran the read-only NF2 scanner successfully on exact B52R14R1.

Observed:
- 347 immediate `+6` memory xrefs;
- cache-hit reads confirmed at:
  - `0x8003CB54 lbu v0,6(a0)`
  - `0x8003CBF4 lbu v1,6(a0)`
  - `0x8003CC08 lbu v1,6(a0)`

This supports the existing model:
- cache hit advance = `cache_record.byte6`;
- cache miss advance = `state+0x3E` or `state+0x40 + 1`;
- optional tracking = `state+0x3C`.

Critical result:
- no direct `+6 WRITE` was found inside the known cache-miss window;
- broad write candidates elsewhere are mostly unrelated struct/UI initialization/copy code.

Therefore:
**do not use the original 8-breakpoint NF2 Lua for promotion evidence.**

## NF2R1 - current reverse target

Verified caller:

```
0x8003CC30  addu a0,s1,zero
0x8003CC34  lw   a2,100(s1)
0x8003CC38  jal  0x8003C67C
0x8003CC40  return site
```

Interpretation:
- `a0` = renderer state;
- `a2` = `state+0x64`, known cache write pointer;
- helper `0x8003C67C` fills/copies the cache record.

Prepared:
- `tools/gaia_nf2r1_cache_fill_helper_probe.py`
- `tools/00_RUN_NF2R1_CACHE_FILL_HELPER_PROBE.cmd`
- `NF2R1_CACHE_FILL_HELPER_PROBE.md`

Generated runtime Lua:
`GaiaMaster_NF2R1_PCSX_CACHE_FILL_CAPTURE.lua`

NF2R1 compares the same cache record:
- before helper;
- after helper;
- byte6 before/after;
- helper return `v0`;
- state+3C / 3E / 40;
- cursor X;
- relevant registers.

## Exact next action

User has **not yet returned NF2R1 runtime TSV**.

Keep instructions simple:

1. Run exact B52R14R1 in PCSX-Redux Interpreter/Debugger.
2. Load/run `GaiaMaster_NF2R1_PCSX_CACHE_FILL_CAPTURE.lua`.
3. Type:
   `gaia_arm_nf2r1()`
4. Let any visible text line appear/re-enter.
5. When game pauses, type:
   `gaia_save_nf2r1()`
6. Send:
   `GaiaMaster_NF2R1_CACHE_FILL_TRACE.tsv`

One event is enough for first analysis.

## What to analyze from TSV

Compare:
- `pre_byte6`
- `post_byte6`
- `return_v0`
- `special` = state+0x3E
- `normal` = state+0x40
- `track` = state+0x3C
- pre/post 16-byte cache record

If helper populates byte6 consistently:
- identify the smallest local width-source substitution point;
- only then design NF2 width-table patch.

If helper does not change byte6:
- use the exact captured record pointer;
- watch only `record+6` at runtime;
- do not return to whole-executable writer scanning.

## Hard safety gates

Do not:
- build VWF ROM yet;
- rewrite global cache stride;
- redirect global font pointers;
- replay old extended-height allocator experiments;
- claim full 229-glyph runtime support;
- claim overall Runtime PASS.

Preferred future architecture:
`glyph/code -> custom width lookup -> cache_record.byte6 -> existing Gaia cursor logic`.

## Canonical B52 state

The parent B52 UI live-source reverse remains unresolved for still-Japanese UI. Do not regress into already-closed plaintext/TIM/JIS paths.

This font branch is intentionally separate from that unresolved ownership problem.

Overall Runtime PASS remains **NO**.

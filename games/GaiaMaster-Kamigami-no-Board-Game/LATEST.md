# Gaia Master - trạng thái mới nhất

Cập nhật: **2026-09-30**

Repo: `RVTGMzz/PSXVH`

Active font branch:
`gaia-new-vietnamese-font-experiment-01`

Canonical reverse parent:
`gaia-character-select-font-atlas-reverse-01`

## Current exact base

B52R14R1:

`0ced9982e1b00566b42ace047236378826c2aa1c`

CLEAN Japan:

`f4d5298583c90d89c4b7e51d2dde160ee07f2aec`

No newer runtime base has been promoted.

## Two workstreams

### 1. Canonical UI live-source reverse

The B52R22-B52R32 reverse/tooling chain remains preserved on the parent branch.

Known dead paths stay closed:
- known PRGPACK CP932 copies are runtime-dead for the still-Japanese main menu / Character Select / chapter UI;
- do not repeat raw TIM, alternate encoding, JIS/tile-index or the same PRGPACK patch path.

Overall source ownership for those still-Japanese screens remains unresolved.

### 2. New Vietnamese font experiment - ACTIVE

The user rejected continued polishing of the old patched-looking font.

Current visual direction comes from supplied PS1 Vietnamese reference screenshots:
- thin, clean strokes;
- complete Vietnamese alphabet;
- vertical metrics close to the original English font;
- proportional spacing.

NF1 V0.1:
- technical proof only;
- not final visual target.

NF1 V0.2:
- 95 printable ASCII glyphs;
- 134 Vietnamese non-ASCII glyphs;
- **229 source glyphs total**.

NF1 V0.3:
- per-glyph ink width;
- proposed per-glyph advance width;
- proportional preview tooling.

Current proven custom mapping-only capacity is only 64 slots, so the full 134 Vietnamese non-ASCII set cannot be honestly claimed to fit the current custom allocation.

## NF2 real scan result

A real NF2 scan was run successfully on exact B52R14R1.

Verified:
- BIN SHA1 `0ced9982e1b00566b42ace047236378826c2aa1c`;
- SLPS SHA1 `267a2b12d01b3ecc5d657ce8c5e9f4108c56a5fd`;
- **347 memory xrefs using immediate offset +6**.

High-confidence font cache-hit reads:
- `0x8003CB54  lbu v0,6(a0)`
- `0x8003CBF4  lbu v1,6(a0)`
- `0x8003CC08  lbu v1,6(a0)`

These reinforce the existing spacing model:
- cache hit advance comes from `cache_record.byte6`;
- cache miss uses `state+0x3E` or `state+0x40 + 1`;
- `state+0x3C` is optional tracking.

Important negative result:
- **no direct +6 write was found inside the known cache-miss window**.

Therefore the original broad NF2 8-breakpoint Lua is **superseded**.

## NF2R1 - current target

Static caller contract:

```
0x8003CC30  addu a0,s1,zero
0x8003CC34  lw   a2,100(s1)
0x8003CC38  jal  0x8003C67C
0x8003CC40  helper return site
```

Interpretation:
- `a0` = renderer state;
- `a2` = `state+0x64`, known cache write pointer;
- helper `0x8003C67C` is now the cleanest place to compare the cache record before/after fill.

Prepared:
- `tools/gaia_nf2r1_cache_fill_helper_probe.py`
- `tools/00_RUN_NF2R1_CACHE_FILL_HELPER_PROBE.cmd`
- `NF2R1_CACHE_FILL_HELPER_PROBE.md`

NF2R1 runtime capture is **PENDING**.

## Next action

Keep this simple:

1. Run `00_RUN_NF2R1_CACHE_FILL_HELPER_PROBE.cmd` with exact B52R14R1.
2. Load generated `GaiaMaster_NF2R1_PCSX_CACHE_FILL_CAPTURE.lua` in PCSX-Redux Interpreter/Debugger.
3. Call `gaia_arm_nf2r1()`.
4. Show/re-enter a visible text line.
5. When PCSX pauses, call `gaia_save_nf2r1()`.
6. Return `GaiaMaster_NF2R1_CACHE_FILL_TRACE.tsv`.

One event is enough for the first analysis.

## Hard gates

Do not:
- use the old 8-breakpoint NF2 Lua for promotion evidence;
- build a VWF ROM yet;
- rewrite global cache stride;
- redirect font pointers globally;
- reuse unsafe extended-height/cache experiments;
- claim full 229-glyph runtime support yet;
- claim overall Runtime PASS.

Preferred future NF2 patch, only after runtime proof:
**local width-source substitution in the verified cache-fill path**.

## Release engineering

Lessons adopted from `2ez4gcx/yugioh-fm-vi-patch`:
- Windows launchers forced to CRLF;
- raw disc images ignored by Git;
- future public release should be patch-only, preferably PPF 3.0;
- publish exact CLEAN and patched SHA-256;
- never overwrite the user's original disc.

Overall Runtime PASS: **NO**.

# B52R25 - Source-buffer writer watch

Date: 2026-09-21  
Repo: `RVTGMzz/PSXVH`  
Branch: `gaia-character-select-font-atlas-reverse-01`

## Status

**TOOLING READY / REAL WRITER HIT PENDING / NO DISC-SOURCE CLAIM**

B52R25 begins only after B52R24 has captured a linear GPU DMA transaction that is correlated with the visible target UI.

It does not patch a ROM.

## Tools

- `tools/gaia_b52r25_writer_watch_generator.py`
- `tools/gaia_b52r25_writer_pc_resolver.py`
- `tools/00_BUILD_B52R25_WRITER_WATCH.cmd`
- `tools/00_RESOLVE_B52R25_WRITER_PC.cmd`

## Writer-watch generator

Input:

`GaiaMaster_B52R24_TRACE.tsv`

Supported:
- DMA2 SyncMode 0
- DMA2 SyncMode 1

Not treated as a linear asset source:
- SyncMode 2 linked-list command memory

For supported linear captures the generator:
- derives MADR/BCR/CHCR;
- calculates the watched physical RAM range;
- mirrors the watch over KSEG0 and KSEG1 aliases;
- generates `GaiaMaster_B52R25_PCSX_SOURCE_WRITER_WATCH.lua`.

Runtime helpers:
- `gaia_arm25()`: catch the next distinct writer PC;
- `gaia_arm25(N)`: skip N distinct writer PCs first;
- `gaia_next25()`: arm and resume;
- `gaia_save25()`: write `GaiaMaster_B52R25_WRITER_TRACE.tsv` **and** `GaiaMaster_B52R25_WRITER_RAM.bin` (2 MiB writer-time RAM snapshot).

The Write breakpoint callback records:
- actual write address/width/cause;
- PC / RA / SP;
- A0 / A1 / A2 / A3.

The callback is wrapped in `pcall`.

## Writer-PC resolver

Inputs:
- `GaiaMaster_B52R25_WRITER_TRACE.tsv`
- exact B52R14R1 BIN or exact CLEAN BIN

The resolver:
- verifies the known SHA1 contract;
- extracts `SLPS_020.75`;
- maps a writer PC inside the main PS-X EXE text to exact SLPS file offset;
- finds a heuristic function start;
- lists direct `jal` callers;
- prints a +/-12-instruction MIPS context;
- classifies BIOS hits;
- classifies RAM code outside the main EXE as likely overlay/runtime-loaded code rather than pretending it belongs to SLPS.

Output:

`GaiaMaster_B52R25_WRITER_RESOLVE.txt`

## Validation

Local authoring validation:
- writer-watch generator py_compile PASS
- **B52R25 WRITER WATCH GENERATOR SELFTEST PASS**
- writer-PC resolver py_compile PASS
- **B52R25 WRITER PC RESOLVER SELFTEST PASS**

## Evidence rules

A writer breakpoint hit proves that a specific CPU instruction wrote into the watched DMA-source RAM range.

It does not yet prove:
- the disc/archive bytes that fed the writer;
- that the first writer is semantically interesting rather than a clear/memset step;
- that a writer outside the main EXE belongs to a particular overlay.

Use `gaia_arm25(N)` to skip earlier distinct writer PCs when needed.

If the resolved writer PC is a decompressor/rasterizer/copy routine inside the main EXE, inspect its callers and arguments next.

If the writer PC is runtime-loaded RAM code outside SLPS text, the next step is overlay ownership mapping.

If no CPU writer breakpoint fires even when armed before the transition, the source may be filled by hardware DMA; then pivot to CD/DMA load ownership rather than CPU write tracing.

## Promotion gate

Only after a concrete writer/load path is tied to the B52R24 target transaction should the project identify the disc/archive member and make a smallest reversible patch.

Overall Runtime PASS remains **NO**.


## B52R29 bridge

If a real writer PC is in main RAM but outside the main `SLPS_020.75` text mapping, keep the new `GaiaMaster_B52R25_WRITER_RAM.bin` snapshot and use:

`B52R29_OVERLAY_WRITER_FINGERPRINT.md`

B52R29 fingerprints code bytes around the writer PC against ISO9660 Form1 files. This can identify the owner of raw overlay code, but not automatically the source data that produced the visible UI.

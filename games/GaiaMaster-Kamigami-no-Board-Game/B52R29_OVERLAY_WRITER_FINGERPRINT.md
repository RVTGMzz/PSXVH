# B52R29 - Overlay writer fingerprint resolver

Date: 2026-09-22  
Repo: `RVTGMzz/PSXVH`  
Branch: `gaia-character-select-font-atlas-reverse-01`

## Status

**TOOLING READY / REAL WRITER SNAPSHOT PENDING / NO OVERLAY-OWNER CLAIM**

B52R29 handles the case where B52R25 catches a source-buffer writer PC in main RAM but outside the main `SLPS_020.75` text mapping.

## B52R25 prerequisite update

`gaia_save25()` now saves both:

- `GaiaMaster_B52R25_WRITER_TRACE.tsv`
- `GaiaMaster_B52R25_WRITER_RAM.bin`

The RAM snapshot is exactly 2 MiB and is taken while paused on the writer hit.

## Tool

- `tools/gaia_b52r27_overlay_fingerprint_resolver.py`
- `tools/00_RESOLVE_B52R29_OVERLAY_FINGERPRINT.cmd`

Inputs:

1. `GaiaMaster_B52R25_WRITER_TRACE.tsv`
2. `GaiaMaster_B52R25_WRITER_RAM.bin`
3. exact B52R14R1 or CLEAN BIN

## Method

For each writer PC:
- PCs inside the main PS-X EXE text are delegated back to the B52R25 writer-PC resolver;
- RAM PCs outside the main EXE are treated as overlay/runtime-loaded candidates;
- code bytes around the physical writer PC are taken from the writer-time RAM snapshot;
- exact anchors are tried in descending strength: 96, 64, 48, 32 bytes;
- ISO9660 Form1 files are searched for the same anchor;
- surrounding 256-byte context similarity is calculated;
- matching file path, file offset, LBA and raw BIN offset are reported.

Outputs:

- `GaiaMaster_B52R29_OVERLAY_FINGERPRINT_REPORT.txt`
- `GaiaMaster_B52R29_OVERLAY_FINGERPRINTS.csv`

Interpretation:
- exact 96/64-byte anchors with high context similarity are strong raw-overlay code-owner candidates;
- 48/32-byte anchors need more corroboration;
- no match can mean decompression, relocation, runtime patching, or that the overlay changed/unloaded before snapshot.

Finding the owner of the **writer code** is not the same as finding the disc bytes that produced the visible Japanese UI.

## Validation

Authoring validation:
- compile PASS
- **B52R29 OVERLAY FINGERPRINT RESOLVER SELFTEST PASS**

The committed B52R25 generator was also verified to contain:
- `_WRITER_RAM.bin`
- the 2 MiB `ffi.string(mem,0x200000)` snapshot
- a self-test guard for RAM-snapshot generation

## Promotion gate

B52R29 becomes actionable only after a real B52R25 writer hit outside the main SLPS text.

A strong overlay code-owner candidate should then be combined with writer arguments/read provenance before any asset/data patch is proposed.

Overall Runtime PASS remains **NO**.

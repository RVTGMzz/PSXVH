# B52R24 - Runtime DMA source capture

Date: 2026-09-21  
Repo: `RVTGMzz/PSXVH`  
Branch: `gaia-character-select-font-atlas-reverse-01`

## Status

**TOOLING READY / RUNTIME CAPTURE PENDING / NO SOURCE-FOUND CLAIM**

B52R24 extends B52R23 from routine-level GPU correlation to exact MMIO-write capture.

It does not patch a ROM and does not create a new BIN/CUE/ISO.

## Tools

- `tools/gaia_b52r24_trace_generator.py`
- `tools/gaia_b52r24_trace_analyzer.py`
- `tools/00_BUILD_B52R24_PCSX_CAPTURE.cmd`
- `tools/00_ANALYZE_B52R24_CAPTURE.cmd`

## Input contract

First run B52R23 on the same exact B52R14R1 BIN.

B52R24 generator consumes:

`GaiaMaster_B52R23_GPU_MMIO_HITS.csv`

It keeps WRITE hits for:

- `DMA2_MADR`
- `DMA2_BCR`
- `DMA2_CHCR`
- `GP0`

and generates:

`GaiaMaster_B52R24_PCSX_DMA_SOURCE_CAPTURE.lua`

## PCSX-Redux capture flow

PCSX-Redux official Lua API was rechecked before materializing this tool.

Required conditions:
- debugger enabled;
- interpreted CPU, not Dynarec;
- the generated Lua breakpoint objects remain referenced so they are not garbage-collected.

Workflow:

1. Load `GaiaMaster_B52R24_PCSX_DMA_SOURCE_CAPTURE.lua` in PCSX-Redux.
2. Cold boot the same B52R14R1 used by B52R23.
3. Navigate to immediately before the green main menu target.
4. In Lua console call `gaia_arm24()`.
5. Enter the target menu.
6. The first captured DMA2 `CHCR` start pauses the emulator.
7. Call `gaia_save24()` while paused.
8. This writes:
   - `GaiaMaster_B52R24_TRACE.tsv`
   - `GaiaMaster_B52R24_RAM.bin`
   - `GaiaMaster_B52R24_META.txt`
9. Drag the TRACE TSV into `00_ANALYZE_B52R24_CAPTURE.cmd`.

Useful helpers:
- `gaia_arm24(N)` skips N DMA starts before capture;
- `gaia_next24()` arms and resumes to the next DMA start;
- `gaia_disarm24()` disables collection.

## Analyzer behavior

The analyzer:
- decodes DMA2 `CHCR` direction / step / SyncMode / start;
- resolves MADR to physical main-RAM offset;
- decodes BCR word/block counts;
- for SyncMode 0/1, extracts the linear DMA source payload;
- for SyncMode 2, parses the linked-list node chain and flattens GPU command words;
- records source-payload entropy;
- searches captured GP0 writes for notable `A0h / 80h / C0h` commands;
- when a direct `A0h CPU->VRAM` sequence is present, reports its x/y/w/h rectangle.

Analyzer outputs include:
- `GaiaMaster_B52R24_ANALYSIS.txt`
- `GaiaMaster_B52R24_DMA_SOURCE.bin`
- `GaiaMaster_B52R24_DMA_NODES.csv` for linked-list captures.

## Validation

Local authoring validation:
- trace generator `py_compile`: PASS
- trace generator self-test: **B52R24 TRACE GENERATOR SELFTEST PASS**
- trace analyzer `py_compile`: PASS
- trace analyzer self-test: **B52R24 TRACE ANALYZER SELFTEST PASS**

The analyzer self-test validates a synthetic SyncMode 1 RAM->GPU transfer with MADR/BCR/CHCR and exact payload extraction.

## Evidence rules

A B52R24 capture can prove:
- the exact RAM address used as a captured GPU DMA source;
- the BCR length for block/slice mode;
- the GPU command list source for linked-list mode;
- an upload rectangle only when the relevant GP0 A0 command sequence is actually captured.

It does **not** by itself prove:
- which disc file/archive member produced that RAM buffer;
- whether the captured DMA is specifically the Japanese menu label rather than background/UI graphics;
- that a ROM patch location is known.

The target frame still needs GPU Logger/origin correlation.

## Promotion gate

B52R25 should only begin after a runtime capture is associated with the visible `ストーリーモード` rendering/upload.

B52R25 task:
**backtrace the proven RAM source to its load/decompression/archive ownership and only then identify the smallest reversible disc-side patch.**

Overall Runtime PASS remains **NO**.

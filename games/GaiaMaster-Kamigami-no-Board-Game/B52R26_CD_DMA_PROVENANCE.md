# B52R26 - CD DMA provenance fallback

Date: 2026-09-21  
Repo: `RVTGMzz/PSXVH`  
Branch: `gaia-character-select-font-atlas-reverse-01`

## Status

**TOOLING READY / REAL CD-DMA CAPTURE PENDING / NO DISC-OWNER CLAIM**

B52R26 is the fallback for cases where B52R25 CPU writer-watch does not fire or where evidence suggests the B52R24 GPU-source buffer may be filled directly by CDROM DMA.

It does not patch a ROM.

## Hardware contract

On PS1:
- DMA2 is GPU.
- DMA3 is CDROM.
- DMA3 registers are:
  - `1F8010B0` MADR
  - `1F8010B4` BCR
  - `1F8010B8` CHCR
- CDROM DMA normally runs device -> RAM in SyncMode 0.

B52R26 uses that only as a provenance probe. A matching RAM range is not yet an ISO-file/LBA proof.

## Tools

- `tools/gaia_b52r26_cd_dma_locator.py`
- `tools/gaia_b52r26_cd_gpu_overlap_analyzer.py`
- `tools/00_RUN_B52R26_CD_DMA_LOCATOR.cmd`
- `tools/00_COMPARE_B52R26_CD_GPU_OVERLAP.cmd`

## Locator/capture flow

Input:
- exact B52R14R1 BIN preferred;
- exact CLEAN Japan fallback.

The locator:
- verifies the known SHA1 contract;
- extracts `SLPS_020.75`;
- scans MIPS code for DMA3 MADR/BCR/CHCR accesses;
- groups/ranks candidate routines;
- emits:
  - `GaiaMaster_B52R26_CD_DMA_MMIO_HITS.csv`
  - `GaiaMaster_B52R26_CD_DMA_LOCATOR_REPORT.txt`
  - `GaiaMaster_B52R26_PCSX_CD_DMA_CAPTURE.lua`

Lua helpers:
- `gaia_arm26()`
- `gaia_arm26(N)` to skip N CD DMA starts
- `gaia_next26()`
- `gaia_save26()` -> `GaiaMaster_B52R26_CD_DMA_TRACE.tsv`

The capture pauses on a DMA3 CHCR start after collecting the preceding MADR/BCR setup.

## CD/GPU overlap analyzer

Inputs:
- B52R24 `TRACE.tsv`
- B52R26 `CD_DMA_TRACE.tsv`

The analyzer compares:
- B52R24 GPU DMA source RAM range;
- B52R26 CD DMA destination RAM range.

Verdicts:
- `EXACT_RANGE_MATCH`
- `GPU_SOURCE_FULLY_INSIDE_CD_DMA`
- `PARTIAL_OVERLAP`
- `NO_OVERLAP`
- `GPU_SYNC2_COMMAND_LIST`

Meaning:
- EXACT/FULL-COVER is strong upstream RAM-load evidence only when both captures belong to the same target transition.
- PARTIAL requires more transactions or a CPU copy/decompression step.
- NO_OVERLAP rules out that captured CD DMA as the direct fill of the B52R24 GPU-source buffer.
- SyncMode 2 GPU command-list memory is not treated as a texture asset payload.

Even an exact overlap still does not identify a disc filename/member/LBA. That requires a later CDROM command/LBA or archive-load ownership trace.

## Validation

Authoring validation completed for core logic:
- DMA3 MADR/CHCR synthetic locator self-test: PASS
- CD/GPU exact/partial overlap core self-test: PASS

Real Gaia Master execution:
- **PENDING**
- no B52R26 CD DMA transaction captured yet
- no CD/GPU overlap verdict from the real game yet
- no disc/archive owner found yet

## Execution gate

Normal route:
1. B52R22
2. B52R23
3. B52R24 target transaction
4. B52R25 CPU writer-watch for linear source when applicable

Use B52R26 when:
- B52R25 does not fire, or
- the target buffer looks like a direct disc load, or
- a CD DMA transaction must be ruled in/out as the upstream fill.

If B52R26 proves a same-transition exact/full-cover relationship, the next phase should trace the corresponding CDROM read command / sector address / archive request to disc ownership.

Overall Runtime PASS remains **NO**.

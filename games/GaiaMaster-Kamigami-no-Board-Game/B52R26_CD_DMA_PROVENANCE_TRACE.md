# B52R26 - CD-DMA provenance trace

Date: 2026-09-22  
Repo: `RVTGMzz/PSXVH`  
Branch: `gaia-character-select-font-atlas-reverse-01`

## Status

**TOOLING READY / REAL TRACE PENDING / NO DISC-SOURCE CLAIM**

B52R26 is the hardware-load branch for a B52R24 linear GPU-source capture. It is useful when B52R25 finds no meaningful CPU writer or when the target RAM buffer may have been filled directly from CD-ROM DMA.

It does not patch the ROM.

## Tools

- `tools/gaia_b52r26_cd_dma_provenance_generator.py`
- `tools/gaia_b52r26_cd_dma_provenance_analyzer.py`
- `tools/00_BUILD_B52R26_CD_DMA_WATCH.cmd`
- `tools/00_ANALYZE_B52R26_CD_DMA.cmd`

## Input gate

Generator input:

`GaiaMaster_B52R24_TRACE.tsv`

The B52R24 target must be DMA2 SyncMode 0/1 so the GPU source is a linear RAM range. SyncMode 2 is GPU command-list RAM and is rejected as a linear asset source.

## Runtime trace

The generated Lua watches the CD-ROM host interface and DMA3 directly:

- `1F801800` CD bank/address
- `1F801801` command
- `1F801802` parameter
- `1F8010B0` DMA3 MADR
- `1F8010B4` DMA3 BCR
- `1F8010B8` DMA3 CHCR

The breakpoint callback decodes the actual MIPS store instruction and source GPR, so the value written to each MMIO register can be recovered even when the setup code is in BIOS.

Tracked CD commands:
- `02h Setloc`
- `06h ReadN`
- `1Bh ReadS`
- `08h Stop`
- `09h Pause`

For Setloc, the BCD minute/second/frame parameters are converted to an LBA candidate.

At every DMA3 start, the Lua records:
- PC / RA / SP
- MADR / BCR / CHCR
- SyncMode + direction
- destination RAM range
- overlap bytes against the B52R24 target source
- tracked LBA + confidence
- active read command

A direct overlap automatically pauses the emulator so `gaia_save26()` can save:

`GaiaMaster_B52R26_CD_DMA_TRACE.tsv`

## Analyzer

The analyzer can run with only the trace, or with trace + exact B52R14R1/CLEAN BIN.

With the BIN it:
- verifies the known SHA1 contract;
- indexes ISO9660 Form1 files;
- maps tracked LBA candidates back to an ISO file extent;
- reports approximate file offset and raw BIN sector offset.

Verdicts:
- `DIRECT_CD_DMA_OVERLAP_CANDIDATE`
- `NO_DIRECT_DMA3_OVERLAP_IN_CAPTURE_WINDOW`

A direct RAM overlap is concrete runtime evidence that the captured CD DMA destination intersects the B52R24 GPU-source buffer. The LBA/file owner remains a provenance candidate whose strength depends on Setloc/sequential tracking.

## Validation

Authoring validation performed after commit:
- generator compile: PASS
- **B52R26 CD DMA PROVENANCE GENERATOR SELFTEST PASS**
- analyzer compile: PASS
- **B52R26 CD DMA PROVENANCE ANALYZER SELFTEST PASS**

## Evidence limits

No real Gaia Master B52R26 trace exists yet.

No-overlap does not rule out:
- staged CD loads;
- CPU copy;
- decompression;
- rasterization;
- an earlier load outside the armed capture window.

Do not patch a disc offset from B52R26 alone. Require agreement with B52R24 target-frame correlation and, where applicable, B52R25/B52R27 ownership evidence.

Overall Runtime PASS remains **NO**.

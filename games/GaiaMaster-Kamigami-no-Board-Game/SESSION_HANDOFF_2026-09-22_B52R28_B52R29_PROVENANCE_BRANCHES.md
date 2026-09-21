# SESSION HANDOFF - 2026-09-22 - B52R28/B52R29 provenance branches

Repo: `RVTGMzz/PSXVH`  
Branch: `gaia-character-select-font-atlas-reverse-01`

## Authority

Current exact working base remains B52R14R1:

`0ced9982e1b00566b42ace047236378826c2aa1c`

CLEAN Japan:

`f4d5298583c90d89c4b7e51d2dde160ee07f2aec`

No newer runtime build has been promoted.

## Existing authority preserved

B52R26 and B52R27 already existed before this session:

- B52R26 = DMA3 CDROM->RAM locator/range-overlap fallback
- B52R27 = disc payload fingerprint against ISO Form1 files

A temporary naming collision was detected during this session and corrected. The new work is now:

- **B52R28** = Setloc/LBA CD-DMA provenance upgrade
- **B52R29** = overlay writer fingerprint resolver

The temporary new B52R26/B52R27 filenames were deleted. Original authoritative B52R26/B52R27 files remain intact.

## B52R28

Files:
- `tools/gaia_b52r28_cd_dma_provenance_generator.py`
- `tools/gaia_b52r28_cd_dma_provenance_analyzer.py`
- `tools/00_BUILD_B52R28_CD_DMA_WATCH.cmd`
- `tools/00_ANALYZE_B52R28_CD_DMA.cmd`
- `B52R28_CD_DMA_PROVENANCE_TRACE.md`

Adds direct PCSX-Redux CD host + DMA3 MMIO watches, MIPS store-value recovery, Setloc/ReadN/ReadS tracking, BCD MSF->LBA conversion, target-RAM overlap detection, and optional ISO file-owner mapping.

Validation:
- generator compile PASS
- generator self-test PASS
- analyzer compile PASS
- analyzer self-test PASS

Real Gaia Master trace: **PENDING**.

## B52R29

B52R25 was extended so `gaia_save25()` now saves:
- `GaiaMaster_B52R25_WRITER_TRACE.tsv`
- `GaiaMaster_B52R25_WRITER_RAM.bin` (2 MiB)

Files:
- `tools/gaia_b52r29_overlay_fingerprint_resolver.py`
- `tools/00_RESOLVE_B52R29_OVERLAY_FINGERPRINT.cmd`
- `B52R29_OVERLAY_WRITER_FINGERPRINT.md`

B52R29 handles writer PCs in RAM but outside main SLPS text by fingerprinting exact 96/64/48/32-byte code anchors from the writer-time RAM snapshot against ISO9660 Form1 files, then ranking candidates by surrounding context similarity.

Validation:
- compile PASS
- self-test PASS
- committed B52R25 RAM-snapshot path verified structurally

Real writer snapshot: **PENDING**.

## Correct runtime execution chain

1. B52R22 on exact B52R14R1.
2. B52R23 on the same BIN.
3. B52R24 capture and correlate the visible `ストーリーモード` frame.
4. If linear:
   - run existing B52R27 disc-payload fingerprint first;
   - run B52R25 writer-watch for CPU transform path;
   - use existing B52R26 for coarse DMA3 overlap;
   - use B52R28 when Setloc/LBA/file provenance is needed.
5. If B52R25 writer PC is outside main SLPS:
   - preserve WRITER_RAM.bin;
   - run B52R29 overlay fingerprint.
6. If SyncMode 2:
   - remain on GPU-origin/texture-upload tracing instead of treating linked-list RAM as an asset.

## Evidence limits

No B52R22-B52R29 runtime tool has yet produced a real target-source proof in this environment.

Therefore:
- remaining visible Japanese UI source not yet identified;
- no target DMA transaction proven;
- no CPU writer proven;
- no direct CD LBA/file owner proven;
- no overlay owner proven;
- no disc-side patch should be created yet;
- overall Runtime PASS remains NO.

Do not reopen dead plaintext/alternate-encoding/raw-TIM/JIS paths and do not modify font.

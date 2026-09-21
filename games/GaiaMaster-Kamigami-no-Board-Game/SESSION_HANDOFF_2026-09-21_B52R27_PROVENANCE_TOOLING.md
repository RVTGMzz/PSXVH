# SESSION HANDOFF - 2026-09-21 - B52R27 provenance tooling

Repo: `RVTGMzz/PSXVH`
Branch: `gaia-character-select-font-atlas-reverse-01`

## Authority

Current exact working base remains B52R14R1:

`0ced9982e1b00566b42ace047236378826c2aa1c`

CLEAN Japan:

`f4d5298583c90d89c4b7e51d2dde160ee07f2aec`

No new runtime build has been promoted.

## Tooling chain now prepared

- B52R22: compressed/custom-pack static live-source probe
- B52R23: GPU/DMA2 MMIO locator + PCSX breakpoints
- B52R24: exact DMA2 source capture + RAM snapshot/analyzer
- B52R25: CPU source-buffer writer watch + writer-PC resolver
- B52R26: CDROM DMA3 capture + CD/GPU RAM-range overlap
- B52R27: exact/aligned captured-payload fingerprint against ISO9660 logical files

## Correct runtime order

1. Run B52R22 and B52R23 on exact B52R14R1.
2. Capture target `ストーリーモード` transaction with B52R24.
3. If linear source payload exists, run B52R27 fingerprint immediately.
4. If exact fingerprint exists, use reported ISO file/offset/LBA as strong ownership evidence.
5. If no exact fingerprint, use B52R25 to catch CPU transform/writer.
6. If no CPU writer fires or direct CD load is suspected, use B52R26 DMA3 capture/overlap.
7. Do not patch until disc/archive ownership is proven and BDP checksum requirements are understood.

## Claims still forbidden

- remaining UI source found
- target DMA transaction proven
- disc/archive ownership proven
- overall Runtime PASS

All require real user-side runtime evidence first.

# SESSION HANDOFF - 2026-09-21 - B52R25 writer-watch tooling

Repo: `RVTGMzz/PSXVH`  
Branch: `gaia-character-select-font-atlas-reverse-01`

## Authority

Current exact working base remains B52R14R1 SHA1:

`0ced9982e1b00566b42ace047236378826c2aa1c`

CLEAN Japan:

`f4d5298583c90d89c4b7e51d2dde160ee07f2aec`

No newer runtime build has been promoted.

## What changed this session

B52R23:
- GPU/DMA MMIO locator + PCSX breakpoint Lua prepared.

B52R24:
- exact MMIO capture generator/analyzer prepared;
- captures MADR/BCR/CHCR/GP0;
- save path is TRACE.tsv + 2 MiB RAM + META;
- analyzer decodes SyncMode and extracts linear/linked-list DMA evidence.

B52R25:
- source-buffer Write watch generator prepared for SyncMode 0/1;
- writer-PC resolver prepared to map a runtime writer back into SLPS text/function/callers.

All new Python tools compile and self-test PASS.

## Important limits

No B52R22/B52R23/B52R24/B52R25 tool has yet been run against a real local Gaia Master BIN in this environment.

Therefore:
- no remaining visible-UI source has been identified;
- no target DMA transaction has been proven;
- no writer PC has been proven;
- no disc/archive ownership has been proven;
- overall Runtime PASS remains NO.

## Correct next execution chain

1. Run B52R22 on exact B52R14R1.
2. Run B52R23 on same BIN.
3. Build B52R24 PCSX capture Lua from B52R23 MMIO CSV.
4. Correlate main-menu `ストーリーモード` with GPU Logger/Show origins.
5. Capture B52R24 transaction and analyze.
6. If target transaction is SyncMode 0/1, build B52R25 writer watch and catch source-buffer writer.
7. Resolve writer PC with exact B52R14R1.
8. Only then move to disc/archive ownership and reversible patch design.

Do not reopen plaintext/alternate encoding/raw TIM/JIS scans and do not modify font.

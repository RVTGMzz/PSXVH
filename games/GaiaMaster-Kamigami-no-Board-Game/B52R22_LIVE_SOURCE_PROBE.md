# B52R22 - Live-source compression/custom-pack probe

Date: 2026-09-20  
Repo: `RVTGMzz/PSXVH`  
Branch: `gaia-character-select-font-atlas-reverse-01`

## Status

**TOOLING READY / LOCAL EXECUTION REQUIRED / NO RUNTIME PASS CLAIM**

B52R21R1 proved that the known PRGPACK CP932 copies are not the live render source for the still-Japanese main menu, Character Select, and `冒険のはじまり` screens. B52R22 therefore does not patch those offsets again.

## What B52R22 does

`tools/gaia_b52r22_live_source_probe.py` is read-only. It:

- accepts the exact B52R14R1 BIN SHA1 `0ced9982e1b00566b42ace047236378826c2aa1c` as the preferred oracle;
- also accepts the exact CLEAN Japan BIN SHA1 `f4d5298583c90d89c4b7e51d2dde160ee07f2aec` as a fallback reverse source;
- indexes the MODE2/2352 ISO9660 filesystem directly;
- finds `PRGPACK` and `SCR_DATA` without hard-coding SCR_DATA extent;
- inspects only the five B52R20 evidence-driven owner spans;
- recursively opens checksum-valid BDP-like containers;
- tests bounded zlib/gzip/raw-deflate/LZ10 paths at small wrapper-prefix offsets;
- keeps raw-deflate results only when decoded bytes expose concrete target/TIM evidence, reducing false positives;
- scans decoded data for the main-menu/Character Select/chapter target strings and structurally valid PS-X TIM images;
- emits only TXT/CSV reports, never another full-disc BIN.

## Target owner spans

PRGPACK:

- `0xBF7AC..0xDDA98`
- `0xDDA98..0x104660`
- `0x14B970..0x155C1C`

SCR_DATA:

- `0x9741A8..0x994850`
- `0x9C1BF4..0x9CE4CC`

These spans are landmarks from B52R20. Their presence does **not** mean the live source is already proven to be inside them.

## Run

Drag the exact B52R14R1 BIN onto:

`tools/00_RUN_B52R22_LIVE_SOURCE_PROBE.cmd`

or run:

```text
python tools/gaia_b52r22_live_source_probe.py "GaiaMaster_B52R14R1.bin"
```

Optional tool self-test:

```text
python tools/gaia_b52r22_live_source_probe.py --selftest
```

## Outputs

Next to the input BIN:

```text
GaiaMaster_B52R22_LIVE_SOURCE_PROBE_REPORT.txt
GaiaMaster_B52R22_LIVE_SOURCE_LEAVES.csv
GaiaMaster_B52R22_LIVE_SOURCE_DECODES.csv
```

No BIN/CUE/ISO output is created.

## Interpretation gate

A new static source candidate requires at least one of:

1. a target Japanese string appearing **after** a bounded decode, not merely as one of the known dead plaintext copies; or
2. a structurally valid PS-X TIM appearing **after** decode.

If neither occurs, B52R22 must not be stretched into a fake source identification. The next step is B52R23 runtime tracing of the main-menu VRAM/upload/decompression path, using B52R22's high-entropy leaf shortlist as breakpoint/source candidates.

Overall Runtime PASS remains **NO**.

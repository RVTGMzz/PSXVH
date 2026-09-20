# B52R23 - GPU upload/runtime trace preparation

Date: 2026-09-21  
Repo: \`RVTGMzz/PSXVH\`  
Branch: \`gaia-character-select-font-atlas-reverse-01\`

## Status

**TOOLING READY / ROM EXECUTION REQUIRED / NO RUNTIME PASS CLAIM**

B52R22 remains the first static live-source probe. B52R23 is the prepared fallback for the case where B52R22 does not expose a decoded target string or decoded TIM.

B52R23 does **not** patch the game. It narrows the MIPS/GPU path used to render/upload the still-Japanese UI so runtime debugging can start from concrete executable addresses instead of blind stepping.

## New tool

\`tools/gaia_b52r23_gpu_upload_locator.py\`

Launcher:

\`tools/00_RUN_B52R23_GPU_UPLOAD_LOCATOR.cmd\`

Accepted BINs:

- preferred B52R14R1 SHA1: \`0ced9982e1b00566b42ace047236378826c2aa1c\`
- CLEAN Japan fallback SHA1: \`f4d5298583c90d89c4b7e51d2dde160ee07f2aec\`

The tool scans the PS-X EXE for direct accesses to GP0, GP1/GPUSTAT, GPU DMA2 MADR/BCR/CHCR, DPCR/DICR, obvious A0h/80h/C0h GP0 copy-command builders, direct jal callers, and heuristic function boundaries. It scores routines higher when GP0 writes occur together with DMA2 setup.

## Outputs

\`\`\`text
GaiaMaster_B52R23_GPU_UPLOAD_LOCATOR_REPORT.txt
GaiaMaster_B52R23_GPU_MMIO_HITS.csv
GaiaMaster_B52R23_GPU_COMMAND_BUILDERS.csv
GaiaMaster_B52R23_GPU_BREAKPOINTS.txt
\`\`\`

No BIN/CUE/ISO output is created.

## Local authoring validation

- \`python -m py_compile\`: PASS
- \`--selftest\`: \`B52R23 SELFTEST PASS\`

The self-test recognizes a synthetic GP0 write and an A0h CPU-to-VRAM command builder. It does **not** prove any Gaia Master routine yet. Real-ROM execution is required.

## Runtime correlation in PCSX-Redux

For CPU breakpoints:

- use the interpreter rather than Dynarec;
- enable the debugger;
- set Exec breakpoints on the highest-scoring routine or exact hit PCs from \`GPU_BREAKPOINTS.txt\`;
- cold boot the same BIN used by the locator;
- approach the green main menu and note which breakpoint fires while \`ストーリーモード\` is being drawn.

For GPU correlation:

- enable GPU Logger;
- capture the target menu frame;
- enable \`Show origins\`;
- inspect texture/upload commands contributing to the Japanese label;
- correlate the GPU origin with one of B52R23's executable hit PCs/callers.

PCSX-Redux also provides execution/read/write mapping breakpoints and CPU trace dumps if the first GPU-origin correlation is ambiguous.

## Promotion gate

A B52R23 address is only a **candidate** until runtime proves that it participates in the target menu draw/upload path. Generic rendering and unrelated texture streaming use the same hardware registers.

Only after live correlation should B52R24 trace the source RAM buffer backward to archive/member/file ownership and create the smallest reversible patch.

Overall Runtime PASS remains **NO**.

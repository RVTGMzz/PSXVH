# Gaia Master — Font Mapping Initializer Scanner 0.2

Updated: **2026-09-13**

## Why 0.2 exists

`GaiaMaster_FontMappingScanner_01.txt` confirmed that the PS-X EXE header has:

```text
PC0    = 0x80035194
GP0    = 0x00000000
T_ADDR = 0x80010000
T_SIZE = 0x00076800
```

Therefore scanner 0.1 cannot derive usable global addresses from the header GP value. Its calculated `0x518` / `0x51C` addresses are only the raw offsets, not real runtime global addresses.

The renderer consumer path is still proven:

```text
0x8003C4E0  lw v1,0x51C(gp)   # mapping base
0x8003C4E4  lw a0,0x518(gp)   # atlas base
0x8003C4EC  lhu v1,0(v0)      # glyph index
0x8003C4F8..0x8003C500         # glyph_index * 72
0x8003C504                     # atlas + glyph offset
```

Known static resource addresses remain:

```text
atlas RAM    = 0x8006BCEC
mapping RAM  = 0x8007AECC
atlas file   = SLPS + 0x5C4EC
mapping file = SLPS + 0x6B6CC
```

## Scanner 0.2

Files:

```text
tools/font_mapping_initializer_scanner_0.2.py
tools/00_RUN_FONT_MAPPING_INITIALIZER_SCANNER_0.2.cmd
```

Expected output:

```text
GaiaMaster_FontMappingInitializerScanner_02.txt
```

This tool is **READ ONLY**. It does not modify the BIN and does not require emulator boot.

It scans the full SLPS executable and reports:

1. entrypoint code around `PC0 = 0x80035194`;
2. all direct `lui gp` + `addiu/ori gp` candidates;
3. every direct `sw/sh` into `gp+0x518` and `gp+0x51C`;
4. local constant propagation for the source register of each global write;
5. all code materializations of `0x8006BCEC` and `0x8007AECC`;
6. raw 32-bit literal occurrences of those addresses;
7. the static mapping bytes at `SLPS+0x6B6CC`;
8. direct static checks for the known mapping samples:

```text
0x8273 Ｔ -> glyph 481
0x8264 Ｅ -> glyph 466
0x8272 Ｓ -> glyph 480
0x889F 亜 -> glyph 0
```

## Gate

No ROM proof is authorized yet.

Only after the initializer/global ownership is proven should the next proof patch:

```text
mapping entries
+
native 12x12 / 72-byte glyph data
```

No runtime pointer redirect, no 12x16 production path, and no composite overlay.

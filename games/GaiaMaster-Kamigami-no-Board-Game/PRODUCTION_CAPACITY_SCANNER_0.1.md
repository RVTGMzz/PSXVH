# Production Capacity Scanner 0.1

Current read-only gate after retiring the 6x12/narrow path.

- Last-good runtime architecture: `0.6.6.1 BASELINE-NORMALIZED`.
- Production lock: native 12x12 / 72-byte / 4bpp / static mapping-only.
- `0.6.6.2c` runtime failed because one-byte aliases did not route to the assumed narrow glyph indices. Do not retest.
- Scanner worst-case target: **134 custom Vietnamese glyphs** = 67 lowercase + 67 uppercase, while plain ASCII bases reuse Gaia native Latin.
- Scanner counts zero-static-hit custom CP932 codes and atlas slots, protects native source glyph slots, separates unmapped vs mapped-but-zero-hit capacity, and emits a deterministic full codepage proposal if PASS.
- Output report: `GaiaMaster_ProductionCapacityScanner_01.txt`.
- No ROM patch and no emulator boot.

If PASS, freeze full Vietnamese codepage and move to a multi-string real `vi_full` production build. If FAIL, inventory only the exact characters present in `vi_full` and allocate that smaller corpus.

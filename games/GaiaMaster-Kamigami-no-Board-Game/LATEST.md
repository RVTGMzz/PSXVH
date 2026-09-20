# Gaia Master - trạng thái mới nhất

Cập nhật: **2026-09-21**

Repo: `RVTGMzz/PSXVH`  
Branch: `gaia-character-select-font-atlas-reverse-01`

## CURRENT - UI LIVE-SOURCE REVERSE PIVOT

Mốc mới nhất không còn là B51. Translation runtime đã tiến qua B52R12/B52R14R1, và reverse UI đã đi tới B52R21R1.

### Known exact current base

B52R14R1:

`0ced9982e1b00566b42ace047236378826c2aa1c`

B52R14R1:
- 23 ISO files indexed
- 19 Form1 scanned
- 4 XA/Form2 safely skipped
- 6 player-count fields patched
- checksum read-back PASS
- font/mapping unchanged

Use this exact base for new reverse tools until a newer base is explicitly proven.

## What has been proven about the still-Japanese UI

Target screens still visibly Japanese include:
- main green menu
- Character Select title/details
- `冒険のはじまり`
- Save/Load/Password-related UI

B52R15:
- 41 exact CP932 hits
- 0 plain candidates
- all copies already changed in base

B52R17:
- 57 encoding hits
- all CP932 changed copies
- 0 unchanged alternate-encoding candidate

B52R18:
- all 173 raw TIM assets exported/reviewed
- target UI not found in raw TIM atlas

B52R19:
- 39 JIS-compatible targets
- 0 tile/glyph-index hits
- 0 unknown-bias live candidates

B52R20:
- 57/57 landmarks inside BDP owners
- 5 owner/member centers
- 8 sibling members exported
- no recognizable target UI in raw 4/8/16bpp previews

B52R21:
- stopped on `ルール -> Luật` byte overflow 8>6

B52R21R1:
- removed overflowing row
- normalized known PRGPACK copy locations
- user runtime screenshots showed **no visible change**
- main menu, Character Select and `冒険のはじまり` remained Japanese

### Current conclusion

The known PRGPACK CP932 copies are **runtime-dead for those visible screens**.

Do not repeat:
- exact PRGPACK patch of those locations
- alternate encoding scan
- raw TIM scan
- JIS/tile-index scan
- owner sibling raw preview scan

Next direction:
**compressed/custom-packed data or runtime-generated large-font UI live-source reverse.**

Recommended first live target:
`ストーリーモード` on the main menu.

## B52R22 - LIVE-SOURCE PROBE TOOLING READY

B52R22 đã được commit theo hướng **read-only**, không tạo thêm full BIN:

- `tools/gaia_b52r22_live_source_probe.py`
- `tools/00_RUN_B52R22_LIVE_SOURCE_PROBE.cmd`
- `B52R22_LIVE_SOURCE_PROBE.md`

Probe:
- khóa exact B52R14R1/CLEAN SHA1;
- index MODE2/2352 ISO9660 trực tiếp;
- tìm PRGPACK + SCR_DATA;
- chỉ đi vào 5 owner spans của B52R20;
- recurse checksum-valid BDP;
- thử bounded zlib/gzip/raw-deflate/LZ10;
- tìm target text/TIM **sau decode**;
- xuất report + 2 CSV, không xuất BIN.

Static authoring validation:
- py_compile PASS
- self-test PASS

**ROM execution pending.** Chưa được gọi source-found và overall Runtime PASS vẫn **NO**.

Next:
1. chạy launcher với exact B52R14R1;
2. nếu có decoded target/TIM thì đi B52R23 ownership/render proof;
3. nếu không có thì B52R23 runtime trace `ストーリーモード` VRAM/upload/decompression.

## B52R23 - GPU TRACE TOOLING READY

B52R23 đã được commit, vẫn **read-only**:

- `tools/gaia_b52r23_gpu_upload_locator.py`
- `tools/00_RUN_B52R23_GPU_UPLOAD_LOCATOR.cmd`
- `B52R23_GPU_UPLOAD_RUNTIME_TRACE.md`

Tool tìm MIPS routine chạm GP0/GP1/DMA2, A0h/80h/C0h command builders, `jal` callers, tạo `GPU_BREAKPOINTS.txt`, và tự sinh `GaiaMaster_B52R23_PCSX_BREAKPOINTS.lua`. Lua script có `gaia_arm()` để chỉ pause/log PC/RA/SP khi bạn chủ động arm ngay trước target menu.

Static authoring validation:
- py_compile PASS
- self-test PASS

**ROM/runtime correlation pending.** Chưa được gọi source-found.

Current execution order:
1. chạy B52R22 trên exact B52R14R1;
2. chạy B52R23 locator trên cùng BIN;
3. dùng PCSX-Redux GPU Logger + Show origins và CPU breakpoints để correlate `ストーリーモード`;
4. chỉ khi ownership được chứng minh mới đi B52R24 source-buffer backtrace/patch.

## Runtime / translation checkpoints

- CLEAN SHA1:
  `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- B50 exact overlay: 1229/1229 static PASS
- B51R2 real CLEAN dry-run/build PASS
- SCR_DATA nested containers: 303, repair checksums bottom-up after mutation
- B52R10 SHA1:
  `61f9175d7f14fa94744a7525fcfde6102e65580d`
- B52R11R3 SHA1:
  `c305f17c7c1ac9aeb26e8a4c0546c6dc1c3286b7`
  - quick-path runtime OK
- B52R12 SHA1:
  `e4cb8c1f485ed66008d6d69f26d06c906d738692`
  - user said path OK
- B52R14R1 SHA1:
  `0ced9982e1b00566b42ace047236378826c2aa1c`

Overall Runtime PASS: **NO**

## Architecture lock

- 12x12 / 72-byte / 4bpp / LOW nibble first
- frozen 60-glyph codepage
- mapping-only
- no renderer hook
- no pointer redirect
- font work parked

## Disk-space rule

Local project is around 20 GB.

Do not keep generating permanent full BINs for every probe.
Keep:
- CLEAN
- one known current base
- newest output under test
- tools/manifests/reports/CSV

Plan later:
`GaiaMaster_SAFE_CLEANUP.cmd` with explicit KEEP/DELETE preview before removal.

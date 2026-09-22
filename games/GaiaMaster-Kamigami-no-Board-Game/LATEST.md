# Gaia Master - trạng thái mới nhất

Cập nhật: **2026-09-23**

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
4. dùng B52R24 exact-MMIO capture để lấy MADR/BCR/CHCR/GP0 + RAM snapshot ở target frame;
5. nếu B52R24 target transaction là SyncMode 0/1, dùng B52R25 writer-watch để bắt code fill source buffer;
6. resolve writer PC về SLPS/overlay ownership before patch;
7. for any proven B52R24 linear payload, run B52R27 fingerprint immediately; exact match can jump straight to ISO file/offset/LBA;
8. if CPU writer-watch does not fire or direct-disc fill is suspected, use B52R26 DMA3 range overlap, then B52R28 Setloc/LBA provenance for CD file-owner candidates.
9. if B52R25 writer PC is outside main SLPS text, use B52R29 with the writer-time RAM snapshot to fingerprint the overlay code owner.

## B52R24 - DMA SOURCE CAPTURE TOOLING READY

Đã commit:

- `tools/gaia_b52r24_trace_generator.py`
- `tools/gaia_b52r24_trace_analyzer.py`
- `tools/00_BUILD_B52R24_PCSX_CAPTURE.cmd`
- `tools/00_ANALYZE_B52R24_CAPTURE.cmd`
- `B52R24_RUNTIME_DMA_SOURCE_CAPTURE.md`

B52R24 lấy `GaiaMaster_B52R23_GPU_MMIO_HITS.csv` và sinh Lua breakpoint đúng WRITE instruction của `DMA2_MADR/BCR/CHCR/GP0`. Runtime helper có `gaia_arm24()`, skip-N, next-DMA và `gaia_save24()`; snapshot chỉ 2 MiB RAM, không sinh ROM.

Analyzer decode SyncMode/BCR/MADR, parse linked-list GPU command chain hoặc extract linear DMA payload và report GP0 A0h upload rectangle khi đủ evidence.

Static validation:
- generator py_compile/self-test PASS
- analyzer py_compile/self-test PASS

**Real Gaia Master capture pending.** Chưa có source-found claim.

B52R25 chỉ mở khi B52R24 transaction được correlate với visible `ストーリーモード`.

## B52R25 - WRITER WATCH TOOLING READY

Đã commit sẵn nhưng chưa được chạy thật:

- `tools/gaia_b52r25_writer_watch_generator.py`
- `tools/gaia_b52r25_writer_pc_resolver.py`
- `tools/00_BUILD_B52R25_WRITER_WATCH.cmd`
- `tools/00_RESOLVE_B52R25_WRITER_PC.cmd`
- `B52R25_SOURCE_BUFFER_WRITER_WATCH.md`

Nếu B52R24 target capture là SyncMode 0/1, B52R25 sinh PCSX-Redux Write watch cho đúng source RAM range, capture writer PC/RA/SP/A0-A3, rồi resolver map writer PC vào SLPS offset/function/callers/MIPS context.

Nếu SyncMode 2, không dùng linear writer watch như asset proof.

Static validation:
- writer-watch generator py_compile/self-test PASS
- writer-PC resolver py_compile/self-test PASS

**Real writer hit pending. No disc-source claim.**

## B52R26 - CD DMA PROVENANCE FALLBACK READY

Prepared:

- `tools/gaia_b52r26_cd_dma_locator.py`
- `tools/gaia_b52r26_cd_gpu_overlap_analyzer.py`
- `tools/00_RUN_B52R26_CD_DMA_LOCATOR.cmd`
- `tools/00_COMPARE_B52R26_CD_GPU_OVERLAP.cmd`
- `B52R26_CD_DMA_PROVENANCE.md`

Use B52R26 when B52R25 writer-watch does not fire or direct CDROM DMA fill is suspected. It captures DMA3 MADR/BCR/CHCR and compares the CD destination RAM range against the B52R24 GPU-source range.

Core synthetic self-tests PASS.

**Real CD DMA capture pending. No file/LBA ownership claim.**

## B52R27 - DISC FINGERPRINT TOOLING READY

Prepared:

- `tools/gaia_b52r27_disc_payload_fingerprint.py`
- `tools/00_RUN_B52R27_DISC_FINGERPRINT.cmd`
- `B52R27_DISC_PAYLOAD_FINGERPRINT.md`

Given a real B52R24 `DMA_SOURCE.bin`, B52R27 searches MODE2/Form1 ISO9660 logical files for:
- exact full payload;
- aligned 64-byte start/middle/end anchors.

It reports file + offset + extent + starting LBA.

Full source compile PASS and self-test PASS.

**Real payload search pending.**

## B52R28 - SETLOC/LBA CD-DMA PROVENANCE READY

B52R28 is an upgrade over B52R26, not a replacement.

Prepared:
- `tools/gaia_b52r28_cd_dma_provenance_generator.py`
- `tools/gaia_b52r28_cd_dma_provenance_analyzer.py`
- `tools/00_BUILD_B52R28_CD_DMA_WATCH.cmd`
- `tools/00_ANALYZE_B52R28_CD_DMA.cmd`
- `B52R28_CD_DMA_PROVENANCE_TRACE.md`

It watches CD host MMIO + DMA3, tracks Setloc/ReadN/ReadS, converts BCD MSF to LBA candidates, detects direct overlap with the B52R24 target RAM range, and can map tracked LBA back to an ISO9660 file when given exact B52R14R1/CLEAN.

Validation:
- generator compile/self-test PASS
- analyzer compile/self-test PASS

**Real trace pending. No LBA/file ownership claim.**

## B52R29 - OVERLAY WRITER FINGERPRINT READY

B52R25 now saves:
- `GaiaMaster_B52R25_WRITER_TRACE.tsv`
- `GaiaMaster_B52R25_WRITER_RAM.bin`

Prepared:
- `tools/gaia_b52r29_overlay_fingerprint_resolver.py`
- `tools/00_RESOLVE_B52R29_OVERLAY_FINGERPRINT.cmd`
- `B52R29_OVERLAY_WRITER_FINGERPRINT.md`

If a B52R25 writer PC is outside main SLPS text, B52R29 searches exact 96/64/48/32-byte code anchors from the writer-time RAM snapshot across ISO Form1 files and ranks matches by surrounding context similarity.

Validation:
- compile PASS
- self-test PASS

**Real writer snapshot pending. No overlay owner claim.**

## B52R30 - OWNERSHIP/PATCH PLANNER READY

Prepared:
- `tools/gaia_b52r30_ownership_patch_planner.py`
- `tools/00_PLAN_B52R30_FROM_B52R27.cmd`
- `B52R30_OWNERSHIP_PATCH_PLANNER.md`

B52R30 accepts a proven/corroborated file-offset candidate, verifies ISO identity, maps checksum-valid BDP ancestry, lists touched LBAs and can simulate a same-length replacement with bottom-up nested checksum repair entirely in memory.

PATCH_PLAN.json now contains strong identity guards: original candidate SHA1, replacement SHA1, full BDP ancestry, checksum changes and simulated logical-file SHA1.

Validation:
- compile PASS
- self-test PASS

**Real candidate execution pending.**

## B52R31 - GUARDED BUILDER READY, EXECUTION LOCKED

Prepared:
- `tools/gaia_b52r31_guarded_candidate_builder.py`
- `tools/00_DRYRUN_B52R31_GUARDED_CANDIDATE.cmd`
- `tools/00_BUILD_B52R31_GUARDED_CANDIDATE.cmd`
- `B52R31_GUARDED_CANDIDATE_BUILDER.md`

Default is dry-run. Build mode refuses any drift from B52R30 plan, creates a new BIN/CUE only, repairs nested BDP checksums, regenerates MODE2/Form1 EDC/ECC, and performs logical-file/checksum readback.

Validation:
- compile PASS
- self-test PASS

**Do not run build mode until real target-frame ownership is proven.**

## B52R32 - CAPTURE SESSION MANAGER READY

Prepared:
- `tools/gaia_b52r32_capture_session_manager.py`
- `tools/00_CHECK_B52R32_SESSION.cmd`
- `tools/00_ADVANCE_B52R32_READONLY.cmd`
- `B52R32_CAPTURE_SESSION_MANAGER.md`

This is now the preferred continuation entry point.

Given exact B52R14R1/CLEAN BIN it scans evidence from B52R22-B52R31, prints one next action, and can auto-run all currently-safe read-only/static steps. It hard-stops at PCSX runtime, ambiguous ownership, and B52R31 build.

Validation:
- compile PASS
- self-test PASS

**No runtime evidence is created automatically.**

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

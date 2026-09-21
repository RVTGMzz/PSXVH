# HANDOFF CURRENT - Gaia Master PS1 Việt hóa

Updated: 2026-09-22
Repo: `RVTGMzz/PSXVH`
Branch: `gaia-character-select-font-atlas-reverse-01`

## Current priority

**Dừng hẳn nhánh vá UI bằng các CP932 copy đã biết trong PRGPACK.**
Runtime screenshots sau B52R21R1 cho thấy các màn mục tiêu vẫn giữ nguyên tiếng Nhật, nên các copy này không phải live render source của UI đang thấy.

Ưu tiên phiên kế tiếp:

1. reverse **live render source** của UI còn Nhật;
2. tập trung vào **custom-packed / compressed / runtime-generated large-font UI**;
3. ưu tiên các màn:
   - main menu xanh lá;
   - Character Select title + mô tả nhân vật;
   - `冒険のはじまり`;
   - Save / Load / Password;
4. không quay lại plaintext/alternate-encoding/TIM/JIS scan đã đóng;
5. không đụng font trừ khi user chủ động yêu cầu;
6. không gọi Runtime PASS toàn game.

## Repo / account / branch

Canonical repo hiện tại:

`RVTGMzz/PSXVH`

Branch:

`gaia-character-select-font-atlas-reverse-01`

Repo trước `ronvotri/Viet-Hoa-PS1` đã đổi tên, không dùng tên cũ nữa.

## CLEAN contract

Exact CLEAN Japan BIN SHA1:

`f4d5298583c90d89c4b7e51d2dde160ee07f2aec`

Không commit ROM/BIN/CUE/ISO lên GitHub.

## Frozen architecture

Giữ nguyên:

- native 12x12 / 72-byte / 4bpp / LOW nibble first
- static mapping-only
- frozen 60-glyph Vietnamese codepage
- no renderer hook
- no pointer redirect
- no 12x16
- no 6x12
- no composite overlay

Font accent polish vẫn parked:
- hook accent còn hơi thấp/gần thân chữ;
- acute trên `ế` chưa thật rõ;
- không sửa font trong UI reverse track hiện tại.

## Canonical runtime lineage

### B50
Canonical exact-offset overlay:
- 1229/1229 static byte-fit PASS
- direct41 + compact1188
- canonical B50 immutable

### B51R2
Real CLEAN dry-run/build PASS.
- rebuilt PREB45 base SHA1: `d7a9be56dabc4b0222e88f264536a0c7b54da3f9`
- B51R2 exact overlay output SHA1: `b50f444193799653ba09df594eadab29f6e0420c`

### B52R7/R8/R9
SCR_DATA translation expanded to strict queue 258/258, but raw builds exposed runtime hangs.

### Critical checksum discovery
SCR_DATA contains **303 nested historical-BDP-like containers**.
Every SCR_DATA mutation must repair all relevant nested checksums bottom-up before output validation.

This was proven by B52R8D4/D5. Do not return to un-repaired SCR_DATA builds.

### B52R10
Checksum-safe SCR base.
- output SHA1: `61f9175d7f14fa94744a7525fcfde6102e65580d`
- broad residual scanner is noisy and must not be used as an automatic translation queue.

### B52R11R3
Curated runtime text95 + checksum-safe.
- 95/95 curated unique
- 266/266 explicit fields
- output SHA1: `c305f17c7c1ac9aeb26e8a4c0546c6dc1c3286b7`
- user quick-path runtime: **OK**
- overall Runtime PASS: NO

### B52R12
Curated expansion based on B52R11R3.
- includes GO / Cinema labels and expansion of known reviewed strings
- user said build/runtime path was OK
- B52R12 base SHA1 later proven by reports:
  `e4cb8c1f485ed66008d6d69f26d06c906d738692`

### B52R14R1
Cross-ISO BDP-safe text build.
- 23 ISO files indexed
- 19 Form1 scanned
- 4 XA/Form2 skipped safely
- 6 exact fields patched, all player-count copies
- BDP checksum read-back PASS
- font/mapping unchanged
- output SHA1:
  `0ced9982e1b00566b42ace047236378826c2aa1c`

**Use B52R14R1 as the known exact current base for new reverse tooling until a newer base is explicitly proven and recorded.**

## UI reverse results B52R15-B52R21R1

### B52R15 - unresolved asset locator
For 25 unresolved UI strings:
- exact-hit rows: 41
- plain patch candidates: 0
- all 41 classified `BASE_ALREADY_CHANGED`

Meaning: known CLEAN CP932 copies were already modified in the current base, yet visible Japanese remained.

### B52R16 - initial TIM census
- 173 raw TIM assets discovered
- 48 previews exported
- target UI not seen in initial contact sheet

### B52R17 - alternate encoding census
39 visible target strings:
- all CLEAN encoding hits: 57
- unchanged source candidates: 0
- non-CP932 live candidates: 0
- all hits were CP932 `CHANGED_COPY`

Closed paths:
- CP932 word swap
- UTF-16 LE/BE
- EUC-JP
- JIS payload / pair swap

### B52R18 - full TIM atlas
All 173 raw TIM assets were exported and reviewed.
The target green menu / Character Select / Load UI was **not present** in the raw TIM atlas.

Therefore do not repeat raw TIM census.

### B52R19 - tile/glyph-index census
39/39 target strings JIS-compatible.
Results:
- all tile/index hits: 0
- unchanged live candidates: 0
- fixed JIS representations: none
- unknown constant-bias glyph scan: none

Therefore do not repeat JIS/tile-index scans.

### B52R20 - owner/sibling raw-gfx probe
Using CLEAN CP932 copies as landmarks:
- exact CLEAN landmark hits: 57
- landmarks inside BDP owner: 57/57
- unique owner/member centers: 5
- sibling members exported: 8

Important owners included:
- PRGPACK `0xBF7AC..0xDDA98`
- PRGPACK `0xDDA98..0x104660`
- PRGPACK `0x14B970..0x155C1C`
- SCR_DATA `0x9741A8..0x994850`
- SCR_DATA `0x9C1BF4..0x9CE4CC`

Raw 4bpp/8bpp/16bpp previews around these members did not expose the target visible UI.

### B52R21
First normalization build stopped correctly on byte overflow:
`ルール -> Luật: 8 > 6`

Do not reintroduce this row without a byte-fit alternative.

### B52R21R1
Removed the overflowing Rule row and normalized the known PRGPACK UI text spans.

User runtime check after B52R21R1:
- main menu still Japanese;
- Character Select title/details still Japanese;
- `冒険のはじまり` still Japanese;
- user explicitly reported no visible change.

**Conclusion: the known PRGPACK CP932 copies are runtime-dead for these visible screens.**
Do not spend another batch re-patching these exact offsets.

## B52R22 - read-only live-source compression/custom-pack probe

Tooling đã được materialize và commit:

- `tools/gaia_b52r22_live_source_probe.py`
- `tools/00_RUN_B52R22_LIVE_SOURCE_PROBE.cmd`
- `B52R22_LIVE_SOURCE_PROBE.md`

Contract của probe:

- ưu tiên exact B52R14R1 SHA1 `0ced9982e1b00566b42ace047236378826c2aa1c`;
- CLEAN Japan exact SHA1 chỉ là fallback reverse source;
- đọc trực tiếp MODE2/2352 + ISO9660, không hard-code SCR_DATA extent;
- chỉ kiểm 5 owner spans đã có bằng chứng từ B52R20;
- recurse checksum-valid BDP containers;
- bounded decode: zlib / gzip / raw-deflate / LZ10 tại các wrapper-prefix nhỏ;
- tìm target text sau decode và structurally-valid PS-X TIM sau decode;
- chỉ xuất TXT/CSV, không sinh thêm BIN/CUE/ISO.

Local authoring checks:
- `python -m py_compile`: PASS
- `--selftest`: **B52R22 SELFTEST PASS**

ROM execution:
- **PENDING** trên exact B52R14R1 hoặc CLEAN;
- chưa có decoded-target/TIM evidence từ ROM thật;
- chưa được gọi source-found;
- overall Runtime PASS vẫn **NO**.

Nếu report có decoded target, B52R23 phải chứng minh ownership trước khi patch.
Nếu chỉ có decoded TIM, B52R23 chỉ render/inspect asset đó.
Nếu cả hai đều không có, chuyển sang runtime trace VRAM/upload/decompression của `ストーリーモード`, dùng shortlist high-entropy leaves làm source candidates.

## B52R23 - GPU upload/runtime-trace locator

Tooling mới đã được commit:

- `tools/gaia_b52r23_gpu_upload_locator.py`
- `tools/00_RUN_B52R23_GPU_UPLOAD_LOCATOR.cmd`
- `B52R23_GPU_UPLOAD_RUNTIME_TRACE.md`

B52R23 là read-only fallback/correlation layer sau B52R22. Nó không patch ROM.

Contract:
- chấp nhận exact B52R14R1 hoặc CLEAN;
- đọc `SLPS_020.75` trực tiếp từ known disc extent;
- parse PS-X EXE text mapping;
- tìm MIPS accesses tới GP0 / GP1-GPUSTAT / DMA2 MADR-BCR-CHCR / DPCR-DICR;
- tìm command builders A0h CPU->VRAM, 80h VRAM->VRAM, C0h VRAM->CPU;
- group hit thành heuristic routines + direct `jal` callers;
- ưu tiên routine có GP0 write đi cùng DMA2 setup;
- xuất report/CSV + breakpoint shortlist + auto-generated PCSX-Redux Lua trace script, không tạo BIN/CUE/ISO.

Local authoring checks:
- `python -m py_compile`: PASS
- `--selftest`: **B52R23 SELFTEST PASS**

ROM execution:
- **PENDING**;
- chưa có GPU-origin/runtime ownership proof từ Gaia Master thật;
- chưa được gọi live source found;
- overall Runtime PASS vẫn **NO**.

Runtime correlation target:
- B52R23 tự sinh `GaiaMaster_B52R23_PCSX_BREAKPOINTS.lua`; load script rồi gọi `gaia_arm()` ngay trước target menu;
- Lua trace ghi PC/RA/SP, pause ở armed hit đầu tiên và tự remove breakpoint đó;
- dùng PCSX-Redux interpreter + debugger cho CPU breakpoints;
- dùng GPU Logger + `Show origins` ở đúng frame main menu;
- ưu tiên `ストーリーモード`;
- correlate GPU origin với B52R23 hit PC/routine;
- sau live correlation dùng B52R24 để capture chính lệnh MMIO + MADR/BCR/CHCR/GP0; disc/archive ownership vẫn để B52R25.

## B52R24 - runtime DMA source capture

Tooling đã được materialize:

- `tools/gaia_b52r24_trace_generator.py`
- `tools/gaia_b52r24_trace_analyzer.py`
- `tools/00_BUILD_B52R24_PCSX_CAPTURE.cmd`
- `tools/00_ANALYZE_B52R24_CAPTURE.cmd`
- `B52R24_RUNTIME_DMA_SOURCE_CAPTURE.md`

B52R24 không patch ROM. Nó lấy CSV exact MMIO hits của B52R23 và sinh Lua để breakpoint ngay tại WRITE instruction của `DMA2_MADR`, `DMA2_BCR`, `DMA2_CHCR` và `GP0`.

PCSX-Redux API đã được recheck với tài liệu chính thức:
- breakpoints yêu cầu debugger + interpreter;
- `PCSX.addBreakpoint`, `PCSX.getRegisters`, `PCSX.pauseEmulator`, `PCSX.getMemPtr` đều đúng contract;
- breakpoint callback được bọc `pcall`.

Runtime helper:
- `gaia_arm24()`: arm capture ngay trước target menu;
- `gaia_arm24(N)`: bỏ qua N DMA start đầu;
- `gaia_next24()`: arm lại và resume sang DMA start kế;
- `gaia_save24()`: save TRACE.tsv + 2 MiB RAM snapshot + META.

Analyzer:
- decode CHCR direction/step/SyncMode/start;
- decode BCR transfer length;
- SyncMode 0/1: extract linear DMA source;
- SyncMode 2: parse linked-list GPU nodes;
- scan GP0 A0h/80h/C0h;
- nếu capture được GP0 A0h + 2 parameter words thì report x/y/w/h của VRAM upload.

Local authoring checks:
- generator py_compile PASS
- **B52R24 TRACE GENERATOR SELFTEST PASS**
- analyzer py_compile PASS
- **B52R24 TRACE ANALYZER SELFTEST PASS**

ROM/runtime state:
- **PENDING**
- chưa có TRACE/RAM capture từ Gaia Master thật;
- chưa được gọi source-found.

Evidence rule:
MADR/BCR/CHCR chỉ chứng minh RAM source của DMA transaction đã bắt. Nó chưa chứng minh disc file/archive member và cũng chưa chứng minh transaction đó là chính label Nhật. Cần correlate đúng frame với GPU Logger/origin trước khi promote.

B52R25 chỉ được bắt đầu khi B52R24 capture được transaction gắn với visible `ストーリーモード`; nhiệm vụ B52R25 là backtrace RAM buffer về load/decompression/archive ownership rồi mới xác định patch nhỏ nhất.

Overall Runtime PASS vẫn **NO**.

## B52R25 - source-buffer writer watch tooling

Tooling đã được chuẩn bị, nhưng **execution gate vẫn phụ thuộc B52R24 real capture**:

- `tools/gaia_b52r25_writer_watch_generator.py`
- `tools/gaia_b52r25_writer_pc_resolver.py`
- `tools/00_BUILD_B52R25_WRITER_WATCH.cmd`
- `tools/00_RESOLVE_B52R25_WRITER_PC.cmd`
- `B52R25_SOURCE_BUFFER_WRITER_WATCH.md`

Writer-watch generator:
- input `GaiaMaster_B52R24_TRACE.tsv`;
- hỗ trợ linear DMA SyncMode 0/1;
- tính source RAM range từ MADR/BCR/CHCR;
- đặt Write breakpoint cho cả KSEG0 + KSEG1 alias;
- Lua helper `gaia_arm25(N)` có thể skip N distinct writer PCs;
- capture actual write address/width/cause + PC/RA/SP + A0-A3;
- `gaia_save25()` xuất `GaiaMaster_B52R25_WRITER_TRACE.tsv`.

SyncMode 2 linked-list không được giả định là linear asset source. Với mode 2 phải quay lại GPU-origin/texture-upload evidence hoặc bắt transaction SyncMode 0/1 phù hợp.

Writer-PC resolver:
- nhận WRITER_TRACE.tsv + exact B52R14R1/CLEAN BIN;
- verify SHA1;
- map main-EXE writer PC về exact `SLPS_020.75` file offset;
- tìm heuristic function start + direct `jal` callers;
- in +/-12 MIPS instructions;
- phân loại BIOS;
- nếu PC ở RAM nhưng ngoài main SLPS text, đánh dấu likely overlay/runtime-loaded code thay vì gán bừa.

Local authoring checks:
- **B52R25 WRITER WATCH GENERATOR SELFTEST PASS**
- **B52R25 WRITER PC RESOLVER SELFTEST PASS**
- py_compile PASS cho cả hai.

Real runtime:
- **PENDING**
- chưa có writer hit thật;
- chưa có disc/archive ownership proof;
- chưa patch ROM.

Evidence rule:
CPU Write breakpoint chỉ bắt CPU writes. Nếu buffer được fill hoàn toàn bằng hardware DMA và không có CPU transform, writer watch có thể không fire; lúc đó phải pivot sang CD/DMA load ownership.

Overall Runtime PASS vẫn **NO**.

## B52R26 - CD DMA provenance fallback

Prepared tooling:

- `tools/gaia_b52r26_cd_dma_locator.py`
- `tools/gaia_b52r26_cd_gpu_overlap_analyzer.py`
- `tools/00_RUN_B52R26_CD_DMA_LOCATOR.cmd`
- `tools/00_COMPARE_B52R26_CD_GPU_OVERLAP.cmd`
- `B52R26_CD_DMA_PROVENANCE.md`

Purpose:
- fallback when B52R25 CPU writer-watch does not fire or a direct disc load is suspected;
- DMA3 is CDROM -> RAM;
- locator finds main-EXE writes to DMA3 MADR/BCR/CHCR and generates PCSX capture Lua;
- overlap analyzer compares B52R26 CD destination range against the proven B52R24 GPU-source RAM range.

Verdicts:
- `EXACT_RANGE_MATCH`
- `GPU_SOURCE_FULLY_INSIDE_CD_DMA`
- `PARTIAL_OVERLAP`
- `NO_OVERLAP`
- `GPU_SYNC2_COMMAND_LIST`

Validation:
- synthetic DMA3 MADR/CHCR locator core self-test PASS;
- synthetic CD/GPU overlap core self-test PASS.

Real execution:
- **PENDING**
- no real CD DMA capture
- no real overlap verdict
- no ISO file/LBA ownership proof.

Evidence rule:
Even exact/full-cover overlap is only same-transition upstream RAM-load evidence. It does not by itself prove which ISO file/member/LBA supplied the bytes.

Overall Runtime PASS remains **NO**.

## B52R27 - disc payload fingerprint resolver

Prepared read-only tooling:

- `tools/gaia_b52r27_disc_payload_fingerprint.py`
- `tools/00_RUN_B52R27_DISC_FINGERPRINT.cmd`
- `B52R27_DISC_PAYLOAD_FINGERPRINT.md`

Purpose:
- shortcut from a proven B52R24 linear `DMA_SOURCE.bin` back to ISO ownership;
- verify exact B52R14R1/CLEAN SHA1;
- parse MODE2/Form1 ISO9660 logical files;
- search full captured payload across file data;
- fallback to aligned 64-byte start/middle/end anchors;
- report file path + file-relative offset + extent + starting LBA.

Verdicts:
- `EXACT_DISC_PAYLOAD_MATCH_FOUND`
- `ALIGNED_ANCHOR_EVIDENCE_ONLY`
- `NO_DISC_FINGERPRINT_MATCH`

Validation:
- full Python source compile PASS during authoring;
- **B52R27 DISC FINGERPRINT SELFTEST PASS**.

Real execution:
- **PENDING**, because no real B52R24 DMA_SOURCE payload has been supplied yet.

Evidence rule:
EXACT is strong verbatim disc-payload evidence. ALIGNED is suggestive only. NO match supports the hypothesis that the GPU-source buffer was transformed/decompressed/rasterized/composed, but does not identify which transform.

No BDP mutation or ROM patch occurs here.

Overall Runtime PASS remains **NO**.

## B52R28 - Setloc/LBA CD-DMA provenance upgrade

This is a **newer provenance layer built on top of the existing B52R26 DMA3 range-overlap tooling**. It does not replace B52R26.

Files:

- `tools/gaia_b52r28_cd_dma_provenance_generator.py`
- `tools/gaia_b52r28_cd_dma_provenance_analyzer.py`
- `tools/00_BUILD_B52R28_CD_DMA_WATCH.cmd`
- `tools/00_ANALYZE_B52R28_CD_DMA.cmd`
- `B52R28_CD_DMA_PROVENANCE_TRACE.md`

Adds:
- direct PCSX-Redux MMIO watches for CD host registers + DMA3;
- MIPS store-value decode so BIOS/main-RAM writers can be traced;
- CD bank tracking;
- `Setloc 02h`, `ReadN 06h`, `ReadS 1Bh`, Stop/Pause tracking;
- BCD MSF -> LBA candidate conversion;
- DMA3 destination overlap against the B52R24 linear target source;
- optional exact-BIN ISO9660 owner mapping from tracked LBA to file path/offset/LBA/raw BIN offset.

Validation performed from the committed Python source:
- generator compile PASS
- **B52R28 CD DMA PROVENANCE GENERATOR SELFTEST PASS**
- analyzer compile PASS
- **B52R28 CD DMA PROVENANCE ANALYZER SELFTEST PASS**

Real Gaia Master execution:
- **PENDING**
- no real Setloc/LBA trace;
- no real DMA3/target overlap;
- no file/LBA ownership claim.

Evidence rule:
A direct DMA3 overlap proves runtime destination overlap only. A tracked LBA/file owner is a provenance candidate whose strength depends on Setloc/sequential tracking. Do not patch from B52R28 alone.

## B52R29 - overlay writer fingerprint resolver

This is the overlay branch after B52R25. It does not replace the existing B52R27 disc-payload fingerprint tool.

Prerequisite update:
`gaia_save25()` now also writes `GaiaMaster_B52R25_WRITER_RAM.bin` (2 MiB) at the paused writer hit.

Files:

- `tools/gaia_b52r29_overlay_fingerprint_resolver.py`
- `tools/00_RESOLVE_B52R29_OVERLAY_FINGERPRINT.cmd`
- `B52R29_OVERLAY_WRITER_FINGERPRINT.md`

Inputs:
- B52R25 WRITER_TRACE.tsv
- B52R25 WRITER_RAM.bin
- exact B52R14R1/CLEAN BIN

Behavior:
- main-SLPS writer PCs remain handled by B52R25 resolver;
- RAM PCs outside main SLPS are treated as overlay/runtime-loaded candidates;
- exact code anchors 96/64/48/32 bytes are searched across ISO9660 Form1 files;
- 256-byte surrounding context similarity ranks candidates;
- report includes file path, file offset, extent, LBA and raw BIN offset.

Validation:
- compile PASS
- **B52R29 OVERLAY FINGERPRINT RESOLVER SELFTEST PASS**
- committed B52R25 generator verified to contain the 2 MiB writer-RAM snapshot path and self-test guard.

Real execution:
- **PENDING**
- no writer snapshot supplied;
- no overlay owner identified.

Evidence rule:
A code-owner fingerprint identifies where the writer code came from, not the asset/data bytes producing the visible Japanese UI.

## Closed/dead reverse paths

Do NOT restart these without genuinely new evidence:

- exact PRGPACK CP932 rewrite of known B52R15/B52R20 locations;
- whole-ISO alternate encodings;
- raw TIM atlas scan;
- JIS/tile/glyph-index representations;
- unknown constant-bias JIS glyph scan;
- raw 4/8/16bpp sibling preview around known text owners.

## Next reverse direction

Treat remaining visible UI as one of:

1. compressed/custom-packed graphic or script data;
2. runtime-generated large-font UI using a different source/renderer;
3. custom archive member decoding not exposed by raw preview;
4. possibly texture/tile composition whose source is not a plain sequential glyph list.

Execution order now: **B52R22** static probe → **B52R23** GPU/DMA locator → **B52R24** exact target DMA capture. For a linear B52R24 payload, run existing **B52R27 disc-payload fingerprint** immediately. Use **B52R25 writer-watch** for CPU transforms. If direct CD fill is suspected, existing **B52R26** gives DMA3 range evidence and new **B52R28** upgrades that path with Setloc/LBA/ISO-owner provenance. If B52R25 writer PC lands outside main SLPS, use **B52R29** overlay fingerprint on the writer-time RAM snapshot. SyncMode 2 remains GPU-origin/texture-upload territory. Do not start another whole-disc encoding census.

Recommended first target:
- main menu `ストーリーモード` because it is large, stable, easy to identify visually.

Then:
- `キャラクターセレクト`
- `冒険のはじまり`
- Save/Load/Password UI

## Translation status / wording

Do not lose the user-facing wording targets:

- ストーリーモード -> Cốt truyện / Chế độ cốt truyện
- 対戦モード -> Đối kháng
- 武器スキルリスト -> Kỹ năng vũ khí
- オプション -> Tùy chọn
- キャラクターセレクト -> Chọn nhân vật
- はじめから -> Bắt đầu
- つづきから -> Chơi tiếp
- ロード方法をえらんでね -> Chọn cách tải / Chọn tải
- セーブデータをロードする -> Tải dữ liệu lưu
- パスワードを使う -> Dùng mật khẩu
- 冒険のはじまり -> Bắt đầu cuộc phiêu lưu / Khởi đầu hành trình

Use shorter wording only when pixel/byte space proves necessary.

## Local disk / cleanup issue

User reported local GitHub working copy is already around **20 GB**.

From now on:
- stop accumulating full-disc BIN for every diagnostic milestone;
- tools/reports/CSV are cheap and should be kept;
- ROM/BIN/CUE/ISO remain local-only and ignored;
- prefer one exact current runtime base + one newest output;
- generated TIM/raw preview atlases may be deleted after evidence is captured in reports;
- prepare a conservative `GaiaMaster_SAFE_CLEANUP.cmd` later:
  - never delete CLEAN;
  - never delete current known base;
  - never touch source/manifests/reports/tools/.git;
  - list candidates before deleting;
  - target superseded full BINs and temporary preview/export folders.

Do not casually tell the user to delete files by hand until keep/delete rules are explicit.

## Allowed claims

Allowed:
- B50 static exact-overlay PASS
- B51R2 real CLEAN dry-run/build PASS
- B52R11R3 quick-path runtime OK
- B52R12 current path was user-confirmed OK
- B52R14R1 static/read-back/checksum PASS
- B52R15-B52R20 read-only reverse results as recorded
- B52R21R1 visible UI source path is runtime-dead based on user screenshots
- B52R22 tooling source compiles and self-tests PASS; ROM execution is still pending
- B52R23 GPU upload locator compiles and self-tests PASS; ROM/runtime correlation is still pending
- B52R24 trace generator/analyzer compile and self-test PASS; real TRACE/RAM capture is still pending
- B52R25 writer-watch generator/resolver compile and self-test PASS; execution remains gated on a target B52R24 capture
- B52R26 DMA3 locator/overlap core logic self-tests PASS; real CD DMA capture is pending
- B52R27 disc fingerprint full source compiles and self-tests PASS; real payload search is pending
- B52R28 Setloc/LBA CD-DMA provenance generator/analyzer compile and self-test PASS; real trace pending
- B52R29 overlay fingerprint resolver compiles and self-tests PASS; real writer snapshot pending

Not allowed:
- overall Runtime PASS
- claiming the remaining UI source has already been identified
- claiming B52R21R1 translated the visible UI

## Fresh-chat continuation

Use `NEXT_CHAT_PROMPT.md`.

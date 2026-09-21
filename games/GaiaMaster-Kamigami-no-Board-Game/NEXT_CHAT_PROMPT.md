# Prompt mở phiên chat mới - Gaia Master

Copy nguyên đoạn dưới đây vào phiên mới:

> Tiếp tục Gaia Master PS1 từ `games/GaiaMaster-Kamigami-no-Board-Game/HANDOFF_CURRENT.md` trên branch `gaia-character-select-font-atlas-reverse-01` của repo `RVTGMzz/PSXVH`. Đọc thêm `LATEST.md`. Current exact working base là B52R14R1 SHA1 `0ced9982e1b00566b42ace047236378826c2aa1c`; CLEAN Japan SHA1 `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`. B52R11R3 quick-path runtime OK, B52R12 user-confirmed path OK. SCR_DATA có 303 nested BDP-like containers, mọi mutation SCR_DATA phải repair checksum bottom-up. UI reverse B52R15-B52R21R1 đã đóng các đường dead: 41 known CP932 hits đều already-changed, B52R17 không có alternate live source, B52R18 đã review đủ 173 raw TIM không có target UI, B52R19 JIS/tile-index = 0, B52R20 owner/sibling raw previews không lộ target UI, và B52R21R1 patch các known PRGPACK copies nhưng runtime screenshots vẫn không đổi: main menu, Character Select và 冒険のはじまり vẫn Nhật. Kết luận: các known PRGPACK CP932 copies là runtime-dead cho các màn này. Không scan lại plaintext/alternate encoding/TIM/JIS và không re-patch các offset đó. B52R22 read-only live-source probe đã được commit và self-test PASS nhưng ROM execution còn pending. B52R23 GPU upload locator cũng đã được commit: `tools/gaia_b52r23_gpu_upload_locator.py` + launcher `00_RUN_B52R23_GPU_UPLOAD_LOCATOR.cmd`; py_compile/self-test PASS, ROM/runtime correlation pending. Locator còn tự sinh `GaiaMaster_B52R23_PCSX_BREAKPOINTS.lua`; load vào PCSX-Redux và gọi `gaia_arm()` ngay trước target menu để armed hit đầu tiên log PC/RA/SP + pause. Thứ tự hiện tại: B52R22 trên exact B52R14R1, B52R23 trên cùng BIN, rồi B52R24 exact-MMIO capture. B52R24 đã có generator/analyzer + launcher, self-test PASS; nó bắt WRITE tại DMA2_MADR/BCR/CHCR/GP0, pause ở DMA start, và `gaia_save24()` xuất TRACE.tsv + 2 MiB RAM + META. Analyzer giải SyncMode, BCR/MADR, linked-list/linear payload và GP0 A0h rectangle. Dùng GPU Logger/Show origins để correlate đúng ストーリーモード. Chưa có real capture/source-found. B52R25 tooling đã chuẩn bị sẵn: writer-watch generator + writer-PC resolver, nhưng execution chỉ mở sau khi B52R24 bắt được target transaction. Với SyncMode 0/1, B52R25 watch source RAM writes và map writer PC về SLPS/overlay; SyncMode 2 không được coi là linear asset source. B52R26 đã chuẩn bị làm fallback DMA3 CDROM->RAM: capture MADR/BCR/CHCR và so range đích CD với range nguồn GPU của B52R24. Exact/full-cover chỉ là upstream RAM-load evidence, chưa phải ISO file/LBA proof. B52R27 disc fingerprint cũng đã sẵn sàng: lấy real `GaiaMaster_B52R24_DMA_SOURCE.bin` và tìm exact/aligned payload trong MODE2/Form1 ISO files để map thẳng file/offset/LBA khi dữ liệu còn nguyên. Không đụng font, không gọi overall Runtime PASS. Local repo đã gần 20GB, tránh tạo thêm full BIN không cần thiết và chuẩn bị workflow cleanup an toàn sau khi có checkpoint mới.

## Files đọc đầu tiên

```text
games/GaiaMaster-Kamigami-no-Board-Game/HANDOFF_CURRENT.md
games/GaiaMaster-Kamigami-no-Board-Game/LATEST.md
games/GaiaMaster-Kamigami-no-Board-Game/NEXT_CHAT_PROMPT.md
games/GaiaMaster-Kamigami-no-Board-Game/SESSION_HANDOFF_2026-09-19_B52R21R1_UI_SOURCE_PIVOT.md
games/GaiaMaster-Kamigami-no-Board-Game/B52R22_LIVE_SOURCE_PROBE.md
games/GaiaMaster-Kamigami-no-Board-Game/B52R23_GPU_UPLOAD_RUNTIME_TRACE.md
games/GaiaMaster-Kamigami-no-Board-Game/B52R24_RUNTIME_DMA_SOURCE_CAPTURE.md
games/GaiaMaster-Kamigami-no-Board-Game/B52R25_SOURCE_BUFFER_WRITER_WATCH.md
games/GaiaMaster-Kamigami-no-Board-Game/B52R26_CD_DMA_PROVENANCE.md
games/GaiaMaster-Kamigami-no-Board-Game/B52R27_DISC_PAYLOAD_FINGERPRINT.md
```

## Do not regress

- không dùng tên repo cũ `ronvotri/Viet-Hoa-PS1`;
- không quay lại B51 như thể chưa có B52;
- không gọi B52R21R1 là visible-UI PASS;
- không scan lại raw TIM 173 asset;
- không scan lại alternate encoding hoặc JIS tile-index;
- không patch lại known PRGPACK CP932 UI copies;
- không sửa font;
- không tạo hàng loạt full-disc BIN cho read-only probes;
- Runtime PASS toàn game vẫn NO.

## First action

1. Chạy `tools/00_RUN_B52R22_LIVE_SOURCE_PROBE.cmd` với exact B52R14R1.
2. Chạy `tools/00_RUN_B52R23_GPU_UPLOAD_LOCATOR.cmd` trên cùng BIN.
3. Đọc B52R22 report/CSV và B52R23 `GPU_UPLOAD_LOCATOR_REPORT.txt` + `GPU_BREAKPOINTS.txt`.
4. Kéo `GaiaMaster_B52R23_GPU_MMIO_HITS.csv` vào `tools/00_BUILD_B52R24_PCSX_CAPTURE.cmd` để tạo capture Lua.
5. PCSX-Redux interpreter + debugger: load Lua, gọi `gaia_arm24()` ngay trước main menu, khi pause gọi `gaia_save24()`.
6. Kéo `GaiaMaster_B52R24_TRACE.tsv` vào `tools/00_ANALYZE_B52R24_CAPTURE.cmd` và correlate với GPU Logger/Show origins.
7. Nếu target capture là SyncMode 0/1, kéo TRACE vào `tools/00_BUILD_B52R25_WRITER_WATCH.cmd`, arm writer watch trước transition, rồi `gaia_save25()` khi hit.
8. Dùng `tools/00_RESOLVE_B52R25_WRITER_PC.cmd` với WRITER_TRACE.tsv + exact B52R14R1 để map writer PC về SLPS/function/callers. Nếu SyncMode 2, tiếp tục GPU-origin/texture-upload trace thay vì writer-watch linear.
9. Nếu writer-watch không fire hoặc nghi direct CD load, chạy `tools/00_RUN_B52R26_CD_DMA_LOCATOR.cmd`, capture bằng Lua sinh ra, rồi so với B52R24 bằng `tools/00_COMPARE_B52R26_CD_GPU_OVERLAP.cmd`.
10. Với B52R24 linear payload, chạy `tools/00_RUN_B52R27_DISC_FINGERPRINT.cmd` cùng `GaiaMaster_B52R24_DMA_SOURCE.bin` + exact B52R14R1. Nếu EXACT, lấy file/offset/LBA làm ownership candidate mạnh; nếu NO match, ưu tiên CPU transform/decompress/rasterize trace.
11. Chưa patch disc cho tới khi ownership được chứng minh. Runtime PASS toàn game vẫn NO.

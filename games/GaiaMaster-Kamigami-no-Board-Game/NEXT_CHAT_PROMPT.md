# Prompt mở phiên chat mới - Gaia Master

Copy nguyên đoạn dưới đây vào phiên mới:

> Tiếp tục Gaia Master PS1 từ `games/GaiaMaster-Kamigami-no-Board-Game/HANDOFF_CURRENT.md` trên branch `gaia-character-select-font-atlas-reverse-01` của repo `RVTGMzz/PSXVH`. Đọc thêm `LATEST.md`. Current exact working base là B52R14R1 SHA1 `0ced9982e1b00566b42ace047236378826c2aa1c`; CLEAN Japan SHA1 `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`. B52R11R3 quick-path runtime OK, B52R12 user-confirmed path OK. SCR_DATA có 303 nested BDP-like containers, mọi mutation SCR_DATA phải repair checksum bottom-up. UI reverse B52R15-B52R21R1 đã đóng các đường dead: 41 known CP932 hits đều already-changed, B52R17 không có alternate live source, B52R18 đã review đủ 173 raw TIM không có target UI, B52R19 JIS/tile-index = 0, B52R20 owner/sibling raw previews không lộ target UI, và B52R21R1 patch các known PRGPACK copies nhưng runtime screenshots vẫn không đổi: main menu, Character Select và 冒険のはじまり vẫn Nhật. Kết luận: các known PRGPACK CP932 copies là runtime-dead cho các màn này. Không scan lại plaintext/alternate encoding/TIM/JIS và không re-patch các offset đó. B52R22 read-only live-source probe đã được commit và self-test PASS nhưng ROM execution còn pending. B52R23 GPU upload locator cũng đã được commit: `tools/gaia_b52r23_gpu_upload_locator.py` + launcher `00_RUN_B52R23_GPU_UPLOAD_LOCATOR.cmd`; py_compile/self-test PASS, ROM/runtime correlation pending. Locator còn tự sinh `GaiaMaster_B52R23_PCSX_BREAKPOINTS.lua`; load vào PCSX-Redux và gọi `gaia_arm()` ngay trước target menu để armed hit đầu tiên log PC/RA/SP + pause. Thứ tự: chạy B52R22 trên exact B52R14R1, sau đó chạy B52R23 trên cùng BIN; dùng B52R23 breakpoint shortlist + PCSX-Redux GPU Logger/Show origins để correlate ストーリーモード. Nếu B52R22 có decoded target/TIM thì B52R23 chứng minh ownership/render; nếu B52R22 âm tính thì B52R23 là entry point cho runtime VRAM/upload trace. Không đụng font, không gọi overall Runtime PASS. Local repo đã gần 20GB, tránh tạo thêm full BIN không cần thiết và chuẩn bị workflow cleanup an toàn sau khi có checkpoint mới.

## Files đọc đầu tiên

```text
games/GaiaMaster-Kamigami-no-Board-Game/HANDOFF_CURRENT.md
games/GaiaMaster-Kamigami-no-Board-Game/LATEST.md
games/GaiaMaster-Kamigami-no-Board-Game/NEXT_CHAT_PROMPT.md
games/GaiaMaster-Kamigami-no-Board-Game/SESSION_HANDOFF_2026-09-19_B52R21R1_UI_SOURCE_PIVOT.md
games/GaiaMaster-Kamigami-no-Board-Game/B52R22_LIVE_SOURCE_PROBE.md
games/GaiaMaster-Kamigami-no-Board-Game/B52R23_GPU_UPLOAD_RUNTIME_TRACE.md
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
4. Dùng PCSX-Redux GPU Logger + Show origins và B52R23 breakpoint shortlist để correlate `ストーリーモード`.
5. Chỉ khi live ownership/source buffer được chứng minh mới làm B52R24 patch; Runtime PASS toàn game vẫn NO.

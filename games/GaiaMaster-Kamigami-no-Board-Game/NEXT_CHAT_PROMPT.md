# Prompt mở phiên chat mới - Gaia Master

Copy nguyên đoạn dưới đây vào phiên mới:

> Tiếp tục Gaia Master PS1 từ `games/GaiaMaster-Kamigami-no-Board-Game/HANDOFF_CURRENT.md` trên branch `gaia-character-select-font-atlas-reverse-01` của repo `RVTGMzz/PSXVH`. Đọc thêm `LATEST.md`. Current exact working base là B52R14R1 SHA1 `0ced9982e1b00566b42ace047236378826c2aa1c`; CLEAN Japan SHA1 `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`. B52R11R3 quick-path runtime OK, B52R12 user-confirmed path OK. SCR_DATA có 303 nested BDP-like containers, mọi mutation SCR_DATA phải repair checksum bottom-up. UI reverse B52R15-B52R21R1 đã đóng các đường dead: 41 known CP932 hits đều already-changed, B52R17 không có alternate live source, B52R18 đã review đủ 173 raw TIM không có target UI, B52R19 JIS/tile-index = 0, B52R20 owner/sibling raw previews không lộ target UI, và B52R21R1 patch các known PRGPACK copies nhưng runtime screenshots vẫn không đổi: main menu, Character Select và 冒険のはじまり vẫn Nhật. Kết luận: các known PRGPACK CP932 copies là runtime-dead cho các màn này. Không scan lại plaintext/alternate encoding/TIM/JIS và không re-patch các offset đó. B52R22 read-only live-source probe đã được commit: `tools/gaia_b52r22_live_source_probe.py` + launcher `00_RUN_B52R22_LIVE_SOURCE_PROBE.cmd`; py_compile/self-test PASS nhưng ROM execution còn pending. Bước đầu tiên là chạy B52R22 trên exact B52R14R1 và đọc report/CSV. Nếu decode lộ target text/TIM thì đi B52R23 ownership/render proof; nếu không thì B52R23 runtime trace VRAM/upload/decompression của ストーリーモード. Không đụng font, không gọi overall Runtime PASS. Local repo đã gần 20GB, tránh tạo thêm full BIN không cần thiết và chuẩn bị workflow cleanup an toàn sau khi có checkpoint mới.

## Files đọc đầu tiên

```text
games/GaiaMaster-Kamigami-no-Board-Game/HANDOFF_CURRENT.md
games/GaiaMaster-Kamigami-no-Board-Game/LATEST.md
games/GaiaMaster-Kamigami-no-Board-Game/NEXT_CHAT_PROMPT.md
games/GaiaMaster-Kamigami-no-Board-Game/SESSION_HANDOFF_2026-09-19_B52R21R1_UI_SOURCE_PIVOT.md
games/GaiaMaster-Kamigami-no-Board-Game/B52R22_LIVE_SOURCE_PROBE.md
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

1. Chạy `tools/00_RUN_B52R22_LIVE_SOURCE_PROBE.cmd` với exact B52R14R1 SHA1 làm oracle.
2. Đọc `GaiaMaster_B52R22_LIVE_SOURCE_PROBE_REPORT.txt` + hai CSV.
3. Nếu có decoded target/TIM evidence, làm B52R23 ownership/render proof.
4. Nếu không có static evidence, làm B52R23 runtime trace `ストーリーモード` VRAM/upload/decompression.
5. Chỉ khi tìm được source có bằng chứng mới tạo patch/build để user test; sau checkpoint hữu ích kế tiếp mới tạo SAFE cleanup workflow cho repo local ~20GB.

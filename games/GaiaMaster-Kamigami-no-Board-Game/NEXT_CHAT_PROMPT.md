# Prompt mở phiên chat mới - Gaia Master New Vietnamese Font / NF2R1

Copy nguyên đoạn dưới đây vào phiên mới:

> Tiếp tục Gaia Master PS1 từ repo `RVTGMzz/PSXVH`, branch `gaia-new-vietnamese-font-experiment-01`. Đọc trước `games/GaiaMaster-Kamigami-no-Board-Game/SESSION_HANDOFF_2026-09-30_GAIA_NEW_FONT_NF2R1.md`, `FONT_EXPERIMENT_HANDOFF.md`, `LATEST.md`, `NF2R1_CACHE_FILL_HELPER_PROBE.md`. Exact working base vẫn là B52R14R1 SHA1 `0ced9982e1b00566b42ace047236378826c2aa1c`; CLEAN SHA1 `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`. Không quay lại vá font cũ. NF1 V0.1 chỉ là technical proof. Hướng visual hiện tại là font Việt mới hoàn toàn theo screenshot reference: nét mảnh, đủ toàn bộ tiếng Việt, vertical metric giống font Anh gốc, spacing proportional. NF1 V0.2 đã định nghĩa 229 source glyphs = 95 ASCII + 134 Vietnamese non-ASCII. NF1 V0.3 đã có per-glyph ink/advance metrics. Current mapping-only custom capacity mới chứng minh 64 slot, thiếu 70 slot cho full Vietnamese set nên không được claim full runtime support. Real NF2 scan đã chạy thành công trên exact B52R14R1: 347 offset+6 xrefs; cache-hit byte6 reads xác nhận tại 0x8003CB54 / 0x8003CBF4 / 0x8003CC08; không có direct +6 WRITE trong known cache-miss window. Broad 8-breakpoint NF2 Lua đã bị supersede, không dùng nữa. NF2R1 là đường hiện tại: caller 0x8003CC30 a0=state, 0x8003CC34 a2=state+0x64 cache_write, 0x8003CC38 jal 0x8003C67C, return 0x8003CC40. Tool `gaia_nf2r1_cache_fill_helper_probe.py` + launcher đã commit. Bước kế tiếp duy nhất là chạy NF2R1 runtime capture trong PCSX-Redux, gọi `gaia_arm_nf2r1()`, cho hiện một dòng chữ, khi pause gọi `gaia_save_nf2r1()`, rồi phân tích `GaiaMaster_NF2R1_CACHE_FILL_TRACE.tsv`. Chỉ cần 1 event đầu tiên. Chưa build VWF ROM, chưa sửa global cache stride/pointer, chưa gọi Runtime PASS.

## Files đọc đầu tiên

```text
games/GaiaMaster-Kamigami-no-Board-Game/SESSION_HANDOFF_2026-09-30_GAIA_NEW_FONT_NF2R1.md
games/GaiaMaster-Kamigami-no-Board-Game/FONT_EXPERIMENT_HANDOFF.md
games/GaiaMaster-Kamigami-no-Board-Game/LATEST.md
games/GaiaMaster-Kamigami-no-Board-Game/NF1_V02_FULL_CHARSET_PLAN.md
games/GaiaMaster-Kamigami-no-Board-Game/NF1_V03_REFERENCE_METRICS.md
games/GaiaMaster-Kamigami-no-Board-Game/NF2_CACHE_ADVANCE_PROBE.md
games/GaiaMaster-Kamigami-no-Board-Game/NF2R1_CACHE_FILL_HELPER_PROBE.md
```

## Do not regress

- không quay về branch font cũ như thể NF1/NF2 chưa tồn tại;
- không tiếp tục polish font cũ;
- không coi NF1 V0.1 là final visual target;
- không dùng broad 8-breakpoint NF2 Lua cũ;
- không patch VWF trước runtime trace NF2R1;
- không sửa global cache stride / VRAM geometry / pointer redirect;
- không claim 229 glyph đã chạy trong game;
- không gọi overall Runtime PASS.

## First action

Nếu user chưa gửi NF2R1 TSV:
1. hướng dẫn cực ngắn, từng bước, tránh thuật ngữ;
2. chạy đúng B52R14R1 trong PCSX-Redux;
3. load `GaiaMaster_NF2R1_PCSX_CACHE_FILL_CAPTURE.lua`;
4. `gaia_arm_nf2r1()`;
5. cho hiện một dòng chữ;
6. khi pause: `gaia_save_nf2r1()`;
7. user gửi `GaiaMaster_NF2R1_CACHE_FILL_TRACE.tsv`.

Nếu user đã gửi TSV: phân tích ngay, không bắt họ chạy lại từ đầu.

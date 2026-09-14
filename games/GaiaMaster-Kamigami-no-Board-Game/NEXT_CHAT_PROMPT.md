# Prompt mở phiên chat mới — Gaia Master

Copy nguyên câu dưới đây vào phiên mới:

> Tiếp tục Gaia Master từ `games/GaiaMaster-Kamigami-no-Board-Game/HANDOFF_CURRENT.md` trên branch `gaia-character-select-font-atlas-reverse-01` của repo `ronvotri/Viet-Hoa-PS1`. Đọc thêm `LATEST.md`, `BATCH44_0.6.54.0.md`, `BATCH45_0.6.55.0_FRONTFACE_POLISH.md` và `REVERSE_WORKBENCH_0.1.md`. Mốc actual build đã chứng minh là `0.6.54.0 R5`: CLEAN SHA1 đúng, Batch42 560/560, Batch43 102/102, combined 662/662, legacy 397/397, return code 0. Runtime screenshot cho thấy chưa thể gọi whole-game Runtime PASS: main menu, Character Select, Story mở đầu, chapter card `冒険のはじまり`, prompt mua đất và nhiều text khác vẫn còn Nhật. `0.6.55.0 Batch45` đã được chuẩn bị để sửa 19 dòng intro, bỏ dấu `=` gây glyph rác và nâng thanh ngang `Đ/đ` lên 1 px; static selftest PASS nhưng cần runtime-test đúng CUE 0.6.55.0. Một Reverse Workbench 0.1 read-only đã được thêm gồm `gaia_graphic_asset_census_0.1.py`, `gaia_runtime_target_locator_0.1.py` và `00_RUN_REVERSE_WORKBENCH_0.1.cmd`: dùng CLEAN BIN để census standard PS-X TIM theo BDP owner, ưu tiên Character Select owner 29 và exact-locate `冒険のはじまり`/text lấy từ screenshot. Workbench không patch BIN và không được dùng để tự nâng version production. Sau runtime Batch45, ưu tiên reverse graphic asset của main menu / Character Select và scanner-driven exact offsets cho Story/chapter/purchase prompt. Giữ kiến trúc native 12x12 / 72-byte / 4bpp / mapping-only / frozen 60 glyph; không renderer hook, pointer redirect, 12x16, 6x12 hay composite overlay.

## Current branch

```text
gaia-character-select-font-atlas-reverse-01
```

## Files phải đọc đầu tiên

```text
games/GaiaMaster-Kamigami-no-Board-Game/HANDOFF_CURRENT.md
games/GaiaMaster-Kamigami-no-Board-Game/LATEST.md
games/GaiaMaster-Kamigami-no-Board-Game/BATCH44_0.6.54.0.md
games/GaiaMaster-Kamigami-no-Board-Game/BATCH45_0.6.55.0_FRONTFACE_POLISH.md
games/GaiaMaster-Kamigami-no-Board-Game/REVERSE_WORKBENCH_0.1.md
```

## First action in next chat

```text
1. Nếu user gửi BUILD_LOG: sửa đúng lỗi build trước.
2. Nếu user gửi FINAL_REPORT + screenshot: phân tích runtime 0.6.55.0 ngay; không bắt kể lại lịch sử.
3. Chỉ khi screenshot chứng minh ổn mới khóa intro/font Batch45.
4. Phân tích output Reverse Workbench 0.1 nếu user gửi.
5. Reverse main-menu / Character Select graphic assets, ưu tiên owner 29.
6. Continue exact-offset discovery for Story / chapter / purchase prompt.
```

## Reverse Workbench 0.1 outputs

```text
GaiaMaster_GRAPHIC_ASSET_CENSUS_0.1_REPORT.txt
GaiaMaster_GRAPHIC_ASSET_CENSUS_0.1_OWNERS.csv
GaiaMaster_GRAPHIC_ASSET_CENSUS_0.1_TIM.csv
GaiaMaster_RUNTIME_TARGET_LOCATOR_0.1_REPORT.txt
```

Known Character Select anchor:

```text
PRGPACK.BDP + 0xBFD2C
owner = 29
owner-local = +0x580
source = キャラクターをえらんでね
```

The committed repo does not contain the full `0.6.38.0` scanner CSV, and `冒険のはじまり` is not in the committed Batch43 manifest/code search. Do not invent an offset. Run/analyze the locator against the CLEAN BIN.

## Hard contracts

```text
CLEAN SHA1 = f4d5298583c90d89c4b7e51d2dde160ee07f2aec
Batch42 exact = 560/560
Batch43 visible = 102/102
Combined exact = 662/662
Legacy = 397/397
```

## Do not regress

- production source must consume staged `Core/translation`;
- dynamic rows must not overlap master-owned ranges;
- same-offset dynamic replacement requires exact source identity;
- Batch43 source identity is checked against CLEAN ROM;
- Batch43 may not overlap the 560 exact fields;
- preserve `%s`, `%d`, `%4d`, `%+3d`, `/V` and token order;
- do not equate 596/596 Translation Master coverage with whole-game coverage;
- Reverse Workbench is read-only discovery, not production promotion proof;
- do not create Batch46 from scanner/static evidence alone while Batch45 runtime is unresolved;
- do not call Runtime PASS before gameplay screenshots prove it.

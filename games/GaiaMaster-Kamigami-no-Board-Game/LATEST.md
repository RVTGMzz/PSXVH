# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-15**

## CURRENT — 0.6.55.0 BATCH45 FRONT-FACE POLISH

Trọng tâm hiện tại: **ổn định production chain + tăng chất lượng mặt tiền theo runtime screenshot**.

Status: **STATIC PASS / PACKAGE READY**. Chưa phải whole-game Runtime PASS.

## Mốc actual build đã chứng minh

Bản **0.6.54.0 R5** đã được user build thật từ CLEAN Japan BIN và PASS:

```text
Batch42 exact fields              = 560 / 560
Batch43 visible whole-game fields = 102 / 102
Combined exact fields             = 662 / 662
Legacy Alpha gate                 = 397 / 397
Build return code                 = 0
Final report                      = YES
```

Clean BIN SHA1:

`f4d5298583c90d89c4b7e51d2dde160ee07f2aec`

## Runtime audit sau R5

Runtime screenshots cho thấy pipeline đã hoạt động nhưng độ phủ hiển thị vẫn còn xa hoàn chỉnh. Các vùng còn Nhật rõ ràng gồm:

- main menu;
- Character Select;
- Story mở đầu;
- chapter/title card `冒険のはじまり`;
- prompt mua đất;
- nhiều Story / gameplay / help strings khác.

Main-menu + Character Select tiếp tục được xem là **graphic/texture candidates** cho tới khi asset được reverse chắc chắn.

Runtime còn phát hiện:

- intro có câu gượng và dấu `=` sinh ký tự rác giữa tiếng Việt;
- thanh ngang của `Đ/đ` nằm quá thấp, khó đọc.

## 0.6.55.0 Batch45

Package:

`GaiaMaster_0.6.55.0_Batch45_FRONTFACE_ONECLICK.zip`

Thay đổi:

```text
19 intro fields rewritten / byte-fit
unsafe '=' removed from intro
Đ/đ crossbar raised 1 px
architecture unchanged
```

Static validation:

```text
Python compile          = 61 files / 0 errors
Batch42 selftest        = PASS
Batch44 selftest        = PASS
Batch45 selftest        = PASS
base exact              = 560
whole-game visible      = 102
combined                = 662
intro polish            = 19 / 19
manifest overlap        = 0
```

ONECLICK workflow vẫn giữ nguyên:

```text
đặt CLEAN BIN cạnh 00_VIET_HOA_GAME.bat
-> double-click BAT
```

## Reverse Workbench 0.1

Đã thêm bộ reverse **read-only**, không đổi production version và không sửa BIN:

```text
tools/gaia_graphic_asset_census_0.1.py
tools/gaia_runtime_target_locator_0.1.py
tools/00_RUN_REVERSE_WORKBENCH_0.1.cmd
REVERSE_WORKBENCH_0.1.md
```

Workbench dùng để:

- quét standard PS-X TIM theo từng PRGPACK BDP owner;
- ưu tiên owner 29 của Character Select;
- exact-locate `冒険のはじまり` và các chuỗi Nhật lấy từ gameplay screenshot;
- báo exact offset, owner/local offset và NUL-field context trước khi cân nhắc patch.

Mốc Character Select đã chứng minh:

```text
PRGPACK.BDP + 0xBFD2C
owner 29 / local +0x580
キャラクターをえらんでね
```

Full scan CSV 0.6.38.0 không được commit vào repo và `冒険のはじまり` không nằm trong manifest Batch43 đã lưu, nên exact offset của chapter card vẫn cần CLEAN BIN để chạy locator.

## Kiến trúc vẫn khóa

```text
native 12x12 / 72-byte / 4bpp / LOW nibble first
static mapping-only
frozen 60-glyph Vietnamese codepage
legacy Alpha gate = 397/397
```

Không renderer hook, pointer redirect, 12x16, 6x12 hoặc composite overlay.

## Việc tiếp theo

1. Runtime-test đúng CUE 0.6.55.0, kiểm tra intro và `Đ/đ`.
2. Nếu screenshot gameplay ổn thì khóa intro/font Batch45.
3. Chạy/analyze Reverse Workbench 0.1 để reverse graphic assets main menu / Character Select.
4. Tìm exact offsets cho Story mở đầu, `冒険のはじまり`, prompt mua đất và các chuỗi visible còn Nhật.
5. Chỉ tạo batch production kế tiếp sau khi CLEAN-source/owner/field/fit/token/overlap gates đều qua.
6. Không gọi whole-game Runtime PASS trước khi có screenshot gameplay xác nhận.

# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-15**

## CURRENT — 0.6.55.1 BATCH45R2 FONT MICRO POLISH

Trọng tâm hiện tại: **khóa lỗi font còn lại từ runtime 0.6.55.0 trước khi quay lại reverse asset/text residual**.

Status: **SOURCE READY / STATIC GATES DESIGNED / RUNTIME CHƯA PASS**.

## Mốc actual build đã chứng minh

Bản **0.6.54.0 R5** vẫn là actual CLEAN-ROM build cuối cùng đã được user chứng minh bằng build log:

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

## Runtime 0.6.55.0

Screenshot `Thế giới đổi chủ` cho thấy:

- lỗi ký tự rác do `=` trong đoạn được chụp đã không còn xuất hiện;
- wording intro đọc được;
- nhưng font vẫn chưa thể khóa.

Lỗi mới được runtime chứng minh:

```text
đ thường: thanh ngang vẫn sai anchor, cần lên thêm 1 px và phải xuyên thân dọc bên phải của d
â/ê/ô: dấu ^ quá sát thân chữ
các chữ kiểu ấ/ế/ố...: structural mark + tone dễ nhập/đè nhau
```

Không có bằng chứng runtime cho thấy `Đ` hoa cũ bị lỗi. Vì vậy R2 tách hẳn `Đ` và `đ` thay vì dùng chung rule.

## 0.6.55.1 Batch45R2

Files:

```text
tools/build_gaia_06551_batch45r2_font_micro_polish.py
tools/00_BUILD_0.6.55.1_BATCH45R2_FONT_POLISH.cmd
BATCH45R2_0.6.55.1_FONT_MICRO_POLISH.md
```

Thiết kế sửa:

```text
Đ  = left-stem rule, trả vertical placement về pre-Batch45
đ  = auto-detect right ascender, bar xuyên stem, lên thêm 1 px so với 0.6.55.0
^/breve = reserve thêm 1 top row, nâng structural mark 1 px
stacked tone = tách sang side lane riêng
```

R2 **không sửa ngược builder 0.6.55.0**. Nó build lại chain 0.6.55.0 từ CLEAN rồi chỉ patch glyph trong SLPS.

Safety gates:

```text
60 glyph frozen codepage
72 bytes/glyph
bbox phải nằm trong 12x12
unaffected glyphs phải byte-identical với 0.6.55.0
Đ/đ phải qua đúng stem rule riêng
structural/tone rendered pixels không được collision
PRGPACK phải byte-for-byte không đổi bởi R2
font bytes phải read-back verify sau EDC/ECC regeneration
Batch42 560/560 recheck trước + sau font patch
Batch45 intro 19/19 recheck trước + sau font patch
```

**Chưa gọi Runtime PASS.** Cần build thật từ CLEAN BIN rồi screenshot gameplay.

## Reverse Workbench 0.1

Bộ reverse read-only vẫn giữ nguyên:

```text
tools/gaia_graphic_asset_census_0.1.py
tools/gaia_runtime_target_locator_0.1.py
tools/00_RUN_REVERSE_WORKBENCH_0.1.cmd
REVERSE_WORKBENCH_0.1.md
```

Mốc Character Select đã chứng minh:

```text
PRGPACK.BDP + 0xBFD2C
owner 29 / local +0x580
キャラクターをえらんでね
```

Main Menu + phần còn Nhật ở Character Select vẫn là graphic/texture candidates cho tới khi asset được xác định chắc chắn.

## Kiến trúc vẫn khóa

```text
native 12x12 / 72-byte / 4bpp / LOW nibble first
static mapping-only
frozen 60-glyph Vietnamese codepage
legacy Alpha gate = 397/397
```

Không renderer hook, pointer redirect, 12x16, 6x12 hoặc composite overlay.

## Việc tiếp theo

1. Build `0.6.55.1` từ exact CLEAN BIN.
2. Nếu có BUILD_LOG lỗi, sửa đúng gate đầu tiên trước.
3. Nếu FINAL_REPORT PASS, test `đ`, `Đ`, `â/ê/ô`, `ấ/ế/ố/ắ` nếu gặp được.
4. Chỉ khóa font khi gameplay screenshot xác nhận.
5. Sau đó tiếp tục Reverse Workbench Main Menu / Character Select.
6. Tiếp tục exact-offset discovery cho Story, `冒険のはじまり`, prompt mua đất.
7. Không gọi whole-game Runtime PASS trước bằng chứng gameplay.

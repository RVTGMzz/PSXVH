# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-14**

## Source-of-truth

Production vẫn khóa vào:

```text
native 12x12 / 72-byte / 4bpp
static mapping-only
60-glyph Vietnamese production codepage
legacy Alpha coverage gate = 397 / 397
```

Không quay lại narrow 6x12, 12x16, pointer redirect, composite overlay hay global spacing hook.

## Runtime mới nhất

`0.6.12.0` đã được user test. Kết quả:

```text
TRANSLATION PROGRESS VISIBLE
CONTENT QA INCOMPLETE
LOWERCASE ă HOTFIX V1 FAIL VISUALLY
```

Ảnh runtime mới cho thấy `ă` đã chạm đúng glyph/slot nhưng breve vẫn sai: phần nhìn thấy chủ yếu là dark shadow, dấu sáng chưa đúng và shadow nằm hơi cao. Root cause trong hotfix v1 là dùng `max(palette index)` làm fill, có thể chọn trúng shadow index 7, đồng thời shadow cũ ở row 2 chưa được dọn sạch.

User cũng xác nhận tiếng Nhật vẫn còn nhiều, nên không tiếp tục micro-fix từng vài câu.

# CURRENT — 0.6.13.0 COMPACT JAPANESE REDUCTION BATCH 4

Files:

```text
ACCENT_UPGRADE_0.6.13.0.md
tools/build_gaia_06130_translation_b4.py
tools/00_BUILD_0.6.13.0_TRANSLATION_B4.cmd
translation/COMPACT_TRANSLATION_OVERRIDES_0.6.13.0.csv
translation/DYNAMIC_LITERAL_OVERRIDES_0.6.13.0.csv
```

### Lowercase `ă` hotfix v2

- giữ nguyên code/slot/body production;
- derive bright fill từ histogram nhưng loại shadow index `7`;
- xóa mark cũ ở rows 0/1 và stale shadow ở row 2;
- redraw breve thấp hơn thành shallow cup;
- draw shadow một pixel xuống/phải bằng native shadow palette;
- chỉ patch glyph `ă`.

### Dịch thêm

Batch 4 có **146 compact exact-offset candidates** nhắm vào các row vẫn có nguy cơ rơi về tiếng Nhật vì bản dịch dài không fit field gốc.

Nhóm nội dung:

```text
mua/bán/đất/thuế
nhận card/vũ khí
battle prompts
route/status
special squares
building/symbol effects
item/card descriptions
```

Builder chỉ apply khi byte-fit; quá dài thì skip an toàn.

Dynamic map tăng từ 12 lên **35 literals**, thêm tên vũ khí/card và một số board/location labels để xử lý `%s` hoặc duplicate runtime ngoài offset chính.

Ví dụ:

```text
サンダー -> Sấm
ハリケーン -> Bão
クロスボウ -> Nỏ
ロングソード -> Kiếm
ファイアボール -> Lửa
バトルアックス -> Rìu
サーカス -> Xiếc
呪いの沼 -> Đầm
```

## State

```text
SOURCE READY
PYTHON SYNTAX PASS
CLEAN-ROM BUILD PENDING
RUNTIME PENDING
```

## Next runtime test

Test rộng thay vì micro-test:

1. nhìn `ă` trong `năng`;
2. chơi vài lượt;
3. mở card/item/event/menu;
4. thử đất/thuế/tuyến/battle;
5. chụp các dòng Nhật còn nguyên hoặc `%s` còn tên Nhật.

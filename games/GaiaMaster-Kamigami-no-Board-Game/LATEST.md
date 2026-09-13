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

`0.6.13.0` tiếp tục giảm tiếng Nhật, nhưng screenshot mới xác nhận lowercase `ă` vẫn lỗi hình:

```text
dấu breve cũ chưa được xóa sạch
+ dấu mới bị vẽ chồng lên
= glyph trông hai tầng / quái hình
```

Vì vậy không tiếp tục kiểu xóa vài row rồi vẽ lại.

# CURRENT — 0.6.14.0 TRANSLATION BATCH 5 + FRESH `ă` REBUILD

Files:

```text
ACCENT_UPGRADE_0.6.14.0.md
tools/build_gaia_06140_translation_b5.py
tools/00_BUILD_0.6.14.0_TRANSLATION_B5.cmd
translation/COMPACT_TRANSLATION_OVERRIDES_0.6.14.0.csv
translation/DYNAMIC_LITERAL_OVERRIDES_0.6.14.0.csv
```

### Fix `ă` v3

Bản mới **bỏ toàn bộ bitmap `ă` cũ** sau inner build rồi dựng lại từ CLEAN native lowercase `a`.

Quy trình:

```text
clean native a
 -> compact fresh body
 -> one shallow-U breve
 -> native shadow
 -> replace entire custom ă glyph
```

Do đó không còn khả năng dấu cũ sót dưới dấu mới.

### Dịch thêm

Batch 5 thêm **38 compact exact-offset candidates** cho gameplay/help/status và các chuỗi đầu game, ví dụ:

```text
Thẻ SK
Dừng: SK
Đấu đối thủ
Vô chủ
Quỹ %5d
Phí %4d
Lượt %s
Dừng %s
Đất %s
Thuế TN
Ô thuế đất
Đồng ý?
Có/Không
Chọn thẻ
Dùng %s
```

Builder chỉ apply khi vừa field gốc. Không ép câu dài.

Dynamic literal map cũng bổ sung:

```text
墓地 -> Mộ
大聖堂 -> Đền
通行税 -> Phí
```

## Gate

```text
397 / 397 legacy coverage vẫn bắt buộc
```

## Test tiếp

1. xem chữ `ă` trong `năng` trước: chỉ còn **một** breve;
2. chơi vài lượt, mở card/item/help/menu;
3. chụp các câu Nhật còn sót thành một mẻ để tiếp tục Batch lớn.

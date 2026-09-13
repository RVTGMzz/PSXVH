# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-14**

## Source-of-truth

Production vẫn khóa vào:

```text
native 12x12 / 72-byte / 4bpp
static mapping-only
60-glyph Vietnamese production codepage
font visual style = 0.6.7.2
legacy Alpha coverage gate = 397 / 397
```

Không quay lại narrow 6x12, 12x16, pointer redirect, composite overlay hay global spacing hook.

## Font

`0.6.7.2` = **FONT VISUAL PASS / FREEZE**.

Runtime mới không cho thấy regression font. Các dấu tiếng Việt đã hiện; vấn đề hiện tại là nội dung/fallback/dynamic Japanese literals.

## Coverage

`0.6.9.2` = **397/397 COVERAGE PASS**.

Không được bỏ một fallback đang fit chỉ để ép câu có dấu dài hơn.

## 0.6.10.0 runtime verdict

User đã test `0.6.10.0 HYBRID FULL-COVERAGE + FRONT ACCENT BATCH 1`.

Kết luận:

```text
FRONT ACCENT/FONT RUNTIME PASS
CONTENT QA INCOMPLETE
```

Ảnh runtime phát hiện ba nhóm lỗi:

```text
Người=cờ / Thếgiới=bàncờ
```

ký tự `=` hiện thành glyph Nhật/rác;

```text
Tải dữ liệu VK?
```

khó hiểu, trong đó `VK` = vũ khí;

và gameplay:

```text
DUNG トロル通り
```

cho thấy `DUNG %s` được patch nhưng `%s` lấy tên Nhật từ bảng động khác.

## CURRENT — 0.6.11.0 HYBRID GAMEPLAY ACCENT BATCH 2

Files:

```text
ACCENT_UPGRADE_0.6.11.0.md
tools/build_gaia_06110_hybrid_accent_b2.py
tools/00_BUILD_0.6.11.0_HYBRID_ACCENT_B2.cmd
translation/FRONT_ACCENT_OVERRIDES_0.6.11.0.csv
translation/GAMEPLAY_ACCENT_OVERRIDES_0.6.11.0.csv
translation/DYNAMIC_LITERAL_OVERRIDES_0.6.11.0.csv
```

### Front fixes

```text
Người=cờ        -> Người cờ
Thếgiới=bàncờ   -> Thếgiới bàncờ
Ko chống        -> Không chống
Tải dữ liệu VK? -> Tải KN vũ khí?
```

### Gameplay Batch 2

Có **335 compact accent candidates** cho:

```text
setup / tavern / gameplay / card / item / event / menu / prompt
```

Wrapper chỉ promote candidate nếu byte-size vừa field gốc. Candidate quá dài sẽ giữ fallback cũ.

### Dynamic literal layer

Screenshot-proven first entry:

```text
トロル通り -> Troll
```

Cùng với:

```text
DUNG %s -> Dừng %s
```

expected runtime:

```text
Dừng Troll
```

Equal-length dynamic replacement có thể patch trực tiếp. Replacement ngắn hơn chỉ được dùng với standalone/null-delimited string.

### Builder strategy

`0.6.11.0` bọc exact `0.6.10.0` builder, vì vậy không thay:

```text
font 0.6.7.2
60-glyph codepage
BDP/checksum code
runtime token handling
397/397 legacy gate
```

Builder source đã syntax-check. **Runtime build vẫn pending** vì phiên hiện tại không có clean BIN mounted.

## Next runtime test

Drag CLEAN BIN vào:

```text
tools/00_BUILD_0.6.11.0_HYBRID_ACCENT_B2.cmd
```

Check một lượt:

1. intro không còn glyph rác ở vị trí `=`;
2. setup hiện `Tải KN vũ khí?`;
3. gameplay case cũ hiện `Dừng Troll`;
4. card/menu/item/event/prompt có thêm dấu;
5. chụp lại mọi tên Nhật `%s` hoặc fallback không dấu còn sót.

## Hard rules

- font `0.6.7.2` vẫn FREEZE;
- exact `397/397` vẫn bắt buộc;
- không 12x16;
- không narrow alias;
- không pointer redirect;
- không composite overlay;
- không global cursor/cache/spacing mutation;
- không retest `0.6.9.0` / `0.6.9.1`;
- không hy sinh coverage để ép accent;
- stop ngay nếu freeze/global corruption.

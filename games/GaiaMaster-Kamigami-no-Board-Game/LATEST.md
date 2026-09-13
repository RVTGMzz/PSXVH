# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-14**

## Source-of-truth

Production tiếp tục khóa vào:

```text
native 12x12 / 72-byte / 4bpp
static mapping-only
60-glyph Vietnamese production codepage
legacy Alpha coverage gate = 397 / 397
```

Font hiện được xem là ổn ở runtime. Không retune font thêm nếu chưa có lỗi hình cụ thể mới.

## CURRENT — 0.6.19.0 STORY / DIALOG / MENU / CARD BATCH 10

Trọng tâm hiện tại:

```text
cốt truyện / intro
thoại NPC / tửu quán
menu / prompt
lá bài + mô tả hiệu ứng
vũ khí / phép / item
event / Ma vương / thần linh
các literal Nhật động còn lọt
```

Chiến lược dịch:

1. ưu tiên dịch trực tiếp từ tiếng Nhật gốc;
2. dùng bản Việt tự nhiên có chất trung cổ/fantasy nếu vừa field;
3. nếu quá dài thì rút gọn nhưng giữ nghĩa;
4. giữ nguyên `%s`, `%d`, `%4d`, `%+3d`, `/V`, `/v`;
5. không được phá gate 397/397 chỉ để nhét câu dài hơn.

Văn phong ưu tiên các thuật ngữ như:

```text
lãnh địa
lộ phí
quân quỹ
Thánh địa
Ma vương
Tà thần
Thần Thời
Thần Vận
tỉ thí
chiến lợi
Sứ giả
Pháp sư
Đạo tặc
```

NPC đối đầu có thể dùng `ta / ngươi`; menu hệ thống vẫn phải rõ nghĩa và dễ chơi.

## Intro cleanup

Tiếp tục loại skeleton cũ gây glyph Nhật chèn giữa câu:

```text
NGUOI=CO      -> NGUOI CO
THEGIOI=BANCO -> THEGIOI BANCO
```

Target hiển thị:

```text
Người cờ
Thế giới bàn cờ
```

## Checkpoint repo

```text
checkpoints/0.6.19.0/GaiaMaster_0.6.19.0_BATCH10_STORY_DIALOG_MENU_CARD.zip
```

Checkpoint này chỉ chứa builder/source hỗ trợ test, không chứa game image.

## Runtime gate tiếp theo

`0.6.19.0` hiện là **candidate**, chưa gọi PASS trước khi test.

Ưu tiên chụp lại:

- intro/cốt truyện;
- thoại dài;
- menu giữa trận;
- danh sách + mô tả lá bài;
- mô tả vũ khí/item;
- event Ma vương/thần linh;
- mọi câu còn Nhật hoặc Nhật-Việt lẫn nhau.

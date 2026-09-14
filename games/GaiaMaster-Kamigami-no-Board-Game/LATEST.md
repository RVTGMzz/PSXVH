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

Font hiện được xem là ổn ở runtime. Không retune font nếu chưa có lỗi hình mới.

# CURRENT — 0.6.20.0 STORY / DIALOG / CARD BATCH 11

Trọng tâm hiện tại:

```text
cốt truyện / intro
thoại NPC / tửu quán
menu / prompt
lá bài + mô tả hiệu ứng
vũ khí / phép / item
event / Ma vương / thần linh
dynamic literal Nhật còn lọt
```

Quy mô standalone builder:

```text
story/front mappings  = 19
Japanese semantic map = 262
fantasy fallback map  = 215
dynamic literals      = 75
```

## Chiến lược dịch

Mỗi row ưu tiên:

```text
Japanese exact semantic translation
-> vi_full đã biên tập fantasy
-> compact fantasy
-> established fantasy fallback
-> fallback phục hồi dấu
```

Chỉ promote nếu vừa field gốc. Giữ nguyên `%s`, `%d`, `%4d`, `%+3d`, `/V`, `/v` theo yêu cầu runtime.

## Văn phong

Trung cổ fantasy dễ đọc, không cổ hóa menu kỹ thuật quá mức.

Ưu tiên:

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

NPC đối đầu có thể dùng `ta / ngươi` khi hợp ngữ cảnh.

## Batch 11 mới

Bổ sung direct Japanese-first mapping cho:

- mua/bán/dựng lãnh địa;
- thuế lợi tức, thuế đất, lộ phí, quân quỹ;
- reward/event narrator;
- lời thoại thách đấu, Ma vương và thần linh;
- card help / effect descriptions;
- dynamic nouns như ô chiến, ngã rẽ, Thánh địa, tượng, lộ, địch thủ.

Source data mới trong repo:

```text
translation/BATCH11_JP_EXACT_0.6.20.0.csv
translation/BATCH11_DYNAMIC_LITERALS_0.6.20.0.csv
BATCH11_0.6.20.0.md
```

## Intro cleanup

Tiếp tục loại skeleton cũ từng render thành glyph Nhật:

```text
NGUOI=CO      -> NGUOI CO
THEGIOI=BANCO -> THEGIOI BANCO
```

Target:

```text
Người cờ
Thế giới bàn cờ
```

## Runtime status

`0.6.20.0` là **candidate**, chưa gọi PASS trước khi test game thực tế.

QA tiếp theo:

- intro/cốt truyện;
- thoại dài / tửu quán;
- menu giữa trận;
- card list + card descriptions;
- weapon/item descriptions;
- event Ma vương/thần linh;
- mọi chuỗi còn Nhật hoặc Nhật-Việt lẫn nhau.

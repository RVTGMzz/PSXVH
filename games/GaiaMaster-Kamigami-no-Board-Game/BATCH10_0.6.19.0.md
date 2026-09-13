# Gaia Master 0.6.19.0 — Batch 10

## Mục tiêu

Đợt này chuyển trọng tâm từ sửa font sang **dịch nội dung sâu**:

- cốt truyện / intro;
- thoại tửu quán và NPC;
- menu / prompt;
- tên + mô tả vũ khí, phép, item;
- tên + mô tả lá bài;
- event, thần linh, Ma vương;
- dynamic literal Nhật còn lọt.

## Văn phong

Giọng chung: **trung cổ fantasy dễ đọc**.

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

NPC đối đầu có thể dùng `ta / ngươi`. Menu kỹ thuật giữ rõ nghĩa.

## Pipeline dịch

Mỗi row thử theo thứ tự:

```text
Japanese exact semantic translation
-> existing vi_full đã biên tập fantasy
-> compact fantasy
-> established fallback style
-> fallback có dấu
```

Chỉ promote khi vừa field gốc. Runtime token phải giữ nguyên.

## Intro

Tiếp tục hard-clean skeleton cũ:

```text
NGUOI=CO      -> NGUOI CO
THEGIOI=BANCO -> THEGIOI BANCO
```

Target:

```text
Người cờ
Thế giới bàn cờ
```

## Font / gate

Font giữ nguyên. Không mở lại renderer/font redesign.

```text
legacy coverage = 397/397
```

## Checkpoint

Standalone one-folder builder được lưu tại:

```text
checkpoints/0.6.19.0/GaiaMaster_0.6.19.0_BATCH10_STORY_DIALOG_MENU_CARD.zip
```

Archive không chứa ROM/game image.

## QA kế tiếp

- story/intro;
- NPC/tửu quán;
- menu giữa trận;
- card list + card descriptions;
- weapon/item descriptions;
- Ma vương/event;
- Japanese residuals / mixed strings.

`0.6.19.0` là runtime candidate, chưa phải final PASS.

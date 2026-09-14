# Gaia Master 0.6.20.0 — Batch 11

## Mục tiêu

Batch 11 tiếp tục hướng content-first, tập trung sâu hơn vào:

- cốt truyện / intro;
- thoại NPC và tửu quán;
- gameplay narrator / prompt;
- menu giữa trận;
- tên + mô tả lá bài;
- vũ khí / ma pháp / item;
- event, Ma vương, thần linh;
- dynamic literal Nhật lọt qua `%s` hoặc bảng phụ.

## Quy mô

Standalone builder hiện có:

```text
story/front mappings     = 19
Japanese semantic map    = 262
fantasy fallback map     = 215
dynamic literals         = 75
```

## Chiến lược dịch

Mỗi row ưu tiên theo thứ tự:

```text
Japanese exact semantic translation
-> vi_full đã biên tập fantasy
-> compact fantasy
-> established fantasy fallback
-> fallback phục hồi dấu
```

Chỉ promote khi vừa field gốc và giữ nguyên runtime token.

## Văn phong

Giọng chung: **trung cổ fantasy dễ đọc**.

Ưu tiên các thuật ngữ:

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

NPC đối đầu có thể dùng `ta / ngươi`; menu kỹ thuật vẫn ưu tiên rõ nghĩa.

## Batch 11 bổ sung trực tiếp

Các nhóm Nhật → Việt được mở rộng gồm:

- mua / bán / dựng lãnh địa;
- thuế lợi tức, thuế đất, lộ phí, quân quỹ;
- lời dẫn event và reward;
- lời thoại thách đấu / Ma vương;
- card help và effect descriptions;
- tên bảng phụ như ô chiến, ô thuế, Thánh địa, ngã rẽ;
- dynamic names bên trong `%s`.

Ví dụ:

```text
この土地を買うよ                -> Mua lãnh địa này
通行税%dゼニーはらってね       -> Nộp %d Z lộ phí
プール金取得                    -> Nhận quân quỹ
もう１回行動できるよ！！        -> Thêm 1 lượt!
神さまからのプレゼント！！      -> Thần ban!
何で わしが はらわにゃ ならんのだ！！ -> Sao ta phải nộp!
我が けんぞくよ                 -> Thuộc hạ của ta
退け                             -> Lui!
```

## Intro

Tiếp tục loại separator cũ:

```text
NGUOI=CO      -> NGUOI CO
THEGIOI=BANCO -> THEGIOI BANCO
```

Story/front được biên tập thêm theo tone thần thoại nhưng vẫn giữ câu ngắn để phù hợp field.

## Font / gate

Font giữ nguyên. Không retune nếu chưa có lỗi hình mới.

```text
legacy Alpha coverage gate = 397/397
```

## Runtime status

`0.6.20.0` là runtime candidate, chưa phải PASS cho tới khi test game thực tế.

## Checkpoint

Standalone package:

```text
checkpoints/0.6.20.0/GaiaMaster_0.6.20.0_BATCH11_STORY_DIALOG_CARD.zip
```

Archive không chứa ROM/game image.

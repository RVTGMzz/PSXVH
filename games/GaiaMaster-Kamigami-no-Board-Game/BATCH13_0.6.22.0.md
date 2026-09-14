# Gaia Master 0.6.22.0 — Batch 13

## Deep Event / Menu / Card Sweep

Batch 13 tiếp tục từ `0.6.21.0` với mục tiêu dọn các chuỗi còn mang cảm giác nửa Việt nửa debug, đặc biệt là fragment menu/card bị game chia nhỏ thành nhiều chuỗi runtime.

### Quy mô hiện tại

```text
story/front mappings  = 19
Japanese semantic map = 359
fantasy fallback map  = 284
dynamic literals      = 103
```

### Delta Batch 13

```text
Japanese semantic new/edited = 61
fantasy fallback new/edited  = 58
dynamic literals new/edited  = 24
```

### Trọng tâm

- fragment menu/card bị cắt khúc
- nhãn card nằm trong dấu ngoặc Nhật
- `Giá trị`, `Lộ phí`, `Quỹ`, `Vô chủ`
- chuỗi runtime có `%s`, `%d`, `%4d`, `%+3d`
- tên nhân vật / vũ khí động
- ô GO / ô chiến / ô quán / thuế / Thánh địa
- tiếp tục giọng trung cổ fantasy nhưng menu vẫn rõ nghĩa

Ví dụ:

```text
価値              -> Giá trị
通行税            -> Lộ phí
金斗雲            -> Cân Đẩu Vân
所有者なし        -> Vô chủ
「バトルカード」  -> Thẻ đấu
「ふみたおし」    -> Quỵt nợ
「ルート変更」    -> Đổi lộ
戦闘マスね        -> Ô chiến
酒場マスだよ      -> Ô quán
聖地マスに止まったよ！ -> Ô Thánh địa!
```

Production lock không đổi:

```text
native 12x12 / 72-byte / 4bpp
static mapping-only
legacy Alpha coverage gate = 397/397
```

`0.6.22.0` vẫn là candidate cho tới khi có runtime QA từ bản build trên clean BIN.

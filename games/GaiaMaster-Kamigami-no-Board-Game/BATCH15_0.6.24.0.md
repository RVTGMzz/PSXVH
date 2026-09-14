# Gaia Master 0.6.24.0 — Batch 15

## Deep Dialog / Help / Event sweep

Batch 15 tiếp tục theo hướng Japanese-first, ưu tiên các chuỗi runtime bị chia nhỏ và phần thoại/event sâu còn sót.

### Delta

```text
Japanese semantic map delta = 46
new semantic keys           = 38
semantic re-edits           = 8
fantasy fallback delta      = 45
dynamic literal delta       = 19
```

### Current scale

```text
story/front mappings  = 19
Japanese semantic map = 435
fantasy fallback map  = 354
dynamic literals      = 125
```

### Trọng tâm

- thoại Ma vương / NPC
- bảng cơ sở, chủ sở hữu, lộ phí, giá trị
- các fragment help bị chia nhỏ
- thuế, tiền tích lũy, đổi lộ, mini game
- Đạo tặc / Pháp sư / Đại quốc / Thần Vận
- dynamic literal cho các bảng phụ

Production lock không đổi: native 12x12 / 72-byte / 4bpp, static mapping-only, legacy gate 397/397. Giữ nguyên `%s`, `%d`, `%4d`, `%+3d` và chỉ promote câu khi vừa field gốc.

`0.6.24.0` là candidate, chờ clean-ROM build và runtime QA trước khi gọi PASS.

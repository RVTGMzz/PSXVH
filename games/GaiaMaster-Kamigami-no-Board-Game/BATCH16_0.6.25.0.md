# Gaia Master 0.6.25.0 — Batch 16

## Dynamic Duplicate / Story / Event Sweep

Batch 16 đổi trọng tâm từ chỉ sửa row chính sang **quét duplicate literal an toàn**.

Mục tiêu:
- tận dụng semantic Nhật -> Việt đã biên tập ở các batch trước;
- tự lọc các câu Nhật tự chứa, không có `%` / `/V` runtime token;
- chỉ đưa vào dynamic sweep khi bản Việt ước lượng vừa field gốc;
- bắt các bản sao tiếng Nhật nằm ngoài offset chính / bảng phụ;
- tiếp tục polish story/front và vài câu event/lãnh địa.

Quy mô candidate 0.6.25.0:

```text
story/front mappings  = 19
Japanese semantic map = 436
fantasy fallback map  = 354
dynamic literals      = 226
```

Batch 16 delta:

```text
semantic map delta              = 15
new semantic key                = 1
semantic re-edits               = 10
safe auto-dynamic candidates    = 100
manual dynamic labels           = 11
total dynamic literals after B16= 226
```

Production locks không đổi:

```text
native 12x12 / 72-byte / 4bpp
static mapping-only
legacy Alpha coverage gate = 397/397
```

Tone: fantasy trung cổ dễ đọc. Giữ `%s`, `%d`, `%4d`, `%+3d`. Font không chỉnh thêm.

`0.6.25.0` vẫn là candidate, cần clean-ROM build + runtime QA trước khi gọi PASS.

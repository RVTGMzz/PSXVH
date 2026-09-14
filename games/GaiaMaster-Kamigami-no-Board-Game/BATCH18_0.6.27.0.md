# Gaia Master 0.6.27.0 — Batch 18

## Residual Killer / Consensus Fit

Batch 18 đổi trọng tâm từ mở rộng phạm vi sang ép nốt các câu còn khó lọt vào field PS1.

### Core mới

1. **Consensus translation**
   - Quét cả 6 Translation Master.
   - Nếu cùng một chuỗi Nhật hoặc fallback lặp ở nhiều nơi và tất cả bản đã dịch thống nhất một nghĩa, dùng bản đó cho bản sao còn trống.

2. **Fit V2**
   - semantic chuẩn
   - semantic micro/ultra compact
   - bản dịch đồng thuận
   - `vi_full` fantasy
   - compact / micro / ultra
   - STYLE fallback
   - fallback phục hồi dấu

3. **Whitespace normalization**
   - Bắt các bản sao chỉ khác khoảng trắng/full-width space, ví dụ `   終了ターン` và `終了ターン`.

4. **Báo cáo sau build**
   - `GaiaMaster_0.6.27.0_RESIDUAL_ALPHA.csv`: row Alpha vẫn chưa có bản Việt.
   - `GaiaMaster_0.6.27.0_FIT_PRESSURE.csv`: row có nghĩa Việt nhưng mọi candidate vẫn quá dài, kèm số byte vượt.

### Base trước runtime harvest

```text
story/front mappings  = 19
Japanese semantic map = 437
fantasy fallback map  = 354
dynamic literals      = 229
```

### Delta thủ công Batch 18

```text
semantic delta = 9
STYLE delta    = 9
dynamic delta  = 5
```

Phần tăng coverage chính đến từ consensus + fit engine khi build, vì số row promote thực tế phụ thuộc 6 Translation Master được tải tại thời điểm build.

### Production locks

```text
native 12x12 / 72-byte / 4bpp
static mapping-only
legacy Alpha coverage gate = 397/397
```

Không chỉnh font, renderer hay pointer. Giữ nguyên token `%s`, `%d`, `%4d`, `%+3d`.

`0.6.27.0` hiện là candidate, syntax PASS. Clean-ROM build và runtime QA vẫn cần người dùng test trước khi gọi PASS.

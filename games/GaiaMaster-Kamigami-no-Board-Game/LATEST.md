# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-14**

## CURRENT — 0.6.34.0 BATCH 25

Trọng tâm: **Dependency-Locked Exact Merge / Static Data Closure**.

## Residual Alpha closure

Tập residual lưu từ 0.6.28.0 đã được xử lý hết ở tầng dữ liệu:

```text
147 residual rows
62 unique Japanese strings
147 / 147 exact-fit Vietnamese rows
0 errors
```

Chuỗi xử lý:

```text
Batch 21: semantic coverage toàn bộ 62 Japanese keys
Batch 22: 21 compact pressure rows
Batch 23: 97 compact pressure rows
Batch 24: compile 147 exact file+offset rows
```

## Batch 25 merge

Batch 25 hợp nhất:

```text
Batch 20 exact candidates = 75
Batch 24 residual exact   = 147
Unique candidate keys     = 222
```

Kết quả đã xác nhận:

```text
Runtime-fit protected keys            = 49
Historical rows skipped no-op/unfit   = 13
Already-locked identical              = 13
Protected wording conflicts           = 0
New exact rows exported               = 209
Errors                                = 0
RESULT                                = STATIC PASS
```

Output chính:

`translation/BATCH25_NEW_EXACT_OFFSET_0.6.34.0.csv`

Validation:

`checkpoints/0.6.34.0/BATCH25_MERGE_VALIDATION.txt`

## CI dependency

Batch 25 workflow hiện tự rebuild Batch 24 từ đúng Batch 21/22/23 sources trong cùng checkout trước khi merge. Điều này loại bỏ race giữa source CSV mới và manifest Batch 24 cũ do nhiều workflow bot chạy/push song song.

## Historical locks

0.6.14.1 chỉ được coi là protected lock nếu row thật sự fit field, giữ runtime token và an toàn với frozen codepage. Batch 19 exact locks vẫn được bảo vệ tuyệt đối.

13 candidate đã giống hệt runtime-fit historical locks nên không export lần hai.

Hai wording mới vẫn được giữ vì historical wording tương ứng là no-op/unfit:

```text
Tới %s
Có/Ko
```

## Production architecture

Không đổi:

```text
native 12x12 / 72-byte / 4bpp / LOW nibble first
static mapping-only
frozen 60-glyph Vietnamese codepage
legacy Alpha coverage gate = 397/397
```

Không mở renderer hook, pointer redirect, 12x16, 6x12, composite overlay hay retune font nếu chưa có runtime evidence mới.

## Status

**0.6.34.0 = STATIC PASS / DATA CHECKPOINT.**

Chưa phải Runtime PASS. Chưa được phép gọi bản này runtime-safe cho tới khi exact manifest được tích hợp vào proven production build path, clean-ROM build giữ gate 397/397, và có screenshot/log test thực tế.

## Tiếp theo

1. Tích hợp `BATCH25_NEW_EXACT_OFFSET_0.6.34.0.csv` làm exact wording layer cuối trong production build path.
2. Giữ nguyên proven historical locks và gate 397/397.
3. Không để global/style/fallback promotion cũ ghi đè Batch 25.
4. Clean-ROM build.
5. Runtime QA bằng screenshot/log.
6. Chỉ mở lại font khi runtime thật sự chứng minh lỗi glyph.

# Gaia Master 0.6.26.0 — Batch 17

## Japanese Extermination

Batch 17 chuyển từ mở rộng mapping thủ công sang **quét sạch residual** trong toàn bộ Translation Master.

### Điểm mới

- Quét cả 6 `TRANSLATION_MASTER_0.6_part*.csv` lúc build.
- Thu hoạch các `vi_full` đã có nhưng chưa nằm trong semantic map.
- Với row `IN_ALPHA_05` còn trống, thử lần lượt:
  1. Japanese semantic map
  2. `vi_full`
  3. compact fantasy
  4. STYLE fallback
  5. phục hồi dấu từ fallback cũ
- Chỉ promote khi giữ đúng runtime token và bản Việt vừa field gốc.
- Các câu Nhật tự chứa, không có `%` hoặc `/V`, đủ an toàn sẽ được đẩy sang dynamic literal để bắt duplicate ngoài offset chính.
- Sinh `GaiaMaster_0.6.26.0_RESIDUAL_ALPHA.csv` sau harvest để biết chính xác row Alpha nào còn chưa xử được.

### Base trước runtime harvest

```text
story/front mappings  = 19
Japanese semantic map = 436
fantasy fallback map  = 354
dynamic literals      = 229
```

Batch 17 manual polish:

```text
21 semantic mappings
21 fantasy fallback mappings
13 dynamic literals
```

Số semantic/dynamic harvest thực tế được in trong CMD khi user build trên clean ROM.

### Production lock

```text
native 12x12 / 72-byte / 4bpp
static mapping-only
legacy Alpha coverage gate = 397/397
```

Không chỉnh font. Giữ nguyên `%s`, `%d`, `%4d`, `%+3d` và runtime token. Intro separator cleanup vẫn bắt buộc.

`0.6.26.0` là candidate, chưa gọi runtime PASS cho tới khi có test thực tế.

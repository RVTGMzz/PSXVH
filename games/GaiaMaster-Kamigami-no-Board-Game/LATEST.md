# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-12 sau runtime test 0.6.3.3 EOL OVERWRITE TEST**.

## Chốt hiện tại

- 0.6.2.x: custom Vietnamese glyph pipeline đã PASS.
- Native 12x12 bị loại cho production stacked Vietnamese diacritics vì quá chật.
- 0.6.3.0 12x16 = **STRUCTURAL PASS**.
- 0.6.3.1 BASELINE + 16-ROW STRIDE = **UNSAFE FAIL**: global text corruption + freeze. Không retest.
- 0.6.3.2 BASELINE ONLY = **STABLE PASS**, nhưng đáy glyph extended bị mất/cắt.
- 0.6.3.3 EOL OVERWRITE TEST = **SAME RESULT AS 0.6.3.2**.

## 0.6.3.3 runtime result

Control:

```text
ＴＥＳＴ亜
```

Target `亜` nằm cuối dòng, không có glyph phía sau.

Runtime user screenshot vẫn cho kết quả gần như 0.6.3.2:

- Japanese header bình thường;
- `ＴＥＳＴ` bình thường;
- extended target/baseline vẫn ổn định;
- không global corruption/freeze;
- **phần dưới của extended glyph vẫn mất/cắt**.

=> Giả thuyết “glyph kế tiếp ghi đè 4 hàng cuối” bị **DISPROVEN**.

Không cần retest 0.6.3.3.

## Reverse mới sau 0.6.3.3

Wide-glyph unpack/copy function thật sự là:

```text
0x8003C67C
```

Target metadata height 15 => loop xử lý 16 rows.

Wide path mỗi source row:

```text
6 source bytes -> 8 converted/cache bytes
```

Native:

```text
12 rows -> 96 converted bytes
```

Extended:

```text
16 rows -> 128 converted bytes
```

Quan trọng hơn, đã tìm được **VRAM upload queue**:

```text
0x8003CDE8..0x8003CE24
```

Nó tạo RECT trên stack rồi gọi:

```text
0x800406F8
```

với:

```text
RECT.x = state + 48
RECT.y = state + 40
RECT.w = 4
RECT.h = (state + 42) - (state + 40) + 1
source = state + 96
```

`0x800406F8` chỉ queue `(RECT + RAM source pointer)` cho VRAM upload.

Điều này cho thấy pipeline phải phân biệt rõ 3 tầng:

1. 96-byte 12x16 source glyph;
2. 128-byte converted/cache glyph;
3. VRAM upload rectangle + sprite texture UV/window.

## CURRENT — 0.6.3.4 UV WINDOW TEST

0.6.3.4 giữ nguyên stable 0.6.3.3 path và chỉ thay **một biến**:

```text
target texture V += 4 px
```

Hook diagnostic tại:

```text
0x8003CCF0
```

Native `subu v0,v0,v1` tại `0x8003CCF4` vẫn chạy trong jump delay slot, nên cave nhận đúng native texture-V trước khi target-specific `+4`.

Không đụng:

```text
0x8003CD94..0x8003CDB4
```

Không thay cache allocator/shared cursor.
Target vẫn ở cuối dòng.

### Câu hỏi của probe

Nếu 4 hàng dưới đã tồn tại trong VRAM nhưng visible texture window lấy sai vùng, `V + 4` phải làm phần dưới E xuất hiện, đồng thời top accents dịch/mất.

Interpretation:

- **lower rows xuất hiện** => 16 rows đã vào VRAM; bug nằm ở UV/window/draw sampling.
- **lower rows vẫn mất/blank/garbage** => truncation xảy ra trước texture sampling, khả năng ở converted cache hoặc VRAM upload content/rectangle.

Package local:

```text
GaiaMaster_FontIsolation_0.6.3.4_UV_WINDOW_TEST.zip
```

## Do not repeat

- Không quay lại Krom path.
- Không polish stacked accents trong native 12x12.
- Không retest 0.6.2.18, 0.6.3.0, 0.6.3.1, 0.6.3.2 hoặc 0.6.3.3 trừ khi có lý do reverse mới rất cụ thể.
- Không patch shared `CD94` cache cursor kiểu 0.6.3.1.

## Sau khi extended-height path ổn định

1. production-safe Vietnamese extended atlas/cache storage;
2. full Vietnamese glyph inventory;
3. compact runtime codepage/mapping;
4. encode `vi_full` có dấu;
5. solve/repack 230 pending rows;
6. clean mixed JP/VI;
7. graphic menu/title patch;
8. full runtime QA + reproducible build.

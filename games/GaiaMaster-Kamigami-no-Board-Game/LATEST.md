# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-12 sau runtime test 0.6.3.4 UV WINDOW TEST**.

## Chốt hiện tại

- 0.6.2.x: custom Vietnamese glyph pipeline đã PASS.
- Native 12x12 bị loại cho production stacked Vietnamese diacritics vì quá chật.
- 0.6.3.0 12x16 = **STRUCTURAL PASS**.
- 0.6.3.1 shared cache-stride rewrite = **UNSAFE FAIL**: global text corruption + freeze. Không retest.
- 0.6.3.2 BASELINE ONLY = **STABLE PASS**, nhưng phần đáy target extended mất/cắt.
- 0.6.3.3 EOL OVERWRITE = **same result**, loại giả thuyết glyph kế tiếp overwrite.
- 0.6.3.4 UV WINDOW TEST = **negative diagnostic**, `V+4` không phục hồi đáy E một cách đúng/clean.

## Font path đã chứng minh

```text
atlas file   = SLPS + 0x5C4EC
mapping file = SLPS + 0x6B6CC
atlas RAM    = 0x8006BCEC
mapping RAM  = 0x8007AECC
860 glyphs
native 12x12 / 72-byte / 4bpp / LOW nibble first
```

Confirmed:

```text
0x8273 Ｔ -> glyph 481
0x8264 Ｅ -> glyph 466
0x8272 Ｓ -> glyph 480
0x889F 亜 -> glyph 0
```

## Extended-height reverse mới

Wide custom copy routine:

```text
0x8003C67C
```

Geometry:

```text
6 source bytes/row -> 8 converted/cache bytes/row
12 rows -> 96 converted bytes
16 rows -> 128 converted bytes
```

Metadata `height=15` làm loop xử lý 16 rows.

### VRAM upload page không bị khóa 12 rows

Font-cache initialization quanh:

```text
0x8003D488..0x8003D5F4
```

mặc định dùng cache page cao khoảng:

```text
240 rows
```

Final flush quanh:

```text
0x8003DB78..0x8003DBE0
```

queue RECT cho cả cache page, không phải một RECT glyph 12-row.

=> Không còn nghi upload `RECT.h` đơn giản bị hardcode 12.

## 0.6.3.4 runtime result

Control:

```text
ＴＥＳＴ亜
```

Giữ 16-row source/copy/sprite + baseline Y -4, chỉ đổi:

```text
target texture V += 4
```

Runtime:

- Japanese header bình thường;
- `ＴＥＳＴ` bình thường;
- target vẫn malformed/truncated;
- lower native E không trở lại sạch/đúng;
- không global corruption/freeze.

=> simple UV/window offset không giải thích lower-row loss.
=> không retest 0.6.3.4.

## CURRENT — 0.6.3.5 POST-COPY RAM SENTINEL

Mục tiêu: test trực tiếp converted RAM rows 10..15 sau `0x8003C67C`.

Hook sạch sau copy tại:

```text
0x8003CC4C
```

Target `0x889F` only:

```text
rows 10..11 = full palette-index-7 band  # control
rows 12..15 = full palette-index-1 band  # bright test
```

Interpretation:

- thấy cả 2-row control + 4-row bright bottom => rows 12..15 survive RAM->VRAM->sprite;
- chỉ thấy control rows10..11 => loss/clipping xảy ra sau converted RAM row11;
- không thấy cả hai => sentinel hook/target path chưa chạy đúng, không suy luận clipping.

Package:

```text
GaiaMaster_FontIsolation_0.6.3.5_POST_COPY_RAM_SENTINEL.zip
```

## Do not repeat

- Không quay lại Krom path.
- Không polish stacked accents production trong 12x12.
- Không retest 0.6.2.18, 0.6.3.0, 0.6.3.1, 0.6.3.2, 0.6.3.3 hoặc 0.6.3.4.
- Không patch shared `0x8003CD94..0x8003CDB4` theo kiểu 0.6.3.1.

## Sau khi extended-height path ổn định

1. production-safe Vietnamese extended atlas/cache storage;
2. full Vietnamese glyph inventory;
3. compact runtime codepage/mapping;
4. encode `vi_full` có dấu;
5. solve/repack 230 pending rows;
6. clean mixed JP/VI;
7. graphic menu/title patch;
8. full runtime QA + reproducible build.

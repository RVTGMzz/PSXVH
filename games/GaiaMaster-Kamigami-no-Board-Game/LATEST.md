# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-12 sau runtime 0.6.3.9 HEIGHT FROM METADATA**.

## Chốt hiện tại

- 0.6.2.x: custom Vietnamese glyph pipeline PASS.
- Native 12x12 bị loại cho production stacked Vietnamese diacritics.
- 0.6.3.0 12x16 = structural evidence useful, nhưng các kết luận về visible-height phải được xem lại sau các probe mới.
- 0.6.3.1 = UNSAFE FAIL, global text corruption + freeze.
- 0.6.3.2 = stable, baseline tốt hơn nhưng lower rows mất/cắt.
- 0.6.3.3 = loại giả thuyết following-glyph overwrite.
- 0.6.3.4 = UV+4 negative.
- 0.6.3.5 = post-copy sentinel không quan sát được vì late `s0` unreliable.
- 0.6.3.6 = UNSAFE FAIL, repeatable freeze ngay sau Sony logo.
- 0.6.3.7 SOURCE ROW SENTINEL = runtime complete; rows10..11 hiện, rows12..15 không hiện đủ.
- 0.6.3.8 FORCE SPRITE HEIGHT16 = diagnostic fail, phá layout toàn cục.
- **0.6.3.9 HEIGHT FROM METADATA = diagnostic fail.**

## 0.6.3.9 runtime result

Probe thay load tại `0x8003CCC0` bằng:

```text
lhu v0,2(s3)
```

với giả thuyết `s3+2` tại stage này vẫn là per-glyph `height_minus_1`.

Runtime screenshot:

- `TEST` bị xếp dọc thành cột;
- target trở thành block/texture nhiễu;
- layout text vẫn bị phá tương tự hướng force-height;
- không thu được thick white rows12..15 theo mong đợi.

=> **Giả thuyết `s3+2` ở `0x8003CCC0` là current glyph metadata height bị loại.**
=> `s3` ở stage này không được phép xem là metadata pointer của `0x8003C210` nếu chưa chứng minh register lifetime.
=> Không build 0.6.3.10 từ suy đoán này.

## Kết luận quan trọng từ 0.6.3.7..0.6.3.9

0.6.3.7 là probe sạch nhất về lower rows vì sentinel được bake trực tiếp vào source 12x16:

```text
rows10..11 = dark/gray full band
rows12..15 = bright white full band
```

Runtime chỉ hiện rõ rows10..11, không hiện đủ khối trắng rows12..15.

0.6.3.8 và 0.6.3.9 chứng minh rằng block quanh `0x8003CCC0` **không thể được sửa bằng cách coi nó là một visible-height field đơn giản**. Cả global force16 lẫn đọc `s3+2` đều làm layout text chuyển thành vertical/blank behavior.

## CURRENT ACTION — REVERSE ONLY, NO USER PROBE YET

Không gửi thêm build ngay.

Reverse chính xác:

```text
0x8003CCA0 .. 0x8003CD20
```

Mục tiêu:

1. trace lifetime của `s1/s2/s3` từ caller tới block này;
2. xác định `lbu 64(s1)` tại `0x8003CCC0` thực sự đại diện cho gì;
3. xác định các store sau `0x8003CCC8` đi vào descriptor/primitive field nào;
4. phân biệt visible texture height, glyph advance, line/layout metric và cache geometry;
5. chỉ build probe mới sau khi có một field/consumer được chứng minh bằng disassembly/dataflow.

## Do not repeat

- không quay lại Krom;
- không polish production stacked accents trong 12x12;
- không retest 0.6.2.18;
- không retest 0.6.3.0..0.6.3.9;
- không patch shared `0x8003CD94..0x8003CDB4` kiểu 0.6.3.1;
- không persistent/global FLAG kiểu 0.6.3.6;
- không force height16 global kiểu 0.6.3.8;
- không dùng `s3+2` tại `0x8003CCC0` như height metadata nếu chưa chứng minh register lifetime.

## Sau khi extended-height path ổn định

1. production-safe Vietnamese extended atlas/cache storage;
2. full Vietnamese glyph inventory;
3. compact runtime codepage/mapping;
4. encode `vi_full` có dấu;
5. solve/repack 230 pending rows;
6. clean mixed JP/VI;
7. graphic menu/title patch;
8. full runtime QA + reproducible build.

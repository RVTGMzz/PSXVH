# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-12 sau runtime 0.6.3.8; current probe = 0.6.3.9 HEIGHT FROM METADATA**.

## Chốt hiện tại

- 0.6.2.x: custom Vietnamese glyph pipeline PASS.
- Native 12x12 bị loại cho production stacked Vietnamese diacritics.
- 0.6.3.0 12x16 = **STRUCTURAL PASS**.
- 0.6.3.1 = **UNSAFE FAIL**, global text corruption + freeze.
- 0.6.3.2 = stable, baseline tốt hơn nhưng lower rows mất/cắt.
- 0.6.3.3 = loại giả thuyết following-glyph overwrite.
- 0.6.3.4 = UV+4 negative.
- 0.6.3.5 = post-copy sentinel không quan sát được vì late `s0` unreliable.
- 0.6.3.6 = **UNSAFE FAIL**, freeze ngay sau Sony logo. Không retest.
- 0.6.3.7 SOURCE ROW SENTINEL = **RUNTIME COMPLETE**.
- 0.6.3.8 FORCE SPRITE HEIGHT16 = **DIAGNOSTIC FAIL** vì ép height toàn cục phá layout text.

## 0.6.3.7 runtime result

Sentinel được bake trực tiếp vào source glyph 12x16:

```text
rows 10..11 = dark/gray full band
rows 12..15 = bright white full band
```

Runtime screenshot:

- Japanese header/TEST ổn;
- dải tối rows 10..11 hiện rõ;
- rows 12..15 không hiện thành khối trắng 4 hàng, chỉ còn mép sáng rất mỏng.

=> source 12x16 được đọc tới vùng đáy, nhưng 4 hàng cuối không được hiển thị đầy đủ.
=> đây không còn là lỗi late flag/hook vì sentinel nằm trực tiếp trong source.

## 0.6.3.8 runtime result

0.6.3.8 ép visible sprite height=16 cho mọi glyph tại `0x8003CCC0`.

Runtime:

- textbox có thể trống;
- `TEST` bị xếp dọc;
- layout text bị phá toàn cục.

=> global force-height16 không hợp lệ.
=> hook sprite-height ảnh hưởng layout/primitive nhiều hơn một window đơn giản.
=> không retest 0.6.3.8.

## Current hypothesis

Ở metadata stage, mỗi glyph đã có per-glyph height tại:

```text
metadata +2 = height_minus_1
native = 11
extended target = 15
```

Late sprite-height path hiện dùng global/native value `lbu v0,64(s1)` và các probe target-specific trước đây dựa vào late `s0`, vốn không đáng tin.

## CURRENT — 0.6.3.9 HEIGHT FROM METADATA

0.6.3.9 giữ source sentinel của 0.6.3.7 và thay sprite-height source bằng:

```text
lhu v0,2(s3)   # current glyph metadata height_minus_1
```

sau đó để native `0x8003CCC8 addiu v0,v0,1` chạy tiếp.

Expected:

```text
native glyphs: 11+1 = 12 px
extended target: 15+1 = 16 px
```

Không dùng:

- late `s0` target check cho sprite height;
- global force-height16;
- persistent flag;
- post-copy hook;
- shared CD94 allocator rewrite;
- UV diagnostic.

Câu hỏi runtime duy nhất:

> TEST/native có trở lại layout bình thường và target có hiện đủ khối trắng rows 12..15 hay không?

Package local:

```text
GaiaMaster_FontIsolation_0.6.3.9_HEIGHT_FROM_METADATA.zip
```

Launcher:

```text
00_RUN_PROBE_0639.cmd
```

## Do not repeat

- không quay lại Krom;
- không polish production stacked accents trong 12x12;
- không retest 0.6.2.18;
- không retest 0.6.3.0..0.6.3.8;
- không patch shared `0x8003CD94..0x8003CDB4` kiểu 0.6.3.1;
- không persistent/global FLAG kiểu 0.6.3.6;
- không force height16 global kiểu 0.6.3.8.

## Sau khi extended-height path ổn định

1. production-safe Vietnamese extended atlas/cache storage;
2. full Vietnamese glyph inventory;
3. compact runtime codepage/mapping;
4. encode `vi_full` có dấu;
5. solve/repack 230 pending rows;
6. clean mixed JP/VI;
7. graphic menu/title patch;
8. full runtime QA + reproducible build.

# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-12 sau runtime test 0.6.2.18 CLEAN ACCENT**, next là **0.6.2.19 VARIANT GRID**.

## Chốt kỹ thuật

- BDP checksum reverse + verify 60/60 nested + top-level.
- MODE2/Form1 patcher + EDC/ECC ổn định.
- Full-width Latin CP932/Shift-JIS: OK.
- ASCII 1-byte: FAIL/mis-render, không dùng.
- Alpha 0.6.1 FRONT là baseline runtime ổn định: 397 patch, SHA1 `54d2fb026bc3b71c79861e723caffb4114caa34c`.
- Translation master: 596 vị trí; 230 dòng pending vì full-width 2-byte overflow slot.

## Character Select / custom font

Visible probe:

```text
PRGPACK.BDP + 0xBFD2C
owner nested BDP: entry 29
local offset: +0x580
```

Custom font:

```text
atlas static:    SLPS + 0x5C4EC
mapping static:  SLPS + 0x6B6CC
atlas RAM:       0x8006BCEC
mapping RAM:     0x8007AECC
860 glyphs
72 bytes/glyph
12x12 pixels
4bpp
LOW nibble first
```

Mapping confirmed:

```text
0x8273 Ｔ -> glyph 481
0x8264 Ｅ -> glyph 466
0x8272 Ｓ -> glyph 480
0x889F 亜 -> glyph 0
```

## Font probe timeline

### 0.6.2.13 — BREAKTHROUGH PASS
No hook/code cave. Static atlas glyph replacement works at runtime. Text khác bình thường, glyph cuối gần `Ế`.

=> **Vietnamese glyph pipeline PASS.**

### 0.6.2.14 / 0.6.2.15
Compact-body strategy rejected vì accented capitals nhìn nhỏ hơn native capitals.

### 0.6.2.16 FULL HEIGHT
Giữ body `Ｅ` rows 2..11 byte-for-byte; dấu chỉ dùng rows 0..1. Runtime body size/baseline đúng, nhưng circumflex chưa đọc tự nhiên.

### 0.6.2.17 FULL HEIGHT AA ACCENT
Accent geometry gần hơn nhưng phần mũ + sắc bị loang/shadow tối, user thấy phần cần sáng chưa rõ.

### 0.6.2.18 CLEAN ACCENT — runtime result
Bỏ dark AA/shadow ở dấu, chỉ dùng bright strokes. Runtime vẫn chưa đạt thẩm mỹ: glyph nhìn gần `Ế` nhưng circumflex/acute vẫn chưa đủ tự nhiên và sạch.

=> Không test tiếp kiểu một ROM / một tweak.

## NEXT — 0.6.2.19 VARIANT GRID

Một ROM sẽ hiển thị **6 mẫu `Ế` full-height cùng lúc**, từ trái sang phải = mẫu 1..6.

Implementation diagnostic:

- giữ native `Ｅ` body rows 2..11 byte-for-byte ở cả 6 mẫu;
- chỉ thay rows 0..1;
- tạm map 6 SJIS codes hợp lệ `889F,88A0,88A1,88A2,88A3,88A5` tới atlas slots `850..855`;
- Character Select probe = full-width `ＴＥＳＴ` + 6 glyph variants;
- không renderer hook / không Krom hook / không code cave.

6 mẫu:

1. clean compact
2. narrow / less clutter
3. wide circumflex
4. light native-edge shading
5. minimal sparse
6. left-shifted circumflex

User chỉ cần chọn mẫu đẹp nhất từ trái sang phải. Sau đó khóa style đó cho full Vietnamese glyph family.

## Sau khi chọn geometry

1. build full Vietnamese glyph inventory;
2. thiết kế compact runtime codepage/mapping;
3. encode `vi_full` có dấu;
4. giải 230 pending overflow rows;
5. dọn mixed JP/VI;
6. patch graphic text menus/title;
7. full runtime QA + reproducible final build.

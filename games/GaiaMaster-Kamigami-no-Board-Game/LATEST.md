# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-12 sau Font Isolation 0.6.2.14**, đang test **0.6.2.15 ACCENT SHAPE**.

## Chốt kỹ thuật

- Checksum BDP đã reverse và verify 60/60 nested + top-level.
- Raw MODE2/Form1 EDC/ECC patch ổn định.
- Full-width Latin CP932/Shift-JIS hiển thị đúng.
- ASCII 1-byte hiển thị sai và **không dùng**.
- Alpha 0.6.1 FRONT là baseline runtime ổn định: **397 patch**, output SHA1 `54d2fb026bc3b71c79861e723caffb4114caa34c`.
- Translation master: 596 vị trí; 230 dòng pending vì full-width 2-byte vượt slot.

## Character Select / custom font — breakthrough

Visible probe:

```text
PRGPACK.BDP + 0xBFD2C
owner nested BDP: entry 29
local offset: +0x580
```

Stage 2 reverse đã tìm được custom font thật trong `SLPS_020.75`:

```text
atlas static:   SLPS + 0x5C4EC
mapping static: SLPS + 0x6B6CC
atlas RAM:      0x8006BCEC
mapping RAM:    0x8007AECC
860 glyphs
72 bytes/glyph
12x12 pixels
4bpp
LOW nibble first
```

Mapping xác nhận:

```text
0x8273 Ｔ -> glyph 481
0x8264 Ｅ -> glyph 466
0x8272 Ｓ -> glyph 480
0x889F 亜 -> glyph 0
```

## Probe timeline quan trọng

### 0.6.2.13 — BREAKTHROUGH PASS
Bỏ toàn bộ renderer hook/code cave. Giữ control full-width:

```text
ＴＥＳＴ亜
```

và thay trực tiếp **static atlas glyph #0** bằng glyph dựng từ `Ｅ` gốc.

Runtime: glyph cuối đã hiện gần như `Ế`, màu/style gần font gốc, text khác bình thường.

=> **Vietnamese glyph pipeline đã PASS.**

### 0.6.2.14 — result
Thử chừa headroom và nén thân E, nhưng screenshot vẫn nhìn gần như `É`.

Phân tích lại cho thấy nguyên nhân chính không phải clipping: circumflex chỉ cao một row nên nhập vào top bar của E sau khi game render/scale.

=> blocker còn lại là **shape của dấu mũ**, không phải renderer/mapping/atlas.

## NEXT — Font Isolation 0.6.2.15 ACCENT SHAPE

Không hook renderer nữa. Giữ static-slot strategy đã pass.

Layout mới:

```text
row 0 = dấu sắc
row 1 = đỉnh mũ
row 2 = hai vai mũ
row 3..11 = thân E native compact 9 hàng
```

Mũ có 2 tầng thật sự để thành hình `^`, tách khỏi top bar.

Expected Character Select:

```text
ＴＥＳＴẾ
```

Sau khi pass:

1. tạo full Vietnamese glyph inventory;
2. thiết kế codepage/runtime mapping không phá text Nhật chưa dịch;
3. encode `vi_full` có dấu;
4. xử lý 230 dòng overflow/repack;
5. dọn mixed JP/VI;
6. patch graphic text menus;
7. QA full game + build reproducible patch package.

Chi tiết reverse nằm trong `CHARACTER_SELECT_FONT_REVERSE_0.1.md` và `HANDOFF_CURRENT.md`.

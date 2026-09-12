# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-12 sau runtime test 0.6.2.16 FULL HEIGHT**.

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

Custom font trong `SLPS_020.75`:

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
Bỏ toàn bộ renderer hook/code cave. Giữ control full-width `ＴＥＳＴ亜` và thay trực tiếp static atlas glyph #0 bằng glyph dựng từ `Ｅ` gốc.

Runtime: glyph cuối hiện gần như `Ế`, màu/style gần font gốc, text khác bình thường.

=> **Vietnamese glyph pipeline đã PASS.**

### 0.6.2.14 / 0.6.2.15 — compact-body strategy rejected
Nén thân E để lấy thêm headroom cho dấu làm chữ có dấu nhỏ hơn chữ thường. Runtime feedback xác nhận không phù hợp production.

=> Không dùng chiến lược thu nhỏ thân chữ.

### 0.6.2.16 FULL HEIGHT — runtime result
Giữ `Ｅ` native nguyên kích thước, row 2..11 byte-for-byte. Nhét circumflex + acute vào đúng hai hàng trống row 0..1.

Runtime:

- thân `Ｅ` đúng kích thước, baseline/style đúng;
- dấu trên hiện được nhiều hơn;
- glyph vẫn chưa đọc tự nhiên thành `Ế`, trông gần `É` với các điểm/nhánh dấu chưa rõ.

=> **Full-height strategy là hướng đúng.** Blocker hiện tại chỉ còn **2-row accent geometry**, không còn là renderer/mapping/size.

## NEXT — 0.6.2.17 FULL HEIGHT AA ACCENT

Giữ nguyên body `Ｅ` 100%.

Chỉ thay hai hàng dấu bằng thiết kế pixel-font rõ hơn:

- circumflex peak dùng bright native index;
- circumflex shoulders dùng darker native anti-alias/shadow indices để không nhập vào top bar `E`;
- acute đặt tách bên phải, cũng dùng 2 mức sáng/tối;
- body rows 2..11 giữ nguyên byte-for-byte.

Mục tiêu runtime:

```text
ＴＥＳＴẾ
```

với thân chữ bằng đúng `Ｅ` gốc và dấu `^ + ´` đọc được rõ trong 2 hàng headroom.

Sau khi geometry đạt yêu cầu:

1. khóa template full-height cho nhóm nguyên âm có dấu;
2. tạo full Vietnamese glyph inventory;
3. thiết kế compact codepage/runtime mapping không phá text Nhật chưa dịch;
4. encode `vi_full` có dấu;
5. xử lý 230 dòng overflow/repack;
6. dọn mixed JP/VI;
7. patch graphic text menus;
8. QA full game + build reproducible patch package.

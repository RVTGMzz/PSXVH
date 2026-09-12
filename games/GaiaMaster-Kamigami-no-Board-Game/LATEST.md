# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-12 sau Font Isolation 0.6.2.15**, đang test **0.6.2.16 FULL HEIGHT**.

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

### 0.6.2.14 — COMPACT FIT
Nén thân E còn 9 hàng để lấy thêm headroom. Runtime vẫn trông gần như `É`.

### 0.6.2.15 — ACCENT SHAPE — runtime result
Dùng 3 hàng cho dấu: sắc / đỉnh mũ / vai mũ và giữ thân E compact 9 hàng.

Runtime screenshot cho thấy phần dấu trên hiện rõ hơn, nhưng glyph vẫn chưa giống `Ế` tự nhiên. Quan trọng hơn, user xác nhận hướng **nén thân chữ làm chữ có dấu trông nhỏ hơn chữ thường**, không chấp nhận cho bản hoàn thiện.

=> **Reject compact-body strategy cho production.**

## NEXT — Font Isolation 0.6.2.16 FULL HEIGHT

Production rule mới:

> Chữ có dấu phải giữ nguyên kích thước thân chữ native. Không được làm `Ă/Â/Ê/Ô/Ơ/Ư...` thấp hoặc nhỏ hơn chữ thường chỉ để nhường chỗ cho dấu.

`Ｅ` native đã có sẵn hai hàng trống ở trên:

```text
row 0 = blank
row 1 = blank
row 2..11 = native E body
```

0.6.2.16 giữ **row 2..11 byte-for-byte**, và nhét cả circumflex + acute vào đúng hai hàng trống:

```text
row 0 = circumflex peak + acute upper pixel
row 1 = circumflex shoulders + acute lower pixel
row 2..11 = E native nguyên kích thước
```

Không hook renderer, không Krom hook, không code cave. Vẫn dùng static-slot strategy đã PASS.

Expected Character Select:

```text
ＴＥＳＴẾ
```

Mục tiêu của 0.6.2.16 không chỉ là "có dấu", mà là **`Ế` phải cao/thân chữ bằng đúng `Ｅ` native**.

Sau khi glyph geometry đạt yêu cầu:

1. khóa template full-height cho nhóm nguyên âm có dấu;
2. tạo full Vietnamese glyph inventory;
3. thiết kế compact codepage/runtime mapping không phá text Nhật chưa dịch;
4. encode `vi_full` có dấu;
5. xử lý 230 dòng overflow/repack;
6. dọn mixed JP/VI;
7. patch graphic text menus;
8. QA full game + build reproducible patch package.

Chi tiết reverse nằm trong `CHARACTER_SELECT_FONT_REVERSE_0.1.md` và `HANDOFF_CURRENT.md`.

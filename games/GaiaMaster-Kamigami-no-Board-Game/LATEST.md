# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-12 sau Font Isolation 0.6.2.13**.

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

Krom2RawAdd đã bị loại cho Character Select sau C2/D2/E2.

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

### 0.6.2.7
Thay glyph index 0 nhưng control dùng ASCII `TEST亜` -> runtime hiện nhiều glyph `É`. Kết luận: atlas injection có tác động runtime nhưng ASCII control không hợp lệ.

### 0.6.2.10
Hook quá sớm trong mapping pipeline -> toàn bộ text bị collapse thành cùng một glyph. Strategy bị loại.

### 0.6.2.11
Post-lookup hook cô lập được ký tự cuối:

```text
ＴＥＳＴ?
```

=> mapping isolation PASS, nhưng custom cave glyph không phải đường tối ưu để finalize.

### 0.6.2.13 — BREAKTHROUGH
Bỏ toàn bộ renderer hook/code cave. Giữ control full-width:

```text
ＴＥＳＴ亜
```

và thay trực tiếp **static atlas glyph #0** bằng glyph dựng từ `Ｅ` gốc.

Runtime user result: glyph cuối đã hiện **gần như `Ế`**, màu/style khớp tốt hơn, text khác bình thường. Vấn đề còn lại chỉ là **dấu phía trên bị clip/cắt**.

Kết luận:

> **Vietnamese glyph pipeline đã PASS.** Character Select render được glyph custom từ static atlas gốc. Blocker hiện tại không còn là renderer/mapping, mà là fit glyph Việt vào ô 12x12.

## NEXT — Font Isolation 0.6.2.14

Không hook renderer nữa.

Mục tiêu 0.6.2.14:

1. tiếp tục static-slot strategy từ 0.6.2.13;
2. giữ row 0 trống để tránh top clipping;
3. đặt dấu sắc + mũ thấp hơn trong glyph;
4. nén thân `Ｅ` gốc theo chiều dọc đủ để chừa headroom nhưng giữ palette/style native;
5. expected Character Select: `ＴＥＳＴẾ` đầy đủ, không cắt dấu.

Sau khi 0.6.2.14 pass:

1. tạo full Vietnamese glyph inventory;
2. thiết kế codepage/runtime mapping không phá text Nhật chưa dịch;
3. encode `vi_full` có dấu;
4. xử lý 230 dòng overflow/repack;
5. dọn mixed JP/VI;
6. patch graphic text menus;
7. QA full game + build reproducible patch package.

Chi tiết reverse nằm trong `CHARACTER_SELECT_FONT_REVERSE_0.1.md`, `FONT_ISOLATION_0.6.2x.md`, và `HANDOFF_CURRENT.md`.

# Gaia Master — Font Isolation 0.6.2.16 FULL HEIGHT

## Vì sao bỏ hướng compact body

0.6.2.15 làm dấu rõ hơn 0.6.2.14, nhưng user xác nhận glyph có dấu trông nhỏ/thấp hơn chữ thường vì thân `Ｅ` bị nén từ 10 hàng xuống 9 hàng.

Điều này không chấp nhận cho bản production: nếu áp dụng cho `Ă Â Ê Ô Ơ Ư...`, toàn bộ chữ có dấu sẽ thấp hơn chữ Latin native và nhìn rất lệch.

## Production rule mới

> Không thu nhỏ thân chữ để lấy chỗ cho dấu.

Full-width `Ｅ` native của Gaia Master có hai hàng trống sẵn ở trên:

```text
row 0 = blank
row 1 = blank
row 2..11 = native E body
```

0.6.2.16 giữ nguyên row 2..11 **byte-for-byte** và nhét toàn bộ stacked diacritic vào hai hàng trống:

```text
row 0 = circumflex peak + acute upper pixel
row 1 = circumflex shoulders + acute lower pixel
row 2..11 = native E body, unchanged
```

Không thay baseline, chiều cao thân, chiều rộng hay palette/shadow của E.

## Renderer strategy

Giữ nguyên breakthrough của 0.6.2.13:

- no renderer hook;
- no Krom hook;
- no code cave;
- static atlas glyph #0 replacement;
- Character Select control = full-width `ＴＥＳＴ亜`.

Static atlas:

```text
SLPS + 0x5C4EC
860 glyphs
72 bytes/glyph
12x12, 4bpp, LOW nibble first
```

Mapping liên quan:

```text
0x8273 Ｔ -> 481
0x8264 Ｅ -> 466
0x8272 Ｓ -> 480
0x889F 亜 -> 0
```

## Expected runtime

```text
ＴＥＳＴẾ
```

Yêu cầu chấp nhận:

1. `ＴＥＳＴ` bình thường;
2. glyph cuối đọc được rõ là `Ế`;
3. thân `Ế` cao bằng `Ｅ` native;
4. màu/viền/shadow không lệch đáng kể;
5. text khác trong game bình thường.

Nếu pass, dùng geometry full-height này làm nền cho full Vietnamese glyph inventory.

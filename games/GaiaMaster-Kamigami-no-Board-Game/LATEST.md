# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-13**

## Runtime baseline

`0.6.6.1 BASELINE-NORMALIZED` đã runtime PASS với câu thật:

```text
Chọn tướng
```

Glyph + vertical baseline đã ổn. Vấn đề còn lại là horizontal spacing của full-width path.

## Narrow route đã mở

FontNarrowBankScanner report mới nhất chứng minh Gaia có native narrow font bank:

```text
RAM        0x8006BAAC
SLPS       0x5C2AC
geometry   6x12 / 4bpp
reachable  15 narrow indices
native advance = 8px
```

Renderer đã có sẵn đường:

```text
1-byte char -> narrow source -> narrow copy -> return 8 -> cached advance 8px
```

Không cần hook spacing.

## Code cave route bị bỏ hẳn

Zero/NOP candidate trước đây kết thúc ở `SLPS+0x5C2B8`, trong khi narrow font resource bắt đầu từ `SLPS+0x5C2AC`.

Nó overlap font data nên **REJECT / NEVER USE AS CAVE**.

## CURRENT — 0.6.6.2 NATIVE NARROW 8PX

Đã tạo gated builder:

```text
tools/build_gaia_0662_native_narrow_8px.py
tools/00_BUILD_0.6.6.2_NATIVE_NARROW_8PX.cmd
FONT_NARROW_PROOF_0.6.6.2.md
```

Local package:

```text
GaiaMaster_0.6.6.2_NATIVE_NARROW_8PX_REAL_TEXT_PROOF.zip
```

Expected visual:

```text
Chọn tướng
```

Proof dùng 8 custom narrow glyphs:

```text
C h ọ n t ư ớ g
```

Space giữ native byte `0x20`, vốn đã advance 8px.

### Safety gate

Trước khi build, script quét plausible CP932 text trong CLEAN PRGPACK + SLPS và chỉ mượn các direct narrow ASCII owners không xuất hiện trong text.

Candidate owners:

```text
# $ & ' ( ) * + " Z X
```

Cố tình không dùng:

```text
! % - , . /
```

đặc biệt `%` vì `%d/%s` là format token.

Nếu không đủ 8 owner sạch:

```text
[BLOCKED]
```

và **không tạo BIN/CUE**. Chỉ tạo:

```text
GaiaMaster_0.6.6.2_NATIVE_NARROW_GATE_REPORT.txt
```

Nếu `[OK]`, builder tạo:

```text
[VI 0.6.6.2 NATIVE NARROW 8PX].bin
[VI 0.6.6.2 NATIVE NARROW 8PX].cue
[VI 0.6.6.2 NATIVE NARROW 8PX].txt
```

## Runtime test

Chỉ test nếu builder báo `[OK]`:

1. boot generated CUE;
2. vào Character Select;
3. xem `Chọn tướng`;
4. chữ phải sít hơn rõ so với 0.6.6.1, khoảng 8px advance;
5. stop ngay nếu freeze/global corruption;
6. gửi screenshot + TXT nếu visual chưa ổn.

Nếu builder báo `[BLOCKED]`, không boot, chỉ gửi gate report.

## Sau khi 0.6.6.2 PASS

Không giữ ASCII aliases làm production.

Bước production tiếp theo:

- chọn private one-byte half-width codes thật trong `0xA1..0xDF` sau text-use validation;
- tránh `0xDE/0xDF` composition semantics;
- data-patch existing table `0x8007E01C`;
- freeze Vietnamese narrow codepage;
- inventory full `vi_full` charset;
- build full 6x12 Vietnamese font;
- integrate vào Translation Master rebuild.

## Hard rules

- no production 12x16;
- no pointer redirect;
- no composite overlay;
- no global cursor/cache/spacing hook;
- never use `SLPS+0x5C0E0..<0x5C2B8` as cave;
- do not treat `0xE0..0xFC` as one-byte private code space;
- no runtime test if 0.6.6.2 gate says BLOCKED.

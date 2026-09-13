# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-13**

## Runtime baseline

`0.6.6.1 BASELINE-NORMALIZED` đã runtime PASS với câu thật:

```text
Chọn tướng
```

Glyph + vertical baseline ổn. Vấn đề đang xử lý là horizontal spacing.

## Native narrow route

Static reverse/scanner đã chứng minh Gaia có native font hẹp:

```text
RAM        0x8006BAAC
SLPS       0x5C2AC
geometry   6x12 / 4bpp
reachable  indices 0..14
native advance = 8px
```

Renderer gốc đã có đường:

```text
1-byte char
 -> narrow source
 -> native narrow copy
 -> return 8
 -> cached advance 8px
```

Không cần global spacing hook để chứng minh 8px.

## Code cave route bị loại

Zero/NOP candidate cũ kết thúc tại `SLPS+0x5C2B8`, nhưng narrow font resource bắt đầu từ `SLPS+0x5C2AC`.

=> overlap font data, **REJECT / NEVER USE AS CAVE**.

## 0.6.6.2 — BUILD GATE FALSE POSITIVE

`0.6.6.2` **không có runtime result**.

Builder đã dừng trước khi tạo BIN/CUE vì text safety scanner quá rộng, nhận nhiều rác binary thành CP932 text, ví dụ:

```text
62R#eUReVR"T"WTV
wp&#"a
s&qﾟ
```

Do đó:

```text
0.6.6.2 = FALSE BLOCK
DO NOT RETEST OLD PACKAGE
```

Manual corpus review xác nhận ba narrow owners thực sự xuất hiện trong text và phải loại:

```text
(  )   -> (速い者順)
+      -> 通行税 %+3d％
```

Các owner đã chủ động loại từ trước:

```text
!      punctuation risk
%      format token
, -    punctuation/control risk
. /    punctuation/control-code risk
```

## CURRENT — 0.6.6.2b NATIVE NARROW 8PX STRICT GATE

Source/launcher:

```text
tools/build_gaia_0662b_native_narrow_8px.py
tools/00_BUILD_0.6.6.2b_NATIVE_NARROW_8PX.cmd
```

Design note:

```text
FONT_NARROW_PROOF_0.6.6.2b.md
```

Expected visual:

```text
Chọn tướng
```

Eight diagnostic narrow owners:

```text
"  #  $  &  '  *  Z  X
```

Space giữ byte native `0x20` và advance 8px.

### Strict safety gate

0.6.6.2b không còn coi mọi ASCII-ish run là text.

Nó chỉ coi:

1. chuỗi có Japanese characters là real text;
2. ASCII-only là real text khi giống compact uppercase UI/debug label;
3. mixed-case binary-looking runs bị bỏ qua.

Nếu bất kỳ một trong tám owner vẫn có hit thật:

```text
[BLOCKED]
```

=> không tạo BIN/CUE, chỉ gửi gate report.

Nếu `[OK]`:

```text
[VI 0.6.6.2b NATIVE NARROW 8PX].cue
```

chỉ test Character Select một lần.

## Important reverse finding — possible scalable narrow bank

Renderer narrow/wide gate tại:

```asm
0x8003C3E8  sltiu v0,a1,15
```

Native narrow source formula:

```text
source = 0x8006BAAC
       + 3 * ((index & ~1) * 12)
       + 3 * (index & 1)
```

Index 16 would land exactly at main atlas base:

```text
0x8006BAAC + 576 = 0x8006BCEC
```

Một main 12x12 / 72-byte cell cũng chính là hai half-cell 6x12 / 36-byte theo layout hàng. Vì vậy main atlas có tiềm năng trở thành vùng narrow mở rộng.

**Chưa được phép runtime patch threshold.** Nếu chỉ tăng `<15` toàn cục sẽ reclassify ASCII/table entries đang có và có thể phá text. Sau proof 0.6.6.2b cần thiết kế selective private-code route, không patch threshold mù.

## Runtime gate

Chỉ nếu 0.6.6.2b builder báo `[OK]`:

1. boot generated CUE;
2. chỉ vào Character Select;
3. expected `Chọn tướng`;
4. spacing phải sít hơn rõ so với 0.6.6.1, target ~8px;
5. stop ngay nếu freeze/global corruption;
6. gửi screenshot + generated TXT.

Nếu `[BLOCKED]`, không boot gì cả.

## Hard rules

- no production 12x16;
- no pointer redirect;
- no composite overlay;
- no global cursor/cache/spacing hook;
- never use `SLPS+0x5C0E0..<0x5C2B8` as cave;
- do not treat `0xE0..0xFC` as private one-byte space;
- do not retest blocked `0.6.6.2`;
- do not globally raise the narrow `<15` threshold;
- stop immediately on freeze/global corruption.

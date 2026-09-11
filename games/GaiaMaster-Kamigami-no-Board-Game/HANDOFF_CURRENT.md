# HANDOFF — Gaia Master PS1 Việt hóa

> File này là checkpoint để chuyển phiên chat mà không mất mạch làm việc.

## Source game

- `GaiaMaster - Kamigami no Board Game (Japan).bin`
- MODE2/2352
- serial `SLPS-02075`
- SHA1 gốc `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- executable `SLPS_020.75`
- main text/archive đang làm: `PRGPACK.BDP`

## Reverse-engineering đã chốt

### BDP

- magic `0x000010F0`
- checksum tại `+0x04`
- TOC size `+0x08`
- count `+0x0C`
- descriptor `(offset,size)` 8 bytes

Checksum:

```text
sum16 = sum(all bytes except +0x04..+0x07) & 0xFFFF
checksum = ((~sum16 & 0xFFFF) << 16) | sum16
```

Verified 60/60 nested BDP + top-level PRGPACK.

### Raw PS1 sector

MODE2/Form1 sector user data starts at raw `+24`, 2048 bytes. Sau patch phải regenerate EDC/ECC. Patcher hiện tại đã verify bằng runtime.

## Encoding/rendering

- Shift-JIS Japanese: OK.
- Full-width Latin CP932: **OK runtime**.
- ASCII 1-byte cũ: **FAIL runtime**, hiện ký hiệu sai dù checksum đúng.
- Nguyên nhân ASCII fail đã reverse: Japanese build đang ở 2-byte KROM mode, nên byte ASCII bị consume theo cặp.
- UTF-8 trực tiếp: không dùng.

## Font renderer breakthrough 0.3

Static reverse đã xác định đường render thật trong `SLPS_020.75`.

### Japanese path

Renderer loop quanh `0x80036460`.

Khi global font/region mode = 0, code tại `0x800364E4` đọc 2 byte Shift-JIS, ghép thành 16-bit code rồi gọi wrapper `0x80068208`.

`0x80068208` là trampoline BIOS `B(51h) Krom2RawAdd`.

=> Japanese glyph bình thường lấy từ BIOS KROM 16x15.

### Single-byte path

Khi font/region mode != 0, code dùng base BIOS font:

```text
BFC7F8DE
```

và tính:

```text
glyph = base + (byte - 0x21) * 15
```

Helper `0x80036788` scan 15 rows, bit7..bit0.

=> single-byte glyph format là 8x15, 15 bytes/glyph.

### Font Test 0.3

Đã build `GaiaMaster_VI_Font_Test_0.3_CUSTOM_GLYPH`.

Diagnostic này:

1. force renderer sang single-byte mode;
2. redirect font base sang custom atlas trong RAM;
3. inject atlas 8x15 vào zero cave của executable;
4. map 67 ký tự Việt HOA có dấu vào custom one-byte codes;
5. hiển thị test ngay INTRO.

Custom atlas:

```text
SLPS file offset: 0x6FE10
RAM address:      0x8007F610
size:             3345 bytes
codes:            0x21..0xFF
```

Visible intro target:

```text
TIẾNG VIỆT
Ă Â Ê Ô Ơ Ư Đ
Á À Ả Ã Ạ
Ắ Ằ Ẳ Ẵ Ặ
Ế Ề Ể Ễ Ệ
Ớ Ờ Ở Ỡ Ợ
Ứ Ừ Ử Ữ Ự
```

Local builder verify:

```text
[OK] GAIA MASTER VI FONT TEST 0.3 BUILD SUCCESS
Patched text locations: 11
Touched nested BDP entries: 1 [29]
Changed raw sectors: 6
Output SHA1: 5099867923398aad35c59ca177c24409a41514d6
```

Runtime result: **đang chờ user test**.

Caveat: test 0.3 force single-byte global nên Japanese text sau intro có thể rác. Chỉ đánh giá intro.

Nếu 0.3 pass, next step là hybrid renderer:

- ASCII/custom Vietnamese -> custom single-byte atlas;
- Japanese Shift-JIS chưa dịch -> KROM 2-byte path.

Điều này vừa cho phép dev build Nhật/Việt lẫn nhau, vừa có thể dùng 1-byte Vietnamese để giảm áp lực slot.

Chi tiết đầy đủ: `FONT_RENDERER_REVERSE_0.3.md`.

## Important diagnostics

- 0.1.8 balanced swap là clue checksum.
- 0.1.9 A/B/C/D checksum-fix: all OK.
- Visible Menu 0.2.1: user thấy `ＶＩＥＴＨＯＡＴＥＳＴ！`.

## Windows builder pitfalls

1. Tên `(Japan).bin` trong parenthesized BAT `IF (...)` gây `.bin was unexpected at this time.`
   - dùng labels/goto, tránh block chứa path có ngoặc.
2. JSON có tiếng Nhật nếu `open()` không chỉ encoding trên Windows có thể `UnicodeDecodeError('charmap')`.
   - JSON nên ASCII-safe (`ensure_ascii=True`) hoặc `open(..., encoding='utf-8')`.

## Translation status

### Alpha 0.5.1

- 203 patch
- runtime user confirmed OK

### Master 0.6

- 596 rows workflow
- source-of-truth giữ `vi_full` có dấu
- runtime fallback `vi_game_current` không dấu

### Alpha 0.6

- 366 patch
- 25 raw sectors
- output SHA1 `5a12d3209deee065c129945e169e632f4cec9a8e`
- 230 rows pending vì full-width 2-byte vượt slot

### Alpha 0.6.1 FRONT

- thêm 31 front-loaded patch
- tổng 397 patch
- 26 raw sectors
- output SHA1 `54d2fb026bc3b71c79861e723caffb4114caa34c`
- runtime user confirmed nhiều text đầu game đã Việt hóa
- nhưng đa số vẫn Nhật
- có intro mixed Nhật + Việt do fragment chưa phủ hết

Front text offsets đáng nhớ:

```text
0xC0274  月も太陽もおおいかくす
0xC028C  世界はもはや人のものではなくなった
0xBFC20  武器スキルのデータをロードする？
```

## Graphic candidates

Chưa tìm thấy dưới dạng normal Shift-JIS strings ở vùng text scan:

- `ストーリーモード`
- `対戦モード`
- `武器スキルリスト`
- `オプション`
- `キャラクターセレクト`

Treat as likely graphic/texture until proven otherwise.

## User testing preference

**Không bắt user vào sâu gameplay để test.**
Mọi diagnostic/demo mới phải đặt visible result ngay intro/main menu/character select nếu có thể.

## NEXT TASK — highest priority

1. User test `Font Test 0.3` ngay intro.
2. Nếu glyph có dấu hiện đúng: build hybrid renderer.
3. Chuyển runtime encoder sang custom Vietnamese one-byte path.
4. Dọn intro mixed Nhật/Việt.
5. Patch graphic main menu/Character Select.
6. Tiếp tục full translation + repack 230 pending rows.

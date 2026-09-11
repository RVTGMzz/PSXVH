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
- ASCII 1-byte: **FAIL runtime**, hiện ký hiệu sai dù checksum đúng. Không quay lại hướng này.
- UTF-8 trực tiếp: không dùng.

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

### Vietnamese diacritics visible font test

User đã đồng ý test dấu ngay bây giờ.

Goal visible string ngay đầu game:

```text
TIẾNG VIỆT
Ă Â Ê Ô Ơ Ư Đ
Á À Ả Ã Ạ
Ắ Ằ Ẳ Ẵ Ặ
Ế Ề Ể Ễ Ệ
Ớ Ờ Ở Ỡ Ợ
Ứ Ừ Ử Ữ Ự
```

Không encode UTF-8 trực tiếp.

Research path:

1. trace text renderer/glyph lookup;
2. executable có đầu mối wrapper/trampoline BIOS `B(51h) Krom2RawAdd`;
3. xác nhận runtime có gọi BIOS font path hay font custom;
4. nếu BIOS path: tìm cách map mã 2-byte không dùng sang custom Vietnamese glyph hoặc hook glyph fetch;
5. nếu custom atlas: locate atlas/table, replace unused glyph slots và tạo encoder map;
6. test visible ngay đầu game.

Nếu font test pass:

- chuyển builder sang encode `vi_full` có dấu;
- dọn intro mixed Nhật/Việt;
- patch graphic main menu/Character Select;
- tiếp tục full translation;
- reverse/repack string table cho 230 pending rows.

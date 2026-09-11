# HANDOFF — Gaia Master PS1 Việt hóa

> Checkpoint để chuyển phiên chat mà không mất mạch làm việc.

## Source game

- `GaiaMaster - Kamigami no Board Game (Japan).bin`
- MODE2/2352
- serial `SLPS-02075`
- SHA1 gốc `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- executable `SLPS_020.75`
- main archive đang làm: `PRGPACK.BDP`

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

MODE2/Form1 user data raw `+24`, 2048 bytes. Sau patch phải regenerate EDC/ECC. Patcher hiện tại đã runtime verify.

## Encoding/rendering

- Shift-JIS Japanese: OK.
- Full-width Latin CP932: OK runtime.
- ASCII 1-byte theo renderer hiện tại: FAIL runtime, hiện ký hiệu sai.
- UTF-8 trực tiếp: không dùng.

## Translation status

### Alpha 0.5.1
- 203 patch
- runtime user confirmed OK

### Master 0.6
- 596 rows
- `vi_full` giữ tiếng Việt có dấu làm source-of-truth
- fallback runtime không dấu

### Alpha 0.6
- 366 patch
- 25 raw sectors
- output SHA1 `5a12d3209deee065c129945e169e632f4cec9a8e`
- 230 rows pending vì full-width 2-byte vượt slot

### Alpha 0.6.1 FRONT
- tổng 397 patch
- 26 raw sectors
- output SHA1 `54d2fb026bc3b71c79861e723caffb4114caa34c`
- runtime user confirmed nhiều text đầu game đã Việt hóa
- vẫn còn nhiều Nhật và intro có fragment Nhật/Việt lẫn nhau

Front offsets quan trọng:

```text
0xC0274  月も太陽もおおいかくす
0xC028C  世界はもはや人のものではなくなった
0xBFC20  武器スキルのデータをロードする？
```

## Font Test 0.3 — kết luận runtime

Bản `GaiaMaster_VI_Font_Test_0.3_CUSTOM_GLYPH` là diagnostic riêng dựng từ ROM gốc, không kế thừa 397 patch của Alpha 0.6.1. User báo sau build game trông như ROM gốc và không có kết quả font có dấu dễ quan sát.

=> Không coi 0.3 là PASS hay FAIL glyph. Nó đơn giản là test không tốt vì target intro không phải trang đầu và branch diagnostic tách khỏi alpha hiện hành.

Không dùng 0.3 làm nền tiếp theo.

## Renderer breakthrough sau 0.3

Có hai đường glyph quan trọng trong executable.

### Renderer loop cũ

Quanh `0x80036460`:
- Japanese 2-byte ghép Shift-JIS rồi gọi wrapper `0x80068208`
- wrapper `0x80068208` là BIOS `B(51h) Krom2RawAdd`
- single-byte path dùng BIOS 8x15 tại `BFC7F8DE`

### Glyph resolver khác, rất quan trọng

Function quanh `0x8003C210` cũng nhận character code, nhận diện lead byte Shift-JIS `0x81..0x9F` / `0xE0..0xFC`, và khi cần glyph 16x15 cũng gọi cùng wrapper `0x80068208`.

=> Hook tốt nhất không phải force renderer global sang single-byte. Hook tốt nhất là **hook chính wrapper Krom2RawAdd**:

- Japanese bình thường -> đi BIOS KROM cũ, không đổi.
- custom Vietnamese reserved code `0x85xx` -> trả pointer vào atlas custom trong SLPS.

Cách này tạo hybrid renderer tự nhiên và giữ text Nhật chưa dịch.

## Alpha 0.6.2 HYBRID FONT TEST — đã build, chờ runtime

Bản mới kế thừa **toàn bộ 397 patch của Alpha 0.6.1 FRONT**.

Thêm 3 executable patches:

1. hook wrapper tại SLPS file offset `0x58A08` (VA `0x80068208`);
2. inject custom wrapper stub tại `0x6FE10`;
3. inject atlas Vietnamese 16x15 tại `0x6FEC0`.

Custom codepage:
- reserved Shift-JIS lead `0x85`
- đủ mapping cho **134 ký tự Việt precomposed hoa + thường**
- normal Japanese vẫn gọi BIOS `Krom2RawAdd`

Atlas:
- 16x15
- 30 bytes/glyph
- 2 bytes mỗi row
- bit7 là pixel trái trong từng byte
- 134 glyph
- 4020 bytes

First intro page được thay trực tiếp để test ngay khi cold boot:

```text
TIẾNG VIỆT ẮỀỘỚỰ
ĂÂÊÔƠƯĐ
```

Hai dòng này thay đúng các offset đã biết xuất hiện đầu intro:

```text
0xC028C -> TIẾNG VIỆT ẮỀỘỚỰ
0xC0274 -> ĂÂÊÔƠƯĐ
```

Local build verify:

```text
[OK] GAIA MASTER VI ALPHA 0.6.2 HYBRID FONT BUILD SUCCESS
Patched text locations: 400
Touched nested BDP entries: 9 [0,3,4,5,6,7,8,29,30]
Changed raw sectors: 30
Output SHA1: 5a6d4e1ebb63e0331e6af81cc7d215f57e3a05ab
```

## Test yêu cầu cho user

Không vào gameplay sâu.

Cold boot và chỉ nhìn **trang intro đầu tiên**:

- nếu thấy `TIẾNG VIỆT ẮỀỘỚỰ` và `ĂÂÊÔƠƯĐ` đúng dấu -> hybrid glyph PASS;
- nếu chữ méo / ký hiệu lạ -> screenshot trang đó;
- sau intro, các patch Việt hóa của Alpha 0.6.1 vẫn phải còn. Nếu mất hết -> đang mở nhầm image hoặc build sai.

## Graphic candidates

Chưa tìm thấy dưới dạng normal Shift-JIS strings:

- `ストーリーモード`
- `対戦モード`
- `武器スキルリスト`
- `オプション`
- `キャラクターセレクト`

Treat as likely graphic/texture until proven otherwise.

## Windows builder pitfalls

1. `(Japan).bin` trong parenthesized BAT `IF (...)` từng gây `.bin was unexpected at this time.` -> dùng labels/goto.
2. JSON tiếng Nhật trên Windows phải `ensure_ascii=True` hoặc `open(..., encoding='utf-8')`.

## User testing preference

**Không bắt user vào sâu gameplay để test.** Mọi diagnostic/demo phải nhìn thấy kết quả ngay intro/main menu/character select nếu có thể.

## NEXT TASK

1. Chờ runtime Alpha 0.6.2 hybrid font test.
2. Nếu PASS: chuyển encoder từ full-width fallback sang custom `0x85xx` cho `vi_full`, nhưng giữ hybrid Japanese fallback.
3. Dọn intro Nhật/Việt lẫn nhau.
4. Patch graphic main menu/Character Select.
5. Tiếp tục full translation + reverse/repack 230 pending rows.

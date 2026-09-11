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

## Encoding/rendering đã xác nhận

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

## Font work — những gì đã thử

### Font Test 0.3

Diagnostic riêng dựng từ ROM gốc. Không kế thừa 397 patch Alpha 0.6.1 nên không phù hợp để đánh giá tiến độ Việt hóa. Không coi là PASS/FAIL glyph.

### Alpha 0.6.2 HYBRID FONT

Ý tưởng:
- hook global wrapper `Krom2RawAdd` tại VA `0x80068208` / SLPS file offset `0x58A08`;
- custom code `0x85xx` trả glyph từ atlas Việt 16x15;
- Japanese bình thường vẫn gọi BIOS KROM.

Kết quả runtime: **TREO ngay sau logo PlayStation, trước intro**.

=> Global hook không an toàn theo cách đã implement.

### Alpha 0.6.2.1 HYBRID HOTFIX

Đổi chiến lược:
- không hook global wrapper;
- chỉ hook renderer call-site tại SLPS `0x26CF4`;
- custom code `0x85xx` -> atlas Việt;
- normal Japanese -> tail jump wrapper gốc.

Kết quả runtime: **vẫn TREO sau logo PlayStation**.

=> Chưa thể kết luận lỗi do custom code/atlas, vì game chết trước khi thấy intro.

### Font Isolation 0.6.2.2

Tách test A/B:

- A: renderer -> stub 8 byte -> wrapper gốc, không custom glyph.
- B: nếu A boot thì map đúng một mã Shift-JIS hợp lệ `0x889F` (`亜`) thành glyph `Ế`.

User báo **vẫn treo**. Theo flow test (A phải chạy trước và nếu A treo thì không chạy B), hiện ghi nhận **A = TREO**.

Điều này rất quan trọng:

> Ngay cả pass-through stub cũng treo, nên chưa phải lỗi font Việt hay mã `0x85xx`. Nghi vấn lớn chuyển sang vị trí code cave / runtime overwrite / redirect call-site.

## Phát hiện code cave mới

Code cave cũ dùng ở các font test:

```text
SLPS file offset 0x6FE10
```

Dù là zero trong file EXE, nó có thể là vùng runtime workspace/BSS-like area bị game ghi đè trước khi renderer gọi tới. Vì vậy patch build đúng trên đĩa nhưng CPU có thể nhảy vào dữ liệu đã bị overwrite.

Đã tìm thấy một vùng zero-padding ngắn hơn nằm giữa các block dữ liệu tĩnh:

```text
SLPS file offset 0x5C0E0 .. 0x5C2B8
length 472 bytes
VA start 0x8006B8E0
```

Vùng này được ưu tiên làm `SAFE_CAVE` tiếp theo.

## Font Isolation 0.6.2.3 SAFE CAVE — build mới nhất

Package local:

`GaiaMaster_VI_Font_Isolation_0.6.2.3_SAFE_CAVE.zip`

Cả hai test vẫn kế thừa toàn bộ 397 patch Alpha 0.6.1 FRONT.

### TEST A2

`TEST_A2_SAFE_CAVE.bat`

Chỉ làm:

```text
renderer call-site 0x26CF4
-> JAL safe cave 0x5C0E0
-> J wrapper gốc 0x80068208
```

Không custom glyph, không atlas, không sửa intro test.

Expected result:

```text
A2 BOOT
hoặc
A2 TREO
```

Nếu A2 TREO: dừng, không test B2.

### TEST B2

`TEST_B2_SAFE_ONE_GLYPH.bat`

Chỉ chạy nếu A2 BOOT.

- dùng mã Shift-JIS hợp lệ `0x889F` (`亜`), không dùng `0x85xx`;
- hook riêng mã này sang một glyph custom 16x15 `Ế`;
- intro đầu đổi thành `TEST + 0x889F`.

Expected:

```text
B2 HIEN Ế
B2 HIEN 亜
B2 TREO
B2 HIEN KHAC
```

Local build verification:

```text
A2 output SHA1 a0f500e9d63cb2f4720eab34a6d24dcb62d2be1a
B2 output SHA1 a159faeba61e51dbbbd3f1371dc40b91bb93225c
```

## Renderer notes

Có hai đường glyph đáng chú ý trong executable:

1. Renderer loop quanh `0x80036460` ghép Shift-JIS rồi gọi wrapper `0x80068208`.
2. Function quanh `0x8003C210` cũng phân loại lead byte SJIS và dùng cùng wrapper khi cần glyph 16x15.

Wrapper gốc `0x80068208` là trampoline BIOS `B(51h) Krom2RawAdd`.

Hiện chưa nên tiếp tục hybrid font lớn cho đến khi A2 xác nhận redirect call-site + safe cave có thể chạy runtime.

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

1. User test `A2 SAFE CAVE`.
2. Nếu A2 BOOT -> test `B2 SAFE ONE GLYPH`.
3. Nếu A2 TREO -> bỏ giả thuyết code cave cũ là nguyên nhân duy nhất; cần reverse chính xác calling convention / renderer target hoặc dùng debugger runtime thay vì tiếp tục đoán hook.
4. Chỉ khi one-glyph pass mới quay lại custom codepage tiếng Việt đầy đủ.
5. Sau font: dọn intro mixed Nhật/Việt, patch graphics, tiếp tục full translation và repack 230 pending rows.

# HANDOFF — Gaia Master PS1 Việt hóa

> Checkpoint hiện tại để chuyển phiên chat mà không mất mạch làm việc.

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
0xBFD2C  キャラクターをえらんでね   # visible Character Select probe
```

## Graphic candidates

Chưa tìm thấy dưới dạng normal Shift-JIS strings:

- `ストーリーモード`
- `対戦モード`
- `武器スキルリスト`
- `オプション`
- `キャラクターセレクト`

Treat as likely graphic/texture until proven otherwise.

## Font work — toàn bộ kết quả tới 0.6.2.6

### Font Test 0.3

Diagnostic riêng dựng từ ROM gốc. Không kế thừa 397 patch Alpha 0.6.1 nên không phù hợp để đánh giá tiến độ Việt hóa. Không coi là PASS/FAIL glyph.

### Alpha 0.6.2 HYBRID FONT

- hook global wrapper `Krom2RawAdd` tại VA `0x80068208` / SLPS file offset `0x58A08`;
- custom code `0x85xx` -> atlas Việt 16x15;
- runtime: **TREO ngay sau logo PlayStation**.

### Alpha 0.6.2.1 HYBRID HOTFIX

- bỏ global hook;
- chỉ hook renderer call-site `0x26CF4`;
- runtime: **vẫn TREO sau logo**.

### Font Isolation 0.6.2.2

- A: pass-through stub qua code cave cũ `0x6FE10` -> wrapper gốc.
- A runtime: **TREO**.

Kết luận: chưa phải lỗi glyph Việt; nghi code cave cũ bị runtime overwrite.

### Font Isolation 0.6.2.3 SAFE CAVE

Safe cave mới:

```text
SLPS file offset 0x5C0E0 .. 0x5C2B8
VA start 0x8006B8E0
length 472 bytes
```

Kết quả user:

- `A2 SAFE PASS`: **BOOT**
- `B2 SAFE ONE GLYPH`: **BOOT**

User không thấy glyph `Ế` vì probe đặt ở intro không đi qua đúng render path cần quan sát.

=> Safe cave mới được xác nhận runtime an toàn.

### Font Isolation 0.6.2.4 VISIBLE MENU

Probe chuyển sang đúng dòng đã từng nhìn thấy ở Character Select:

```text
PRGPACK 0xBFD2C
キャラクターをえらんでね
```

- C1 text-only: `TEST亜`
- C2 hook call-site `0x26CF4`, map `0x889F` (`亜`) -> glyph `Ế`

Kết quả:

```text
C1: HIEN TEST亜
C2: HIEN TEST亜
```

=> Call-site `0x26CF4` KHÔNG phải đường glyph của dòng Character Select này.

### Font Isolation 0.6.2.5 SECOND RENDER PATH

Test direct Krom caller thứ hai:

```text
SLPS file offset 0x2CCA0
VA 0x8003C4A0
```

- D1 pass-through: `TEST亜`
- D2 intercept `0x889F` -> `Ế`

Kết quả:

```text
D1: HIEN TEST亜
D2: HIEN TEST亜
```

=> Direct caller `0x2CCA0` cũng KHÔNG phải đường glyph của Character Select.

### Font Isolation 0.6.2.6 GLOBAL SAFE WRAPPER

Do cả 2 direct caller đều không bắt được, thử lại global wrapper nhưng dùng SAFE CAVE đã xác nhận boot và chỉ intercept 1 mã SJIS hợp lệ `0x889F`.

- E1 global pass-through exact wrapper behavior
- E2 global wrapper + intercept `0x889F` -> custom glyph `Ế`

Kết quả user:

```text
E1: BOOT + TEST亜
E2: HIEN TEST亜
```

## Kết luận font mới nhất

Kết quả C2 + D2 + E2 rất mạnh:

> Character Select KHÔNG lấy glyph `亜` qua wrapper `Krom2RawAdd` mà ta đã hook, kể cả khi hook global wrapper bằng safe cave.

Do đó **dừng hướng Krom wrapper cho Character Select**. Không cần test thêm direct/global Krom hooks kiểu tương tự.

Khả năng còn lại mạnh nhất:

1. game dùng custom glyph cache/font atlas riêng cho UI này;
2. glyph đã được preload/copy vào cache/VRAM bằng đường khác, không qua wrapper đang hook;
3. có renderer khác nhận code Shift-JIS nhưng tra atlas/table riêng.

## Renderer notes

Đã thấy hai direct caller tới wrapper `0x80068208`:

1. quanh `0x80036460` / file `0x26CF4`
2. quanh `0x8003C210` / call file `0x2CCA0`

Cả hai đều không ảnh hưởng glyph Character Select probe `0xBFD2C`.

Wrapper gốc `0x80068208` là trampoline BIOS `B(51h) Krom2RawAdd`, nhưng Character Select đang đi đường khác hoặc dùng glyph cache đã có sẵn.

## Windows builder pitfalls

1. `(Japan).bin` trong parenthesized BAT `IF (...)` từng gây `.bin was unexpected at this time.` -> dùng labels/goto.
2. JSON tiếng Nhật trên Windows phải `ensure_ascii=True` hoặc `open(..., encoding='utf-8')`.

## User testing preference

**Tối ưu thời gian test.**

- Không bắt user vào sâu gameplay.
- Ưu tiên test có giá trị thông tin cao nhất trước.
- Test phụ chỉ chạy khi kết quả chính không phân biệt được nguyên nhân.
- Mọi probe visible nên ở intro/main menu/Character Select.

## NEXT TASK — KHÔNG test Krom wrapper nữa

1. Reverse custom font cache/atlas của Character Select/UI.
2. Tìm vùng RAM/VRAM hoặc asset chứa glyph `亜` / bộ font Nhật đang được UI này sử dụng.
3. Tìm code reference từ Character Select renderer tới atlas/cache này.
4. Khi tìm được, tạo **một probe duy nhất**: thay glyph `亜` trong cache/atlas thành `Ế` và giữ text `TEST亜` ở `0xBFD2C`.
5. Nếu hiện `TESTẾ`, mới mở rộng thành custom Vietnamese glyph table/codepage.
6. Sau font: dọn intro mixed Nhật/Việt, patch graphics, tiếp tục full translation và repack 230 pending rows.

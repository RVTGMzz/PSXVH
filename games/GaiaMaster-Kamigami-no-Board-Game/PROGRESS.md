# Gaia Master: Kamigami no Board Game (Japan) — Tiến độ Việt hóa

Cập nhật: **2026-09-12 sau Font Isolation 0.6.2.6**.

## Bản game mục tiêu

- Platform: PlayStation 1
- Region: Japan
- Serial: `SLPS-02075`
- Disc format: MODE2/2352 BIN/CUE
- SHA1 BIN gốc: `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- Emulator test: DuckStation

## Reverse-engineering đã chốt

### BDP

`PRGPACK.BDP` là archive BDP chứa 60 nested BDP.

Header:

- `+0x00`: magic `0x000010F0`
- `+0x04`: checksum 32-bit
- `+0x08`: TOC size
- `+0x0C`: entry count
- descriptor `(offset,size)` 8 byte/entry

Checksum:

```text
sum16 = sum(all bytes except checksum field +0x04..+0x07) & 0xFFFF
checksum = ((~sum16 & 0xFFFF) << 16) | sum16
```

Đã verify trên **60/60 nested BDP** và top-level `PRGPACK.BDP`.

### Raw PS1 sector

MODE2/Form1 user data ở raw `+24`, 2048 byte. Sau patch phải regenerate EDC/ECC. Pipeline hiện tại đã runtime verify.

## Encoding/runtime đã xác nhận

- Shift-JIS Japanese: OK.
- Full-width Latin CP932: **OK runtime**.
- ASCII 1-byte: **FAIL runtime**, hiện ký hiệu sai.
- UTF-8 trực tiếp: không dùng.

## Windows builder pitfalls đã chốt

1. `(Japan).bin` trong parenthesized BAT block từng gây `.bin was unexpected at this time.` -> dùng labels/goto.
2. JSON tiếng Nhật trên Windows phải ASCII-safe hoặc explicit `encoding='utf-8'`.

## Translation status

### Alpha 0.5.1

- 203 patch
- runtime user confirmed OK

### Master 0.6

- **596 rows** trong workflow
- `vi_full`: tiếng Việt có dấu, source-of-truth
- `vi_game_current`: fallback không dấu
- **230 rows** chờ repack vì full-width 2-byte vượt slot

### Alpha 0.6

- 366 patch
- 25 raw sectors
- output SHA1 `5a12d3209deee065c129945e169e632f4cec9a8e`

### Alpha 0.6.1 FRONT

- 397 patch
- 26 raw sectors
- output SHA1 `54d2fb026bc3b71c79861e723caffb4114caa34c`
- user xác nhận nhiều text đầu game đã Việt hóa
- vẫn còn nhiều Nhật
- intro có fragment Nhật + Việt lẫn nhau do chưa patch đủ toàn bộ fragment

Visible front offsets quan trọng:

```text
0xC0274  月も太陽もおおいかくす
0xC028C  世界はもはや人のものではなくなった
0xBFC20  武器スキルのデータをロードする？
0xBFD2C  キャラクターをえらんでね
```

`0xBFD2C` hiện là probe Character Select chính vì user đã xác nhận nhìn thấy trực tiếp.

## Graphic candidates

Các label lớn sau chưa tìm thấy như normal Shift-JIS strings trong vùng text đã scan:

- `ストーリーモード`
- `対戦モード`
- `武器スキルリスト`
- `オプション`
- `キャラクターセレクト`

Khả năng cao cần graphic/texture patch riêng, nhưng chưa tuyên bố 100% cho tới khi asset được xác định.

# Font/glyph tiếng Việt — chuỗi test 0.6.2.x

## 0.6.2 HYBRID FONT

Global hook `Krom2RawAdd` + custom `0x85xx` atlas.

Runtime: **TREO sau logo PlayStation**.

## 0.6.2.1 HYBRID HOTFIX

Hook direct renderer call-site `0x26CF4` thay vì global wrapper.

Runtime: **vẫn TREO sau logo**.

## 0.6.2.2 Isolation

Pass-through stub ở code cave cũ `0x6FE10`.

Runtime: **TREO**.

=> nghi code cave bị runtime overwrite.

## 0.6.2.3 SAFE CAVE

Safe cave mới:

```text
SLPS 0x5C0E0 .. 0x5C2B8
VA 0x8006B8E0
length 472 bytes
```

Kết quả:

```text
A2: BOOT
B2: BOOT
```

=> safe cave runtime an toàn.

## 0.6.2.4 VISIBLE MENU

Probe chuyển sang Character Select `0xBFD2C`.

```text
C1: HIEN TEST亜
C2: HIEN TEST亜
```

C2 hook direct caller `0x26CF4`, intercept `0x889F` (`亜`) -> `Ế` nhưng không có tác dụng.

## 0.6.2.5 SECOND RENDER PATH

Direct caller thứ hai:

```text
SLPS file offset 0x2CCA0
VA 0x8003C4A0
```

Kết quả:

```text
D1: HIEN TEST亜
D2: HIEN TEST亜
```

=> caller thứ hai cũng không phải đường glyph của Character Select.

## 0.6.2.6 GLOBAL SAFE WRAPPER

Thử global `Krom2RawAdd` wrapper lại nhưng dùng safe cave và chỉ intercept mã Shift-JIS hợp lệ `0x889F`.

Kết quả:

```text
E1: BOOT + TEST亜
E2: HIEN TEST亜
```

## Kết luận font hiện tại

C2 + D2 + E2 đều giữ nguyên `亜`.

=> Character Select **không lấy glyph `亜` qua Krom2RawAdd path đã hook**.

Không tiếp tục tạo thêm biến thể direct/global Krom wrapper tương tự.

Khả năng mạnh tiếp theo:

1. custom glyph cache/font atlas riêng;
2. glyph preload vào RAM/VRAM;
3. renderer UI lookup table/cache khác;
4. asset font custom/nén chưa được nhận diện.

Chi tiết đầy đủ nằm ở:

```text
FONT_ISOLATION_0.6.2x.md
HANDOFF_CURRENT.md
```

# NEXT TASK

1. Reverse custom font cache/atlas của Character Select/UI.
2. Tìm bitmap glyph `亜` trong RAM/VRAM/asset.
3. Xác định glyph dimensions/packing/index table.
4. Làm **một probe duy nhất**:

```text
text vẫn = TEST亜
bitmap glyph 亜 -> bitmap Ế
```

Expected:

```text
TESTẾ
```

5. Nếu pass, mở rộng thành bảng glyph tiếng Việt có dấu.
6. Sau font: dọn intro mixed Nhật/Việt, patch graphics, tiếp tục full translation và reverse/repack 230 rows pending.

## Quy tắc test tối ưu thời gian

- test chính trước;
- control test chỉ chạy nếu test chính treo hoặc mơ hồ;
- ưu tiên Character Select / intro / main menu;
- không bắt user vào sâu gameplay;
- không lặp lại nhánh Krom wrapper đã bị loại.

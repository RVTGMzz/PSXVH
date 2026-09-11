# Gaia Master: Kamigami no Board Game (Japan) — Tiến độ Việt hóa

## Bản game mục tiêu

- Platform: PlayStation 1
- Region: Japan
- Serial: `SLPS-02075`
- Disc format: MODE2/2352 BIN/CUE
- SHA1 BIN gốc: `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- Emulator test: DuckStation

## Những gì đã xác định

- `SLPS_020.75` chứa nhiều text gameplay/card/menu dạng Shift-JIS.
- `PRGPACK.BDP` là BDP archive chứa 60 nested BDP.
- Các nested BDP và top-level BDP dùng cùng cơ chế checksum additive 32-bit.
- Latin full-width Shift-JIS đã được xác nhận hiển thị trong game.
- Patcher raw MODE2/Form1 + EDC/ECC đang hoạt động đúng.

## Cấu trúc BDP đã reverse

Header quan sát được:

- `+0x00`: magic `0x000010F0`
- `+0x04`: checksum 32-bit
- `+0x08`: TOC size
- `+0x0C`: entry count
- sau đó là descriptor `(offset, size)` 8 byte/entry

Payload base top-level của `PRGPACK.BDP` là `8 + toc_size`.

### Checksum

Công thức đã khớp chính xác với **toàn bộ 60 nested BDP** và top-level `PRGPACK.BDP`:

```text
sum16 = sum(all bytes except checksum field +0x04..+0x07) & 0xFFFF
checksum = ((~sum16 & 0xFFFF) << 16) | sum16
```

Nested BDP từng gây treo ở entry 30:

- bắt đầu tại PRGPACK offset `0xDDA98`
- size `0x26BC8`
- checksum gốc `0x9BC0643F`
- chứa bảng 79 chuỗi ở đầu payload

Các test 0.1.8 đã chứng minh patch text nhưng không sửa checksum sẽ treo; `BALANCED_SWAP` chạy vì tổng byte không đổi.

## Diagnostic 0.1.9 — ĐÃ CHỐT

Người dùng đã test:

- A `FIX_A_CHECKSUM`: **OK**
- B `FIX_SLOT_CHECKSUM`: **OK**
- C `FIX_FIRST_CHECKSUM`: **OK**
- D `FULLWIDTH_BATDAU_CHECKSUM`: **OK**

Kết luận: nguyên nhân treo của các alpha trước là checksum nested BDP chưa được cập nhật.

## Visible Menu Test 0.2.1 — ĐÃ CHỐT

Người dùng xác nhận nhìn thấy trực tiếp:

```text
ＶＩＥＴＨＯＡＴＥＳＴ！
```

ở màn chọn nhân vật.

Điều này xác nhận:

1. text patch được game đọc thật;
2. full-width Latin Shift-JIS render được;
3. checksum repair hoạt động trong menu/setup thực tế.

## Alpha 0.5 — LARGE BATCH

Đã tạo `GaiaMaster_Vietnamese_Alpha_0.5` để chuyển khỏi giai đoạn diagnostic nhỏ lẻ.

### Phạm vi

- **203 vị trí text** được patch trong một lần build.
- `SLPS_020.75`: 73 vị trí.
- `PRGPACK.BDP`: 130 vị trí.
- 9 nested BDP bị tác động: entries `0, 3, 4, 5, 6, 7, 8, 29, 30`.
- Text Việt hiện dùng **không dấu + full-width Latin**.
- Các câu dài được rút gọn để không vượt dung lượng chuỗi gốc.

Một số text nhìn dễ:

- `ＣＨＯＮ　ＮＨＡＮＶＡＴ`
- `ＸＡＣ　ＮＨＡＮ？`
- `ＮＨＡＮ　ＮＵＴ　Ｏ`
- `ＢＡＴ　ＤＡＵ！`
- `ＫＯ　ＤＡＴＡ`
- `ＣＨＯＮ　ＳＬＯＴ`

### Builder Alpha 0.5

Builder thực hiện tự động:

1. xác minh SHA1 BIN gốc;
2. xác minh SHA1 `SLPS_020.75` và `PRGPACK.BDP` bên trong image;
3. patch 203 vị trí exact-byte;
4. tính lại checksum cho mọi nested BDP bị sửa;
5. tính lại checksum top-level `PRGPACK.BDP`;
6. ghi lại user-data vào raw BIN;
7. regenerate EDC/ECC cho sector MODE2/Form1 bị thay đổi;
8. tạo BIN/CUE `[VI Alpha 0.5]`.

### Kiểm tra nội bộ trước khi giao test

Builder đã chạy thành công trên BIN SHA1 chuẩn:

- patched locations: `203`
- touched nested BDP entries: `9`
- changed raw sectors: `18`
- output SHA1 test: `2887affb46f0af0c823da2bc365e94b366719c65`

Sau build đã verify:

- 203/203 vị trí có đúng bytes mới;
- checksum top-level PRGPACK hợp lệ;
- checksum 60/60 nested BDP hợp lệ;
- các text visible decode đúng full-width Shift-JIS.

**Trạng thái:** chờ người dùng test Alpha 0.5 trong DuckStation từ menu → gameplay.

## Giới hạn hiện tại

- Chưa phải full translation toàn game.
- Chưa có tiếng Việt có dấu.
- Một số title/logo/menu có thể là texture/image chứ không phải text.
- Chưa repack pointer table để cho phép câu Việt dài tùy ý; Alpha 0.5 vẫn giữ nguyên slot byte của chuỗi gốc.

## Bước sau Alpha 0.5

Nếu Alpha 0.5 chơi ổn:

1. mở rộng batch sang các text còn lại trong SLPS/PRGPACK;
2. dump + phân loại các pack khác (`EVCARD.BDP`, `DUELDATA.BDP`, `PC_DATA.BDP`, `SCR_DATA.BDP`);
3. reverse font/glyph table để hướng tới tiếng Việt có dấu;
4. nghiên cứu repack/pointer table để giảm giới hạn độ dài câu;
5. cuối cùng xuất patch thay vì phân phối BIN game.

## Trạng thái handoff

- Original: **OK**
- COPY_ONLY: **OK**
- BDP structure: **đã reverse cơ bản**
- BDP checksum: **đã reverse + verify 60/60 nested + top-level**
- EDC/ECC raw patch: **OK**
- Full-width Latin rendering: **OK**
- Visible menu test: **OK**
- Alpha 0.5 large batch: **builder hoàn thành, chờ test gameplay thực tế**

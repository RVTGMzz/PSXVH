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
- Nested BDP và top-level BDP dùng checksum additive 32-bit.
- Full-width Latin Shift-JIS đã được xác nhận hiển thị đúng trong game.
- ASCII 1-byte đã test sau khi checksum được sửa đúng và **hiển thị ký hiệu sai**, vì vậy không dùng cho bản dịch.
- Patcher raw MODE2/Form1 + EDC/ECC đang hoạt động đúng.

## Cấu trúc BDP đã reverse

Header quan sát được:

- `+0x00`: magic `0x000010F0`
- `+0x04`: checksum 32-bit
- `+0x08`: TOC size
- `+0x0C`: entry count
- sau đó là descriptor `(offset, size)` 8 byte/entry

Checksum:

```text
sum16 = sum(all bytes except checksum field +0x04..+0x07) & 0xFFFF
checksum = ((~sum16 & 0xFFFF) << 16) | sum16
```

Công thức đã verify trên 60/60 nested BDP và top-level `PRGPACK.BDP`.

## Diagnostic đã chốt

### 0.1.9 checksum fix

- A `FIX_A_CHECKSUM`: **OK**
- B `FIX_SLOT_CHECKSUM`: **OK**
- C `FIX_FIRST_CHECKSUM`: **OK**
- D `FULLWIDTH_BATDAU_CHECKSUM`: **OK**

Kết luận: nguyên nhân treo của các patch trước là checksum nested BDP chưa được cập nhật.

### Visible Menu 0.2.1

Người dùng đã nhìn thấy trực tiếp:

```text
ＶＩＥＴＨＯＡＴＥＳＴ！
```

=> text patch thật sự được game đọc và full-width Latin render đúng.

### ASCII Capacity Test 0.2.2

ASCII 1-byte build được nhưng khi chạy game **hiện ký hiệu/chữ sai**.

=> loại hướng ASCII. Runtime hiện tiếp tục dùng full-width Latin Shift-JIS.

## Alpha 0.5 — runtime đã xác nhận

- 203 vị trí text.
- `SLPS_020.75`: 73 vị trí.
- `PRGPACK.BDP`: 130 vị trí.
- 9 nested BDP bị tác động: `0, 3, 4, 5, 6, 7, 8, 29, 30`.
- Người dùng xác nhận **đã thấy bản dịch hoạt động trong game**.

## Translation master 0.6

Master hiện có **596 vị trí** đã đưa vào workflow dịch.

Master giữ song song:

1. tiếng Nhật gốc;
2. tiếng Việt chuẩn có dấu để làm bản dịch nguồn;
3. fallback không dấu cho runtime hiện tại.

Mục tiêu là khi custom font/glyph hoàn thành thì đổi encoding mà không phải dịch lại từ đầu.

## Alpha 0.6 — LARGE BATCH

Đã build gói `GaiaMaster_Vietnamese_Alpha_0.6`.

### Phạm vi

- **366 vị trí text** được patch an toàn với giới hạn slot hiện tại.
- Alpha 0.5: 203 vị trí.
- Thêm mới ở Alpha 0.6: **163 vị trí**.
- `SLPS_020.75`: 158 vị trí trong tổng batch.
- `PRGPACK.BDP`: 208 vị trí trong tổng batch.
- 9 nested BDP bị sửa: `0, 3, 4, 5, 6, 7, 8, 29, 30`.
- **230 vị trí** trong master đã có bản dịch nhưng chưa thể nhét an toàn vì full-width Latin tốn 2 byte/ký tự và vượt slot gốc. Các dòng này được tách riêng để xử lý sau khi reverse/repack string table.

### Local verification

Builder chạy thành công trên BIN SHA1 chuẩn:

```text
Patched text locations: 366
Touched nested BDP entries: 9 [0, 3, 4, 5, 6, 7, 8, 29, 30]
Changed raw sectors: 25
Output SHA1: 5a12d3209deee065c129945e169e632f4cec9a8e
```

Builder tự động:

1. verify SHA1 BIN gốc;
2. verify embedded `SLPS_020.75` / `PRGPACK.BDP`;
3. patch exact bytes;
4. cập nhật nested BDP checksum;
5. cập nhật top-level BDP checksum;
6. ghi lại user-data;
7. regenerate Mode2/Form1 EDC/ECC;
8. tạo BIN/CUE `[VI Alpha 0.6]`.

**Trạng thái Alpha 0.6:** builder/local verify OK, chờ runtime test trong DuckStation.

## Hai bài toán kỹ thuật còn lại

### 1. Repack / string table

Cần reverse cách tổ chức string table để cho phép câu Việt dài hơn slot Nhật gốc. Đây là chìa khóa để đưa 230 dòng pending và các câu tự nhiên hơn vào game.

### 2. Font tiếng Việt có dấu

Hiện full-width Latin chạy được nhưng các glyph `ă â ê ô ơ ư đ` và dấu thanh chưa có đường render xác nhận. Tiếp tục nghiên cứu font/glyph mapping hoặc hook font renderer.

## Hướng tiếp theo

1. test runtime Alpha 0.6;
2. tiếp tục mở rộng master dịch;
3. reverse/repack string table;
4. nghiên cứu custom glyph tiếng Việt;
5. dump/phân loại thêm `EVCARD.BDP`, `DUELDATA.BDP`, `PC_DATA.BDP`, `SCR_DATA.BDP`;
6. cuối cùng phát hành patch thay vì phân phối BIN game.

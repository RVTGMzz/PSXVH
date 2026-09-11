# Gaia Master: Kamigami no Board Game (Japan) — Tiến độ reverse-engineering

## Bản game mục tiêu

- Platform: PlayStation 1
- Region: Japan
- Serial: `SLPS-02075`
- Disc format: MODE2/2352 BIN/CUE
- SHA1 BIN gốc: `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- Emulator test: DuckStation

## Những gì đã xác định

### 1. Game gốc

Bản BIN/CUE gốc vào gameplay bàn cờ bình thường.

### 2. Text

Text tiếng Nhật đọc được dưới dạng Shift-JIS, không phải toàn bộ bị nén.

Hai vùng quan trọng đã tìm thấy:

- `SLPS_020.75`: executable, có ít nhất khoảng 358 chuỗi Nhật rõ.
- `PRGPACK.BDP`: có khoảng 1.950 chuỗi ứng viên hợp lệ, gồm gameplay/menu/hướng dẫn/đối thoại.

Tổng dump ứng viên đã từng thu được khoảng 2.282 chuỗi.

### 3. Alpha 0.1 thất bại

Thử thay text Nhật bằng ASCII và padding NUL. Game vẫn qua intro/chọn nhân vật nhưng treo khi chuyển vào gameplay.

Kết luận: không được giả định renderer/parser chấp nhận ASCII 1-byte + padding `00`.

### 4. Diagnostic 0.1.3 SAFE_SJIS thất bại

Thử dùng Latin full-width trong Shift-JIS, giữ độ dài chuỗi. Game vẫn treo khi load gameplay.

### 5. Diagnostic 0.1.4 JP_MARKER

Chỉ thay hai chuỗi Nhật bằng chuỗi Nhật khác, cùng Shift-JIS và cùng chính xác số byte:

- `PRGPACK.BDP`: `ゲームをはじめるよ` → `ゲームをはじめるね`.
- `SLPS_020.75`: `%sの番よ！` → `%sの番だ！`.

Kết quả: treo khi vào gameplay.

### 6. COPY_ONLY

Chỉ copy BIN, không sửa byte nào.

Kết quả: gameplay bình thường.

Điều này xác nhận BIN gốc, CUE mới và thao tác copy không phải nguyên nhân.

### 7. Diagnostic 0.1.5 cô lập từng file

- `JP_PRGPACK_ONLY`: chỉ patch `ゲームをはじめるよ` → `ゲームをはじめるね` trong `PRGPACK.BDP`: được báo là **OK**.
- `JP_SLPS_ONLY`: chỉ patch `%sの番よ！` → `%sの番だ！` trong `SLPS_020.75`: **OK**.

Kết quả PRGPACK_ONLY sau đó mâu thuẫn với các test 0.1.6/0.1.7, nên hiện xem đây là một false negative/stale-image khả dĩ và không dùng nó làm bằng chứng rằng offset 908648 an toàn.

## Diagnostic 0.1.6 — KẾT QUẢ

### A. `COMBO_RETEST`

- PRGPACK offset `908648`: `ゲームをはじめるよ` → `ゲームをはじめるね`.
- SLPS offset `2768`: `%sの番よ！` → `%sの番だ！`.
- **Kết quả: TREO.**

### B. `PRGPACK_TWO_SECTORS`

- PRGPACK offset `908648`: `ゲームをはじめるよ` → `ゲームをはじめるね`.
- PRGPACK offset `0x510`: `やるね` → `やるよ`.
- **Kết quả: TREO.**

### C. `SLPS_TWO_SECTORS`

Hai patch đều trong `SLPS_020.75`.

- **Kết quả: OK.**

### D. `COMBO_ALT`

Patch khác trong PRGPACK + patch khác trong SLPS.

- **Kết quả: OK.**

Kết luận: không phải mọi multi-sector patch đều lỗi, không phải mọi cross-file patch đều lỗi, và không phải cứ sửa PRGPACK là lỗi.

## Diagnostic 0.1.7 — KẾT QUẢ

Bốn test đều liên quan đến hai chuỗi nằm tại vùng raw sector `3122` của `PRGPACK.BDP`.

- A `A_ONLY_FRESH`: **TREO**
- B `B_ONLY_SAME_SECTOR`: **TREO**
- C `A_PLUS_B_SAME_SECTOR`: **TREO**
- D `A_PLUS_C_ADJACENT`: **TREO**

Điều này xác nhận chắc hơn rằng riêng thay đổi tại vùng dữ liệu chứa offset `908648` / sector `3122` là trigger ổn định. Kết quả 0.1.5 PRGPACK_ONLY trước đó không còn được coi là đáng tin để kết luận vùng này an toàn.

## Phát hiện cấu trúc BDP mới sau 0.1.7

`PRGPACK.BDP` không phải một blob phẳng. Nó là một archive BDP chứa nhiều BDP con.

Header BDP quan sát được:

- dword 0: `0x000010F0` lặp lại ở các BDP.
- dword 1: giá trị 32-bit chưa xác định chức năng.
- dword 2: kích thước TOC theo mẫu `8 + count * 8`.
- dword 3: số entry.
- tiếp theo là các cặp `(offset, size)` 8 byte/entry.
- offset entry tính từ base sau bảng TOC.

Với `PRGPACK.BDP`:

- count = 60.
- payload base top-level = `0x1F0` (496).
- entry 30 có offset tương đối `907432`, size `158664`.
- nested BDP entry 30 thực sự bắt đầu tại PRGPACK offset `0xDDA98` (907928).
- nested BDP này có 1 entry.
- payload nested bắt đầu tại `0xDDAB0`.
- đầu payload là bảng text với count = 79 chuỗi.

Hai chuỗi gây treo nằm trong chính bảng text 79 chuỗi này:

- index 36, PRGPACK offset `0xDDD68` (908648), raw sector 3122: `ゲームをはじめるよ`.
- index 37, PRGPACK offset `0xDDD7C` (908668), raw sector 3122: `データがないわよ`.

Một patch PRGPACK khác từng chạy được (`やるね` → `やるよ` tại offset `0x510`) nằm trong một nested BDP khác, nên giả thuyết mới mạnh hơn là **nested BDP entry 30 hoặc vùng đầu của nó có integrity/validation riêng**, không phải toàn bộ PRGPACK bị khóa.

EDC/ECC raw-sector đã được kiểm tra bằng cách regenerate sector gốc và so byte-for-byte; các sector kiểm tra khớp dữ liệu gốc. Chưa có bằng chứng lỗi ECC/EDC.

## Diagnostic 0.1.8 — NESTED BDP

Mục tiêu là phân biệt:

1. raw sector 3122 có tính chất đặc biệt;
2. toàn bộ nested BDP entry 30 có integrity/checksum/validation;
3. có checksum đơn giản phụ thuộc tổng/xor byte;
4. patcher vẫn hoạt động bình thường ở nested BDP khác.

### Test A — `FIRST_STRING_S3122`

Trong nested entry 30, đổi string index 0:

- `あ` → `い`
- cùng 2 byte Shift-JIS
- PRGPACK offset `0xDDAB4`
- raw sector 3122

### Test B — `SLOT_S3123`

Trong cùng nested entry 30 nhưng sector kế tiếp:

- `ＳＬＯＴをえらんでね` → `ＳＬＯＴをえらんでよ`
- PRGPACK offset `0xDE110`
- raw sector 3123

Nếu A treo nhưng B OK, sector 3122 hoặc phần đầu nested archive là vùng đặc biệt.

Nếu A và B đều treo, khả năng validation áp trên toàn nested entry 30 tăng mạnh.

### Test C — `CONTROL_OTHER_PACK`

Control ở nested BDP khác:

- `やるね` → `やるよ`
- PRGPACK offset `0x510`

Nếu C OK trong khi A/B treo, patcher/ECC vẫn hoạt động và lỗi bị cô lập vào nested entry 30.

### Test D — `BALANCED_SWAP`

Trong nested entry 30:

- `ゲームをはじめるよ` → `ゲームをはじめるね`
- `ＳＬＯＴをえらんでね` → `ＳＬＯＴをえらんでよ`

Việc đổi một `よ→ね` và một `ね→よ` giữ nguyên histogram byte, tổng byte và XOR byte toàn archive. Nếu D bất ngờ chạy trong khi A/B treo, cần điều tra checksum đơn giản kiểu additive/xor. Nếu D vẫn treo, checksum nếu có nhiều khả năng là CRC/hash/position-sensitive hoặc nguyên nhân không phải checksum đơn giản.

## Quy tắc test

- Cold boot game cho từng image.
- Không load save state DuckStation từ image khác.
- Mỗi BAT luôn nhận BIN gốc SHA1 chuẩn.
- Mở đúng `.cue` mới sinh có nhãn diagnostic tương ứng.

## Mục tiêu dài hạn

Sau khi giải quyết được cơ chế ghi dữ liệu ổn định:

1. dump text có cấu trúc;
2. xác định pointer table;
3. xác định font/glyph table;
4. tạo custom encoding cho tiếng Việt;
5. thêm `ă â ê ô ơ ư đ` và các dấu;
6. reinsert text;
7. build patch thay vì phân phối BIN game.

## Trạng thái handoff hiện tại

- Original: OK
- COPY_ONLY: OK
- 0.1.6 A COMBO_RETEST: TREO
- 0.1.6 B PRGPACK_TWO: TREO
- 0.1.6 C SLPS_TWO: OK
- 0.1.6 D COMBO_ALT: OK
- 0.1.7 A A_ONLY_FRESH: TREO
- 0.1.7 B B_ONLY_SAME_SECTOR: TREO
- 0.1.7 C A+B SAME_SECTOR: TREO
- 0.1.7 D A+C ADJACENT: TREO

Tiếp tục bằng diagnostic 0.1.8. Chưa quay lại ASCII/full-width Latin cho tới khi hiểu cơ chế nested BDP entry 30.
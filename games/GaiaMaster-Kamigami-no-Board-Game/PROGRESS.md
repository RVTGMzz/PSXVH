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

- `JP_PRGPACK_ONLY`: chỉ patch `ゲームをはじめるよ` → `ゲームをはじめるね` trong `PRGPACK.BDP`: **OK**.
- `JP_SLPS_ONLY`: chỉ patch `%sの番よ！` → `%sの番だ！` trong `SLPS_020.75`: **OK**.

Mỗi file đều chấp nhận ít nhất một thay đổi Nhật → Nhật cùng độ dài.

## Diagnostic 0.1.6 — KẾT QUẢ

### A. `COMBO_RETEST`

Patch:
- `PRGPACK.BDP` offset `908648`: `ゲームをはじめるよ` → `ゲームをはじめるね`.
- `SLPS_020.75` offset `2768`: `%sの番よ！` → `%sの番だ！`.

**Kết quả: TREO.**

### B. `PRGPACK_TWO_SECTORS`

Patch:
- `PRGPACK.BDP` offset `908648`: `ゲームをはじめるよ` → `ゲームをはじめるね`.
- `PRGPACK.BDP` offset `0x510`: `やるね` → `やるよ`.

**Kết quả: TREO.**

### C. `SLPS_TWO_SECTORS`

Hai patch đều trong `SLPS_020.75`.

**Kết quả: OK.**

### D. `COMBO_ALT`

Patch khác trong `PRGPACK.BDP` + patch khác trong `SLPS_020.75`.

**Kết quả: OK.**

## Suy luận mới sau 0.1.6

Điểm chung duy nhất của hai image bị treo A và B là patch sau:

- File: `PRGPACK.BDP`
- File offset: `908648`
- Raw sector: `3122`
- Text: `ゲームをはじめるよ` → `ゲームをはじめるね`

Tuy nhiên patch này **một mình đã từng chạy OK ở diagnostic 0.1.5**. Vì vậy hiện tượng cần giải thích là:

> patch tại sector 3122 có vẻ chỉ gây treo khi tồn tại thêm ít nhất một thay đổi khác trong image.

Điều này bác bỏ các giả thuyết đơn giản sau:

- không phải mọi multi-sector patch đều lỗi, vì `SLPS_TWO_SECTORS` chạy;
- không phải mọi cross-file patch đều lỗi, vì `COMBO_ALT` chạy;
- không phải cứ sửa `PRGPACK.BDP` là lỗi, vì `JP_PRGPACK_ONLY` và patch PRGPACK trong `COMBO_ALT` chạy.

EDC/ECC raw-sector cũng đã được kiểm tra bằng cách regenerate các sector gốc và so byte-for-byte; các sector kiểm tra khớp dữ liệu ECC/EDC gốc, nên chưa có bằng chứng thuật toán ECC là nguyên nhân.

## Diagnostic 0.1.7 — Trigger sector 3122

Mục tiêu là xác nhận lại patch nghi vấn và phân biệt lỗi theo số thay đổi hay theo ranh giới sector.

### A. `A_ONLY_FRESH`

Chỉ patch đúng offset `908648` trong PRGPACK, build mới hoàn toàn.

### B. `B_ONLY_SAME_SECTOR`

Patch một chuỗi khác nằm cùng raw sector `3122`, offset `908668`:

`データがないわよ` → `データがないわね`.

### C. `A_PLUS_B_SAME_SECTOR`

Hai thay đổi cùng nằm trong **một raw sector 3122**.

Nếu C treo nhưng A/B riêng lẻ chạy, khả năng cao có logic/chunk validation hoặc hành vi parser liên quan số thay đổi trong vùng dữ liệu này, không phải số sector.

### D. `A_PLUS_C_ADJACENT`

Patch A tại sector `3122` + một patch Nhật → Nhật ở sector kế bên `3123`.

Mục tiêu: kiểm tra xem A có trở thành trigger khi image chứa thêm một modified sector gần nó hay không.

## Quy tắc test từ 0.1.7

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
- 0.1.5 JP_PRGPACK_ONLY: OK
- 0.1.5 JP_SLPS_ONLY: OK
- 0.1.6 A COMBO_RETEST: TREO
- 0.1.6 B PRGPACK_TWO: TREO
- 0.1.6 C SLPS_TWO: OK
- 0.1.6 D COMBO_ALT: OK

Tiếp tục bằng diagnostic 0.1.7. Chưa quay lại ASCII/full-width Latin cho tới khi hiểu rõ trigger tại PRGPACK offset 908648 / raw sector 3122.
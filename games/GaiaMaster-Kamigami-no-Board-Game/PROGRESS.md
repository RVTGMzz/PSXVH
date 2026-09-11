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

### 5. Diagnostic 0.1.4 JP_MARKER: treo khi sửa đồng thời hai file

Chỉ thay hai chuỗi Nhật bằng chuỗi Nhật khác, cùng encoding Shift-JIS và cùng chính xác số byte:

- Trong `PRGPACK.BDP`: đổi ký tự cuối của câu bắt đầu game từ `よ` sang `ね`.
- Trong `SLPS_020.75`: đổi `よ` sang `だ` trong chuỗi lượt chơi.

Không dùng Latin, không NUL padding, không thay pointer.

**Kết quả lúc test 0.1.4:** treo khi vào gameplay.

### 6. COPY_ONLY thành công

`TEST_0_COPY_ONLY.bat` chỉ copy BIN, không sửa byte nào.

**Kết quả:** vào gameplay bình thường.

Điều này xác nhận:

- file BIN gốc tốt;
- DuckStation/cấu hình test không phải nguyên nhân;
- thao tác copy file và CUE mới không gây treo;
- treo chỉ xuất hiện ở một số dạng thay đổi dữ liệu game.

### 7. Diagnostic 0.1.5 cô lập từng file: CẢ HAI ĐỀU OK

Đã test riêng từng patch Nhật → Nhật, cùng byte:

#### `JP_PRGPACK_ONLY`

- Chỉ sửa `PRGPACK.BDP`.
- Chỉ thay đúng chuỗi `ゲームをはじめるよ` → `ゲームをはじめるね`.
- Một sector bị thay đổi.

**Kết quả:** vào gameplay bình thường, không crash.

#### `JP_SLPS_ONLY`

- Chỉ sửa `SLPS_020.75`.
- Chỉ thay `%sの番よ！` → `%sの番だ！`.
- Một sector bị thay đổi.

**Kết quả:** vào gameplay bình thường, không crash.

## Kết luận mới nhất

Đây là mốc chẩn đoán rất quan trọng:

- Không thể kết luận `PRGPACK.BDP` tự nó có checksum làm game treo.
- Không thể kết luận `SLPS_020.75` tự nó có integrity check làm game treo.
- Mỗi file đều chấp nhận ít nhất một thay đổi Nhật → Nhật cùng độ dài và vẫn chạy.
- Hiện tượng treo chỉ từng xuất hiện khi **hai thay đổi cùng tồn tại trong một image** ở test 0.1.4.

Do đó giả thuyết cần ưu tiên bây giờ là:

1. lỗi chỉ xảy ra khi patch nhiều sector;
2. lỗi chỉ xảy ra khi patch đồng thời `PRGPACK.BDP` + `SLPS_020.75`;
3. cặp chuỗi cụ thể trong test 0.1.4 có tương tác bất ngờ;
4. hoặc test 0.1.4 đã vô tình mở nhầm/stale image và cần retest với output tên mới.

## Diagnostic 0.1.6 — bước tiếp theo

Bốn test mới được tạo để phân biệt các giả thuyết:

### A. `COMBO_RETEST`

Retest đúng hai patch từng làm 0.1.4 treo, nhưng output tên mới để loại trừ khả năng mở nhầm image cũ.

### B. `PRGPACK_TWO_SECTORS`

Sửa hai sector khác nhau, đều nằm trong `PRGPACK.BDP`.

Mục tiêu: kiểm tra bản thân việc thay nhiều hơn một sector có làm patcher/EDC/ECC có vấn đề hay không.

### C. `SLPS_TWO_SECTORS`

Sửa hai sector khác nhau, đều nằm trong `SLPS_020.75`.

Mục tiêu giống B nhưng cô lập executable.

### D. `COMBO_ALT`

Sửa một chuỗi khác trong `PRGPACK.BDP` + một chuỗi khác trong `SLPS_020.75`.

Mục tiêu: xác định liệu **bất kỳ** combo cross-file nào cũng gây treo, hay chỉ cặp chuỗi cũ.

## Cách đọc kết quả 0.1.6

- Nếu A giờ chạy: rất có thể lần test 0.1.4 đã dùng nhầm/stale file.
- Nếu A treo nhưng B và C chạy: patch nhiều sector tự nó không phải nguyên nhân; tập trung vào tương tác cross-file hoặc cặp chuỗi cụ thể.
- Nếu B hoặc C treo: điều tra raw-sector multi-sector patching/EDC/ECC trước khi làm tiếp text.
- Nếu D cũng treo trong khi B/C chạy: có dấu hiệu bất kỳ image nào cùng sửa cả `PRGPACK` và `SLPS` đều nhạy cảm.
- Nếu D chạy nhưng A treo: cặp chuỗi cụ thể của 0.1.4 hoặc timing/loading của chúng đáng nghi.

## Mục tiêu dài hạn

Sau khi giải quyết được cơ chế ghi dữ liệu ổn định:

1. dump text có cấu trúc;
2. xác định pointer table;
3. xác định font/glyph table;
4. tạo custom encoding cho tiếng Việt;
5. thêm `ă â ê ô ơ ư đ` và các dấu;
6. reinsert text;
7. build patch thay vì phân phối BIN game.

## Lưu ý cho phiên chat sau

Kết quả đã được xác nhận tới 0.1.5:

- Original: OK
- COPY_ONLY: OK
- JP_PRGPACK_ONLY: OK
- JP_SLPS_ONLY: OK
- JP_MARKER 0.1.4 (hai file cùng sửa): TREO theo lần test trước

Không quay lại ASCII/full-width Latin trước khi kết thúc chuỗi diagnostic 0.1.6.

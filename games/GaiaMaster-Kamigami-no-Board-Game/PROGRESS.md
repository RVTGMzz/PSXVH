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

### 5. Diagnostic 0.1.4 JP_MARKER thất bại

Đây là kết quả quan trọng nhất hiện tại.

Chỉ thay hai chuỗi Nhật bằng chuỗi Nhật khác, cùng encoding Shift-JIS và cùng chính xác số byte:

- Trong `PRGPACK.BDP`: đổi ký tự cuối của câu bắt đầu game từ `よ` sang `ね`.
- Trong `SLPS_020.75`: đổi `よ` sang `だ` trong chuỗi lượt chơi.

Không dùng Latin, không NUL padding, không thay pointer.

**Kết quả:** vẫn treo khi vào gameplay.

### 6. COPY_ONLY thành công

`TEST_0_COPY_ONLY.bat` chỉ copy BIN, không sửa byte nào.

**Kết quả:** vào gameplay bình thường.

Điều này xác nhận:

- file BIN gốc tốt;
- DuckStation/cấu hình test không phải nguyên nhân;
- thao tác copy file và CUE mới không gây treo;
- treo chỉ xuất hiện khi dữ liệu game thực sự bị sửa.

## Giả thuyết hiện tại

Không nên tiếp tục sửa text trực tiếp cho tới khi cô lập nguyên nhân. Các khả năng cần kiểm tra:

1. Một trong hai vùng `PRGPACK.BDP` hoặc `SLPS_020.75` có checksum/validation riêng.
2. EDC/ECC sector đang được tái tạo nhưng game còn phụ thuộc dữ liệu subheader hoặc dạng MODE2 cụ thể.
3. Vị trí logical-file mapping/extent đã đúng để đọc text nhưng chưa đủ an toàn để ghi ngược.
4. Game có integrity check đối với executable/data pack.
5. Chỉ một trong hai file bị patch là nguyên nhân treo, nhưng test JP_MARKER 0.1.4 sửa cả hai cùng lúc nên chưa cô lập được.

## Bước tiếp theo bắt buộc

### Test A: JP marker chỉ trong PRGPACK

- Chỉ thay chuỗi Nhật trong `PRGPACK.BDP`.
- Không sửa `SLPS_020.75`.
- Cùng độ dài byte, Shift-JIS Nhật → Nhật.

### Test B: JP marker chỉ trong SLPS

- Chỉ thay chuỗi Nhật trong `SLPS_020.75`.
- Không sửa `PRGPACK.BDP`.
- Cùng độ dài byte, Shift-JIS Nhật → Nhật.

Nếu chỉ một test treo, ta xác định được file nhạy cảm.

Nếu cả hai đều treo, cần dừng patch raw-sector và chuyển sang kiểm tra:

- cách extract/reinsert file theo ISO9660;
- sector Form 1/Form 2 và subheader;
- checksum/integrity riêng của pack/executable;
- debugger PCSX-Redux để xem điểm treo.

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

Đừng quay lại thử ASCII/full-width Latin trước khi giải quyết lỗi treo khi patch Nhật → Nhật. COPY_ONLY đã chứng minh vấn đề nằm ở thay đổi dữ liệu, không phải quá trình copy/build đơn thuần.

# Việt Hóa PS1

Kho lưu trữ quy trình, công cụ chẩn đoán và tiến độ các dự án Việt hóa game PlayStation 1.

Mục tiêu của repo này là giữ lại toàn bộ kiến thức kỹ thuật theo từng game để có thể tiếp tục ở các phiên làm việc sau mà không phải reverse-engineer lại từ đầu.

## Nguyên tắc

- Không lưu ROM/BIN/CUE game gốc hoặc dữ liệu có bản quyền dung lượng lớn.
- Chỉ lưu script, patch, bảng dịch, ghi chú reverse-engineering và tài liệu kiểm thử.
- Mỗi game nằm trong một thư mục riêng dưới `games/`.
- Ghi lại SHA1 của bản game dùng để phát triển để tránh patch nhầm region/version.

## Dự án hiện tại

### Gaia Master: Kamigami no Board Game (Japan)

Thư mục: `games/GaiaMaster-Kamigami-no-Board-Game/`

Trạng thái hiện tại: đang reverse-engineer cơ chế đọc dữ liệu/text. Bản game gốc chạy vào gameplay bình thường; bản COPY_ONLY byte-identical cũng chạy bình thường; nhưng chỉ cần thay 2 chuỗi Shift-JIS tiếng Nhật bằng chuỗi Nhật khác cùng độ dài byte thì game treo khi vào gameplay. Điều này cho thấy vấn đề hiện tại không còn nằm ở BAT/Python hay việc copy BIN, mà liên quan tới cách sector/file nội bộ được sửa hoặc cơ chế kiểm tra/đọc dữ liệu của game.

Xem `PROGRESS.md` trong thư mục game để tiếp tục.

# Gaia Master — Kế hoạch full translation + tiếng Việt có dấu

## Trạng thái đã xác nhận

- Alpha 0.5.1 build thành công trên máy người dùng.
- Người dùng xác nhận text Việt hóa không dấu đã hiển thị trong game.
- Full-width Latin Shift-JIS đang hoạt động.
- Cơ chế checksum nested BDP + top-level PRGPACK và rebuild EDC/ECC đã ổn định.

## Quyết định workflow

Không cần chọn giữa “dịch hoàn chỉnh” và “nghiên cứu dấu”. Hai việc sẽ chạy song song.

### Track A — Full translation

Nguồn dịch nên giữ cả hai dạng:

- `vi_full`: bản tiếng Việt tự nhiên có dấu, dùng làm bản dịch chuẩn.
- `vi_no_accents`: bản fallback không dấu để build/test ngay bằng full-width Latin.

Như vậy toàn bộ nội dung có thể được dịch ngay mà không phải dịch lại sau khi font tiếng Việt có dấu hoàn tất.

### Track B — Font/glyph tiếng Việt

Mục tiêu là tạo custom mapping 2-byte cho các ký tự Việt ngoài Shift-JIS, ưu tiên:

`ă â ê ô ơ ư đ`

và các nguyên âm có dấu thanh cần thiết.

Patcher cuối cùng sẽ encode `vi_full` qua custom map thay vì chỉ chuyển ASCII sang full-width Shift-JIS.

## Phát hiện ban đầu về font

- Scan các TIM chuẩn trong asset chưa thấy một font atlas Shift-JIS rõ ràng.
- Trong executable có trampoline/wrapper BIOS function `B(51h)` (Krom2RawAdd), đây là đầu mối quan trọng để kiểm tra liệu renderer có lấy glyph Shift-JIS từ BIOS ROM hay không.
- Chưa kết luận renderer thực sự gọi wrapper này ở runtime; cần trace/disassembly thêm trước khi chọn cách inject glyph.

## Test font mục tiêu

Khi xác định được đường glyph, test visible menu duy nhất nên hiển thị một chuỗi đủ bộ ký tự, ví dụ:

`TIẾNG VIỆT Ă Â Ê Ô Ơ Ư Đ Ắ Ề Ộ Ớ Ự`

Nếu test này pass, chuyển thẳng sang build full translation có dấu.

## Nguyên tắc

- Không dừng dịch nội dung để chờ font.
- Không bỏ bản dịch có dấu để chỉ giữ bản không dấu.
- Bản không dấu chỉ là fallback kỹ thuật trong giai đoạn font chưa hoàn tất.
- Mục tiêu cuối cùng vẫn là bản Việt hóa có dấu đầy đủ.

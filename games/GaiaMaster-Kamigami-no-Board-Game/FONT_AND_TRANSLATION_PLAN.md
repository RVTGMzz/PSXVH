# Gaia Master — Kế hoạch full translation + tiếng Việt có dấu

Cập nhật sau runtime test Alpha 0.6.1 FRONT.

## Trạng thái encoding đã xác nhận

- Full-width Latin Shift-JIS: **OK runtime**.
- ASCII 1-byte: **FAIL runtime**, hiển thị ký hiệu sai dù checksum/EDC/ECC đúng.
- Vì vậy fallback hiện tại vẫn là full-width Latin không dấu.
- UTF-8 trực tiếp không phải hướng hợp lệ cho engine này.

## Workflow dịch

Master luôn giữ:

- `vi_full`: tiếng Việt tự nhiên có dấu, source-of-truth.
- `vi_game_current`: fallback không dấu để build/test bằng full-width Latin.

Không được bỏ `vi_full`, để khi custom font pass không phải dịch lại toàn bộ.

Master 0.6 hiện có **596 vị trí**.

## Runtime hiện tại

- Alpha 0.5.1: user xác nhận bản dịch chạy.
- Alpha 0.6: 366 patch, local verify OK.
- Alpha 0.6.1 FRONT: 397 patch, user xác nhận nhiều text đầu game đã Việt hóa nhưng vẫn còn nhiều Nhật và có màn mixed Nhật/Việt do fragment chưa phủ hết.

## Font/glyph tiếng Việt — ưu tiên số 1 tiếp theo

User đã đồng ý test tiếng Việt có dấu ngay bước tiếp theo, trước khi tiếp tục đổ thêm quá nhiều fallback không dấu.

### Không làm

- không nhét UTF-8 trực tiếp;
- không test ở gameplay sâu;
- không làm từng ký tự rời nếu có thể tránh.

### Visible test mục tiêu

Đặt ngay intro/main menu/character-select:

```text
TIẾNG VIỆT
Ă Â Ê Ô Ơ Ư Đ
Á À Ả Ã Ạ
Ắ Ằ Ẳ Ẵ Ặ
Ế Ề Ể Ễ Ệ
Ớ Ờ Ở Ỡ Ợ
Ứ Ừ Ử Ữ Ự
```

Nếu pass thì chuyển builder sang custom encoder cho `vi_full`.

## Đầu mối kỹ thuật

- Scan TIM chuẩn chưa tìm được font atlas Shift-JIS rõ ràng.
- Executable có wrapper/trampoline liên quan BIOS `B(51h) Krom2RawAdd`.
- Đây là đầu mối cần trace để xác định game dùng BIOS Kanji/font ROM hay renderer/font riêng.

### Nếu dùng BIOS font path

- tìm các mã Shift-JIS 2-byte không dùng trong game;
- hook/remap glyph fetch;
- inject bitmap glyph Việt vào buffer/cache của renderer;
- tạo custom encoder từ Unicode Việt -> mã 2-byte giả lập.

### Nếu dùng custom atlas

- locate atlas + glyph index table;
- chiếm các slot glyph Nhật ít/không dùng;
- thay bitmap bằng `ă â ê ô ơ ư đ` + tổ hợp dấu cần thiết;
- map custom code 2-byte -> slot mới.

## Sau khi font test pass

1. builder encode `vi_full` có dấu;
2. dọn sạch intro mixed Nhật/Việt;
3. patch graphic main menu/Character Select title;
4. tiếp tục full translation;
5. reverse/repack string table cho 230 dòng pending vì slot ngắn.

## Nguyên tắc UX test

Mọi font diagnostic mới phải có kết quả nhìn thấy **ngay đầu game** để user không phải đi sâu gameplay.

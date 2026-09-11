# Gaia Master — trạng thái mới nhất

Cập nhật 2026-09-11.

## Kết quả diagnostic 0.1.8

- `FIRST_STRING_S3122`: TREO
- `SLOT_S3123`: TREO
- `CONTROL_OTHER_PACK`: OK
- `BALANCED_SWAP`: OK

## Phát hiện checksum nested BDP

Nested BDP chứa bảng text gameplay có checksum 32-bit tại offset `+0x04`.

Công thức đã khớp chính xác dữ liệu gốc:

```text
sum16 = sum(all bytes except checksum field +0x04..+0x07) & 0xFFFF
checksum = ((~sum16 & 0xFFFF) << 16) | sum16
```

Điều này giải thích vì sao balanced swap chạy: tổng byte không đổi nên checksum cũ vẫn hợp lệ.

## Kết quả diagnostic 0.1.9

User test:

- A `FIX_A_CHECKSUM`: OK
- B `FIX_SLOT_CHECKSUM`: OK
- C `FIX_FIRST_CHECKSUM`: OK
- D `FULLWIDTH_BATDAU_CHECKSUM`: OK
- Không quan sát thấy `BATDAU!!!` trên màn hình do vị trí text khó bắt gặp.

Kết luận: cơ chế patch + cập nhật checksum BDP + regenerate PS1 EDC/ECC đã hoạt động ổn định ở vùng nested BDP này.

## Visible menu test 0.2.0

Tạo prototype patch 3 chuỗi ở pre-game setup / character-select để kiểm tra renderer Latin full-width ở vị trí dễ quan sát.

Patcher Python được test trực tiếp với BIN gốc SHA1 `f4d5298583c90d89c4b7e51d2dde160ee07f2aec` và build thành công.

Tuy nhiên trên máy user, file BAT của gói 0.2.0 mở rồi đóng ngay trước khi user đọc được lỗi.

## 0.2.1 FIXED launcher

Đã đổi sang launcher BAT ASCII-only không BOM:

- `BUILD_VISIBLE_MENU_TEST_FIXED.bat` mở một cửa sổ `cmd /k` riêng nên không tự đóng.
- `BUILD_WORKER.bat` tự phát hiện Python và ghi `build_log.txt`.
- `KEO_BIN_VAO_DAY.bat` hỗ trợ drag-drop BIN.

Patcher Python giữ nguyên vì đã được xác nhận build thành công trong môi trường kiểm thử.

## Bước kế tiếp

1. User test build 0.2.1 FIXED.
2. Nếu build được, kiểm tra text ở màn setup/chọn nhân vật có hiển thị Latin full-width hay không.
3. Nếu renderer hiển thị được, bắt đầu prototype Việt hóa UI/menu không dấu.
4. Sau đó mới reverse font/glyph để thêm tiếng Việt có dấu.

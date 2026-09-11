# Gaia Master — Worklog 0.6

## Sau Alpha 0.5.1

Người dùng đã xác nhận Alpha 0.5.1 build được và phần Việt hóa đã hiển thị trong game.

## Master translation 0.6

Đã mở rộng workflow dịch lên **596 vị trí text**:

- 203 vị trí kế thừa từ Alpha 0.5.
- 393 vị trí mới đã được dịch và đưa vào master 0.6.
- Master lưu song song:
  - Japanese gốc.
  - `vi_full`: bản dịch tiếng Việt có dấu dùng làm nguồn chính.
  - `vi_game_current`: fallback hiện tại dùng cho game trong khi font tiếng Việt có dấu chưa hoàn tất.

Nhóm text mới gồm nhiều phần gameplay quan trọng như:

- tên vũ khí / item / event card;
- ô đặc biệt;
- thuế, mua bán đất, thế chấp;
- xây / phá symbol;
- route, warp, battle;
- thông báo nhận tiền / mất tiền / nhận thẻ;
- nhiều câu thoại và hướng dẫn gameplay trong `PRGPACK.BDP`.

## ASCII Capacity Test 0.2.2

Đây là test kỹ thuật quan trọng trước khi build batch lớn tiếp theo.

Trước đây ASCII 1-byte từng được thử khi chưa biết checksum BDP nên game treo. Vì vậy chưa có bằng chứng renderer không hỗ trợ ASCII.

Sau khi checksum BDP đã reverse xong, test 0.2.2 đổi ba dòng menu dễ nhìn thành ASCII 1-byte:

- `XAC NHAN CAI DAT?`
- `CHON NHAN VAT`
- `NHAN NUT O`

Patcher test đã được build nội bộ thành công trên BIN SHA1 chuẩn:

- patched locations: 3
- touched nested BDP entry: 29
- changed raw sectors: 3
- output SHA1: `d5c24566e7eaa4183f806d0c34071aaab8f48e3f`

### Vì sao test này đáng làm

Full-width Latin tốn 2 byte / ký tự, tương đương chữ Nhật. ASCII chỉ tốn 1 byte / ký tự.

Nếu ASCII render đúng sau khi checksum đã được sửa, dung lượng câu Việt gần như tăng gấp đôi. Khi đó bản full translation có thể tự nhiên hơn rất nhiều và ít phải rút gọn.

Nếu ASCII lỗi hiển thị, tiếp tục dùng full-width Latin và nghiên cứu repack/pointer table để nới độ dài.

## Font tiếng Việt có dấu

Vẫn giữ song song nhánh nghiên cứu custom glyph/font. `vi_full` có dấu đã được lưu từ bây giờ để sau khi font pass không phải dịch lại nội dung.

## Trạng thái tiếp theo

- Chờ kết quả duy nhất của ASCII 0.2.2: `ASCII HIEN DUNG` hoặc `ASCII LOI`.
- Sau kết quả này, build Alpha 0.6/0.7 theo encoding phù hợp và tiếp tục mở rộng translation master thay vì quay lại diagnostic nhỏ lẻ.

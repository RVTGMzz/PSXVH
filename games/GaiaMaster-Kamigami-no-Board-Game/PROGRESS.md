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
- Tổng dump ứng viên đã từng thu được khoảng 2.282 chuỗi.

### 3. Alpha 0.1 thất bại

Thử thay text Nhật bằng ASCII và padding NUL. Game vẫn qua intro/chọn nhân vật nhưng treo khi chuyển vào gameplay.

### 4. Diagnostic 0.1.3 SAFE_SJIS thất bại

Thử dùng Latin full-width trong Shift-JIS, giữ độ dài chuỗi. Game vẫn treo khi load gameplay.

### 5. COPY_ONLY

Chỉ copy BIN, không sửa byte nào.

**Kết quả: OK.**

Điều này xác nhận BIN gốc, CUE mới và thao tác copy không phải nguyên nhân.

## Diagnostic 0.1.6 — kết quả

- A `COMBO_RETEST`: **TREO**
- B `PRGPACK_TWO_SECTORS`: **TREO**
- C `SLPS_TWO_SECTORS`: **OK**
- D `COMBO_ALT`: **OK**

Kết luận: không phải mọi multi-sector patch đều lỗi, không phải mọi cross-file patch đều lỗi, và không phải cứ sửa PRGPACK là lỗi.

## Diagnostic 0.1.7 — kết quả

- A `A_ONLY_FRESH`: **TREO**
- B `B_ONLY_SAME_SECTOR`: **TREO**
- C `A_PLUS_B_SAME_SECTOR`: **TREO**
- D `A_PLUS_C_ADJACENT`: **TREO**

Vùng bị cô lập nằm trong nested BDP tại `PRGPACK.BDP` offset `0xDDA98`.

## Cấu trúc BDP đã reverse được

Các BDP quan sát được có dạng:

- dword `+0x00`: magic `0x000010F0`
- dword `+0x04`: checksum 32-bit
- dword `+0x08`: kích thước TOC, theo mẫu `8 + count * 8`
- dword `+0x0C`: count
- tiếp theo là các descriptor 8 byte

Nested BDP chứa bảng text gameplay đang nghiên cứu:

- bắt đầu tại PRGPACK offset `0xDDA98`
- kích thước block: `0x26BC8`
- checksum gốc: `0x9BC0643F`
- count = 1
- bảng text đầu payload có 79 chuỗi

Một số chuỗi quan trọng:

- `0xDDD68`: `ゲームをはじめるよ`
- `0xDDD7C`: `データがないわよ`
- `0xDE110`: `ＳＬＯＴをえらんでね`

## Diagnostic 0.1.8 — kết quả

- A `FIRST_STRING_S3122`: **TREO**
- B `SLOT_S3123`: **TREO**
- C `CONTROL_OTHER_PACK`: **OK**
- D `BALANCED_SWAP`: **OK**

### Ý nghĩa

A và B cho thấy thay đổi bất kỳ trong nested BDP mục tiêu đều có thể làm game treo, kể cả khác sector.

C xác nhận patcher raw-sector và EDC/ECC vẫn hoạt động ở BDP khác.

D là phát hiện quyết định: đổi một `よ→ね` và một `ね→よ` trong cùng nested BDP, tức tổng byte không đổi, thì game chạy bình thường.

## Đã reverse được checksum BDP

Với nested BDP mục tiêu, trường 32-bit tại `+0x04` là checksum additive.

Công thức khớp **chính xác** dữ liệu gốc:

```text
sum16 = sum(tất cả byte của BDP, bỏ qua 4 byte checksum tại +0x04..+0x07) & 0xFFFF
checksum = ((~sum16 & 0xFFFF) << 16) | sum16
```

Với block gốc:

```text
sum16    = 0x643F
~sum16   = 0x9BC0
checksum = 0x9BC0643F
```

Đã kiểm tra thêm trên nhiều BDP `count=1` khác trong `PRGPACK.BDP`: low 16-bit của checksum luôn bằng byte-sum modulo 65536, high 16-bit luôn là one's complement của low 16-bit.

Điều này giải thích hoàn toàn kết quả `BALANCED_SWAP`: tổng byte không đổi nên checksum cũ vẫn hợp lệ.

## Diagnostic 0.1.9 — kết quả hiện có

Patcher 0.1.9 có khả năng:

1. patch text trong nested BDP mục tiêu;
2. tự tính lại checksum BDP;
3. ghi checksum mới vào header;
4. regenerate EDC/ECC cho mọi raw sector bị thay đổi.

### Kết quả đã xác nhận

- A `FIX_A_CHECKSUM`: **OK**
- B `FIX_SLOT_CHECKSUM`: **OK**

Đây là bằng chứng thực nghiệm rất mạnh rằng checksum BDP chính là nguyên nhân khiến các bản patch trước treo khi vào gameplay.

### Chưa xác nhận rõ từ lần test hiện tại

Tin nhắn kết quả gần nhất chỉ xác nhận chắc A và B. Các dòng C, D và trạng thái hiển thị `BATDAU!!!` vẫn để nguyên lựa chọn mẫu nên chưa được coi là kết quả hợp lệ.

Các test còn cần chốt:

- C `FIX_FIRST_CHECKSUM`: `OK` hoặc `TREO`
- D `FULLWIDTH_BATDAU_CHECKSUM`: `OK` hoặc `TREO`
- Nếu D OK: có nhìn thấy `ＢＡＴＤＡＵ！！！` trong game hay không

### Ý nghĩa nếu C/D đều OK

- cơ chế sửa checksum đã được xác nhận đủ mạnh để dùng làm nền cho patcher thật;
- nếu D hiển thị được Latin full-width, renderer hỗ trợ bộ ký tự đó;
- bước sau có thể chuyển từ diagnostic sang prototype Việt hóa menu/gameplay có kiểm soát.

## Quy tắc test

- Cold boot cho từng image.
- Không load save state từ image khác.
- Mỗi BAT dùng BIN gốc SHA1 chuẩn.
- Mở đúng `.cue` mới sinh.

## Mục tiêu dài hạn

1. dump text có cấu trúc;
2. xác định pointer table;
3. xác định font/glyph table;
4. tạo custom encoding cho tiếng Việt;
5. thêm `ă â ê ô ơ ư đ` và các dấu;
6. reinsert text;
7. build patch thay vì phân phối BIN game.

## Trạng thái handoff hiện tại

- Original: **OK**
- COPY_ONLY: **OK**
- 0.1.6 A: **TREO**
- 0.1.6 B: **TREO**
- 0.1.6 C: **OK**
- 0.1.6 D: **OK**
- 0.1.7 A/B/C/D: **TREO**
- 0.1.8 A: **TREO**
- 0.1.8 B: **TREO**
- 0.1.8 C: **OK**
- 0.1.8 D: **OK**
- Checksum BDP: **đã reverse được**
- 0.1.9 A `FIX_A_CHECKSUM`: **OK**
- 0.1.9 B `FIX_SLOT_CHECKSUM`: **OK**
- 0.1.9 C/D và hiển thị `BATDAU!!!`: **đang chờ xác nhận rõ**

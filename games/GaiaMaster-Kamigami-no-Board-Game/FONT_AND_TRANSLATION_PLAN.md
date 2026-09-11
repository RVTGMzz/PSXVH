# Gaia Master — Kế hoạch full translation + tiếng Việt có dấu

Cập nhật sau runtime test **Font Isolation 0.6.2.6**.

## Trạng thái encoding đã xác nhận

- Full-width Latin Shift-JIS: **OK runtime**.
- ASCII 1-byte: **FAIL runtime**, hiển thị ký hiệu sai dù checksum/EDC/ECC đúng.
- UTF-8 trực tiếp: không dùng.
- Fallback hiện tại vẫn là full-width Latin không dấu.

## Workflow dịch

Master luôn giữ:

- `vi_full`: tiếng Việt tự nhiên có dấu, source-of-truth.
- `vi_game_current`: fallback không dấu để build/test bằng full-width Latin.

Master 0.6 hiện có **596 vị trí**. Không bỏ `vi_full`, để khi font dấu hoàn tất không phải dịch lại toàn bộ.

## Runtime hiện tại

- Alpha 0.5.1: user xác nhận bản dịch chạy.
- Alpha 0.6: 366 patch, local verify OK.
- Alpha 0.6.1 FRONT: **397 patch**, runtime user xác nhận nhiều text đầu game đã Việt hóa nhưng còn nhiều Nhật và mixed fragment.

## Font/glyph tiếng Việt — tình trạng mới nhất

### Safe cave đã xác nhận runtime

Code cave cũ `0x6FE10` gây treo ở pass-through test.

Safe cave mới:

```text
SLPS file offset 0x5C0E0 .. 0x5C2B8
VA start 0x8006B8E0
length 472 bytes
```

A2/B2 đều boot, nên vùng này có thể dùng cho probe code ngắn.

### Visible Character Select probe

Dòng chắc chắn nhìn thấy:

```text
PRGPACK 0xBFD2C
キャラクターをえらんでね
```

Text-only probe hiện `TEST亜`, nên vị trí text và mã Shift-JIS `0x889F` được xác nhận runtime.

### Krom2RawAdd không phải đường glyph cần tìm

Đã thử remap `0x889F` (`亜`) thành glyph `Ế` qua:

1. direct call-site `0x26CF4`;
2. direct call-site `0x2CCA0`;
3. global wrapper `Krom2RawAdd` tại `0x80068208` dùng safe cave.

Kết quả:

```text
C1: TEST亜
C2: TEST亜
D1: TEST亜
D2: TEST亜
E1: BOOT + TEST亜
E2: TEST亜
```

=> Character Select **không lấy glyph qua Krom2RawAdd path đã hook**.

### Quyết định

**Dừng hướng Krom wrapper cho Character Select.** Không tiếp tục tạo thêm direct/global hook cùng kiểu này.

Khả năng mạnh hơn hiện tại:

- UI dùng custom font atlas riêng;
- glyph Nhật đã được preload/copy vào RAM/VRAM cache;
- renderer Character Select tra glyph qua table/cache khác.

## Hướng reverse tiếp theo

### Track A — custom atlas/cache

1. xác định asset/RAM/VRAM chứa glyph `亜` đang thấy ở Character Select;
2. tìm glyph dimensions/packing/index;
3. truy ngược renderer hoặc upload path tới atlas/cache;
4. làm **một probe duy nhất**: thay bitmap `亜` thành `Ế`, vẫn giữ text `TEST亜`;
5. nếu runtime hiện `TESTẾ`, mở rộng mapping sang bộ tiếng Việt.

### Track B — full translation vẫn tiếp tục

Không dừng dịch nội dung để chờ font:

- `vi_full` tiếp tục được biên tập có dấu;
- fallback không dấu vẫn dùng khi cần test nội dung;
- 230 dòng vượt slot chờ reverse/repack.

## Khi font test pass

1. tạo custom encoder Unicode Việt -> glyph code/index;
2. builder dùng `vi_full` có dấu;
3. dọn sạch intro mixed Nhật/Việt;
4. patch graphic main menu/Character Select title;
5. tiếp tục full translation;
6. reverse/repack string table cho 230 dòng pending.

## Nguyên tắc test để tiết kiệm thời gian

- không bắt user vào sâu gameplay;
- ưu tiên probe ở intro/main menu/Character Select;
- chạy test có giá trị thông tin cao nhất trước;
- chỉ chạy control test khi kết quả chính bị treo hoặc không phân biệt được nguyên nhân;
- không lặp lại các nhánh Krom wrapper đã bị loại.

# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-12 sau Font Isolation 0.6.2.6**.

## Chốt kỹ thuật

- Checksum BDP đã reverse và verify 60/60 nested + top-level.
- Raw MODE2/Form1 EDC/ECC patch ổn định.
- Full-width Latin Shift-JIS hiển thị đúng.
- ASCII 1-byte hiển thị ký hiệu sai, **đã loại**.
- Alpha 0.5.1 được user xác nhận Việt hóa hiển thị và game chạy.
- Alpha 0.6.1 FRONT hiện là nền runtime ổn định để kế thừa: **397 patch**, output SHA1 `54d2fb026bc3b71c79861e723caffb4114caa34c`.

## Translation master

- 596 vị trí trong workflow.
- Giữ song song `vi_full` có dấu + fallback không dấu.
- 230 dòng đang chờ reverse/repack vì full-width 2-byte vượt slot gốc.

## Font isolation — kết quả mới nhất

### Safe cave

Code cave cũ `0x6FE10` gây treo ở pass-through test. Safe cave mới đã runtime xác nhận boot:

```text
SLPS file offset 0x5C0E0 .. 0x5C2B8
VA start 0x8006B8E0
length 472 bytes
```

### Visible probe

Character Select probe chắc chắn nhìn thấy:

```text
PRGPACK 0xBFD2C
キャラクターをえらんでね
```

Text-only probe hiện đúng `TEST亜`.

### Krom2RawAdd path đã bị loại cho Character Select

Đã thử intercept mã Shift-JIS hợp lệ `0x889F` (`亜`) thành glyph custom `Ế` theo nhiều vị trí:

- C2: direct caller `0x26CF4` -> vẫn `TEST亜`.
- D2: direct caller `0x2CCA0` -> vẫn `TEST亜`.
- E2: global wrapper `Krom2RawAdd` + safe cave -> vẫn `TEST亜`.

Control/pass-through đều boot:

- A2: BOOT
- B2: BOOT
- C1: `TEST亜`
- D1: `TEST亜`
- E1: BOOT + `TEST亜`

Kết luận hiện tại:

> Character Select không lấy glyph `亜` qua wrapper `Krom2RawAdd` mà ta đã hook. Không tiếp tục test thêm các biến thể Krom wrapper tương tự.

## Hướng font tiếp theo

Ưu tiên reverse **custom glyph cache/font atlas** của UI:

1. tìm vùng RAM/VRAM hoặc asset chứa glyph `亜` / bộ font Nhật đang hiển thị ở Character Select;
2. tìm renderer/index table trỏ tới atlas/cache đó;
3. làm đúng một probe: giữ text `TEST亜` nhưng thay bitmap glyph `亜` thành `Ế`;
4. nếu hiện `TESTẾ`, mở rộng thành bảng glyph tiếng Việt có dấu;
5. sau đó chuyển builder sang encode `vi_full`.

## Sau khi font pass

1. dọn intro mixed Nhật/Việt;
2. patch graphic main menu/Character Select title;
3. tiếp tục full translation;
4. reverse/repack 230 dòng pending.

Chi tiết font isolation được lưu riêng trong `FONT_ISOLATION_0.6.2x.md` và checkpoint đầy đủ nằm ở `HANDOFF_CURRENT.md`.

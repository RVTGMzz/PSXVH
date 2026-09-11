# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-11 sau runtime test Alpha 0.6.1 FRONT**.

## Chốt kỹ thuật

- Checksum BDP đã reverse và verify 60/60 nested + top-level.
- Raw MODE2/Form1 EDC/ECC patch ổn định.
- Full-width Latin Shift-JIS hiển thị đúng.
- ASCII 1-byte build được nhưng runtime hiện ký hiệu sai, **đã loại**.
- Alpha 0.5.1 được user xác nhận Việt hóa hiển thị và game chạy.

## Translation master

- 596 vị trí trong workflow.
- Luôn giữ `vi_full` có dấu + fallback runtime không dấu.
- Không dịch lại từ đầu khi font dấu hoàn tất.

## Alpha 0.6

- 366 patch.
- +163 so với Alpha 0.5.
- 230 dòng đã dịch nhưng chưa fit slot full-width, đang chờ repack.
- Local verify output SHA1: `5a12d3209deee065c129945e169e632f4cec9a8e`.

## Alpha 0.6.1 FRONT

Mục tiêu là thấy Việt hóa ngay đầu game.

- thêm 31 patch front-loaded;
- tổng 397 patch;
- changed sectors: 26;
- output SHA1: `54d2fb026bc3b71c79861e723caffb4114caa34c`.

User runtime test:

- nhiều chỗ đầu game đã Việt hóa;
- đa số game vẫn còn Nhật;
- có màn intro bị Nhật + Việt lẫn do một màn ghép nhiều text fragment nhưng mới patch một phần.

## Graphic/menu finding

Các label lớn như `ストーリーモード`, `対戦モード`, `オプション`, `キャラクターセレクト` không xuất hiện như chuỗi Shift-JIS bình thường trong vùng text đã scan. Khả năng cao cần graphic/texture patch riêng.

## Next milestone

**Ưu tiên test tiếng Việt có dấu ngay đầu game.**

Không nhét UTF-8 trực tiếp. Cần trace renderer/glyph path, kiểm tra đầu mối BIOS `Krom2RawAdd`, rồi tạo custom 2-byte glyph mapping hoặc font injection.

Visible test mục tiêu:

```text
TIẾNG VIỆT
Ă Â Ê Ô Ơ Ư Đ
Á À Ả Ã Ạ
Ắ Ằ Ẳ Ẵ Ặ
Ế Ề Ể Ễ Ệ
Ớ Ờ Ở Ỡ Ợ
Ứ Ừ Ử Ữ Ự
```

Sau font test:

1. dọn sạch intro mixed Nhật/Việt;
2. patch graphic main menu/Character Select;
3. tiếp tục full translation;
4. reverse/repack 230 dòng pending.

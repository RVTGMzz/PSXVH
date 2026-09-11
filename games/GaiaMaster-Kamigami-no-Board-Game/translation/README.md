# Gaia Master translation snapshot

Checkpoint hiện tại: **Translation Master 0.6**.

## Nội dung

Master được chia thành 6 file để dễ lưu/đọc trong repo:

- `TRANSLATION_MASTER_0.6_part01.csv`
- `TRANSLATION_MASTER_0.6_part02.csv`
- `TRANSLATION_MASTER_0.6_part03.csv`
- `TRANSLATION_MASTER_0.6_part04.csv`
- `TRANSLATION_MASTER_0.6_part05.csv`
- `TRANSLATION_MASTER_0.6_part06.csv`

Tổng cộng: **596 rows**.

Các cột:

- `file`: file game nguồn (`PRGPACK.BDP` / `SLPS_020.75`)
- `offset_hex`: offset trong file đã extract
- `japanese`: text Nhật gốc
- `vi_full`: bản dịch tiếng Việt chuẩn có dấu, source-of-truth
- `vi_game_current`: fallback không dấu hiện dùng để build bằng full-width Shift-JIS
- `status`: trạng thái workflow
- `note`: ghi chú

## Front demo 0.6.1

`FRONT_DEMO_ADDED_061.csv` chứa 31 patch bổ sung ở intro/setup/character-select để tester thấy Việt hóa ngay đầu game.

## Rebuild patch manifest

Chạy:

```bash
python tools/generate_alpha061_patches.py
```

Script sẽ đọc 6 master parts + `FRONT_DEMO_ADDED_061.csv` và tạo lại `tools/patches_alpha061.json`.

Generator đã được kiểm tra local và tạo **397 patches**, byte-for-byte tương đương manifest Alpha 0.6.1 đã dùng để build runtime test.

Sau đó `tools/build_alpha061_front.py` dùng manifest này để build BIN/CUE từ BIN gốc chuẩn.

## Lưu ý encoding

- full-width Latin CP932: runtime OK
- ASCII 1-byte: runtime FAIL, không dùng
- tiếng Việt có dấu: đang là next milestone, cần custom glyph/font mapping

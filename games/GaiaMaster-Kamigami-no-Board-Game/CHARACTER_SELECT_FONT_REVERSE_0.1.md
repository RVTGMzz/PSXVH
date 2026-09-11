# Gaia Master — Character Select custom glyph cache/font atlas reverse 0.1

## Mục tiêu

Probe visible giữ nguyên text:

```text
TEST亜
```

nhưng thay bitmap/cache/atlas của `亜` (`Shift-JIS 0x889F`) thành glyph chẩn đoán `Ế`.

Expected runtime:

```text
TESTẾ
```

Đây là bước kế tiếp sau Font Isolation 0.6.2.6. Không quay lại hook `Krom2RawAdd`, vì direct caller #1, direct caller #2 và global safe wrapper đều đã không chạm glyph `亜` của Character Select.

## Điểm reverse đã chốt

- Character Select probe: `PRGPACK.BDP + 0xBFD2C`.
- `0x889F` = `亜`.
- Chuyển `0x889F` sang JIS cho atlas-order probe:
  - row `0x30`
  - cell `0x21`
  - linear 94×94 index `1410`
- Safe executable cave cũ vẫn giữ làm thông tin tham chiếu, nhưng task này không cần thêm Krom hook.

## Tooling mới

Đang dùng forensic scanner riêng cho Gaia Master, chạy trên BIN local của người test. Scanner không sửa game.

Scanner làm ba lớp:

1. Bóc `SLPS_020.75` + `PRGPACK.BDP`, parse nested BDP và xác định entry sở hữu offset Character Select.
2. Quét TIM trong SLPS/PRGPACK/nested entries, decode PNG, chấm điểm texture có dáng font atlas và tìm tile gần hình `亜`.
3. Quét raw fixed-stride 1bpp JIS-like atlas ở các layout `16x15/30`, `16x15/32`, `16x16/32`, lấy JIS index 1410 làm tâm contact sheet.

Output chính:

```text
report.json
report.txt
tim/*.png
raw_jis/*.png
```

Scanner tự đóng gói các output forensic thành ZIP và không đưa game BIN/SLPS/PRGPACK vào ZIP.

## Probe builder

Probe builder generic nhận scanner `report.json` và candidate `raw:N` hoặc `tim:N`.

Nó sẽ:

- ưu tiên baseline `Alpha 0.6.1 FRONT` SHA1 `54d2fb026bc3b71c79861e723caffb4114caa34c` để giữ 397 patch hiện tại;
- patch Character Select về `TEST亜`;
- thay đúng candidate glyph bitmap thành glyph chẩn đoán `Ế`;
- rebuild nested/top-level BDP checksum;
- ghi lại MODE2/Form1 sectors và regenerate EDC/ECC;
- xuất BIN + CUE để test ngay ở Character Select.

Clean ROM chỉ được dùng khi chủ động bật `--allow-clean`; không dùng clean ROM làm probe chính vì sẽ mất baseline 397 patch.

## Quy trình test tối ưu

1. Chạy scanner một lần trên BIN Gaia Master local.
2. Đọc `report.json` + contact sheets, chọn candidate có bằng chứng mạnh nhất.
3. Build **một probe chính duy nhất** trên Alpha 0.6.1 FRONT.
4. Vào Character Select.
5. Nếu hiện `TESTẾ`: atlas/cache path PASS, bắt đầu mở rộng Vietnamese glyph table/codepage.
6. Nếu vẫn `TEST亜`: loại candidate đó và dùng candidate tiếp theo theo evidence; không quay lại Krom wrapper.

## Trạng thái hiện tại

Tool scanner và generic atlas probe builder đã được dựng và sanity-test bằng synthetic BDP/TIM/raw-atlas data. Repo không chứa ROM/SLPS/PRGPACK binary, nên offset atlas thật chưa được phép đoán tĩnh. Bước cần dữ liệu tiếp theo là chạy scanner trên BIN local để lấy candidate report thật.

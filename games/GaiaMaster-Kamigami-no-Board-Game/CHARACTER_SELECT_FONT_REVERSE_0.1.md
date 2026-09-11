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

## Scanner 0.1.3 — kết quả thật

User đã chạy scanner trên clean BIN đúng SHA1:

```text
f4d5298583c90d89c4b7e51d2dde160ee07f2aec
```

Embedded files cũng match source-of-truth:

```text
SLPS_020.75  1dfeb6b7cfda59c108dde2dc0b8abda9a40e6ae5
PRGPACK.BDP  a9b195b8ae5d8cad7f4f755daa08337d4671632c
```

Scanner xác nhận Character Select offset:

```text
PRGPACK + 0xBFD2C
=> owner nested entry 29
=> entry29 local +0x580
```

### TIM scan

Chỉ có 3 TIM candidate điểm thấp, đều thuộc `PRGPACK.entry00`, kích thước `36x80 4bpp`. Visual inspection không cho thấy font atlas / glyph sheet đáng tin cậy.

### Raw JIS-like scan

Top candidates tập trung ở:

- `PRGPACK.entry29`
- `PRGPACK.entry33`
- `PRGPACK.entry08`
- `PRGPACK.entry10`
- `SLPS_020.75`

Visual inspection của contact sheets cho thấy các candidate top là structured data/code-like bit patterns, không phải chuỗi glyph Nhật. Không patch `raw:1` hoặc `tim:1` vì hiện không có evidence đủ mạnh và có nguy cơ phá data.

## Kết luận sau scanner

Static flat-atlas hypothesis bị yếu đi đáng kể.

Khả năng mạnh hơn hiện tại:

1. Character Select dựng glyph cache lúc runtime;
2. font/glyph nằm trong sub-BDP/overlay của entry29 thay vì flat JIS-order atlas;
3. renderer lookup qua table/overlay riêng rồi upload glyph/tiles lên VRAM;
4. cache được populate trước khi Character Select draw nên hook Krom trước đó không nhìn thấy code path glyph thực tế.

## Stage 2

Không build probe mù từ scanner 0.1.3.

Bước kế tiếp là reverse trực tiếp:

- `SLPS_020.75`
- `PRGPACK.BDP`
- `PRGPACK_entry29.BDP`
- children của entry29

Một Stage 2 extractor đã được dựng để user chạy trên clean BIN, chỉ trích ~2 MB dữ liệu cần reverse và không sửa game.

Khi nhận `GaiaMaster_FontReverse_STAGE2.zip`, reverse tiếp:

1. parse entry29 recursively;
2. xác định child/overlay chứa local offset `+0x580`;
3. disassemble/search MIPS code/data tables liên quan;
4. lần theo loader/render/VRAM upload path;
5. chỉ khi tìm được bitmap/cache thật của `0x889F`, tạo **một probe duy nhất** `TEST亜 -> TESTẾ`.

## Quy tắc test

- Không quay lại Krom wrapper diagnostics.
- Không patch candidate chỉ vì score scanner cao.
- Không bắt user vào sâu gameplay.
- Chỉ tạo runtime probe sau khi có static evidence đủ mạnh.

# Gaia Master — BDP format notes

Đây là ghi chú reverse-engineering từ `PRGPACK.BDP` của Gaia Master (SLPS-02075).

## Header quan sát được

```text
+0x00  u32  magic = 0x000010F0
+0x04  u32  checksum
+0x08  u32  TOC size / first descriptor value
+0x0C  u32  count
...          descriptor table
```

Mẫu quan sát cho `+0x08`:

```text
TOC_size = 8 + count * 8
```

Ví dụ:

- count 1  -> `0x10`
- count 2  -> `0x18`
- count 5  -> `0x30`
- count 20 -> `0xA8`

## Checksum

Với các BDP `count=1` đã kiểm tra, checksum tại `+0x04` có công thức:

```python
sum16 = sum(all_bytes_except_checksum_field) & 0xFFFF
checksum = ((~sum16 & 0xFFFF) << 16) | sum16
```

Tức:

```text
LOW16  = byte sum modulo 65536
HIGH16 = one's complement của LOW16
```

### Nested BDP chứa bảng gameplay

```text
PRGPACK offset : 0xDDA98
block length   : 0x26BC8
checksum gốc   : 0x9BC0643F
sum16 gốc      : 0x643F
~sum16         : 0x9BC0
```

Kiểm tra:

```text
0x9BC0 << 16 | 0x643F = 0x9BC0643F
```

## Bằng chứng runtime

Diagnostic 0.1.8:

- sửa 1 chuỗi trong block nhưng không sửa checksum -> game treo khi load gameplay;
- sửa chuỗi khác trong cùng block -> vẫn treo;
- sửa BDP khác -> game chạy;
- balanced swap `よ→ね` + `ね→よ`, giữ nguyên tổng byte -> game chạy.

Balanced swap là bằng chứng thực nghiệm mạnh cho checksum additive.

## Khi patch

Thứ tự an toàn:

1. sửa payload;
2. tính lại checksum BDP;
3. ghi checksum mới vào `+0x04`;
4. với BIN MODE2/2352, regenerate EDC/ECC cho mọi sector bị thay đổi;
5. cold boot để test, không dùng save state từ image khác.

## Trạng thái

Công thức checksum đã khớp dữ liệu gốc và giải thích toàn bộ kết quả diagnostic 0.1.8. Diagnostic 0.1.9 đang dùng công thức này để xác nhận runtime sau khi checksum được cập nhật.

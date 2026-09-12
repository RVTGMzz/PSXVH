# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-12 sau runtime 0.6.3.10 và reverse consumer cuối của glyph record**.

## Chốt hiện tại

- Custom Vietnamese atlas path PASS từ 0.6.2.13.
- Native 12x12 bị loại cho production stacked Vietnamese diacritics.
- 0.6.3.7 SOURCE ROW SENTINEL vẫn là bằng chứng sạch nhất: rows10..11 hiện, rows12..15 không hiện đủ.
- 0.6.3.8/0.6.3.9 là diagnostic fail vì chạm sai/global vào sprite-height path.
- 0.6.3.10 dùng **stack metadata thật** tại `sp+18`; runtime **ổn nhưng kết quả target y hệt 0.6.3.7**.

=> **visible sprite height không còn là blocker hàng đầu**.

## Reverse mới sau 0.6.3.10

Caller và draw consumer đã được reverse sâu hơn.

### 1. Copy routine thật sự đọc đủ 12-pixel width

`0x8003C67C` chọn wide path khi metadata width >= 9.
Target custom-atlas có metadata width 12, nên mỗi source row đọc đủ:

```text
6 source bytes -> 8 converted/cache bytes
```

Với height=15:

```text
16 rows -> 128 converted bytes
```

### 2. Final cache upload không hardcode glyph height=12

Cache dùng một page cao hơn nhiều glyph. Flush page tại `0x8003CDE8..0x8003CE24` / cleanup `0x8003DBA4..0x8003DBE0` upload một RECT page, không phải một glyph-RECT 12-row riêng.

### 3. Record byte +7 thật sự đi tới GPU primitive height

Record 16-byte được build quanh `0x8003CC..`.
Consumer cuối tại `0x8003DA48` đọc:

```text
record+7 -> primitive height
```

nên 0.6.3.10 negative cho thấy việc mở height lên 16 không phục hồi rows12..15. Lower-row loss xảy ra trước final primitive sampling hoặc trong cache/VRAM placement.

## CURRENT — 0.6.3.11 RAM TAIL MIRROR

Mục tiêu: hỏi trực tiếp liệu converted RAM rows12..15 có tồn tại ngay sau `0x8003C67C` hay không.

Không dùng late `s0`, không global flag.
Target identity dựa trên **source pointer thật trong caller metadata**:

```text
metadata base = sp+16
source pointer = *(sp+20)
target source = 0x8007ABFC
```

Sau copy, trước allocator advance:

```text
current converted dest = *(s1+100)
rows12..15 = dest+96 .. dest+127
```

0.6.3.11 mirror 32 byte này lên vùng chắc chắn nhìn thấy:

```text
rows8..11 = dest+64 .. dest+95
```

Source sentinel vẫn có rows12..15 = bright white.

### Interpretation

- **Bright 4-row block xuất hiện cao hơn trong glyph** => rows12..15 tồn tại đúng trong converted RAM; loss nằm downstream ở VRAM placement/cache coordinates.
- **Không có bright mirror block** => rows12..15 không tồn tại như expected ngay sau copy, hoặc destination pointer model sai.

Package:

```text
GaiaMaster_FontIsolation_0.6.3.11_RAM_TAIL_MIRROR.zip
```

Launcher:

```text
00_RUN_PROBE_06311.cmd
```

## Do not repeat

- Không quay lại Krom.
- Không polish production stacked accents trong 12x12.
- Không retest 0.6.2.18.
- Không retest 0.6.3.0..0.6.3.10.
- Không patch shared `0x8003CD94..0x8003CDB4` kiểu 0.6.3.1.
- Không persistent/global flag kiểu 0.6.3.6.
- Không force sprite height global kiểu 0.6.3.8.
- Không dùng `s3+2` như glyph metadata.

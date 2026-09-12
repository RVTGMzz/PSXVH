# HANDOFF — Gaia Master PS1 Việt hóa

> Current source-of-truth sau runtime test **0.6.2.16 FULL HEIGHT**, next là **0.6.2.17 FULL HEIGHT AA ACCENT**.

## Source game

- `GaiaMaster - Kamigami no Board Game (Japan).bin`
- MODE2/2352
- serial `SLPS-02075`
- clean BIN SHA1 `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- executable `SLPS_020.75`
- main archive `PRGPACK.BDP`
- stable translation baseline: Alpha 0.6.1 FRONT SHA1 `54d2fb026bc3b71c79861e723caffb4114caa34c`

## BDP / raw sector

```text
magic    +0x00 = 0x000010F0
checksum +0x04
TOC size +0x08
count    +0x0C
descriptor = (offset,size), 8 bytes
```

Checksum:

```text
sum16 = sum(all bytes except +0x04..+0x07) & 0xFFFF
checksum = ((~sum16 & 0xFFFF) << 16) | sum16
```

Verified 60/60 nested BDP + top-level PRGPACK.

Raw disc: MODE2/Form1, user data raw `+24`, 2048 bytes; modified sectors phải regenerate EDC/ECC.

## Translation status

- Alpha 0.5.1: 203 patch, runtime user confirmed OK.
- Master 0.6: 596 rows, `vi_full` là source-of-truth có dấu.
- Alpha 0.6: 366 patch; 230 rows pending vì full-width 2-byte overflow slot.
- Alpha 0.6.1 FRONT: 397 patch, runtime stable.
- vẫn còn mixed JP/VI + graphic text cần xử lý sau font.

## Encoding rules

- Shift-JIS Japanese: OK.
- Full-width Latin CP932: OK.
- ASCII 1-byte: FAIL/mis-render, không dùng làm runtime control text.
- UTF-8 trực tiếp: không dùng.

## Character Select visible probe

```text
PRGPACK.BDP + 0xBFD2C
owner nested BDP = entry 29
local offset = +0x580
```

Probe chuẩn:

```text
ＴＥＳＴ亜
82 73 82 64 82 72 82 73 88 9F
```

## Custom atlas path đã reverse

Character Select đi custom mapping/atlas branch của renderer `0x8003C210`.

```text
atlas RAM   = 0x8006BCEC
mapping RAM = 0x8007AECC
atlas file  = SLPS + 0x5C4EC
mapping file= SLPS + 0x6B6CC
```

Mapping confirmed:

```text
0x8273 Ｔ -> glyph 481
0x8264 Ｅ -> glyph 466
0x8272 Ｓ -> glyph 480
0x889F 亜 -> glyph 0
```

Atlas:

```text
860 glyphs
72 bytes/glyph
12x12 pixels
4bpp
LOW nibble first
```

`Ｅ` native = glyph index 466, dùng làm style reference.

## Probe history quan trọng

### Krom path rejected
C2/D2/E2 không chạm Character Select. Không quay lại Krom wrapper.

### 0.6.2.13 STATIC SLOT / NO HOOK — BREAKTHROUGH PASS

- không hook renderer;
- không code cave;
- giữ text `ＴＥＳＴ亜`;
- thay trực tiếp static atlas glyph #0 (`亜`) bằng glyph Việt dựng từ `Ｅ` gốc.

Runtime:

- text khác bình thường;
- `ＴＥＳＴ` đúng;
- glyph cuối gần như `Ế`;
- màu/style gần font gốc.

=> **Vietnamese glyph pipeline PASS**.

### 0.6.2.14 / 0.6.2.15 — compact body rejected
Nén thân E còn 9 hàng để lấy thêm headroom. Runtime cho thấy chữ có dấu nhìn nhỏ hơn chữ thường. User không chấp nhận cho production.

=> Production rule: không thu nhỏ body native.

### 0.6.2.16 FULL HEIGHT — runtime result

Giữ body `Ｅ` nguyên vẹn:

```text
row 0..1 = dấu
row 2..11 = native E body byte-for-byte
```

Runtime screenshot:

- thân E đúng size/baseline/style;
- phần dấu hiện nhiều hơn;
- nhưng tổng thể vẫn gần `É`, circumflex chưa đọc tự nhiên thành `^`;
- user xác nhận kích thước body full-height là đúng hướng.

=> Blocker hiện tại chỉ còn **accent geometry trong 2 blank rows**.

## NEXT — 0.6.2.17 FULL HEIGHT AA ACCENT

Không thay renderer/mapping/atlas strategy.

Giữ body `Ｅ` 100% byte-for-byte.

Thiết kế lại 2 hàng dấu:

- row 0: bright circumflex peak + acute upper pixel;
- row 1: darker/anti-aliased circumflex shoulders + acute lower pixel;
- dùng chính palette indices native `1/4/7` của glyph `Ｅ` để dấu không hòa vào top bar;
- body row 2..11 không đổi.

Expected:

```text
ＴＥＳＴẾ
```

Mục tiêu là full-height, không thu nhỏ thân chữ, và mắt đọc rõ `^ + ´`.

## Sau khi geometry PASS

1. khóa template full-height cho A/E/O/U family;
2. build full Vietnamese glyph inventory;
3. thiết kế compact runtime codepage/mapping;
4. chuyển `vi_full` sang encoder có dấu;
5. giải 230 pending overflow rows;
6. dọn mixed JP/VI;
7. patch graphic menus/title;
8. full runtime QA + reproducible final build.

## Windows builder pitfalls

- tránh parse `(Japan).bin` trong parenthesized BAT block;
- launcher ASCII + CRLF;
- máy test hiện tại có `C:\Python312\python.exe`;
- JSON Nhật: UTF-8 explicit hoặc `ensure_ascii=True`.

## User testing preference

- probe visible ở Character Select;
- không bắt đi sâu gameplay;
- mỗi vòng chỉ một thay đổi có giá trị thông tin cao;
- không quay lại nhánh kỹ thuật đã loại.

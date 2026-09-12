# HANDOFF — Gaia Master PS1 Việt hóa

> Current source-of-truth sau Font Isolation **0.6.2.14**, đang test **0.6.2.15 ACCENT SHAPE**.

## Source game

- `GaiaMaster - Kamigami no Board Game (Japan).bin`
- MODE2/2352
- serial `SLPS-02075`
- clean BIN SHA1 `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- executable `SLPS_020.75`
- main archive `PRGPACK.BDP`
- stable translation baseline: Alpha 0.6.1 FRONT SHA1 `54d2fb026bc3b71c79861e723caffb4114caa34c`

## BDP / raw sector

BDP:

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

## Encoding rules đã chốt

- Shift-JIS Japanese: OK.
- Full-width Latin CP932: OK.
- ASCII 1-byte: FAIL/mis-render trong Japanese renderer, **không dùng làm control/runtime text**.
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

## Krom path đã loại

Các probe C2/D2/E2 đều cho `TEST亜`, nên Character Select không lấy glyph qua Krom2RawAdd path đã hook. Không quay lại direct/global Krom hooks.

## Stage 2 breakthrough — custom atlas thật

Character Select đi custom mapping/atlas branch quanh `0x8003C4DC` trong renderer `0x8003C210`.

Default pointers:

```text
atlas RAM   = 0x8006BCEC
mapping RAM = 0x8007AECC
atlas file  = SLPS + 0x5C4EC
mapping file= SLPS + 0x6B6CC
```

Final glyph pointer calculation:

```text
mapping code -> glyph index
glyph byte offset = index * 72
final pointer = atlas base + offset
```

Mapping confirmed:

```text
0x8273 Ｔ -> glyph 481
0x8264 Ｅ -> glyph 466
0x8272 Ｓ -> glyph 480
0x889F 亜 -> glyph 0
```

## Atlas format — FINAL CURRENT FINDING

```text
860 glyphs
72 bytes/glyph
12x12 pixels
4bpp
LOW nibble first
```

Full-width `Ｅ` = glyph index 466, dùng làm style/palette reference.

## Probe history mới nhất

### 0.6.2.7
Static glyph #0 replacement + ASCII control -> `É É É É É`. Chứng minh atlas injection có runtime effect, nhưng ASCII control sai.

### 0.6.2.10
Early mapping hook -> toàn text collapse về cùng glyph. Reject strategy.

### 0.6.2.11
Post-lookup hook -> `ＴＥＳＴ?`. Isolation target PASS, nhưng cave glyph strategy chưa sạch.

### 0.6.2.12
Đổi nibble assumption -> vẫn `ＴＥＳＴ?`; dừng đoán cave packing.

### 0.6.2.13 STATIC SLOT / NO HOOK — BREAKTHROUGH PASS

Không hook renderer, không code cave.

- giữ text `ＴＥＳＴ亜`;
- thay trực tiếp static atlas glyph #0 (`亜`) bằng glyph Việt dựng từ `Ｅ` gốc.

Runtime:

- text khác bình thường;
- `ＴＥＳＴ` đúng;
- glyph cuối hiện gần như `Ế`;
- màu/style gần font gốc.

=> **Vietnamese glyph pipeline PASS**.

### 0.6.2.14 COMPACT FIT — result

Thử chừa row 0 trống, hạ dấu sắc + mũ và nén thân E xuống 9 hàng. Runtime screenshot vẫn nhìn gần như `É`.

Phân tích lại bitmap + screenshot cho thấy vấn đề chính không còn là top clipping. Circumflex của 0.6.2.14 chỉ cao **1 row**, nên khi game render/scale nó nhập thị giác với top bar của E. Dấu sắc vẫn thấy, vì vậy ký tự trông như `É`.

=> blocker hiện tại là **glyph accent geometry**, không phải renderer/mapping/atlas.

## 0.6.2.15 ACCENT SHAPE — task hiện tại

Không thay renderer/mapping.

Giữ static-slot strategy đã PASS và chỉ làm mũ rõ hơn:

```text
row 0 = dấu sắc
row 1 = đỉnh mũ
row 2 = hai vai mũ
row 3..11 = thân E native compact 9 hàng
```

Mũ giờ có 2 tầng pixel thật sự để tạo hình `^`, tách khỏi thanh ngang trên của E.

Expected runtime:

```text
ＴＥＳＴẾ
```

## Sau 0.6.2.15 PASS

1. khóa template glyph 12x12;
2. build full Vietnamese glyph inventory;
3. thiết kế compact runtime codepage/mapping;
4. chuyển `vi_full` sang encoder có dấu;
5. giải 230 pending overflow rows;
6. dọn mixed JP/VI;
7. patch graphic menu/title text;
8. full runtime QA + reproducible final patch/build.

## Windows builder pitfalls

- Tránh parse `(Japan).bin` trong parenthesized BAT block.
- Launcher nên ASCII + CRLF, gọi trực tiếp `C:\Python312\python.exe` trên máy test hiện tại.
- JSON tiếng Nhật: `ensure_ascii=True` hoặc UTF-8 explicit.

## User testing preference

- test visible ở intro/main menu/Character Select;
- không bắt đi sâu gameplay khi chưa cần;
- một probe có giá trị thông tin cao mỗi vòng;
- khi font pipeline đã pass, ưu tiên tiến thẳng sang production glyph/codepage thay vì lặp diagnostic không cần thiết.

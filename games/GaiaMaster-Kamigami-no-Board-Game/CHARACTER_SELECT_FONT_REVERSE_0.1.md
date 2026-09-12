# Gaia Master — Character Select custom glyph cache/font atlas reverse 0.1

## Mục tiêu

Visible probe chuẩn dùng full-width CP932:

```text
ＴＥＳＴ亜
```

Mục tiêu cuối:

```text
ＴＥＳＴẾ
```

Không quay lại hook `Krom2RawAdd`: direct caller #1, direct caller #2 và global safe wrapper đều đã không chạm glyph Character Select.

## Source-of-truth

- clean BIN SHA1: `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- Alpha 0.6.1 FRONT SHA1: `54d2fb026bc3b71c79861e723caffb4114caa34c`
- `SLPS_020.75` SHA1: `1dfeb6b7cfda59c108dde2dc0b8abda9a40e6ae5`
- `PRGPACK.BDP` SHA1: `a9b195b8ae5d8cad7f4f755daa08337d4671632c`
- Character Select text: `PRGPACK + 0xBFD2C`
- owner nested BDP: entry 29
- local offset: `+0x580`

## Stage 2 breakthrough — custom atlas path

Renderer function around `0x8003C210` có hai nguồn glyph.

Character Select dùng custom mapping/atlas branch quanh:

```text
0x8003C4DC sll  v0,v0,1
0x8003C4E0 lw   v1,0x51C(gp)   # mapping base
0x8003C4E4 lw   a0,0x518(gp)   # atlas base
0x8003C4E8 addu v0,v0,v1
0x8003C4EC lhu  v1,0(v0)       # glyph index
0x8003C4F8 sll  v0,v1,3
0x8003C4FC addu v0,v0,v1
0x8003C500 sll  a1,v0,3        # glyph_index * 72
0x8003C504 addu a0,a0,a1       # final glyph pointer
```

Default pointers:

```text
atlas RAM   = 0x8006BCEC
mapping RAM = 0x8007AECC
atlas file  = SLPS + 0x5C4EC
mapping file= SLPS + 0x6B6CC
```

Mapping đã xác nhận:

```text
0x8273 Ｔ -> glyph 481
0x8264 Ｅ -> glyph 466
0x8272 Ｓ -> glyph 480
0x889F 亜 -> glyph 0
```

## Atlas format — final corrected finding

```text
860 glyphs
72 bytes/glyph
12x12 pixels
4bpp
LOW nibble first
```

`Ｅ` full-width là glyph 466 và được dùng làm style/palette reference.

## Probe timeline

### 0.6.2.7
Thay static glyph #0, nhưng control dùng ASCII `TEST亜` -> nhiều ký tự thành `É`. Điều này vẫn chứng minh atlas injection tác động runtime, nhưng ASCII 1-byte không phải control hợp lệ.

### 0.6.2.10
Hook sớm ở mapping branch làm nhiều/all text collapse thành một glyph. Strategy bị loại.

### 0.6.2.11
Post-lookup hook giữ text thường bình thường và chỉ đổi ký tự cuối:

```text
ＴＥＳＴ?
```

=> target isolation PASS, nhưng custom cave glyph pointer không phải strategy tối ưu.

### 0.6.2.12
Đổi nibble order nhưng runtime vẫn `ＴＥＳＴ?` -> loại hướng tiếp tục đoán cave glyph packing.

### 0.6.2.13 — STATIC SLOT / NO HOOK — PASS

Bỏ hoàn toàn renderer hook/code cave/pointer override.

Control:

```text
ＴＥＳＴ亜
```

Thay trực tiếp static atlas glyph #0 (`亜`) bằng glyph `Ế` dựng từ full-width `Ｅ` gốc.

Runtime user result:

- text khác bình thường;
- bốn chữ `ＴＥＳＴ` đúng;
- glyph cuối hiện gần như `Ế`;
- màu/style thân glyph gần khớp font gốc.

=> static custom atlas path đã PASS runtime.

### 0.6.2.14 — COMPACT FIT — runtime result

0.6.2.14 hạ dấu xuống và nén thân `Ｅ` để chừa headroom, nhưng runtime screenshot **vẫn nhìn gần như `É`**.

So sánh bitmap offline với screenshot cho thấy chẩn đoán cũ “bị clip trần” chưa chính xác. Nguyên nhân chính là:

- circumflex của 0.6.2.14 chỉ cao **1 hàng pixel**;
- sau khi game scale/render, hàng mũ này nhập thị giác vào thanh ngang trên của `E`;
- dấu sắc vẫn thấy, nên glyph trông giống `É` thay vì `Ế`.

Đây là lỗi **glyph design**, không còn là lỗi renderer/mapping/atlas.

## 0.6.2.15 — ACCENT SHAPE — current probe

Giữ nguyên toàn bộ strategy đã PASS:

- no renderer hook;
- no Krom hook;
- no code cave;
- static atlas glyph #0 replacement;
- LOW-nibble-first 12x12 4bpp;
- thân `Ｅ` native compact 9 hàng;
- palette/shadow lấy từ font gốc.

Chỉ thay geometry dấu:

```text
row 0 = dấu sắc
row 1 = đỉnh mũ
row 2 = hai vai mũ
row 3..11 = thân E compact từ font gốc
```

Mục tiêu là tạo mũ `^` thật sự có **2 tầng**, tách rõ khỏi top bar của E.

Expected runtime:

```text
ＴＥＳＴẾ
```

## Sau khi 0.6.2.15 pass

1. khóa template 12x12 cho nhóm nguyên âm có dấu;
2. build full Vietnamese glyph inventory;
3. chọn/thiết kế compact codepage;
4. encoder `vi_full` có dấu;
5. xử lý 230 dòng overflow/repack;
6. graphic text + mixed JP/VI cleanup;
7. QA full ROM.

# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-12 sau reverse dataflow quanh 0x8003CCA0..0x8003CD20**.

## Chốt hiện tại

- Custom Vietnamese atlas path PASS từ 0.6.2.13.
- Native 12x12 bị loại cho production stacked Vietnamese diacritics.
- 0.6.3.7 SOURCE ROW SENTINEL là probe sạch nhất về lower rows: rows10..11 hiện, rows12..15 không hiện đủ.
- 0.6.3.8 global force-height16 phá layout.
- 0.6.3.9 `lhu 2(s3)` phá layout vì **s3 không phải metadata pointer** ở stage đó.

## Reverse breakthrough

Full caller reverse chứng minh:

```text
s5 = current 16-byte output/cache record base
s3 = s5 + 15
```

Do đó tại `0x8003CCC0`, `lhu 2(s3)` đọc ngoài current record.

Current glyph metadata thật được tạo ở caller stack:

```text
0x8003CAC0  a2 = sp+16
0x8003C210  writes glyph metadata into sp+16
```

Sau đó cùng caller frame:

```text
0x8003CC3C  a1 = sp+16
0x8003C67C  copy routine
```

`0x8003C67C` dùng `lhu 2(a1)` làm `height_minus_1` của source-row loop.

Vì vậy tại sprite geometry stage, per-current-glyph height đã được dataflow chứng minh là:

```text
lhu v0,18(sp)   # (sp+16)+2
```

Native metadata = 11 -> native `+1` => 12 px.
Extended target metadata = 15 -> native `+1` => 16 px.

## CURRENT — 0.6.3.10 HEIGHT FROM STACK METADATA

Start từ stable 0.6.3.7 source-row sentinel.

Chỉ thay load tại `0x8003CCC0` bằng:

```text
lhu v0,18(sp)
```

rồi resume native:

```text
0x8003CCC8 addiu v0,v0,1
```

Source sentinel giữ nguyên:

```text
rows10..11 = dark/gray full band
rows12..15 = bright white full band
```

Không late `s0`, không global force-height, không persistent flag, không post-copy hook, không UV patch, không shared `CD94` allocator rewrite.

Package:

```text
GaiaMaster_FontIsolation_0.6.3.10_HEIGHT_FROM_STACK_METADATA.zip
```

Launcher:

```text
00_RUN_PROBE_06310.cmd
```

## Do not repeat

- Không quay lại Krom.
- Không polish production stacked accents trong 12x12.
- Không retest 0.6.2.18.
- Không retest 0.6.3.0..0.6.3.9.
- Không patch shared `0x8003CD94..0x8003CDB4` kiểu 0.6.3.1.
- Không persistent/global flag kiểu 0.6.3.6.
- Không global force-height16 kiểu 0.6.3.8.
- Không dùng `s3+2` như glyph metadata tại `0x8003CCC0`.

# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-13**

## Chốt hiện tại

Production direction hiện tại là:

> **giữ renderer/font geometry native 12x12 / 72-byte / 4bpp và tìm cách patch mapping + glyph data trực tiếp.**

Không tiếp tục 12x16, không tiếp tục composite overlay, không runtime pointer redirect.

## Những gì đã chứng minh

- `0.6.2.13` chứng minh static custom-atlas replacement hoạt động.
- Một glyph 12x12 duy nhất không đủ đẹp cho full-size Latin body + stacked Vietnamese marks.
- 0.6.3.x 12x16 chạm quá nhiều state chung và không phù hợp production.
- 0.6.4.x composite overlay cho thấy accent art có thể đẹp, nhưng runtime placement không ổn định.
- repo/PPF Việt hóa PS1 Yu-Gi-Oh! MCBB củng cố hướng patch tối thiểu: font/resource + mapping/data thay vì redesign renderer.

## 0.6.5.x

### 0.6.5.0 UNIFIED NATIVE-CELL FONT

Mục tiêu:

```text
A Â Ấ Ẳ E Ê Ế Ể O Ô Ố Ỗ
```

Runtime ra phần lớn glyph A-like và một Kanji lạc chỗ.

Kết luận:

> giả thuyết `0x889F..0x88AA` map tuyến tính vào atlas slots `0..11` là sai.

### 0.6.5.1

Không chạy tới runtime vì builder kiểm zero-filled cave quá rộng. Clean ROM vẫn đúng.

### 0.6.5.2 ATLAS-BACKED CUSTOM BANK

**UNSAFE FAIL**:

- màn đen;
- Game FPS 0;
- treo cứng.

Không retest. Không dùng lại runtime redirect kiểu này.

## CURRENT — READ-ONLY FONT MAPPING SCANNER 0.1

Hiện tại **không có ROM probe nào cần test**.

Package local:

```text
GaiaMaster_FontMappingScanner_0.1.zip
```

Chạy:

```text
00_RUN_FONT_MAPPING_SCANNER.cmd
```

Gửi lại:

```text
GaiaMaster_FontMappingScanner_01.txt
```

Scanner không sửa ROM và không cần boot emulator.

Mục tiêu phiên tiếp theo:

1. đọc report scanner;
2. xác định mapping data thật;
3. nếu mapping patch được như data, build proof mới chỉ sửa mapping entries + native 12x12 glyph data;
4. không tạo runtime hook mới trước khi mapping ownership được chứng minh.

## File quan trọng

```text
HANDOFF_CURRENT.md
FONT_MAPPING_PIVOT_0.6.5.md
PROBE_BUILD_INDEX.md
CHARACTER_SELECT_FONT_REVERSE_0.1.md
YUGIOH_MCBB_REFERENCE_PIVOT.md
```

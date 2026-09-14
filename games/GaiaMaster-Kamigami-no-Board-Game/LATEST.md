# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-14**

## CURRENT — 0.6.40.0 BATCH 30

Trọng tâm: **Accent Sweep + Whole-Game Japanese Discovery**.

## Vì sao đổi hướng

Screenshot runtime cho thấy Translation Master 596 dòng hiện tại chưa phủ toàn game. Nhiều story/tutorial/help strings vẫn hoàn toàn bằng tiếng Nhật, trong khi một số row đã biết vẫn có thể rơi xuống fallback Alpha không dấu.

Vì vậy từ Batch30, dự án chạy hai hướng song song:

1. nâng dấu hàng loạt cho fallback đã có bằng bằng chứng semantic an toàn;
2. quét trực tiếp CLEAN PRGPACK/SLPS để tìm text Nhật chưa từng vào master.

## Nâng dấu

Batch27 Japanese-key promotion: **2 row mới**.

Batch28 same-row lexical accent transplant sau khi bảo vệ historical locks: **71 row mới**.

Ví dụ:

```text
NHAN THE SK   -> Nhận thẻ SK
THE VK DA DAY -> Thẻ VK đã đầy
DOI DUONG?    -> Đổi đường?
HUY            -> Hủy
CHON KHU?      -> Chọn khu?
PHA CAI NAO!!  -> Phá cái nào!!
```

## Batch29 exact merge

```text
Input B20/B24/B27/B28          = 295
Unique final exact keys        = 295
Runtime-fit protected keys     = 49
Historical no-op/unfit         = 13
Already-locked identical       = 13
Protected wording conflicts    = 0
New exact rows exported        = 282
Final exact verification set   = 295
Errors                         = 0
RESULT                         = STATIC PASS
```

Validation:

`checkpoints/0.6.39.0/BATCH29_MERGE_VALIDATION.txt`

## Batch30 production builder

Windows launcher:

`tools/00_BUILD_0.6.40.0_BATCH30_ACCENT_SWEEP.cmd`

Python builder:

`tools/build_gaia_06400_batch30_accent_sweep.py`

Builder selftest PASS:

```text
New exact targets     = 282
Final exact verify    = 295
Legacy shadows        = 282
Dynamic sinks         = 5
Legacy gate           = 397/397
Gameplay masks        = 180
Compact13 masks       = 67
Compact14 masks       = 2
Global-map preserves  = 33
Source restore        = PASS
```

Production chain vẫn là 0.6.14 -> 0.6.10 đã chứng minh. Không tạo encoder hoặc ROM patch engine thứ hai.

Sau actual clean-ROM build, **295/295 exact fields phải khớp byte-for-byte** mới PASS.

## Whole-game scanner

Read-only scanner:

```text
tools/00_SCAN_0.6.38.0_FULL_JAPANESE.cmd
tools/scan_full_japanese_text_06380.py
```

Nó quét CLEAN `PRGPACK.BDP` + `SLPS_020.75`, loại vùng font/mapping và so với Translation Master hiện tại.

Output cần gửi lại:

```text
GaiaMaster_0.6.38.0_FULL_JAPANESE_SCAN.csv
GaiaMaster_0.6.38.0_FULL_JAPANESE_SCAN_REPORT.txt
```

Các screenshot anchor được ưu tiên gồm Memory Card, story dialogue, tutorial, battle-card help và end-turn text.

## Clean-ROM gate

```text
SHA1 f4d5298583c90d89c4b7e51d2dde160ee07f2aec
```

## Runtime checkpoint

Ảnh cũ còn `LUOT ジガ` cho thấy emulator chưa chạy output mới, vì key `%sの番よ！` đã được exact-map thành `Tới %s` trong manifest hiện tại.

Bản EASY 0.6.40 tự tìm CLEAN BIN bằng SHA1 để tránh build nhầm BIN cũ. Sau build phải mở đúng output có tên 0.6.40.0, không dùng Recent/History của emulator nếu nó trỏ vào image cũ.

## Production architecture không đổi

```text
native 12x12 / 72-byte / 4bpp / LOW nibble first
static mapping-only
frozen 60-glyph Vietnamese codepage
legacy Alpha coverage gate = 397/397
```

Không renderer hook, pointer redirect, 12x16, 6x12, composite overlay hoặc font retune nếu chưa có runtime evidence mới.

## Status

**0.6.40.0 = BUILD-READY / STATIC PASS.**

Chưa phải Runtime PASS.

## Tiếp theo

1. Build 0.6.40 từ CLEAN BIN.
2. Kiểm report phải có 295/295 byte verification và gate 397/397.
3. Chạy whole-game scanner trên CLEAN BIN.
4. Import scanner output để mở rộng master sang story/tutorial/help.
5. Làm batch lớn tiếp theo theo visible-runtime coverage, không chỉ dựa trên số row cũ.

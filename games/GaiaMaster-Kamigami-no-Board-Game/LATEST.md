# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-14**

## CURRENT — 0.6.52.0 BATCH 42

Trọng tâm: **Current Translation Master Closure + Whole-Game Japanese Discovery**.

Status: **BUILD-READY / STATIC PASS**. Chưa phải Runtime PASS.

## Mốc dữ liệu mới

Sau Batch34, residual fallback trong Translation Master còn 218 row. Batch36 thực hiện large curated compact sweep:

```text
Curated Japanese keys   = 184
New exact rows          = 185
Exact-full-field rows   = 65
Errors                  = 0
```

Sau đó Batch38 kiểm lại chỉ còn **33 residual rows**. Batch39 xử lý đủ 33/33, bao gồm hai chuỗi runtime-token đặc biệt.

Batch40 merge hiện tại:

```text
B37 new rows             = 514
B37 final rows           = 527
B39 closure rows         = 33
Merged new exact targets = 547
Merged final verify set  = 560
Errors                   = 0
RESULT                   = STATIC MERGE PASS
```

## Full Translation Master coverage audit

Batch41 audit toàn bộ 596 row, không chỉ các row có fallback:

```text
Translation Master rows       = 596
Batch40 final exact keys      = 560
Batch19 exact locks           = 24
Runtime-fit historical locks  = 25
Union covered master keys     = 596 / 596
Uncovered master keys         = 0
Uncovered with Alpha fallback = 0
Uncovered with vi_full        = 0
RESULT                        = MASTER FALLBACK COVERAGE PASS
```

Quan trọng: **596/596 chỉ nói về Translation Master hiện tại, KHÔNG phải toàn bộ game.** Story / Tutorial / Help / Memory Card có thể nằm ngoài master và vẫn cần whole-game scanner.

## Batch42 production builder

Python builder:

`tools/build_gaia_06520_batch42_master_closure.py`

Production stage:

`tools/batch40_stage_06500.py`

Builder + real staging/restoration selftest đều PASS.

Actual clean-ROM build bắt buộc đạt:

```text
547 exact targets staged
560 / 560 exact fields byte verification
397 / 397 legacy Alpha gate
source restoration PASS
```

Clean Japan BIN SHA1:

`f4d5298583c90d89c4b7e51d2dde160ee07f2aec`

## EASY package

`GaiaMaster_0.6.52.0_Batch42_EASY.zip`

Ngoài cùng:

```text
00_VIET_HOA_GAME.cmd
01_QUET_TOAN_BO_GAME.cmd
02_DOC_TRUOC.txt
```

`00_VIET_HOA_GAME.cmd` tự tìm đúng CLEAN BIN bằng SHA1.

## Whole-game scanner

Sau khi build/test, chạy:

`01_QUET_TOAN_BO_GAME.cmd`

Gửi lại:

```text
GaiaMaster_0.6.38.0_FULL_JAPANESE_SCAN.csv
GaiaMaster_0.6.38.0_FULL_JAPANESE_SCAN_REPORT.txt
```

Đây là input để mở rộng master sang Story / Tutorial / Help / Memory Card text chưa từng được 596-row master bắt tới.

## Architecture vẫn khóa

```text
native 12x12 / 72-byte / 4bpp / LOW nibble first
static mapping-only
frozen 60-glyph Vietnamese codepage
legacy Alpha gate = 397/397
```

Không renderer hook, pointer redirect, 12x16, 6x12, composite overlay hoặc font retune nếu chưa có runtime evidence.

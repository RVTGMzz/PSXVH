# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-14**

## CURRENT — 0.6.35.0 BATCH 26

Trọng tâm: **Final Exact Production Wrapper / Build-Ready Static Pass**.

## Translation data đã đóng

```text
Residual Alpha 0.6.28.0      = 147 rows
Đã resolve                   = 147 / 147
Batch20 + Batch24 final set  = 222 exact keys
Historical proven locks reuse = 13
Batch25 new exact rows       = 209
Batch25 conflicts            = 0
```

## Batch 26 production precedence

Batch 26 đã chứng minh 209 exact mới có thể đi xuyên production chain cũ mà không bị các lớp 0.6.11-0.6.14 ghi đè:

```text
Legacy shadow rows                 = 209
Dynamic sink rows                  = 4
0.6.11 exact collisions masked     = 149
0.6.13 exact collisions masked     = 23
0.6.14 exact collisions masked     = 2
Global-map preservation entries    = 29
Effective dynamic hits             = 10
Dynamic hits identical             = 6
Dynamic differing hits safely sunk = 4
Legacy gate before                 = 397
Legacy gate during wrapper         = 397
Final exact static mismatches      = 0
Errors                             = 0
RESULT                             = STATIC PRECEDENCE PASS
```

Audit:

`checkpoints/0.6.35.0/BATCH26_PRECEDENCE_AUDIT.txt`

## Production builder đã sẵn sàng

Windows launcher:

`tools/00_BUILD_0.6.35.0_BATCH26_FINAL_EXACT.cmd`

Python builder:

`tools/build_gaia_06350_batch26_final.py`

Builder giữ nguyên production chain:

```text
0.6.35 staging
 -> 0.6.14
    -> 0.6.13
       -> 0.6.12
          -> 0.6.11
             -> 0.6.10 exact builder
```

Không tạo encoder/ROM patch engine thứ hai.

## Clean-ROM gate

Chỉ nhận Japan CLEAN BIN:

```text
SHA1 f4d5298583c90d89c4b7e51d2dde160ee07f2aec
```

## Hard output verification

Sau khi inner production builder chạy xong, 0.6.35 đọc lại BIN đầu ra và dùng readable 0.6.10 encoder + frozen codepage để xác minh toàn bộ final exact set:

```text
222 / 222 exact fields phải khớp byte-for-byte
```

Chỉ một field lệch cũng làm build fail.

## CI hiện tại

Đã PASS:

- production precedence audit;
- real CSV staging + restoration hash selftest;
- final Batch26 builder `--selftest`.

GitHub không chứa CLEAN ROM nên chưa chạy actual image build trên CI.

## Production architecture không đổi

```text
native 12x12 / 72-byte / 4bpp / LOW nibble first
static mapping-only
frozen 60-glyph Vietnamese codepage
legacy Alpha coverage gate = 397/397
```

Không renderer hook, pointer redirect, 12x16, 6x12, composite overlay hay retune font nếu chưa có runtime evidence mới.

## Status

**0.6.35.0 = BUILD-READY / STATIC PRECEDENCE PASS.**

Chưa phải Runtime PASS.

## Tiếp theo

1. Kéo CLEAN Japan BIN vào `00_BUILD_0.6.35.0_BATCH26_FINAL_EXACT.cmd`.
2. Yêu cầu report 0.6.35.0 báo **222/222 exact byte verification** và source restore PASS.
3. Chạy game thật.
4. Gửi screenshot/log để kiểm Japanese còn sót, clipping, token, intro separators và glyph.
5. Chỉ khi runtime evidence đạt mới nâng lên Runtime PASS.

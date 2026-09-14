# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-14**

## CURRENT — 0.6.28.0 BATCH 19

Trọng tâm: **Exact-Offset Lock / Session Handoff**.

Base trước runtime harvest:

```text
story/front mappings  = 19
Japanese semantic map = 437
fantasy fallback map  = 355
dynamic literals      = 231
```

Batch 19 manual delta:

```text
20 Japanese semantic edits
20 fantasy fallback edits
12 dynamic literals
```

Điểm mới quan trọng:

- Giữ Residual Killer / Consensus Fit của Batch 18.
- Export mọi `vi_full` đã fit sang exact `file + offset` compact override path trước khi gọi inner builder.
- Không ghi đè các historical exact lock 0.6.14.1.
- Sinh 3 report: `RESIDUAL_ALPHA`, `FIT_PRESSURE`, `EXACT_OFFSET_LOCKS`.
- Output recovery quét cả package folder và source tạm.
- Có `SESSION_HANDOFF_0.6.28.0.md` và `NEXT_SESSION_START_0.6.28.0.txt` để chuyển phiên an toàn.

Repo material:

```text
BATCH19_0.6.28.0.md
SESSION_HANDOFF_0.6.28.0.md
NEXT_SESSION_START_0.6.28.0.txt
translation/BATCH19_JP_EXACT_0.6.28.0.csv
translation/BATCH19_STYLE_0.6.28.0.csv
translation/BATCH19_DYNAMIC_0.6.28.0.csv
checkpoints/0.6.28.0/README.md
```

Production lock không đổi: native 12x12 / 72-byte / 4bpp, static mapping-only, frozen codepage, legacy coverage gate 397/397. Font không chỉnh.

`0.6.28.0` là candidate; loader syntax PASS. Clean-ROM build và runtime QA vẫn chờ test thực tế.

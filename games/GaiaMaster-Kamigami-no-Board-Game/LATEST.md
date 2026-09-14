# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-14**

## CURRENT — 0.6.27.0 BATCH 18

Trọng tâm: **Residual Killer / Consensus Fit** — săn các row còn trống và các câu đã có nghĩa Việt nhưng chưa từng vừa field PS1.

Base trước runtime harvest:

```text
story/front mappings  = 19
Japanese semantic map = 437
fantasy fallback map  = 354
dynamic literals      = 229
```

Batch 18 manual delta:

```text
9 semantic mappings
9 fantasy fallback mappings
5 dynamic literals
```

Điểm mới quan trọng của Batch 18:

- Consensus translation giữa các row lặp trong 6 Translation Master.
- Fit V2: semantic -> consensus -> vi_full -> compact -> micro -> ultra -> STYLE -> accent fallback.
- Whitespace normalization để bắt duplicate chỉ khác khoảng trắng/full-width space.
- Sinh `GaiaMaster_0.6.27.0_RESIDUAL_ALPHA.csv` cho row Alpha còn trống.
- Sinh `GaiaMaster_0.6.27.0_FIT_PRESSURE.csv` cho row có bản Việt nhưng vẫn quá dài, kèm số byte vượt.

Repo material:

```text
BATCH18_0.6.27.0.md
translation/BATCH18_JP_EXACT_0.6.27.0.csv
translation/BATCH18_STYLE_0.6.27.0.csv
translation/BATCH18_DYNAMIC_0.6.27.0.csv
checkpoints/0.6.27.0/README.md
```

Production lock không đổi: native 12x12 / 72-byte / 4bpp, static mapping-only, legacy coverage gate 397/397. Font không chỉnh.

`0.6.27.0` là candidate; syntax PASS. Clean-ROM build và runtime QA vẫn chờ test thực tế.

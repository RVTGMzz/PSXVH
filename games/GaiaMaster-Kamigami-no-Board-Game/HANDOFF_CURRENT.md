# HANDOFF — Gaia Master PS1 Việt hóa

Updated: 2026-09-14
Branch: `gaia-character-select-font-atlas-reverse-01`

## Current candidate

**0.6.27.0 — Residual Killer / Consensus Fit Batch 18**

Base scale trước runtime harvest:

```text
story/front mappings  = 19
Japanese semantic map = 437
fantasy fallback map  = 354
dynamic literals      = 229
```

### Batch 18 core

Batch 18 chuyển từ broad sweep sang fit/residual elimination.

1. Quét cả 6 Translation Master và học **consensus translation** từ các row lặp đã có bản Việt.
2. Với mỗi row, thử theo thứ tự ưu tiên:
   - semantic chuẩn
   - semantic micro/ultra compact
   - consensus theo Japanese key
   - `vi_full` fantasy
   - compact / micro / ultra
   - STYLE fallback
   - consensus theo fallback
   - fallback phục hồi dấu
3. Chỉ promote khi giữ runtime token và vừa field Nhật.
4. Chuẩn hóa khoảng trắng để bắt duplicate chỉ khác normal/full-width space.
5. Sinh hai báo cáo:
   - `GaiaMaster_0.6.27.0_RESIDUAL_ALPHA.csv`
   - `GaiaMaster_0.6.27.0_FIT_PRESSURE.csv`

`FIT_PRESSURE` ghi cả candidate ngắn nhất, số byte field Nhật, số byte candidate và mức vượt. Đây là đầu vào chính cho Batch 19.

Repo material:

```text
BATCH18_0.6.27.0.md
translation/BATCH18_JP_EXACT_0.6.27.0.csv
translation/BATCH18_STYLE_0.6.27.0.csv
translation/BATCH18_DYNAMIC_0.6.27.0.csv
checkpoints/0.6.27.0/README.md
```

Production locks remain unchanged:

```text
native 12x12 / 72-byte / 4bpp
static mapping-only
legacy Alpha coverage gate = 397/397
```

Translation policy: Japanese-first, natural Vietnamese if it fits, then increasingly compact fantasy wording. Preserve `%s`, `%d`, `%4d`, `%+3d` and runtime token order.

Intro separator cleanup remains mandatory:

```text
NGUOI=CO      -> NGUOI CO
THEGIOI=BANCO -> THEGIOI BANCO
```

`0.6.27.0` is syntax-checked only. Clean-ROM build and runtime QA are still pending. Do not call PASS without user evidence.

Next priority: use the two Batch 18 reports plus runtime screenshots to eliminate the final Japanese/overlong rows with exact-offset compact wording.

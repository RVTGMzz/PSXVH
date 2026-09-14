# HANDOFF — Gaia Master PS1 Việt hóa

Updated: 2026-09-14
Branch: `gaia-character-select-font-atlas-reverse-01`

## Current candidate

**0.6.26.0 — Japanese Extermination Batch 17**

Base scale trước runtime harvest:

```text
story/front mappings  = 19
Japanese semantic map = 436
fantasy fallback map  = 354
dynamic literals      = 229
```

Batch 17 manual delta:

```text
semantic polish       = 21
fantasy fallback      = 21
dynamic manual        = 13
```

### Batch 17 core

Build-time residual harvester quét toàn bộ 6 Translation Master. Với row `IN_ALPHA_05` còn `vi_full` trống, thử theo thứ tự:

1. Japanese semantic map
2. `vi_full`
3. compact fantasy
4. STYLE fallback
5. accent-restored fallback

Chỉ promote khi giữ runtime token và vừa field Nhật. Các câu Nhật tự chứa, không có `%` hoặc `/V`, đủ an toàn được thêm vào dynamic literal để bắt duplicate ngoài offset chính.

Sau harvest, builder sinh:

`GaiaMaster_0.6.26.0_RESIDUAL_ALPHA.csv`

để Batch kế tiếp biết chính xác row Alpha nào vẫn chưa dịch được.

Repo material:

```text
BATCH17_0.6.26.0.md
translation/BATCH17_JP_EXACT_0.6.26.0.csv
translation/BATCH17_STYLE_0.6.26.0.csv
translation/BATCH17_DYNAMIC_0.6.26.0.csv
checkpoints/0.6.26.0/README.md
```

Production locks remain unchanged:

```text
native 12x12 / 72-byte / 4bpp
static mapping-only
legacy Alpha coverage gate = 397/397
```

Translation policy: Japanese-first, natural Vietnamese if it fits, compact fallback if needed, preserve `%s`, `%d`, `%4d`, `%+3d`. Tone: readable medieval fantasy.

Intro separator cleanup remains mandatory:

```text
NGUOI=CO      -> NGUOI CO
THEGIOI=BANCO -> THEGIOI BANCO
```

`0.6.26.0` is syntax-checked only. Clean-ROM build and runtime QA are still pending. Do not call PASS without user evidence.

Next priority: use the residual CSV plus runtime screenshots to eliminate the final Japanese strings rather than broadening scope again.

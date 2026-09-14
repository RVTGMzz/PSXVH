# HANDOFF — Gaia Master PS1 Việt hóa

Updated: 2026-09-14
Branch: `gaia-character-select-font-atlas-reverse-01`

## Current candidate

**0.6.22.0 — Deep Event / Menu / Card Batch 13**

Current scale:

```text
story/front mappings  = 19
Japanese semantic map = 359
fantasy fallback map  = 284
dynamic literals      = 103
```

Batch 13 delta:

```text
Japanese semantic new/edited = 61
fantasy fallback new/edited  = 58
dynamic literals new/edited  = 24
```

Repo checkpoint material:

```text
BATCH13_0.6.22.0.md
translation/BATCH13_JP_EXACT_0.6.22.0.csv
translation/BATCH13_STYLE_0.6.22.0.csv
translation/BATCH13_DYNAMIC_0.6.22.0.csv
checkpoints/0.6.22.0/
```

Production locks remain unchanged:

```text
native 12x12 / 72-byte / 4bpp
static mapping-only
legacy Alpha coverage gate = 397/397
```

Translation policy: Japanese-first, natural Vietnamese if it fits, compact fallback if needed, preserve runtime tokens `%s`, `%d`, `%4d`, `%+3d`.

Tone: readable medieval fantasy. Prefer terms such as `lãnh địa`, `lộ phí`, `Thánh địa`, `Ma vương`, `Tà thần`, `Thần Thời`, `Thần Vận`, `thánh kiếm`, `ma pháp`, `phong ấn`, `tỉ thí`.

Intro separator cleanup remains mandatory:

```text
NGUOI=CO      -> NGUOI CO
THEGIOI=BANCO -> THEGIOI BANCO
```

Batch 13 specifically attacks split runtime fragments, quoted card labels, dynamic names and board/economy labels such as `Giá trị`, `Lộ phí`, `Quỹ`, `Vô chủ`, `Ô GO`, `Ô chiến`, `Ô quán`, tax squares and `Thánh địa`.

`0.6.22.0` is a candidate pending clean-ROM build and runtime QA. Next priority: remaining long story/dialog lines, event text still sourced outside Translation Master, deeper card-help screens, and any Japanese text caught in screenshots.

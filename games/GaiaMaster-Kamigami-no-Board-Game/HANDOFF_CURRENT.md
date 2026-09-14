# HANDOFF — Gaia Master PS1 Việt hóa

Updated: 2026-09-14
Branch: `gaia-character-select-font-atlas-reverse-01`

## Current candidate

**0.6.23.0 — Property / Economy / Card Batch 14**

Current scale:

```text
story/front mappings  = 19
Japanese semantic map = 397
fantasy fallback map  = 327
dynamic literals      = 113
```

Batch 14 delta:

```text
Japanese semantic map delta = 50
new semantic keys           = 38
semantic re-edits           = 1
fantasy fallback delta      = 46
dynamic literal delta       = 16
```

Repo material:

```text
BATCH14_0.6.23.0.md
translation/BATCH14_JP_EXACT_0.6.23.0.csv
translation/BATCH14_STYLE_0.6.23.0.csv
translation/BATCH14_DYNAMIC_0.6.23.0.csv
```

Production locks remain unchanged:

```text
native 12x12 / 72-byte / 4bpp
static mapping-only
legacy Alpha coverage gate = 397/397
```

Translation policy: Japanese-first, natural Vietnamese if it fits, compact fallback if needed, preserve runtime tokens `%s`, `%d`, `%4d`, `%+3d`.

Tone: readable medieval fantasy. Prefer terms such as `lãnh địa`, `lộ phí`, `ngân quỹ`, `Thánh địa`, `Ma vương`, `Tà thần`, `Thần Thời`, `Thần Vận`, `thần tượng`, `tỉ thí`.

Intro separator cleanup remains mandatory:

```text
NGUOI=CO      -> NGUOI CO
THEGIOI=BANCO -> THEGIOI BANCO
```

Batch 14 specifically attacks the property/economy layer and mid-match management UI: sell, mortgage, price, funds, shops, land/area selection, assets, symbols, reclaiming property and card-help toll modifiers.

`0.6.23.0` is a candidate pending clean-ROM build and runtime QA. Next priority: long story/dialog lines, event text sourced outside Translation Master, deeper card-help screens, and any Japanese strings seen in runtime screenshots.

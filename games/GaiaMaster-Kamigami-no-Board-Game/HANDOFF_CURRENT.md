# HANDOFF — Gaia Master PS1 Việt hóa

Updated: 2026-09-14
Branch: `gaia-character-select-font-atlas-reverse-01`

## Current candidate

**0.6.24.0 — Deep Dialog / Help / Event Batch 15**

Current scale:

```text
story/front mappings  = 19
Japanese semantic map = 435
fantasy fallback map  = 354
dynamic literals      = 125
```

Batch 15 delta:

```text
Japanese semantic map delta = 46
new semantic keys           = 38
semantic re-edits           = 8
fantasy fallback delta      = 45
dynamic literal delta       = 19
```

Repo material:

```text
BATCH15_0.6.24.0.md
translation/BATCH15_JP_EXACT_0.6.24.0.csv
translation/BATCH15_STYLE_0.6.24.0.csv
translation/BATCH15_DYNAMIC_0.6.24.0.csv
```

Production locks remain unchanged:

```text
native 12x12 / 72-byte / 4bpp
static mapping-only
legacy Alpha coverage gate = 397/397
```

Translation policy: Japanese-first, natural Vietnamese if it fits, compact fallback if needed, preserve runtime tokens `%s`, `%d`, `%4d`, `%+3d`.

Tone: readable medieval fantasy. Prefer terms such as `lãnh địa`, `lộ phí`, `ngân quỹ`, `Thánh địa`, `Ma vương`, `Tà thần`, `Thần Thời`, `Thần Vận`, `thần tượng`, `tỉ thí`, `Linh tuyền`.

Intro separator cleanup remains mandatory:

```text
NGUOI=CO      -> NGUOI CO
THEGIOI=BANCO -> THEGIOI BANCO
```

Batch 15 specifically attacks deeper dialogue and fragmented help text: Ma-vương/NPC lines, facility/owner/value/toll panels, tax and accumulated-money explanations, route switching, mini-game fragments, and card/event wording for Đạo tặc, Pháp sư, Đại quốc and Thần Vận.

`0.6.24.0` is a candidate pending clean-ROM build and runtime QA. Next priority: long story/dialog lines outside the current Translation Master, deeper event screens, card-help pages and any Japanese strings seen in runtime screenshots.

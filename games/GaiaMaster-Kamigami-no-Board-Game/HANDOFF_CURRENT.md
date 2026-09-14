# HANDOFF — Gaia Master PS1 Việt hóa

Updated: 2026-09-14
Branch: `gaia-character-select-font-atlas-reverse-01`

## Current candidate

**0.6.21.0 — Deep Story / Card / Item Batch 12**

Current scale:

```text
story/front mappings  = 19
Japanese semantic map = 309
fantasy fallback map  = 256
dynamic literals      = 86
```

Batch 12 delta:

```text
Japanese semantic new/edited = 92
fantasy fallback new/edited  = 64
dynamic literals new/edited  = 15
```

Repo checkpoint material:

```text
BATCH12_0.6.21.0.md
translation/BATCH12_JP_EXACT_0.6.21.0.csv
translation/BATCH12_STYLE_0.6.21.0.csv
translation/BATCH12_DYNAMIC_0.6.21.0.csv
checkpoints/0.6.21.0/
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

`0.6.21.0` is a candidate pending runtime QA. Next priority: story/intro, NPC/tavern dialogue, mid-match menus, card list/help, weapon/item/magic descriptions, area/tax/hospital/Ma vương events, and any remaining Japanese text.

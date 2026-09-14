# 0.6.21.0 Batch 12 checkpoint

Standalone user package:

```text
GaiaMaster_0.6.21.0_BATCH12_DEEP_STORY_CARD_ITEM.zip
```

The game image is never stored here.

Reconstruction source for Batch 12 is the previous Batch 11 builder/checkpoint plus:

```text
../../translation/BATCH12_JP_EXACT_0.6.21.0.csv
../../translation/BATCH12_STYLE_0.6.21.0.csv
../../translation/BATCH12_DYNAMIC_0.6.21.0.csv
../../BATCH12_0.6.21.0.md
```

Scale after applying this delta:

```text
story/front mappings  = 19
Japanese semantic map = 309
fantasy fallback map  = 256
dynamic literals      = 86
```

Production locks remain native 12x12 / 72-byte / 4bpp, static mapping-only, and the 397/397 legacy coverage gate.

Runtime status: candidate pending user test.

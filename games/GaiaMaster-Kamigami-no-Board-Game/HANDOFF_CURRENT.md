# HANDOFF — Gaia Master PS1 Việt hóa

Updated: 2026-09-14
Branch: `gaia-character-select-font-atlas-reverse-01`

## Current candidate

**0.6.28.0 — Exact-Offset Lock / Session Handoff Batch 19**

Current base scale before runtime harvest:

```text
story/front mappings  = 19
Japanese semantic map = 437
fantasy fallback map  = 355
dynamic literals      = 231
```

### Batch 19 core

1. Giữ nguyên Residual Killer / Consensus Fit V2 của Batch 18.
2. Sau semantic/consensus fitting, mọi row có `vi_full` giữ token và vừa field Nhật sẽ được xuất thêm vào đường exact `file + offset` của `COMPACT_TRANSLATION_OVERRIDES_0.6.14.0.csv`.
3. Không tự ghi đè các exact lock lịch sử 0.6.14.1 đã từng test.
4. Sinh ba report sau build:
   - `GaiaMaster_0.6.28.0_RESIDUAL_ALPHA.csv`
   - `GaiaMaster_0.6.28.0_FIT_PRESSURE.csv`
   - `GaiaMaster_0.6.28.0_EXACT_OFFSET_LOCKS.csv`
5. Output recovery quét cả package folder và temporary source folder trước khi rename output.
6. Package có session snapshot và next-session bootstrap để chuyển phiên an toàn.

Manual Batch 19 delta:

```text
20 Japanese semantic edits
20 fantasy fallback edits
12 dynamic literal edits
```

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

Production locks remain unchanged:

```text
native 12x12 / 72-byte / 4bpp / LOW nibble first
static mapping-only
frozen 60-glyph Vietnamese codepage
legacy Alpha coverage gate = 397/397
```

No renderer hook, pointer redirect, 12x16, 6x12, composite overlay, or font retuning without new runtime evidence.

Translation policy: Japanese-first, natural Vietnamese if it fits, then fantasy compact -> micro -> ultra. Preserve `%s`, `%d`, `%4d`, `%+3d`, `/V` runtime token order.

Intro cleanup remains mandatory:

```text
NGUOI=CO      -> NGUOI CO
THEGIOI=BANCO -> THEGIOI BANCO
```

`0.6.28.0` is a candidate. Loader syntax PASS only. Clean-ROM build and runtime QA are still pending user evidence. Do not call runtime PASS without screenshots/logs.

## Next session priority

Read `SESSION_HANDOFF_0.6.28.0.md` first. Ask user for the three Batch 19 report CSVs and runtime screenshots. Use `FIT_PRESSURE` to create exact-offset compact wording for remaining overlong rows, use `RESIDUAL_ALPHA` for remaining untranslated rows, and use visible Japanese screenshots to catch strings outside Translation Master. Font stays frozen.

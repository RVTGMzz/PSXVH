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
BATCH19_REPORT_RECONSTRUCTION_0.6.28.0.md
SESSION_HANDOFF_0.6.28.0.md
NEXT_SESSION_START_0.6.28.0.txt
translation/BATCH19_JP_EXACT_0.6.28.0.csv
translation/BATCH19_STYLE_0.6.28.0.csv
translation/BATCH19_DYNAMIC_0.6.28.0.csv
tools/gaia_batch19_report_compiler_06280.py
tools/00_RUN_0.6.28.0_BATCH19_REPORTS.cmd
checkpoints/0.6.28.0/README.md
```

### 2026-09-14 report-stage reconstruction

Git history audit found that the handoff snapshot contained the Batch 19 translation deltas and documentation, but the executable report stage itself had not been committed. The repo now contains a conservative repo-native reconstruction:

```text
tools/gaia_batch19_report_compiler_06280.py
tools/00_RUN_0.6.28.0_BATCH19_REPORTS.cmd
```

It reads the six Translation Master parts, cumulative Batch semantic/style maps, Batch 18 duplicate consensus, and the historical 0.6.14.1 exact-lock file. It is report-only and does not modify ROM/BIN/CUE/BDP/font data.

Default generated output:

```text
checkpoints/0.6.28.0/reports/GaiaMaster_0.6.28.0_RESIDUAL_ALPHA.csv
checkpoints/0.6.28.0/reports/GaiaMaster_0.6.28.0_FIT_PRESSURE.csv
checkpoints/0.6.28.0/reports/GaiaMaster_0.6.28.0_EXACT_OFFSET_LOCKS.csv
checkpoints/0.6.28.0/reports/GaiaMaster_0.6.28.0_AUTO_EXACT_OVERRIDES.csv
checkpoints/0.6.28.0/reports/GaiaMaster_0.6.28.0_REPORT_SUMMARY.txt
```

The execution environment used during this handoff could not reach GitHub from its local shell, so the compiler has not been run against a checked-out branch here. Do not invent report counts. Run the one-click CMD in a local checkout, then consume the generated CSVs.

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

1. Run `tools/00_RUN_0.6.28.0_BATCH19_REPORTS.cmd` in a current local checkout.
2. Consume `FIT_PRESSURE` first and create exact-offset compact wording for remaining overlong rows.
3. Consume `RESIDUAL_ALPHA` for remaining untranslated Alpha rows.
4. Review `EXACT_OFFSET_LOCKS` / `AUTO_EXACT_OVERRIDES` before integrating them into a ROM build path.
5. Use runtime screenshots to catch visible Japanese outside Translation Master.
6. Font stays frozen unless runtime demonstrates a real glyph defect.

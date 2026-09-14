# HANDOFF — Gaia Master PS1 Việt hóa

Updated: 2026-09-14
Branch: `gaia-character-select-font-atlas-reverse-01`

## Current checkpoint

**0.6.44.0 — Batch 34 Curated Compact Production Build**

Status: **BUILD-READY / STATIC PASS**.

This is still **not Runtime PASS**.

Read next:

```text
BATCH34_0.6.44.0.md
checkpoints/0.6.41.0/BATCH31_RESIDUAL_ALPHA_PRIORITY_REPORT.txt
checkpoints/0.6.42.0/BATCH32_CURATED_COMPACT_REPORT.txt
checkpoints/0.6.43.0/BATCH33_MERGE_REPORT.txt
translation/BATCH32_CURATED_COMPACT_0.6.42.0.csv
translation/BATCH33_NEW_EXACT_OFFSET_0.6.43.0.csv
translation/BATCH33_FINAL_EXACT_SET_0.6.43.0.csv
tools/batch33_stage_06430.py
tools/build_gaia_06440_batch34_curated_compact.py
tools/scan_full_japanese_text_06380.py
```

## Why Batch31-34 exists

After 0.6.40, the 596-row Translation Master still contained many Alpha-era ASCII fallbacks even though 295 exact fields were already protected. Batch31 rebuilt the residual inventory instead of redoing already-fixed rows.

```text
Translation Master rows      = 596
Protected B29 exact keys     = 295
Residual fallback rows       = 265
Unique residual clusters     = 242
```

Breakdown:

```text
NO_VI_FULL            = 34 clusters / 44 rows
VI_FULL_TOO_LONG      = 207 clusters / 220 rows
VI_FULL_TOKEN_MISMATCH= 1 cluster / 1 row
```

The main remaining problem inside the known master is therefore field pressure, not lack of semantic translation.

## Batch32 curated compact sweep

25 Japanese semantic keys were manually compacted into codepage-safe Vietnamese. This exported **47 new exact rows**.

The first CI pass caught unsupported `ễ` in `Dễ chí mạng`; the wording was changed to `Hay CM` rather than expanding the frozen codepage.

Final Batch32 result:

```text
Curated Japanese keys       = 25
Curated keys producing rows = 25
New exact rows exported     = 47
Exact-full-field rows       = 25
Errors                      = 0
RESULT                      = STATIC CURATED PASS
```

Examples:

```text
武器カードを / 武器カードは -> Thẻ VK
終了ターン                 -> Hết
%sのラッキー！！           -> %s hên!
なにか捨ててね             -> Bỏ bớt
騎士団                     -> Kỵ
お店破壊                   -> Phá!
%dゼニーはらってね         -> Trả %dZ
いやしのうた               -> Hồi HP
指定武器カード１枚を盗む   -> Cướp thẻ VK
あいての命中率を落とす     -> Giảm CX
ＨＰを６０回復する         -> Hồi 60HP
死亡するとＨＰ１００で復活 -> Hồi sinh100HP
```

## Batch33 merged exact state

```text
B29 new rows               = 282
B29 final rows             = 295
B32 curated rows           = 47
Merged new exact targets   = 329
Merged final verify set    = 342
Errors                     = 0
RESULT                     = STATIC MERGE PASS
```

## Batch34 production staging / builder contract

The stage wrapper reuses the already-audited Batch29/30 precedence implementation rather than introducing a new patch engine.

CI has executed the real temporary stage + restore cycle successfully.

Production chain remains:

```text
0.6.44 staging
 -> 0.6.14
    -> 0.6.13
       -> 0.6.12
          -> 0.6.11
             -> 0.6.10 exact builder
```

Python builder:

```text
tools/build_gaia_06440_batch34_curated_compact.py
```

Clean Japan BIN required:

```text
SHA1 f4d5298583c90d89c4b7e51d2dde160ee07f2aec
```

Hard post-build contract:

```text
new exact targets staged = 329
final exact fields        = 342/342 byte verification required
legacy Alpha gate         = 397/397
source restoration        = PASS
```

A mismatch blocks the build.

## EASY package

Current test package:

```text
GaiaMaster_0.6.44.0_Batch34_EASY.zip
```

Root launchers:

```text
00_VIET_HOA_GAME.cmd
01_QUET_TOAN_BO_GAME.cmd
02_DOC_TRUOC.txt
```

The build launcher auto-selects the CLEAN BIN by SHA1. The scanner remains read-only.

## Whole-game Japanese scanner remains critical

Runtime screenshots already proved that closing known master rows does not equal whole-game coverage. Memory Card, story/tutorial and card-help Japanese can exist outside the 596-row master.

Run:

```text
01_QUET_TOAN_BO_GAME.cmd
```

Return:

```text
GaiaMaster_0.6.38.0_FULL_JAPANESE_SCAN.csv
GaiaMaster_0.6.38.0_FULL_JAPANESE_SCAN_REPORT.txt
```

These are the next critical input for visible story/tutorial expansion.

## Production architecture remains frozen

```text
native 12x12 / 72-byte / 4bpp / LOW nibble first
static mapping-only
frozen 60-glyph Vietnamese codepage
legacy Alpha coverage gate = 397/397
```

Hard exclusions remain:

- no renderer hook
- no pointer redirect
- no 12x16
- no 6x12
- no composite overlay
- no font retuning without runtime evidence

Preserve `%s`, `%d`, `%4d`, `%+3d`, `/V` and token order.

## Next priority

1. Build 0.6.44 from CLEAN Japan BIN.
2. Require `GaiaMaster_0.6.44.0_BATCH34_FINAL_REPORT.txt` to show **342/342** exact byte verification and **397/397** legacy gate.
3. Boot the newly generated 0.6.44 image, not an emulator Recent/History entry pointing to an older image.
4. Run the whole-game scanner on the CLEAN BIN.
5. Import scanner output and prioritize UNSEEN-JAPANESE story/tutorial/help strings by exact offset.
6. Never call Runtime PASS before actual gameplay screenshots/logs are reviewed.

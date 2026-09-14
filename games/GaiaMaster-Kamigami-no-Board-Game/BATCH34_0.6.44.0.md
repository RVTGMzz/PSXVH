# Gaia Master 0.6.44.0 — Batch 34 Curated Compact

Updated: 2026-09-14

Status: **BUILD-READY / STATIC PASS**. This is **not Runtime PASS**.

## What Batch31-34 added

Batch31 re-inventoried all known fallback rows after the 0.6.40 exact set:

```text
Translation Master rows      = 596
Protected B29 exact keys     = 295
Residual fallback rows       = 265
Unique residual clusters     = 242
```

Batch32 manually curated 25 high-priority Japanese semantic keys and exported **47 new exact rows**. The first pass caught one unsupported `ễ`; it was replaced with the codepage-safe compact wording `Hay CM`. Final result:

```text
Curated Japanese keys        = 25
New exact rows               = 47
Exact-full-field rows        = 25
Errors                       = 0
RESULT                       = STATIC CURATED PASS
```

Examples include compact UI/gameplay/card text such as:

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

Batch33 merges the previous exact set with Batch32:

```text
B29 new rows             = 282
B29 final rows           = 295
B32 curated rows         = 47
Merged new exact targets = 329
Merged final verify set  = 342
Errors                   = 0
RESULT                   = STATIC MERGE PASS
```

The production stage reuses the already-audited Batch29/30 precedence implementation. CI executes the real temporary stage and restore cycle and passes.

## Batch34 production contract

Windows/EASY entrypoint calls:

```text
tools/build_gaia_06440_batch34_curated_compact.py
```

Clean Japan BIN required:

```text
SHA1 f4d5298583c90d89c4b7e51d2dde160ee07f2aec
```

The builder must maintain:

```text
new exact targets staged = 329
final exact byte verify   = 342/342
legacy Alpha gate         = 397/397
source restoration        = PASS
```

Architecture remains frozen:

```text
native 12x12 / 72-byte / 4bpp / LOW nibble first
static mapping-only
frozen 60-glyph Vietnamese codepage
no renderer hook
no pointer redirect
```

## Whole-game coverage remains the next major target

The known 596-row Translation Master is still not the whole game. Story/tutorial/help Japanese visible in runtime screenshots must be discovered through the read-only scanner:

```text
01_QUET_TOAN_BO_GAME.cmd
```

Expected scanner outputs:

```text
GaiaMaster_0.6.38.0_FULL_JAPANESE_SCAN.csv
GaiaMaster_0.6.38.0_FULL_JAPANESE_SCAN_REPORT.txt
```

After the user returns those files, prioritize UNSEEN-JAPANESE/story/tutorial/help strings by exact offset.

Never call Runtime PASS until the actual 0.6.44 output is booted and gameplay screenshots/logs are reviewed.

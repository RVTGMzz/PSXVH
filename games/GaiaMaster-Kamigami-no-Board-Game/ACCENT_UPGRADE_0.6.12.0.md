# Gaia Master 0.6.12.0 - Large Gameplay Translation Batch 3

Updated: **2026-09-14**

## Runtime evidence from 0.6.11.0

`0.6.11.0` proved that the accented pipeline is active, but runtime screenshots exposed three concrete regressions:

1. intro still rendered one Japanese-looking glyph at the old `=` positions in `NGUOI=CO` and `THEGIOI=BANCO`;
2. lowercase `ă` rendered with the breve shaped like a cap/hat instead of a cup;
3. gameplay still contained no-accent fallback text and dynamic Japanese names, e.g. `LUOT ジガー`.

Verdict: **0.6.11.0 PARTIAL PASS / CONTENT QA FAIL**. It remains useful as the inner production baseline.

## Current candidate

**0.6.12.0 Large Gameplay Translation Batch 3**

This is intentionally a large batch to reduce tiny test cycles. It keeps the proven production chain and expands translation breadth at the same time as fixing the screenshot-proven defects.

## Hard production locks retained

- exact old Alpha legacy coverage gate: **397 / 397**;
- native main font: `12x12 / 72-byte / 4bpp`;
- static mapping-only routing;
- 60-glyph Vietnamese production codepage;
- no renderer hook, pointer redirect, 12x16, or 6x12 narrow path;
- no broad font retuning.

The only font change in this batch is a targeted redraw of lowercase `ă`, justified by direct runtime evidence.

## Batch 3 translation expansion

`translation/BATCH3_FALLBACK_ACCENT_MAP_0.6.12.0.csv` contains **278** curated old-fallback -> accented compact mappings.

In addition, the builder globalizes the already-curated `0.6.11.0` Batch 2 mappings: if another Translation Master row uses the same old fallback, it receives the same accented rewrite when it fits its original fixed field.

Coverage includes setup, tavern dialogue, gameplay prompts, land/tax actions, cards, items, events, menus, status labels, shop/building names, movement, route switching, battle prompts and repeated strings.

Rules remain conservative:

```text
accented compact text fits original field
 -> promote

too long
 -> do not force
 -> keep existing fallback
```

## Repeated/runtime Japanese recovery

The builder scans CLEAN `SLPS_020.75` and `PRGPACK.BDP` for standalone copies of Japanese strings already known to have safe compact translations. Unrepresented standalone occurrences are injected as synthetic translation rows for this build only.

Compact dynamic-name map includes:

```text
トロル通り -> Troll
ジガー     -> Jig
ダンテ     -> Dan
孫悟空     -> Ngộ
ハヤテ     -> Hay
ヤスツナ   -> Yasu
ガラハッド -> Galah
ティアラ   -> Tiar
ゴライアス -> Golia
メグメグ   -> Megu
アガート   -> Agat
シンバッド -> Sinba
```

The compact forms are deliberate because the original fixed Japanese fields are very short.

## Intro hotfix

The fallback skeleton itself is corrected, not only the accented override:

```text
NGUOI=CO        -> NGUOI CO
THEGIOI=BANCO   -> THEGIOI BANCO
```

This targets the exact positions that rendered as unrelated Japanese-looking glyphs at runtime.

## Lowercase `ă` glyph hotfix

After the inner production build succeeds, the wrapper reconstructs the frozen production custom-code allocation, finds the existing `ă` atlas slot, and redraws only its top two accent rows.

Old breve: cap/hat-like.
New breve: shallow cup/smile.

The base `a`, mapping, slot, codepage and all other Vietnamese glyphs remain unchanged.

## Files

```text
tools/build_gaia_06120_big_translation_b3.py
tools/00_BUILD_0.6.12.0_BIG_TRANSLATION_B3.cmd
translation/BATCH3_FALLBACK_ACCENT_MAP_0.6.12.0.csv
translation/DYNAMIC_LITERAL_OVERRIDES_0.6.12.0.csv
```

## Build state

```text
SOURCE READY
PYTHON SYNTAX PASS
CLEAN-ROM BUILD PENDING
RUNTIME PENDING
```

The current session does not mount the user's clean game BIN, so the actual ROM build and emulator verification remain the runtime gate.

## Runtime gate

One broad test pass should check:

1. intro has no Japanese-looking glyph at the former `=` positions;
2. `ă` in words such as `năng` has the correct cup-shaped breve;
3. gameplay label becomes accented, e.g. `Lượt` instead of `LUOT` where the field permits it;
4. `ジガー` is gone and compact dynamic names appear in Latin/Vietnamese form;
5. menus/cards/items/events show materially more accented Vietnamese than 0.6.11.0;
6. no freeze, global font corruption, or regression of legacy coverage.

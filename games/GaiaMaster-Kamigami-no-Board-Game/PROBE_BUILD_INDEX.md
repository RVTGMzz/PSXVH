# Gaia Master — probe/build index

Updated: **2026-09-14**

Purpose: prevent checkpoint confusion and accidental retesting.

## Stable baselines

```text
Clean Japan BIN SHA1
f4d5298583c90d89c4b7e51d2dde160ee07f2aec

Alpha 0.6.1 FRONT SHA1
54d2fb026bc3b71c79861e723caffb4114caa34c
```

## Historical locks

- `0.6.2.13`: static custom atlas PASS.
- `0.6.3.x`: 12x16 corruption/freezes. Do not revive.
- `0.6.4.x`: composite overlay unreliable.
- `0.6.5.2`: pointer redirect UNSAFE FAIL / NEVER RETEST.
- `0.6.5.3`: mapping-only structural PASS.
- `0.6.5.4`: native-base copy PASS.
- `0.6.5.5`: compact accent style PASS enough for production.
- `0.6.6.0`: `Chọn tướng` end-to-end PASS.
- `0.6.6.1`: baseline-normalized PASS.
- `0.6.6.2 / 2b`: false safety blocks only.
- `0.6.6.2c`: one-byte alias runtime FAIL / retired.

## Production codepage

```text
60 custom Vietnamese glyphs
64 conservative zero-hit atlas slots
4 reserve slots
```

Frozen production set:

```text
àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ
```

## 0.6.7.x

- `0.6.7.0`: full 60-glyph production codepage boots/renders.
- `0.6.7.2`: FONT VISUAL PASS / production visual baseline.

Do not broadly retune font. Reopen only a glyph with direct runtime evidence.

## 0.6.9.x — old Alpha coverage recovery

Old Alpha legacy coverage = exactly **397 patch keys**.

- `0.6.9.0`: bad total-count gate. BUILD GATE BUG ONLY.
- `0.6.9.1`: bad legacy classification gate. BUILD GATE BUG ONLY.
- `0.6.9.2`: exact legacy reconstruction **397/397 PASS**.

Every later production build must preserve `397/397`.

## 0.6.10.0 — Front Accent Batch 1

Runtime result:

```text
FRONT ACCENT/FONT RUNTIME PASS
CONTENT QA INCOMPLETE
```

## 0.6.11.0 — Gameplay Accent Batch 2

- 335 compact accent candidates.
- first dynamic literal: `トロル通り -> Troll`.
- runtime PARTIAL PASS / CONTENT QA FAIL.
- exposed old `=` fallback leak, malformed lowercase `ă`, and remaining Japanese dynamic content.

## 0.6.12.0 — Large Gameplay Translation Batch 3

Files:

```text
ACCENT_UPGRADE_0.6.12.0.md
tools/build_gaia_06120_big_translation_b3.py
translation/BATCH3_FALLBACK_ACCENT_MAP_0.6.12.0.csv
translation/DYNAMIC_LITERAL_OVERRIDES_0.6.12.0.csv
```

Added:

- fixed the actual old front `=` fallback skeletons;
- 278 curated fallback-to-accent mappings;
- global reuse of Batch 2 mappings;
- standalone Japanese repeat scan;
- 12 compact dynamic names;
- targeted post-build lowercase `ă` hotfix v1.

### Runtime result — 2026-09-14

Translation progress is visible, but content QA remains incomplete.

New screenshot of `năng` proves the `ă` slot is patched but the v1 hotfix is visually wrong:

- breve appears mainly as dark/shadow pixels;
- mark/shadow sits too high;
- v1 used `max(nonzero palette index)` as fill, which can select known shadow index `7`;
- stale old-shadow pixels can remain in row 2.

User also reports substantial Japanese remains.

Do not treat `0.6.12.0` as final candidate.

# CURRENT — 0.6.13.0 COMPACT JAPANESE REDUCTION BATCH 4

Files:

```text
ACCENT_UPGRADE_0.6.13.0.md
tools/build_gaia_06130_translation_b4.py
tools/00_BUILD_0.6.13.0_TRANSLATION_B4.cmd
translation/COMPACT_TRANSLATION_OVERRIDES_0.6.13.0.csv
translation/DYNAMIC_LITERAL_OVERRIDES_0.6.13.0.csv
```

## Batch 4 strategy

Keep unchanged:

```text
exact 397/397 legacy gate
12x12 / 72-byte / 4bpp mapping-only architecture
60-glyph production codepage
existing BDP/checksum and raw-token pipeline
```

Add:

- **146 exact-offset compact Vietnamese candidates** for rows likely to stay Japanese when longer Vietnamese text does not fit;
- byte-fit gate on every candidate;
- dynamic literal map expanded from 12 to **35 entries**;
- weapon/card names added to dynamic cleanup;
- selected board/location names added where compact replacements fit;
- lowercase `ă` hotfix v2.

Dynamic examples:

```text
サンダー -> Sấm
ハリケーン -> Bão
クロスボウ -> Nỏ
ロングソード -> Kiếm
ファイアボール -> Lửa
バトルアックス -> Rìu
サーカス -> Xiếc
呪いの沼 -> Đầm
```

### `ă` hotfix v2

- reconstruct same frozen custom code/slot;
- derive bright fill from body histogram excluding shadow index 7;
- clear old rows 0/1 mark pixels;
- clear stale row-2 shadow pixels only;
- draw lower shallow bright breve;
- draw native shadow one pixel down/right;
- regenerate MODE2 EDC/ECC;
- no other glyph touched.

## Build state

```text
SOURCE READY
PYTHON SYNTAX PASS
CLEAN-ROM BUILD PENDING
RUNTIME PENDING
```

## Next gate

Broad runtime sweep:

1. `ă` in `năng`;
2. several gameplay turns;
3. card/item/event/menu;
4. land/tax/route/battle;
5. collect remaining full Japanese lines and Japanese `%s` names.

## Do not repeat

- no production 12x16;
- no composite overlay;
- no pointer redirect;
- no narrow alias;
- no global cursor/cache/spacing mutation;
- no broad font retune;
- no `0.6.9.0 / 0.6.9.1` retests;
- never sacrifice fitting legacy coverage;
- stop immediately on freeze/global corruption.

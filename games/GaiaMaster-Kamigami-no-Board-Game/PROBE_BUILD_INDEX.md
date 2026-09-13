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

Broad font tuning remains frozen. Reopen only a glyph with direct runtime evidence.

## 0.6.9.x — old Alpha coverage recovery

Old Alpha legacy coverage = exactly **397 patch keys**.

- `0.6.9.0`: bad total-count gate. BUILD GATE BUG ONLY.
- `0.6.9.1`: bad legacy classification gate. BUILD GATE BUG ONLY.
- `0.6.9.2`: exact legacy reconstruction **397/397 PASS**.

Every later production build must preserve `397/397`.

## 0.6.10.0

Front Accent Batch 1. Runtime:

```text
FRONT ACCENT/FONT RUNTIME PASS
CONTENT QA INCOMPLETE
```

## 0.6.11.0

Gameplay Accent Batch 2.

- 335 compact accent candidates.
- first dynamic literal: `トロル通り -> Troll`.
- runtime PARTIAL PASS / CONTENT QA FAIL.
- exposed malformed lowercase `ă`, old `=` fallback leak and mixed Japanese dynamic content.

## 0.6.12.0

Large Gameplay Translation Batch 3.

- 278 curated fallback-accent mappings;
- repeat-literal scan;
- broader dynamic-name map;
- targeted lowercase `ă` hotfix v1.

Runtime: translation progress visible, but `ă` hotfix visually incomplete.

## 0.6.13.0

Compact Japanese Reduction Batch 4.

- 146 compact exact-offset candidates;
- dynamic literals expanded to 35;
- lowercase `ă` hotfix v2 tried to erase top rows and redraw a lower breve.

Runtime screenshot proves v2 still leaves old breve/shadow pixels under the new mark.

Verdict:

```text
0.6.13.0 = CONTENT PROGRESS / LOWERCASE ă HOTFIX V2 FAIL VISUALLY
```

Do not retest as final candidate.

# CURRENT — 0.6.14.0 TRANSLATION BATCH 5 + FRESH `ă` REBUILD

Files:

```text
ACCENT_UPGRADE_0.6.14.0.md
tools/build_gaia_06140_translation_b5.py
tools/00_BUILD_0.6.14.0_TRANSLATION_B5.cmd
translation/COMPACT_TRANSLATION_OVERRIDES_0.6.14.0.csv
translation/DYNAMIC_LITERAL_OVERRIDES_0.6.14.0.csv
```

## Font strategy v3

Stop erasing guessed rows in the existing `ă` glyph.

`0.6.14.0` rebuilds the entire glyph from CLEAN native lowercase full-width `a`:

```text
CLEAN native a
 -> fresh compact body
 -> exactly one shallow-U breve
 -> native one-pixel shadow
 -> replace whole custom ă bitmap
```

Old 0.6.12/0.6.13 breve pixels therefore cannot survive.

## Translation Batch 5

Adds **38** exact-offset compact candidates concentrated on:

- gameplay/help fragments in `PRGPACK.BDP` around `0x68E18..0x68EE8`;
- early `SLPS_020.75` board/gameplay prompts;
- `Lượt %s`, `Dừng %s`, `Đất %s`, tax/land prompts and basic choice/card strings.

Dynamic map keeps earlier compact names/items and adds safe literals such as:

```text
墓地   -> Mộ
大聖堂 -> Đền
通行税 -> Phí
```

## Gate

```text
397/397 legacy coverage remains mandatory
```

## Next runtime test

1. inspect `năng`: exactly one breve and no doubled shadow;
2. play a broader board/gameplay/help sweep;
3. capture remaining Japanese strings in batches;
4. continue large translation batches, not micro-builds.

## Do not repeat

- no production 12x16;
- no narrow alias;
- no pointer redirect;
- no composite overlay;
- no global cursor/cache/spacing mutation;
- no `0.6.9.0 / 0.6.9.1` retest;
- no broad font retune beyond demonstrated glyph defects;
- stop immediately on freeze/global corruption.

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

- `0.6.2.13` static custom atlas: **PASS**.
- `0.6.3.x` 12x16: corruption/freezes. **Do not revive**.
- `0.6.4.x` composite overlay: unreliable. **Not production**.
- `0.6.5.2` runtime pointer redirect: **UNSAFE FAIL / NEVER RETEST**.
- Mapping Initializer Scanner 0.2: mapping/global ownership **PROVEN**.
- `0.6.5.3`: mapping-only **STRUCTURAL PASS**.
- `0.6.5.4`: native-base copy **PASS**.
- `0.6.5.5`: compact accent style **PASS enough for production**.

## 0.6.6.x

- `0.6.6.0`: `Chọn tướng` rendered end-to-end. **PASS**.
- `0.6.6.1`: baseline-normalized. **PASS**.
- `0.6.6.2 / 2b`: safety-gate false blocks. No runtime. Retired.
- `0.6.6.2c`: one-byte alias rendered unrelated/garbled glyphs. **RUNTIME FAIL / RETIRED**.

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
- `0.6.7.2`: **FONT VISUAL PASS / production visual baseline**.

Do not broadly retune font. A single glyph can only be reopened with direct runtime evidence.

## 0.6.8.x

`0.6.8.0 / 0.6.8.1`: safe-fit/front experiments did not restore desired gameplay coverage. Retired.

## 0.6.9.x — old Alpha coverage recovery

Old Alpha legacy coverage = exactly **397 patch keys**.

- `0.6.9.0`: bad total-count gate. **BUILD GATE BUG ONLY**.
- `0.6.9.1`: bad legacy classification gate. **BUILD GATE BUG ONLY**.
- `0.6.9.2`: exact legacy reconstruction **397/397 PASS**; Vietnamese fallback visible at runtime.

Production builds after this point must preserve the exact `397/397` gate.

## 0.6.10.0 — Front Accent Batch 1

Files:

```text
tools/build_gaia_06100_hybrid_accent_b1.py
translation/FRONT_ACCENT_OVERRIDES_0.6.10.0.csv
ACCENT_UPGRADE_0.6.10.0.md
```

Runtime result 2026-09-14:

```text
FRONT ACCENT/FONT RUNTIME PASS
CONTENT QA INCOMPLETE
```

Accented Vietnamese rendered, proving the production codepage path. QA defects included old `=` fallback glyphs, cryptic setup wording, and mixed dynamic `%s` Japanese values.

## 0.6.11.0 — Gameplay Accent Batch 2

Files:

```text
ACCENT_UPGRADE_0.6.11.0.md
tools/build_gaia_06110_hybrid_accent_b2.py
translation/FRONT_ACCENT_OVERRIDES_0.6.11.0.csv
translation/GAMEPLAY_ACCENT_OVERRIDES_0.6.11.0.csv
translation/DYNAMIC_LITERAL_OVERRIDES_0.6.11.0.csv
```

Source strategy:

- wraps exact 0.6.10.0 production builder;
- retains 397/397 legacy gate;
- contains 335 compact accent candidates;
- promotes only when the target fits the original field;
- first dynamic literal target was `トロル通り -> Troll`.

### Runtime result — 2026-09-14

**PARTIAL PASS / CONTENT QA FAIL**.

Screenshots prove:

1. intro still has a Japanese-looking glyph at the two old `=` positions because `FRONT_DEMO_ADDED_061.csv` fallback rows themselves still contain `=`;
2. lowercase `ă` in `năng` has a malformed cap/hat-like breve;
3. gameplay still shows no-accent fallback and Japanese dynamic text, e.g. `LUOT ジガー`.

Do not retest 0.6.11.0 as final candidate.

# CURRENT — 0.6.12.0 LARGE GAMEPLAY TRANSLATION BATCH 3

Files:

```text
ACCENT_UPGRADE_0.6.12.0.md
tools/build_gaia_06120_big_translation_b3.py
tools/00_BUILD_0.6.12.0_BIG_TRANSLATION_B3.cmd
translation/BATCH3_FALLBACK_ACCENT_MAP_0.6.12.0.csv
translation/DYNAMIC_LITERAL_OVERRIDES_0.6.12.0.csv
```

## Batch 3 strategy

Keep:

```text
exact 397/397 legacy gate
12x12 / 72-byte / 4bpp mapping-only architecture
60-glyph production codepage
existing BDP/checksum and raw-token path
```

Add in one larger iteration:

- correct old front skeletons `NGUOI=CO -> NGUOI CO` and `THEGIOI=BANCO -> THEGIOI BANCO`;
- **278** curated compact fallback-to-accent mappings;
- global reuse of all 0.6.11.0 Batch 2 accent mappings on duplicate `vi_game_current` rows;
- standalone/null-delimited Japanese repeat scan in clean `SLPS_020.75` and `PRGPACK.BDP`;
- temporary synthetic translation rows for safe repeated copies not already owned by Translation Master;
- 12 compact dynamic name/place replacements;
- targeted post-build redraw of lowercase `ă` breve only.

Dynamic compact map includes:

```text
トロル通り -> Troll
ジガー -> Jig
ダンテ -> Dan
孫悟空 -> Ngộ
ハヤテ -> Hay
ヤスツナ -> Yasu
ガラハッド -> Galah
ティアラ -> Tiar
ゴライアス -> Golia
メグメグ -> Megu
アガート -> Agat
シンバッド -> Sinba
```

The `ă` hotfix does not add a slot or change mapping. It finds the existing frozen slot and redraws only the two mark rows as a proper cup/smile breve.

## Build state

```text
SOURCE READY
PYTHON SYNTAX PASS
CLEAN-ROM BUILD PENDING
RUNTIME PENDING
```

Actual clean ROM is not mounted in the ChatGPT runtime.

## Next gate

Do one broad runtime sweep instead of micro-tests:

1. intro former `=` positions;
2. lowercase `ă` in `năng` or another visible word;
3. setup and first several turns;
4. old `LUOT ジガー` class of mixed text;
5. card/item/event/menu screens;
6. land/tax/route/battle actions;
7. report any Japanese, no-accent fallback, clipping, bad diacritic, freeze or global corruption.

## Do not repeat

- no production 12x16;
- no `0.6.3.x` retests;
- no composite overlay;
- no `0.6.5.2` pointer redirect;
- no one-byte narrow alias;
- no global cursor/cache/spacing mutation;
- no `0.6.9.0 / 0.6.9.1` retests;
- never remove fitting fallback coverage merely to force accents;
- no broad font retune from the single `ă` defect;
- stop immediately on freeze/global corruption.

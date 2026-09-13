# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** production stays on **native 12x12 / 72-byte / 4bpp / static mapping-only**. `0.6.9.2` remains the exact **397/397 legacy coverage PASS**. `0.6.10.0` proved accented Vietnamese renders at runtime. `0.6.11.0` was runtime-tested and is now **PARTIAL PASS / CONTENT QA FAIL**. The active candidate is **0.6.12.0 LARGE GAMEPLAY TRANSLATION BATCH 3**.

Updated: **2026-09-14**  
Branch: `gaia-character-select-font-atlas-reverse-01`

## Baselines

- Game: `GaiaMaster - Kamigami no Board Game (Japan).bin`
- serial: `SLPS-02075`
- clean BIN SHA1: `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- clean SLPS SHA1: `1dfeb6b7cfda59c108dde2dc0b8abda9a40e6ae5`
- clean PRGPACK SHA1: `a9b195b8ae5d8cad7f4f755daa08337d4671632c`
- repo: `ronvotri/Viet-Hoa-PS1`

## Proven font architecture

```text
runtime GP     = 0x80085F28
atlas global   = gp+0x518
mapping global = gp+0x51C
main atlas RAM = 0x8006BCEC
mapping RAM    = 0x8007AECC
main atlas file= SLPS+0x5C4EC
mapping file   = SLPS+0x6B6CC
860 glyphs
native main font = 12x12 / 72-byte / 4bpp / LOW nibble first
```

Pipeline:

```text
code & 0x7FFF
 -> mapping[index]
 -> glyph index
 -> glyph_index * 72
 -> atlas base + offset
```

## Production codepage

The 60-character production repertoire remains:

```text
àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ
```

Capacity baseline:

```text
60 custom Vietnamese glyphs
64 conservative zero-hit atlas slots
4 reserve slots
```

`0.6.7.2` remains the visual baseline. Do **not** reopen broad font tuning. However, the `0.6.11.0` screenshot directly demonstrates one real glyph defect: lowercase `ă` has the breve drawn cap/hat-like. `0.6.12.0` therefore performs one narrowly-scoped post-build repair of that glyph only. Mapping, slot, body and all other glyphs remain unchanged.

## Coverage hard gate

The old Alpha source produced exactly **397 patch keys**. Every current production build must preserve:

```text
legacy Alpha coverage = 397 / 397
```

Extra newer `vi_full` rows are allowed.

Runtime/control tokens remain raw where required:

```text
%s %d %+3d /V /v ...
```

Never remove a fitting `vi_game_current` fallback merely to force a longer accented string.

## Historical locks

- `0.6.2.13`: static custom atlas PASS.
- `0.6.3.x`: 12x16 corruption/freezes. Retired.
- `0.6.4.x`: composite overlay unreliable. Retired.
- `0.6.5.2`: **UNSAFE FAIL / NEVER RETEST**.
- `0.6.5.3`: mapping-only structural PASS.
- `0.6.5.4`: native-base copy PASS.
- `0.6.5.5`: compact accent style PASS enough for production.
- `0.6.6.0`: real text `Chọn tướng` end-to-end PASS.
- `0.6.6.1`: baseline-normalized PASS.
- `0.6.6.2` / `2b`: false safety blocks only. Retired.
- `0.6.6.2c`: one-byte narrow alias runtime FAIL. Retired.
- `0.6.7.0`: full 60-glyph production codepage boots/renders.
- `0.6.7.2`: visual baseline PASS.
- `0.6.8.x`: insufficient gameplay coverage. Retired.
- `0.6.9.0` / `0.6.9.1`: gate bugs only. Do not retest.
- `0.6.9.2`: exact legacy reconstruction **397/397 COVERAGE PASS**.
- `0.6.10.0`: accented front/font runtime PASS; content QA incomplete.

## 0.6.11.0 runtime result

User runtime screenshots on 2026-09-14 prove that the accented pipeline remains active, but expose three concrete defects:

### 1. Intro old `=` positions still leak a wrong glyph

Visible cases include:

```text
Thế giới [wrong glyph] bàn cờ
Người [wrong glyph] cờ
```

Root cause: Batch 2 changed the accented front override but the dedicated old front fallback skeleton still contained:

```text
NGUOI=CO
THEGIOI=BANCO
```

### 2. Lowercase `ă` shape regression

In `năng`, the breve over `ă` is visibly wrong. This is the only demonstrated glyph regression that currently justifies reopening font pixels.

### 3. Remaining fallback/Japanese dynamic text

Runtime still shows examples such as:

```text
XONG!
LUOT ジガー
```

So there are both unaccented duplicate fallback strings and short runtime names outside the first translated occurrence.

Verdict:

```text
0.6.11.0 = PARTIAL PASS / CONTENT QA FAIL
```

Do not spend another tiny build only on one of these issues.

# CURRENT — 0.6.12.0 LARGE GAMEPLAY TRANSLATION BATCH 3

Design note:

```text
ACCENT_UPGRADE_0.6.12.0.md
```

Builder / launcher:

```text
tools/build_gaia_06120_big_translation_b3.py
tools/00_BUILD_0.6.12.0_BIG_TRANSLATION_B3.cmd
```

New data:

```text
translation/BATCH3_FALLBACK_ACCENT_MAP_0.6.12.0.csv
translation/DYNAMIC_LITERAL_OVERRIDES_0.6.12.0.csv
```

## Large-batch strategy

`0.6.12.0` deliberately combines hotfixes with a much larger translation expansion.

It wraps the proven `0.6.11.0 -> 0.6.10.0` production chain, so the exact 397/397 gate, BDP/checksum writer, token semantics and 60-character codepage remain the inner engine.

### Global fallback accent promotion

Batch 3 contains **278 manually curated fallback -> accented compact mappings**.

It also reuses every existing Batch 2 accent candidate globally. When another Translation Master row has the same `vi_game_current` fallback, the same accented wording is promoted if it fits that row's original CP932 field.

This covers substantially more:

```text
setup / tavern / gameplay / tax / land / route
card / item / weapon / event / menu / prompt
status fragments / building names / movement / battle text
```

Safety rule:

```text
accented target fits -> promote
accented target too long -> retain old fitting fallback
```

### Standalone repeated-literal scan

From the CLEAN extracted `SLPS_020.75` and `PRGPACK.BDP`, Batch 3 scans standalone/null-delimited copies of Japanese literals that already have a safe compact translation. Missing duplicate occurrences are injected as temporary translation rows for this build only.

This targets the class of bug where one known offset is translated but another runtime copy remains Japanese.

### Dynamic compact names

Current compact map:

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

The abbreviations are intentional because these source fields are very short.

### Intro fallback fix

Batch 3 fixes the actual old fallback data:

```text
NGUOI=CO      -> NGUOI CO
THEGIOI=BANCO -> THEGIOI BANCO
```

not just the front accent overlay.

### Targeted lowercase `ă` hotfix

After the inner build succeeds, Batch 3 reconstructs the frozen production custom-code allocation, finds the existing `ă` atlas slot and redraws only the top two breve rows as a shallow cup/smile.

No renderer change. No new glyph slot. No codepage expansion.

## Build state

```text
SOURCE READY
PYTHON SYNTAX PASS
CLEAN-ROM BUILD PENDING
RUNTIME PENDING
```

The clean game BIN is not mounted in the current ChatGPT runtime, so actual ROM generation must still happen on the user's machine.

## Next runtime gate

Prefer **one broad sweep**, not micro-tests:

1. intro: former `=` positions contain normal spaces, no Japanese-looking glyph;
2. setup: verify accented strings still render;
3. inspect `năng` or another word containing `ă`;
4. first several turns: `Lượt` where field allows it and no `ジガー`;
5. open cards/items/events/menus and exercise land/tax/route/battle actions;
6. screenshot every remaining Japanese string, no-accent fallback, clipping, broken diacritic or freeze.

## Hard do-not-repeat

- no production 12x16;
- no narrow alias path;
- no pointer redirect;
- no composite overlay;
- no global cursor/cache/spacing mutation;
- no `0.6.9.0` / `0.6.9.1` retests;
- no broad font retune from one bad glyph;
- never sacrifice fitting legacy fallback to force accents;
- stop immediately on freeze/global corruption.

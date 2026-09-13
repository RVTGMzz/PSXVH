# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** production stays on **native 12x12 / 72-byte / 4bpp / static mapping-only**. `0.6.9.2` remains exact **397/397 legacy coverage PASS**. `0.6.10.0` proved accented Vietnamese renders at runtime. `0.6.12.0` improved translation coverage but its lowercase `ă` hotfix is visually incomplete. Active candidate: **0.6.13.0 COMPACT JAPANESE REDUCTION BATCH 4**.

Updated: **2026-09-14**  
Branch: `gaia-character-select-font-atlas-reverse-01`

## Baselines

- Game: `GaiaMaster - Kamigami no Board Game (Japan).bin`
- serial: `SLPS-02075`
- clean BIN SHA1: `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- clean SLPS SHA1: `1dfeb6b7cfda59c108dde2dc0b8abda9a40e6ae5`
- clean PRGPACK SHA1: `a9b195b8ae5d8cad7f4f755daa08337d4671632c`
- repo: `ronvotri/Viet-Hoa-PS1`

## Architecture lock

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

Frozen production repertoire:

```text
àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ
```

Capacity:

```text
60 custom Vietnamese glyphs
64 conservative zero-hit atlas slots
4 reserve slots
```

## Coverage hard gate

Every production build must preserve:

```text
legacy Alpha coverage = 397 / 397
```

Extra newer `vi_full` rows are allowed. Runtime/control tokens such as `%s`, `%d`, `%+3d`, `/V`, `/v` remain raw where required.

Never sacrifice a fitting fallback merely to force a longer accented string.

## Runtime history relevant to current work

- `0.6.7.2`: visual baseline PASS. Do not broadly retune font.
- `0.6.9.2`: exact 397/397 coverage PASS.
- `0.6.10.0`: accented front/font runtime PASS.
- `0.6.11.0`: content QA fail; old `=` fallback leak, malformed `ă`, Japanese dynamic names.
- `0.6.12.0`: large translation Batch 3, intro/fallback work improved, but runtime screenshot shows lowercase `ă` still wrong and user reports too much Japanese remains.

## 0.6.12.0 lowercase `ă` diagnosis

Screenshot of `năng` proves the correct glyph slot is being reached, but v1 hotfix is visually wrong.

Root cause in v1 postpatch:

```text
fill = max(nonzero palette index)
```

Palette index `7` is the known dark/shadow layer, so the new breve could be drawn with the shadow color. Also only rows 0/1 were erased, allowing stale old-shadow pixels to remain in row 2.

This is a demonstrated glyph regression, so a targeted patch is justified. No other glyph should be reopened.

# CURRENT — 0.6.13.0 COMPACT JAPANESE REDUCTION BATCH 4

Design note:

```text
ACCENT_UPGRADE_0.6.13.0.md
```

Builder / launcher:

```text
tools/build_gaia_06130_translation_b4.py
tools/00_BUILD_0.6.13.0_TRANSLATION_B4.cmd
```

New data:

```text
translation/COMPACT_TRANSLATION_OVERRIDES_0.6.13.0.csv
translation/DYNAMIC_LITERAL_OVERRIDES_0.6.13.0.csv
```

## `ă` hotfix v2

After the proven inner build completes:

1. reconstruct exact frozen custom code/slot for `ă`;
2. derive bright fill from lower-body histogram, explicitly excluding shadow index `7`;
3. clear rows 0/1 in the mark band;
4. clear only shadow-colored stale pixels from row 2;
5. draw a **lower shallow cup** in the bright fill;
6. draw native shadow one pixel down/right;
7. regenerate changed MODE2 sector EDC/ECC.

No new slot, no mapping change, no renderer change, no other glyph patch.

## Translation Batch 4

`COMPACT_TRANSLATION_OVERRIDES_0.6.13.0.csv` contains **146 exact-offset compact candidates**.

Purpose: convert rows that can remain Japanese because their longer Vietnamese wording does not fit fixed CP932 fields.

Areas targeted:

```text
land / buy / sell / tax
card and weapon acquisition
battle prompts
route/status strings
special squares
building/symbol effects
item/card descriptions
```

Safety:

```text
candidate fits original field -> promote to vi_full for build
candidate too long -> skip safely
```

## Dynamic Japanese reduction

`DYNAMIC_LITERAL_OVERRIDES_0.6.13.0.csv` expands the runtime literal map from 12 to **35 entries**.

It keeps existing character names and adds weapon/card/location names that may appear through `%s` or duplicated standalone data.

Examples:

```text
サンダー -> Sấm
ハリケーン -> Bão
クロスボウ -> Nỏ
ロングソード -> Kiếm
ハンマー -> Búa
ファイアボール -> Lửa
バトルアックス -> Rìu
サーカス -> Xiếc
呪いの沼 -> Đầm
```

## Build state

```text
SOURCE READY
PYTHON SYNTAX PASS
CLEAN-ROM BUILD PENDING
RUNTIME PENDING
```

The clean BIN is not mounted in ChatGPT runtime. Build from the user's CLEAN Japan BIN.

## Next runtime gate

Do one broad test:

1. inspect `ă` in `năng` or another visible word;
2. verify no new font/global corruption;
3. play several turns;
4. open card/item/event/menu screens;
5. exercise land/tax/route/battle actions;
6. screenshot remaining Japanese whole lines and Japanese `%s` names.

## Hard do-not-repeat

- no production 12x16;
- no narrow alias path;
- no pointer redirect;
- no composite overlay;
- no global cursor/cache/spacing mutation;
- no broad font retune from one glyph;
- no `0.6.9.0 / 0.6.9.1` retests;
- stop immediately on freeze/global corruption.

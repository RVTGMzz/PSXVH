# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** production stays on **native 12x12 / 72-byte / 4bpp / static mapping-only**. `0.6.9.2` remains exact **397/397 legacy coverage PASS**. `0.6.10.0` proved accented Vietnamese renders at runtime. `0.6.13.0` reduced Japanese content further but the lowercase `ă` hotfix still visually overlaps the old breve. Active candidate: **0.6.14.0 TRANSLATION BATCH 5 + FRESH `ă` REBUILD**.

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

No renderer hook, pointer redirect, 12x16, narrow 6x12 or global spacing mutation.

## Production codepage

Frozen 60-character set:

```text
àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ
```

Capacity baseline:

```text
60 custom Vietnamese glyphs
64 conservative zero-hit atlas slots
4 reserve slots
```

## Coverage hard gate

Every production build after `0.6.9.2` must preserve:

```text
legacy Alpha coverage = 397 / 397
```

Runtime/control tokens such as `%s`, `%d`, `%+3d`, `/V`, `/v` remain raw where required. Never sacrifice a fitting fallback merely to force a longer accented string.

## Runtime history relevant to current work

### 0.6.10.0

Accented front/font runtime PASS. Content QA still incomplete.

### 0.6.11.0

Gameplay Accent Batch 2. Runtime exposed:

- old `=` fallback leak in intro;
- malformed lowercase `ă`;
- mixed Japanese dynamic values such as `LUOT ジガー`.

### 0.6.12.0

Large translation Batch 3. Intro fallback cleanup and broader translation improved. First targeted `ă` redraw still visually wrong.

### 0.6.13.0

Batch 4 added 146 compact exact-offset candidates and expanded dynamic literals to 35. Runtime screenshot proves the `ă` patch still leaves the old breve/shadow underneath the new one. The result looks double-layered.

This is now classified as:

```text
0.6.13.0 = CONTENT PROGRESS / LOWERCASE ă HOTFIX V2 FAIL VISUALLY
```

Do not keep erasing guessed top rows.

# CURRENT — 0.6.14.0 TRANSLATION BATCH 5 + FRESH `ă` REBUILD

Files:

```text
ACCENT_UPGRADE_0.6.14.0.md
tools/build_gaia_06140_translation_b5.py
tools/00_BUILD_0.6.14.0_TRANSLATION_B5.cmd
translation/COMPACT_TRANSLATION_OVERRIDES_0.6.14.0.csv
translation/DYNAMIC_LITERAL_OVERRIDES_0.6.14.0.csv
```

## Fresh lowercase `ă` strategy

The new builder does **not mutate the previous `ă` bitmap**.

It instead:

1. reads CLEAN native full-width lowercase `a`;
2. reconstructs the frozen custom code/slot for `ă`;
3. builds a new compact body from the clean `a` glyph;
4. draws exactly one shallow-U breve and native shadow;
5. replaces the entire custom `ă` bitmap.

Therefore old breve/shadow pixels from 0.6.12/0.6.13 cannot survive.

## Translation Batch 5

Adds 38 exact-offset compact candidates, including:

```text
Thẻ SK
Dừng: SK
Đấu đối thủ
Vô chủ
Quỹ %5d
Phí %4d
Lượt %s
Dừng %s
Đất %s
Thuế TN
Ô thuế đất
Đồng ý?
Có/Không
Chọn thẻ
Dùng %s
```

Candidate only applies if it fits the original CP932 field.

Dynamic literal map keeps earlier names/items and adds additional safe standalone forms such as:

```text
墓地   -> Mộ
大聖堂 -> Đền
通行税 -> Phí
```

## Build chain

```text
0.6.14.0 -> 0.6.13.0 -> 0.6.12.0 -> 0.6.11.0 -> 0.6.10.0
```

So earlier translation work and the exact 397/397 gate remain intact.

## Next runtime gate

First inspect `năng`:

- exactly one breve over `ă`;
- no old cap/hat underneath;
- no doubled shadow;
- readable body alignment.

Then play a broader sweep and capture remaining Japanese strings in batches. Continue large translation batches rather than micro-fixes.

## Hard do-not-repeat

- no production 12x16;
- no narrow alias;
- no pointer redirect;
- no composite overlay;
- no global cursor/cache/spacing mutation;
- no `0.6.9.0 / 0.6.9.1` retest;
- no broad font retune beyond demonstrated glyph defects;
- stop immediately on freeze/global corruption.

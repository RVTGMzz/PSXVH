# HANDOFF — Gaia Master PS1 Việt hóa

Updated: 2026-09-14
Branch: `gaia-character-select-font-atlas-reverse-01`

## Current source-of-truth

Production remains locked to the native font architecture:

```text
12x12 / 72-byte / 4bpp
static mapping-only
legacy Alpha coverage gate = 397/397
```

The font is now accepted at runtime. Active work is content expansion and removal of remaining Japanese strings.

## Current candidate

**0.6.19.0 — Story / Dialog / Menu / Card Batch 10**

Checkpoint artifact in repo:

```text
checkpoints/0.6.19.0/GaiaMaster_0.6.19.0_BATCH10_STORY_DIALOG_MENU_CARD.zip
```

This archive contains only the standalone builder/checkpoint files, never a game image.

## Important history

- `0.6.9.2`: exact 397/397 legacy coverage PASS.
- `0.6.10.0`: accented Vietnamese rendered at runtime.
- `0.6.11.0`: exposed intro separator leakage, broken lowercase `ă`, and dynamic Japanese values.
- `0.6.12.0` → `0.6.13.0`: larger translation batches; early `ă` hotfixes still failed visually.
- `0.6.14.0` / `0.6.14.1`: fresh lowercase `ă` rebuild from clean native `a`; later runtime feedback accepted the font as visually OK. `0.6.14.1` also replaced unsupported lowercase `ý` in a prompt with codepage-safe `Được?`.
- `0.6.15.0` → `0.6.18.0`: content-first standalone batches added intro cleanup, fantasy tone, menu/card/item/event/weapon translations, and more dynamic literals.
- `0.6.19.0`: Japanese-first semantic pass focused on story, dialogue, menu, cards, weapons/items, event text, and fantasy terminology.

The repository branch physically stopped at `0.6.14.1` while Batches 6–10 were being distributed as standalone builders. This handoff records that gap explicitly; `0.6.19.0` is the new recovery checkpoint.

## Translation policy

1. Translate from the Japanese source first whenever possible.
2. Prefer full natural Vietnamese if it fits the original field.
3. If too long, use a compact version that keeps the meaning.
4. Preserve runtime tokens such as `%s`, `%d`, `%4d`, `%+3d`, `/V`, `/v`.
5. Never sacrifice the 397/397 gate to force a longer string.

## Tone guide

Readable medieval fantasy, not excessively archaic.

Preferred vocabulary includes:

```text
lãnh địa
lộ phí
quân quỹ
Thánh địa
Ma vương
Tà thần
Thần Thời
Thần Vận
tỉ thí
chiến lợi
Sứ giả
Pháp sư
Đạo tặc
```

NPC challenge dialogue may use `ta / ngươi` where appropriate. Technical settings/menu text stays clear and practical.

## Intro cleanup

Keep the old separator skeleton out of production:

```text
NGUOI=CO      -> NGUOI CO
THEGIOI=BANCO -> THEGIOI BANCO
```

Accented targets:

```text
Người cờ
Thế giới bàn cờ
```

## Production font / codepage lock

Frozen 60-character production set remains unchanged:

```text
àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ
```

Do not reintroduce 12x16, narrow 6x12, renderer hooks, pointer redirects, composite overlays, or global spacing changes.

## Runtime status

`0.6.19.0` is a candidate, not a PASS, until tested in-game.

Next QA priority:

- story / intro sequences;
- long NPC dialogue;
- tavern dialogue;
- card list + card descriptions;
- weapon/item descriptions;
- mid-match menus;
- event / Ma vương sequences;
- any remaining Japanese or mixed Japanese/Vietnamese text.

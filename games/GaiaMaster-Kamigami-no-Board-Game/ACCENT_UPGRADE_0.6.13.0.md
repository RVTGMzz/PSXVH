# Gaia Master 0.6.13.0 — Compact Japanese Reduction Batch 4

Updated: **2026-09-14**

## Goal

`0.6.12.0` runtime proved the lowercase `ă` slot was being patched, but the mark still looked wrong:

- the 0.6.12 hotfix picked the dark shadow palette as the breve fill;
- part of the previous mark shadow could survive into row 2;
- the visible breve therefore looked dark/high instead of a clean bright cup.

`0.6.13.0` keeps the production architecture and fixes only this demonstrated regression while continuing translation work.

## Architecture lock

Unchanged:

```text
native main font 12x12 / 72-byte / 4bpp
static mapping-only
60-glyph Vietnamese production codepage
exact legacy Alpha coverage = 397 / 397
no renderer hook
no pointer redirect
```

## Lowercase ă hotfix v2

Post-build patch policy:

1. reconstruct the exact frozen code and atlas slot for `ă`;
2. derive native bright fill from the glyph histogram while excluding shadow index `7`;
3. remove the old top-mark pixels and stale row-2 shadow;
4. draw a lower shallow breve in the bright fill;
5. draw the native shadow one pixel down/right;
6. regenerate changed MODE2 sector ECC/EDC.

No other production glyph is touched.

## Translation Batch 4

New data:

```text
translation/COMPACT_TRANSLATION_OVERRIDES_0.6.13.0.csv
translation/DYNAMIC_LITERAL_OVERRIDES_0.6.13.0.csv
```

The compact table contains **146 candidates** targeted at rows which can remain Japanese when the longer Vietnamese wording does not fit the fixed field.

Areas covered include:

```text
buy/sell/land
taxes
event/card acquisition
battle prompts
route changes
status text
special squares
symbol/building effects
item/card descriptions
```

Every candidate is byte-fit checked. Too-long text is skipped rather than forced.

The dynamic table expands to **35 literals**, adding weapon/card names and short board/location labels which may be supplied through `%s` or duplicated outside the normal translated row.

Examples:

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

## Runtime gate

Test broadly, not only the intro:

1. verify `ă` in words such as `năng` has a bright low breve and normal shadow;
2. enter gameplay and inspect menus/cards/items/events;
3. note any remaining Japanese whole line;
4. note any Japanese name embedded inside Vietnamese `%s` text;
5. stop immediately on freeze/global corruption.

This is still a runtime candidate, not final.

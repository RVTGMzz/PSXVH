# Gaia Master 0.6.21.0 — Batch 12 Deep Story / Card / Item

Updated: 2026-09-14

## Focus

Batch 12 continues the Japanese-first content sweep. The font remains locked and is not retuned.

Primary additions:

- defensive items and disposable defense;
- sealed magic / Dark Meteor / Excalibur / legendary weapons;
- revival, healing, drain, critical and item-seal effects;
- card exchange;
- area ownership / ownership transfer / hospital fee messages;
- Ma vương shop-destruction event text;
- symbol/building card help;
- extra dynamic literals for equipment, buildings and card names.

## Scale

```text
story/front mappings  = 19
Japanese semantic map = 309
fantasy fallback map  = 256
dynamic literals      = 86
```

Batch 12 delta:

```text
Japanese semantic new/edited = 92
fantasy fallback new/edited  = 64
dynamic literals new/edited  = 15
```

## Tone

Readable medieval fantasy:

```text
lãnh địa
lộ phí
Thánh địa
Ma vương
Tà thần
Thần Thời
Thần Vận
thánh kiếm
ma pháp
phong ấn
tỉ thí
```

Technical menus remain clear and practical.

## Safety

- preserve `%s`, `%d`, `%4d`, `%+3d`;
- only promote translations that fit the original fixed field;
- keep native 12x12 / 72-byte / 4bpp font path;
- keep static mapping-only architecture;
- exact legacy coverage gate remains 397/397;
- intro separator cleanup remains active.

## Runtime status

`0.6.21.0` is a candidate until tested in-game.

Priority QA:

1. story / intro;
2. tavern and NPC dialogue;
3. card list and card help;
4. weapon / item / magic descriptions;
5. area ownership / tax / hospital / Ma vương events;
6. remaining Japanese or mixed Japanese/Vietnamese strings.

# Gaia Master Reverse Workbench 0.1

Date: 2026-09-15
Branch: `gaia-character-select-font-atlas-reverse-01`

## Status

This is a **source-only / read-only reverse-workbench addition**.

It does **not** bump the production localization version and does **not** change the current runtime verdict.

Current production checkpoint remains:

- `0.6.55.0 / Batch45 Front-Face Runtime Polish`
- static/package state only
- **NOT Runtime PASS until gameplay screenshots are inspected**

Last actual clean-ROM production proof remains the R5 / `0.6.54.0` chain:

```text
Batch42 exact       = 560 / 560
Batch43 visible     = 102 / 102
Combined exact      = 662 / 662
Legacy Alpha        = 397 / 397
Translation Master = 596 / 596
```

## Architecture lock

Do not change any of these while using the workbench:

- native `12x12 / 72-byte / 4bpp / low-nibble-first` font;
- mapping-only architecture;
- frozen 60-glyph Vietnamese codepage;
- no renderer hook;
- no pointer redirect;
- no 12x16 path;
- no 6x12 path;
- preserve runtime token identity/order;
- preserve the R5 exact-overlap and CLEAN-source gates.

## Why this workbench exists

The broad Japanese scanner used for Batch43 is a CP932/text scanner. It scans text-like ranges in `PRGPACK.BDP` and `SLPS_020.75`, but it does not inventory image/texture assets.

Runtime screenshots after `0.6.54.0` still showed Japanese in:

- Main Menu;
- Character Select header/names/description;
- Story dialogue;
- chapter/title card;
- land-purchase prompt;
- other gameplay/help paths.

The remaining Main Menu / Character Select labels may therefore belong to a graphic or texture path even though some nearby Character Select setup strings are proven text-backed.

Known Character Select text anchor:

```text
PRGPACK.BDP + 0xBFD2C
owner = nested BDP entry 29
owner-local = +0x580
source = キャラクターをえらんでね
```

## Tool 1: Graphic Asset Census

Path:

`tools/gaia_graphic_asset_census_0.1.py`

Purpose:

1. verify the exact CLEAN Japan BIN;
2. extract clean `SLPS_020.75` and `PRGPACK.BDP` in memory;
3. enumerate all top-level PRGPACK nested BDP owners;
4. find structurally valid standard PS-X TIM candidates;
5. map PRGPACK TIM candidates back to their BDP owner/local offset;
6. highlight owner 29 and candidates near the proven Character Select text offsets.

Run:

```text
python tools/gaia_graphic_asset_census_0.1.py "Gaia Master CLEAN.bin"
```

Outputs next to the CLEAN BIN:

```text
GaiaMaster_GRAPHIC_ASSET_CENSUS_0.1_OWNERS.csv
GaiaMaster_GRAPHIC_ASSET_CENSUS_0.1_TIM.csv
GaiaMaster_GRAPHIC_ASSET_CENSUS_0.1_REPORT.txt
```

Interpretation:

- `CHAR_SELECT_OWNER_NEAR_TEXT` is the first-priority TIM set to inspect.
- Other TIMs inside owner 29 are second priority.
- A structurally valid TIM hit is only an asset candidate, not proof that the screenshot label comes from it.
- If owner 29 contains no useful standard TIM, continue toward raw/custom/compressed graphic discovery rather than forcing the normal CP932 text path.
- The tool is read-only and never patches the BIN.

## Tool 2: Runtime Target Locator

Path:

`tools/gaia_runtime_target_locator_0.1.py`

Purpose:

Locate exact visible Japanese copied from gameplay screenshots in the CLEAN ROM before promoting anything into a translation batch.

Default target:

```text
冒険のはじまり
```

This is the runtime-proven chapter/title-card text seen after `0.6.54.0`.

Run default target:

```text
python tools/gaia_runtime_target_locator_0.1.py "Gaia Master CLEAN.bin"
```

Run screenshot-derived targets:

```text
python tools/gaia_runtime_target_locator_0.1.py "Gaia Master CLEAN.bin" "日本語その1" "日本語その2"
```

Output:

```text
GaiaMaster_RUNTIME_TARGET_LOCATOR_0.1_REPORT.txt
```

For each exact CP932 hit the report gives:

- file;
- exact offset;
- nested BDP owner where applicable;
- owner-local offset;
- nearest NUL-terminated field length where detectable;
- diagnostic CP932 context.

A locator hit is **not automatically safe to patch**. Production promotion still requires the proven R5/Batch43 gates:

1. source identity against CLEAN ROM;
2. correct nested BDP owner boundary;
3. NUL/fixed-field boundary proof;
4. encoded Vietnamese must fit the existing byte budget;
5. frozen 60-glyph codepage only;
6. runtime token identity/order preserved;
7. no overlap with the 560 Batch42 exact fields;
8. nested/top BDP checksum and raw-sector EDC/ECC regeneration;
9. gameplay screenshot verification after build.

## Current reverse order

Until Batch45 runtime evidence arrives, reverse work can continue read-only in this order:

1. Main Menu graphic/asset discovery;
2. Character Select graphic/asset discovery, starting from owner 29;
3. exact locator for `冒険のはじまり`;
4. feed exact Japanese Story / land-purchase screenshot strings into the locator;
5. only after target ownership/field safety is proven, prepare the next curated exact-offset batch.

Do **not** create a production Batch46 merely from scanner/static evidence while Batch45 runtime is still unresolved.

## Batch45 runtime lock checklist

When `0.6.55.0` FINAL_REPORT + gameplay screenshots arrive, inspect before changing status:

- intro wording is readable/natural enough;
- no garbage glyph from the removed `=` usage;
- `Đ/đ` crossbar is visibly one pixel higher and acceptable;
- no freeze, corrupted menus, or global font damage;
- previously proven routes remain intact;
- the exact build/report still shows the expected 662 combined contract.

Only then may intro/font be marked locked and development proceed to the next production batch.

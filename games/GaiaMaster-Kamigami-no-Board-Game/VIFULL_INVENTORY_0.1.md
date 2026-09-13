# Gaia Master — vi_full Inventory 0.1

Current production direction is locked to the last-good `0.6.6.1` architecture:

```text
native 12x12 / 72-byte / 4bpp
static mapping-only
no runtime hook
no pointer redirect
```

## Why this scanner exists

`Production Capacity Scanner 0.1` tested the stronger worst-case target of the full Vietnamese precomposed repertoire:

```text
134 custom glyphs required
837 zero-static-hit custom codes available
64 conservative zero-static-hit atlas slots available
34 of those completely unmapped
```

Result: full 134-glyph worst-case codepage does not fit while preserving all currently referenced Japanese glyphs.

This is a valid capacity failure, not a build/runtime failure.

## vi_full Inventory 0.1

Files:

```text
tools/vifull_inventory_0.1.py
tools/00_RUN_VIFULL_INVENTORY_0.1.cmd
```

The scanner reads `TRANSLATION_MASTER_0.6_part01..part06.csv` from branch `gaia-character-select-font-atlas-reverse-01` and inventories only non-empty `vi_full` rows.

It reports:
- exact unique Vietnamese precomposed characters currently used;
- lowercase/uppercase split;
- frequency per custom character;
- Unicode punctuation that can be normalized to ASCII;
- other non-ASCII symbols needing an encoder policy;
- PASS/FAIL against the known conservative 64-slot atlas capacity.

Expected report:

```text
GaiaMaster_ViFullInventory_01.txt
```

## Gate

If current `vi_full` custom glyph need is `<=64`:
- freeze an exact current-corpus production codepage;
- allocate deterministic `Unicode -> custom CP932 code -> atlas slot` entries;
- build a multi-string real-translation proof on the proven 12x12 pipeline.

If current `vi_full` custom glyph need is `>64`:
- do not revive narrow/12x16/composite paths;
- reclaim only Japanese slots whose remaining occurrences are fully covered by translated rows;
- expand codepage incrementally with explicit provenance.

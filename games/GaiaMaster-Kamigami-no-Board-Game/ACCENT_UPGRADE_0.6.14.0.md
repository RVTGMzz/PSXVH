# Gaia Master 0.6.14.0 — Translation Batch 5 + Fresh `ă` Rebuild

Updated: **2026-09-14**

## Runtime trigger

User screenshot from `0.6.13.0` proves the lowercase `ă` hotfix still contains overlapping mark pixels. The old breve was not fully removed before the replacement mark was drawn, so the result looks double-layered.

This is now treated as a **single-glyph reconstruction problem**, not another row-erasing problem.

## Architecture remains locked

- native main font `12x12 / 72-byte / 4bpp / LOW nibble first`;
- static mapping-only route;
- production 60-glyph Vietnamese codepage;
- exact Alpha legacy coverage gate `397 / 397`;
- no renderer hook;
- no pointer redirect;
- no 12x16 or 6x12 production path.

## Lowercase `ă` v3

`0.6.14.0` does **not** mutate the already-patched `ă` bitmap.

Instead it:

1. reads the CLEAN native full-width lowercase `a` glyph;
2. reconstructs the existing frozen custom code and destination slot for `ă`;
3. builds a fresh compact lowercase `a` body from clean source pixels;
4. draws exactly one shallow-U breve and one native shadow;
5. replaces the entire destination `ă` glyph bitmap.

Therefore old cap/hat/breve pixels from 0.6.12/0.6.13 cannot remain underneath the new accent.

## Translation Batch 5

New exact-offset compact overrides:

```text
translation/COMPACT_TRANSLATION_OVERRIDES_0.6.14.0.csv
```

Current Batch 5 adds 38 additional compact candidates, concentrating on:

- gameplay/help fragments around PRGPACK `0x68E18..0x68EE8`;
- early board/gameplay strings in `SLPS_020.75`;
- accented `Lượt %s`, `Dừng %s`, `Đất %s`, tax/land/event prompts;
- several rows that were still likely to remain Japanese when the longer `vi_full` string did not fit.

Every candidate is still gated by the original CP932 field length. Too-long strings are skipped rather than forced.

## Dynamic literal expansion

```text
translation/DYNAMIC_LITERAL_OVERRIDES_0.6.14.0.csv
```

Batch 5 keeps the previous 35 compact runtime literals and adds additional safe standalone forms such as:

```text
墓地   -> Mộ
大聖堂 -> Đền
通行税 -> Phí
```

## Build chain

```text
0.6.14.0
  -> 0.6.13.0
  -> 0.6.12.0
  -> 0.6.11.0
  -> 0.6.10.0
```

So all earlier translation work, checksum logic, token handling and the exact `397/397` gate remain intact.

## Runtime gate

Test broadly, but first inspect a word containing lowercase `ă`, especially:

```text
năng
```

Expected:

- exactly one breve;
- no old cap/hat underneath;
- no doubled shadow;
- body remains readable and aligned.

Then continue through board/gameplay/help/card/item/event screens and capture remaining Japanese strings in batches.

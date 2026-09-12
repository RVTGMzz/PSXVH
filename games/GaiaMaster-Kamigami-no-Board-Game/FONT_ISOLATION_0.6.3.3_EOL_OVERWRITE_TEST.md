# Gaia Master — Font Isolation 0.6.3.3 EOL OVERWRITE TEST

Prepared: **2026-09-12**
Status: **BUILT / awaiting runtime result**

## Why this probe exists

0.6.3.2 is stable but the bottom of the 12x16 target glyph is missing while a normal full-width `Ａ` follows it.

The strongest current hypothesis is that the following native glyph overwrites the final four converted rows because the shared cache cursor still advances only 12 rows even though the target wrote 16 rows.

## One-variable design

0.6.3.2 control:

```text
ＴＥＳＴ亜Ａ
```

0.6.3.3 control:

```text
ＴＥＳＴ亜
```

The target is deliberately the **last glyph on the line**.

Nothing else structural changes.

## Unchanged from 0.6.3.2

- 12x16 / 96-byte target source glyph;
- 16-row target copy/unpack path;
- 16-pixel target visible height;
- target baseline correction `Y -= 4 px`;
- native Japanese/Latin remains 12x12;
- no shared cache RAM pointer rewrite;
- no VRAM Y cursor rewrite;
- no patch to `0x8003CD94..0x8003CDB4`.

## Exact diagnostic question

> Does the missing lower part of the 16-row target return when no following glyph exists to overwrite its converted/cache footprint?

## Interpretation matrix

### Result A — bottom returns

Then the current model is strongly confirmed:

```text
extended target writes 128 converted bytes
native cursor advances only 96 bytes
next native glyph starts 32 bytes too early
next glyph overwrites target rows 12..15
```

Production implication:

- do not globally mutate the shared native cache cursor;
- design an isolated target cache/destination path for extended Vietnamese glyphs;
- preserve native shared allocator state.

### Result B — bottom still missing

Then following-glyph overwrite is not the full explanation.

Reverse next:

1. target copy destination footprint;
2. source row count actually consumed by `0x8003C67C`;
3. destination texture upload height;
4. descriptor/primitive visible height;
5. UV/texture window / clipping behavior;
6. any post-upload clearing or cache compaction.

## Safety

0.6.3.3 intentionally avoids the unsafe shared-state patch from 0.6.3.1.

If unrelated Japanese text corrupts or the game freezes, stop immediately and treat that as a new regression.

## Package produced

Local test package name:

```text
GaiaMaster_FontIsolation_0.6.3.3_EOL_OVERWRITE_TEST.zip
```

Launcher:

```text
00_RUN_PROBE_0633.cmd
```

Do not confuse this with 0.6.3.1 or 0.6.3.2 during future handoffs.

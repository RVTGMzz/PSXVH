# Gaia Master — Font Isolation 0.6.3.3 EOL OVERWRITE TEST

Runtime test date: **2026-09-12**
Status: **RUNTIME COMPLETE — FOLLOWING-GLYPH OVERWRITE DISPROVEN**

## Why this probe existed

0.6.3.2 was stable but the bottom of the 12x16 target glyph was missing while a normal full-width `Ａ` followed it.

Hypothesis:

```text
16-row target writes 128 converted bytes
native cursor advances 96 bytes
following glyph may start 32 bytes / 4 rows too early
```

## One-variable design

0.6.3.2:

```text
ＴＥＳＴ亜Ａ
```

0.6.3.3:

```text
ＴＥＳＴ亜
```

Target is the last glyph on the line.

Unchanged:

- 12x16 / 96-byte target source;
- 16-row metadata/copy path;
- 16-pixel visible-height request;
- baseline Y `-4`;
- no shared cache RAM pointer rewrite;
- no VRAM cursor rewrite;
- no patch to `0x8003CD94..0x8003CDB4`.

## Runtime result

Result is essentially the same as 0.6.3.2:

- Japanese header normal;
- `ＴＥＳＴ` normal;
- target stable;
- no global corruption/freeze;
- lower target rows still missing/cut.

=> Removing the following glyph does **not** restore the target bottom.
=> Following-glyph overwrite is disproven.

Do not retest 0.6.3.3.

## Consequence

The loss is internal to target copy/cache/upload/draw behavior, not caused by a later normal glyph overwriting the target.

Next historical probe was 0.6.3.4 UV WINDOW TEST.

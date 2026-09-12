# Gaia Master — Font Isolation 0.6.3.2 BASELINE ONLY — STABLE PASS

Runtime test date: **2026-09-12**

## Purpose

Isolate the 0.6.3.1 regression source by returning to the structurally-safe 0.6.3.0 12x16 path and adding **only baseline correction**.

Do not touch the shared cache allocator/cursor block around `0x8003CD94..0x8003CDB4`.

Control string:

```text
ＴＥＳＴ亜Ａ
```

Target intent:

```text
ＴＥＳＴẾＡ
```

The trailing full-width `Ａ` is a sentinel to observe what happens immediately after an extended target glyph.

## Changes from 0.6.3.0

Kept:

- target 12x16 / 96-byte source glyph;
- target copy/unpack height = 16 rows;
- target visible sprite height = 16;
- untouched Japanese/Latin remains on the native 12x12 path.

Added only:

```text
target visible Y -= 4 px
```

Removed / intentionally absent:

- no shared cache RAM pointer advance rewrite;
- no VRAM Y cursor advance rewrite;
- no patch to `0x8003CD94..0x8003CDB4`.

## Runtime result

**STABLE PASS with lower-row loss.**

User screenshot confirms:

- Japanese Character Select header renders normally;
- full-width `ＴＥＳＴ` is normal;
- extended target glyph renders and its baseline is substantially improved;
- trailing full-width `Ａ` is intact;
- unrelated text does not corrupt;
- no later freeze was reported for this build;
- however the lower part / final rows of the 12x16 target glyph are missing or cut.

## Conclusions

### Baseline correction is safe

The target-only `Y -= 4 px` correction does not reproduce the 0.6.3.1 global corruption.

Therefore the baseline experiment is not the cause of the 0.6.3.1 regression.

### 0.6.3.1 regression points to shared cache stride mutation

0.6.3.1 additionally rewrote shared converted-cache / VRAM cursor advance at:

```text
0x8003CD94 .. 0x8003CDB4
```

0.6.3.2 leaves that block native and global text stability returns.

This strongly implicates the shared cache-advance rewrite as the unsafe change.

## Strong next hypothesis — following-glyph overwrite

Known wide-glyph conversion geometry:

```text
6 source bytes per row -> 8 converted/cache bytes per row
```

Therefore:

```text
12 rows -> 96 converted bytes
16 rows -> 128 converted bytes
```

In 0.6.3.2 the target writes 16 converted rows, but the shared native cursor still advances only 12 rows.

That means the following native glyph may start 32 bytes / 4 rows too early and overwrite the extended target's last four converted rows.

This matches the screenshot pattern:

- upper/head/body of target exists;
- target lower portion is missing;
- following `Ａ` itself remains intact.

This is a **strong hypothesis, not yet proven**.

## Next diagnostic

Build **0.6.3.3 EOL OVERWRITE TEST** with the target at end-of-line:

```text
ＴＥＳＴ亜
```

No trailing glyph.
No new renderer hook.
No cache-stride rewrite.

Question:

> If no glyph follows, does the missing bottom of the 16-row target return?

Interpretation:

- bottom returns => following-glyph overwrite confirmed;
- bottom still missing => clipping/copy/display limitation exists inside the target path itself.

## Do-not-repeat rules

- do not retest 0.6.3.1;
- do not reintroduce the naive shared `CD94` stride patch;
- do not return to production 12x12 stacked-diacritic polishing;
- do not treat the missing bottom as proven clipping until 0.6.3.3 is runtime-tested.

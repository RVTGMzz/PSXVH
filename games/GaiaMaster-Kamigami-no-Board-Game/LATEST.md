# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-12 sau runtime test 0.6.3.6 EARLY-FLAG POST-COPY SENTINEL**.

## Chốt hiện tại

- 0.6.2.x: custom Vietnamese glyph pipeline đã PASS.
- Native 12x12 bị loại cho production stacked Vietnamese diacritics vì quá chật.
- 0.6.3.0 12x16 = **STRUCTURAL PASS**.
- 0.6.3.1 shared cache-stride rewrite = **UNSAFE FAIL**: global corruption + freeze.
- 0.6.3.2 = **STABLE PASS** nhưng lower rows mất/cắt.
- 0.6.3.3 = overwrite hypothesis disproven.
- 0.6.3.4 = UV+4 negative diagnostic.
- 0.6.3.5 = sentinel not observed; late `s0` target check unreliable.
- **0.6.3.6 = UNSAFE FAIL: game freezes immediately after Sony logo.**

## 0.6.3.6 runtime result

0.6.3.6 introduced one new architectural idea:

```text
metadata stage: target 0x889F -> persistent FLAG=1
other glyphs                 -> FLAG=0
late post-copy hook reads FLAG, not s0
```

Runtime:

- game reaches Sony logo;
- then freezes before Character Select;
- repeated test gives same freeze;
- therefore no sentinel result exists and rows12..15 cannot be inferred from this build.

=> **Never retest 0.6.3.6.**

Strongest suspect is the new persistent runtime state / early metadata rewrite, not the previously stable 12x16 source itself. A file region being zero-filled does not prove it is safe as mutable runtime storage.

## Proven font facts retained

```text
atlas file   = SLPS + 0x5C4EC
mapping file = SLPS + 0x6B6CC
atlas RAM    = 0x8006BCEC
mapping RAM  = 0x8007AECC
native 12x12 / 72-byte / 4bpp / LOW nibble first
```

Wide custom copy routine:

```text
0x8003C67C
6 source bytes/row -> 8 converted bytes/row
12 rows -> 96 converted bytes
16 rows -> 128 converted bytes
```

Metadata height=15 drives 16 copy iterations.

## NEXT REVERSE DIRECTION

Do **not** build another persistent-flag probe.

Return to the stable 0.6.3.5/0.6.3.3 path and identify the target at/inside the copy pipeline without new shared/global state.

Preferred next strategies, in order:

1. identify target by the unique extended source glyph pointer / metadata source pointer already present in the copy call;
2. if necessary, hook inside `0x8003C67C` where the actual source pointer and row loop are live;
3. use a target/source-pointer-local sentinel there, avoiding late `s0` and avoiding persistent RAM flags;
4. only build the next ROM after exact registers/arguments are proven.

## Hard do-not-repeat

- no Krom path;
- no production 12x12 stacked-accent polishing;
- no retest 0.6.2.18;
- no retest 0.6.3.0..0.6.3.6;
- no shared `0x8003CD94..0x8003CDB4` allocator rewrite;
- no persistent target FLAG in the 0.6.3.6 style.

## After extended-height path is stable

1. production-safe Vietnamese extended atlas/cache storage;
2. full Vietnamese glyph inventory;
3. compact runtime codepage/mapping;
4. encode `vi_full` có dấu;
5. solve/repack 230 pending rows;
6. clean mixed JP/VI;
7. graphic menu/title patch;
8. full runtime QA + reproducible build.

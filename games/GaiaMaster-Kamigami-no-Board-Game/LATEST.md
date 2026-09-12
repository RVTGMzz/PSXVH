# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-12 sau runtime 0.6.3.6 UNSAFE FAIL; current probe = 0.6.3.7 SOURCE ROW SENTINEL**.

## Chốt hiện tại

- 0.6.2.x: custom Vietnamese glyph pipeline đã PASS.
- Native 12x12 bị loại cho production stacked Vietnamese diacritics vì quá chật.
- 0.6.3.0 12x16 = **STRUCTURAL PASS**.
- 0.6.3.1 shared cache-stride rewrite = **UNSAFE FAIL**.
- 0.6.3.2 = **STABLE PASS** nhưng lower rows mất/cắt.
- 0.6.3.3 = following-glyph overwrite disproven.
- 0.6.3.4 = UV+4 negative diagnostic.
- 0.6.3.5 = post-copy sentinel not observed; late `s0` identity unreliable.
- 0.6.3.6 = **UNSAFE FAIL: freezes immediately after Sony logo**.

## 0.6.3.6 lesson

0.6.3.6 introduced a persistent early target FLAG stored in cave memory. Runtime freezes before Character Select, repeated twice.

=> never retest.
=> do not carry target identity with persistent/global mutable state.

Dedicated note:

```text
FONT_ISOLATION_0.6.3.6_UNSAFE_FAIL.md
```

## Current probe — 0.6.3.7 SOURCE ROW SENTINEL

0.6.3.7 avoids all late target-identity machinery.

Start from stable extended path:

- target 12x16 / 96-byte source;
- copy height = 16 rows;
- sprite height = 16;
- baseline Y -= 4;
- target at EOL;
- no `CD94` allocator rewrite;
- no UV+4;
- no post-copy sentinel hook;
- no persistent FLAG;
- no late `s0` test.

Diagnostic is baked directly into the **source glyph**:

```text
source rows 10..11 = full palette-index-7 dark/gray band
source rows 12..15 = full palette-index-1 bright white band
```

Interpretation:

- gray + white visible => rows12..15 survive source -> copy -> cache -> VRAM -> sprite;
- gray visible but white absent => structural lower-row loss confirmed;
- neither visible => source/slot/copy-path assumption still wrong.

Package:

```text
GaiaMaster_FontIsolation_0.6.3.7_SOURCE_ROW_SENTINEL.zip
```

Launcher:

```text
00_RUN_PROBE_0637.cmd
```

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

## Hard do-not-repeat

- no Krom path;
- no production 12x12 stacked-accent polishing;
- no retest 0.6.2.18;
- no retest 0.6.3.0..0.6.3.6;
- no shared `0x8003CD94..0x8003CDB4` allocator rewrite;
- no persistent early FLAG like 0.6.3.6.

## After extended-height path is stable

1. production-safe Vietnamese extended atlas/cache storage;
2. full Vietnamese glyph inventory;
3. compact runtime codepage/mapping;
4. encode `vi_full` có dấu;
5. solve/repack 230 pending rows;
6. clean mixed JP/VI;
7. graphic menu/title patch;
8. full runtime QA + reproducible build.

# Gaia Master — Font Isolation 0.6.3.11 RAM TAIL MIRROR

Prepared: **2026-09-12**
Status: **BUILT / awaiting runtime**

## Why this probe exists

0.6.3.10 used the proven per-current-glyph stack metadata height and runtime remained stable but visually unchanged from 0.6.3.7.

Final consumer reverse also proves `record+7` really becomes GPU primitive height.

Therefore the missing rows are no longer best explained by visible-height geometry.

The next exact question is:

> Do converted rows12..15 actually exist in RAM immediately after `0x8003C67C` returns?

## Proven dataflow

Caller metadata:

```text
metadata base = sp+16
source pointer = *(sp+20)
```

Target diagnostic source pointer:

```text
0x8007ABFC
```

This comes from:

```text
atlas RAM 0x8006BCEC + slot850 * 72
```

Current converted destination before native allocator advance:

```text
dest = *(s1+100)
```

Wide target copy geometry:

```text
8 converted bytes per row
rows12..15 = dest+96 .. dest+127
```

## Mirror diagnostic

Hook after copy at:

```text
0x8003CC4C
```

Only when:

```text
*(sp+20) == 0x8007ABFC
```

copy:

```text
dest+96..127  ->  dest+64..95
rows12..15        rows8..11
```

The target source sentinel already makes rows12..15 solid bright.

Therefore if those rows exist after conversion, the mirror should create an obvious bright 4-row block inside rows8..11, which are safely inside the native visible region.

## Interpretation

### Bright 4-row mirror block appears

Then converted rows12..15 definitely exist after `0x8003C67C`.

Focus next on:

- VRAM placement;
- texture V / page coordinates;
- page cursor / upload contents;
- cache-to-VRAM mapping.

### No bright mirror block

Then one of these is true:

- rows12..15 were not written as expected by the converter;
- current destination pointer model is wrong;
- source row processing differs from current model despite loop count.

Focus next inside `0x8003C67C` and destination semantics.

## Safety

This probe does **not**:

- mutate shared allocator stride;
- use a persistent/global flag;
- force height globally;
- use late `s0` for target identity;
- alter UV.

Target identity comes from the current glyph's proven source pointer in caller metadata.

## Package

```text
GaiaMaster_FontIsolation_0.6.3.11_RAM_TAIL_MIRROR.zip
```

Launcher:

```text
00_RUN_PROBE_06311.cmd
```

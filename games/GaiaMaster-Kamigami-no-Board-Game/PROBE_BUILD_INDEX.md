# Gaia Master — probe/build index

Updated: **2026-09-12**

Purpose: prevent checkpoint confusion and accidental retesting.

## Stable baselines

```text
Clean Japan BIN SHA1
f4d5298583c90d89c4b7e51d2dde160ee07f2aec

Alpha 0.6.1 FRONT SHA1
54d2fb026bc3b71c79861e723caffb4114caa34c
```

## 0.6.2.x

### 0.6.2.13 STATIC SLOT / NO HOOK
**BREAKTHROUGH PASS**. Static custom Vietnamese atlas path works.

### 0.6.2.14..0.6.2.20
Geometry/cosmetic experiments. Production conclusion: native 12x12 is too cramped for stacked Vietnamese diacritics.

## 0.6.3.x extended-height

### 0.6.3.0 EXTENDED HEIGHT 12x16
**STRUCTURAL PASS**. Do not retest.

### 0.6.3.1 BASELINE + 16-ROW STRIDE
**UNSAFE FAIL**. Global corruption + later freeze. Never retest.

### 0.6.3.2 BASELINE ONLY
**STABLE PASS WITH LOWER-ROW LOSS**. Do not retest.

### 0.6.3.3 EOL OVERWRITE
**RUNTIME COMPLETE**. Following-glyph overwrite disproven. Do not retest.

### 0.6.3.4 UV WINDOW
**RUNTIME COMPLETE / NEGATIVE**. V+4 does not restore lower rows. Do not retest.

### 0.6.3.5 POST-COPY RAM SENTINEL
**RUNTIME COMPLETE / NO SENTINEL**. Late `s0` identity unreliable. Do not retest.

### 0.6.3.6 EARLY-FLAG POST-COPY SENTINEL
**UNSAFE FAIL / BOOT FREEZE**. Repeatable freeze after Sony logo. Persistent/global flag strategy rejected. Never retest.

### 0.6.3.7 SOURCE ROW SENTINEL
**RUNTIME COMPLETE**.

Source target contains:

```text
rows10..11 dark/gray full band
rows12..15 bright white full band
```

Runtime:

- Japanese/TEST normal;
- dark rows10..11 visible;
- rows12..15 do not appear as a thick white 4-row block;
- only a thin bright edge remains.

=> lower four source rows are not fully visible.

### 0.6.3.8 FORCE SPRITE HEIGHT16
**DIAGNOSTIC FAIL**.

Forced height=16 for every glyph. Runtime textbox can go blank and TEST stacks vertically. Global height override breaks layout. Do not retest.

### 0.6.3.9 HEIGHT FROM METADATA
**BUILT / CURRENT PROBE**.

Start from 0.6.3.7. At `0x8003CCC0`, visible height now comes from current glyph metadata:

```text
lhu v0,2(s3)
0x8003CCC8 addiu v0,v0,1
```

Expected:

```text
native metadata 11 -> 12px
extended target metadata 15 -> 16px
```

Keeps source sentinel. No late s0, no global force-height, no flag, no post-copy hook, no CD94 allocator rewrite.

Package:

```text
GaiaMaster_FontIsolation_0.6.3.9_HEIGHT_FROM_METADATA.zip
```

Launcher:

```text
00_RUN_PROBE_0639.cmd
```

Question:

> Does normal layout return while target shows the complete bright rows12..15 block?

## Current do-not-repeat

- no Krom path;
- no production 12x12 stacked-accent polishing;
- no retest 0.6.2.18;
- no retest 0.6.3.0..0.6.3.8;
- no shared `0x8003CD94..0x8003CDB4` rewrite;
- no persistent/global flag;
- no global force-height16.

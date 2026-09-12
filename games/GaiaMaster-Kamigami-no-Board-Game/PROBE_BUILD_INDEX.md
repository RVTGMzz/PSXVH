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
Historical structural evidence. Do not retest.

### 0.6.3.1 BASELINE + 16-ROW STRIDE
**UNSAFE FAIL**. Global corruption + later freeze. Never retest.

### 0.6.3.2 BASELINE ONLY
**STABLE PASS WITH LOWER-ROW LOSS**. Do not retest.

### 0.6.3.3 EOL OVERWRITE
**RUNTIME COMPLETE**. Following-glyph overwrite disproven. Do not retest.

### 0.6.3.4 UV WINDOW
**RUNTIME COMPLETE / NEGATIVE**. Do not retest.

### 0.6.3.5 POST-COPY RAM SENTINEL
**RUNTIME COMPLETE / NO SENTINEL**. Late `s0` identity unreliable. Do not retest.

### 0.6.3.6 EARLY-FLAG SENTINEL
**UNSAFE FAIL / BOOT FREEZE**. Persistent/global flag rejected. Never retest.

### 0.6.3.7 SOURCE ROW SENTINEL
**RUNTIME COMPLETE / HIGH-VALUE RESULT**.

```text
rows10..11 dark/gray full band
rows12..15 bright white full band
```

Runtime shows rows10..11 but not the full rows12..15 block.

### 0.6.3.8 FORCE SPRITE HEIGHT16
**DIAGNOSTIC FAIL**. Global height override breaks layout. Do not retest.

### 0.6.3.9 HEIGHT FROM METADATA
**DIAGNOSTIC FAIL / RUNTIME COMPLETE**.

Used `lhu v0,2(s3)` at `0x8003CCC0`.
Runtime: TEST vertical + target texture garbage.
Reverse proved `s3=s5+15`, so this was not metadata.
Do not retest.

### 0.6.3.10 HEIGHT FROM STACK METADATA
**RUNTIME COMPLETE / STABLE NEGATIVE**.

Used dataflow-proven current glyph height:

```text
lhu v0,18(sp)
0x8003CCC8 addiu v0,v0,1
```

Runtime:
- native layout stable;
- target looks essentially identical to 0.6.3.7;
- rows12..15 still not visible as full bright block.

Reverse of final consumer confirms `record+7` really reaches GPU primitive height.

=> visible-height geometry is not the remaining blocker.
=> do not retest.

### 0.6.3.11 RAM TAIL MIRROR
**BUILT / CURRENT PROBE**.

Question:

> Do converted rows12..15 actually exist immediately after `0x8003C67C`?

Target identity:

```text
metadata source pointer = *(sp+20)
target source = 0x8007ABFC
```

Current converted destination before allocator advance:

```text
dest = *(s1+100)
```

Mirror:

```text
source converted rows12..15: dest+96..127
copy to visible rows8..11:   dest+64..95
```

Because rows12..15 source sentinel is solid bright, a successful mirror should create an obvious 4-row bright block higher in the glyph.

Interpretation:
- bright mirror block => lower converted rows exist; blocker is downstream VRAM/cache placement;
- no block => converted tail absent/wrong or destination model wrong.

Package:

```text
GaiaMaster_FontIsolation_0.6.3.11_RAM_TAIL_MIRROR.zip
```

Launcher:

```text
00_RUN_PROBE_06311.cmd
```

## Current do-not-repeat

- no Krom path;
- no production 12x12 stacked-accent polishing;
- no retest 0.6.2.18;
- no retest 0.6.3.0..0.6.3.10;
- no shared `0x8003CD94..0x8003CDB4` rewrite;
- no persistent/global flag;
- no global force-height16;
- no `s3+2` metadata assumption.

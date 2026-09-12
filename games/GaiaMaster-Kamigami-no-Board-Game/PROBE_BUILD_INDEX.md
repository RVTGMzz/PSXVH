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
**DIAGNOSTIC FAIL**. `s3+2` was not metadata; runtime vertical TEST/garbage. Do not retest.

### 0.6.3.10 HEIGHT FROM STACK METADATA
**RUNTIME COMPLETE / STABLE NEGATIVE**.
Uses proven `lhu v0,18(sp)`. Runtime stable but target still same as 0.6.3.7. Final primitive height is not the main blocker. Do not retest.

### 0.6.3.11 RAM TAIL MIRROR
**RUNTIME COMPLETE / INCONCLUSIVE NEGATIVE**.
No bright mirror block, but no independent control proved hook/destination correctness. Do not retest.

### 0.6.3.12 CONTROLLED RAM TAIL MIRROR
**DIAGNOSTIC FAIL / LAYOUT CORRUPTION**.

Runtime:
- `TEST` becomes vertical;
- target becomes texture/block garbage;
- control/mirror cannot be interpreted;
- post-copy write itself is perturbing live state/layout.

Conclusion:
- do not infer anything about rows12..15 from 0.6.3.12;
- do not write through `state+100` again until raw executable dataflow is re-verified;
- never retest 0.6.3.12.

## CURRENT — READ-ONLY REVERSE DUMP

No runtime game probe is current.

Tool:

```text
GaiaMaster_063_REVERSE_DUMP_0.1.zip
00_RUN_REVERSE_DUMP.cmd
```

Output:

```text
GaiaMaster_063_REVERSE_DUMP.txt
```

This tool does not patch the ROM and does not require emulator/game boot.

It dumps the exact MIPS code around:

```text
0x8003C180..0x8003C780
0x8003C880..0x8003CE80
0x8003D380..0x8003D540
0x8003D980..0x8003DAA0
0x8003DB40..0x8003DC40
```

Next runtime build is forbidden until the dump resolves:
- true destination register inside `0x8003C67C`;
- lifetime of `state+100` across the call;
- cache-page placement and per-glyph Y;
- exact path from converted rows to record U/V/H.

## Current do-not-repeat

- no Krom path;
- no production 12x12 stacked-accent polishing;
- no retest 0.6.2.18;
- no retest 0.6.3.0..0.6.3.12;
- no shared `0x8003CD94..0x8003CDB4` rewrite;
- no persistent/global flag;
- no global force-height16;
- no `s3+2` metadata assumption;
- no post-copy write through `state+100` until reverse proves its lifetime.

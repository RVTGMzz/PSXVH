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

Uses proven:

```text
lhu v0,18(sp)
```

Runtime stable but target still same as 0.6.3.7. Final primitive height is not the main blocker. Do not retest.

### 0.6.3.11 RAM TAIL MIRROR
**RUNTIME COMPLETE / INCONCLUSIVE NEGATIVE**.

Attempted:

```text
converted rows12..15 dest+96..127
-> rows8..11 dest+64..95
```

Runtime:
- header/TEST stable;
- no obvious bright 4-row mirror block;
- target essentially unchanged.

Problem: no independent visual control proved hook execution and current destination pointer.

=> no conclusion yet about whether tail is absent.
=> do not retest.

### 0.6.3.12 CONTROLLED RAM TAIL MIRROR
**BUILT / CURRENT PROBE**.

Target identity:

```text
lhu 18(sp) == 15
```

At post-copy hook:

```text
dest = *(s1+100)
```

Two visual signals:

```text
CONTROL rows6..7 = full 0x77 dark/gray
MIRROR  rows12..15 -> rows8..11
```

Interpretation:

- dark control + bright mirror => converted tail exists; blocker downstream in cache/VRAM placement;
- dark control + no bright mirror => hook/dest correct but tail content missing/wrong immediately after copy; reverse `0x8003C67C`;
- no dark control => hook/destination model still wrong.

Package:

```text
GaiaMaster_FontIsolation_0.6.3.12_CONTROLLED_RAM_TAIL_MIRROR.zip
```

Launcher:

```text
00_RUN_PROBE_06312.cmd
```

## Current do-not-repeat

- no Krom path;
- no production 12x12 stacked-accent polishing;
- no retest 0.6.2.18;
- no retest 0.6.3.0..0.6.3.11;
- no shared `0x8003CD94..0x8003CDB4` rewrite;
- no persistent/global flag;
- no global force-height16;
- no `s3+2` metadata assumption.

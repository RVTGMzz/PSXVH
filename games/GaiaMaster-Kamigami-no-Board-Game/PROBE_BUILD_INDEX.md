# Gaia Master — probe/build index

Updated: **2026-09-13**

Purpose: prevent checkpoint confusion and accidental retesting.

## Stable baselines

```text
Clean Japan BIN SHA1
f4d5298583c90d89c4b7e51d2dde160ee07f2aec

Alpha 0.6.1 FRONT SHA1
54d2fb026bc3b71c79861e723caffb4114caa34c
```

## Historical locks

- `0.6.2.13` static custom atlas: **PASS**.
- `0.6.3.x` 12x16: corruption/freezes. **Do not revive**.
- `0.6.4.x` composite overlay: unreliable. **Not production**.
- `0.6.5.2` runtime pointer redirect: **UNSAFE FAIL / NEVER RETEST**.
- Mapping Initializer Scanner 0.2: mapping/global ownership **PROVEN**.
- `0.6.5.3`: mapping-only **STRUCTURAL PASS**.
- `0.6.5.4`: native-base copy **PASS**.
- `0.6.5.5`: compact accent style **PASS enough for production**.

## 0.6.6.x

### 0.6.6.0 REAL-TEXT ENCODER

`Chọn tướng` rendered end-to-end.

Result: **PASS**, baseline needed polish.

### 0.6.6.1 BASELINE-NORMALIZED

Result: **PASS / LAST GOOD**.

Proven:
- native 12x12 production geometry;
- static mapping-only custom Vietnamese routing;
- baseline acceptable;
- stable boot/UI;
- no hook or pointer redirect.

Remaining wide horizontal spacing is visual polish only.

### 0.6.6.2

**BUILD GATE FALSE POSITIVE.** No ROM/runtime result. Do not retest.

### 0.6.6.2b

**BUILD GATE FALSE POSITIVE.** No ROM/runtime result. Do not retest.

### 0.6.6.2c NATIVE NARROW 8PX

Builder succeeded and runtime-tested.

Expected `Chọn tướng`; actual unrelated/garbled glyphs.

Result:

```text
RUNTIME FAIL
RETIRE 6x12 / one-byte alias production path
DO NOT RETEST
```

This does not affect the 12x12 mapping-only PASS.

## Production Capacity Scanner 0.1 — RESULT

READ-ONLY. No patched BIN and no emulator boot.

Worst-case target:

```text
67 lowercase custom chars
67 uppercase custom chars
TOTAL = 134 custom glyphs
```

User result on verified CLEAN BIN:

```text
Zero-hit custom codes : 837
Zero-hit atlas slots  : 64
Unmapped zero slots   : 34
Verdict               : FAIL
```

Atlas split:

```text
34 completely unmapped zero-hit slots
30 mapped-but-static-unused zero-hit slots
64 total conservative allocatable slots
```

Conclusion:
- code-space capacity is abundant;
- conservative atlas capacity is the bottleneck;
- full 134-glyph codepage does not fit while preserving all currently referenced Japanese glyphs;
- this is a valid capacity FAIL, not a broken build;
- do not rerun unless reclaim rules change.

## CURRENT — vi_full Inventory 0.1

READ-ONLY. No game BIN required.

Files:

```text
tools/vifull_inventory_0.1.py
tools/00_RUN_VIFULL_INVENTORY_0.1.cmd
```

Goal:
- read Translation Master 0.6 parts 01..06;
- inventory only actual `vi_full` content;
- count exact Vietnamese precomposed characters currently needed;
- normalize punctuation where possible;
- compare actual custom glyph need against 64 known conservative atlas slots.

Report:

```text
GaiaMaster_ViFullInventory_01.txt
```

### If PASS (<=64)

Freeze exact current-corpus codepage and build a multi-string 12x12 production proof.

### If FAIL (>64)

Do not return to narrow/12x16. Design explicit Japanese-slot reclaim based on rows already translated.

## Do not repeat

- no Krom path;
- no production 12x16;
- no failed 0.6.3.x retests;
- no composite overlay loop;
- no 0.6.5.2 pointer redirect;
- no 0.6.5.3 retest;
- no 0.6.6.2 / 2b retest;
- no 0.6.6.2c retest;
- no one-byte narrow alias path;
- no global cursor/cache spacing mutation;
- no spacing-driven architecture rewrite;
- no repeated 134-glyph capacity scan without an atlas-reclaim change;
- stop immediately on freeze/global corruption.

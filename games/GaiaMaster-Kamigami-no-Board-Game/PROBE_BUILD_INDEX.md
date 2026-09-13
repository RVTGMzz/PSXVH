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

Remaining wide horizontal spacing is classified as visual polish.

### 0.6.6.2

**BUILD GATE FALSE POSITIVE.** No ROM/runtime result. Do not retest.

### 0.6.6.2b

**BUILD GATE FALSE POSITIVE.** No ROM/runtime result. Do not retest.

### 0.6.6.2c NATIVE NARROW 8PX

Builder succeeded, runtime tested.

Expected:

```text
Chọn tướng
```

Actual:
- unrelated/garbled glyphs;
- one-byte aliases did not route to the assumed narrow indices.

Result:

```text
RUNTIME FAIL
RETIRE 6x12 / one-byte alias production path
DO NOT RETEST
```

This does not affect the 12x12 mapping-only PASS.

## CURRENT — PRODUCTION CAPACITY SCANNER 0.1

READ-ONLY. No emulator boot and no patched BIN.

Goal:

Test whether the proven 12x12 architecture can fit the **full Vietnamese repertoire**, not merely the currently translated subset.

Worst-case production target:

```text
67 lowercase custom chars
67 uppercase custom chars
TOTAL = 134 custom glyphs
```

Scanner checks:
- zero-static-hit CP932 custom-code capacity;
- zero-static-hit atlas capacity;
- completely unmapped vs mapped-but-zero-hit slots;
- protects native Latin source glyph slots;
- emits deterministic full codepage proposal if capacity PASS.

Report:

```text
GaiaMaster_ProductionCapacityScanner_01.txt
```

### If PASS

Freeze full Vietnamese codepage and move directly to a multi-string 12x12 production build using real `vi_full` text.

### If FAIL

Inventory exact characters present in `vi_full` and allocate only that smaller corpus.

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
- stop immediately on freeze/global corruption.

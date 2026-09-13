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

## 0.6.2.x

### 0.6.2.13 STATIC SLOT / NO HOOK

**BREAKTHROUGH PASS.** Static custom Vietnamese atlas replacement works.

### 0.6.2.14..0.6.2.20

Cosmetic/native-cell experiments. Conclusion: one native 12x12 glyph cannot keep a full-size base letter and stacked Vietnamese marks at acceptable quality.

## 0.6.3.x extended-height research

### 0.6.3.0
Historical 12x16 structural evidence. Do not retest.

### 0.6.3.1
**UNSAFE FAIL.** Shared stride/cursor mutation caused corruption + freeze.

### 0.6.3.2
Stable with lower-row loss.

### 0.6.3.3
Following-glyph overwrite disproven.

### 0.6.3.4
UV-window diagnostic negative.

### 0.6.3.5
Late-s0 sentinel inconclusive.

### 0.6.3.6
**UNSAFE FAIL.** Persistent/global flag caused boot freeze.

### 0.6.3.7
Source-row sentinel: rows10..11 visible, rows12..15 not fully visible.

### 0.6.3.8
**DIAGNOSTIC FAIL.** Global height16 broke layout.

### 0.6.3.9
**DIAGNOSTIC FAIL.** False `s3+2` metadata assumption.

### 0.6.3.10
**STABLE NEGATIVE.** Correct height metadata did not recover lower rows.

### 0.6.3.11
Mirror negative, inconclusive.

### 0.6.3.12
**DIAGNOSTIC FAIL / LAYOUT CORRUPTION.** Never retest.

## 0.6.4.x composite accent experiments

### 0.6.4.0
Composite accent proof concept.

### 0.6.4.1
Outlined accent artwork looked better.

### 0.6.4.2
Horizontal X-shift refinement did not reliably move overlay as expected.

### 0.6.4.3
Tried to account for multiple render/cache paths. Placement still moved the wrong way / remained unreliable.

### 0.6.4.4
Integrated one-cell art test inspired visually by a finished PS1 Vietnamese patch. Not production direction.

**Conclusion for 0.6.4.x:** accent art can be acceptable, but runtime overlay placement is too fragile. Stop tuning X/Y placement.

## 0.6.5.x native-cell / mapping pivot

Detailed note:

`FONT_MAPPING_PIVOT_0.6.5.md`

### 0.6.5.0 UNIFIED NATIVE-CELL VIETNAMESE

Intended visual order:

```text
A Â Ấ Ẳ E Ê Ế Ể O Ô Ố Ỗ
```

Runtime:
- mostly repeated A-like glyphs;
- one unrelated Kanji;
- no freeze.

Conclusion:

**MAPPING ASSUMPTION FAIL.** Consecutive CP932 codes do not map linearly to atlas slots 0..11.

### 0.6.5.1 POST-LOOKUP CUSTOM BANK

**BUILD-TIME FAIL ONLY.**

Builder incorrectly required a large region to be zero-filled. User's CLEAN BIN was correct. No runtime conclusion.

### 0.6.5.2 ATLAS-BACKED CUSTOM BANK

**UNSAFE FAIL. NEVER RETEST.**

Runtime:
- black screen;
- Game FPS 0;
- hard freeze before useful output.

Conclusion:

Do not use runtime post-lookup pointer redirect for this path.

### Font Mapping Scanner 0.1

Read-only scanner found `GP0=0` in the PS-X EXE header, so final renderer globals were not statically available from header GP.

### Font Mapping Initializer Scanner 0.2 — OWNERSHIP PROVEN

Read-only report proved:

```text
runtime GP = 0x80085F28
atlas global = gp+0x518
map global   = gp+0x51C
```

Initializer at `0x8003DD48..0x8003DD5C` writes the native defaults directly:

```text
atlas   = 0x8006BCEC
mapping = 0x8007AECC
```

Static mapping samples all matched runtime-known values, including `0x889F -> glyph 0`.

**Gate opened:** mapping ownership is demonstrated. Data-only proof is allowed.

## CURRENT — 0.6.5.3 MAPPING-ONLY NATIVE-CELL PROOF

Builder:

```text
tools/build_gaia_0653_mapping_only.py
tools/00_BUILD_0.6.5.3_MAPPING_ONLY.cmd
```

Detailed note:

`FONT_MAPPING_PROOF_0.6.5.3.md`

Architecture:

```text
0x889F..0x88AA
  -> patched static mapping entries
  -> selected low-use atlas slots
  -> native 12x12 / 72-byte glyph data
```

No code hook. No pointer redirect. No 12x16. No composite overlay.

Expected Character Select visual:

```text
A Â Ấ Ẳ E Ê Ế Ể O Ô Ố Ỗ
```

Status: **READY FOR ONE RUNTIME TEST.**

## Current do-not-repeat

- no Krom path;
- no production 12x16 path;
- no retest 0.6.2.18;
- no retest failed 0.6.3.x probes;
- no composite X/Y tuning loop;
- no 0.6.5.2 runtime redirect;
- no assumption consecutive code == consecutive atlas slot;
- stop immediately on freeze/global corruption.

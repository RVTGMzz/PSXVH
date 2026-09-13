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
Native-cell art experiments. One 12x12 cell requires a compact unified Vietnamese style.

## 0.6.3.x extended-height research

- `0.6.3.1` **UNSAFE FAIL**: corruption + freeze.
- `0.6.3.2` stable with lower-row loss.
- `0.6.3.3` following-glyph overwrite disproven.
- `0.6.3.4` UV-window negative.
- `0.6.3.6` **UNSAFE FAIL**: boot freeze.
- `0.6.3.7` rows10..11 visible, lower rows not fully visible.
- `0.6.3.8/9/12` diagnostic/layout failures.
- `0.6.3.10` stable negative.

**Do not revive 12x16 as production.**

## 0.6.4.x composite accent experiments

Accent art became acceptable, but overlay placement remained unreliable across real render/cache paths.

**Conclusion:** stop composite X/Y tuning. Not production.

## 0.6.5.x native-cell / mapping pivot

### 0.6.5.0 UNIFIED NATIVE-CELL VIETNAMESE
Runtime showed repeated A-like glyphs + unrelated Kanji.

**MAPPING ASSUMPTION FAIL:** consecutive CP932 codes do not map linearly to atlas slots.

### 0.6.5.1 POST-LOOKUP CUSTOM BANK
**BUILD-TIME FAIL ONLY.** Bad zero-filled-region assumption. No runtime conclusion.

### 0.6.5.2 ATLAS-BACKED CUSTOM BANK
**UNSAFE FAIL. NEVER RETEST.**

- black screen;
- Game FPS 0;
- hard freeze.

Reject runtime post-lookup pointer redirect.

### Font Mapping Scanner 0.1
Found `GP0=0` in EXE header. Final GP is initialized later.

### Font Mapping Initializer Scanner 0.2 — OWNERSHIP PROVEN

```text
runtime GP = 0x80085F28
atlas global = gp+0x518
map global   = gp+0x51C
```

Initializer `0x8003DD48..0x8003DD5C` writes:

```text
atlas   = 0x8006BCEC
mapping = 0x8007AECC
```

Known mapping samples all matched.

**Gate opened:** static mapping/data-only proof allowed.

### 0.6.5.3 MAPPING-ONLY NATIVE-CELL

Architecture:

```text
0x889F..0x88AA
  -> patched mapping entries
  -> selected low-use atlas slots
  -> native 12x12 / 72-byte glyph cells
```

Runtime result: **STRUCTURAL PASS / GLYPH-GENERATOR FAIL.**

What passed:
- game boots;
- no freeze/global corruption;
- mapping-controlled test line appears;
- custom atlas slots are reached;
- no code hook/pointer redirect needed.

What failed visually:
- glyphs look dark/shadow-like;
- accented E/O families look A-like.

Root causes found:

```python
setpix(..., v=7)
base = label[0] if label[0] in "AEO" else "A"
```

The second line makes Unicode `Ê/Ế/Ể/Ô/Ố/Ỗ` fall back to A.

**Do not retest 0.6.5.3.**

## CURRENT — 0.6.5.4 NATIVE-BASE STYLE PROOF

Files:

```text
FONT_MAPPING_PROOF_0.6.5.4.md
tools/build_gaia_0654_native_base.py
tools/00_BUILD_0.6.5.4_NATIVE_BASE.cmd
```

Changes from 0.6.5.3:
- plain A/E/O are copied byte-for-byte from Gaia's own native full-width glyphs;
- explicit A/E/O family tables fix Unicode base selection;
- accent color is derived from the native glyph palette instead of hardcoding index 7;
- mapping-only architecture remains unchanged.

Expected Character Select visual:

```text
A Â Ấ Ẳ E Ê Ế Ể O Ô Ố Ỗ
```

Status: **READY FOR ONE RUNTIME TEST.**

## Current do-not-repeat

- no Krom path;
- no production 12x16;
- no failed 0.6.3.x retests;
- no composite X/Y tuning loop;
- no 0.6.5.2 runtime redirect;
- no assumption consecutive code == consecutive atlas slot;
- no 0.6.5.3 retest;
- stop immediately on freeze/global corruption.

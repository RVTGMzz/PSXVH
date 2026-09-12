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
**BREAKTHROUGH PASS**. Static custom Vietnamese atlas path works.

### 0.6.2.14..0.6.2.20
One-glyph geometry/cosmetic experiments. Conclusion: full Vietnamese stacked marks do not fit cleanly in one native 12x12 cell while preserving full base body.

## 0.6.3.x extended-height research

### 0.6.3.0
Historical 12x16 structural evidence. Do not retest.

### 0.6.3.1
**UNSAFE FAIL**. Shared stride/cursor mutation caused corruption + freeze.

### 0.6.3.2
Stable with lower-row loss.

### 0.6.3.3
Following-glyph overwrite disproven.

### 0.6.3.4
UV-window diagnostic negative.

### 0.6.3.5
Late-s0 sentinel inconclusive.

### 0.6.3.6
**UNSAFE FAIL**. Persistent/global flag caused boot freeze.

### 0.6.3.7
High-value source-row sentinel: rows10..11 visible, rows12..15 not fully visible.

### 0.6.3.8
**DIAGNOSTIC FAIL**. Global height16 broke layout.

### 0.6.3.9
**DIAGNOSTIC FAIL**. False `s3+2` metadata assumption.

### 0.6.3.10
**STABLE NEGATIVE**. Proven `sp+18` height did not recover lower rows.

### 0.6.3.11
Inconclusive mirror negative.

### 0.6.3.12
**DIAGNOSTIC FAIL / LAYOUT CORRUPTION**. Post-copy write probe made TEST vertical/target garbage. Never retest.

### Reverse dump 0.1 result

Read-only executable dump proves:

```text
0x8003CC34  a2 = state+100 current converted start
0x8003CC38  jal 0x8003C67C
...
0x8003CD94  state+100 advance begins
```

So state+100 has not advanced immediately after the copy call. 0.6.3.12 failed for a deeper live-state/register reason.

Reverse dump 0.2 remains available for completing old extended-height documentation.

## 0.6.4.x composite accent pivot

External reference study: `2ez4gcx/yugioh-mcbb-vi-patch` is a finished Japanese PS1 -> Vietnamese patch whose public README describes translated text, redrawn font and a few code-adjustment bytes. The repo does not expose development source, so no exact technique is attributed to it. Strategic lesson: prefer targeted font/compositor changes over broad renderer redesign when possible.

### 0.6.4.0 COMPOSITE ACCENT OVERLAY — **CURRENT PROBE**

Internal text:

```text
ＴＥＳＴＥ亜
```

Expected visual:

```text
ＴＥＳＴẾ
```

Design:
- native full-size E unchanged;
- glyph #0 becomes transparent circumflex+acute overlay;
- overlay native 12x12 descriptor is shifted `X -= 12`, `Y -= 4`;
- overlay therefore sits over preceding E;
- no 12x16 geometry/cache path is involved.

Package:

```text
GaiaMaster_FontIsolation_0.6.4.0_COMPOSITE_ACCENT_OVERLAY.zip
```

Launcher:

```text
00_RUN_PROBE_0640.cmd
```

Pass question:

> Do the stacked marks appear cleanly above the full-size native E?

If PASS, production next steps:
- neutralize overlay horizontal advance for inline use;
- define top-accent overlay families;
- define bottom-mark overlay family;
- design text encoder that expands one Vietnamese character into base+overlay internal sequence;
- keep native 12x12 cache/VRAM pipeline.

## Current do-not-repeat

- no Krom path;
- no production one-glyph stacked-accent polishing in 12x12;
- no retest 0.6.2.18;
- no retest 0.6.3.0..0.6.3.12;
- no shared CD94 rewrite;
- no persistent/global flag;
- no global force-height16;
- no `s3+2` metadata assumption;
- no post-copy RAM write diagnostic like 0.6.3.12.

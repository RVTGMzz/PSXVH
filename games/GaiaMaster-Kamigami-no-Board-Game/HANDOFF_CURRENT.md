# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** production remains locked to **native 12x12 / 72-byte / 4bpp / static mapping-only**. `0.6.7.2` is the frozen **FONT VISUAL PASS**. `0.6.9.2` is the exact **397/397 legacy coverage PASS**. Runtime screenshots now prove `0.6.10.0` renders accented Vietnamese correctly, but expose content defects. The active candidate is **0.6.11.0 HYBRID GAMEPLAY ACCENT BATCH 2**.

## Baselines

- Game: `GaiaMaster - Kamigami no Board Game (Japan).bin`
- serial: `SLPS-02075`
- clean BIN SHA1: `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- clean SLPS SHA1: `1dfeb6b7cfda59c108dde2dc0b8abda9a40e6ae5`
- clean PRGPACK SHA1: `a9b195b8ae5d8cad7f4f755daa08337d4671632c`
- repo: `ronvotri/Viet-Hoa-PS1`
- branch: `gaia-character-select-font-atlas-reverse-01`

## Proven font architecture

```text
runtime GP     = 0x80085F28
atlas global   = gp+0x518
mapping global = gp+0x51C
main atlas RAM = 0x8006BCEC
mapping RAM    = 0x8007AECC
main atlas file= SLPS+0x5C4EC
mapping file   = SLPS+0x6B6CC
860 glyphs
native main font = 12x12 / 72-byte / 4bpp / LOW nibble first
```

Pipeline:

```text
code & 0x7FFF
 -> mapping[index]
 -> glyph index
 -> glyph_index * 72
 -> atlas base + offset
```

## Frozen font / codepage

`0.6.7.2` = **FONT VISUAL PASS / FREEZE**.

Do not retune the font based on current QA. Runtime screenshots show the accents themselves are working. The active problems are text content, fixed-field fit and Japanese literals supplied through dynamic `%s`.

Frozen custom set:

```text
àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ
```

Capacity remains:

```text
60 custom Vietnamese glyphs
64 conservative zero-hit atlas slots
4 reserve slots
```

## Historical production locks

- `0.6.2.13`: static custom atlas PASS.
- `0.6.3.x`: 12x16 corruption/freezes. Retired.
- `0.6.4.x`: composite overlay unreliable. Retired.
- `0.6.5.2`: **UNSAFE FAIL / NEVER RETEST**.
- `0.6.5.3`: mapping-only structural PASS.
- `0.6.5.4`: native-base copy PASS.
- `0.6.5.5`: compact accent style PASS enough for production.
- `0.6.6.0`: real text `Chọn tướng` end-to-end.
- `0.6.6.1`: baseline-normalized PASS.
- `0.6.6.2` / `2b`: build-gate false blocks only.
- `0.6.6.2c`: one-byte narrow alias runtime FAIL. Retired.
- `0.6.7.0`: full 60-glyph production codepage boots/renders.
- `0.6.7.2`: **FONT VISUAL PASS / FREEZE**.
- `0.6.8.0` / `0.6.8.1`: insufficient gameplay coverage.
- `0.6.9.0` / `0.6.9.1`: build-gate bugs only. Do not retest.
- `0.6.9.2`: exact legacy reconstruction **397/397 COVERAGE PASS**.

## Coverage rule

The old Alpha source produced exactly **397 patch keys**. Every production build after `0.6.9.2` must preserve:

```text
legacy Alpha coverage = 397 / 397
```

Extra newer `vi_full`-only rows are allowed.

Runtime/control tokens remain raw:

```text
%s %d %+3d /V /v ...
```

Never remove a fitting `vi_game_current` fallback unless an accented replacement actually fits.

## 0.6.10.0 runtime result

`0.6.10.0 HYBRID FULL-COVERAGE + FRONT ACCENT BATCH 1` is no longer waiting on the font gate.

User runtime screenshots show accented Vietnamese rendering in intro/setup. Therefore:

```text
0.6.10.0 = FRONT ACCENT/FONT RUNTIME PASS
            CONTENT QA INCOMPLETE
```

Observed defects:

### 1. Intro unsafe `=`

Rows such as:

```text
Người=cờ
Thếgiới=bàncờ
```

show a Japanese-looking/garbled glyph at `=`.

Conclusion: this is a content/encoding choice, not a font regression. Remove `=`.

### 2. Cryptic setup wording

Runtime:

```text
Tải dữ liệu VK?
```

`VK` meant **vũ khí**; the Japanese source refers to weapon-skill data. Batch 2 changes this to compact:

```text
Tải KN vũ khí?
```

### 3. Mixed runtime `%s`

Runtime screenshot:

```text
DUNG トロル通り
```

This proves the format string was patched while `%s` receives a Japanese name from a separate dynamic table.

Batch 2 targets:

```text
DUNG %s    -> Dừng %s
トロル通り -> Troll
```

Expected runtime:

```text
Dừng Troll
```

## CURRENT — 0.6.11.0 HYBRID GAMEPLAY ACCENT BATCH 2

Design note:

```text
ACCENT_UPGRADE_0.6.11.0.md
```

Builder / launcher:

```text
tools/build_gaia_06110_hybrid_accent_b2.py
tools/00_BUILD_0.6.11.0_HYBRID_ACCENT_B2.cmd
```

Data:

```text
translation/FRONT_ACCENT_OVERRIDES_0.6.11.0.csv
translation/GAMEPLAY_ACCENT_OVERRIDES_0.6.11.0.csv
translation/DYNAMIC_LITERAL_OVERRIDES_0.6.11.0.csv
```

### Architecture strategy

The `0.6.11.0` builder is intentionally a wrapper around the exact `0.6.10.0` builder.

This preserves unchanged:

- `0.6.7.2` font atlas style;
- frozen 60-glyph codepage;
- BDP/checksum writer;
- runtime token semantics;
- exact old Alpha `397/397` gate.

### Gameplay Batch 2

`GAMEPLAY_ACCENT_OVERRIDES_0.6.11.0.csv` contains **335 candidate compact rewrites** across:

```text
setup
repeated tavern dialogue
gameplay prompts
cards
items/weapons
events
menus
status/name fragments
```

The wrapper checks byte fit before promotion.

```text
candidate fits -> temporarily promote to vi_full
candidate too long -> keep old fallback untouched
```

This is a hard safety rule. Coverage wins over accent completeness.

### Dynamic literal layer

`DYNAMIC_LITERAL_OVERRIDES_0.6.11.0.csv` adds screenshot-proven Japanese literals that are not owned by the normal format string row.

Initial entry:

```text
トロル通り -> Troll
```

Safety:

- equal encoded-length replacement may be injected directly;
- shorter replacement only when the source literal is standalone/null-delimited.

### Front cleanup

`FRONT_ACCENT_OVERRIDES_0.6.11.0.csv` retains all 31 front/setup rows and fixes the runtime QA issues without changing the font.

Important examples:

```text
Người cờ
Thếgiới bàncờ
Không chống
Tải KN vũ khí?
Có      không
```

## Build / runtime state

Repository source for `0.6.11.0` is **BUILDER READY / RUNTIME PENDING**.

The wrapper has been syntax-checked, but this session does not have the clean game BIN mounted, so the inner ROM build cannot be executed here.

When run from the full repo, drag the CLEAN BIN onto:

```text
tools/00_BUILD_0.6.11.0_HYBRID_ACCENT_B2.cmd
```

The wrapper:

1. verifies clean BIN SHA1;
2. scans dynamic literals;
3. temporarily applies front/gameplay overlays;
4. invokes the exact `0.6.10.0` builder;
5. requires its normal gates, including `397/397`;
6. restores source CSVs even on failure;
7. writes `GaiaMaster_0.6.11.0_B2_WRAPPER_REPORT.txt`;
8. packages detected BIN/CUE/report outputs where available.

## Next runtime gate

Test one build, maximizing information:

1. intro: `Người cờ` / `Thếgiới bàncờ` with no garbage glyph;
2. setup: `Tải KN vũ khí?`;
3. real match: trigger the previous mixed line and expect `Dừng Troll`;
4. inspect card/menu/item/event/prompt accents;
5. screenshot any remaining Japanese literal or unaccented fallback.

Do not reopen font work unless an actual glyph regression appears.

## Hard do-not-repeat

- no Krom path;
- no production 12x16;
- no failed 0.6.3.x retests;
- no composite overlay loop;
- no 0.6.5.2 pointer redirect;
- no 0.6.6.2 / 2b retests;
- no 0.6.6.2c retest;
- no one-byte narrow alias production path;
- no global cursor/cache/spacing mutation;
- no spacing-driven architecture rewrite;
- no accent retuning after `0.6.7.2` without a demonstrated regression;
- no `0.6.9.0` / `0.6.9.1` retests;
- never sacrifice fitting fallback coverage merely to force accents;
- stop immediately on freeze/global corruption.

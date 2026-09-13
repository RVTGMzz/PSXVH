# Gaia Master — probe/build index

Updated: **2026-09-14**

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

### 0.6.6.0
`Chọn tướng` rendered end-to-end. **PASS**.

### 0.6.6.1
Baseline-normalized. **PASS**.

### 0.6.6.2 / 0.6.6.2b
Safety-gate false blocks. No runtime. Do not retest.

### 0.6.6.2c
Native narrow one-byte alias produced unrelated/garbled glyphs. **RUNTIME FAIL / RETIRED**.

## Production codepage

Actual Translation Master production repertoire:

```text
60 custom Vietnamese glyphs
64 conservative zero-hit atlas slots
4 reserve slots
```

Frozen custom set:

```text
àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ
```

## 0.6.7.x

### 0.6.7.0
Full 60-glyph production codepage boots/renders.

### 0.6.7.2
**FONT VISUAL PASS / FREEZE.**

No current runtime evidence justifies reopening font tuning.

## 0.6.8.x

`0.6.8.0` / `0.6.8.1`: safe-fit/front experiments did not restore desired gameplay coverage. Retired as production direction.

## 0.6.9.x — old Alpha coverage recovery

Old Alpha legacy coverage = exactly **397 patch keys**.

### 0.6.9.0
Bad total-count gate. **BUILD GATE BUG ONLY**.

### 0.6.9.1
Bad legacy classification gate. **BUILD GATE BUG ONLY**.

### 0.6.9.2
Exact legacy reconstruction:

```text
legacy = 397 / 397
extra vi_full-only rows allowed
```

Runtime showed Vietnamese intro fallback.

**COVERAGE PASS / ACCENT COVERAGE INCOMPLETE.**

## 0.6.10.0 — Front Accent Batch 1

Files:

```text
tools/build_gaia_06100_hybrid_accent_b1.py
tools/00_BUILD_0.6.10.0_HYBRID_ACCENT_B1.cmd
translation/FRONT_ACCENT_OVERRIDES_0.6.10.0.csv
ACCENT_UPGRADE_0.6.10.0.md
```

All 31 dedicated front/setup rows had accented compact overrides.

### Runtime result — 2026-09-14

User screenshots prove accented Vietnamese is rendered with the frozen font.

Verdict:

```text
FRONT ACCENT/FONT RUNTIME PASS
CONTENT QA INCOMPLETE
```

Observed content defects:

```text
Người=cờ
Thếgiới=bàncờ
```

`=` renders as an unrelated Japanese-looking/garbled glyph.

Setup:

```text
Tải dữ liệu VK?
```

is unclear; `VK` means `vũ khí`.

Gameplay:

```text
DUNG トロル通り
```

shows that a translated format string still receives a Japanese dynamic `%s` value.

This is not a reason to retune the font.

## CURRENT — 0.6.11.0 HYBRID GAMEPLAY ACCENT BATCH 2

Files:

```text
ACCENT_UPGRADE_0.6.11.0.md
tools/build_gaia_06110_hybrid_accent_b2.py
tools/00_BUILD_0.6.11.0_HYBRID_ACCENT_B2.cmd
translation/FRONT_ACCENT_OVERRIDES_0.6.11.0.csv
translation/GAMEPLAY_ACCENT_OVERRIDES_0.6.11.0.csv
translation/DYNAMIC_LITERAL_OVERRIDES_0.6.11.0.csv
```

### Strategy

`0.6.11.0` reuses the exact `0.6.10.0` builder as its inner engine.

Therefore these remain locked:

```text
font 0.6.7.2
60-glyph codepage
BDP/checksum writer
runtime format/control token handling
exact 397/397 legacy gate
```

### Front cleanup

Runtime-driven fixes include:

```text
Người=cờ        -> Người cờ
Thếgiới=bàncờ   -> Thếgiới bàncờ
Ko chống        -> Không chống
Tải dữ liệu VK? -> Tải KN vũ khí?
```

### Gameplay Batch 2

`GAMEPLAY_ACCENT_OVERRIDES_0.6.11.0.csv` contains:

```text
335 compact accent candidates
```

covering setup, repeated tavern dialogue, gameplay, card, item, event, menu and prompt rows.

Wrapper policy:

```text
accented compact candidate fits original field
 -> promote to vi_full for this build

candidate too long
 -> do not force
 -> old fallback remains
```

This prevents accent work from reducing coverage.

### Dynamic literal recovery

Initial screenshot-proven row:

```text
トロル通り -> Troll
```

Combined with:

```text
DUNG %s -> Dừng %s
```

expected runtime:

```text
Dừng Troll
```

Dynamic safety:

- equal encoded length can replace directly;
- shorter replacement requires a standalone/null-delimited literal.

### Build state

```text
SOURCE/BUILDER READY
PYTHON SYNTAX PASS
ROM BUILD PENDING
RUNTIME PENDING
```

Reason ROM build is pending: clean game BIN is not mounted in the current session.

## Next gate

Run one `0.6.11.0` build from CLEAN BIN and inspect:

1. intro `=` garbage is gone;
2. setup says `Tải KN vũ khí?`;
3. old mixed case becomes `Dừng Troll`;
4. gameplay/card/menu/item/event/prompt accent coverage;
5. any remaining Japanese dynamic name or no-accent fallback.

## Do not repeat

- no Krom path;
- no production 12x16;
- no failed `0.6.3.x` retests;
- no composite overlay loop;
- no `0.6.5.2` pointer redirect;
- no `0.6.6.2` / `2b` retests;
- no `0.6.6.2c` retest;
- no one-byte narrow alias;
- no global cursor/cache/spacing mutation;
- no accent retuning after `0.6.7.2` without demonstrated regression;
- no `0.6.9.0` / `0.6.9.1` retests;
- never remove fitting fallback coverage merely to force accents;
- stop immediately on freeze/global corruption.

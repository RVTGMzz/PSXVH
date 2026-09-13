# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** giữ renderer/font geometry native **12x12 / 72-byte / 4bpp**. Mapping-data-only đã runtime PASS. `0.6.6.0` chứng minh production encoder với câu Việt thật `Chọn tướng`; `0.6.6.1 BASELINE-NORMALIZED` đã runtime **PASS** ở mức baseline/glyph đủ tốt. Vấn đề còn lại là **horizontal spacing/advance**: Latin-looking glyphs vẫn cách nhau rộng kiểu full-width Nhật. Current step là **READ-ONLY FontSpacingScanner 0.1** để chứng minh ownership của `state+0x3C/+0x3E/+0x40`. Chưa build runtime 0.6.6.2 cho tới khi spacing ownership được chứng minh.

## Baseline

- Game: `GaiaMaster - Kamigami no Board Game (Japan).bin`
- serial: `SLPS-02075`
- clean BIN SHA1: `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- Alpha 0.6.1 FRONT SHA1: `54d2fb026bc3b71c79861e723caffb4114caa34c`
- branch: `gaia-character-select-font-atlas-reverse-01`
- repo: `ronvotri/Viet-Hoa-PS1`

## Proven font facts

```text
runtime GP     = 0x80085F28
atlas global   = gp+0x518
mapping global = gp+0x51C
atlas RAM      = 0x8006BCEC
mapping RAM    = 0x8007AECC
atlas file     = SLPS + 0x5C4EC
mapping file   = SLPS + 0x6B6CC
860 glyphs
native 12x12 / 72-byte / 4bpp / LOW nibble first
```

Renderer mapping consumer:

```text
code & 0x7FFF
 -> mapping[index]
 -> glyph index
 -> glyph index * 72
 -> atlas base + offset
```

Character Select proof field:

```text
PRGPACK.BDP + 0xBFD2C
owner nested BDP = entry 29
24 bytes used safely by current proofs
```

## Hard historical conclusions

- `0.6.2.13`: static custom-atlas replacement PASS.
- `0.6.3.x`: 12x16 touched shared renderer/cache state and caused corruption/freezes. Do not revive.
- `0.6.4.x`: composite overlay placement unreliable. Not production.
- `0.6.5.2`: **UNSAFE FAIL / NEVER RETEST**, runtime pointer redirect caused black screen, Game FPS 0, hard freeze.
- Font Mapping Scanner 0.2: runtime GP + atlas/mapping ownership proven.
- `0.6.5.3`: mapping-only path STRUCTURAL PASS; generator bugs only.
- `0.6.5.4`: native A/E/O copy PIPELINE PASS; vertical crowding only.
- `0.6.5.5`: compact Vietnamese glyph board visual PASS enough for production pivot.

## Translation source

Translation Master 0.6:
- 596 rows;
- `vi_full` = accented source-of-truth;
- `vi_game_current` = old no-accent fallback.

Production strategy remains:

```text
plain Latin / numbers / punctuation
  -> reuse Gaia native full-width CP932 glyphs

Vietnamese-specific precomposed chars
  -> dedicated custom mapping entries
  -> selected zero-static-hit native 12x12 atlas slots
```

## 0.6.6.0 PRODUCTION ENCODER REAL-TEXT — PASS

Runtime phrase:

```text
Chọn tướng
```

Proven:
- actual accented Vietnamese text encodes end-to-end;
- plain Latin uses native Gaia glyphs;
- `ọ`, `ư`, `ớ` use custom zero-static-hit codes + safe atlas cells;
- mapping-only production encoding works without code hook/pointer redirect;
- stable boot/UI.

Remaining issue at that step was vertical baseline because custom bodies were forced into a fixed band.

## 0.6.6.1 BASELINE-NORMALIZED REAL-TEXT — PASS

Runtime screenshot shows `Chọn tướng` with custom Vietnamese glyphs aligned acceptably with native Latin.

Decision:

> glyph generation, mapping, real-text encoding, and vertical baseline are now considered solved enough for production. Do not keep polishing this proof phrase vertically.

Observed remaining issue:
- horizontal character spacing is visibly wider than natural Latin typography.

This is **not** a glyph/mapping/baseline failure.

## Proven horizontal-advance reverse facts

Gaia does not simply add a hardcoded 12 pixels. It caches a 16-byte per-glyph record and uses `record+6` as horizontal advance.

### Cache hit

```text
record = state+84 + cache_slot*16
advance = record.byte6
cursor_x = state+24
cursor_x += advance
if advance != state+62:
    cursor_x += state+60
```

Key neighborhood:

```text
0x8003CB54  lbu v0,6(a0)
...
0x8003CBF4  lbu v1,6(a0)
0x8003CBF8  lhu v0,24(s1)
0x8003CC00  addu a1,v0,v1
0x8003CC04  sh a1,24(s1)
0x8003CC08  lbu v1,6(a0)
0x8003CC0C  lh v0,62(s1)
0x8003CC14  beq v1,v0,...
0x8003CC1C  lhu v0,60(s1)
0x8003CC24  addu v0,a1,v0
```

### Cache miss

After glyph copy:

```text
copy_return == 8
    ? advance = state+62
    : advance = state+64 + 1

if advance != state+62:
    advance += state+60

state+24 += advance
```

Key neighborhood:

```text
0x8003CC98  bne a0,8,...
0x8003CCA0  lh v0,62(s1)
...
0x8003CCAC  lh v0,64(s1)
0x8003CCB4  addiu v0,v0,1
...
0x8003CD64  lh v1,62(s1)
0x8003CD74  lh v0,60(s1)
0x8003CD7C  addu a0,a0,v0
0x8003CD80  lhu v0,24(s1)
0x8003CD88  addu v0,v0,a0
0x8003CD90  sh v0,24(s1)
```

Interpretation currently allowed:
- `state+60` = extra tracking;
- `state+62` = special/small advance candidate;
- `state+64` = native dimension feeding normal advance;
- cache `record+6` = final advance used on subsequent hits.

Do **not** yet claim a half-width mode is proven. Ownership/value source of these state fields is still pending.

## CURRENT — READ-ONLY FontSpacingScanner 0.1

Detailed note:

`FONT_SPACING_SCANNER_0.1.md`

Files:

```text
tools/font_spacing_scanner_0.1.py
tools/00_RUN_FONT_SPACING_SCANNER_0.1.cmd
```

Expected report:

```text
GaiaMaster_FontSpacingScanner_01.txt
```

Scanner behavior:
- CLEAN or Alpha 0.6.1 BIN accepted;
- no patch;
- no emulator boot;
- scans every direct READ/WRITE xref to `state+0x3C/+0x3E/+0x40`;
- scans cache-field writes `+0x54/+0x58/+0x5C/+0x60/+0x64/+0x6C`;
- dumps cache hit/miss advance neighborhoods;
- dumps renderer/cache init neighborhood through `0x8003D780`;
- lists direct callers into that init range.

Goal:

> prove where `state+60`, `state+62`, and `state+64` come from before touching runtime spacing.

Preferred outcome:
- if these are constructor/config metrics, use a local/native spacing path or data-side metric change;
- avoid global cursor hooks.

## Next gate

Only after spacing ownership is proven should a runtime `0.6.6.2` be considered.

Possible safe direction, if supported by report:

```text
Vietnamese/Latin text
 -> native mapping/glyph pipeline
 -> local proportional/smaller advance metric
 -> no global Japanese spacing regression
```

## Hard do-not-repeat

- no Krom path;
- no production 12x16;
- no failed 0.6.3.x retests;
- no composite X/Y tuning;
- no 0.6.5.2 runtime redirect;
- no assumption consecutive code == consecutive atlas slot;
- no 0.6.5.3 retest;
- no more 12-glyph style-board loops unless a production regression requires it;
- do not reopen mapping/encoder/baseline because of horizontal spacing;
- **no runtime spacing patch until `state+60/+62/+64` ownership is proven**;
- stop immediately on freeze/global corruption.

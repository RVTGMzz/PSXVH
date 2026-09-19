# SESSION HANDOFF 2026-09-19 - B52R21R1 UI SOURCE PIVOT

Repo: `RVTGMzz/PSXVH`  
Branch: `gaia-character-select-font-atlas-reverse-01`

## Why this handoff exists

This session moved Gaia Master from broad runtime text expansion into a focused reverse-engineering problem: several large UI/menu screens remain Japanese even though their obvious CP932 copies have already been changed.

The key outcome is not another translation count. It is a **source-of-truth pivot**:

> Known PRGPACK CP932 copies for the remaining UI are not the live render source.

## Current exact base

B52R14R1:

`0ced9982e1b00566b42ace047236378826c2aa1c`

Use it as the exact known input for the next reverse tool.

CLEAN:

`f4d5298583c90d89c4b7e51d2dde160ee07f2aec`

## Evidence chain

### B52R14R1
Safe cross-ISO BDP build:
- 23 files indexed
- 19 MODE2/Form1 scanned
- 4 XA/Form2 skipped
- 6 exact player-count fields patched
- BDP checksum read-back PASS
- font/mapping unchanged

### B52R15
25 unresolved rows:
- 41 exact-hit rows
- 0 plain patch candidates
- all 41 were `BASE_ALREADY_CHANGED`

### B52R16
- 173 raw TIM found
- initial 48 previewed

### B52R17
39 target strings:
- 57 CLEAN hits
- 57 `CHANGED_COPY`
- 0 unchanged candidate
- 0 non-CP932 candidate

### B52R18
Corrected the B52R16 sampling limitation:
- exported all 173 TIM assets
- reviewed 4 atlas pages + UI shortlist
- target menu/load/character UI not found

### B52R19
Tile/glyph-index hypothesis:
- 39/39 targets JIS-compatible
- 0 hits
- 0 live candidates
- unknown constant-bias scan also 0

### B52R20
Known text copies used only as BDP landmarks:
- 57 exact CLEAN landmarks
- all 57 inside BDP owners
- 5 owner/member centers
- 8 sibling members exported

Important PRGPACK owners:
- `0xBF7AC..0xDDA98`
- `0xDDA98..0x104660`
- `0x14B970..0x155C1C`

Important SCR_DATA owners:
- `0x9741A8..0x994850`
- `0x9C1BF4..0x9CE4CC`

Raw 4bpp/8bpp/16bpp previews did not reveal the target visible UI.

### B52R21 / R1
B52R21 stopped correctly:
- `ルール -> Luật`
- 8 encoded bytes > 6 source bytes

R1 removed that row and normalized the known PRGPACK UI-copy spans.

User then tested and supplied screenshots:
- main menu still Japanese
- Character Select still Japanese
- `冒険のはじまり` still Japanese
- user explicitly said no visible change

This is the decisive runtime observation.

## Dead paths now closed

Do not burn another session on:
- rewriting the same PRGPACK CP932 locations;
- whole-disc CP932/alternate-encoding scans;
- raw TIM census;
- JIS/tile/glyph index scans;
- unknown constant-bias JIS scan;
- raw grayscale/direct-color sibling member previews.

Only revisit one of these if genuinely new evidence points back to it.

## Next technical hypothesis

Remaining UI is likely one of:

1. compressed graphic/script block;
2. custom packed archive member needing format-specific decode;
3. runtime-generated large-font/tile UI using a lookup/control structure not represented as sequential JIS IDs;
4. composition data referencing glyphs/tiles through a non-JIS table.

Start with the stable main-menu label:

`ストーリーモード`

Why:
- always visible;
- large distinctive geometry;
- deterministic screen;
- easy runtime verification.

Do targeted reverse:
- find candidate compressed/custom blocks near menu scene assets/code;
- inspect decompression/upload path if source-level static data is opaque;
- use delta/runtime evidence instead of another blind full-disc encoding search.

## Translation target reminders

- ストーリーモード -> Cốt truyện
- 対戦モード -> Đối kháng
- 武器スキルリスト -> Kỹ năng vũ khí
- オプション -> Tùy chọn
- キャラクターセレクト -> Chọn nhân vật
- 冒険のはじまり -> Bắt đầu cuộc phiêu lưu / Khởi đầu hành trình

## Runtime policy

Overall Runtime PASS remains NO.

Allowed:
- B52R11R3 quick-path runtime OK
- B52R12 user-confirmed path OK
- B52R21R1 known PRGPACK UI-copy path runtime-dead for the tested screens

Do not promote those to whole-game PASS.

## Disk-space policy

User reported local repo/worktree around 20 GB.

Next chat should avoid creating full BIN for read-only analysis.
Keep local only:
- CLEAN ROM
- exact current base
- newest candidate under test

Keep in Git:
- scripts
- manifests
- reports
- handoff notes

Later create `GaiaMaster_SAFE_CLEANUP.cmd` with preview-first deletion and hard KEEP guards.

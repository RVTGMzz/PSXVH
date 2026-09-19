# HANDOFF CURRENT - Gaia Master PS1 Việt hóa

Updated: 2026-09-19
Repo: `RVTGMzz/PSXVH`
Branch: `gaia-character-select-font-atlas-reverse-01`

## Current priority

**Dừng hẳn nhánh vá UI bằng các CP932 copy đã biết trong PRGPACK.**
Runtime screenshots sau B52R21R1 cho thấy các màn mục tiêu vẫn giữ nguyên tiếng Nhật, nên các copy này không phải live render source của UI đang thấy.

Ưu tiên phiên kế tiếp:

1. reverse **live render source** của UI còn Nhật;
2. tập trung vào **custom-packed / compressed / runtime-generated large-font UI**;
3. ưu tiên các màn:
   - main menu xanh lá;
   - Character Select title + mô tả nhân vật;
   - `冒険のはじまり`;
   - Save / Load / Password;
4. không quay lại plaintext/alternate-encoding/TIM/JIS scan đã đóng;
5. không đụng font trừ khi user chủ động yêu cầu;
6. không gọi Runtime PASS toàn game.

## Repo / account / branch

Canonical repo hiện tại:

`RVTGMzz/PSXVH`

Branch:

`gaia-character-select-font-atlas-reverse-01`

Repo trước `ronvotri/Viet-Hoa-PS1` đã đổi tên, không dùng tên cũ nữa.

## CLEAN contract

Exact CLEAN Japan BIN SHA1:

`f4d5298583c90d89c4b7e51d2dde160ee07f2aec`

Không commit ROM/BIN/CUE/ISO lên GitHub.

## Frozen architecture

Giữ nguyên:

- native 12x12 / 72-byte / 4bpp / LOW nibble first
- static mapping-only
- frozen 60-glyph Vietnamese codepage
- no renderer hook
- no pointer redirect
- no 12x16
- no 6x12
- no composite overlay

Font accent polish vẫn parked:
- hook accent còn hơi thấp/gần thân chữ;
- acute trên `ế` chưa thật rõ;
- không sửa font trong UI reverse track hiện tại.

## Canonical runtime lineage

### B50
Canonical exact-offset overlay:
- 1229/1229 static byte-fit PASS
- direct41 + compact1188
- canonical B50 immutable

### B51R2
Real CLEAN dry-run/build PASS.
- rebuilt PREB45 base SHA1: `d7a9be56dabc4b0222e88f264536a0c7b54da3f9`
- B51R2 exact overlay output SHA1: `b50f444193799653ba09df594eadab29f6e0420c`

### B52R7/R8/R9
SCR_DATA translation expanded to strict queue 258/258, but raw builds exposed runtime hangs.

### Critical checksum discovery
SCR_DATA contains **303 nested historical-BDP-like containers**.
Every SCR_DATA mutation must repair all relevant nested checksums bottom-up before output validation.

This was proven by B52R8D4/D5. Do not return to un-repaired SCR_DATA builds.

### B52R10
Checksum-safe SCR base.
- output SHA1: `61f9175d7f14fa94744a7525fcfde6102e65580d`
- broad residual scanner is noisy and must not be used as an automatic translation queue.

### B52R11R3
Curated runtime text95 + checksum-safe.
- 95/95 curated unique
- 266/266 explicit fields
- output SHA1: `c305f17c7c1ac9aeb26e8a4c0546c6dc1c3286b7`
- user quick-path runtime: **OK**
- overall Runtime PASS: NO

### B52R12
Curated expansion based on B52R11R3.
- includes GO / Cinema labels and expansion of known reviewed strings
- user said build/runtime path was OK
- B52R12 base SHA1 later proven by reports:
  `e4cb8c1f485ed66008d6d69f26d06c906d738692`

### B52R14R1
Cross-ISO BDP-safe text build.
- 23 ISO files indexed
- 19 Form1 scanned
- 4 XA/Form2 skipped safely
- 6 exact fields patched, all player-count copies
- BDP checksum read-back PASS
- font/mapping unchanged
- output SHA1:
  `0ced9982e1b00566b42ace047236378826c2aa1c`

**Use B52R14R1 as the known exact current base for new reverse tooling until a newer base is explicitly proven and recorded.**

## UI reverse results B52R15-B52R21R1

### B52R15 - unresolved asset locator
For 25 unresolved UI strings:
- exact-hit rows: 41
- plain patch candidates: 0
- all 41 classified `BASE_ALREADY_CHANGED`

Meaning: known CLEAN CP932 copies were already modified in the current base, yet visible Japanese remained.

### B52R16 - initial TIM census
- 173 raw TIM assets discovered
- 48 previews exported
- target UI not seen in initial contact sheet

### B52R17 - alternate encoding census
39 visible target strings:
- all CLEAN encoding hits: 57
- unchanged source candidates: 0
- non-CP932 live candidates: 0
- all hits were CP932 `CHANGED_COPY`

Closed paths:
- CP932 word swap
- UTF-16 LE/BE
- EUC-JP
- JIS payload / pair swap

### B52R18 - full TIM atlas
All 173 raw TIM assets were exported and reviewed.
The target green menu / Character Select / Load UI was **not present** in the raw TIM atlas.

Therefore do not repeat raw TIM census.

### B52R19 - tile/glyph-index census
39/39 target strings JIS-compatible.
Results:
- all tile/index hits: 0
- unchanged live candidates: 0
- fixed JIS representations: none
- unknown constant-bias glyph scan: none

Therefore do not repeat JIS/tile-index scans.

### B52R20 - owner/sibling raw-gfx probe
Using CLEAN CP932 copies as landmarks:
- exact CLEAN landmark hits: 57
- landmarks inside BDP owner: 57/57
- unique owner/member centers: 5
- sibling members exported: 8

Important owners included:
- PRGPACK `0xBF7AC..0xDDA98`
- PRGPACK `0xDDA98..0x104660`
- PRGPACK `0x14B970..0x155C1C`
- SCR_DATA `0x9741A8..0x994850`
- SCR_DATA `0x9C1BF4..0x9CE4CC`

Raw 4bpp/8bpp/16bpp previews around these members did not expose the target visible UI.

### B52R21
First normalization build stopped correctly on byte overflow:
`ルール -> Luật: 8 > 6`

Do not reintroduce this row without a byte-fit alternative.

### B52R21R1
Removed the overflowing Rule row and normalized the known PRGPACK UI text spans.

User runtime check after B52R21R1:
- main menu still Japanese;
- Character Select title/details still Japanese;
- `冒険のはじまり` still Japanese;
- user explicitly reported no visible change.

**Conclusion: the known PRGPACK CP932 copies are runtime-dead for these visible screens.**
Do not spend another batch re-patching these exact offsets.

## Closed/dead reverse paths

Do NOT restart these without genuinely new evidence:

- exact PRGPACK CP932 rewrite of known B52R15/B52R20 locations;
- whole-ISO alternate encodings;
- raw TIM atlas scan;
- JIS/tile/glyph-index representations;
- unknown constant-bias JIS glyph scan;
- raw 4/8/16bpp sibling preview around known text owners.

## Next reverse direction

Treat remaining visible UI as one of:

1. compressed/custom-packed graphic or script data;
2. runtime-generated large-font UI using a different source/renderer;
3. custom archive member decoding not exposed by raw preview;
4. possibly texture/tile composition whose source is not a plain sequential glyph list.

Next session should use **targeted runtime/live-source reverse**, not another whole-disc encoding census.

Recommended first target:
- main menu `ストーリーモード` because it is large, stable, easy to identify visually.

Then:
- `キャラクターセレクト`
- `冒険のはじまり`
- Save/Load/Password UI

## Translation status / wording

Do not lose the user-facing wording targets:

- ストーリーモード -> Cốt truyện / Chế độ cốt truyện
- 対戦モード -> Đối kháng
- 武器スキルリスト -> Kỹ năng vũ khí
- オプション -> Tùy chọn
- キャラクターセレクト -> Chọn nhân vật
- はじめから -> Bắt đầu
- つづきから -> Chơi tiếp
- ロード方法をえらんでね -> Chọn cách tải / Chọn tải
- セーブデータをロードする -> Tải dữ liệu lưu
- パスワードを使う -> Dùng mật khẩu
- 冒険のはじまり -> Bắt đầu cuộc phiêu lưu / Khởi đầu hành trình

Use shorter wording only when pixel/byte space proves necessary.

## Local disk / cleanup issue

User reported local GitHub working copy is already around **20 GB**.

From now on:
- stop accumulating full-disc BIN for every diagnostic milestone;
- tools/reports/CSV are cheap and should be kept;
- ROM/BIN/CUE/ISO remain local-only and ignored;
- prefer one exact current runtime base + one newest output;
- generated TIM/raw preview atlases may be deleted after evidence is captured in reports;
- prepare a conservative `GaiaMaster_SAFE_CLEANUP.cmd` later:
  - never delete CLEAN;
  - never delete current known base;
  - never touch source/manifests/reports/tools/.git;
  - list candidates before deleting;
  - target superseded full BINs and temporary preview/export folders.

Do not casually tell the user to delete files by hand until keep/delete rules are explicit.

## Allowed claims

Allowed:
- B50 static exact-overlay PASS
- B51R2 real CLEAN dry-run/build PASS
- B52R11R3 quick-path runtime OK
- B52R12 current path was user-confirmed OK
- B52R14R1 static/read-back/checksum PASS
- B52R15-B52R20 read-only reverse results as recorded
- B52R21R1 visible UI source path is runtime-dead based on user screenshots

Not allowed:
- overall Runtime PASS
- claiming the remaining UI source has already been identified
- claiming B52R21R1 translated the visible UI

## Fresh-chat continuation

Use `NEXT_CHAT_PROMPT.md`.

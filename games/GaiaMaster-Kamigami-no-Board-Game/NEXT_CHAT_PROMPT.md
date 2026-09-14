# Prompt mở phiên chat mới — Gaia Master

Copy nguyên câu dưới đây vào phiên mới:

> Tiếp tục Gaia Master từ `games/GaiaMaster-Kamigami-no-Board-Game/HANDOFF_CURRENT.md` trên branch `gaia-character-select-font-atlas-reverse-01` của repo `ronvotri/Viet-Hoa-PS1`. Đọc thêm `LATEST.md`, `BATCH44_0.6.54.0.md`, `BATCH45_0.6.55.0_FRONTFACE_POLISH.md`, `BATCH45R2_0.6.55.1_FONT_MICRO_POLISH.md` và `REVERSE_WORKBENCH_0.1.md`. Mốc actual CLEAN-ROM build cuối cùng đã chứng minh vẫn là `0.6.54.0 R5`: Batch42 560/560, Batch43 102/102, combined 662/662, legacy 397/397, return code 0. User đã runtime-test 0.6.55.0 và gửi screenshot `Thế giới đổi chủ`: lỗi rác do `=` không còn thấy trong dòng này, nhưng font chưa PASS. Lowercase `đ` vẫn sai vì generic stroke rule neo theo mép trái trong khi native `d` có ascender bên phải; user yêu cầu thanh ngang lên thêm 1 px và phải xuyên đúng thân dọc. User cũng phát hiện circumflex `^` ở `â/ê/ô` quá sát thân và stacked marks dễ đè nhau. `0.6.55.1 Batch45R2` đã được thêm để tách `Đ`/`đ`: uppercase `Đ` dùng left-stem + pre-Batch45 vertical placement vì chưa có runtime evidence nó lỗi; lowercase `đ` auto-detect right stem và dùng center-2 (một px cao hơn 0.6.55.0). Circumflex/breve reserve 3 top rows, structural mark lên 1 px, stacked tones sang side lane riêng. R2 patch SLPS font only, yêu cầu PRGPACK byte-for-byte unchanged, all 60 glyphs 72-byte/12x12, unaffected glyphs byte-identical, structural/tone rendered pixels non-overlap, Batch42/intro gates recheck trước+sau. Không được gọi Runtime PASS nếu chưa có screenshot 0.6.55.1. Reverse Workbench 0.1 read-only vẫn dùng cho Main Menu / Character Select / Story/chapter/purchase prompt sau khi font gate ổn. Giữ architecture native 12x12 / mapping-only / frozen 60 glyph, không renderer hook, pointer redirect, 12x16, 6x12 hay composite overlay.

## Current branch

```text
gaia-character-select-font-atlas-reverse-01
```

## Files phải đọc đầu tiên

```text
games/GaiaMaster-Kamigami-no-Board-Game/HANDOFF_CURRENT.md
games/GaiaMaster-Kamigami-no-Board-Game/LATEST.md
games/GaiaMaster-Kamigami-no-Board-Game/BATCH44_0.6.54.0.md
games/GaiaMaster-Kamigami-no-Board-Game/BATCH45_0.6.55.0_FRONTFACE_POLISH.md
games/GaiaMaster-Kamigami-no-Board-Game/BATCH45R2_0.6.55.1_FONT_MICRO_POLISH.md
games/GaiaMaster-Kamigami-no-Board-Game/REVERSE_WORKBENCH_0.1.md
```

## Current R2 builder

```text
tools/build_gaia_06551_batch45r2_font_micro_polish.py
tools/00_BUILD_0.6.55.1_BATCH45R2_FONT_POLISH.cmd
```

## First action in next chat

```text
1. Nếu user gửi BUILD_LOG: sửa đúng lỗi gate đầu tiên trước, không nhảy sang việc khác.
2. Nếu user gửi FINAL_REPORT 0.6.55.1 + screenshot: audit đ / Đ / â-ê-ô / stacked accents ngay.
3. Chỉ khi screenshot chứng minh ổn mới khóa font Batch45R2.
4. Sau font gate, phân tích Reverse Workbench và reverse main-menu / Character Select asset.
5. Continue exact-offset discovery for Story / chapter `冒険のはじまり` / purchase prompt.
```

## Runtime font expectations 0.6.55.1

```text
đ  : thanh ngang phải xuyên thân dọc bên phải của d, cao hơn 0.6.55.0 một pixel
Đ  : giữ left-stem form; không tự retune thêm nếu chưa có screenshot chứng minh lỗi
âêô: ^ phải tách khỏi thân rõ hơn
ấếố...: tone không được nhập/đè với ^
ắ: acute không được đè với breve
```

## Reverse Workbench 0.1 outputs

```text
GaiaMaster_GRAPHIC_ASSET_CENSUS_0.1_REPORT.txt
GaiaMaster_GRAPHIC_ASSET_CENSUS_0.1_OWNERS.csv
GaiaMaster_GRAPHIC_ASSET_CENSUS_0.1_TIM.csv
GaiaMaster_RUNTIME_TARGET_LOCATOR_0.1_REPORT.txt
```

Known Character Select anchor:

```text
PRGPACK.BDP + 0xBFD2C
owner = 29
owner-local = +0x580
source = キャラクターをえらんでね
```

Do not invent the offset of `冒険のはじまり`; the committed repo still lacks the full 0.6.38 scanner CSV.

## Hard contracts

```text
CLEAN SHA1 = f4d5298583c90d89c4b7e51d2dde160ee07f2aec
Batch42 exact = 560/560
Batch43 visible = 102/102
Combined exact = 662/662
Legacy = 397/397
Architecture = native 12x12 / 72-byte / 4bpp / mapping-only / frozen 60 glyphs
```

## Do not regress

- production source must consume staged `Core/translation`;
- dynamic rows must not overlap master-owned ranges;
- same-offset dynamic replacement requires exact source identity;
- Batch43 source identity is checked against CLEAN ROM;
- Batch43 may not overlap the 560 exact fields;
- preserve `%s`, `%d`, `%4d`, `%+3d`, `/V` and token order;
- do not equate 596/596 Translation Master coverage with whole-game coverage;
- Reverse Workbench is read-only discovery, not production promotion proof;
- do not create Batch46 while Batch45R2 runtime font gate is unresolved;
- do not call Runtime PASS before gameplay screenshots prove it.

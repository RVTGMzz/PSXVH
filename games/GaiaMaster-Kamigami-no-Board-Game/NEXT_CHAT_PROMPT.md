# Prompt mở phiên chat mới — Gaia Master

Copy nguyên câu dưới đây vào phiên mới:

> Tiếp tục Gaia Master từ `games/GaiaMaster-Kamigami-no-Board-Game/HANDOFF_CURRENT.md` trên branch `gaia-character-select-font-atlas-reverse-01` của repo `ronvotri/Viet-Hoa-PS1`. Đọc thêm `LATEST.md`, `BATCH44_0.6.54.0.md` và `BATCH45_0.6.55.0_FRONTFACE_POLISH.md`. Mốc actual build đã chứng minh là `0.6.54.0 R5`: CLEAN SHA1 đúng, Batch42 560/560, Batch43 102/102, combined 662/662, legacy 397/397, return code 0. Runtime screenshot cho thấy chưa thể gọi whole-game Runtime PASS: main menu, Character Select, Story mở đầu, chapter card `冒険のはじまり`, prompt mua đất và nhiều text khác vẫn còn Nhật. `0.6.55.0 Batch45` đã được chuẩn bị để sửa 19 dòng intro, bỏ dấu `=` gây glyph rác và nâng thanh ngang `Đ/đ` lên 1 px; static selftest PASS nhưng cần runtime-test đúng CUE 0.6.55.0. Sau đó ưu tiên reverse graphic asset của main menu / Character Select và scanner-driven exact offsets cho Story/chapter/purchase prompt. Giữ kiến trúc native 12x12 / 72-byte / 4bpp / mapping-only / frozen 60 glyph; không renderer hook, pointer redirect, 12x16, 6x12 hay composite overlay.

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
```

## First action in next chat

```text
1. Runtime-test exact 0.6.55.0 CUE.
2. Check intro for no garbage glyph and more natural wording.
3. Check Đ/đ crossbar readability.
4. If stable, reverse main-menu / Character Select graphic assets.
5. Continue exact-offset discovery for Story / chapter / purchase prompt.
```

## Hard contracts

```text
CLEAN SHA1 = f4d5298583c90d89c4b7e51d2dde160ee07f2aec
Batch42 exact = 560/560
Batch43 visible = 102/102
Combined exact = 662/662
Legacy = 397/397
```

## Do not regress

- production source must consume staged `Core/translation`;
- dynamic rows must not overlap master-owned ranges;
- same-offset dynamic replacement requires exact source identity;
- Batch43 source identity is checked against CLEAN ROM;
- Batch43 may not overlap the 560 exact fields;
- preserve `%s`, `%d`, `%4d`, `%+3d`, `/V` and token order;
- do not equate 596/596 Translation Master coverage with whole-game coverage;
- do not call Runtime PASS before gameplay screenshots prove it.

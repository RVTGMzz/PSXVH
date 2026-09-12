# Prompt mở phiên chat mới — Gaia Master

Copy nguyên câu dưới đây vào phiên mới:

> Tiếp tục Gaia Master từ `HANDOFF_CURRENT.md` trên branch `gaia-character-select-font-atlas-reverse-01`. Đọc thêm `LATEST.md` và `FONT_ISOLATION_0.6.3.0_FAIL.md`. 0.6.3.0 EXTENDED HEIGHT 12x16 đã runtime FAIL, không test lại và không quay về mài glyph 12x12. Bắt đầu bằng reverse toàn bộ target render path từ final glyph pointer qua copy/unpack/cache tới GPU primitive để xác định chính xác stage nào vẫn khóa native 12-row/72-byte geometry. Chỉ build probe mới sau khi đã cô lập được một giả thuyết cụ thể.

## Current branch

```text
gaia-character-select-font-atlas-reverse-01
```

## Files phải đọc đầu tiên

```text
games/GaiaMaster-Kamigami-no-Board-Game/HANDOFF_CURRENT.md
games/GaiaMaster-Kamigami-no-Board-Game/LATEST.md
games/GaiaMaster-Kamigami-no-Board-Game/FONT_ISOLATION_0.6.3.0_FAIL.md
```

## Không được lặp lại

- không test lại 0.6.2.18;
- không test lại 0.6.3.0;
- không quay về Krom wrapper cho Character Select;
- không tiếp tục vòng lặp chỉnh từng pixel `Ế` trong 12x12;
- không build thêm 12x16 probe mù trước khi reverse đủ copy/unpack/buffer/sprite/clipping path.

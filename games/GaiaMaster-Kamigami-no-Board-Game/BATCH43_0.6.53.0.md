# Gaia Master 0.6.53.0 — Batch43 Whole-Game Visible Expansion

Nguồn: `GaiaMaster_0.6.38.0_FULL_JAPANESE_SCAN.csv` do CLEAN Japan BIN sinh ra.

Scanner report:

```text
CLEAN SHA1                   = f4d5298583c90d89c4b7e51d2dde160ee07f2aec
Translation Master keys      = 596
Scanner candidates           = 13330
Known same offset            = 561
Known text other offset      = 120
Unseen Japanese candidates   = 12649
Unique unseen Japanese       = 6361
Screenshot-anchor hits       = 18
```

Batch43 chọn **102 row mới** theo exact offset, tất cả đều:

- `PRGPACK.BDP`
- scanner confidence = `HIGH`
- NUL-terminated
- không overlap tập exact Batch40
- token identity/order giữ nguyên
- fit byte budget
- chỉ dùng frozen 60-glyph Vietnamese codepage + CP932/ASCII hợp lệ

Phạm vi ưu tiên:

1. Memory Card / initialization / save / load.
2. Một số repeated-unmapped labels như `バトルカード`, `いちかばちか`, `みがわり`.
3. Tutorial/help cụm `PRGPACK.BDP 0x143090..0x14363C`.
4. Screenshot anchor:

```text
同じエリアのマスを3つそろえるの！
-> Gom 3 ô cùng khu
```

Manifest:

`translation/BATCH43_WHOLEGAME_VISIBLE_0.6.53.0.csv`

Static package selftest hiện tại:

```text
Base exact contract    = 560
New visible expansion = 102
Combined exact fields = 662
Token/codepage/fit    = PASS
Master overlap         = 0
```

Runtime proof vẫn bắt buộc. Không gọi whole-game complete hoặc Runtime PASS chỉ từ static result.

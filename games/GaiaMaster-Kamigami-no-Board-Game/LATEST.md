# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-12 sau runtime test 0.6.3.5 POST-COPY RAM SENTINEL**.

## Chốt hiện tại

- 0.6.2.x: custom Vietnamese glyph pipeline đã PASS.
- Native 12x12 bị loại cho production stacked Vietnamese diacritics vì quá chật.
- 0.6.3.0 12x16 = **STRUCTURAL PASS**.
- 0.6.3.1 shared cache-stride rewrite = **UNSAFE FAIL**: global text corruption + freeze. Không retest.
- 0.6.3.2 BASELINE ONLY = **STABLE PASS**, nhưng phần đáy target extended mất/cắt.
- 0.6.3.3 EOL OVERWRITE = **same result**, loại giả thuyết glyph kế tiếp overwrite.
- 0.6.3.4 UV WINDOW TEST = **negative diagnostic**, `V+4` không phục hồi đáy E đúng/clean.
- 0.6.3.5 POST-COPY RAM SENTINEL = **sentinel not observed**; không được dùng để kết luận clipping vì late hook nhận diện target bằng `s0` chưa được chứng minh còn hợp lệ.

## Font path đã chứng minh

```text
atlas file   = SLPS + 0x5C4EC
mapping file = SLPS + 0x6B6CC
atlas RAM    = 0x8006BCEC
mapping RAM  = 0x8007AECC
860 glyphs
native 12x12 / 72-byte / 4bpp / LOW nibble first
```

Confirmed:

```text
0x8273 Ｔ -> glyph 481
0x8264 Ｅ -> glyph 466
0x8272 Ｓ -> glyph 480
0x889F 亜 -> glyph 0
```

## Extended-height facts

Wide custom copy routine:

```text
0x8003C67C
```

Geometry:

```text
6 source bytes/row -> 8 converted/cache bytes/row
12 rows -> 96 converted bytes
16 rows -> 128 converted bytes
```

Metadata `height=15` makes the loop process 16 rows.

Font cache/upload page itself is much taller than 12 rows (roughly 240-row page), so missing rows are not explained by a glyph-only upload RECT hardcoded to 12.

## 0.6.3.5 runtime result

Control:

```text
ＴＥＳＴ亜
```

Intended sentinel after copy:

```text
rows 10..11 = dark/gray band
rows 12..15 = bright white band
```

Runtime screenshot:

- Japanese header normal;
- `ＴＥＳＴ` normal;
- target resembles previous truncated glyph;
- no clear gray band;
- no clear white lower band;
- no global corruption/freeze.

=> 0.6.3.5 did not prove anything about row12..15 survival.
=> strongest issue: late hook at `0x8003CC4C` checked `s0 == 0x889F`, but `s0` is not proven to still be the original character code at that stage.

Do not retest 0.6.3.5.

## CURRENT — 0.6.3.6 EARLY-FLAG POST-COPY SENTINEL

Same stable extended path and same sentinel pattern, but target identity is now decided **early** at the proven metadata hook:

```text
target 0x889F -> FLAG = 1
other glyph    -> FLAG = 0
```

The post-copy hook reads only FLAG and never trusts late-stage `s0`.

Sentinel remains:

```text
rows 10..11 = dark/gray full band  # control
rows 12..15 = bright white full band  # test
```

Interpretation:

- gray + white visible => rows12..15 survive converted RAM -> VRAM -> sprite;
- gray visible but white absent => rows12..15 are lost after converted RAM;
- neither visible => our assumed post-copy destination/path is wrong; do not infer clipping.

Package:

```text
GaiaMaster_FontIsolation_0.6.3.6_EARLY_FLAG_POST_COPY_SENTINEL.zip
```

Launcher:

```text
00_RUN_PROBE_0636.cmd
```

## Do not repeat

- Không quay lại Krom path.
- Không polish stacked accents production trong 12x12.
- Không retest 0.6.2.18, 0.6.3.0, 0.6.3.1, 0.6.3.2, 0.6.3.3, 0.6.3.4 hoặc 0.6.3.5.
- Không patch shared `0x8003CD94..0x8003CDB4` theo kiểu 0.6.3.1.

## Sau khi extended-height path ổn định

1. production-safe Vietnamese extended atlas/cache storage;
2. full Vietnamese glyph inventory;
3. compact runtime codepage/mapping;
4. encode `vi_full` có dấu;
5. solve/repack 230 pending rows;
6. clean mixed JP/VI;
7. graphic menu/title patch;
8. full runtime QA + reproducible build.

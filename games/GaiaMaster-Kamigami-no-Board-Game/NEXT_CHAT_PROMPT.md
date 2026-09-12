# Prompt mở phiên chat mới — Gaia Master

Copy nguyên câu dưới đây vào phiên mới:

> Tiếp tục Gaia Master từ `HANDOFF_CURRENT.md` trên branch `gaia-character-select-font-atlas-reverse-01`. Đọc thêm `LATEST.md`, `CHARACTER_SELECT_FONT_REVERSE_0.1.md`, `PROBE_BUILD_INDEX.md`, `FONT_ISOLATION_0.6.3.1_UNSAFE_FAIL.md`, `FONT_ISOLATION_0.6.3.2_STABLE_PASS.md`, `FONT_ISOLATION_0.6.3.3_EOL_OVERWRITE_TEST.md` và `FONT_ISOLATION_0.6.3.4_UV_WINDOW_TEST.md`. Runtime 0.6.3.3 cho kết quả y hệt 0.6.3.2 dù target nằm cuối dòng, nên giả thuyết glyph phía sau overwrite 4 hàng đáy đã bị loại. Current probe là 0.6.3.4 UV WINDOW TEST: giữ 16-row copy, sprite height 16, baseline Y -4, không đụng CD94/cache allocator, chỉ dịch target texture V +4 để xác định 4 hàng đáy có tồn tại trong VRAM nhưng đang bị texture-window sampling sai hay không. Không retest các build cũ và không quay về mài dấu trong 12x12.

## Current branch

```text
gaia-character-select-font-atlas-reverse-01
```

## Files phải đọc đầu tiên

```text
games/GaiaMaster-Kamigami-no-Board-Game/HANDOFF_CURRENT.md
games/GaiaMaster-Kamigami-no-Board-Game/LATEST.md
games/GaiaMaster-Kamigami-no-Board-Game/CHARACTER_SELECT_FONT_REVERSE_0.1.md
games/GaiaMaster-Kamigami-no-Board-Game/PROBE_BUILD_INDEX.md
games/GaiaMaster-Kamigami-no-Board-Game/FONT_ISOLATION_0.6.3.1_UNSAFE_FAIL.md
games/GaiaMaster-Kamigami-no-Board-Game/FONT_ISOLATION_0.6.3.2_STABLE_PASS.md
games/GaiaMaster-Kamigami-no-Board-Game/FONT_ISOLATION_0.6.3.3_EOL_OVERWRITE_TEST.md
games/GaiaMaster-Kamigami-no-Board-Game/FONT_ISOLATION_0.6.3.4_UV_WINDOW_TEST.md
```

## Current runtime facts

### 0.6.3.0

**STRUCTURAL PASS** for target 12x16 source/copy/display.

Do not retest.

### 0.6.3.1

**UNSAFE FAIL**:

- global Japanese text corruption;
- repeated/misplaced glyphs;
- later garbled screen;
- game freeze.

Do not retest.
Do not naively patch shared cache-advance block `0x8003CD94..0x8003CDB4` again.

### 0.6.3.2

**STABLE PASS WITH LOWER-ROW LOSS**:

```text
ＴＥＳＴ亜Ａ
```

- global text normal;
- no freeze;
- baseline corrected;
- trailing `Ａ` intact;
- target bottom missing.

### 0.6.3.3

**EOL OVERWRITE HYPOTHESIS REJECTED**:

```text
ＴＥＳＴ亜
```

Target placed at end-of-line with no following glyph.
Runtime still looks the same as 0.6.3.2 and target bottom is still missing.

=> following-glyph overwrite is not the cause.
=> missing rows are lost/clipped inside target copy/cache/VRAM/texture path itself.

### 0.6.3.4 — current test

One-variable probe:

```text
target texture V += 4
```

Everything else stays on the stable 0.6.3.2/0.6.3.3 path:

- target 16-row source/copy;
- sprite height 16;
- baseline Y -4;
- target at end-of-line;
- no CD94 cache-stride rewrite;
- no shared allocator mutation.

Diagnostic interpretation:

- if bottom E appears while top/accent shifts or disappears, the 16 rows are present in VRAM and the bug is texture-V/window sampling;
- if bottom is still missing/blank/garbled, data is being lost before texture sampling, so reverse converted cache or VRAM upload rectangle/content next.

Current local package:

```text
GaiaMaster_FontIsolation_0.6.3.4_UV_WINDOW_TEST.zip
```

## Không được lặp lại

- không quay về Krom wrapper cho Character Select;
- không test lại 0.6.2.18;
- không test lại 0.6.3.0;
- tuyệt đối không test lại unsafe 0.6.3.1;
- không retest 0.6.3.2 hoặc 0.6.3.3 trừ khi cần đối chiếu byte-level offline, không yêu cầu user chạy lại;
- không quay về vòng lặp chỉnh từng pixel dấu `Ế` trong native 12x12;
- không mutate shared cache allocator/cursor cho target khi chưa chứng minh ownership/state isolation.

## Reusable project knowledge

Đọc thêm:

```text
PS1_LOCALIZATION_REUSABLE_LESSONS.md
```

Nó ghi lại các bài học có thể tái sử dụng cho game PS1 khác, bao gồm vì sao game US/EU Latin thường dễ hơn game Nhật nhưng không phải lúc nào cũng vậy.

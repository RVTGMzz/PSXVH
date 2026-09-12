# Prompt mở phiên chat mới — Gaia Master

Copy nguyên câu dưới đây vào phiên mới:

> Tiếp tục Gaia Master từ `HANDOFF_CURRENT.md` trên branch `gaia-character-select-font-atlas-reverse-01`. Đọc thêm `LATEST.md`, `CHARACTER_SELECT_FONT_REVERSE_0.1.md`, `PROBE_BUILD_INDEX.md`, `FONT_ISOLATION_0.6.3.2_STABLE_PASS.md` và `FONT_ISOLATION_0.6.3.3_EOL_OVERWRITE_TEST.md`. 0.6.3.0 đã chứng minh 12x16 structurally; 0.6.3.1 là UNSAFE FAIL vì shared cache-stride rewrite gây global corruption/freeze; 0.6.3.2 BASELINE ONLY là stable pass nhưng target mất phần đáy khi có glyph theo sau. Current probe là 0.6.3.3 EOL OVERWRITE TEST: `ＴＥＳＴ亜`, không trailing glyph, để xác định có phải glyph sau đang overwrite 4 hàng cuối của target 16-row hay không. Không retest các build cũ và không quay về mài dấu trong 12x12.

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
games/GaiaMaster-Kamigami-no-Board-Game/FONT_ISOLATION_0.6.3.2_STABLE_PASS.md
games/GaiaMaster-Kamigami-no-Board-Game/FONT_ISOLATION_0.6.3.3_EOL_OVERWRITE_TEST.md
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

Strong hypothesis: following native glyph overwrites last 4 converted rows because target writes 128 converted bytes but native cursor advances only 96.

### 0.6.3.3 — current test

```text
ＴＥＳＴ亜
```

Target at end-of-line.
No new hook.
No CD94 stride patch.

Question:

> Does the missing bottom return with no following glyph?

## Không được lặp lại

- không quay về Krom wrapper cho Character Select;
- không test lại 0.6.2.18;
- không test lại 0.6.3.0;
- tuyệt đối không test lại unsafe 0.6.3.1;
- không quay về vòng lặp chỉnh từng pixel dấu `Ế` trong native 12x12;
- không mutate shared cache allocator/cursor cho target khi chưa chứng minh ownership/state isolation.

## Reusable project knowledge

Đọc thêm:

```text
PS1_LOCALIZATION_REUSABLE_LESSONS.md
```

Nó ghi lại các bài học có thể tái sử dụng cho game PS1 khác, bao gồm vì sao game US/EU Latin thường dễ hơn game Nhật nhưng không phải lúc nào cũng vậy.

# Gaia Master 0.6.11.0 — Hybrid Gameplay Accent Batch 2

Updated: **2026-09-14**

## Runtime verdict carried forward

`0.6.10.0` proved the production font path and accented Vietnamese are working at runtime.

The user supplied runtime screenshots showing:

1. accented front/setup text renders with the frozen `0.6.7.2` font;
2. some intro rows using ASCII `=` render a Japanese-looking/garbled glyph;
3. `Tải dữ liệu VK?` is technically compact but unclear Vietnamese;
4. gameplay can become mixed text, e.g. `DUNG トロル通り`, proving the format string was patched while `%s` still receives a Japanese dynamic literal.

Therefore:

```text
0.6.10.0 = FRONT ACCENT/FONT RUNTIME PASS
            CONTENT QA INCOMPLETE
```

No font change is justified. `0.6.7.2` remains frozen.

## Candidate

**0.6.11.0 HYBRID GAMEPLAY ACCENT BATCH 2**

Architecture is unchanged:

```text
native 12x12 / 72-byte / 4bpp
static mapping-only
60-glyph frozen Vietnamese codepage
font visual baseline = 0.6.7.2
exact legacy Alpha coverage gate = 397 / 397
```

The new builder is a wrapper around the exact `0.6.10.0` builder:

```text
tools/build_gaia_06110_hybrid_accent_b2.py
tools/00_BUILD_0.6.11.0_HYBRID_ACCENT_B2.cmd
```

This deliberately keeps the proven font writer, BDP patch/checksum code and exact legacy gate unchanged.

## Front cleanup

New source:

```text
translation/FRONT_ACCENT_OVERRIDES_0.6.11.0.csv
```

Changes prompted directly by runtime QA include:

```text
Người=cờ       -> Người cờ
Thếgiới=bàncờ  -> Thếgiới bàncờ
Ko chống       -> Không chống
Tải dữ liệu VK? -> Tải KN vũ khí?
```

The `=` removal is important because the runtime screenshot showed it resolving to an unrelated Japanese-looking glyph on this route.

## Gameplay Accent Batch 2

Source:

```text
translation/GAMEPLAY_ACCENT_OVERRIDES_0.6.11.0.csv
```

The batch contains **335 compact candidates** spanning:

- setup;
- repeated tavern dialogue;
- gameplay prompts;
- cards;
- items/weapons;
- events;
- menus;
- compact status/name fragments.

Examples:

```text
DUNG %s        -> Dừng %s
NHAN %s        -> Nhận %s
BO %s          -> Bỏ %s
CHON THE DUNG  -> Chọn thẻ dùng
THACH DAU?     -> Thách đấu?
THUE THU NHAP  -> Thuế thu nhập
HOI 50HP!      -> Hồi 50HP!
DOI DUONG      -> Đổi đường
PHI GIAM30%    -> Phí giảm30%
```

The wrapper does **not** force every candidate. Before invoking the exact inner builder it estimates the locked runtime byte cost and only promotes a compact accented candidate when it fits the original Japanese field.

If a candidate is too long:

```text
keep old vi_game_current fallback
```

This is intentional. Accent coverage must never reduce the proven `397/397` gameplay coverage.

## Dynamic Japanese literal fix

New source:

```text
translation/DYNAMIC_LITERAL_OVERRIDES_0.6.11.0.csv
```

First screenshot-proven case:

```text
トロル通り -> Troll
```

The observed runtime line:

```text
DUNG トロル通り
```

should therefore become:

```text
Dừng Troll
```

The wrapper scans the clean extracted SLPS/PRGPACK for exact CP932 literals.

Safety rule:

- equal encoded length may be replaced directly;
- a shorter replacement is only injected when the Japanese literal is a standalone null-delimited string.

This avoids truncating an unknown larger record.

## Production codepage safety

The wrapper rejects any new non-CP932 Vietnamese glyph that is outside the frozen 60-glyph set.

The frozen set remains:

```text
àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ
```

No new atlas slot is allocated.

## Build flow

1. Drag the **CLEAN Japan BIN** onto:

```text
tools/00_BUILD_0.6.11.0_HYBRID_ACCENT_B2.cmd
```

2. Wrapper verifies clean BIN SHA1.
3. Wrapper temporarily applies front/gameplay/dynamic overlays.
4. Exact `0.6.10.0` builder runs and must still pass its normal gates, including exact legacy `397/397`.
5. Original repository CSV files are restored in `finally`, including on builder failure.
6. New/modified build outputs are versioned as `0.6.11.0`.
7. Wrapper emits:

```text
GaiaMaster_0.6.11.0_B2_WRAPPER_REPORT.txt
```

and packages detected BIN/CUE/report outputs when available.

## Next runtime gate

Check in this order:

1. Intro: no garbage glyph where `=` previously appeared.
2. Setup: `Tải KN vũ khí?` is readable and accents remain correct.
3. Start a real match.
4. Trigger the screenshot case: expect `Dừng Troll`, no Japanese suffix.
5. Inspect card/item/event/menu/prompt text for newly accented compact rows.
6. Capture any remaining mixed Japanese `%s` name so it can be added to the dynamic literal table.

## Hard locks

Still do not revisit:

- 12x16 production;
- pointer redirect;
- composite overlay;
- narrow 6x12 alias path;
- global spacing/cursor/cache mutation;
- accent retuning after `0.6.7.2`;
- `0.6.9.0` / `0.6.9.1`.

Content is now the active problem, not font architecture.

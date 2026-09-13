# Gaia Master 0.6.10.0 — Hybrid Full Coverage + Front Accent Batch 1

Updated: **2026-09-13**

## Status

`0.6.9.2` proved that the old Alpha gameplay coverage is alive again: the intro/runtime screenshot showed the old Vietnamese fallback text being used instead of Japanese. This is a **coverage PASS**, but not yet an accent-coverage PASS because `FRONT_DEMO_ADDED_061.csv` only contained `vi_no_accents`.

Current candidate: **0.6.10.0**.

## Architecture lock

- native main font `12x12 / 72-byte / 4bpp / LOW nibble first`;
- static mapping-only font route;
- 60-glyph production Vietnamese codepage;
- visual style frozen at `0.6.7.2`;
- no renderer hook;
- no pointer redirect;
- no 12x16;
- no 6x12 narrow route;
- full-width horizontal spacing remains accepted polish.

## Hybrid coverage gate

The builder reconstructs the old Alpha 0.6.1 patch-key set exactly and requires:

```text
legacy Alpha coverage = 397 / 397
```

Rows that exist only in newer `vi_full` are allowed as extra patches and do not break the gate.

Text preference:

```text
vi_full (accented) if it fits
-> otherwise vi_game_current fallback
-> dedicated front-demo row fallback from FRONT_DEMO_ADDED_061.csv
```

Runtime tokens such as `%d`, `%s`, `%+3d`, `/V`, `/v` are preserved as raw ASCII, matching the old Alpha generator semantics.

## 0.6.9.x gate history

- `0.6.9.0`: **BUILD GATE BUG**, hybrid total was 399 but gate incorrectly demanded total exactly 397. No runtime conclusion.
- `0.6.9.1`: **BUILD GATE BUG**, incorrectly classified many non-fitting `vi_game_current` rows as legacy and reported 228 lost rows. No runtime conclusion.
- `0.6.9.2`: exact legacy reconstruction fixed the gate. Builder/runtime proceeded. Intro screenshot showed Vietnamese fallback text, proving broad legacy coverage pipeline is active. Most intro lines were still unaccented because the dedicated front CSV only had `vi_no_accents`.

## Front accent Batch 1

`0.6.10.0` adds compact accented overrides for all 31 dedicated front/setup rows. Exact data is stored in:

```text
translation/FRONT_ACCENT_OVERRIDES_0.6.10.0.csv
```

Examples:

```text
100 năm mệnh
Lực địa loạn
Thời Gaia Master
Đến lúc!
Thế giới mất chủ
Tải dữ liệu VK?
Kỹ năng LV1
Nhân vật này?
Xác nhận?
```

The front-accent gate requires all 31 overrides to encode and fit. It blocks instead of silently falling back if any accented override fails.

## Exact current builder snapshot

```text
tools/build_gaia_06100_hybrid_accent_b1.py
tools/00_BUILD_0.6.10.0_HYBRID_ACCENT_B1.cmd
```

The Python file in GitHub is a runnable compressed snapshot of the exact readable builder source used to make the local package.

Readable-source SHA1:

```text
faea2fbf90d3b4038ad64d3872934c043115878a
```

Local package name / SHA1:

```text
GaiaMaster_0.6.10.0_HYBRID_FRONT_ACCENT_BATCH1.zip
d43e8547f9baca4e254f96fdb7850a5c6f873e86
```

## Next runtime test

Build from CLEAN BIN, then check intro first.

Expected improvement over 0.6.9.2:

```text
100 năm mệnh
Lực địa loạn
Thời Gaia Master
Đến lúc!
```

should now be accented.

After intro passes, enter a real match and inspect menu/card/item/prompt text. The next production task is **Accent Upgrade Batch 2** for gameplay rows that still fall back to `vi_game_current` without accents.

## Hard locks

Do not revisit:

- 12x16 production;
- pointer redirect;
- composite overlay;
- narrow 6x12 alias path;
- global spacing/cursor mutation;
- accent shape tuning after `0.6.7.2` unless an actual glyph regression is demonstrated.

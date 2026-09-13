# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-13**

## Source-of-truth

Production đã khóa vào:

```text
native 12x12 / 72-byte / 4bpp
static mapping-only
60-glyph Vietnamese production codepage
font visual style = 0.6.7.2
```

Không quay lại narrow 6x12, 12x16, pointer redirect, composite overlay hay global spacing hook.

## Font visual baseline

`0.6.7.2` = **FONT VISUAL PASS / FREEZE**.

User runtime screenshot của:

```text
Chọn tướng
```

được đánh giá perfect.

Accent rule đã khóa:
- horn của `ơ/ư` bám sát thân chữ;
- dấu sắc/huyền tách đủ xa khỏi horn;
- baseline-normalized từ 0.6.6.1;
- spacing ngang hơi rộng được chấp nhận.

## Production codepage capacity

Actual Translation Master 0.6 hiện cần:

```text
60 custom Vietnamese glyphs
64 conservative zero-hit atlas slots
4 reserve slots
```

Frozen custom set:

```text
àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ
```

## Coverage recovery

Old Alpha 0.6.1 từng có **397 patch keys** từ gameplay/front text.

`0.6.8.0` và `0.6.8.1` không cho runtime coverage như mong muốn, nên không còn là hướng hiện tại.

### 0.6.9.0

Hybrid pipeline tìm `399` patch nhưng gate sai, bắt tổng phải đúng 397.

**Build gate bug only. Do not retest.**

### 0.6.9.1

Gate tiếp theo sai logic legacy và báo mất 228 row.

**Build gate bug only. Do not retest.**

### 0.6.9.2

Exact legacy reconstruction:

```text
legacy Alpha coverage = 397 / 397
extra vi_full-only patches allowed
```

Runtime intro đã hiện Vietnamese fallback:

```text
100 NAM MENH
LUC DIA LOAN
THOI GAIA MASTER
DEN LUC!
```

=> **coverage pipeline PASS**.

Nhưng intro vẫn không dấu vì `FRONT_DEMO_ADDED_061.csv` chỉ có `vi_no_accents`.

## CURRENT — 0.6.10.0 HYBRID FULL-COVERAGE + FRONT ACCENT BATCH 1

Current repo files:

```text
tools/build_gaia_06100_hybrid_accent_b1.py
tools/00_BUILD_0.6.10.0_HYBRID_ACCENT_B1.cmd
ACCENT_UPGRADE_0.6.10.0.md
translation/FRONT_ACCENT_OVERRIDES_0.6.10.0.csv
```

Builder source snapshot is exact; readable-source SHA1:

```text
faea2fbf90d3b4038ad64d3872934c043115878a
```

Local package:

```text
GaiaMaster_0.6.10.0_HYBRID_FRONT_ACCENT_BATCH1.zip
SHA1 d43e8547f9baca4e254f96fdb7850a5c6f873e86
```

### Coverage rule

```text
legacy Alpha coverage must remain 397 / 397
extra vi_full-only rows may be added
```

Text priority:

```text
vi_full accented if it fits
-> vi_game_current fallback if it fits
-> dedicated front override/fallback
```

Runtime format/control tokens remain raw:

```text
%s %d %+3d /V /v ...
```

### Front Accent Batch 1

All 31 dedicated intro/setup rows now have compact accented overrides.

Expected intro examples:

```text
100 năm mệnh
Lực địa loạn
Thời Gaia Master
Đến lúc!
Đất ảo trời
Thế giới mất chủ
```

Expected setup examples:

```text
Tải dữ liệu VK?
Kỹ năng LV1
Nhân vật này?
Xác nhận?
```

The builder blocks if any of the 31 accented front overrides cannot fit.

## Next session

Start by reading:

```text
HANDOFF_CURRENT.md
PROBE_BUILD_INDEX.md
ACCENT_UPGRADE_0.6.10.0.md
```

Then:

1. runtime-test `0.6.10.0` intro;
2. if intro accent pass, enter a real match;
3. inspect card/menu/item/prompt text;
4. collect remaining no-accent fallback rows;
5. build **Accent Upgrade Batch 2** for gameplay content while preserving exact `397/397` legacy coverage.

## Hard rules

- never retest `0.6.5.2`;
- no 12x16 production;
- no narrow 6x12 alias production;
- no pointer redirect;
- no composite overlay;
- no global cursor/cache/spacing mutation;
- no accent retuning after 0.6.7.2 unless a real glyph regression appears;
- no 0.6.9.0 / 0.6.9.1 retest;
- keep fallback coverage until an accented replacement actually fits;
- stop immediately on freeze/global corruption.

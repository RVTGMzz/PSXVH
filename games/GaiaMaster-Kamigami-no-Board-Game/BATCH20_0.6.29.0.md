# Gaia Master 0.6.29.0 - Batch 20

## Exact-Offset Pressure Sweep

Batch 20 consumes the safer Batch 19 V2 `FIT_PRESSURE` report and targets the easiest remaining field-pressure rows first.

### Safety pivot carried forward

Batch 19 V2 disables automatic consensus promotion keyed only by the accentless `vi_game_current` fallback. This prevents ambiguous fallback collisions such as `NHAN` being interpreted as `nhận`, `nhẫn`, or `nhân` without Japanese evidence.

Still allowed:
- Japanese-keyed semantic mappings;
- Japanese-keyed consensus;
- curated STYLE fallback mappings;
- direct `vi_full` exact locks;
- exact `file + offset` compact wording.

### Batch 20 delta

```text
75 exact file+offset compact rows
source band: V2 FIT_PRESSURE only
pressure band: <= 6 bytes over field before rewrite
```

The first draft contained 84 candidates. Static validation correctly rejected 9 keys that already belonged to Batch 19 / historical exact-lock sets. Those 9 rows were removed rather than overriding proven locks.

Data file:

```text
translation/BATCH20_EXACT_OFFSET_0.6.29.0.csv
```

Representative compactions:

```text
Tiến 6 ô      -> Đi 6 ô
Tiến 6        -> Đi 6
Đổi tối đa 2  -> Đổi đến 2
Siêu tốc      -> Cực tốc
Khu %s        -> Khu%s
%sエリア%s    -> Khu%s%s
```

The sweep prefers readable Vietnamese over arbitrary abbreviation. Fragments are only shortened where the game field itself is a fragment.

### Static validator

```text
tools/validate_batch20_06290.py
.github/workflows/gaia-batch20-validation.yml
```

The validator requires every Batch 20 row to:
1. exist in the persisted 0.6.28.0 V2 `FIT_PRESSURE` report;
2. belong to the <=6-byte pressure band;
3. avoid Batch 19 and historical 0.6.14.1 exact-lock collisions;
4. preserve runtime token identity and order;
5. fit the original Japanese CP932 field byte budget;
6. use only CP932-native glyphs or the frozen Vietnamese custom codepage.

### Production locks

Unchanged:

```text
native 12x12 / 72-byte / 4bpp / LOW nibble first
static mapping-only
frozen 60-glyph Vietnamese codepage
legacy Alpha coverage gate = 397/397
```

No renderer hook, pointer redirect, alternate font size, composite overlay, or font retuning.

## Status

`0.6.29.0` is a translation-data candidate. Static validation must PASS before the sweep is promoted into a ROM build path. Runtime PASS still requires clean-ROM build plus screenshots/log evidence.

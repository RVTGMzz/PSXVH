# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-12 sau runtime test 0.6.3.2 BASELINE ONLY — STABLE PASS, nhưng target 12x16 bị mất 4 hàng đáy khi có glyph theo sau.**

## Chốt kỹ thuật hiện tại

- 0.6.2.x đã chứng minh custom Vietnamese glyph pipeline hoạt động.
- Native 12x12 bị loại cho production stacked diacritics vì quá chật.
- 0.6.3.0 12x16 = **STRUCTURAL PASS**.
- 0.6.3.1 BASELINE + 16-ROW STRIDE = **UNSAFE FAIL** vì global text corruption + freeze; không retest.
- 0.6.3.2 BASELINE ONLY = **STABLE PASS**: global text bình thường, game không treo, baseline cải thiện, trailing `Ａ` còn nguyên.

## 0.6.3.2 runtime result

Control:

```text
ＴＥＳＴ亜Ａ
```

Runtime:

- header Japanese normal;
- `ＴＥＳＴ` normal;
- target extended glyph visible và baseline tốt hơn;
- trailing `Ａ` intact;
- không có global corruption/freeze như 0.6.3.1;
- nhưng phần **đáy của extended `Ế` bị mất/cắt**.

=> Baseline hook tự nó an toàn. Regression của 0.6.3.1 gần như chắc chắn nằm ở shared cache-advance rewrite quanh `0x8003CD94`.

## New strong hypothesis — following-glyph overwrite

Known copy geometry:

```text
wide glyph source row: 6 bytes
converted/cache row:   8 bytes
native 12 rows:        96 bytes
extended 16 rows:      128 bytes
```

0.6.3.2 cho target copy 16 rows, nhưng shared cache cursor vẫn advance native 12 rows.

Therefore the following native glyph can begin **4 rows too early** and overwrite the extended target's last 4 converted/cache rows.

This matches the runtime screenshot: target top/body appears, but lower portion is lost while following `Ａ` itself remains intact.

This is still a hypothesis until isolated.

## NEXT — 0.6.3.3 EOL OVERWRITE TEST

One-variable probe:

```text
0.6.3.2: ＴＥＳＴ亜Ａ
0.6.3.3: ＴＥＳＴ亜
```

Target is intentionally the **last glyph on the line**.

No new renderer hook.
No CD94 cache-stride patch.
No code-path change.

Question:

> Does the bottom of Ế return when no following glyph can overwrite its cache footprint?

Interpretation:

- bottom returns => following-glyph cache overwrite confirmed;
- bottom still missing => clipping/copy/display issue remains inside target path itself.

## Production direction if overwrite is confirmed

Do NOT mutate the shared cache cursor globally again.

Prefer one of:

1. dedicated extended Vietnamese cache/storage region;
2. target-specific isolated cache allocation with original shared state preserved;
3. separate production extended atlas/cache path.

## Long-term after stable extended-height path

1. production-safe external/extended Vietnamese atlas/cache storage;
2. full Vietnamese glyph inventory;
3. compact runtime codepage/mapping;
4. encode `vi_full` with accents;
5. solve/repack 230 pending rows;
6. clean mixed JP/VI;
7. patch graphic menu/title text;
8. full runtime QA + reproducible build.

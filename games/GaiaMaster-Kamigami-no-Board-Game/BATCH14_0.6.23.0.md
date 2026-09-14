# Gaia Master 0.6.23.0 — Batch 14

## Property / Economy / Card sweep

Batch 14 tập trung vào các menu giữa trận và fragment kinh tế/tài sản còn khô hoặc còn Nhật:

- bán / thế chấp / giá / ngân quỹ
- chọn tiệm / lãnh địa / gia sản
- tấn công lãnh địa / thần tượng / chuộc tài sản
- fragment mô tả hiệu ứng
- card-help lộ phí x2/x3 và +/- %
- các literal động như `土地`, `物件`, `価格`, `資金`, `エリア名`

Current scale:

```text
story/front mappings  = 19
Japanese semantic map = 397
fantasy fallback map  = 327
dynamic literals      = 113
```

Batch 14 delta:

```text
Japanese semantic map delta = 50
new semantic keys           = 38
semantic re-edits           = 1
fantasy fallback delta      = 46
dynamic literal delta       = 16
```

Translation policy remains Japanese-first, byte-fit gated and token-safe. Preserve `%s`, `%d`, `%4d`, `%+3d`.

Tone remains readable medieval fantasy: prefer `lãnh địa`, `lộ phí`, `ngân quỹ`, `thần tượng`, `tỉ thí`, but keep technical menus clear.

Production locks remain unchanged: native 12x12 / 72-byte / 4bpp, static mapping-only, legacy coverage gate 397/397.

`0.6.23.0` is a candidate pending clean-ROM build and runtime QA.

# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-14**

## Source-of-truth

Production vẫn khóa vào:

```text
native 12x12 / 72-byte / 4bpp
static mapping-only
60-glyph Vietnamese production codepage
legacy Alpha coverage gate = 397 / 397
```

`0.6.7.2` vẫn là visual baseline. Không quay lại narrow 6x12, 12x16, pointer redirect, composite overlay hay global spacing hook.

## Runtime mới nhất

`0.6.11.0` đã được user test và được phân loại:

```text
PARTIAL PASS / CONTENT QA FAIL
```

Ảnh runtime chứng minh accented pipeline hoạt động, nhưng phát hiện:

1. hai vị trí `=` cũ trong front fallback vẫn hiện thành glyph Nhật/rác;
2. lowercase `ă` trong `năng` có breve sai hình;
3. vẫn còn fallback không dấu và tên Nhật động, ví dụ `LUOT ジガー`.

## CURRENT — 0.6.12.0 LARGE GAMEPLAY TRANSLATION BATCH 3

Batch này cố tình làm lớn để giảm số vòng build-test nhỏ.

### Giữ nguyên

```text
exact 397/397 legacy gate
BDP/checksum writer
runtime token handling
60-glyph codepage
12x12 mapping-only architecture
```

### Sửa lỗi runtime

```text
NGUOI=CO      -> NGUOI CO
THEGIOI=BANCO -> THEGIOI BANCO
```

và sau inner build chỉ redraw hai hàng accent trên glyph lowercase `ă` thành breve dạng cup/smile. Không đổi mapping/body/slot hay font khác.

### Dịch thêm lớn

`BATCH3_FALLBACK_ACCENT_MAP_0.6.12.0.csv` hiện có **278 curated compact accent mappings**.

Builder còn globalize toàn bộ Batch 2 mapping: mọi Translation Master row có cùng fallback cũ đều được thử promote sang bản có dấu khi vẫn vừa field gốc.

Nội dung mở rộng phủ setup, tavern, gameplay, thuế/đất/tuyến đường, card, item, weapon, event, menu, prompt, building/status/movement/battle strings.

Candidate quá dài vẫn giữ fallback cũ để không làm mất coverage.

### Dynamic / repeated Japanese

Builder scan standalone/null-delimited copies trong CLEAN `SLPS_020.75` và `PRGPACK.BDP`, rồi inject temporary translation rows cho duplicate chưa có offset trong master.

Compact runtime names gồm:

```text
トロル通り -> Troll
ジガー -> Jig
ダンテ -> Dan
孫悟空 -> Ngộ
ハヤテ -> Hay
ヤスツナ -> Yasu
ガラハッド -> Galah
ティアラ -> Tiar
ゴライアス -> Golia
メグメグ -> Megu
アガート -> Agat
シンバッド -> Sinba
```

## Files

```text
ACCENT_UPGRADE_0.6.12.0.md
tools/build_gaia_06120_big_translation_b3.py
tools/00_BUILD_0.6.12.0_BIG_TRANSLATION_B3.cmd
translation/BATCH3_FALLBACK_ACCENT_MAP_0.6.12.0.csv
translation/DYNAMIC_LITERAL_OVERRIDES_0.6.12.0.csv
```

## State

```text
SOURCE READY
PYTHON SYNTAX PASS
ROM BUILD PENDING
RUNTIME PENDING
```

Clean BIN không mounted trong phiên ChatGPT nên cần build trên máy user.

## Next runtime test

Test một lượt rộng: intro -> setup -> vài lượt đầu -> card/item/event/menu -> đất/thuế/tuyến đường/battle. Chụp lại mọi Japanese còn sót, fallback không dấu, dấu sai, clipping hoặc freeze.

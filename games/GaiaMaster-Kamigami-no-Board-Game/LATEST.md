# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-14**

## CURRENT — 0.6.44.0 BATCH 34

Trọng tâm: **Curated Compact Sweep + Whole-Game Japanese Discovery**.

## Tiến độ mới sau 0.6.40

Batch31 kiểm kê lại toàn bộ fallback còn sót sau tập exact 295 field:

```text
Translation Master rows      = 596
Protected B29 exact keys     = 295
Residual fallback rows       = 265
Unique residual clusters     = 242
```

Phần lớn residual không phải chưa dịch nghĩa mà là bản `vi_full` quá dài so với field gốc.

## Batch32 curated compact

25 Japanese semantic keys được rút gọn thủ công thành tiếng Việt vừa field, không suy nghĩa từ fallback ASCII.

```text
New exact rows exported = 47
Exact-full-field rows   = 25
Errors                  = 0
RESULT                  = STATIC CURATED PASS
```

Ví dụ:

```text
武器カードを / 武器カードは -> Thẻ VK
終了ターン                 -> Hết
%sのラッキー！！           -> %s hên!
なにか捨ててね             -> Bỏ bớt
騎士団                     -> Kỵ
お店破壊                   -> Phá!
%dゼニーはらってね         -> Trả %dZ
いやしのうた               -> Hồi HP
指定武器カード１枚を盗む   -> Cướp thẻ VK
あいての命中率を落とす     -> Giảm CX
ＨＰを６０回復する         -> Hồi 60HP
死亡するとＨＰ１００で復活 -> Hồi sinh100HP
```

Một chữ `ễ` không có trong frozen codepage đã bị CI bắt; wording được sửa thành `Hay CM`, không mở rộng font.

## Batch33 exact merge

```text
B29 new rows             = 282
B29 final rows           = 295
B32 curated rows         = 47
Merged new exact targets = 329
Merged final verify set  = 342
Errors                   = 0
RESULT                   = STATIC MERGE PASS
```

## Batch34 production builder

Python builder:

`tools/build_gaia_06440_batch34_curated_compact.py`

Builder/stage selftest đều PASS. Production chain vẫn tái dùng 0.6.14 -> 0.6.10 đã chứng minh, không tạo encoder thứ hai.

Clean-ROM gate:

```text
SHA1 f4d5298583c90d89c4b7e51d2dde160ee07f2aec
```

Actual build bắt buộc đạt:

```text
329 exact targets staged
342/342 exact fields byte verification
397/397 legacy Alpha gate
source restore PASS
```

## EASY package hiện tại

`GaiaMaster_0.6.44.0_Batch34_EASY.zip`

Ngoài cùng chỉ cần:

```text
00_VIET_HOA_GAME.cmd
01_QUET_TOAN_BO_GAME.cmd
02_DOC_TRUOC.txt
```

Build launcher tự tìm đúng CLEAN BIN bằng SHA1.

## Whole-game scanner

Read-only scanner vẫn là bước quan trọng nhất để mở rộng khỏi 596-row master:

```text
01_QUET_TOAN_BO_GAME.cmd
```

Output cần gửi lại:

```text
GaiaMaster_0.6.38.0_FULL_JAPANESE_SCAN.csv
GaiaMaster_0.6.38.0_FULL_JAPANESE_SCAN_REPORT.txt
```

Nó sẽ dùng để bắt story/tutorial/help/Memory Card text chưa từng xuất hiện trong Translation Master.

## Production architecture không đổi

```text
native 12x12 / 72-byte / 4bpp / LOW nibble first
static mapping-only
frozen 60-glyph Vietnamese codepage
legacy Alpha coverage gate = 397/397
```

Không renderer hook, pointer redirect, 12x16, 6x12, composite overlay hoặc font retune nếu chưa có runtime evidence mới.

## Status

**0.6.44.0 = BUILD-READY / STATIC PASS.**

Chưa phải Runtime PASS.

## Tiếp theo

1. Build 0.6.44 từ CLEAN BIN.
2. Kiểm report có **342/342** byte verification và **397/397** legacy gate.
3. Boot đúng output 0.6.44.
4. Chạy whole-game scanner.
5. Gửi scanner CSV + REPORT để mở batch story/tutorial/help theo exact offset.

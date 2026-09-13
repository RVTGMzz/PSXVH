# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-13**

## Chốt hiện tại

Production direction vẫn là:

> **giữ renderer/font geometry native 12x12 / 72-byte / 4bpp, dùng static mapping + native atlas data; không pointer redirect.**

`0.6.6.0` đã render end-to-end câu Việt thật `Chọn tướng`.
`0.6.6.1 BASELINE-NORMALIZED` đã runtime **PASS** về glyph + vertical baseline.

Vấn đề còn lại là **horizontal spacing**.

## Spacing reverse — gate đã đóng

`GaiaMaster_FontSpacingScanner_01.txt` chứng minh:

```text
cache record = 16 bytes
record+6     = horizontal advance
```

Cache miss:

```text
copy_return == 8
  ? advance = state+0x3E
  : advance = state+0x40 + 1
```

Character Select có:

```text
state+0x3C tracking = 0
```

Gaia có native narrow metric:

```text
state+0x3E = 8
```

Nhưng custom/full-width CP932 path hiện tại thuộc wide-copy class, nên `Chọn tướng` vẫn chiếm khoảng full-width Nhật.

## Cache-key finding

Cache không key theo character code.
Nó key theo source glyph từ `0x8003C210`, tương đương:

```text
cache_key = glyph_source_pointer >> 1
```

Vì vậy không được map mã Việt mới về cùng native Latin slot rồi chỉ đổi advance, vì cache record có thể alias với full-width Latin/Japanese.

## Current architecture — private native bank

First proof cần 9 private display units:

```text
C h ọ n SPACE t ư ớ g
```

Mỗi unit dùng:

```text
reserved zero-hit CP932 code
 -> private native 12x12 atlas slot
 -> unique source/cache key
 -> normal 12x12 bitmap copy
 -> cached advance 8px only for private source range
```

Plain Latin và space cũng được duplicate vào private slots. Không reuse native Latin slots.

Không ép narrow-copy geometry vì 12px bitmap có thể bị clip.

## CURRENT — READ-ONLY FONT PRIVATE BANK SCANNER 0.1

Package local:

```text
GaiaMaster_FontPrivateBankScanner_0.1.zip
```

Expected report:

```text
GaiaMaster_FontPrivateBankScanner_01.txt
```

Scanner một lượt để tìm:

1. block 9 atlas slot liên tiếp với zero static text hits;
2. >=9 custom CP932 codes zero-hit;
3. source-pointer/cache-key range của private bank;
4. NOP/zero runs làm **code-cave candidate**, chưa tự động coi là safe;
5. dump patch neighborhood quanh `0x8003CC98`.

Detailed note:

```text
FONT_PRIVATE_BANK_SCANNER_0.1.md
```

## Runtime gate

**Chưa có 0.6.6.2 runtime build.**

Sau khi đọc report private-bank scanner:

- manual reverse candidate cave;
- nếu cave + private bank đều PASS, build đúng **một** Character Select proof `Chọn tướng`;
- patch chỉ local cached advance cho private source range;
- Japanese/native path giữ nguyên 100%.

## Hard rules

- native 12x12 / 72-byte / 4bpp;
- no production 12x16;
- no composite overlay;
- no 0.6.5.2 pointer redirect;
- no global cursor/spacing patch;
- no reuse native Latin slots for private spacing proof;
- no unsafe 0.6.3.x retests;
- stop immediately on freeze/global corruption.

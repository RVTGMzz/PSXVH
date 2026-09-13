# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-13**

## Runtime baseline

`0.6.6.0` đã render end-to-end câu Việt thật:

```text
Chọn tướng
```

`0.6.6.1 BASELINE-NORMALIZED` đã runtime **PASS** về glyph + vertical baseline.

Vấn đề còn lại duy nhất đang xử lý là **horizontal spacing**.

## Spacing facts đã chứng minh

```text
cache record+6 = horizontal advance
copy_return == 8 ? advance = state+0x3E : state+0x40+1
state+0x3C tracking = 0
```

Metric setter chứng minh dimension `11` có native narrow advance:

```text
state+0x3E = 8
```

Current custom CP932 path thuộc Japanese full-width class, nên vẫn rộng khoảng 12px.

## FontPrivateBankScanner 0.1 — PASS phần data

Report mới nhất tìm được:

```text
private atlas bank = slots 432..440
9/9 all-unmapped
9/9 zero static text hits
32 zero-hit CP932 codes
```

Tuy nhiên zero/NOP run duy nhất:

```text
SLPS+0x5C0E0..<0x5C2B8
```

**không phải code cave an toàn**.

Native narrow font bank bắt đầu ở:

```text
RAM  0x8006BAAC
SLPS 0x5C2AC
```

Nên zero-run trên overlap **12 byte** vào font resource. Candidate này bị **REJECT / NEVER USE AS CAVE**.

## Pivot mới — native narrow bank, không hook

Gaia có sẵn một đường 1-byte narrow:

```text
halfwidth remap table = 0x8007E01C
narrow glyph source   = 0x8006BAAC
main 12x12 atlas      = 0x8006BCEC
```

Với dimension 11:

```text
12 rows
each narrow glyph = 3 source bytes / row
2 glyphs interleaved in a 6-byte row
pair block = 72 bytes
native narrow copy returns 8
native horizontal advance = 8px
```

Khoảng `0x8006BAAC..<0x8006BCEC` dài đúng 576 byte, khớp 8 packed pairs / 15 narrow source indices.

Nếu tìm được 9 source index không đụng text gốc, ta có thể render:

```text
C h ọ n SPACE t ư ớ g
```

bằng pipeline hoàn toàn native:

```text
private 1-byte code
 -> existing halfwidth table
 -> selected native narrow source
 -> native narrow copy
 -> native 8px advance
```

**Không code cave. Không cursor hook. Không record+6 hook. Không pointer redirect.**

## CURRENT — READ-ONLY FontNarrowBankScanner 0.1

Files repo:

```text
tools/font_narrow_bank_scanner_0.1.py
tools/00_RUN_FONT_NARROW_BANK_SCANNER_0.1.cmd
FONT_NARROW_BANK_SCANNER_0.1.md
```

Expected report:

```text
GaiaMaster_FontNarrowBankScanner_01.txt
```

Scanner kiểm tra:

1. 15 native narrow source indices;
2. ASCII + halfwidth aliases dùng chung từng source;
3. strict null-terminated text hits trong PRGPACK + SLPS;
4. state-dependent halfwidth table flags;
5. có >=9 source sạch + 9 halfwidth code hợp lệ hay không.

## Gate tiếp theo

Nếu scanner **STATIC PASS**:

- cross-check 9 alias/source với Translation Master;
- thiết kế font Việt compact ~6px;
- sau đó mới build **ONE data-only Character Select proof**.

Nếu scanner **STATIC NEGATIVE**:

- không test emulator;
- giữ `0.6.6.1` làm baseline;
- tiếp tục reverse cache-advance offline.

## Hard rules

- native font resource only;
- no production 12x16;
- no composite overlay;
- no `0.6.5.2` pointer redirect;
- no global cursor/spacing patch;
- never use `SLPS+0x5C0E0..<0x5C2B8` as a cave;
- no runtime `0.6.6.2` before narrow-bank gate + Translation Master cross-check;
- stop immediately on freeze/global corruption.

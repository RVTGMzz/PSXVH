# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** production is locked to **native 12x12 / 72-byte / 4bpp / static mapping-only**. `0.6.7.2` is the current **FONT VISUAL PASS** and freezes the accepted Vietnamese accent composition. The active production candidate is **0.6.8.0 PROD60 SAFE-FIT vi_full BATCH 1**, which keeps the 0.6.7.2 font/codepage and applies every current `vi_full` row that can safely replace its Japanese source in-place without relocation.

## Baselines

- Game: `GaiaMaster - Kamigami no Board Game (Japan).bin`
- serial: `SLPS-02075`
- clean BIN SHA1: `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- clean SLPS SHA1: `1dfeb6b7cfda59c108dde2dc0b8abda9a40e6ae5`
- clean PRGPACK SHA1: `a9b195b8ae5d8cad7f4f755daa08337d4671632c`
- repo: `ronvotri/Viet-Hoa-PS1`
- branch: `gaia-character-select-font-atlas-reverse-01`

## Proven architecture

```text
runtime GP     = 0x80085F28
atlas global   = gp+0x518
mapping global = gp+0x51C
main atlas RAM = 0x8006BCEC
mapping RAM    = 0x8007AECC
main atlas file= SLPS+0x5C4EC
mapping file   = SLPS+0x6B6CC
860 glyphs
native main font = 12x12 / 72-byte / 4bpp / LOW nibble first
```

Pipeline:

```text
code & 0x7FFF
 -> mapping[index]
 -> glyph index
 -> glyph_index * 72
 -> atlas base + offset
```

Known mapping facts:

```text
0x8273 Ｔ -> glyph 481
0x8264 Ｅ -> glyph 466
0x8272 Ｓ -> glyph 480
0x889F 亜 -> glyph 0
```

## Runtime history / locks

- `0.6.2.13`: static custom-atlas replacement PASS.
- `0.6.3.x`: 12x16 caused corruption/freezes. Historical only.
- `0.6.4.x`: composite overlay unreliable. Stop.
- `0.6.5.2`: **UNSAFE FAIL / NEVER RETEST**, pointer redirect caused black screen/FPS0/hard freeze.
- `0.6.5.3`: mapping-only structural PASS.
- `0.6.5.4`: native-base copy PASS.
- `0.6.5.5`: compact accent style PASS enough for production.
- `0.6.6.0`: real text `Chọn tướng` rendered end-to-end.
- `0.6.6.1`: baseline-normalized real text PASS / previous LAST GOOD.
- `0.6.6.2` + `0.6.6.2b`: safety-gate false blocks, no runtime.
- `0.6.6.2c`: native narrow 6x12 one-byte alias runtime FAIL, garbled glyphs. Retired.
- `0.6.7.0`: full 60-glyph production codepage boots and renders correctly; accent polish remained.
- `0.6.7.1`: horn on `ơ/ư` moved closer to the base successfully; acute/grave became too close to horn.
- `0.6.7.2`: **FONT VISUAL PASS / FREEZE THIS STYLE.** User runtime screenshot judged `Chọn tướng` perfect. Horn hugs the base; acute/grave are separated cleanly. Do not retune unless a new production glyph regression is demonstrated.

Wide horizontal spacing is accepted visual polish and is not an architecture blocker.

## Capacity result

Worst-case theoretical 134-glyph full Vietnamese set does not fit conservative clean capacity:

```text
837 zero-static-hit custom codes
64 zero-static-hit atlas slots
34 completely unmapped zero-hit slots
30 mapped-but-static-unused zero-hit slots
```

Actual current Translation Master 0.6 corpus:

```text
596 rows total
393 rows with non-empty vi_full
125 unique characters in vi_full
60 custom Vietnamese glyphs
56 lowercase + 4 uppercase
```

Result: **PASS with 4 reserve slots**.

Exact current custom set:

```text
àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ
```

No other non-ASCII/non-Vietnamese policy characters are currently required.

## Frozen production slot allocation

```text
# 34 completely unmapped zero-hit
18 33 58 160 182 261 301 371 392
420 421 422 423 424 425 426 427 428 429 430 431
432 433 434 435 436 437 438 439 440
517 695 704 713

# 26 mapped-but-static-unused zero-hit
38 94 108 109 129 130 150 208 295 326 335 345 372
385 394 398 400 403 702 715 729 745 750 754 757 790

# reserve
794 807 821 824
```

Custom codes are selected deterministically from zero-static-hit CP932 codes in the proven `>=0x889F` region.

## 0.6.7.2 accepted accent rule

For `ơ/ư` family:
- horn stays attached close to the body;
- acute/grave are shifted farther away so they do not merge with the horn;
- baseline-normalized body behavior from 0.6.6.1 is retained;
- this style is now frozen as the production font baseline.

## CURRENT — 0.6.8.0 PROD60 SAFE-FIT vi_full BATCH 1

Local package:

```text
GaiaMaster_0.6.8.0_PRODUCTION_SAFE_FIT_BATCH1.zip
```

Immediate sanity anchors remain:

```text
PRGPACK+0xBFBEC -> Đã ổn?
PRGPACK+0xBFD2C -> Chọn tướng
PRGPACK+0xBFE4C -> Nhấn O
```

After installing the frozen 60-glyph codepage, the builder loads Translation Master 0.6 parts 01..06 and attempts every non-empty `vi_full` row.

A row is applied only when all are true:
1. file is `PRGPACK.BDP` or `SLPS_020.75`;
2. Japanese source bytes match CLEAN data exactly at the CSV offset;
3. source string is NUL-terminated;
4. row has no printf/control token requiring raw ASCII semantics (`%s`, `%d`, `%4d`, `%+3d`, `/V`, `/v` etc.);
5. encoded Vietnamese byte length is <= original Japanese byte length.

Otherwise the row is skipped and logged. The builder never expands a file or overwrites the following string.

For PRGPACK rows, every touched nested BDP checksum plus the top-level checksum is rebuilt. Raw Mode2/Form1 CD EDC/ECC is rebuilt for all changed sectors.

### Runtime expectation

1. the three anchor strings should look exactly as good as 0.6.7.2;
2. user can then play normally and encounter many real `vi_full` translations;
3. format-token rows intentionally remain Japanese in Batch 1;
4. overlength rows intentionally remain Japanese in Batch 1;
5. report gives exact counts and full APPLIED/SKIPPED lists.

### Next after 0.6.8.0 PASS

- freeze the exact `CODEPAGE60` manifest;
- build **Batch 2 token-aware encoder** preserving raw formatter/control sequences while encoding display text around them;
- after token rows are solved, design relocation/length-expansion only for remaining overlength rows;
- continue filling currently empty `vi_full` rows without changing the font architecture unless the custom-character inventory exceeds the 4 reserve slots.

## Hard do-not-repeat

- no Krom path;
- no production 12x16;
- no failed 0.6.3.x retests;
- no composite overlay loop;
- no 0.6.5.2 pointer redirect;
- no 0.6.6.2 / 2b retests;
- no 0.6.6.2c retest;
- no one-byte narrow alias production path;
- no global cursor/cache/spacing mutation;
- no spacing-driven architecture rewrite;
- no accent retuning after 0.6.7.2 unless a real production regression proves it necessary;
- do not patch printf/control-token rows with the plain display encoder;
- stop immediately on freeze/global corruption.

## Testing preference

- minimize emulator tests;
- maximize information per test;
- never repeat known failed/already-proven builds;
- read reports immediately when uploaded.

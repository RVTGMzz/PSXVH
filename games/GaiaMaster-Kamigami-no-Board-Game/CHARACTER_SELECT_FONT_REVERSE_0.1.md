# Gaia Master — Character Select custom glyph cache/font atlas reverse 0.1

## Mục tiêu

Visible probe chuẩn dùng full-width CP932:

```text
ＴＥＳＴ亜
```

Mục tiêu cuối:

```text
ＴＥＳＴẾ
```

Không quay lại hook `Krom2RawAdd`: direct caller #1, direct caller #2 và global safe wrapper đều đã không chạm glyph Character Select.

## Source-of-truth

- clean BIN SHA1: `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- Alpha 0.6.1 FRONT SHA1: `54d2fb026bc3b71c79861e723caffb4114caa34c`
- `SLPS_020.75` SHA1: `1dfeb6b7cfda59c108dde2dc0b8abda9a40e6ae5`
- `PRGPACK.BDP` SHA1: `a9b195b8ae5d8cad7f4f755daa08337d4671632c`
- Character Select text: `PRGPACK + 0xBFD2C`
- owner nested BDP: entry 29
- local offset: `+0x580`

## Stage 2 breakthrough — custom atlas path

Renderer function around `0x8003C210` có hai nguồn glyph.

Character Select dùng custom mapping/atlas branch quanh:

```text
0x8003C4DC sll  v0,v0,1
0x8003C4E0 lw   v1,0x51C(gp)   # mapping base
0x8003C4E4 lw   a0,0x518(gp)   # atlas base
0x8003C4E8 addu v0,v0,v1
0x8003C4EC lhu  v1,0(v0)       # glyph index
0x8003C4F8 sll  v0,v1,3
0x8003C4FC addu v0,v0,v1
0x8003C500 sll  a1,v0,3        # glyph_index * 72
0x8003C504 addu a0,a0,a1       # final glyph pointer
```

Default pointers:

```text
atlas RAM   = 0x8006BCEC
mapping RAM = 0x8007AECC
atlas file  = SLPS + 0x5C4EC
mapping file= SLPS + 0x6B6CC
```

Mapping đã xác nhận:

```text
0x8273 Ｔ -> glyph 481
0x8264 Ｅ -> glyph 466
0x8272 Ｓ -> glyph 480
0x889F 亜 -> glyph 0
```

## Atlas format — final corrected finding

```text
860 glyphs
72 bytes/glyph
12x12 pixels
4bpp
LOW nibble first
```

`Ｅ` full-width là glyph 466 và được dùng làm style/palette reference.

## Probe timeline — native 12x12

### 0.6.2.7
Thay static glyph #0, nhưng control dùng ASCII `TEST亜` -> nhiều ký tự thành `É`. Điều này vẫn chứng minh atlas injection tác động runtime, nhưng ASCII 1-byte không phải control hợp lệ.

### 0.6.2.10
Hook sớm ở mapping branch làm nhiều/all text collapse thành một glyph. Strategy bị loại.

### 0.6.2.11
Post-lookup hook giữ text thường bình thường và chỉ đổi ký tự cuối:

```text
ＴＥＳＴ?
```

=> target isolation PASS, nhưng custom cave glyph pointer không phải strategy tối ưu.

### 0.6.2.12
Đổi nibble order nhưng runtime vẫn `ＴＥＳＴ?` -> loại hướng tiếp tục đoán cave glyph packing.

### 0.6.2.13 — STATIC SLOT / NO HOOK — PASS

Bỏ hoàn toàn renderer hook/code cave/pointer override.

Control:

```text
ＴＥＳＴ亜
```

Thay trực tiếp static atlas glyph #0 (`亜`) bằng glyph `Ế` dựng từ full-width `Ｅ` gốc.

Runtime user result:

- text khác bình thường;
- bốn chữ `ＴＥＳＴ` đúng;
- glyph cuối hiện gần như `Ế`;
- màu/style thân glyph gần khớp font gốc.

=> static custom atlas path đã PASS runtime.

### 0.6.2.14..0.6.2.20 — production 12x12 rejected

Nhiều strategy đã thử:

- compact body;
- full-height body;
- AA accent;
- clean accent;
- six-variant grid;
- refined sample 2.

Kết luận production:

> **12x12 không đủ headroom cho stacked Vietnamese diacritics nếu giữ nguyên cỡ thân chữ native.**

Đặc biệt xấu với các ký tự như:

```text
Ế Ể Ẳ Ỗ Ử Ấ Ố ...
```

Không quay lại vòng lặp chỉnh từng pixel cho production 12x12.

## Extended-height reverse — 0.6.3.x

### Renderer / metadata

Character renderer:

```text
0x8003C210
```

Glyph metadata struct relevant fields:

```text
+0  glyph width metric
+2  source/copy height metric
+4  source glyph pointer
+8  custom-atlas flag
```

Descriptor relevant bytes:

```text
+4/+5 = texture UV
+6    = visible width
+7    = visible height
```

### Wide-glyph unpack/copy

Function:

```text
0x8003C67C
```

Per source row:

```text
6 source bytes -> 8 converted/cache bytes
```

Therefore:

```text
12x12 source = 72 bytes
12 rows converted = 96 bytes

12x16 source = 96 bytes
16 rows converted = 128 bytes
```

This distinction between source footprint and converted/cache footprint is critical.

## 0.6.3.0 EXTENDED HEIGHT 12x16 — STRUCTURAL PASS

Initially marked FAIL because the target looked malformed. Pixel-level review later corrected that classification.

Runtime actually shows:

- extra headroom/accent pixels;
- taller target footprint;
- full E body shifted downward relative to `TEST`.

That downward shift is exactly what was expected because baseline correction was intentionally absent.

=> **16-row source/copy/display path is structurally proven.**

Do not retest 0.6.3.0.

## 0.6.3.1 BASELINE + 16-ROW STRIDE — UNSAFE FAIL

Added:

1. target Y `-4 px`;
2. target-specific rewrite of shared converted-cache/VRAM advance around `0x8003CD94..0x8003CDB4`.

Runtime:

- unrelated Japanese text corrupts/repeats;
- Character Select corrupts;
- later screen garbles;
- game freezes.

=> **UNSAFE FAIL**.

Strongest suspect: shared cache/VRAM allocator state was desynchronized.

Do not retest and do not reapply the naive shared `CD94` stride patch.

## 0.6.3.2 BASELINE ONLY — STABLE PASS WITH LOWER-ROW LOSS

Control:

```text
ＴＥＳＴ亜Ａ
```

Changes:

- keep 16-row source/copy/display path;
- apply only target `Y -= 4 px`;
- leave shared cache pointer + VRAM cursor native.

Runtime:

- Japanese header normal;
- `ＴＥＳＴ` normal;
- baseline improved;
- trailing `Ａ` intact;
- no global corruption/freeze;
- lower part of target `Ế` is missing/cut.

=> baseline correction is safe.
=> 0.6.3.1 regression is tied to shared cache-stride mutation, not baseline correction.

Dedicated note:

```text
FONT_ISOLATION_0.6.3.2_STABLE_PASS.md
```

## Current hypothesis — following-glyph overwrite

The target writes:

```text
16 rows * 8 converted bytes = 128 bytes
```

but native shared cursor still advances:

```text
12 rows * 8 converted bytes = 96 bytes
```

So the following glyph may begin:

```text
32 bytes / 4 rows too early
```

and overwrite the bottom four rows of the extended target.

The 0.6.3.2 screenshot fits this pattern, but it is not yet proven.

## 0.6.3.3 EOL OVERWRITE TEST — current probe

Change exactly one variable:

```text
0.6.3.2: ＴＥＳＴ亜Ａ
0.6.3.3: ＴＥＳＴ亜
```

Target is last glyph on the line.

No new hook.
No cache-stride patch.
No changed copy/display logic.

Question:

> Does the target bottom return when no following glyph can overwrite it?

Interpretation:

- bottom returns => following-glyph overwrite confirmed;
- bottom still missing => target copy/upload/display/clipping still truncates rows internally.

Dedicated note:

```text
FONT_ISOLATION_0.6.3.3_EOL_OVERWRITE_TEST.md
```

## Current production direction

If 0.6.3.3 confirms overwrite, do **not** mutate the shared global font-cache cursor again.

Prefer:

1. dedicated/isolated converted-cache region for Vietnamese extended glyphs;
2. target-specific RAM/VRAM destination while preserving native shared allocator state;
3. separate production extended atlas/cache path.

Then scale to full Vietnamese glyph inventory and codepage.

## Reference files

```text
HANDOFF_CURRENT.md
LATEST.md
PROBE_BUILD_INDEX.md
PS1_LOCALIZATION_REUSABLE_LESSONS.md
FONT_ISOLATION_0.6.3.1_UNSAFE_FAIL.md
FONT_ISOLATION_0.6.3.2_STABLE_PASS.md
FONT_ISOLATION_0.6.3.3_EOL_OVERWRITE_TEST.md
```

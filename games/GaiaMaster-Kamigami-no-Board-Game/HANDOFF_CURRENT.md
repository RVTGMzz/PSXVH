# HANDOFF — Gaia Master PS1 Việt hóa

> **Current source-of-truth:** `0.6.6.1 BASELINE-NORMALIZED` là LAST GOOD runtime build. Production direction bị khóa về **native 12x12 / 72-byte / static mapping-only**. `0.6.6.2c` narrow 6x12 runtime FAIL và đã RETIRED. `Production Capacity Scanner 0.1` đã chạy trên CLEAN BIN: full 134-glyph Vietnamese repertoire **không fit** với conservative zero-hit atlas capacity hiện tại (837 safe codes nhưng chỉ 64 allocatable zero-hit atlas slots, trong đó 34 completely unmapped). Current step là **vi_full Inventory 0.1**: inventory chính xác các ký tự tiếng Việt đang thực sự xuất hiện trong Translation Master 0.6 parts 01..06, rồi freeze codepage nhỏ hơn nếu <=64.

## Baseline fingerprints

- Game: `GaiaMaster - Kamigami no Board Game (Japan).bin`
- serial: `SLPS-02075`
- clean BIN SHA1: `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- clean SLPS SHA1: `1dfeb6b7cfda59c108dde2dc0b8abda9a40e6ae5`
- clean PRGPACK SHA1: `a9b195b8ae5d8cad7f4f755daa08337d4671632c`
- repo: `ronvotri/Viet-Hoa-PS1`
- branch: `gaia-character-select-font-atlas-reverse-01`

## Proven production font facts

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

Renderer mapping path:

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

Character Select proof field:

```text
PRGPACK.BDP + 0xBFD2C
owner nested BDP = entry 29
field = 24 bytes
```

## Runtime locks

- `0.6.2.13`: static custom-atlas replacement PASS.
- `0.6.3.x`: 12x16 caused shared-state corruption/freezes. Historical only.
- `0.6.4.x`: composite overlay placement unreliable. Stop.
- `0.6.5.2`: **UNSAFE FAIL / NEVER RETEST**, runtime pointer redirect caused black screen/FPS0/hard freeze.
- `0.6.5.3`: mapping-only structural PASS.
- `0.6.5.4`: native base copy PASS.
- `0.6.5.5`: compact accented glyph style PASS enough for production pivot.
- `0.6.6.0`: real Vietnamese text `Chọn tướng` rendered end-to-end.
- `0.6.6.1`: baseline-normalized real text **PASS / LAST GOOD**.
- `0.6.6.2`: safety-gate false block, no runtime build.
- `0.6.6.2b`: stricter safety-gate false block, no runtime build.
- `0.6.6.2c`: native narrow 6x12 one-byte alias proof **RUNTIME FAIL**; garbled glyphs. RETIRE narrow one-byte production path.

## 0.6.6.1 LAST GOOD

Proven:
- main 12x12 atlas + static mapping works for Vietnamese;
- plain Latin can reuse native full-width Gaia glyphs;
- `ọ`, `ư`, `ớ` render acceptably;
- vertical baseline is production-usable;
- stable boot/UI;
- no hook;
- no pointer redirect.

Remaining wide horizontal spacing is classified as **visual polish only**. Do not rewrite architecture to chase spacing.

## Production Capacity Scanner 0.1 — RESULT

User ran the READ-ONLY scanner on the verified CLEAN BIN.

Result:

```text
Target custom glyphs: 134
Zero-hit custom codes: 837
Zero-hit atlas slots : 64
Unmapped zero slots  : 34
Verdict              : FAIL
```

Detailed breakdown:

```text
zero-hit + completely unmapped slots        = 34
zero-hit + mapped-but-static-unused slots   = 30
total conservative allocatable zero-hit     = 64
needed for full Vietnamese precomposed set  = 134
```

Interpretation:
- custom code space is NOT the bottleneck;
- atlas capacity is the bottleneck under the conservative rule of preserving all currently referenced Japanese glyphs;
- scanner worked correctly; this is a capacity FAIL, not a build crash;
- no runtime BIN/CUE was created by the scanner.

Do not rerun the 134-glyph worst-case scanner unless atlas-reclaim policy changes.

## CURRENT — vi_full Inventory 0.1

Files:

```text
tools/vifull_inventory_0.1.py
tools/00_RUN_VIFULL_INVENTORY_0.1.cmd
```

Purpose:
- fetch/read `TRANSLATION_MASTER_0.6_part01..part06.csv`;
- inventory only non-empty `vi_full` rows;
- compute exact unique Vietnamese precomposed characters currently needed;
- split lowercase/uppercase;
- normalize Unicode punctuation that can map back to ASCII;
- compare current real-corpus custom glyph need against known clean capacity = 64 slots.

Expected report:

```text
GaiaMaster_ViFullInventory_01.txt
```

### Next if vi_full inventory PASS (<=64)

1. freeze deterministic `Unicode -> custom CP932 code -> atlas slot` table for exactly the current corpus;
2. reuse 0.6.6.1 baseline-preserving 12x12 glyph generator;
3. build a multi-string production proof from real `vi_full` rows;
4. keep current full-width spacing until translation pipeline is stable at scale.

### Next if vi_full inventory FAIL (>64)

Do NOT revive narrow/12x16/composite. Instead design an explicit atlas-reclaim policy:
- identify Japanese glyph slots whose remaining occurrences are all in rows already translated;
- patch those rows and reclaim only those now-dead slots;
- expand codepage incrementally with provenance/reporting.

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
- no code cave at the narrow-font boundary;
- no spacing-driven architecture rewrite;
- no assumption full 134-glyph Vietnamese must fit before shipping a useful production codepage;
- stop immediately on freeze/global corruption.

## User testing preference

- minimize emulator tests;
- maximize information per test;
- READ-ONLY scanners before risky runtime builds;
- never repeat known failed or already-proven builds.

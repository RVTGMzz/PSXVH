# Prompt mở phiên chat mới — Gaia Master

Copy nguyên câu dưới đây vào phiên mới:

> Tiếp tục Gaia Master từ `games/GaiaMaster-Kamigami-no-Board-Game/HANDOFF_CURRENT.md` trên branch `gaia-character-select-font-atlas-reverse-01` của repo `ronvotri/Viet-Hoa-PS1`. Đọc thêm `LATEST.md` và `translation/source_layer/checkpoint_B51/README.md`. Current production candidate là **B51R1**. B51R1 STATIC CI PASS đã chứng minh B50 restore 1229/1229, raw B50 có đúng 19 unsupported chars trên 64 rows, correction layer phủ 64/64, sau correction frozen-60 còn 0 unsupported rows, B40/Batch42 560/560, B43 102/102, combined 662/662, intro 19/19, legacy 397/397, Translation Master 596/596, duplicate/overlap/byte/token PASS, font glyph added = 0, B50 canonical mutated = NO. Validated commit `33a5049bf6dc932a95892eeb1dbb99033c8d074b`, GitHub Actions run `35005218964`. B50 vẫn là canonical binary checkpoint vì chưa chạy được BIN thật trong connected environment. Bước kế tiếp là chạy `tools/build_gaia_b51r1_guarded_exact_overlay.py` dry-run trên exact CLEAN Japan BIN SHA1 `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`; chỉ nếu dry-run thật PASS mới build từ known-good runtime base đã có frozen 60-glyph codepage và đã pass 560/102/19. Không dùng CLEAN làm build base. Không đụng font. Không gọi build PASS khi chưa chạy BIN thật và không gọi Runtime PASS khi chưa có screenshot gameplay.

## Current branch

```text
gaia-character-select-font-atlas-reverse-01
```

## Files phải đọc đầu tiên

```text
games/GaiaMaster-Kamigami-no-Board-Game/HANDOFF_CURRENT.md
games/GaiaMaster-Kamigami-no-Board-Game/LATEST.md
games/GaiaMaster-Kamigami-no-Board-Game/translation/source_layer/checkpoint_B51/README.md
games/GaiaMaster-Kamigami-no-Board-Game/translation/source_layer/checkpoint_B51/B51R1_STATIC_CI_PROOF.txt
games/GaiaMaster-Kamigami-no-Board-Game/translation/source_layer/B51_RUNTIME_CHARSET_CORRECTIONS.csv
```

## Current production tools

```text
tools/build_gaia_b51_guarded_exact_overlay.py
tools/build_gaia_b51r1_guarded_exact_overlay.py
tools/validate_gaia_b51_static.py
tools/00_RUN_B51R1_GUARDED_DRYRUN.cmd
tools/00_BUILD_B51R1_GUARDED_EXACT_OVERLAY.cmd
```

## First action in next chat

```text
1. Nếu có CLEAN BIN thật: chạy B51R1 guarded dry-run trước.
2. Nếu dry-run fail: sửa đúng gate đầu tiên, không bypass.
3. Chỉ nếu dry-run PASS: build từ known-good runtime base BIN, không phải CLEAN.
4. Sau build: yêu cầu B51R1 1229/1229 output bytes + historical 560/102/19 + font/mapping read-back unchanged.
5. Sau đó mới test gameplay và xem screenshot.
6. Runtime PASS chỉ khi screenshot gameplay chứng minh ổn.
```

## B51R1 static proof

```text
Validated commit                  = 33a5049bf6dc932a95892eeb1dbb99033c8d074b
GitHub Actions run                = 35005218964
B50 exact candidates              = 1229/1229
Raw B50 unsupported chars         = 19/19 known debt
Raw B50 bad rows                  = 64/64 known debt
B51R1 exact-key corrections       = 64/64
Corrected frozen-60 charset       = PASS, 0 unsupported rows
B50 canonical mutated             = NO
New font glyphs                   = 0
B40 / Batch42                     = 560/560
B43                               = 102/102
Combined                          = 662/662
Intro                             = 19/19
Legacy Alpha                      = 397/397
Translation Master               = 596/596
Duplicate/overlap/byte/token      = PASS
ROM/font/pointer modified         = NO
Runtime PASS                      = NO
```

## B43 historical padding rule

Do not reintroduce the bad assumption that every historical B43 `field_bytes` must equal literal Japanese CP932 length.

The proven B43 builder supports padded fields. For B40/B43 historical manifest reconstruction use manifest field size as authoritative and require:

```text
field_bytes >= literal Japanese CP932 byte length
```

B50 exact source fields remain strict.

Known example:

```text
PRGPACK.BDP+0xDE0A0
Japanese = はい　　　いいえ
field_bytes = 22
```

## CLEAN dry-run command

```text
python tools/build_gaia_b51r1_guarded_exact_overlay.py "GaiaMaster - Kamigami no Board Game (Japan).bin"
```

Windows launcher:

```text
tools/00_RUN_B51R1_GUARDED_DRYRUN.cmd
```

## Guarded build command

Only after the real dry-run passes:

```text
python tools/build_gaia_b51r1_guarded_exact_overlay.py "GaiaMaster - Kamigami no Board Game (Japan).bin" --build-from "KNOWN_GOOD_RUNTIME_BASE.bin"
```

Windows launcher:

```text
tools/00_BUILD_B51R1_GUARDED_EXACT_OVERLAY.cmd
```

## Hard contracts

```text
CLEAN SHA1        = f4d5298583c90d89c4b7e51d2dde160ee07f2aec
B50 rows          = 1229
B50 direct        = 41
B50 compact       = 1188
B51R1 corrections = 64
Batch42/B40       = 560/560
Batch43           = 102/102
Combined          = 662/662
Intro             = 19/19
Legacy            = 397/397
Master            = 596/596
Architecture      = native 12x12 / 72-byte / 4bpp / mapping-only / frozen 60 glyphs
```

## Do not regress

- B50 canonical checkpoint stays immutable;
- B51R1 corrections are a separate text-only layer;
- no automatic new font glyphs;
- no READABLE/R5/Batch45 font-builder invocation from B51R1;
- no renderer hook or pointer redirect;
- preserve `%s`, `%d`, `%2d`, `%4d`, `%5d`, `%+3d`, `/V`, `/v`, `/Pxx`, `/PFx` order;
- no partial/conflicting overlap with B40/B43/intro protected spans;
- build base must already contain frozen-60 and historical 560/102/19;
- font atlas and mapping must be byte-identical before/after B51R1 build;
- do not call real dry-run/build PASS from CI-only evidence;
- do not call Runtime PASS before gameplay screenshots.
